"""
test_section_utils.py
---------------------
Tests for the shared section normalizer used by both ingestion (parser) and retrieval (rag_usecase).
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.section_utils import normalize_section


class TestNormalizeSection:
    # ------------------------------------------------------------------ #
    # Contraindications                                                    #
    # ------------------------------------------------------------------ #
    def test_contraindications_exact(self):
        assert normalize_section("contraindications") == "contraindications"

    def test_contraindications_title_case(self):
        assert normalize_section("Contraindications") == "contraindications"

    def test_contraindications_upper_case(self):
        assert normalize_section("CONTRAINDICATIONS") == "contraindications"

    def test_contraindications_with_fda_number(self):
        assert normalize_section("4 Contraindications") == "contraindications"

    def test_contraindications_with_dot_number(self):
        assert normalize_section("4. Contraindications") == "contraindications"

    def test_contraindication_singular(self):
        assert normalize_section("Contraindication") == "contraindications"

    # ------------------------------------------------------------------ #
    # Warnings                                                             #
    # ------------------------------------------------------------------ #
    def test_warnings_exact(self):
        assert normalize_section("warnings") == "warnings"

    def test_warnings_and_precautions(self):
        assert normalize_section("Warnings and Precautions") == "warnings"

    def test_warnings_ampersand(self):
        assert normalize_section("Warnings & Precautions") == "warnings"

    def test_boxed_warning(self):
        assert normalize_section("Boxed Warning") == "warnings"

    def test_black_box_warning(self):
        assert normalize_section("Black Box Warning") == "warnings"

    def test_warnings_with_fda_number(self):
        assert normalize_section("5 Warnings and Precautions") == "warnings"

    # ------------------------------------------------------------------ #
    # Adverse Reactions                                                    #
    # ------------------------------------------------------------------ #
    def test_adverse_reactions_exact(self):
        assert normalize_section("adverse reactions") == "adverse reactions"

    def test_adverse_reactions_title_case(self):
        assert normalize_section("Adverse Reactions") == "adverse reactions"

    def test_side_effects(self):
        assert normalize_section("Side Effects") == "adverse reactions"

    def test_adverse_reactions_with_fda_number(self):
        assert normalize_section("6 Adverse Reactions") == "adverse reactions"

    # ------------------------------------------------------------------ #
    # Noise / Excluded Sections                                            #
    # ------------------------------------------------------------------ #
    def test_patient_package_insert_excluded(self):
        assert normalize_section("SPL Patient Package Insert") == "_excluded"

    def test_medication_guide_excluded(self):
        assert normalize_section("Medication Guide") == "_excluded"

    def test_full_prescribing_info_excluded(self):
        assert normalize_section("Full Prescribing Information") == "_excluded"

    def test_highlights_excluded(self):
        assert normalize_section("Highlights of Prescribing Information") == "_excluded"

    # ------------------------------------------------------------------ #
    # Other canonical sections                                             #
    # ------------------------------------------------------------------ #
    def test_dosage_and_administration(self):
        assert normalize_section("Dosage and Administration") == "dosage"

    def test_drug_interactions(self):
        assert normalize_section("Drug Interactions") == "drug interactions"

    def test_drug_interactions_fda_number(self):
        assert normalize_section("7 Drug Interactions") == "drug interactions"

    def test_pregnancy(self):
        assert normalize_section("Pregnancy") == "pregnancy"

    def test_pregnancy_and_lactation(self):
        assert normalize_section("Pregnancy and Lactation") == "pregnancy"

    def test_lactation(self):
        assert normalize_section("Lactation") == "lactation"

    def test_nursing_mothers(self):
        assert normalize_section("Nursing Mothers") == "lactation"

    def test_pediatric_use(self):
        assert normalize_section("Pediatric Use") == "pediatric use"

    def test_geriatric_use(self):
        assert normalize_section("Geriatric Use") == "geriatric use"

    def test_overdosage(self):
        assert normalize_section("Overdosage") == "overdosage"

    def test_storage_and_handling(self):
        assert normalize_section("Storage and Handling") == "storage"

    def test_patient_counseling(self):
        assert normalize_section("Patient Counseling Information") == "patient counseling information"

    def test_indications_and_usage(self):
        assert normalize_section("Indications and Usage") == "indications"

    # ------------------------------------------------------------------ #
    # Edge cases                                                           #
    # ------------------------------------------------------------------ #
    def test_empty_string_returns_empty(self):
        assert normalize_section("") == ""

    def test_none_equivalent_empty_string(self):
        assert normalize_section("   ") == ""

    def test_unknown_section_passthrough_lowercase(self):
        result = normalize_section("Clinical Pharmacology")
        # Should passthrough as lowercased, not crash
        assert isinstance(result, str)
        assert result == result.lower()
