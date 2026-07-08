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
    "t2dm": "type 2 diabetes mellitus"
}

class LayeredQueryExpander:
    """
    Expands a clinical query to capture synonyms and ontological equivalents.
    Layer 1: Static Dictionary/Ontology Lookup (Fast, 100% accurate)
    Layer 2: LLM Fallback (Slower, handles complex multi-word clinical concepts)
    """
    def __init__(self, llm_provider: LLMProviderProtocol):
        self.llm = llm_provider

    def expand(self, query: str) -> List[str]:
        expanded_queries = [query]
        q_lower = query.lower()
        
        # Layer 1: Dictionary / Ontology Expansion
        found_ontology = False
        for abbreviation, expansion in MEDICAL_ONTOLOGY.items():
            # Basic word boundary check
            if abbreviation in q_lower.split():
                expanded = q_lower.replace(abbreviation, expansion)
                expanded_queries.append(expanded)
                found_ontology = True
                logger.info("ontology_expansion_applied", original=abbreviation, expanded=expansion)
                
        if found_ontology:
            # If we found a direct clinical mapping, skip LLM call to save latency
            return expanded_queries
            
        # Layer 2: LLM Assisted Rewriting Fallback
        prompt = f"""
You are a medical query expansion assistant. 
Given the user's clinical query, generate exactly 1 alternative medical phrasing using standard clinical terminology or synonyms to maximize search retrieval recall.
Do NOT answer the question. ONLY output the alternative query string.

Original Query: {query}
Alternative Query:
"""
        logger.info("llm_expansion_fallback_triggered", query=query)
        try:
            llm_response = self.llm.generate(prompt)
            alt_query = llm_response.strip().strip('"').strip("'")
            if alt_query and alt_query.lower() != query.lower():
                expanded_queries.append(alt_query)
        except Exception as e:
            logger.error("llm_expansion_failed", error=str(e))
            
        return list(set(expanded_queries))
