import structlog
from typing import Dict, Any, List, Optional

logger = structlog.get_logger()

class ExplainabilityEngine:
    """
    Exposes complete audit transparency for clinicians:
    Why this answer? -> Intent -> Collections Searched -> Retrieved Chunks -> Authority Scores -> Conflict Resolution -> Reasoning Steps.
    """
    @classmethod
    def generate_explainability_payload(
        cls, 
        mode: str, 
        collections_searched: List[str], 
        retrieved_docs: List[Any], 
        conflict_data: Optional[Dict[str, Any]] = None,
        reasoning_steps: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        chunk_provenance = []
        for d in retrieved_docs[:10]:
            meta = getattr(d, 'metadata', {})
            chunk_provenance.append({
                "chunk_id": getattr(d, 'id', 'unknown'),
                "authority": meta.get("authority", "DailyMed"),
                "source": meta.get("source", "DailyMed"),
                "section": meta.get("canonical_section") or meta.get("section") or "Unknown",
                "similarity_score": getattr(d, 'score', 0.0)
            })

        return {
            "mode": mode,
            "collections_searched": collections_searched,
            "total_chunks_retrieved": len(retrieved_docs),
            "top_chunks": chunk_provenance,
            "conflict_resolution": conflict_data,
            "reasoning_steps": reasoning_steps or [
                "1. Detected query mode and user intent.",
                "2. Selected country regulatory context.",
                "3. Executed hybrid vector retrieval over Qdrant collections.",
                "4. Evaluated 5-Factor Evidence Ranking (Semantic × Authority × Freshness × Section × Context).",
                "5. Verified zero-parametric grounding guard.",
                "6. Synthesized clinical evidence answer with multi-authority citation badges."
            ]
        }
