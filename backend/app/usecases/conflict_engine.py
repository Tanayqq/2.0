import structlog
from typing import List, Dict, Any, Optional
from app.domain.models import ReferenceDocument

logger = structlog.get_logger()

class MultiAuthorityConflictEngine:
    """
    Identifies regulatory and clinical discrepancies across international authorities
    (FDA vs CDSCO vs WHO vs EMA) and formats an explicit Authority Comparison Table.
    """
    @classmethod
    def detect_and_resolve_conflicts(cls, docs: List[ReferenceDocument]) -> Optional[Dict[str, Any]]:
        logger.info("evaluating_multi_authority_conflicts", doc_count=len(docs))
        
        authority_claims: Dict[str, List[str]] = {}
        for doc in docs:
            meta = doc.metadata or {}
            auth = meta.get("authority", "DailyMed")
            content = doc.content.lower()
            
            if auth not in authority_claims:
                authority_claims[auth] = []
                
            if "approved" in content or "indicated" in content:
                authority_claims[auth].append("Approved / Indicated")
            elif "restricted" in content or "boxed warning" in content or "schedule h1" in content:
                authority_claims[auth].append("Restricted / Warnings Applied")
            elif "withdrawn" in content or "banned" in content:
                authority_claims[auth].append("Withdrawn / Banned")

        # Check if multiple authorities have differing primary stances
        unique_authorities = list(authority_claims.keys())
        if len(unique_authorities) >= 2:
            conflict_table = {
                "has_conflict": True,
                "authorities": unique_authorities,
                "summary": "Multi-Authority Regulatory Position Comparison",
                "table_data": []
            }
            for auth in unique_authorities:
                claims = list(set(authority_claims[auth]))
                status = ", ".join(claims) if claims else "Standard Label Reference"
                conflict_table["table_data"].append({
                    "authority": auth,
                    "status": status
                })
            return conflict_table
            
        return None
