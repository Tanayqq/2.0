from typing import Protocol, List, Dict, Any, Optional
from pydantic import BaseModel

class MedicalSection(BaseModel):
    title: str
    content: str

class NormalizedMedicalDocument(BaseModel):
    drug: str
    generic_name: str
    source: str
    source_url: Optional[str] = None           # Deep link to originating FDA/DailyMed label
    authority: Optional[str] = None            # "FDA", "DailyMed", "EMA", "CDSCO"
    authority_version: Optional[str] = None    # Label effective date e.g. "2024-03-15"
    drug_revision: Optional[str] = None        # e.g. revision/set_id for version history
    country: str
    version: str
    effective_date: Optional[str] = None
    revision: Optional[str] = None
    ingested_at: str
    retrieved_on: Optional[str] = None         # ISO timestamp of the API fetch
    sections: List[MedicalSection]
    synonyms: List[str] = []                   # Drug spelling variants e.g. amoxycillin→amoxicillin

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
