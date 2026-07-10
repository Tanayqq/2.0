import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ingestion.pipeline.interfaces.source_provider import NormalizedMedicalDocument, MedicalSection
from ingestion.pipeline.parser import MedicalParser

def test_medical_parser_standardizes_titles():
    doc = NormalizedMedicalDocument(
        drug="TestDrug",
        generic_name="GenericTest",
        source="test",
        country="US",
        version="1.0",
        effective_date="2023-10-01",
        revision="123",
        ingested_at="2023-10-01T00:00:00Z",
        sections=[
            MedicalSection(title="indications and usage", content="This drug is indicated for..."),
            MedicalSection(title="side effects", content="Side effects include nausea..."),
            MedicalSection(title="Unknown Section Title", content="Some other content here...")
        ]
    )
    
    parser = MedicalParser()
    parsed_doc = parser.parse(doc)
    
    # Assert standardizations
    assert len(parsed_doc.sections) == 3
    assert parsed_doc.sections[0].title == "Indications"
    assert parsed_doc.sections[1].title == "Adverse Reactions"
    assert parsed_doc.sections[2].title == "Unknown Section Title"

def test_medical_parser_cleans_text_and_deduplicates():
    doc = NormalizedMedicalDocument(
        drug="TestDrug",
        generic_name="GenericTest",
        source="test",
        country="US",
        version="1.0",
        effective_date="2023-10-01",
        revision="123",
        ingested_at="2023-10-01T00:00:00Z",
        sections=[
            MedicalSection(title="Indications", content="   Some text with tags <p>and extra spaces</p>   \n\n\n\nmore text."),
            MedicalSection(title="indications and usage", content="Short content")  # Duplicate standard title
        ]
    )
    
    parser = MedicalParser()
    parsed_doc = parser.parse(doc)
    
    # Assert deduplication (should keep the longer text since title standardizes to "Indications")
    assert len(parsed_doc.sections) == 1
    assert parsed_doc.sections[0].title == "Indications"
    assert "Some text with tags and extra spaces\n\nmore text." in parsed_doc.sections[0].content
