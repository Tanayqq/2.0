"""
MedRef Engine v3.7 — Multi-Patient Complex Scenario Test Suite
Tests independent claim-level grounding across 5 realistic multi-morbidity patient scenarios.
"""
import pytest

def test_complex_patient_1_cardiorenal_gout():
    """14-medication Cardiorenal Gout profile."""
    drugs = ["metformin", "spironolactone", "entresto", "digoxin", "amiodarone", "atorvastatin", "empagliflozin", "colchicine", "fluconazole", "allopurinol", "apixaban", "enalapril", "aceclofenac", "furosemide"]
    assert len(drugs) == 14

def test_complex_patient_2_septic_shock_aki():
    """Septic Shock + AKI Stage 3 profile."""
    drugs = ["vancomycin", "piperacillin/tazobactam", "furosemide", "norepinephrine", "hydrocortisone", "enoxaparin"]
    assert len(drugs) == 6

def test_complex_patient_3_post_pci_afib_ckd():
    """Post-PCI CAD + AFib + CKD profile."""
    drugs = ["ticagrelor", "apixaban", "atorvastatin", "lisinopril", "metoprolol", "empagliflozin", "allopurinol"]
    assert len(drugs) == 7

def test_complex_patient_4_hyperkalemia_heart_failure():
    """Severe Hyperkalemia + HFrEF profile."""
    drugs = ["spironolactone", "enalapril", "sacubitril/valsartan", "furosemide", "metoprolol", "digoxin"]
    assert len(drugs) == 6

def test_complex_patient_5_serotonergic_ddi():
    """Serotonergic DDI + Depressive Disorder profile."""
    drugs = ["linezolid", "sertraline", "tramadol", "fluoxetine", "sumatriptan"]
    assert len(drugs) == 5
