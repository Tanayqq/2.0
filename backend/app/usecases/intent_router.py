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
        "DRUG_CHAT": ["openfda_labels", "drug_labels_india"],
        "DISEASE_CHAT": ["disease_corpus", "disease_guidelines"],
        "SYMPTOM_CHAT": ["disease_corpus", "openfda_labels"],
        "PATIENT_SCENARIO": ["openfda_labels", "drug_interactions", "disease_guidelines"],
        "COMPARISON": ["openfda_labels", "drug_labels_india"],
        "INTERACTION_CHECK": ["drug_interactions", "openfda_labels"],
        "MEDICAL_REP": ["drug_labels_india", "openfda_labels"],
        "CLINICAL_GUIDELINE": ["disease_guidelines", "disease_corpus"],
        "RESEARCH_LITERATURE": ["primary_literature", "openfda_labels"]
    }

    @classmethod
    def classify_intent(cls, question: str, mode_override: Optional[str] = None) -> ClinicalChatMode:
        if mode_override and mode_override.upper() in cls.MODE_COLLECTIONS:
            return mode_override.upper()  # type: ignore

        q_lower = question.lower()

        # --- Research Literature (highest priority: explicit trial names) ---
        if any(kw in q_lower for kw in [
            "flow", "dapa-ckd", "fidelio-dkd", "credence", "empa-kidney", "emperor",
            "declare", "canvas", "leader", "sustain", "rewind", "pioneer",
            "trial", "rct", "nejm", "lancet", "pubmed", "cochrane",
            "study shows", "latest evidence", "outcomes", "randomized"
        ]):
            return "RESEARCH_LITERATURE"

        # --- Multi-drug interaction: 2+ drug names joined by + or 'and' with risk/interaction context ---
        import re as _re
        drug_count = len(_re.findall(r'\b(vancomycin|amiodarone|digoxin|metoprolol|clarithromycin|furosemide|norepinephrine|piperacillin|tazobactam|spironolactone|enalapril|naproxen|warfarin|heparin|aspirin|clopidogrel|rivaroxaban|apixaban|semaglutide|dapagliflozin|empagliflozin|canagliflozin|finerenone|metformin|insulin|lisinopril|amlodipine|atorvastatin|rosuvastatin|losartan|valsartan|omeprazole|pantoprazole|azithromycin|ciprofloxacin|levofloxacin|meropenem|linezolid|daptomycin|cefazolin|ceftriaxone|piperacillin|tazobactam|morphine|fentanyl|midazolam|propofol|rocuronium|succinylcholine)\b', q_lower))
        if drug_count >= 2 and any(kw in q_lower for kw in [
            "risk", "interaction", "cascade", "synergy", "concurrent", "coadministration",
            "together", "combine", "combination", "concomitant", "threat", "potentiation",
            "nephrotoxicity", "hepatotoxicity", "qtc", "tdp", "bradycardia", "hypotension",
            "icu", "septic", "shock", "+"
        ]):
            return "INTERACTION_CHECK"

        # --- Patient Scenario: age/clinical context BEFORE disease keywords ---
        if any(kw in q_lower for kw in [
            "year-old", "year old", "-year-old", "yo ", "yo,",
            "patient with", "patient on", "patient who",
            "hba1c", "lvef", "uacr", "egfr", "scr", "creatinine",
            "ckd stage", "step-therapy", "step therapy", "prioritize",
            "male patient", "female patient", "55-year", "60-year", "65-year", "70-year",
            "justify", "cardiorenal", "ada 2025", "kdigo 2024",
            "on metformin", "on insulin", "on lisinopril"
        ]):
            return "PATIENT_SCENARIO"

        # --- Drug Interaction (general) ---
        if any(kw in q_lower for kw in ["interaction", "coadministration", "together", "interact", "combine"]):
            return "INTERACTION_CHECK"

        # --- Comparison ---
        if any(kw in q_lower for kw in ["versus", " vs ", "vs.", "compare", "difference between"]):
            return "COMPARISON"

        # --- Medical Rep ---
        if any(kw in q_lower for kw in ["monograph", "competitor", "market position", "sales rep", "detail sheet"]):
            return "MEDICAL_REP"

        # --- Clinical Guideline ---
        if any(kw in q_lower for kw in [
            "guideline", "ada 2026", "ada 2025", "kdigo", "gold 2026", "gina",
            "icmr guideline", "ntep", "esc ", "acc/aha", "surviving sepsis"
        ]):
            return "CLINICAL_GUIDELINE"

        # --- Symptom Chat ---
        if any(kw in q_lower for kw in ["fever", "cough", "shortness of breath", "dyspnea", "chest pain", "diarrhea", "rash"]):
            return "SYMPTOM_CHAT"

        # --- Disease Chat (last, after patient scenario checked) ---
        if any(kw in q_lower for kw in [
            "asthma", "copd", "diabetes", "hypertension", "ckd", "stroke",
            "heart failure", "sepsis", "aki", "ards", "cirrhosis", "nafld"
        ]):
            return "DISEASE_CHAT"

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
