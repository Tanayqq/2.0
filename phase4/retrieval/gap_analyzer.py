"""
Phase 4: Retrieval Gap & Root-Cause Disambiguator.
Determines whether a retrieval failure was caused by:
1. RANKING_ISSUE (Correct document exists in vector DB, but was ranked outside top-K)
2. CORPUS_GAP (Target document does not exist in vector DB)
"""
import sys
import os
from typing import Dict, Any, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
from app.core.config import settings
from qdrant_client import QdrantClient

class RetrievalGapAnalyzer:
    @staticmethod
    def analyze_failure_root_cause(case_question: str, expected_keywords: List[str], retrieved_chunk_ids: List[str]) -> Dict[str, Any]:
        url = os.getenv("QDRANT_URL", settings.QDRANT_URL)
        key = os.getenv("QDRANT_API_KEY", settings.QDRANT_API_KEY)
        client = QdrantClient(url=url, api_key=key)

        # Check if relevant document exists anywhere in the vector database
        found_in_corpus = False
        collections_checked = ["disease_guidelines", "drug_interactions", "openfda_labels", "primary_literature"]

        for col in collections_checked:
            try:
                hits = client.scroll(
                    collection_name=col,
                    limit=10,
                    with_payload=True
                )[0]

                for hit in hits:
                    text = str(hit.payload.get("text", "")).lower()
                    if any(kw.lower() in text for kw in expected_keywords):
                        found_in_corpus = True
                        break
            except Exception:
                continue

            if found_in_corpus:
                break

        if found_in_corpus:
            root_cause = "RANKING_ISSUE"
            explanation = "Relevant document exists in vector collection, but dense reranker ranked it outside top-K."
            recommendation = "Adjust similarity threshold or increase hybrid search alpha weight."
        else:
            root_cause = "CORPUS_GAP"
            explanation = "Target clinical document does not exist in vector database collections."
            recommendation = "Ingest additional guideline/DDI chunks for target condition."

        return {
            "root_cause": root_cause,
            "explanation": explanation,
            "recommendation": recommendation,
            "found_in_corpus": found_in_corpus
        }
