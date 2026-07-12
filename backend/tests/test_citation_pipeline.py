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

def assert_citation_integrity(response, expected_drug=None, expected_section=None):
    answer = response.answer
    citations = response.citations
    
    # 1. sentence has no citation -> fail
    import re as regex
    raw_sentences = regex.split(r'(?<=[.!?])\s+', answer.strip())
    sentences = [s.strip() for s in raw_sentences if s.strip()]
    
    inline_refs = set(regex.findall(r'\[([0-9]+)\]', answer))
    
    for sentence in sentences:
        if not regex.search(r'[a-zA-Z]', sentence):
            continue
        cleaned = sentence.rstrip(".!? \t\n\r")
        ends_with_cit = cleaned.endswith("]") and regex.search(r'(?:\[[0-9]+\]|\[Unsupported Citation Removed\])$', cleaned)
        assert ends_with_cit, f"Sentence does not end with citation: {sentence}"
        
    # 2. citation not in bibliography -> fail
    bib_ids = {c.document_id for c in citations}
    for inline_id in inline_refs:
        assert inline_id in bib_ids, f"Inline citation {inline_id} not in bibliography"
        
    # 3. bibliography item never cited -> fail
    for bib_id in bib_ids:
        assert bib_id in inline_refs, f"Bibliography item {bib_id} is never cited inline"
        
    # 4. FDA [see Warnings] appears -> fail
    assert not regex.search(r'\[see\s+[^\]]+\]', answer, flags=regex.IGNORECASE), "FDA bracketed cross-reference found in answer"
    
    # 5. wrong drug cited -> fail
    if expected_drug:
        for c in citations:
            assert c.drug.lower() == expected_drug.lower(), f"Wrong drug cited: {c.drug} (expected {expected_drug})"
            
    # 6. wrong section cited -> fail
    if expected_section:
        for c in citations:
            assert c.section.lower() == expected_section.lower(), f"Wrong section cited: {c.section} (expected {expected_section})"

def test_scenario_1_one_chunk():
    """Test 1: One retrieved chunk -> every sentence ends with [1]."""
    citations = [
        Citation(document_id="1", source="DailyMed", snippet="sentence one two", uuid="uuid-1", drug="Metformin", section="Contraindications", count=0)
    ]
    docs = [
        ReferenceDocument(id="uuid-1", content="sentence one two", source="DailyMed", metadata={})
    ]
    
    usecase = ProcessClinicalQueryUseCase(None, None, None, None)
    usecase._build_context = mock_build_context_generator(citations, docs).__get__(usecase, ProcessClinicalQueryUseCase)
    usecase.llm = DummyLLM("This is sentence one.[1] This is sentence two.[1]")
    
    response = usecase.execute(MedicalQuery(question="Test question"))
    assert response.answer == "This is sentence one.[1] This is sentence two.[1]"
    assert len(response.citations) == 1
    assert response.citations[0].document_id == "1"
    assert_citation_integrity(response, expected_drug="Metformin", expected_section="Contraindications")

def test_scenario_2_two_chunks():
    """Test 2: Two retrieved chunks -> Sentence.[1][2]."""
    citations = [
        Citation(document_id="1", source="DailyMed", snippet="Sentence", uuid="uuid-1", drug="Metformin", section="Contraindications", count=0),
        Citation(document_id="2", source="DailyMed", snippet="Sentence", uuid="uuid-2", drug="Metformin", section="Contraindications", count=0)
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
    assert_citation_integrity(response, expected_drug="Metformin")

def test_scenario_3_hallucinated_citation():
    """Test 3: Hallucinated citation [99] -> replaced by [Unsupported Citation Removed]."""
    citations = [
        Citation(document_id="1", source="DailyMed", snippet="Fact 1", uuid="uuid-1", drug="Metformin", section="Contraindications", count=0)
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
    assert_citation_integrity(response)

def test_scenario_4_bibliography_sync():
    """Test 4: Bibliography has 1, 2 but answer only cites [1] -> bibliography automatically becomes 1."""
    citations = [
        Citation(document_id="1", source="DailyMed", snippet="Sentence", uuid="uuid-1", drug="Metformin", section="Contraindications", count=0),
        Citation(document_id="2", source="DailyMed", snippet="Fact 2", uuid="uuid-2", drug="Metformin", section="Contraindications", count=0)
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
    assert_citation_integrity(response)

def test_scenario_5_source_citation_prevention():
    """Test 5: Source contains [see Warnings and Precautions (5.1)] -> normalized and not treated as citation."""
    citations = [
        Citation(document_id="1", source="DailyMed", snippet="Sentence warnings precautions", uuid="uuid-1", drug="Metformin", section="Contraindications", count=0)
    ]
    docs = [
        ReferenceDocument(id="uuid-1", content="Sentence warnings precautions", source="DailyMed", metadata={})
    ]
    
    usecase = ProcessClinicalQueryUseCase(None, None, None, None)
    usecase._build_context = mock_build_context_generator(citations, docs).__get__(usecase, ProcessClinicalQueryUseCase)
    usecase.llm = DummyLLM("Sentence [see Warnings and Precautions (5.1)].[1]")
    
    response = usecase.execute(MedicalQuery(question="Test question"))
    # The [see Warnings and Precautions (5.1)] should be normalized to see Warnings and Precautions (5.1)
    # The [1] should be preserved as RAG citation
    assert "see Warnings and Precautions (5.1)" in response.answer
    assert "[see Warnings and Precautions (5.1)]" not in response.answer
    assert response.answer.endswith("[1]")
    assert len(response.citations) == 1
    assert_citation_integrity(response)

if __name__ == "__main__":
    test_scenario_1_one_chunk()
    test_scenario_2_two_chunks()
    test_scenario_3_hallucinated_citation()
    test_scenario_4_bibliography_sync()
    test_scenario_5_source_citation_prevention()
    print("All pipeline test cases completed successfully!")
