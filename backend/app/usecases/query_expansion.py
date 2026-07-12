import json
from typing import List
from app.domain.interfaces import LLMProviderProtocol
import structlog

logger = structlog.get_logger()

# A minimal medical ontology mapping to prioritize exact, fast expansions
MEDICAL_ONTOLOGY = {
    "hba1c": "hemoglobin a1c",
    "mi": "myocardial infarction",
    "chf": "congestive heart failure",
    "gerd": "gastroesophageal reflux disease",
    "nsaid": "nonsteroidal anti-inflammatory drug",
    "htn": "hypertension",
    "ckd": "chronic kidney disease",
    "t2dm": "type 2 diabetes mellitus",
    "adrs": "adverse reactions side effects",
    "rx": "prescription treatment",
    "dx": "diagnosis",
    "sx": "symptoms",
    "tx": "treatment",
    "ddx": "differential diagnosis",
    "hx": "history",
    "bid": "twice a day",
    "tid": "three times a day",
    "qd": "daily",
    "prn": "as needed"
}

class LayeredQueryExpander:
    """
    Expands a clinical query to capture synonyms and ontological equivalents.
    Uses Static Dictionary/Ontology Lookup (Fast, 100% accurate, 0 LLM cost).
    LLM fallback has been permanently removed to optimize rate limits.
    """
    def __init__(self, llm_provider=None):
        # We accept llm_provider for backwards compatibility but do not use it
        self.llm = None

    def expand(self, query: str, skip_llm: bool = True) -> List[str]:
        expanded_queries = [query]
        q_lower = query.lower()
        
        # Ontology Expansion
        for abbreviation, expansion in MEDICAL_ONTOLOGY.items():
            if abbreviation in q_lower.split():
                expanded = q_lower.replace(abbreviation, expansion)
                expanded_queries.append(expanded)
                logger.info("ontology_expansion_applied", original=abbreviation, expanded=expansion)
                
        # Zero-latency medical synonym expansion for key attributes
        if "refrigerat" in q_lower or "stor" in q_lower or "keep" in q_lower:
            expanded_queries.append("storage temperature and handling")
            expanded_queries.append("refrigeration requirements and shelf life")
        if "side effect" in q_lower or "adverse" in q_lower:
            expanded_queries.append("adverse reactions side effects")
        if "interaction" in q_lower:
            expanded_queries.append("drug interactions")
            
        return list(set(expanded_queries))
