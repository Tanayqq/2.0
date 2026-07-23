from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal

ClinicalChatMode = Literal[
    "DRUG_CHAT",
    "DISEASE_CHAT",
    "SYMPTOM_CHAT",
    "PATIENT_SCENARIO",
    "COMPARISON",
    "INTERACTION_CHECK",
    "MEDICAL_REP",
    "CLINICAL_GUIDELINE",
    "RESEARCH_LITERATURE"
]

CountryContext = Literal["US", "IN", "GLOBAL"]

class PatientProfile(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    eGFR: Optional[float] = None
    hepatic_stage: Optional[str] = None
    pregnancy: Optional[bool] = None
    smoking: Optional[bool] = None
    comorbidities: List[str] = Field(default_factory=list)
    active_medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    vitals: Dict[str, Any] = Field(default_factory=dict)
    recent_labs: Dict[str, Any] = Field(default_factory=dict)

class MedicalQuery(BaseModel):
    question: str
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None
    mode: Optional[ClinicalChatMode] = "DRUG_CHAT"
    country_context: Optional[CountryContext] = "GLOBAL"
    patient_profile: Optional[PatientProfile] = None
    filters: Optional[Dict[str, List[str]]] = None

class Citation(BaseModel):
    document_id: str
    source: str
    snippet: str
    uuid: Optional[str] = None
    drug: Optional[str] = None
    disease: Optional[str] = None
    section: Optional[str] = None
    authority: Optional[str] = "DailyMed"
    authority_priority: Optional[int] = 98
    freshness_factor: Optional[float] = 1.0
    publication_date: Optional[str] = None
    domain: Optional[str] = "Drug Knowledge"
    similarity: Optional[float] = None
    count: int = 1
    citation_number: Optional[int] = None

class ReferenceDocument(BaseModel):
    id: str
    content: str
    source: str
    metadata: dict
    score: Optional[float] = None
    cross_encoder_score: Optional[float] = None

class AnswerResponse(BaseModel):
    answer: str
    citations: List[Citation]
    disclaimer: str = "Clinical judgment remains with the treating physician. MedRef is an evidence-grounded decision engine."
    metadata: dict = {}
