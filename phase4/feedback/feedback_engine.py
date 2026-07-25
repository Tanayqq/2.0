"""
Phase 4: Clinician Feedback Engine.
Collects and persists real-world clinician feedback (Helpful, Incorrect, Needs Citation, Incomplete)
for continuous clinical validation and query quality analytics.
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List

FEEDBACK_LOG_PATH = os.path.join(os.path.dirname(__file__), "clinician_feedback.json")

class ClinicianFeedbackEngine:
    @staticmethod
    def record_feedback(query_text: str, request_id: str, rating: str, feedback_type: str, comments: str = "") -> Dict[str, Any]:
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": request_id,
            "query_text": query_text,
            "rating": rating, # Helpful, Partially Helpful, Incorrect, Incomplete
            "feedback_type": feedback_type, # Needs Citation, Dosing Error, DDI Missed, etc.
            "comments": comments
        }

        feedback_list = []
        if os.path.exists(FEEDBACK_LOG_PATH):
            try:
                with open(FEEDBACK_LOG_PATH, "r", encoding="utf-8") as f:
                    feedback_list = json.load(f)
            except Exception:
                feedback_list = []

        feedback_list.append(entry)

        with open(FEEDBACK_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(feedback_list, f, indent=2)

        return {"status": "SUCCESS", "feedback_count": len(feedback_list), "entry": entry}

    @staticmethod
    def get_feedback_analytics() -> Dict[str, Any]:
        if not os.path.exists(FEEDBACK_LOG_PATH):
            return {"total_feedback": 0, "positive_pct": 100.0, "common_issues": []}

        try:
            with open(FEEDBACK_LOG_PATH, "r", encoding="utf-8") as f:
                feedback_list = json.load(f)
        except Exception:
            return {"total_feedback": 0, "positive_pct": 100.0, "common_issues": []}

        if not feedback_list:
            return {"total_feedback": 0, "positive_pct": 100.0, "common_issues": []}

        positive_count = sum(1 for fb in feedback_list if fb.get("rating") == "Helpful")
        positive_pct = round((positive_count / len(feedback_list)) * 100, 1)

        issues = {}
        for fb in feedback_list:
            ftype = fb.get("feedback_type", "General")
            issues[ftype] = issues.get(ftype, 0) + 1

        sorted_issues = sorted([{"issue": k, "count": v} for k, v in issues.items()], key=lambda x: x["count"], reverse=True)

        return {
            "total_feedback": len(feedback_list),
            "positive_pct": positive_pct,
            "common_issues": sorted_issues
        }
