import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ingestion.pipeline.interfaces.source_provider import NormalizedMedicalDocument, MedicalSection
from ingestion.pipeline.chunker import MedicalSectionChunker
from ingestion.pipeline.config import ingestion_config

def test_chunker_keeps_small_section_as_single_chunk():
    chunker = MedicalSectionChunker()
    chunker.min_size = 5
    # Approx 20 words = 26 tokens (fits within limits)
    text = "Atorvastatin is indicated as an adjunct to diet to reduce elevated total-C, LDL-C, apo B, and TG levels."
    
    chunks = chunker.chunk_section("Indications", text)
    assert len(chunks) == 1
    assert chunks[0].section_title == "Indications"
    assert chunks[0].content == text
    assert chunks[0].chunk_index == 0

def test_chunker_recursive_splits_large_section():
    # Force low chunk sizes for testing splitting behavior
    chunker = MedicalSectionChunker()
    chunker.max_size = 30  # Small max size to force splitting
    chunker.target_size = 20
    chunker.min_size = 5
    chunker.overlap = 5
    
    # 3 paragraphs of text
    text = (
        "Paragraph one is a brief introduction. It has some sentences in it.\n\n"
        "Paragraph two is the middle section containing details. It describes active elements.\n\n"
        "Paragraph three contains the final warnings. Do not ignore these warnings."
    )
    
    chunks = chunker.chunk_section("Warnings", text)
    
    # Verify that it split the text into multiple chunks
    assert len(chunks) > 1
    # Check that they all relate to "Warnings"
    for c in chunks:
        assert c.section_title == "Warnings"
        # Check that token size is within max limit
        assert chunker.count_tokens(c.content) <= chunker.max_size
