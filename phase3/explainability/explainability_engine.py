"""
Phase 3 Pillar A: Explainability Engine & Evidence Trust Summaries.
Generates structured Trust Cards detailing why a clinical recommendation was made, citing agreeing guidelines, confidence rating, and authority consensus.
"""
from typing import Dict, Any, List

class ExplainabilityEngine:
    @staticmethod
    def generate_trust_summary(citations: List[Dict[str, Any]], intent: str, confidence: float) -> Dict[str, Any]:
        authorities = []
        sources_used = []

        for cit in citations:
            auth = cit.get("authority") or "DailyMed"
            domain = cit.get("domain") or cit.get("source") or "FDA Label"

            if auth not in authorities:
                authorities.append(auth)
            source_label = f"{auth} ({domain})" if auth != domain else auth
            if source_label not in sources_used:
                sources_used.append(source_label)

        # Compute Confidence Level
        if len(authorities) >= 2 and confidence >= 0.90:
            confidence_rating = "HIGH"
            rationale = f"Multiple independent clinical authorities ({', '.join(authorities[:3])}) agree on this recommendation."
        elif len(authorities) >= 1:
            confidence_rating = "MEDIUM"
            rationale = f"Grounded directly in {authorities[0]} prescribing guidelines and label evidence."
        else:
            confidence_rating = "LOW"
            rationale = "Derived from single-source reference label evidence."

        return {
            "sources_used": sources_used[:5],
            "authorities_count": len(authorities),
            "confidence_rating": confidence_rating,
            "rationale": rationale,
            "intent_classified": intent,
            "intent_confidence_pct": int(confidence * 100)
        }
