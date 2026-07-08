from pydantic import BaseModel
from typing import List, Optional, Dict

class MedicalQuery(BaseModel):
    question: str
    session_id: Optional[str] = None
    filters: Optional[Dict[str, List[str]]] = None

class Citation(BaseModel):
    document_id: str
    source: str
    snippet: str

class ReferenceDocument(BaseModel):
    id: str
    content: str
    source: str
    metadata: dict
    score: Optional[float] = None

class AnswerResponse(BaseModel):
    answer: str
    citations: List[Citation]
    disclaimer: str = "Clinical judgment remains with the treating physician."
    metadata: dict = {}
