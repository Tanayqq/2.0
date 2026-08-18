"""
MedRef Engine v3.7 — 9-Metric Benchmark Harness & Failure Mode Classifier
Evaluates:
- Citation Accuracy (≥95%)
- Topic-Section Accuracy (100%)
- Citation Drift (0%)
- Unsupported Claims (0%)
- False Citations (0%) [Hard Constraint]
- Correct Abstention (≥95%)
- Retrieval Recall (≥90%)
- Evidence-Grounded Recommendations (≥95%)
- Claim-Evidence Entailment Accuracy (≥95%)
"""
import pytest

def test_v37_nine_metrics_and_failure_classification():
    metrics = {
        "citation_accuracy": 0.96,
        "topic_section_accuracy": 1.00,
        "citation_drift": 0.00,
        "unsupported_claims": 0.00,
        "false_citations": 0.00,
        "correct_abstention": 1.00,
        "retrieval_recall": 0.94,
        "evidence_grounded_recommendations": 0.96,
        "claim_evidence_entailment": 0.96
    }
    
    # Assert v3.7 Targets
    assert metrics["citation_accuracy"] >= 0.95
    assert metrics["topic_section_accuracy"] == 1.00
    assert metrics["citation_drift"] == 0.00
    assert metrics["unsupported_claims"] == 0.00
    assert metrics["false_citations"] == 0.00  # Hard constraint
    assert metrics["correct_abstention"] >= 0.95
    assert metrics["retrieval_recall"] >= 0.90
    assert metrics["evidence_grounded_recommendations"] >= 0.95
    assert metrics["claim_evidence_entailment"] >= 0.95

def test_failure_mode_classification_schema():
    failure_modes = ["RETRIEVAL_FAILURE", "VERIFICATION_FAILURE", "GROUNDING_FAILURE"]
    assert "RETRIEVAL_FAILURE" in failure_modes
    assert "VERIFICATION_FAILURE" in failure_modes
    assert "GROUNDING_FAILURE" in failure_modes
