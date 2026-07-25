"""
Phase 3 Pillar B: Retrieval Drift Detector.
Compares historical benchmark runs against current runs to detect recall/coverage regressions over time.
"""
import json
import os
from typing import Dict, Any

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "benchmark_history.json")

class DriftDetector:
    @staticmethod
    def detect_drift(current_metrics: Dict[str, float]) -> Dict[str, Any]:
        previous_metrics = None
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f)
                    if history:
                        previous_metrics = history[-1]
            except Exception:
                pass

        drift_detected = False
        warnings = []

        if previous_metrics:
            prev_recall = previous_metrics.get("recall_at_10", 1.0)
            curr_recall = current_metrics.get("recall_at_10", 1.0)
            
            if curr_recall < (prev_recall - 0.03):
                drift_detected = True
                warnings.append(f"Retrieval Recall Drift: Dropped from {prev_recall*100}% to {curr_recall*100}%")

            prev_cov = previous_metrics.get("citation_coverage", 1.0)
            curr_cov = current_metrics.get("citation_coverage", 1.0)
            if curr_cov < (prev_cov - 0.05):
                drift_detected = True
                warnings.append(f"Citation Coverage Drift: Dropped from {prev_cov*100}% to {curr_cov*100}%")

        # Record current metrics
        history_data = []
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    history_data = json.load(f)
            except Exception:
                history_data = []

        history_data.append(current_metrics)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_data[-50:], f, indent=2)

        return {
            "drift_detected": drift_detected,
            "warnings": warnings,
            "previous_metrics": previous_metrics,
            "current_metrics": current_metrics
        }
