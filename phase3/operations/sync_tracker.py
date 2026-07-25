"""
Phase 3 Pillar C: Source Synchronization Tracker & Freshness Registry.
Tracks versioning, publication date, last sync, next sync, and sync status across all 14 authoritative medical sources.
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List

SYNC_REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "source_sync_registry.json")

DEFAULT_SOURCES: List[Dict[str, Any]] = [
    {"source_id": "openfda", "name": "openFDA Drug Labels", "authority": "FDA", "version": "2026.1", "publication_date": "2026-01-15", "sync_interval_days": 30, "status": "ACTIVE"},
    {"source_id": "dailymed", "name": "DailyMed Package Inserts", "authority": "NLM", "version": "2026.1", "publication_date": "2026-01-20", "sync_interval_days": 30, "status": "ACTIVE"},
    {"source_id": "kdigo", "name": "KDIGO CKD Guidelines", "authority": "KDIGO", "version": "2024.2", "publication_date": "2024-11-10", "sync_interval_days": 90, "status": "ACTIVE"},
    {"source_id": "ada", "name": "ADA Standards of Care", "authority": "ADA", "version": "2026.1", "publication_date": "2026-01-01", "sync_interval_days": 90, "status": "ACTIVE"},
    {"source_id": "acc_aha", "name": "ACC/AHA Heart Failure Guidelines", "authority": "ACC/AHA", "version": "2024.1", "publication_date": "2024-05-15", "sync_interval_days": 90, "status": "ACTIVE"},
    {"source_id": "esc", "name": "ESC Cardiovascular Guidelines", "authority": "ESC", "version": "2024.1", "publication_date": "2024-08-30", "sync_interval_days": 90, "status": "ACTIVE"},
    {"source_id": "cdsco", "name": "CDSCO India Pharmacopoeia", "authority": "CDSCO", "version": "2025.3", "publication_date": "2025-10-01", "sync_interval_days": 60, "status": "ACTIVE"},
    {"source_id": "nfi", "name": "National Formulary of India", "authority": "NFI", "version": "2025.1", "publication_date": "2025-06-15", "sync_interval_days": 60, "status": "ACTIVE"},
    {"source_id": "who", "name": "WHO Essential Medicines List", "authority": "WHO", "version": "2025.2", "publication_date": "2025-09-01", "sync_interval_days": 180, "status": "ACTIVE"},
    {"source_id": "idsa", "name": "IDSA Antimicrobial Guidelines", "authority": "IDSA", "version": "2024.1", "publication_date": "2024-07-01", "sync_interval_days": 90, "status": "ACTIVE"},
    {"source_id": "gold", "name": "GOLD COPD Strategy", "authority": "GOLD", "version": "2025.1", "publication_date": "2024-11-20", "sync_interval_days": 90, "status": "ACTIVE"},
    {"source_id": "gina", "name": "GINA Asthma Strategy", "authority": "GINA", "version": "2025.1", "publication_date": "2025-05-10", "sync_interval_days": 90, "status": "ACTIVE"},
    {"source_id": "nccn", "name": "NCCN Clinical Practice Guidelines", "authority": "NCCN", "version": "2025.1", "publication_date": "2025-01-10", "sync_interval_days": 90, "status": "ACTIVE"},
    {"source_id": "rxnorm", "name": "RxNorm Standard Terminology", "authority": "NLM", "version": "2026.01", "publication_date": "2026-01-05", "sync_interval_days": 30, "status": "ACTIVE"}
]

class SourceSyncTracker:
    @staticmethod
    def get_sync_registry() -> List[Dict[str, Any]]:
        if os.path.exists(SYNC_REGISTRY_PATH):
            try:
                with open(SYNC_REGISTRY_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        # Initialize default registry
        now_str = datetime.now().strftime("%Y-%m-%d")
        registry = []
        for src in DEFAULT_SOURCES:
            interval = src.get("sync_interval_days", 30)
            next_sync = (datetime.now() + timedelta(days=interval)).strftime("%Y-%m-%d")
            entry = dict(src)
            entry["last_sync"] = now_str
            entry["next_sync"] = next_sync
            registry.append(entry)

        with open(SYNC_REGISTRY_PATH, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2)

        return registry

    @staticmethod
    def update_source_sync(source_id: str, new_version: str = None, status: str = "ACTIVE") -> Dict[str, Any]:
        registry = SourceSyncTracker.get_sync_registry()
        now_str = datetime.now().strftime("%Y-%m-%d")
        updated_entry = None

        for entry in registry:
            if entry["source_id"] == source_id:
                entry["last_sync"] = now_str
                interval = entry.get("sync_interval_days", 30)
                entry["next_sync"] = (datetime.now() + timedelta(days=interval)).strftime("%Y-%m-%d")
                entry["status"] = status
                if new_version:
                    entry["version"] = new_version
                updated_entry = entry
                break

        with open(SYNC_REGISTRY_PATH, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2)

        return updated_entry

if __name__ == "__main__":
    reg = SourceSyncTracker.get_sync_registry()
    print("================================================================================")
    print("        MEDREF PHASE 3 PILLAR C — SOURCE SYNCHRONIZATION REGISTRY               ")
    print("================================================================================")
    print(f"{'Source ID':15} | {'Authority':10} | {'Version':10} | {'Last Sync':12} | {'Next Sync':12} | {'Status':10}")
    print("-" * 80)
    for s in reg:
        print(f"{s['source_id']:15} | {s['authority']:10} | {s['version']:10} | {s['last_sync']:12} | {s['next_sync']:12} | {s['status']:10}")
    print("================================================================================\n")
