import structlog
from typing import List, Dict, Any
from app.domain.models import ReferenceDocument, PatientProfile
from ingestion.pipeline.source_registry import SourceRegistry

logger = structlog.get_logger()

class EvidenceRankingEngine:
    """
    5-Factor Evidence Ranking Engine:
    Final Score = Semantic Score * Authority Score * Freshness * Section Importance * Patient Context Weight
    """
    SECTION_WEIGHTS = {
        "boxed_warning": 1.5,
        "warnings": 1.4,
        "contraindications": 1.4,
        "dosage_and_administration": 1.3,
        "indications": 1.2,
        "mechanism_of_action": 1.0,
        "adverse_reactions": 1.1,
        "drug_interactions": 1.3,
        "pregnancy": 1.4,
        "renal_impairment": 1.4
    }

    @classmethod
    def rank_documents(
        cls, 
        docs: List[ReferenceDocument], 
        requested_section: str = "", 
        patient_profile: PatientProfile = None
    ) -> List[ReferenceDocument]:
        logger.info("ranking_evidence_documents", doc_count=len(docs))
        
        for doc in docs:
            meta = doc.metadata or {}
            
            # 1. Semantic Score (0.0 - 1.0)
            semantic_score = doc.cross_encoder_score if doc.cross_encoder_score is not None else (doc.score or 0.70)
            
            # 2. Authority Score (Normalized 0.8 - 1.0 based on priority)
            authority = meta.get("authority", "DailyMed")
            priority = SourceRegistry.get_authority_priority(authority)
            authority_score = priority / 100.0
            
            # 3. Freshness Factor (Default 1.0)
            freshness = meta.get("freshness_factor", 1.0)
            
            # 4. Section Importance Weight
            sec = (meta.get("canonical_section") or meta.get("section") or "").lower()
            sec_weight = cls.SECTION_WEIGHTS.get(sec, 1.0)
            if requested_section and sec == requested_section.lower():
                sec_weight *= 1.2
                
            # 5. Patient Context Weight
            context_weight = 1.0
            if patient_profile:
                if patient_profile.pregnancy and sec == "pregnancy":
                    context_weight = 1.5
                if patient_profile.eGFR and patient_profile.eGFR < 45 and sec == "renal_impairment":
                    context_weight = 1.5
                if patient_profile.active_medications and sec == "drug_interactions":
                    context_weight = 1.3
                    
            final_score = semantic_score * authority_score * freshness * sec_weight * context_weight
            doc.score = round(final_score, 4)

        # Sort documents by final weighted score descending
        ranked = sorted(docs, key=lambda x: x.score or 0.0, reverse=True)
        return ranked
