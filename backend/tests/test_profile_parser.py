import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ingestion.pipeline.profile_parser import DeterministicProfileParser
from ingestion.pipeline.interfaces.source_provider import NormalizedMedicalDocument, MedicalSection
from app.domain.profile_schema import DrugIdentityProfile, DrugClinicalProfile

def test_profile_parser_extracts_identity_correctly():
    parser = DeterministicProfileParser()
    
    doc = NormalizedMedicalDocument(
        drug="Metformin",
        generic_name="METFORMIN HYDROCHLORIDE",
        source="DailyMed",
        country="US",
        version="1",
        effective_date="2026-07-15",
        revision="set-id-123",
        ingested_at="2026-07-15T00:00:00Z",
        sections=[
            MedicalSection(title="Clinical Pharmacology", content="Metformin is a biguanide antihyperglycemic agent.")
        ]
    )
    
    identity = parser.build_identity_profile(doc)
    
    assert isinstance(identity, DrugIdentityProfile)
    assert identity.entity_id == "drug:metformin"
    assert identity.generic_name.value == "METFORMIN HYDROCHLORIDE"
    assert identity.prescription_status.value == "Prescription Only"
    assert identity.generic_name.confidence == "deterministic"
    assert identity.generic_name.authority == "FDA"

def test_profile_parser_extracts_clinical_correctly():
    parser = DeterministicProfileParser()
    
    doc = NormalizedMedicalDocument(
        drug="Metformin",
        generic_name="METFORMIN HYDROCHLORIDE",
        source="DailyMed",
        country="US",
        version="1",
        effective_date="2026-07-15",
        revision="set-id-123",
        ingested_at="2026-07-15T00:00:00Z",
        sections=[
            MedicalSection(title="Mechanism of Action", content="It decreases hepatic glucose production and improves insulin sensitivity."),
            MedicalSection(title="Contraindications", content="Contraindicated in patients with: 1. Severe renal impairment. 2. Metabolic acidosis."),
            MedicalSection(title="Warnings", content="- Metformin-associated lactic acidosis. - Hypoxic states."),
            MedicalSection(title="Dosage and Administration", content="The maximum daily dose is 2550 mg once daily orally. Take with meals."),
            MedicalSection(title="Adverse Reactions", content="Common side effects include nausea and diarrhea. Serious lactic acidosis is rare.")
        ]
    )
    
    clinical = parser.build_clinical_profile(doc)
    
    assert isinstance(clinical, DrugClinicalProfile)
    assert clinical.mechanism.value == "It decreases hepatic glucose production and improves insulin sensitivity."
    assert any("renal impairment" in item.lower() for item in clinical.contraindications.value)
    assert any("lactic acidosis" in item.lower() for item in clinical.warnings.value)
    assert clinical.dosing["maximum_dose"].value == "2550 mg"
    assert clinical.dosing["route"].value == "Oral"
    assert clinical.side_effects["common"].value is not None
    assert "nausea" in clinical.side_effects["common"].value.lower()
    assert clinical.side_effects["rare"].value == "Not available"  # Not explicitly matched by simple regex
