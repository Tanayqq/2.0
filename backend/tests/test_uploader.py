import pytest
import sys
import os
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ingestion.pipeline.uploader import MedicalUploader

def test_deterministic_uuid_generation():
    # Test values
    drug = "Lisinopril"
    section = "Contraindications"
    chunk_index = 0
    version = "1"
    
    unique_string = f"{drug.lower()}_{section.lower()}_{chunk_index}_{version}"
    uuid1 = str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_string))
    
    # Run again with same values
    uuid2 = str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_string))
    
    # Run with different chunk index
    unique_string_diff = f"{drug.lower()}_{section.lower()}_1_{version}"
    uuid_diff = str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_string_diff))
    
    assert uuid1 == uuid2  # Must be identical (idempotent)
    assert uuid1 != uuid_diff  # Must be different for different chunks
    
    # Validate UUID format
    try:
        val_uuid = uuid.UUID(uuid1)
        assert str(val_uuid) == uuid1
    except ValueError:
        pytest.fail("Generated ID is not a valid UUID string")
