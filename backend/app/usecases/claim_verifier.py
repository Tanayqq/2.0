import re
from typing import Dict, Any, List, Optional
from app.domain.claim_contract import ClaimContract, EvidenceEntry, VerificationResult

def entity_match(claim: ClaimContract, evidence: EvidenceEntry) -> VerificationResult:
    """
    Checks entity matching:
    1. For single-drug claims, primary evidence drug or extracted entities must match claim target.
    2. For DDI claims, ALL required_entities must be present in the evidence.
    """
    c_drug = claim.drug.lower().strip()
    e_drug = (evidence.drug or "").lower().strip()
    e_text = (evidence.text or "").lower()
    e_entities = [ent.lower().strip() for ent in evidence.entities]

    # Check DDI multi-entity requirement
    if claim.claim_type == "DDI_INTERACTION" or len(claim.required_entities) > 1:
        for req_ent in claim.required_entities:
            req_lower = req_ent.lower().strip()
            found_in_drug = req_lower in e_drug or e_drug in req_lower
            found_in_text = req_lower in e_text
            found_in_entities = any(req_lower in ent for ent in e_entities)
            if not (found_in_drug or found_in_text or found_in_entities):
                return VerificationResult(
                    passed=False,
                    reason="MISSING_DDI_ENTITY",
                    details=f"DDI requirement missing entity '{req_ent}' in evidence chunk."
                )
        return VerificationResult(passed=True, reason="PASSED")

    # Single-drug claim entity matching
    is_primary_match = (e_drug == c_drug) or (c_drug in e_drug) or (e_drug in c_drug)
    is_text_match = c_drug in e_text
    is_entity_list_match = any(c_drug in ent for ent in e_entities)

    if is_primary_match or is_text_match or is_entity_list_match:
        return VerificationResult(passed=True, reason="PASSED")

    return VerificationResult(
        passed=False,
        reason="ENTITY_MISMATCH",
        details=f"Claim drug '{claim.drug}' does not match evidence drug '{evidence.drug}'."
    )

def topic_match(claim: ClaimContract, evidence: EvidenceEntry) -> VerificationResult:
    """
    Checks clinical topic matching:
    1. RENAL_DOSING: Disqualifies 'pregnancy', 'overdose', or 'spinal_hematoma' chunks. Requires renal topics/text.
    2. PREGNANCY_CONTRAINDICATION: Requires 'pregnancy' / 'fetal' topics or text.
    3. HYPERKALEMIA_SAFETY: Requires 'potassium' / 'hyperkalemia' topics or text. Rejects unrelated DDI chunks.
    4. DDI_INTERACTION: Requires 'interaction' / 'coadministration' / 'cyp' / 'p-gp' topics or text.
    """
    sec_lower = (evidence.section or "").lower()
    e_text = (evidence.text or "").lower()
    e_topics = [t.lower() for t in evidence.topics]

    # Topic rule 1: RENAL_DOSING claims
    if claim.claim_type == "RENAL_DOSING":
        # Disqualify pregnancy chunks for renal claims
        if "pregnancy" in sec_lower or "lactation" in sec_lower or "pregnancy" in e_topics:
            return VerificationResult(
                passed=False,
                reason="TOPIC_MISMATCH",
                details="Renal dosing claim cannot cite pregnancy-only evidence."
            )
        # Disqualify pure overdose chunks lacking explicit renal predicates
        is_overdose = "overdose" in sec_lower or "overdosage" in sec_lower or "overdose" in e_topics or "overdose" in e_text
        has_explicit_renal = any(k in e_text or k in sec_lower for k in ["egfr", "gfr", "renal impairment", "renal disease", "severe renal", "creatinine clearance", "ckd", "kidney"])
        if is_overdose and not has_explicit_renal:
            return VerificationResult(
                passed=False,
                reason="TOPIC_MISMATCH",
                details="Renal dosing claim cannot cite pure overdose evidence."
            )
        # Disqualify spinal/epidural hematoma warnings for renal claims
        if "spinal" in e_text or "epidural" in e_text or "hematoma" in e_text:
            if not has_explicit_renal:
                return VerificationResult(
                    passed=False,
                    reason="TOPIC_MISMATCH",
                    details="Renal dosing claim cannot cite spinal/epidural hematoma evidence."
                )

    # Topic rule 2: PREGNANCY_CONTRAINDICATION claims
    if claim.claim_type == "PREGNANCY_CONTRAINDICATION":
        has_preg_evidence = any(k in e_text or k in sec_lower or k in e_topics for k in ["pregnant", "pregnancy", "fetus", "fetal", "teratogen", "embryo", "gestation", "boxed warning"])
        if not has_preg_evidence:
            return VerificationResult(
                passed=False,
                reason="TOPIC_MISMATCH",
                details="Pregnancy contraindication claim requires explicit pregnancy/fetal evidence."
            )

    # Topic rule 3: HYPERKALEMIA_SAFETY claims
    if claim.claim_type == "HYPERKALEMIA_SAFETY":
        has_k_evidence = any(k in e_text or k in sec_lower or k in e_topics for k in ["potassium", "hyperkalemia", "k+", "potassium-sparing", "aldactone warning"])
        if not has_k_evidence:
            return VerificationResult(
                passed=False,
                reason="TOPIC_MISMATCH",
                details="Hyperkalemia safety claim requires explicit potassium/hyperkalemia evidence."
            )

    # Topic rule 4: Required topics validation if specified
    TOPIC_SYNONYMS = {
        "renal_dosing": ["renal", "egfr", "gfr", "kidney", "creatinine", "ckd", "contraindications", "warnings", "dosing", "dosage", "renal_dosing"],
        "pregnancy_contraindication": ["pregnancy", "pregnant", "lactation", "fetal", "fetus", "teratogen", "boxed warning", "warnings", "contraindications", "pregnancy_contraindication"],
        "hyperkalemia_safety": ["potassium", "hyperkalemia", "k+", "aldactone", "warnings", "precautions", "hyperkalemia_safety"],
        "ddi_interaction": ["interaction", "cyp", "p-gp", "coadministration", "concomitant", "drug interactions", "drug_interactions", "ddi_interaction"],
        "indication_gdmt": ["indication", "indications", "clinical", "pharmacology", "guideline", "treatment", "management", "indication_gdmt"]
    }

    if claim.required_topics:
        topic_found = False
        for req_top in claim.required_topics:
            req_lower = req_top.lower().strip()
            synonyms = TOPIC_SYNONYMS.get(req_lower, [req_lower])
            for syn in synonyms:
                if syn in sec_lower or syn in e_text or any(syn in top for top in e_topics):
                    topic_found = True
                    break
            if topic_found:
                break
        if not topic_found:
            return VerificationResult(
                passed=False,
                reason="TOPIC_MISMATCH",
                details=f"Required topics '{claim.required_topics}' not found in evidence."
            )

    return VerificationResult(passed=True, reason="PASSED")

def predicate_match(claim: ClaimContract, evidence: EvidenceEntry) -> VerificationResult:
    """Checks required clinical action/effect predicates in the evidence."""
    if not claim.required_predicates:
        return VerificationResult(passed=True, reason="PASSED")

    sec_lower = (evidence.section or "").lower()
    e_text = (evidence.text or "").lower()
    e_preds = [p.lower() for p in evidence.predicates]

    for req_pred in claim.required_predicates:
        p_lower = req_pred.lower().strip()
        found = (p_lower in e_text) or (p_lower in sec_lower) or any(p_lower in pred for pred in e_preds)
        if not found:
            return VerificationResult(
                passed=False,
                reason="PREDICATE_MISMATCH",
                details=f"Required predicate '{req_pred}' not found in evidence text or predicates."
            )

    return VerificationResult(passed=True, reason="PASSED")

def patient_factor_supported(claim: ClaimContract, evidence: EvidenceEntry) -> VerificationResult:
    """
    Validates patient factors (e.g. eGFR threshold bounds):
    Example: Patient eGFR = 22. If evidence specifies egfr_min = 30 (e.g. "safe when eGFR >= 30"),
    it contradicts a STOP claim for eGFR 22 and fails verification.
    """
    bounds = evidence.patient_factor_bounds or {}
    factors = claim.patient_factors or {}

    # Check eGFR threshold bounds
    if "egfr" in factors:
        p_egfr = float(factors["egfr"])
        if "egfr_min" in bounds and p_egfr >= bounds["egfr_min"] and claim.action == "STOP":
            return VerificationResult(
                passed=False,
                reason="PATIENT_FACTOR_MISMATCH",
                details=f"Patient eGFR {p_egfr} satisfies egfr_min {bounds['egfr_min']}, contradicting STOP claim."
            )
        if "egfr_max" in bounds and p_egfr > bounds["egfr_max"]:
            return VerificationResult(
                passed=False,
                reason="PATIENT_FACTOR_MISMATCH",
                details=f"Patient eGFR {p_egfr} exceeds egfr_max {bounds['egfr_max']} bound."
            )

    return VerificationResult(passed=True, reason="PASSED")

def contradiction_check(claim: ClaimContract, evidence: EvidenceEntry) -> VerificationResult:
    """Checks if evidence text explicitly contradicts claim action (e.g. STOP vs 'safe to continue')."""
    e_text = (evidence.text or "").lower()
    
    if claim.action == "STOP":
        if "safe to continue" in e_text or "no dose adjustment required" in e_text:
            return VerificationResult(
                passed=False,
                reason="CONTRADICTION",
                details="Evidence asserts safety/continuation, contradicting STOP claim."
            )

    return VerificationResult(passed=True, reason="PASSED")

def verify_claim_evidence(claim: ClaimContract, evidence: EvidenceEntry) -> VerificationResult:
    """
    Mandatory 5-Step Boolean Contract Verification Gate:
    1. entity_match()
    2. topic_match()
    3. predicate_match()
    4. patient_factor_supported()
    5. contradiction_check()
    """
    res_ent = entity_match(claim, evidence)
    if not res_ent.passed:
        return res_ent

    res_top = topic_match(claim, evidence)
    if not res_top.passed:
        return res_top

    res_pred = predicate_match(claim, evidence)
    if not res_pred.passed:
        return res_pred

    res_fact = patient_factor_supported(claim, evidence)
    if not res_fact.passed:
        return res_fact

    res_con = contradiction_check(claim, evidence)
    if not res_con.passed:
        return res_con

    return VerificationResult(passed=True, reason="PASSED")
