import re
import structlog
from typing import Dict, Any, List, Optional
from app.domain.models import ClinicalChatMode, CountryContext

logger = structlog.get_logger()

class IntentRouter:
    """
    Intelligent Intent Router & Multi-Collection Dispatcher for MedRef v5.0.
    Classifies input queries into one of the 9 Clinical Chat Modes and selects
    the targeted Qdrant vector collections to query.
    """
    MODE_COLLECTIONS: Dict[ClinicalChatMode, List[str]] = {
        "DRUG_CHAT": ["drug_labels_us", "openfda_labels"],
        "DISEASE_CHAT": ["disease_corpus", "disease_guidelines"],
        "SYMPTOM_CHAT": ["disease_corpus", "openfda_labels"],
        "PATIENT_SCENARIO": ["drug_labels_us", "drug_interactions", "disease_guidelines"],
        "COMPARISON": ["drug_labels_us", "openfda_labels"],
        "INTERACTION_CHECK": ["drug_interactions", "openfda_labels"],
        "MEDICAL_REP": ["drug_labels_us", "openfda_labels", "drug_regulatory"],
        "CLINICAL_GUIDELINE": ["disease_guidelines", "disease_corpus"],
        "RESEARCH_LITERATURE": ["primary_literature", "openfda_labels"]
    }

    @classmethod
    def classify_intent(cls, question: str, mode_override: Optional[str] = None) -> ClinicalChatMode:
        if mode_override and mode_override.upper() in cls.MODE_COLLECTIONS:
            return mode_override.upper()  # type: ignore

        q_lower = question.lower()

        if any(kw in q_lower for kw in ["versus", " vs ", "vs.", "compare", "difference between"]):
            return "COMPARISON"
        if any(kw in q_lower for kw in ["interaction", "coadministration", "together", "interact", "combine"]):
            return "INTERACTION_CHECK"
        if any(kw in q_lower for kw in ["monograph", "competitor", "market position", "sales rep", "detail sheet"]):
            return "MEDICAL_REP"
        if any(kw in q_lower for kw in ["guideline", "ada 2026", "kdigo", "gold 2026", "gina", "icmr guideline", "ntep"]):
            return "CLINICAL_GUIDELINE"
        if any(kw in q_lower for kw in ["trial", "nejm", "lancet", "pubmed", "cochrane", "study shows", "latest evidence"]):
            return "RESEARCH_LITERATURE"
        if any(kw in q_lower for kw in ["fever", "cough", "shortness of breath", "dyspnea", "chest pain", "diarrhea", "rash"]):
            return "SYMPTOM_CHAT"
        if any(kw in q_lower for kw in ["asthma", "copd", "diabetes", "hypertension", "ckd", "stroke", "heart failure"]):
            return "DISEASE_CHAT"
        if any(kw in q_lower for kw in ["year old", "yo ", "patient with", "egfr", "ckd stage"]):
            return "PATIENT_SCENARIO"

        return "DRUG_CHAT"

    @classmethod
    def route_query(cls, question: str, country_context: CountryContext = "GLOBAL", mode_override: Optional[str] = None) -> Dict[str, Any]:
        mode = cls.classify_intent(question, mode_override)
        target_collections = list(cls.MODE_COLLECTIONS.get(mode, ["openfda_labels"]))

        # Country context routing adjustments
        if country_context == "IN":
            target_collections.append("drug_labels_india")
            target_collections.append("brand_aliases")
        elif country_context == "US":
            target_collections.append("drug_labels_us")

        target_collections = list(dict.fromkeys(target_collections))

        logger.info("query_routed", mode=mode, country_context=country_context, collections=target_collections)

        return {
            "mode": mode,
            "country_context": country_context,
            "target_collections": target_collections
        }
