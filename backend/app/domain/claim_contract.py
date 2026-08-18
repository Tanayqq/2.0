from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class ClaimContract:
    """Atomic Clinical Claim Contract defining strict verification requirements."""
    drug: str
    action: str  # STOP, HOLD, REDUCE_DOSE, CONTINUE
    claim_type: str  # RENAL_DOSING, PREGNANCY_CONTRAINDICATION, HYPERKALEMIA_SAFETY, DDI_INTERACTION, INDICATION_GDMT
    patient_factors: Dict[str, Any] = field(default_factory=dict)
    required_entities: List[str] = field(default_factory=list)
    required_topics: List[str] = field(default_factory=list)
    required_predicates: List[str] = field(default_factory=list)

@dataclass
class EvidenceEntry:
    """Structured Metadata and Content of a candidate evidence chunk."""
    entry_id: str
    drug: str
    section: str
    text: str
    source: str = "DailyMed"
    source_version: str = "v4.0"
    effective_date: str = "2026-07"
    entities: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    predicates: List[str] = field(default_factory=list)
    patient_factor_bounds: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VerificationResult:
    """Outcome of verifying a ClaimContract against an EvidenceEntry."""
    passed: bool
    reason: str  # PASSED, ENTITY_MISMATCH, MISSING_DDI_ENTITY, TOPIC_MISMATCH, PREDICATE_MISMATCH, PATIENT_FACTOR_MISMATCH, CONTRADICTION
    details: Optional[str] = None

@dataclass
class CandidateAudit:
    """Audit log entry for a single candidate chunk evaluated against a ClaimContract."""
    citation_id: str
    drug: str
    section: str
    entity_match: bool
    topic_match: bool
    predicate_match: bool
    patient_factor_match: bool
    contradiction: bool
    verified: bool
    failure_reason: str

@dataclass
class CitationLedger:
    """Audit ledger tracking all candidate evidence evaluations for a clinical recommendation."""
    claim_id: str
    drug: str
    action: str
    claim_type: str
    candidates: List[CandidateAudit] = field(default_factory=list)
    final_status: str = "EVIDENCE_UNAVAILABLE"  # VERIFIED, EVIDENCE_UNAVAILABLE
    citation_id: Optional[str] = None
