"""
Phase 3 Pillar B: Retrieval Failure Logger.
Automatically logs failed benchmark cases to phase3/evaluation/retrieval_failures.json for backlog prioritization.
"""
import json
import os
from typing import Dict, Any, List

FAILURES_FILE_PATH = os.path.join(os.path.dirname(__file__), "retrieval_failures.json")

class FailureLogger:
    @staticmethod
    def log_failure(case_data: Dict[str, Any], actual_response: Dict[str, Any], failure_reasons: List[str]):
        failure_record = {
            "case_id": case_data.get("case_id"),
            "category": case_data.get("category"),
            "difficulty": case_data.get("difficulty"),
            "question": case_data.get("question"),
            "expected_intent": case_data.get("expected_intent"),
            "actual_intent": actual_response.get("metadata", {}).get("retrieval_diagnostics", {}).get("intent"),
            "expected_recommendation": case_data.get("expected_recommendation"),
            "failure_reasons": failure_reasons,
            "actual_answer": actual_response.get("answer", "")[:500],
            "grounding_status": actual_response.get("metadata", {}).get("grounding_status"),
            "retrieved_chunk_count": len(actual_response.get("citations", []))
        }

        existing_failures = []
        if os.path.exists(FAILURES_FILE_PATH):
            try:
                with open(FAILURES_FILE_PATH, "r", encoding="utf-8") as f:
                    existing_failures = json.load(f)
            except Exception:
                existing_failures = []

        # Replace existing failure record for case_id if present
        existing_failures = [f for f in existing_failures if f.get("case_id") != case_data.get("case_id")]
        existing_failures.append(failure_record)

        with open(FAILURES_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(existing_failures, f, indent=2)

        return failure_record
