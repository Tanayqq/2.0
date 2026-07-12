import sys
import os
import pytest

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.domain.models import Citation, MedicalQuery, ReferenceDocument
from app.usecases.rag_usecase import ProcessClinicalQueryUseCase

class DummyLLM:
    def __init__(self, answer: str):
        self.answer = answer
    def generate(self, prompt: str) -> str:
        return self.answer

def mock_build_context_generator(citations, docs):
    def mock_build_context(self, query):
        from app.citation_map import CitationMap
        cmap = CitationMap()
        for c in citations:
            cmap.add_entry(
                uuid=c.uuid or "uuid-placeholder",
                citation_number=c.document_id,
                source=c.source,
                drug=c.drug or "Metformin",
                section=c.section or "Contraindications",
                text=c.snippet,
                similarity=c.similarity
            )
        return "Context", citations, docs, 0.1, "High", {
            "rank_scores": [0.9],
            "retrieval_latency_sec": 0.1,
            "total_retrieved": len(docs),
            "total_filtered": len(docs),
            "threshold_applied": 0.75,
            "confidence": "High",
            "avg_similarity": 0.9,
            "retrieved_count": len(docs),
            "resolved_drug": "Metformin",
            "detected_sections": [],
            "raw_retrieved_log": [],
            "rejection_log": []
        }, cmap
    return mock_build_context

def test_scenario_1_valid_citation():
    """Test 1: Sentence.[1] should preserve the citation."""
    citations = [
        Citation(document_id="1", source="DailyMed", snippet="Sentence", uuid="uuid-1", count=0)
    ]
    docs = [
        ReferenceDocument(id="uuid-1", content="Sentence", source="DailyMed", metadata={})
    ]
    
    usecase = ProcessClinicalQueryUseCase(None, None, None, None)
    usecase._build_context = mock_build_context_generator(citations, docs).__get__(usecase, ProcessClinicalQueryUseCase)
    usecase.llm = DummyLLM("Sentence.[1]")
    
    response = usecase.execute(MedicalQuery(question="Test question"))
    assert response.answer == "Sentence.[1]"
    assert len(response.citations) == 1
    assert response.citations[0].document_id == "1"

def test_scenario_2_multiple_citations():
    """Test 2: Sentence.[1][2] should preserve both citations."""
    citations = [
        Citation(document_id="1", source="DailyMed", snippet="Sentence", uuid="uuid-1", count=0),
        Citation(document_id="2", source="DailyMed", snippet="Sentence", uuid="uuid-2", count=0)
    ]
    docs = [
        ReferenceDocument(id="uuid-1", content="Sentence", source="DailyMed", metadata={}),
        ReferenceDocument(id="uuid-2", content="Sentence", source="DailyMed", metadata={})
    ]
    
    usecase = ProcessClinicalQueryUseCase(None, None, None, None)
    usecase._build_context = mock_build_context_generator(citations, docs).__get__(usecase, ProcessClinicalQueryUseCase)
    usecase.llm = DummyLLM("Sentence.[1][2]")
    
    response = usecase.execute(MedicalQuery(question="Test question"))
    assert response.answer == "Sentence.[1][2]"
    assert len(response.citations) == 2

def test_scenario_3_no_citation():
    """Test 3: Sentence. (no citation) should trigger Validator FAIL."""
    citations = [
        Citation(document_id="1", source="DailyMed", snippet="Fact 1", uuid="uuid-1", count=0)
    ]
    docs = [
        ReferenceDocument(id="uuid-1", content="Fact 1", source="DailyMed", metadata={})
    ]
    
    usecase = ProcessClinicalQueryUseCase(None, None, None, None)
    usecase._build_context = mock_build_context_generator(citations, docs).__get__(usecase, ProcessClinicalQueryUseCase)
    usecase.llm = DummyLLM("Sentence.")
    
    response = usecase.execute(MedicalQuery(question="Test question"))
    assert response.answer == "Unable to generate a fully grounded answer from the indexed corpus."
    assert len(response.citations) == 0
    assert response.metadata.get("validation_failed") is not None

def test_scenario_4_bibliography_sync():
    """Test 4: Bibliography with 1, 2 but answer only cites [1] -> bibliography automatically becomes 1."""
    citations = [
        Citation(document_id="1", source="DailyMed", snippet="Sentence", uuid="uuid-1", count=0),
        Citation(document_id="2", source="DailyMed", snippet="Fact 2", uuid="uuid-2", count=0)
    ]
    docs = [
        ReferenceDocument(id="uuid-1", content="Sentence", source="DailyMed", metadata={}),
        ReferenceDocument(id="uuid-2", content="Fact 2", source="DailyMed", metadata={})
    ]
    
    usecase = ProcessClinicalQueryUseCase(None, None, None, None)
    usecase._build_context = mock_build_context_generator(citations, docs).__get__(usecase, ProcessClinicalQueryUseCase)
    usecase.llm = DummyLLM("Sentence.[1]")
    
    response = usecase.execute(MedicalQuery(question="Test question"))
    assert response.answer == "Sentence.[1]"
    assert len(response.citations) == 1
    assert response.citations[0].uuid == "uuid-1"

def test_scenario_5_hallucinated_citation():
    """Test 5: Hallucinated citation [99] -> Sentence.[Unsupported Citation Removed]."""
    citations = [
        Citation(document_id="1", source="DailyMed", snippet="Fact 1", uuid="uuid-1", count=0)
    ]
    docs = [
        ReferenceDocument(id="uuid-1", content="Fact 1", source="DailyMed", metadata={})
    ]
    
    usecase = ProcessClinicalQueryUseCase(None, None, None, None)
    usecase._build_context = mock_build_context_generator(citations, docs).__get__(usecase, ProcessClinicalQueryUseCase)
    usecase.llm = DummyLLM("Sentence.[99]")
    
    response = usecase.execute(MedicalQuery(question="Test question"))
    assert response.answer == "Sentence.[Unsupported Citation Removed]"
    assert len(response.citations) == 0

if __name__ == "__main__":
    test_scenario_1_valid_citation()
    test_scenario_2_multiple_citations()
    test_scenario_3_no_citation()
    test_scenario_4_bibliography_sync()
    test_scenario_5_hallucinated_citation()
    print("All test cases completed successfully!")
