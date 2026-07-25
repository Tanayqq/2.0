"""
Phase 4 Data Governance & Provenance Registry.
Tracks complete metadata provenance for every ingested document chunk:
source, version, publication_date, authority, license, collection, chunk_count, embedding_model, sha256.
"""
import json
import os
import hashlib
from typing import Dict, Any, List

GOVERNANCE_REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "governance_manifest.json")

class DataGovernanceRegistry:
    @staticmethod
    def register_document(
        doc_id: str,
        title: str,
        authority: str,
        collection: str,
        version: str,
        pub_date: str,
        license_type: str = "Public Domain / Open Access",
        chunk_count: int = 1,
        content_sample: str = ""
    ) -> Dict[str, Any]:
        doc_hash = hashlib.sha256(content_sample.encode("utf-8")).hexdigest() if content_sample else "sha256:default"

        entry = {
            "doc_id": doc_id,
            "title": title,
            "authority": authority,
            "collection": collection,
            "version": version,
            "publication_date": pub_date,
            "license": license_type,
            "chunk_count": chunk_count,
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "sha256": doc_hash
        }

        registry = []
        if os.path.exists(GOVERNANCE_REGISTRY_PATH):
            try:
                with open(GOVERNANCE_REGISTRY_PATH, "r", encoding="utf-8") as f:
                    registry = json.load(f)
            except Exception:
                registry = []

        registry = [r for r in registry if r.get("doc_id") != doc_id]
        registry.append(entry)

        with open(GOVERNANCE_REGISTRY_PATH, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2)

        return entry

    @staticmethod
    def get_provenance_summary() -> Dict[str, Any]:
        if not os.path.exists(GOVERNANCE_REGISTRY_PATH):
            return {"total_registered_documents": 0, "authorities": [], "collections": {}}

        try:
            with open(GOVERNANCE_REGISTRY_PATH, "r", encoding="utf-8") as f:
                registry = json.load(f)
        except Exception:
            return {"total_registered_documents": 0, "authorities": [], "collections": {}}

        authorities = list(set(r.get("authority", "FDA") for r in registry))
        collections = {}
        for r in registry:
            col = r.get("collection", "general")
            collections[col] = collections.get(col, 0) + 1

        return {
            "total_registered_documents": len(registry),
            "authorities_count": len(authorities),
            "authorities": authorities,
            "collection_breakdown": collections
        }
