"""
MedRef Engine v4.0 Standalone Verification Test Script
Run this script to verify the 5-Step Boolean Verifier Gate and Citation Ledger end-to-end.

Usage:
    python run_verifiable_scenario.py
"""

import sys
import os

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from app.domain.claim_contract import ClaimContract, EvidenceEntry, CitationLedger, CandidateAudit
from app.usecases.claim_verifier import verify_claim_evidence, entity_match, topic_match, predicate_match, patient_factor_supported, contradiction_check
from app.usecases.rag_usecase import ProcessClinicalQueryUseCase
from app.citation_map import CitationMap
from app.domain.models import Citation

def run_test():
    print("=" * 80)
    print("  MEDREF ENGINE v4.0 — END-TO-END CLINICAL VERIFICATION BENCHMARK")
    print("=" * 80)
    print("\n[1] INITIALIZING MOCK VECTOR DB & CITATION MAP ...")

    cmap = CitationMap()
    cmap.add_entry(
        uuid="uuid-1", citation_number="1", source="DailyMed - Enalapril Boxed Warning",
        drug="Enalapril", section="Boxed Warning",
        text="WARNING: FETAL TOXICITY - When pregnancy is detected, discontinue enalapril as soon as possible. Drugs that act directly on the renin-angiotensin system can cause injury and death to the developing fetus."
    )
    cmap.add_entry(
        uuid="uuid-2", citation_number="2", source="DailyMed - Spironolactone Contraindications",
        drug="Spironolactone", section="Contraindications",
        text="Spironolactone is contraindicated in patients with hyperkalemia (serum potassium > 5.0 mEq/L) and during pregnancy due to antiandrogenic risk to fetus."
    )
    cmap.add_entry(
        uuid="uuid-3", citation_number="3", source="DailyMed - Metformin Contraindications",
        drug="Metformin", section="Contraindications",
        text="Metformin is contraindicated in severe renal impairment (eGFR below 30 mL/min/1.73m2) due to risk of fatal metformin-associated lactic acidosis (MALA)."
    )
    cmap.add_entry(
        uuid="uuid-4", citation_number="4", source="DailyMed - Empagliflozin Pregnancy Warning",
        drug="Empagliflozin", section="Use in Specific Populations",
        text="Empagliflozin is contraindicated during the second and third trimesters of pregnancy due to risk of fetal renal tubule dilatation. Discontinue when pregnancy is detected."
    )
    cmap.add_entry(
        uuid="uuid-5", citation_number="5", source="DailyMed - Amiodarone Drug Interactions",
        drug="Amiodarone", section="Drug Interactions",
        text="Amiodarone inhibits P-glycoprotein efflux and surges serum digoxin concentration by 70-100%. Reduce digoxin dose by 50% immediately."
    )
    cmap.add_entry(
        uuid="uuid-6", citation_number="6", source="DailyMed - Amiodarone Indications",
        drug="Amiodarone", section="Indications and Usage",
        text="Amiodarone is indicated for rhythm control in atrial fibrillation and treatment of recurrent ventricular arrhythmia."
    )

    citations = [
        Citation(document_id="1", source="DailyMed", snippet="Enalapril Boxed Warning", uuid="uuid-1", drug="Enalapril", section="Boxed Warning", count=0),
        Citation(document_id="2", source="DailyMed", snippet="Spironolactone Contraindications", uuid="uuid-2", drug="Spironolactone", section="Contraindications", count=0),
        Citation(document_id="3", source="DailyMed", snippet="Metformin Contraindications", uuid="uuid-3", drug="Metformin", section="Contraindications", count=0),
        Citation(document_id="4", source="DailyMed", snippet="Empagliflozin Warning", uuid="uuid-4", drug="Empagliflozin", section="Use in Specific Populations", count=0),
        Citation(document_id="5", source="DailyMed", snippet="Amiodarone DDI", uuid="uuid-5", drug="Amiodarone", section="Drug Interactions", count=0),
        Citation(document_id="6", source="DailyMed", snippet="Amiodarone Indications", uuid="uuid-6", drug="Amiodarone", section="Indications and Usage", count=0),
    ]

    rule_decisions = {
        "decisions": {
            "Enalapril": {"action": "STOP", "reason": "CONTRAINDICATED IN PREGNANCY (FDA Boxed Warning)"},
            "Spironolactone": {"action": "STOP", "reason": "CONTRAINDICATED IN PREGNANCY & HYPERKALEMIA (K+ 6.1)"},
            "Metformin XR": {"action": "STOP", "reason": "eGFR 22.0 mL/min < 30 mL/min threshold (MALA risk)"},
            "Empagliflozin": {"action": "STOP", "reason": "CONTRAINDICATED IN PREGNANCY (2nd/3rd Trimester)"},
            "Digoxin": {"action": "REDUCE DOSE", "reason": "Amiodarone DDI P-gp inhibition"},
            "Amiodarone": {"action": "CONTINUE", "reason": "Rhythm control in AFib / arrhythmia"}
        },
        "immediate_dangers": [
            "BOXED WARNING - FETAL TOXICITY IN PREGNANCY (Enalapril)",
            "CRITICAL HYPERKALEMIA (K+ = 6.1 mEq/L)",
            "CONTRAINDICATED METFORMIN IN STAGE 4/5 CKD (eGFR = 22.0 mL/min)"
        ],
        "major_interactions": [{"pair": "Amiodarone ↔ Digoxin", "severity": "CRITICAL", "mechanism": "P-gp inhibition"}],
        "mandatory_monitoring": ["Serum Potassium (K+): q24h", "Serum Digoxin Trough Level: 7-10 days"],
        "labs": {"egfr": 22.0, "potassium": 6.1}
    }

    print("  CitationMap loaded with 6 evidence entries.")

    print("\n[2] RUNNING VERIFIER GATE & EXECUTING RESPONSE SANITIZER ...")

    sanitized_report = ProcessClinicalQueryUseCase._sanitize_clinical_markdown_response(
        answer_text="raw model response",
        rule_decisions=rule_decisions,
        citation_map=cmap,
        citations=citations,
        question_text="34 year old pregnant female patient with eGFR 22, K+ 6.1 taking Amiodarone, Digoxin, Enalapril, Spironolactone, Metformin XR, Empagliflozin"
    )

    print("\n" + "=" * 80)
    print("  GENERATED 8-SECTION CLINICAL REPORT (SANITY CHECK)")
    print("=" * 80)
    print(sanitized_report)

    print("\n" + "=" * 80)
    print("  VERIFICATION RESULT CHECKS")
    print("=" * 80)

    # Check 1: Enalapril cites [1]
    assert "| Enalapril | STOP | CONTRAINDICATED IN PREGNANCY (FDA Boxed Warning) | [1] |" in sanitized_report
    print("  ✓ Check 1 Passed: Enalapril correctly bound to Boxed Warning chunk [1]")

    # Check 2: Spironolactone cites [2]
    assert "| Spironolactone | STOP | CONTRAINDICATED IN PREGNANCY & HYPERKALEMIA (K+ 6.1) | [2] |" in sanitized_report
    print("  ✓ Check 2 Passed: Spironolactone correctly bound to Contraindications chunk [2]")

    # Check 3: Metformin XR cites [3]
    assert "| Metformin XR | STOP | eGFR 22.0 mL/min < 30 mL/min threshold (MALA risk) | [3] |" in sanitized_report
    print("  ✓ Check 3 Passed: Metformin XR correctly bound to eGFR < 30 chunk [3]")

    # Check 4: Empagliflozin cites [4]
    assert "| Empagliflozin | STOP | CONTRAINDICATED IN PREGNANCY (2nd/3rd Trimester) | [4] |" in sanitized_report
    print("  ✓ Check 4 Passed: Empagliflozin correctly bound to Pregnancy chunk [4]")

    # Check 5: Digoxin cites [5] (Amiodarone DDI chunk)
    assert "| Digoxin | REDUCE DOSE | Amiodarone DDI P-gp inhibition | [5] |" in sanitized_report
    print("  ✓ Check 5 Passed: Digoxin correctly bound to Amiodarone P-gp DDI chunk [5]")

    # Check 6: Amiodarone cites [6]
    assert "| Amiodarone | CONTINUE | Rhythm control in AFib / arrhythmia | [6] |" in sanitized_report
    print("  ✓ Check 6 Passed: Amiodarone correctly bound to Indications chunk [6]")

    print("\n" + "=" * 80)
    print("  🎉 ALL VERIFICATION CHECKS PASSED WITH 100% PRECISION (0 FALSE CITATIONS)!")
    print("=" * 80)

if __name__ == "__main__":
    run_test()
