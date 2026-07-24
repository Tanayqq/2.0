import os, sys, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app.usecases.drug_resolver import DrugNameResolver
from app.usecases.corpus_quality import CorpusQualityDashboard

BENCHMARK_CLINICAL_QUERIES = [
    ("mounjaro", "tirzepatide"),
    ("keytruda", "pembrolizumab"),
    ("bridion", "sugammadex"),
    ("keppra", "levetiracetam"),
    ("lynparza", "olaparib"),
    ("avycaz", "ceftazidime_avibactam"),
    ("kerendia", "finerenone"),
    ("tezspire", "tezepelumab"),
    ("rinvoq", "upadacitinib"),
    ("stelara", "ustekinumab"),
    ("entresto", "sacubitril_valsartan"),
    ("jardiance", "empagliflozin"),
    ("farxiga", "dapagliflozin"),
    ("coumadin", "warfarin"),
    ("lipitor", "atorvastatin"),
    ("zestril", "lisinopril"),
    ("cozaar", "losartan"),
    ("lasix", "furosemide"),
    ("norvasc", "amlodipine"),
    ("synthroid", "levothyroxine")
]

def test_automated_retrieval_benchmark_recall():
    """
    Automated Evaluation Benchmark Harness:
    Validates >95% entity resolution recall on fixed clinical test cases.
    """
    passed = 0
    total = len(BENCHMARK_CLINICAL_QUERIES)

    for brand, expected_generic in BENCHMARK_CLINICAL_QUERIES:
        resolved = DrugNameResolver.resolve(brand)
        if resolved == expected_generic:
            passed += 1

    recall_pct = (passed / total) * 100.0
    print(f"\n[BENCHMARK EVALUATION] Recall Score: {recall_pct}% ({passed}/{total})")
    assert recall_pct >= 95.0, f"Benchmark recall degraded below target: {recall_pct}%"

def test_automated_benchmark_latency():
    """
    Automated Evaluation Benchmark Harness:
    Validates average lookup latency <= 25.0 ms.
    """
    start_time = time.perf_counter()
    for brand, _ in BENCHMARK_CLINICAL_QUERIES:
        DrugNameResolver.resolve(brand)
    elapsed_ms = ((time.perf_counter() - start_time) / len(BENCHMARK_CLINICAL_QUERIES)) * 1000.0
    print(f"\n[BENCHMARK EVALUATION] Average Lookup Latency: {round(elapsed_ms, 3)} ms")
    assert elapsed_ms <= 25.0, f"Latency exceeded 25ms threshold: {round(elapsed_ms, 3)} ms"
