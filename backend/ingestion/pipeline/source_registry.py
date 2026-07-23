from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import datetime

@dataclass
class SourceMetadata:
    source: str                 # e.g. "DailyMed", "openFDA", "CDSCO", "PubMed"
    source_type: str            # e.g. "Drug Label", "Disease Guideline", "Interaction DB", "Literature"
    authority: str              # e.g. "FDA", "CDSCO", "ICMR", "ADA", "KDIGO", "WHO", "EMA"
    country: str                # e.g. "US", "IN", "GLOBAL"
    version: str                # e.g. "2026-07"
    priority: int               # e.g. FDA=100, DailyMed=98, ICMR=96, WHO=95, EMA=94, CDSCO=93, RxNorm=90
    status: str = "ACTIVE"      # "ACTIVE", "ARCHIVED", "SUPERSEDED"
    last_updated: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat() + "Z")

class SourceRegistry:
    """
    Central registry defining metadata standards for all data sources feeding the 6 Knowledge Domains.
    """
    REGISTRY: Dict[str, SourceMetadata] = {
        "DailyMed": SourceMetadata(
            source="DailyMed",
            source_type="Drug Label",
            authority="FDA",
            country="US",
            version="2026-07",
            priority=98
        ),
        "openFDA": SourceMetadata(
            source="openFDA",
            source_type="Drug Label Metadata",
            authority="FDA",
            country="US",
            version="2026-07",
            priority=100
        ),
        "CDSCO": SourceMetadata(
            source="CDSCO",
            source_type="Drug Regulatory & Approvals",
            authority="CDSCO",
            country="IN",
            version="2026-07",
            priority=93
        ),
        "NFI": SourceMetadata(
            source="National Formulary of India",
            source_type="Drug Formulary",
            authority="CDSCO",
            country="IN",
            version="2026-01",
            priority=92
        ),
        "ICMR": SourceMetadata(
            source="ICMR Guidelines",
            source_type="Disease Guideline",
            authority="ICMR",
            country="IN",
            version="2026-05",
            priority=96
        ),
        "NTEP": SourceMetadata(
            source="NTEP Tuberculosis Guidelines",
            source_type="National Treatment Regimen",
            authority="MoHFW",
            country="IN",
            version="2026-01",
            priority=95
        ),
        "ADA": SourceMetadata(
            source="ADA Standards of Care",
            source_type="Disease Guideline",
            authority="ADA",
            country="GLOBAL",
            version="2026-01",
            priority=97
        ),
        "KDIGO": SourceMetadata(
            source="KDIGO Clinical Practice Guideline",
            source_type="Disease Guideline",
            authority="KDIGO",
            country="GLOBAL",
            version="2026-03",
            priority=96
        ),
        "PubMed": SourceMetadata(
            source="PubMed Medline",
            source_type="Primary Literature",
            authority="NIH",
            country="GLOBAL",
            version="2026-07",
            priority=85
        )
    }

    @classmethod
    def get_source_metadata(cls, source_name: str) -> Optional[SourceMetadata]:
        return cls.REGISTRY.get(source_name)

    @classmethod
    def get_authority_priority(cls, authority_name: str) -> int:
        for src in cls.REGISTRY.values():
            if src.authority.upper() == authority_name.upper():
                return src.priority
        return 80  # Default fallback priority
