import os
import time
import requests
import structlog
from typing import Dict, Any, List, Optional
from ...interfaces.source_provider import MedicalSourceProvider, NormalizedMedicalDocument
from ...adapters.dailymed_adapter import DailyMedAdapter
from ...config import ingestion_config

logger = structlog.get_logger()

class DailyMedProvider(MedicalSourceProvider):
    """
    MedicalSourceProvider for DailyMed SPL REST API.
    """
    def __init__(self):
        self.search_url = "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json"
        self.xml_url_template = "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/{setid}.xml"

    def _execute_request_with_retry(self, url: str, stream: bool = False) -> Optional[requests.Response]:
        retries = 0
        backoff = ingestion_config.BACKOFF_FACTOR
        
        while retries <= ingestion_config.MAX_RETRIES:
            try:
                response = requests.get(url, timeout=20, stream=stream)
                
                # Check for rate limiting
                if response.status_code == 429:
                    logger.warning("dailymed_rate_limited", retry=retries, url=url)
                    time.sleep(backoff)
                    retries += 1
                    backoff *= 2
                    continue
                    
                response.raise_for_status()
                return response
                
            except requests.RequestException as e:
                logger.warning("dailymed_request_failed", error=str(e), retry=retries, url=url)
                if retries == ingestion_config.MAX_RETRIES:
                    logger.error("dailymed_request_failed_permanently", error=str(e), url=url)
                    return None
                time.sleep(backoff)
                retries += 1
                backoff *= 2
                
        return None

    def health_check(self) -> Dict[str, Any]:
        """
        Check connectivity to the DailyMed API.
        """
        start_time = time.time()
        try:
            # We fetch list with limit=1 to verify health
            response = requests.get(self.search_url, params={"limit": 1}, timeout=5)
            latency = response.elapsed.total_seconds()
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "latency_sec": latency,
                    "rate_limit_remaining": None,  # DailyMed doesn't return headers by default
                    "rate_limit_reset_sec": None
                }
            else:
                return {
                    "status": "unhealthy",
                    "latency_sec": latency,
                    "error_code": response.status_code
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "latency_sec": time.time() - start_time,
                "error": str(e)
            }

    def fetch_single_drug(self, drug_name: str) -> Optional[NormalizedMedicalDocument]:
        """
        Fetch and normalize a drug label from DailyMed.
        """
        logger.info("fetching_dailymed_drug_label", drug=drug_name)
        
        raw_filename = f"dailymed_{drug_name.lower().replace(' ', '_')}.xml"
        raw_filepath = os.path.join(ingestion_config.RAW_DATA_DIR, raw_filename)
        
        # Check if local cache exists
        if os.path.exists(raw_filepath):
            try:
                with open(raw_filepath, "r", encoding="utf-8") as f:
                    xml_content = f.read()
                logger.info("loaded_dailymed_label_from_cache", drug=drug_name, path=raw_filepath)
                normalized_doc = DailyMedAdapter.to_normalized(xml_content, drug_name)
                return normalized_doc
            except Exception as e:
                logger.warning("failed_loading_dailymed_cache_falling_back_to_api", error=str(e))
                
        # 1. Search for the drug to get the Set ID
        search_params = {"drug_name": drug_name, "limit": 1}
        search_url_with_params = f"{self.search_url}?drug_name={drug_name}&limit=1"
        
        resp = self._execute_request_with_retry(search_url_with_params)
        if not resp:
            return None
            
        search_data = resp.json()
        data_list = search_data.get("data", [])
        if not data_list:
            logger.warning("dailymed_drug_not_found", drug=drug_name)
            return None
            
        # Get the setid of the first match
        setid = data_list[0].get("setid", "")
        if not setid:
            logger.warning("dailymed_setid_missing_in_response", drug=drug_name)
            return None
            
        logger.info("found_dailymed_setid", drug=drug_name, setid=setid)
        
        # 2. Fetch the XML document
        xml_url = self.xml_url_template.format(setid=setid)
        xml_resp = self._execute_request_with_retry(xml_url)
        if not xml_resp:
            return None
            
        xml_content = xml_resp.text
        
        # Save raw XML file before normalization
        raw_filename = f"dailymed_{drug_name.lower().replace(' ', '_')}.xml"
        raw_filepath = os.path.join(ingestion_config.RAW_DATA_DIR, raw_filename)
        try:
            with open(raw_filepath, "w", encoding="utf-8") as f:
                f.write(xml_content)
            logger.debug("saved_raw_dailymed_file", path=raw_filepath)
        except Exception as e:
            logger.error("failed_saving_raw_dailymed_file", path=raw_filepath, error=str(e))

        # 3. Normalize XML Content via Adapter
        try:
            normalized_doc = DailyMedAdapter.to_normalized(xml_content, drug_name)
            return normalized_doc
        except Exception as e:
            logger.error("dailymed_normalization_failed", drug=drug_name, setid=setid, error=str(e))
            return None

    def fetch_documents(self, drug_names: List[str]) -> List[NormalizedMedicalDocument]:
        """
        Batch fetch and normalize documents.
        """
        results = []
        for name in drug_names:
            doc = self.fetch_single_drug(name)
            if doc:
                results.append(doc)
            # Gentle politeness delay
            time.sleep(0.5)
        return results
