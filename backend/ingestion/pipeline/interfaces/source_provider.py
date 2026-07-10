from typing import Protocol, List, Dict, Any, Optional
from pydantic import BaseModel

class MedicalSection(BaseModel):
    title: str
    content: str

class NormalizedMedicalDocument(BaseModel):
    drug: str
    generic_name: str
    source: str
    country: str
    version: str
    effective_date: Optional[str] = None
    revision: Optional[str] = None
    ingested_at: str
    sections: List[MedicalSection]

class MedicalSourceProvider(Protocol):
    """
    Protocol for external medical source data providers (e.g. DailyMed, openFDA).
    """
    def health_check(self) -> Dict[str, Any]:
        """
        Check the status of the provider API.
        Returns:
            Dict containing:
                "status": "healthy" or "unhealthy"
                "latency_sec": float
                "rate_limit_remaining": Optional[int]
                "rate_limit_reset_sec": Optional[int]
        """
        ...

    def fetch_single_drug(self, drug_name: str) -> Optional[NormalizedMedicalDocument]:
        """
        Fetch and normalize document for a single drug.
        """
        ...

    def fetch_documents(self, drug_names: List[str]) -> List[NormalizedMedicalDocument]:
        """
        Batch fetch and normalize documents.
        """
        ...
