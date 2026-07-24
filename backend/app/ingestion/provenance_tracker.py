from typing import Dict, Any, Optional
from datetime import datetime
import uuid

class DocumentProvenanceTracker:
    """
    Document-Level Provenance & Lineage Tracker for MedRef v6.0.
    Attaches immutable audit metadata to every ingested document/chunk:
    - document_id
    - source (DailyMed, CDSCO, ADA, KDIGO, GINA, ESC)
    - source_version_date
    - ingestion_batch_id
    - corpus_version_introduced
    - last_validated
    - last_updated
    - superseded_by
    """

    @classmethod
    def attach_provenance(
        cls, doc_payload: Dict[str, Any], source: str, source_version_date: str,
        ingestion_batch_id: str, corpus_version: str, superseded_by: Optional[str] = None
    ) -> Dict[str, Any]:
        now_iso = datetime.utcnow().isoformat() + "Z"
        doc_id = doc_payload.get("document_id") or f"doc_{uuid.uuid4().hex[:12]}"

        provenance_metadata = {
            "document_id": doc_id,
            "source": source,
            "source_version_date": source_version_date,
            "ingestion_batch_id": ingestion_batch_id,
            "corpus_version_introduced": corpus_version,
            "last_validated": now_iso,
            "last_updated": now_iso,
            "superseded_by": superseded_by
        }

        # Attach provenance directly into document metadata payload
        doc_payload["provenance"] = provenance_metadata
        return doc_payload

    @classmethod
    def audit_provenance(cls, doc_payload: Dict[str, Any]) -> Tuple[bool, str]:
        prov = doc_payload.get("provenance")
        if not prov:
            return False, "Missing document-level provenance metadata block."
        
        required_keys = ["document_id", "source", "source_version_date", "ingestion_batch_id", "corpus_version_introduced"]
        for key in required_keys:
            if not prov.get(key):
                return False, f"Missing required provenance field: '{key}'"
                
        return True, "Provenance metadata valid."
