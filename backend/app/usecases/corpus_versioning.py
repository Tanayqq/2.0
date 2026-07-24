from typing import Dict, Any, List
from datetime import datetime

class CorpusVersionManager:
    """
    Corpus Versioning Manager for MedRef v6.0.
    Tracks release versions (e.g. v1.0 -> v1.1 -> v1.2), batch increments,
    and batch QA audit certificates for production traceability and rollback safety.
    """

    VERSION_HISTORY: List[Dict[str, Any]] = [
        {
            "version": "v1.0",
            "release_date": "2026-07-24",
            "canonical_drugs": 385,
            "brand_aliases": 380,
            "disease_monographs": 55,
            "interaction_pairs": 145,
            "batch_delta": {"new_drugs": "+385", "new_aliases": "+380", "new_guidelines": "+15"},
            "qa_status": "PASS",
            "release_notes": "Initial multi-domain baseline corpus (FDA DailyMed, CDSCO India, ADA 2026, KDIGO 2024, ESC 2024)"
        }
    ]

    @classmethod
    def get_current_version(cls) -> Dict[str, Any]:
        return cls.VERSION_HISTORY[-1]

    @classmethod
    def register_new_version(
        cls, version_tag: str, drugs_count: int, aliases_count: int,
        diseases_count: int, interactions_count: int, delta: Dict[str, str],
        qa_status: str, notes: str
    ) -> Dict[str, Any]:
        entry = {
            "version": version_tag,
            "release_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "canonical_drugs": drugs_count,
            "brand_aliases": aliases_count,
            "disease_monographs": diseases_count,
            "interaction_pairs": interactions_count,
            "batch_delta": delta,
            "qa_status": qa_status,
            "release_notes": notes
        }
        cls.VERSION_HISTORY.append(entry)
        return entry

    @classmethod
    def get_all_history(cls) -> List[Dict[str, Any]]:
        return cls.VERSION_HISTORY
