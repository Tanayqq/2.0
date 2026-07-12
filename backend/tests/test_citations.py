import sys
import os
import re

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.domain.models import Citation, MedicalQuery, ReferenceDocument
from app.usecases.rag_usecase import ProcessClinicalQueryUseCase

class DummyLLM:
    def __init__(self, answer: str):
        self.answer = answer
    def generate(self, prompt: str) -> str:
        return self.answer

def test_citation_post_processing():
    # Setup process use case with dummy components
    usecase = ProcessClinicalQueryUseCase(
        llm_provider=None,
        vector_db=None,
        embedding_model=None,
        cross_encoder=None
    )
    
    # Mock citations list (from context)
    mock_citations = [
        Citation(document_id="1", source="DailyMed", snippet="Fact 1", uuid="uuid-1", drug="Metformin", section="Mechanism", similarity=0.9, count=0),
        Citation(document_id="2", source="DailyMed", snippet="Fact 2", uuid="uuid-2", drug="Metformin", section="Dosing", similarity=0.8, count=0),
        Citation(document_id="3", source="DailyMed", snippet="Fact 3", uuid="uuid-3", drug="Metformin", section="Adverse", similarity=0.75, count=0)
    ]
    
    # Test case 1: Space orphans and consecutive duplicates
    raw_answer = "Metformin is useful.   [1]   [1] Also it helps. \n\n [2] And final. [3][1]"
    usecase.llm = DummyLLM(raw_answer)
    
    # Mock execute path validation
    response = usecase.execute(MedicalQuery(question="Test question"))
    print("Test Case 1 Answer:", response.answer)
    print("Test Case 1 Citations:")
    for c in response.citations:
        print(f"  [{c.document_id}] UUID: {c.uuid} | Count: {c.count}")
        
    assert response.answer == "Metformin is useful.[1] Also it helps.[2] And final.[3][1]"
    assert len(response.citations) == 3
    # Check counts
    c1 = next(c for c in response.citations if c.uuid == "uuid-1")
    c2 = next(c for c in response.citations if c.uuid == "uuid-2")
    c3 = next(c for c in response.citations if c.uuid == "uuid-3")
    assert c1.count == 2
    assert c2.count == 1
    assert c3.count == 1

    # Test case 2: Malformed formats ([Doc 1], [Document ID: 1])
    raw_answer_malformed = "Lisinopril is safe [Document 1]. It causes cough [Doc 2] and [Document ID: 1]."
    usecase.llm = DummyLLM(raw_answer_malformed)
    response_malformed = usecase.execute(MedicalQuery(question="Test question"))
    print("\nTest Case 2 Answer:", response_malformed.answer)
    assert response_malformed.answer == "Lisinopril is safe[1]. It causes cough[2] and[1]."

    # Test case 3: Vancouver style renumbering order of appearance
    # If LLM cites original [2] first, then original [1] second
    raw_answer_vancouver = "Metformin dosing is twice daily.[2] Mechanism is complex.[1]"
    usecase.llm = DummyLLM(raw_answer_vancouver)
    response_vancouver = usecase.execute(MedicalQuery(question="Test question"))
    print("\nTest Case 3 Answer (Vancouver):", response_vancouver.answer)
    print("Test Case 3 Citations (Vancouver):")
    for c in response_vancouver.citations:
        print(f"  [{c.document_id}] UUID: {c.uuid} | Count: {c.count}")
        
    # Standardized: the first inline citation must become [1], the second [2]
    assert response_vancouver.answer == "Metformin dosing is twice daily.[1] Mechanism is complex.[2]"
    # The bibliography list must match this order
    assert response_vancouver.citations[0].uuid == "uuid-2" # originally [2] (dosing)
    assert response_vancouver.citations[0].document_id == "1"
    assert response_vancouver.citations[1].uuid == "uuid-1" # originally [1] (mechanism)
    assert response_vancouver.citations[1].document_id == "2"

    print("\nAll unit tests passed successfully!")

# Mock ProcessClinicalQueryUseCase's _build_context to return our fixed mock values
def mock_build_context(self, query):
    mock_citations = [
        Citation(document_id="1", source="DailyMed", snippet="Fact 1", uuid="uuid-1", drug="Metformin", section="Mechanism", similarity=0.9, count=0),
        Citation(document_id="2", source="DailyMed", snippet="Fact 2", uuid="uuid-2", drug="Metformin", section="Dosing", similarity=0.8, count=0),
        Citation(document_id="3", source="DailyMed", snippet="Fact 3", uuid="uuid-3", drug="Metformin", section="Adverse", similarity=0.75, count=0)
    ]
    mock_docs = [
        ReferenceDocument(id="uuid-1", content="Fact 1", source="DailyMed", metadata={}),
        ReferenceDocument(id="uuid-2", content="Fact 2", source="DailyMed", metadata={}),
        ReferenceDocument(id="uuid-3", content="Fact 3", source="DailyMed", metadata={})
    ]
    from app.citation_map import CitationMap
    cmap = CitationMap()
    for c in mock_citations:
        cmap.add_entry(
            uuid=c.uuid,
            citation_number=c.document_id,
            source=c.source,
            drug=c.drug or "Metformin",
            section=c.section or "Contraindications",
            text=c.snippet,
            similarity=c.similarity
        )
    return "Context", mock_citations, mock_docs, 0.1, "High", {
        "detected_sections": []
    }, cmap
    
ProcessClinicalQueryUseCase._build_context = mock_build_context

if __name__ == "__main__":
    test_citation_post_processing()
