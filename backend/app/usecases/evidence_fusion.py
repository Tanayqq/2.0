"""
Evidence Fusion Engine for MedRef v5.0 Phase 2 Architecture.

Fuses multi-collection RAG evidence chunks by deduplicating passages,
merging overlapping clinical recommendations, and resolving metadata conflicts
using strict Authority Priority hierarchy.
"""

from typing import List, Dict, Any
import re

AUTHORITY_PRIORITY = {
    "KDIGO": 1,
    "ADA": 1,
    "ACC/AHA": 1,
    "ESC": 1,
    "Surviving Sepsis": 1,
    "FDA": 2,
    "NEJM": 2,
    "Lancet": 2,
    "DailyMed": 3,
    "CDSCO": 3,
    "NFI": 4,
    "ASHP": 4
}

class EvidenceFusionEngine:
    """
    Consolidates, deduplicates, and merges multi-source clinical evidence.
    """
    
    @classmethod
    def fuse_evidence(cls, docs: List[Any]) -> List[Any]:
        if not docs:
            return []
            
        # Step 1: Deduplicate identical / near-identical text content
        seen_texts: Dict[str, Any] = {}
        for doc in docs:
            raw_text = getattr(doc, "content", getattr(doc, "text", "")).strip()
            # Normalize text for deduplication matching
            norm_text = re.sub(r'\s+', ' ', raw_text.lower()[:200])
            
            if norm_text not in seen_texts:
                seen_texts[norm_text] = doc
            else:
                existing_doc = seen_texts[norm_text]
                # Keep highest authority doc
                existing_auth = existing_doc.metadata.get("authority", "DailyMed")
                curr_auth = doc.metadata.get("authority", "DailyMed")
                
                existing_rank = AUTHORITY_PRIORITY.get(existing_auth, 99)
                curr_rank = AUTHORITY_PRIORITY.get(curr_auth, 99)
                
                if curr_rank < existing_rank:
                    seen_texts[norm_text] = doc
                    
        fused_docs = list(seen_texts.values())
        
        # Step 2: Sort fused documents by Cross-Encoder Score DESC -> Authority Priority ASC
        fused_docs.sort(
            key=lambda d: (
                getattr(d, "cross_encoder_score", 0.0) or getattr(d, "score", 0.0) or 0.0,
                -AUTHORITY_PRIORITY.get(d.metadata.get("authority", "DailyMed"), 99)
            ),
            reverse=True
        )
        
        return fused_docs
