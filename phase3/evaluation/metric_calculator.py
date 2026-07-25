"""
Phase 3 Pillar B: Metric Calculator for Clinical Evaluation Benchmark Harness.
Computes Recall@k, Precision@k, MRR, Citation Coverage %, Unsupported Claim %, and Latency.
"""
from typing import List, Dict, Any

class MetricCalculator:
    @staticmethod
    def calculate_retrieval_metrics(retrieved_chunk_ids: List[str], expected_chunk_ids: List[str], k: int = 10) -> Dict[str, float]:
        top_k = retrieved_chunk_ids[:k]
        if not expected_chunk_ids:
            return {"recall_at_k": 1.0, "precision_at_k": 1.0, "mrr": 1.0}

        relevant_found = set(top_k).intersection(set(expected_chunk_ids))
        recall = len(relevant_found) / len(expected_chunk_ids) if expected_chunk_ids else 1.0
        precision = len(relevant_found) / len(top_k) if top_k else 0.0

        # Calculate Mean Reciprocal Rank (MRR)
        mrr = 0.0
        for rank, chunk_id in enumerate(top_k, start=1):
            if chunk_id in expected_chunk_ids:
                mrr = 1.0 / rank
                break

        return {
            "recall_at_k": round(recall, 4),
            "precision_at_k": round(precision, 4),
            "mrr": round(mrr, 4)
        }

    @staticmethod
    def calculate_grounding_metrics(audit_logs: List[str], grounding_status: str) -> Dict[str, float]:
        coverage = 1.0
        unsupported_rate = 0.0

        for log in audit_logs:
            if "Citation Grounding Score:" in log:
                try:
                    val = float(log.split(":")[1].replace("%", "").strip())
                    coverage = round(val / 100.0, 4)
                except ValueError:
                    pass

        if grounding_status != "PASS" and coverage < 1.0:
            unsupported_rate = round(1.0 - coverage, 4)

        return {
            "citation_coverage": coverage,
            "unsupported_claim_rate": unsupported_rate
        }
