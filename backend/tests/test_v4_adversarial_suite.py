import pytest
from app.domain.claim_contract import ClaimContract, EvidenceEntry
from app.usecases.claim_verifier import verify_claim_evidence

def test_metformin_egfr22_rejects_overdose_chunk():
    """Test 1: Metformin renal claim rejects pure overdose chunk."""
    claim = ClaimContract(
        drug="metformin",
        action="STOP",
        claim_type="RENAL_DOSING",
        patient_factors={"egfr": 22, "is_pregnant": True},
        required_entities=["metformin"],
        required_topics=["renal impairment", "egfr"],
        required_predicates=["discontinue", "contraindicated", "egfr", "renal"]
    )
    evidence = EvidenceEntry(
        entry_id="chunk_overdose_01",
        drug="metformin",
        section="precautions",
        text="In the event of an overdose with metformin extended-release tablets, consider contacting Poison Help... Lactic acidosis has been reported in overdose cases.",
        entities=["metformin"],
        topics=["overdose"],
        predicates=["overdose", "lactic acidosis"]
    )
    result = verify_claim_evidence(claim, evidence)
    assert result.passed is False
    assert result.reason in ["TOPIC_MISMATCH", "PREDICATE_MISMATCH"]

def test_metformin_wrong_egfr_threshold_rejected():
    """Test 2: Metformin eGFR 22 claim rejects eGFR 38 continuation chunk."""
    claim = ClaimContract(
        drug="metformin",
        action="STOP",
        claim_type="RENAL_DOSING",
        patient_factors={"egfr": 22},
        required_entities=["metformin"],
        required_topics=["renal impairment", "egfr"],
        required_predicates=["discontinue", "contraindicated"]
    )
    evidence = EvidenceEntry(
        entry_id="chunk_egfr38_02",
        drug="metformin",
        section="renal_impairment",
        text="Metformin may be continued in patients with eGFR 38 mL/min/1.73m2.",
        entities=["metformin"],
        topics=["renal_dosing"],
        predicates=["continue"],
        patient_factor_bounds={"egfr_min": 30}
    )
    result = verify_claim_evidence(claim, evidence)
    assert result.passed is False
    assert result.reason in ["PATIENT_FACTOR_MISMATCH", "CONTRADICTION", "PREDICATE_MISMATCH"]

def test_metformin_egfr22_correct_evidence_passes():
    """Test 3: Metformin eGFR 22 claim passes valid contraindication chunk."""
    claim = ClaimContract(
        drug="metformin",
        action="STOP",
        claim_type="RENAL_DOSING",
        patient_factors={"egfr": 22},
        required_entities=["metformin"],
        required_topics=["renal impairment", "egfr"],
        required_predicates=["contraindicated", "egfr", "discontinue"]
    )
    evidence = EvidenceEntry(
        entry_id="chunk_valid_met_03",
        drug="metformin",
        section="contraindications",
        text="Metformin is contraindicated in patients with eGFR below 30 mL/min/1.73m2 due to risk of lactic acidosis. Discontinue immediately.",
        entities=["metformin"],
        topics=["renal impairment", "egfr"],
        predicates=["contraindicated", "egfr", "discontinue"],
        patient_factor_bounds={"egfr_max": 30}
    )
    result = verify_claim_evidence(claim, evidence)
    assert result.passed is True
    assert result.reason == "PASSED"

def test_wrong_drug_rejected():
    """Test 4: Enalapril pregnancy claim rejects Amiodarone chunk."""
    claim = ClaimContract(
        drug="enalapril",
        action="STOP",
        claim_type="PREGNANCY_CONTRAINDICATION",
        patient_factors={"is_pregnant": True},
        required_entities=["enalapril"],
        required_topics=["pregnancy"],
        required_predicates=["discontinue", "pregnancy"]
    )
    evidence = EvidenceEntry(
        entry_id="chunk_amiodarone_04",
        drug="amiodarone",
        section="warnings",
        text="Amiodarone may cause substantial toxicity.",
        entities=["amiodarone"],
        topics=["warnings"],
        predicates=["toxicity"]
    )
    result = verify_claim_evidence(claim, evidence)
    assert result.passed is False
    assert result.reason == "ENTITY_MISMATCH"

def test_amiodarone_digoxin_ddi_requires_both_drugs():
    """Test 5: Digoxin DDI claim with Amiodarone rejects generic Digoxin toxicity chunk lacking Amiodarone."""
    claim = ClaimContract(
        drug="digoxin",
        action="REDUCE_DOSE",
        claim_type="DDI_INTERACTION",
        required_entities=["amiodarone", "digoxin"],
        required_topics=["ddi"],
        required_predicates=["concentration", "dose"]
    )
    evidence = EvidenceEntry(
        entry_id="chunk_digoxin_tox_05",
        drug="digoxin",
        section="warnings",
        text="Digoxin toxicity may occur with elevated serum concentrations.",
        entities=["digoxin"],
        topics=["toxicity"],
        predicates=["toxicity", "concentration"]
    )
    result = verify_claim_evidence(claim, evidence)
    assert result.passed is False
    assert result.reason == "MISSING_DDI_ENTITY"

def test_amiodarone_digoxin_ddi_correct_passes():
    """Test 5b: Digoxin DDI claim passes when chunk documents Amiodarone + Digoxin P-gp interaction."""
    claim = ClaimContract(
        drug="digoxin",
        action="REDUCE_DOSE",
        claim_type="DDI_INTERACTION",
        required_entities=["amiodarone", "digoxin"],
        required_topics=["ddi"],
        required_predicates=["concentration", "dose"]
    )
    evidence = EvidenceEntry(
        entry_id="chunk_ami_dig_05b",
        drug="amiodarone",
        section="drug_interactions",
        text="Amiodarone inhibits P-glycoprotein and surges digoxin serum concentration. Reduce digoxin dose by 50%.",
        entities=["amiodarone", "digoxin"],
        topics=["ddi"],
        predicates=["concentration", "dose"]
    )
    result = verify_claim_evidence(claim, evidence)
    assert result.passed is True
    assert result.reason == "PASSED"

def test_enalapril_pregnancy_vs_ddi_chunk():
    """Test 6: Enalapril pregnancy claim rejects standard DDI chunk."""
    claim = ClaimContract(
        drug="enalapril",
        action="STOP",
        claim_type="PREGNANCY_CONTRAINDICATION",
        patient_factors={"is_pregnant": True},
        required_entities=["enalapril"],
        required_topics=["pregnancy"],
        required_predicates=["pregnancy", "fetal toxicity"]
    )
    evidence = EvidenceEntry(
        entry_id="chunk_enalapril_ddi_06",
        drug="enalapril",
        section="drug_interactions",
        text="Nonsteroidal Anti-Inflammatory Agents: NSAIDs may diminish the antihypertensive effect of ACE inhibitors.",
        entities=["enalapril", "nsaids"],
        topics=["drug_interactions"],
        predicates=["interaction"]
    )
    result = verify_claim_evidence(claim, evidence)
    assert result.passed is False
    assert result.reason in ["TOPIC_MISMATCH", "PREDICATE_MISMATCH"]

def test_apixaban_renal_rejects_spinal_hematoma():
    """Test 7: Apixaban renal dosing claim rejects Spinal Hematoma warning chunk."""
    claim = ClaimContract(
        drug="apixaban",
        action="REDUCE_DOSE",
        claim_type="RENAL_DOSING",
        patient_factors={"egfr": 22},
        required_entities=["apixaban"],
        required_topics=["renal impairment", "egfr"],
        required_predicates=["dose", "renal"]
    )
    evidence = EvidenceEntry(
        entry_id="chunk_apix_spinal_07",
        drug="apixaban",
        section="warnings",
        text="SPINAL/EPIDURAL HEMATOMA: Epidural or spinal hematomas may occur in patients treated with Eliquis who are receiving neuraxial anesthesia.",
        entities=["apixaban"],
        topics=["warnings"],
        predicates=["hematoma", "paralysis"]
    )
    result = verify_claim_evidence(claim, evidence)
    assert result.passed is False
    assert result.reason in ["TOPIC_MISMATCH", "PREDICATE_MISMATCH"]

def test_spironolactone_hyperkalemia_rejects_lithium_ddi():
    """Test 8: Spironolactone hyperkalemia claim rejects Lithium DDI chunk."""
    claim = ClaimContract(
        drug="spironolactone",
        action="STOP",
        claim_type="HYPERKALEMIA_SAFETY",
        patient_factors={"k_level": 6.1},
        required_entities=["spironolactone"],
        required_topics=["hyperkalemia", "potassium"],
        required_predicates=["hyperkalemia", "potassium"]
    )
    evidence = EvidenceEntry(
        entry_id="chunk_spiro_lith_08",
        drug="spironolactone",
        section="drug_interactions",
        text="Lithium: Spironolactone reduces renal clearance of lithium, increasing risk of lithium toxicity.",
        entities=["spironolactone", "lithium"],
        topics=["drug_interactions"],
        predicates=["clearance", "toxicity"]
    )
    result = verify_claim_evidence(claim, evidence)
    assert result.passed is False
    assert result.reason in ["TOPIC_MISMATCH", "PREDICATE_MISMATCH"]

def test_empagliflozin_pregnancy_rejects_metformin_kdigo():
    """Test 9: Empagliflozin pregnancy claim rejects Metformin KDIGO chunk."""
    claim = ClaimContract(
        drug="empagliflozin",
        action="STOP",
        claim_type="PREGNANCY_CONTRAINDICATION",
        patient_factors={"is_pregnant": True},
        required_entities=["empagliflozin"],
        required_topics=["pregnancy"],
        required_predicates=["pregnancy", "discontinue"]
    )
    evidence = EvidenceEntry(
        entry_id="chunk_met_kdigo_09",
        drug="metformin",
        section="guidelines",
        text="KDIGO 2024: Metformin is safe to continue when eGFR >= 30 mL/min.",
        entities=["metformin"],
        topics=["guidelines"],
        predicates=["continue"]
    )
    result = verify_claim_evidence(claim, evidence)
    assert result.passed is False
    assert result.reason in ["ENTITY_MISMATCH", "TOPIC_MISMATCH"]

def test_amiodarone_continuation_rejects_pure_toxicity_warning_chunk():
    """Test 10: Amiodarone continuation claim rejects pure toxicity warning chunk lacking indication text."""
    claim = ClaimContract(
        drug="amiodarone",
        action="CONTINUE",
        claim_type="INDICATION_GDMT",
        required_entities=["amiodarone"],
        required_topics=["indication_gdmt"],
        required_predicates=["amiodarone"]
    )
    evidence = EvidenceEntry(
        entry_id="chunk_amiodarone_warning_10",
        drug="amiodarone",
        section="warnings",
        text="Amiodarone hydrochloride can cause pulmonary toxicity and hepatoxicity which can be fatal.",
        entities=["amiodarone"],
        topics=["warnings"],
        predicates=["toxicity"]
    )
    result = verify_claim_evidence(claim, evidence)
    assert result.passed is False
    assert result.reason == "TOPIC_MISMATCH"
