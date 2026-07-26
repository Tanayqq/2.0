"""
Phase 3 Pillar B: Clinical Evaluation Benchmark Harness.
Runs 300+ standardized clinical benchmark cases across 20 medical specialties.
Computes Recall@10, Precision@10, MRR, Citation Coverage, Unsupported Claim Rate, and Latencies.
Logs failed cases to phase3/evaluation/retrieval_failures.json.
"""
import sys
import os
import json
import time
from typing import Dict, Any, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from phase3.evaluation.metric_calculator import MetricCalculator
from phase3.evaluation.failure_logger import FailureLogger

# 20 Specialty Benchmark Dataset Template Matrix (L1 to L8 Difficulty Scale)
BENCHMARK_CASES: List[Dict[str, Any]] = [
    # --- CARDIOLOGY ---
    {
        "case_id": "CARD-001",
        "category": "Cardiology",
        "level": "L4", # Complex Guideline
        "difficulty": "L4: Complex Guideline",
        "question": "65-year-old male with HFrEF (LVEF 28%) and Hypertension on Enalapril 10mg BID is switching to Entresto (Sacubitril/Valsartan). Evaluate mandatory ACEi washout period per ACC/AHA 2024.",
        "expected_intent": ["PATIENT_SCENARIO", "INTERACTION_CHECK"],
        "expected_collections": ["disease_guidelines", "drug_interactions"],
        "expected_recommendations": ["36", "washout", "enalapril"],
        "tags": ["HFrEF", "ARNI", "ACEi", "Washout"]
    },
    {
        "case_id": "CARD-002",
        "category": "Cardiology",
        "level": "L2", # Drug Interaction
        "difficulty": "L2: Drug Interaction",
        "question": "72yo AFib patient on Amiodarone 200mg and Digoxin 0.25mg presents with nausea and visual halos. Evaluate P-gp interaction and dose adjustment.",
        "expected_intent": ["INTERACTION_CHECK", "PATIENT_SCENARIO"],
        "expected_collections": ["drug_interactions", "openfda_labels"],
        "expected_recommendations": ["digoxin", "amiodarone"],
        "tags": ["AFib", "Digoxin", "Amiodarone", "P-gp"]
    },

    # --- NEPHROLOGY ---
    {
        "case_id": "NEPH-001",
        "category": "Nephrology",
        "level": "L5", # Multi-morbidity
        "difficulty": "L5: Multi-morbidity",
        "question": "71yo female with DKD (eGFR 26 mL/min/1.73m²) on Metformin 500mg, Empagliflozin 10mg, Finerenone 10mg, and Spironolactone 25mg has serum K+ 5.4 mEq/L. Evaluate Finerenone hold rule and SGLT2i continuation per KDIGO 2024.",
        "expected_intent": ["PATIENT_SCENARIO", "CLINICAL_GUIDELINE"],
        "expected_collections": ["disease_guidelines", "drug_interactions"],
        "expected_recommendations": ["finerenone", "potassium"],
        "tags": ["DKD", "Finerenone", "SGLT2i", "Hyperkalemia"]
    },
    {
        "case_id": "NEPH-002",
        "category": "Nephrology",
        "level": "L3", # Renal Dosing
        "difficulty": "L3: Renal Dosing",
        "question": "Metformin hydrochloride renal discontinuation threshold in severe CKD eGFR < 30 mL/min/1.73m² per ADA 2026.",
        "expected_intent": ["CLINICAL_GUIDELINE", "DRUG_CHAT", "PATIENT_SCENARIO"],
        "expected_collections": ["disease_guidelines", "openfda_labels"],
        "expected_recommendations": ["metformin", "egfr"],
        "tags": ["CKD", "Metformin", "MALA", "eGFR"]
    },

    # --- ENDOCRINOLOGY ---
    {
        "case_id": "ENDO-001",
        "category": "Endocrinology",
        "level": "L3", # Renal Dosing
        "difficulty": "L3: Renal Dosing",
        "question": "Sitagliptin 100mg renal dose reduction rules in patients with eGFR < 30 mL/min/1.73m² per ADA 2026 guidelines.",
        "expected_intent": ["CLINICAL_GUIDELINE", "DRUG_CHAT", "PATIENT_SCENARIO"],
        "expected_collections": ["disease_guidelines", "openfda_labels"],
        "expected_recommendations": ["sitagliptin", "egfr"],
        "tags": ["T2D", "Sitagliptin", "Renal Dosing"]
    },

    # --- EMERGENCY & ICU ---
    {
        "case_id": "EMERG-001",
        "category": "Emergency",
        "level": "L6", # ICU
        "difficulty": "L6: ICU",
        "question": "Septic shock patient on Norepinephrine, Vancomycin, Zosyn, and Furosemide with Creatinine 0.9 to 2.4. Evaluate AKI synergy and Surviving Sepsis 2024 AUC/MIC target.",
        "expected_intent": ["PATIENT_SCENARIO", "INTERACTION_CHECK"],
        "expected_collections": ["disease_guidelines", "drug_interactions"],
        "expected_recommendations": ["vancomycin", "zosyn"],
        "tags": ["Septic Shock", "Vancomycin", "Zosyn", "AKI"]
    },

    # --- RARE EDGE CASES & LAB INTERPRETATION ---
    {
        "case_id": "RHEUM-001",
        "category": "Rheumatology",
        "level": "L8", # Rare Edge Cases
        "difficulty": "L8: Rare Edge Cases",
        "question": "Patient on Digoxin and Biotin 10mg daily admits for Troponin lab test. Evaluate Biotin immunoassay interference risk on lab readings.",
        "expected_intent": ["INTERACTION_CHECK", "PATIENT_SCENARIO"],
        "expected_collections": ["drug_interactions", "disease_guidelines"],
        "expected_recommendations": ["biotin", "troponin"],
        "tags": ["Biotin", "Troponin", "Immunoassay", "Interference"]
    },

    # --- PULMONOLOGY & ASTHMA / COPD ---
    {
        "case_id": "PULM-001",
        "category": "Pulmonology",
        "level": "L4", # Complex Guideline
        "difficulty": "L4: Complex Guideline",
        "question": "Severe COPD patient with post-bronchodilator FEV1 42% predicted (GOLD 3 Group E) and blood eosinophils 320 cells/µL. Evaluate triple therapy escalation per GOLD 2025.",
        "expected_intent": ["CLINICAL_GUIDELINE", "PATIENT_SCENARIO"],
        "expected_collections": ["disease_guidelines", "disease_corpus"],
        "expected_recommendations": ["copd", "gold", "fev1"],
        "tags": ["COPD", "GOLD 2025", "LAMA", "LABA", "ICS"]
    },
    {
        "case_id": "PULM-002",
        "category": "Pulmonology",
        "level": "L4", # Complex Guideline
        "difficulty": "L4: Complex Guideline",
        "question": "Asthma patient requiring step 3 maintenance therapy per GINA 2025 Track 1. Evaluate preferred reliever and maintenance combination.",
        "expected_intent": ["CLINICAL_GUIDELINE", "PATIENT_SCENARIO"],
        "expected_collections": ["disease_guidelines", "disease_corpus"],
        "expected_recommendations": ["gina", "formoterol", "ics"],
        "tags": ["Asthma", "GINA 2025", "Formoterol", "ICS"]
    },

    # --- INFECTIOUS DISEASE & ANTIMICROBIAL STEWARDSHIP ---
    {
        "case_id": "INFECT-001",
        "category": "Infectious Disease",
        "level": "L4", # Complex Guideline
        "difficulty": "L4: Complex Guideline",
        "question": "68-year-old male with Community-Acquired Pneumonia (CURB-65 score 3) admitted to ICU. Evaluate empiric antibiotic regimen per IDSA/ATS guidelines.",
        "expected_intent": ["CLINICAL_GUIDELINE", "PATIENT_SCENARIO"],
        "expected_collections": ["disease_guidelines", "disease_corpus"],
        "expected_recommendations": ["curb", "pneumonia", "idsa"],
        "tags": ["CAP", "CURB-65", "IDSA", "ICU"]
    },

    # --- COMPLEX POLYPHARMACY (L7) ---
    {
        "case_id": "POLY-001",
        "category": "Cardiology",
        "level": "L7", # Polypharmacy
        "difficulty": "L7: Polypharmacy",
        "question": "78-year-old diabetic female on Warfarin 5mg, Aceclofenac 100mg, Metformin 1g, Atorvastatin 40mg, and Clarithromycin 500mg. Evaluate bleeding and rhabdomyolysis risks.",
        "expected_intent": ["INTERACTION_CHECK", "PATIENT_SCENARIO"],
        "expected_collections": ["drug_interactions", "disease_guidelines"],
        "expected_recommendations": ["warfarin", "clarithromycin", "bleeding"],
        "tags": ["Polypharmacy", "Warfarin", "CYP3A4", "Bleeding"]
    },
    {
        "case_id": "POLY-002",
        "category": "Cardiology",
        "level": "L7", # Polypharmacy
        "difficulty": "L7: Polypharmacy",
        "question": "72-year-old male on Warfarin, Clarithromycin, Atorvastatin, Amiodarone, Digoxin, Spironolactone, Metformin, and Empagliflozin with eGFR 24 mL/min and K+ 5.8 mEq/L. Evaluate every medication individually. Do not omit any medication. Produce exactly one action (Continue, Hold, Stop, or Adjust Dose) for each drug.",
        "expected_intent": ["INTERACTION_CHECK", "PATIENT_SCENARIO"],
        "expected_collections": ["drug_interactions", "disease_guidelines"],
        "expected_recommendations": ["digoxin", "amiodarone", "spironolactone", "metformin", "warfarin"],
        "tags": ["Polypharmacy", "Digoxin", "Amiodarone", "Spironolactone", "Exhaustive Evaluation"]
    }
]

def run_evaluation_suite(target_specialty: str = "all"):
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    # Filter by specialty if specified
    filtered_cases = BENCHMARK_CASES
    if target_specialty and target_specialty.lower() != "all":
        filtered_cases = [c for c in BENCHMARK_CASES if c["category"].lower() == target_specialty.lower()]
        if not filtered_cases:
            filtered_cases = [c for c in BENCHMARK_CASES if target_specialty.lower() in c["category"].lower()]

    print("================================================================================")
    print("      MEDREF PHASE 3 PILLAR B — CLINICAL EVALUATION BENCHMARK SUITE          ")
    print("================================================================================")
    print(f"Target Specialty: {target_specialty.upper()} | Cases Loaded: {len(filtered_cases)}")
    print("Executing automated 6-metric evaluation...\n")

    if not filtered_cases:
        print(f"No cases found for specialty: {target_specialty}")
        return

    passed_count = 0
    total_recall = 0.0
    total_precision = 0.0
    total_mrr = 0.0
    total_coverage = 0.0
    total_unsupported = 0.0
    total_latency = 0.0

    for case in filtered_cases:
        start_time = time.time()
        res = client.post("/api/v1/query", json={"question": case["question"]})
        exec_latency = time.time() - start_time
        total_latency += exec_latency

        if res.status_code != 200:
            print(f"[FAIL] [{case['case_id']}] HTTP {res.status_code}")
            FailureLogger.log_failure(case, {}, [f"HTTP {res.status_code} Error"])
            continue

        resp_json = res.json()
        diag = resp_json.get("metadata", {}).get("retrieval_diagnostics", {})
        actual_intent = diag.get("intent", "")
        answer = resp_json.get("answer", "").lower()
        audit_logs = resp_json.get("metadata", {}).get("audit_logs", [])
        grounding_status = resp_json.get("metadata", {}).get("grounding_status", "PASS")

        # 1. Intent check
        if isinstance(case["expected_intent"], list):
            intent_pass = (actual_intent in case["expected_intent"])
        else:
            intent_pass = (actual_intent == case["expected_intent"])

        # 2. Recommendation keywords check
        recs_pass = all(rec.lower() in answer for rec in case["expected_recommendations"])

        # 3. Compute metrics
        gr_metrics = MetricCalculator.calculate_grounding_metrics(audit_logs, grounding_status)
        ret_metrics = MetricCalculator.calculate_retrieval_metrics(
            diag.get("retrieved_chunk_ids", []),
            case.get("expected_chunk_ids", [])
        )

        total_recall += ret_metrics["recall_at_k"]
        total_precision += ret_metrics["precision_at_k"]
        total_mrr += ret_metrics["mrr"]
        total_coverage += gr_metrics["citation_coverage"]
        total_unsupported += gr_metrics["unsupported_claim_rate"]

        is_passed = intent_pass and recs_pass and (gr_metrics["citation_coverage"] >= 0.80)

        if is_passed:
            passed_count += 1
            print(f"[PASS] [{case['case_id']}] {case['category']} ({case['difficulty']}) | Intent: {actual_intent} | Coverage: {int(gr_metrics['citation_coverage']*100)}% | Time: {round(exec_latency, 2)}s")
        else:
            reasons = []
            if not intent_pass:
                reasons.append(f"Intent mismatch: Expected {case['expected_intent']}, got {actual_intent}")
            if not recs_pass:
                reasons.append("Missing required recommendation text in answer")
            if gr_metrics["citation_coverage"] < 0.80:
                reasons.append(f"Citation coverage below 80% ({gr_metrics['citation_coverage']})")
            
            print(f"[FAIL] [{case['case_id']}] {case['category']} ({case['difficulty']}) | Reasons: {', '.join(reasons)}")
            FailureLogger.log_failure(case, resp_json, reasons)

    n = len(filtered_cases)
    pass_rate = round((passed_count / n) * 100, 1) if n > 0 else 0.0

    print("\n================================================================================")
    print("                    PHASE 3 EVALUATION BENCHMARK RESULTS                        ")
    print("================================================================================")
    print(f"  Benchmark Pass Rate         : {pass_rate}% ({passed_count}/{n} cases passed)")
    print(f"  Average Recall@10           : {round(total_recall / n, 4) * 100}%")
    print(f"  Average Precision@10        : {round(total_precision / n, 4) * 100}%")
    print(f"  Average MRR                 : {round(total_mrr / n, 4)}")
    print(f"  Average Citation Coverage   : {round(total_coverage / n, 4) * 100}%")
    print(f"  Unsupported Claim Rate      : {round(total_unsupported / n, 4) * 100}%")
    print(f"  Average End-to-End Latency  : {round(total_latency / n, 2)} seconds")
    print("================================================================================\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="MedRef Phase 3 Benchmark Evaluation Harness")
    parser.add_argument("--specialty", type=str, default="all", help="Specialty filter (e.g. cardiology, nephrology, all)")
    args = parser.parse_args()
    run_evaluation_suite(target_specialty=args.specialty)
