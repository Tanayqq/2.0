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
        ends_with_cit = cleaned.endswith("]") and regex.search(r'(?:\[[0-9]+\])$', cleaned)
        unavailable = cleaned.endswith("*(Evidence unavailable in retrieved sources.)*")
        assert ends_with_cit or unavailable, f"Sentence does not end with citation: {sentence}"
        
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
    """Test 3: Hallucinated citation [99] -> replaced by user-friendly unavailable text."""
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
    # [99] is invalid — should be replaced with user-friendly unavailable text
    assert "[99]" not in response.answer
    assert "[Unsupported Citation Removed]" not in response.answer
    assert "Evidence unavailable in retrieved sources" in response.answer or len(response.citations) == 0
    assert len(response.citations) == 0

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

def test_section_priority_scoring():
    from app.usecases.rag_usecase import _get_section_score
    assert _get_section_score("drug_interactions") == 100
    assert _get_section_score("contraindications") == 95
    assert _get_section_score("geriatric_use") == 5
    assert _get_section_score("unknown_section") == 30

def test_content_signature_dedup():
    from app.usecases.rag_usecase import _content_sig
    sig1 = _content_sig("Metformin", "Contraindications", "Severe renal impairment eGFR < 30")
    sig2 = _content_sig("metformin", "contraindications", "Severe renal impairment  eGFR < 30 ")
    assert sig1 == sig2

def test_multi_drug_content_detection():
    from app.usecases.rag_usecase import _detect_all_drugs_in_content
    text = "Co-administration of Amiodarone and Warfarin leads to increased Digoxin level."
    found = _detect_all_drugs_in_content(text, ["amiodarone", "warfarin", "digoxin", "metformin"])
    assert set(found) == {"amiodarone", "warfarin", "digoxin"}

def test_evidence_integrity_check():
    usecase = ProcessClinicalQueryUseCase(None, None, None, None)
    good_doc = ReferenceDocument(id="uuid-1", content="Valid content meeting min length 40 characters easily", source="DailyMed", metadata={"drug_name": "Metformin", "section": "Contraindications"})
    good_doc.score = 0.8
    bad_doc_short = ReferenceDocument(id="uuid-2", content="Short", source="DailyMed", metadata={"drug_name": "Metformin", "section": "Contraindications"})
    bad_doc_short.score = 0.8
    bad_doc_no_drug = ReferenceDocument(id="uuid-3", content="Valid content meeting min length 40 characters easily", source="DailyMed", metadata={"section": "Contraindications"})
    bad_doc_no_drug.score = 0.8

    result = usecase._evidence_integrity_check([good_doc, bad_doc_short, bad_doc_no_drug], ["metformin"])
    assert len(result) == 1
    assert result[0].id == "uuid-1"

def test_scenario_6_multi_drug_citation_binding_and_guideline_separation():
    """
    Test 6: Multi-drug scenario validating:
    - Digoxin cites Digoxin chunk [3], NOT Metformin [2] or KDIGO [1]
    - Sacubitril/Valsartan cites Sacubitril chunk [4] via token matching
    - Metoprolol (no chunk) gets NO citation tag, NEVER falls back to [1]
    - Section 6 Guideline Recommendations cites KDIGO chunk [1]
    """
    from app.citation_map import CitationMap
    cmap = CitationMap()
    cmap.add_entry(uuid="uuid-1", citation_number="1", source="KDIGO 2024", drug="General Clinical Evidence", section="Guideline Recommendations", text="KDIGO 2024 CKD Management Guidelines")
    cmap.add_entry(uuid="uuid-2", citation_number="2", source="DailyMed", drug="Metformin", section="Contraindications", text="Metformin is contraindicated in eGFR < 30 mL/min due to lactic acidosis")
    cmap.add_entry(uuid="uuid-3", citation_number="3", source="DailyMed", drug="Digoxin", section="Drug Interactions", text="Amiodarone inhibits P-gp increasing Digoxin exposure")
    cmap.add_entry(uuid="uuid-4", citation_number="4", source="DailyMed", drug="Sacubitril", section="Warnings and Precautions", text="Sacubitril/Valsartan requires starting at low dose in severe renal impairment")

    citations = [
        Citation(document_id="1", source="KDIGO 2024", snippet="KDIGO 2024", uuid="uuid-1", drug="General Clinical Evidence", section="Guideline Recommendations", count=0),
        Citation(document_id="2", source="DailyMed", snippet="Metformin", uuid="uuid-2", drug="Metformin", section="Contraindications", count=0),
        Citation(document_id="3", source="DailyMed", snippet="Digoxin", uuid="uuid-3", drug="Digoxin", section="Drug Interactions", count=0),
        Citation(document_id="4", source="DailyMed", snippet="Sacubitril", uuid="uuid-4", drug="Sacubitril", section="Warnings and Precautions", count=0),
    ]

    rule_decisions = {
        "decisions": {
            "Metformin": {"action": "STOP", "reason": "eGFR 23 < 30"},
            "Digoxin": {"action": "REDUCE DOSE", "reason": "Amiodarone DDI"},
            "Sacubitril/Valsartan": {"action": "REDUCE DOSE", "reason": "eGFR 23"},
            "Metoprolol": {"action": "CONTINUE", "reason": "HFrEF Class 1A GDMT"}
        },
        "immediate_dangers": ["Severe Hyperkalemia (K+ 6.2)"],
        "major_interactions": [{"pair": "Amiodarone ↔ Digoxin", "severity": "CRITICAL", "mechanism": "P-gp inhibition"}],
        "mandatory_monitoring": ["Serum Potassium (K+): Check q24h"],
        "labs": {"egfr": 23.0, "potassium": 6.2}
    }

    sanitized = ProcessClinicalQueryUseCase._sanitize_clinical_markdown_response(
        answer_text="raw llm answer",
        rule_decisions=rule_decisions,
        citation_map=cmap,
        citations=citations,
        question_text="65 year old male patient with HFrEF, CKD stage 4 (eGFR 23), potassium 6.2"
    )

    # 1. Metformin row MUST cite [2]
    assert "| Metformin | STOP | eGFR 23 < 30 | [2] |" in sanitized

    # 2. Digoxin row MUST cite [3] (NOT [1] or [2])
    assert "| Digoxin | REDUCE DOSE | Amiodarone DDI | [3] |" in sanitized

    # 3. Sacubitril/Valsartan row MUST cite [4] (token match for Sacubitril)
    assert "| Sacubitril/Valsartan | REDUCE DOSE | eGFR 23 | [4] |" in sanitized

    # 4. Metoprolol row MUST have empty citation | | (NEVER fall back to [1])
    assert "| Metoprolol | CONTINUE | HFrEF Class 1A GDMT |  |" in sanitized

    # 5. Section 6 Guideline Recommendations MUST cite KDIGO chunk [1]
    assert "**6. Guideline Recommendations**\nClass 1A GDMT recommendations apply for HFrEF/CKD cardiorenal management per ACC/AHA 2024 & KDIGO 2024. [1]" in sanitized

if __name__ == "__main__":
    test_scenario_1_one_chunk()
    test_scenario_2_two_chunks()
    test_scenario_3_hallucinated_citation()
    test_scenario_4_bibliography_sync()
    test_scenario_5_source_citation_prevention()
    test_section_priority_scoring()
    test_content_signature_dedup()
    test_multi_drug_content_detection()
    test_evidence_integrity_check()
    test_scenario_6_multi_drug_citation_binding_and_guideline_separation()
    print("All pipeline test cases completed successfully!")


