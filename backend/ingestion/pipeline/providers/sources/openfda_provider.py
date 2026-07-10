import os
import json
import time
import requests
import structlog
from typing import Dict, Any, List, Optional
from ...interfaces.source_provider import MedicalSourceProvider, NormalizedMedicalDocument
from ...adapters.openfda_adapter import OpenFDAAdapter
from ...config import ingestion_config

logger = structlog.get_logger()

class OpenFDAProvider(MedicalSourceProvider):
    """
    MedicalSourceProvider for openFDA drug labels API.
    """
    def __init__(self):
        self.base_url = "https://api.fda.gov/drug/label.json"
        
    def _execute_request_with_retry(self, url: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        retries = 0
        backoff = ingestion_config.BACKOFF_FACTOR
        
        while retries <= ingestion_config.MAX_RETRIES:
            try:
                start_time = time.time()
                response = requests.get(url, params=params, timeout=15)
                latency = time.time() - start_time
                
                # Check for rate limiting (HTTP 429)
                if response.status_code == 429:
                    logger.warning("openfda_rate_limited", retry=retries, url=url)
                    time.sleep(backoff)
                    retries += 1
                    backoff *= 2
                    continue
                    
                response.raise_for_status()
                return response.json()
                
            except requests.RequestException as e:
                logger.warning("openfda_request_failed", error=str(e), retry=retries, url=url)
                if retries == ingestion_config.MAX_RETRIES:
                    logger.error("openfda_request_failed_permanently", error=str(e), url=url)
                    return None
                time.sleep(backoff)
                retries += 1
                backoff *= 2
                
        return None

    def health_check(self) -> Dict[str, Any]:
        """
        Check connectivity to the openFDA API.
        """
        params = {"limit": 1}
        start_time = time.time()
        try:
            # We bypass the standard retry wrapper to quickly get status
            response = requests.get(self.base_url, params=params, timeout=5)
            latency = response.elapsed.total_seconds()
            
            rate_limit_remaining = None
            rate_limit_reset = None
            
            # openFDA returns rate limit headers:
            # X-RateLimit-Remaining: 239
            # X-RateLimit-Limit: 240
            if "X-RateLimit-Remaining" in response.headers:
                rate_limit_remaining = int(response.headers["X-RateLimit-Remaining"])
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "latency_sec": latency,
                    "rate_limit_remaining": rate_limit_remaining,
                    "rate_limit_reset_sec": rate_limit_reset
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
        Fetch and normalize a drug label from openFDA.
        """
        logger.info("fetching_openfda_drug_label", drug=drug_name)
        
        raw_filename = f"openfda_{drug_name.lower().replace(' ', '_')}.json"
        raw_filepath = os.path.join(ingestion_config.RAW_DATA_DIR, raw_filename)
        
        # Check if local cache exists
        if os.path.exists(raw_filepath):
            try:
                with open(raw_filepath, "r", encoding="utf-8") as f:
                    raw_result = json.load(f)
                logger.info("loaded_openfda_label_from_cache", drug=drug_name, path=raw_filepath)
                normalized_doc = OpenFDAAdapter.to_normalized(raw_result)
                if normalized_doc and not normalized_doc.drug:
                    normalized_doc.drug = drug_name.capitalize()
                return normalized_doc
            except Exception as e:
                logger.warning("failed_loading_openfda_cache_falling_back_to_api", error=str(e))
                
        # Try brand name search first
        params = {
            "search": f'openfda.brand_name:"{drug_name}"',
            "limit": 1
        }
        
        data = self._execute_request_with_retry(self.base_url, params)
        
        # Fallback to generic name search if brand name returns nothing
        if not data or not data.get("results"):
            logger.info("openfda_brand_name_not_found_trying_generic", drug=drug_name)
            params = {
                "search": f'openfda.generic_name:"{drug_name}"',
                "limit": 1
            }
            data = self._execute_request_with_retry(self.base_url, params)
            
        if not data or not data.get("results"):
            logger.warning("openfda_drug_not_found", drug=drug_name)
            return None
            
        raw_result = data["results"][0]
        
        # Save raw source file (idempotent, overwrite if exists)
        raw_filename = f"openfda_{drug_name.lower().replace(' ', '_')}.json"
        raw_filepath = os.path.join(ingestion_config.RAW_DATA_DIR, raw_filename)
        try:
            with open(raw_filepath, "w", encoding="utf-8") as f:
                json.dump(raw_result, f, indent=2, ensure_ascii=False)
            logger.debug("saved_raw_openfda_file", path=raw_filepath)
        except Exception as e:
            logger.error("failed_saving_raw_openfda_file", path=raw_filepath, error=str(e))

        # Normalize via adapter
        try:
            normalized_doc = OpenFDAAdapter.to_normalized(raw_result)
            # Ensure the query drug name is set if the normalized doc name is missing
            if normalized_doc and not normalized_doc.drug:
                normalized_doc.drug = drug_name.capitalize()
            return normalized_doc
        except Exception as e:
            logger.error("openfda_normalization_failed", drug=drug_name, error=str(e))
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
