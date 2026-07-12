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
    
    # Assert standardizations (now lowercase canonical)
    assert len(parsed_doc.sections) == 3
    assert parsed_doc.sections[0].title == "indications"
    assert parsed_doc.sections[1].title == "adverse reactions"
    assert parsed_doc.sections[2].title == "unknown section title"

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
    
    # Assert deduplication (should keep the longer text since title standardizes to "indications")
    assert len(parsed_doc.sections) == 1
    assert parsed_doc.sections[0].title == "indications"
    assert "Some text with tags and extra spaces\n\nmore text." in parsed_doc.sections[0].content

def test_medical_parser_discards_noise_sections():
    """Parser must remove patient package insert, highlights, and other noise sections."""
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
            MedicalSection(title="4 Contraindications", content="Do not use in patients with severe renal impairment."),
            MedicalSection(title="SPL Patient Package Insert", content="This leaflet summarizes the most important information..."),
            MedicalSection(title="Full Prescribing Information", content="Full prescribing information: Contents"),
            MedicalSection(title="Highlights of Prescribing Information", content="Some highlight text here"),
            MedicalSection(title="Warnings and Precautions", content="Use caution in patients with hepatic impairment.")
        ]
    )

    parser = MedicalParser()
    parsed_doc = parser.parse(doc)

    titles = [s.title for s in parsed_doc.sections]
    # Noise sections must be gone
    assert "_excluded" not in titles
    assert "spl patient package insert" not in titles
    assert "patient package insert" not in titles
    assert "highlights of prescribing information" not in titles
    assert "full prescribing information" not in titles
    # Clinical sections must be present as lowercase canonical
    assert "contraindications" in titles
    assert "warnings" in titles
    assert len(parsed_doc.sections) == 2

