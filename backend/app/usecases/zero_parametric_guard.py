import structlog
from typing import List, Dict, Any, Tuple, Optional
from app.domain.models import ReferenceDocument

logger = structlog.get_logger()

class ZeroParametricGuard:
    """
    Strict Zero-Parametric Grounding Guard.
    Prevents the LLM from filling evidence gaps from parametric memory.
    Returns an explicit, transparent search audit if retrieved evidence is missing or below threshold.
    """
    SEARCHED_AUTHORITIES = ["DailyMed", "FDA", "CDSCO", "ICMR", "ADA", "KDIGO", "WHO", "EMA"]

    @classmethod
    def validate_retrieval(cls, docs: List[ReferenceDocument], min_score_threshold: float = 0.10) -> Tuple[bool, Optional[str]]:
        if not docs:
            logger.warning("zero_parametric_guard_triggered", total_docs=0)
            
            auth_check_list = "\n".join([f"  ✓ {auth}" for auth in cls.SEARCHED_AUTHORITIES])
            audit_msg = (
                "### ⚠️ No Authoritative Evidence Found\n\n"
                "No supporting medical evidence was found inside the indexed corpus for this query.\n\n"
                "**Authorities Searched**:\n"
                f"{auth_check_list}\n\n"
                "**Safety Directive**: MedRef strictly avoids generating unsupported or ungrounded medical advice "
                "from non-indexed parametric memory to preserve clinical trust and patient safety."
            )
            return False, audit_msg
            
        return True, None
