from pydantic import BaseModel
from typing import Any, Optional, List, Dict

class ProfileField(BaseModel):
    value: Any = None
    source: str = ""  # e.g., "DailyMed", "openFDA"
    authority: str = "FDA"  # e.g., "FDA"
    section: str = ""  # e.g., "Dosage and Administration"
    chunk_id: Optional[str] = None  # Exact chunk UUID producing this field
    confidence: str = "deterministic"  # "deterministic", "validated", "fallback_llm", "missing"
    evidence_strength: str = "HIGH"  # "HIGH" (Official Label), "MEDIUM" (Clinical Study)
    status: str = "present"  # "present", "missing", "not_applicable", "not_ingested"
    reason: Optional[str] = None
    
    # Ingestion Lineage & Freshness
    parser_version: str = "4.0"
    pipeline_version: str = "3.5"
    document_checksum: str = ""
    last_verified: str = ""  # ISO Date YYYY-MM-DD

class RegistryEntry(BaseModel):
    entity_id: str  # e.g. "drug:metformin"
    entity_type: str = "drug"  # Default to "drug"
    generic_name: str
    preferred_authority: str = "FDA"
    active_profile_version: int = 1
    aliases: List[str] = []

class DrugIdentityProfile(BaseModel):
    entity_id: str  # e.g. "drug:metformin"
    entity_type: str = "drug"
    generic_name: ProfileField
    brand_names: ProfileField  # List[str] in ProfileField.value
    drug_class: ProfileField
    prescription_status: ProfileField
    atc_code: ProfileField
    rxnorm_id: ProfileField
    unii: ProfileField
    manufacturer: ProfileField

class DrugClinicalProfile(BaseModel):
    entity_id: str  # e.g. "drug:metformin"
    entity_type: str = "drug"
    authority: str = "FDA"
    
    # Clinical Fields
    mechanism: ProfileField
    indications: ProfileField  # List[str] in ProfileField.value
    dosing: Dict[str, ProfileField]  # keys: adult, pediatric, geriatric, renal, hepatic, loading_dose, maintenance_dose, maximum_dose, route, instructions
    contraindications: ProfileField  # List[str] in ProfileField.value
    warnings: ProfileField  # List[str] in ProfileField.value
    side_effects: Dict[str, ProfileField]  # keys: common, less_common, rare, life_threatening
    drug_interactions: Dict[str, ProfileField]  # keys: contraindicated, major, moderate, minor, monitoring_required
    special_populations: Dict[str, ProfileField]  # keys: pregnancy, lactation, pediatric, geriatric, renal, hepatic, dialysis, pharmacogenomics
    storage: Dict[str, ProfileField]  # keys: temperature, light_protection, moisture_protection, container, expiration
    patient_counseling: Dict[str, ProfileField]  # keys: key_points, driving, alcohol, missed_dose, monitoring, lifestyle
