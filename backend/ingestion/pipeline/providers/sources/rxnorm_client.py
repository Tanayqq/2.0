import urllib.request
import urllib.parse
import json
import structlog
from typing import List, Optional

logger = structlog.get_logger()

class RxNormClient:
    """
    Stateless client to query the National Library of Medicine (NLM) RxNorm REST API.
    Does not require API keys.
    """
    BASE_URL = "https://rxnav.nlm.nih.gov/REST"

    def get_rxcui(self, drug_name: str) -> Optional[str]:
        """
        Retrieves the RxNorm Concept Unique Identifier (rxcui) for a given drug name.
        """
        try:
            query = urllib.parse.urlencode({"name": drug_name})
            url = f"{self.BASE_URL}/rxcui.json?{query}"
            
            req = urllib.request.Request(
                url, 
                headers={"User-Agent": "MedRefRAGPipeline/3.3"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
                
            rxnorm_ids = data.get("idGroup", {}).get("rxnormId", [])
            if rxnorm_ids:
                return rxnorm_ids[0]
        except Exception as e:
            logger.warning("rxnorm_rxcui_lookup_failed", drug=drug_name, error=str(e))
        return None

    def get_all_names(self, rxcui: str) -> List[str]:
        """
        Retrieves related terms (Brand Names, Ingredients, Precise Ingredients, Synonyms) 
        from the RxNorm concept. Filters to keep names clean (no strengths or dosage forms).
        """
        names = []
        try:
            url = f"{self.BASE_URL}/rxcui/{rxcui}/allrelated.json"
            req = urllib.request.Request(
                url, 
                headers={"User-Agent": "MedRefRAGPipeline/3.3"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
                
            concept_groups = data.get("allRelatedGroup", {}).get("conceptGroup", [])
            
            # Keep only clean term types: BN (Brand Name), IN/PIN/MIN (Ingredients), SY (Synonyms)
            allowed_ttys = {"BN", "IN", "PIN", "MIN", "SY"}
            
            for group in concept_groups:
                tty = group.get("tty")
                if tty in allowed_ttys:
                    properties = group.get("conceptProperties", [])
                    for prop in properties:
                        name = prop.get("name")
                        if name:
                            # Clean name: remove trailing details or keep if simple
                            clean_name = name.strip()
                            # Basic heuristic to avoid full strings like "Amoxicillin 250 MG Oral Tablet"
                            # If it contains numbers or 'Oral', 'Tablet', etc., it's probably too specific
                            lower_name = clean_name.lower()
                            if any(char.isdigit() for char in clean_name):
                                continue
                            if any(word in lower_name for word in [" tablet", " capsule", " oral", " injection", " suspension", " powder"]):
                                continue
                            names.append(clean_name)
        except Exception as e:
            logger.warning("rxnorm_allrelated_lookup_failed", rxcui=rxcui, error=str(e))
        return list(dict.fromkeys(names)) # Deduplicate
