import pytest
import sys
import os
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ingestion.pipeline.interfaces.source_provider import NormalizedMedicalDocument, MedicalSection
from ingestion.pipeline.validator import MedicalValidator
from ingestion.pipeline.config import ingestion_config

def test_validator_rejects_empty_drug_or_source():
    v = MedicalValidator()
    
    # Missing drug
    doc = NormalizedMedicalDocument(
        drug="",
        generic_name="Generic",
        source="test",
        country="US",
        version="1",
        ingested_at="2023-10-01T00:00:00Z",
        sections=[MedicalSection(title="Indications", content="Valid content of reasonable length")]
    )
    is_valid, reason = v.validate(doc)
    assert not is_valid
    assert "drug name" in reason.lower()

    # Missing source
    doc.drug = "Valid Drug"
    doc.source = ""
    is_valid, reason = v.validate(doc)
    assert not is_valid
    assert "source" in reason.lower()

def test_validator_rejects_empty_or_short_sections():
    v = MedicalValidator()
    
    # Empty section content
    doc = NormalizedMedicalDocument(
        drug="TestDrug",
        generic_name="Generic",
        source="test",
        country="US",
        version="1",
        ingested_at="2023-10-01T00:00:00Z",
        sections=[MedicalSection(title="Indications", content="")]
    )
    is_valid, reason = v.validate(doc)
    assert not is_valid
    assert "empty" in reason.lower() or "0 chars" in reason.lower()
    
    # Tiny section content
    doc.sections = [MedicalSection(title="Indications", content="abc")]
    is_valid, reason = v.validate(doc)
    assert not is_valid
    assert "too short" in reason.lower() or "chars" in reason.lower() or "truncated" in reason.lower()

def test_validator_sends_to_dlq(tmp_path):
    # Set DLQ directory to a temp path for testing
    old_dlq = ingestion_config.DLQ_DIR
    ingestion_config.DLQ_DIR = str(tmp_path)
    
    v = MedicalValidator()
    doc = NormalizedMedicalDocument(
        drug="TestDrug",
        generic_name="Generic",
        source="test",
        country="US",
        version="1",
        ingested_at="2023-10-01T00:00:00Z",
        sections=[MedicalSection(title="Indications", content="abc")]  # fails validation (too short)
    )
    
    is_valid, reason = v.validate(doc)
    assert not is_valid
    
    v.send_to_dlq(doc, reason)
    
    # Check if file was created in temp DLQ directory
    files = os.listdir(str(tmp_path))
    assert len(files) == 1
    assert files[0].startswith("testdrug_test_failed_")
    
    with open(os.path.join(str(tmp_path), files[0]), "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["error_reason"] == reason
        assert data["document"]["drug"] == "TestDrug"
        
    # Restore config
    ingestion_config.DLQ_DIR = old_dlq

# Make sure json is imported for load in test_validator_sends_to_dlq
import json
