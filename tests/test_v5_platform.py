import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from ingestion.pipeline.source_registry import SourceRegistry
from app.usecases.conversation_engine import ConversationEngine
from app.usecases.patient_memory import PatientMemoryStore
from app.usecases.recommendation_engine import RecommendationModule
from app.usecases.clinical_workflow import ClinicalWorkflowEngine
from app.usecases.evidence_ranker import EvidenceRankingEngine
from app.usecases.zero_parametric_guard import ZeroParametricGuard
from app.usecases.conflict_engine import MultiAuthorityConflictEngine
from app.usecases.explainability_engine import ExplainabilityEngine
from app.usecases.intent_router import IntentRouter
from app.domain.models import ReferenceDocument, PatientProfile

def test_source_registry():
    meta = SourceRegistry.get_source_metadata("DailyMed")
    assert meta is not None
    assert meta.authority == "FDA"
    assert meta.priority == 98
    assert SourceRegistry.get_authority_priority("CDSCO") == 93

def test_conversation_engine_slot_filling():
    engine = ConversationEngine()
    result = engine.process_intake("I have a fever")
    assert result["status"] == "NEED_CLARIFICATION"
    assert "duration_days" in result["pending_slots"]
    assert "How many days" in result["next_question"]

def test_patient_memory_store():
    store = PatientMemoryStore()
    profile = PatientProfile(age=67, gender="Male", eGFR=42.0, active_medications=["warfarin"])
    store.save_profile("p-101", profile)
    retrieved = store.get_profile("p-101")
    assert retrieved is not None
    assert retrieved.age == 67
    assert retrieved.eGFR == 42.0

def test_recommendation_module():
    profile = PatientProfile(age=67, eGFR=25.0, pregnancy=True)
    rec = RecommendationModule.recommend_therapy("chest pain", profile)
    assert len(rec["first_line_drugs"]) > 0
    assert any("Contraindicated" in c for c in rec["contraindicated_drugs"])

def test_clinical_workflow_engine():
    workflow = ClinicalWorkflowEngine.execute_workflow("chest pain")
    assert workflow is not None
    assert "Acute Chest Pain" in workflow["title"]
    assert len(workflow["steps"]) >= 5

def test_evidence_ranking_engine():
    doc1 = ReferenceDocument(id="1", content="test", source="DailyMed", metadata={"authority": "FDA", "section": "warnings"}, score=0.85)
    doc2 = ReferenceDocument(id="2", content="test", source="CDSCO", metadata={"authority": "CDSCO", "section": "overview"}, score=0.85)
    profile = PatientProfile(age=67, eGFR=20.0)
    ranked = EvidenceRankingEngine.rank_documents([doc1, doc2], requested_section="warnings", patient_profile=profile)
    assert len(ranked) == 2
    assert ranked[0].id == "1"  # Warnings section + FDA priority ranks higher

def test_zero_parametric_guard():
    empty_docs = []
    is_valid, audit_text = ZeroParametricGuard.validate_retrieval(empty_docs)
    assert is_valid is False
    assert "No Authoritative Evidence Found" in audit_text
    assert "DailyMed" in audit_text
    assert "CDSCO" in audit_text

def test_conflict_engine():
    doc1 = ReferenceDocument(id="1", content="FDA approved drug X", source="DailyMed", metadata={"authority": "FDA"})
    doc2 = ReferenceDocument(id="2", content="CDSCO restricted drug X under Schedule H1", source="CDSCO", metadata={"authority": "CDSCO"})
    conflict = MultiAuthorityConflictEngine.detect_and_resolve_conflicts([doc1, doc2])
    assert conflict is not None
    assert conflict["has_conflict"] is True
    assert len(conflict["table_data"]) == 2

def test_explainability_engine():
    payload = ExplainabilityEngine.generate_explainability_payload("DRUG_CHAT", ["openfda_labels"], [])
    assert payload["mode"] == "DRUG_CHAT"
    assert len(payload["reasoning_steps"]) >= 4

def test_intent_router_9_modes():
    assert IntentRouter.classify_intent("Compare Ozempic vs Mounjaro") == "COMPARISON"
    assert IntentRouter.classify_intent("Can I take Warfarin together with Aspirin?") == "INTERACTION_CHECK"
    assert IntentRouter.classify_intent("Show me ADA 2026 guidelines for diabetes") == "CLINICAL_GUIDELINE"
    assert IntentRouter.classify_intent("Latest NEJM trial for Semaglutide") == "RESEARCH_LITERATURE"
    assert IntentRouter.classify_intent("Metformin dosing") == "DRUG_CHAT"

if __name__ == "__main__":
    pytest.main(["-v", __file__])
