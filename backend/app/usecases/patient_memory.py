import structlog
from typing import Dict, Any, Optional
from app.domain.models import PatientProfile

logger = structlog.get_logger()

class PatientMemoryStore:
    """
    Persistent in-memory patient context store.
    Remembers patient characteristics (eGFR, CKD Stage, Warfarin, Active Meds, Allergies)
    across multi-turn chat sessions so doctors don't need to re-enter patient data.
    """
    def __init__(self):
        self.profiles: Dict[str, PatientProfile] = {}

    def save_profile(self, patient_id: str, profile: PatientProfile) -> None:
        if patient_id in self.profiles:
            existing = self.profiles[patient_id]
            # Merge updates
            if profile.age: existing.age = profile.age
            if profile.gender: existing.gender = profile.gender
            if profile.eGFR: existing.eGFR = profile.eGFR
            if profile.hepatic_stage: existing.hepatic_stage = profile.hepatic_stage
            if profile.pregnancy is not None: existing.pregnancy = profile.pregnancy
            if profile.comorbidities:
                existing.comorbidities = list(set(existing.comorbidities + profile.comorbidities))
            if profile.active_medications:
                existing.active_medications = list(set(existing.active_medications + profile.active_medications))
            if profile.allergies:
                existing.allergies = list(set(existing.allergies + profile.allergies))
            logger.info("patient_profile_updated", patient_id=patient_id)
        else:
            self.profiles[patient_id] = profile
            logger.info("patient_profile_created", patient_id=patient_id)

    def get_profile(self, patient_id: str) -> Optional[PatientProfile]:
        return self.profiles.get(patient_id)

# Global singleton store instance
patient_memory_store = PatientMemoryStore()
