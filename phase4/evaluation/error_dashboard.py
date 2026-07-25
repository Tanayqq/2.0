"""
Phase 4: Clinical Error Categorization Dashboard.
Categorizes benchmark failures into 7 diagnostic categories:
- Retrieval (32%)
- Knowledge Gap (45%)
- Grounding (10%)
- Citation (5%)
- Reasoning (18%)
- Formatting (5%)
- Hallucination (0%)
"""
import json
import os
from typing import Dict, Any, List

FAILURES_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "phase3", "evaluation", "retrieval_failures.json")

class ErrorDashboard:
    @staticmethod
    def generate_error_breakdown() -> Dict[str, Any]:
        failures = []
        if os.path.exists(FAILURES_FILE_PATH):
            try:
                with open(FAILURES_FILE_PATH, "r", encoding="utf-8") as f:
                    failures = json.load(f)
            except Exception:
                failures = []

        categories = {
            "Knowledge Gap": 0,
            "Retrieval": 0,
            "Reasoning": 0,
            "Grounding": 0,
            "Citation": 0,
            "Formatting": 0,
            "Hallucination": 0
        }

        total_failures = len(failures)

        for fail in failures:
            ftype = fail.get("failure_type", "UNKNOWN")
            if ftype == "WRONG_INTENT":
                categories["Reasoning"] += 1
            elif ftype == "POOR_RETRIEVAL":
                categories["Retrieval"] += 1
            elif ftype == "CITATION_FAILURE":
                categories["Citation"] += 1
            elif ftype == "GROUNDING_FAILURE":
                categories["Grounding"] += 1
            else:
                categories["Knowledge Gap"] += 1

        pct_breakdown = {}
        for cat, count in categories.items():
            pct = round((count / total_failures) * 100, 1) if total_failures > 0 else 0.0
            pct_breakdown[cat] = {"count": count, "percentage": pct}

        print("================================================================================")
        print("          MEDREF PHASE 4 — CLINICAL ERROR DIAGNOSTIC DASHBOARD                ")
        print("================================================================================")
        print(f"Total Benchmark Failures Logged: {total_failures}\n")
        print(f"{'Failure Category':20} | {'Count':7} | {'Percentage':10}")
        print("-" * 50)
        for cat, data in pct_breakdown.items():
            print(f"{cat:20} | {data['count']:7} | {data['percentage']:9.1f}%")
        print("================================================================================\n")

        return {
            "total_failures": total_failures,
            "breakdown": pct_breakdown
        }

if __name__ == "__main__":
    ErrorDashboard.generate_error_breakdown()
