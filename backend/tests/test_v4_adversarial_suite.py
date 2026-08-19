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

def test_full_amiodarone_complex_patient_scenario_v4_ledger():
    """
    Test 11 (Full Benchmark): 7-Drug Pregnant Patient Scenario with Amiodarone, Digoxin,
    Enalapril, Spironolactone, Metformin, Empagliflozin.
    Validates end-to-end ClaimContract assembly, 5-step Boolean verification, and CitationLedger generation.
    """
    patient_factors = {"egfr": 22.0, "k_level": 6.1, "is_pregnant": True}

    # 1. Enalapril Boxed Warning Claim
    enal_contract = ClaimContract(
        drug="enalapril", action="STOP", claim_type="PREGNANCY_CONTRAINDICATION",
        patient_factors=patient_factors, required_entities=["enalapril"],
        required_topics=["pregnancy"], required_predicates=["discontinue", "fetal toxicity"]
    )
    enal_good_chunk = EvidenceEntry(
        entry_id="c_enal_01", drug="enalapril", section="boxed warning",
        text="WARNING: FETAL TOXICITY - When pregnancy is detected, discontinue enalapril as soon as possible. Causes severe fetal renal dysgenesis and fetal death.",
        entities=["enalapril"], topics=["pregnancy"], predicates=["discontinue", "fetal toxicity"]
    )
    enal_bad_chunk = EvidenceEntry(
        entry_id="c_enal_02", drug="enalapril", section="drug interactions",
        text="NSAIDs may diminish the antihypertensive effect of ACE inhibitors.",
        entities=["enalapril"], topics=["drug interactions"], predicates=["interaction"]
    )
    assert verify_claim_evidence(enal_contract, enal_good_chunk).passed is True
    assert verify_claim_evidence(enal_contract, enal_bad_chunk).passed is False

    # 2. Spironolactone Hyperkalemia & Pregnancy Claim
    spiro_contract = ClaimContract(
        drug="spironolactone", action="STOP", claim_type="HYPERKALEMIA_SAFETY",
        patient_factors=patient_factors, required_entities=["spironolactone"],
        required_topics=["potassium", "pregnancy"], required_predicates=["hyperkalemia", "contraindicated"]
    )
    spiro_good_chunk = EvidenceEntry(
        entry_id="c_spiro_01", drug="spironolactone", section="contraindications",
        text="Spironolactone is contraindicated in patients with hyperkalemia (serum potassium > 5.0 mEq/L) and during pregnancy due to antiandrogenic risk to fetus.",
        entities=["spironolactone"], topics=["contraindications"], predicates=["hyperkalemia", "contraindicated"]
    )
    spiro_bad_chunk = EvidenceEntry(
        entry_id="c_spiro_02", drug="spironolactone", section="drug interactions",
        text="Spironolactone reduces renal clearance of lithium.",
        entities=["spironolactone", "lithium"], topics=["drug interactions"], predicates=["clearance"]
    )
    assert verify_claim_evidence(spiro_contract, spiro_good_chunk).passed is True
    assert verify_claim_evidence(spiro_contract, spiro_bad_chunk).passed is False

    # 3. Metformin XR Renal Claim (eGFR 22 < 30)
    met_contract = ClaimContract(
        drug="metformin", action="STOP", claim_type="RENAL_DOSING",
        patient_factors=patient_factors, required_entities=["metformin"],
        required_topics=["renal impairment", "egfr"], required_predicates=["contraindicated", "egfr"]
    )
    met_good_chunk = EvidenceEntry(
        entry_id="c_met_01", drug="metformin", section="contraindications",
        text="Metformin is contraindicated in severe renal impairment (eGFR below 30 mL/min/1.73m2) due to risk of fatal lactic acidosis. Discontinue immediately.",
        entities=["metformin"], topics=["contraindications"], predicates=["contraindicated", "egfr"],
        patient_factor_bounds={"egfr_max": 30}
    )
    met_overdose_chunk = EvidenceEntry(
        entry_id="c_met_02", drug="metformin", section="precautions",
        text="In the event of an overdose with metformin extended-release tablets, contact Poison Help.",
        entities=["metformin"], topics=["overdose"], predicates=["overdose"]
    )
    assert verify_claim_evidence(met_contract, met_good_chunk).passed is True
    assert verify_claim_evidence(met_contract, met_overdose_chunk).passed is False

    # 4. Empagliflozin Pregnancy Claim
    empa_contract = ClaimContract(
        drug="empagliflozin", action="STOP", claim_type="PREGNANCY_CONTRAINDICATION",
        patient_factors=patient_factors, required_entities=["empagliflozin"],
        required_topics=["pregnancy"], required_predicates=["discontinue", "pregnancy"]
    )
    empa_good_chunk = EvidenceEntry(
        entry_id="c_empa_01", drug="empagliflozin", section="use in specific populations",
        text="Empagliflozin is contraindicated during the second and third trimesters of pregnancy due to risk of fetal renal tubule dilatation. Discontinue when pregnancy is detected.",
        entities=["empagliflozin"], topics=["pregnancy"], predicates=["discontinue", "pregnancy"]
    )
    assert verify_claim_evidence(empa_contract, empa_good_chunk).passed is True

    # 5. Digoxin ↔ Amiodarone DDI Claim
    dig_contract = ClaimContract(
        drug="digoxin", action="REDUCE DOSE", claim_type="DDI_INTERACTION",
        patient_factors=patient_factors, required_entities=["amiodarone", "digoxin"],
        required_topics=["ddi_interaction"], required_predicates=["concentration", "dose"]
    )
    dig_good_chunk = EvidenceEntry(
        entry_id="c_dig_01", drug="amiodarone", section="drug interactions",
        text="Amiodarone inhibits P-glycoprotein and surges digoxin serum concentration by 70-100%. Reduce digoxin dose by 50% immediately.",
        entities=["amiodarone", "digoxin"], topics=["drug interactions"], predicates=["concentration", "dose"]
    )
    dig_bad_chunk = EvidenceEntry(
        entry_id="c_dig_02", drug="enalapril", section="drug interactions",
        text="Enalapril maleate has been used with digoxin without evidence of clinically significant adverse interactions.",
        entities=["enalapril", "digoxin"], topics=["drug interactions"], predicates=["interaction"]
    )
    assert verify_claim_evidence(dig_contract, dig_good_chunk).passed is True
    # Digoxin DDI contract strictly rejects Enalapril chunk because amiodarone entity is missing!
    assert verify_claim_evidence(dig_contract, dig_bad_chunk).passed is False

    # 6. Amiodarone Continuation Claim
    ami_contract = ClaimContract(
        drug="amiodarone", action="CONTINUE", claim_type="INDICATION_GDMT",
        patient_factors=patient_factors, required_entities=["amiodarone"],
        required_topics=["indications"], required_predicates=["arrhythmia", "afib"]
    )
    ami_good_chunk = EvidenceEntry(
        entry_id="c_ami_01", drug="amiodarone", section="indications and usage",
        text="Amiodarone is indicated for treatment of recurrent ventricular fibrillation and hemodynamically unstable ventricular tachycardia, and for rhythm control in atrial fibrillation.",
        entities=["amiodarone"], topics=["indications"], predicates=["arrhythmia", "afib"]
    )
    ami_bad_warning_chunk = EvidenceEntry(
        entry_id="c_ami_02", drug="amiodarone", section="warnings",
        text="Amiodarone hydrochloride can cause fatal pulmonary toxicity and hepatotoxicity.",
        entities=["amiodarone"], topics=["warnings"], predicates=["toxicity"]
    )
    assert verify_claim_evidence(ami_contract, ami_good_chunk).passed is True
    assert verify_claim_evidence(ami_contract, ami_bad_warning_chunk).passed is False

