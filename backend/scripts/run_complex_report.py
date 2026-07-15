"""
Run the complex 10-drug report query locally and trace the RAG pipeline.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=" * 80)
print("RUNNING COMPLEX REPORT QUERY")
print("=" * 80)

payload = {
    "question": (
        "Using ONLY the indexed corpus, generate a report containing exactly these drugs: "
        "Metformin Warfarin Lisinopril Atorvastatin Gabapentin Omeprazole Amoxicillin Albuterol "
        "Losartan Ibuprofen For each drug return ONLY: • Contraindications • Warnings • Drug Interactions "
        "Rules: - Keep every drug completely separate. - Never mix information between drugs. - "
        "Every sentence must have an inline citation. - Every citation must exist in Sources Referenced. - "
        "If a section is unavailable write exactly: Not found in available sources."
    ),
    "filters": {}
}

# 1. Call debug endpoint to see retrieval logs
print("\n--- DEBUG RETRIEVAL ---")
res_debug = client.post("/api/v1/debug/retrieval", json=payload)
if res_debug.status_code == 200:
    data = res_debug.json()
    print("Summary:")
    for k, v in data.get("debug_summary", {}).items():
        print(f"  {k}: {v}")
else:
    print(f"Failed debug: {res_debug.status_code} {res_debug.text}")

# 2. Call main query endpoint
print("\n--- MAIN QUERY RESPONSE ---")
res_query = client.post("/api/v1/query", json=payload)
if res_query.status_code == 200:
    data = res_query.json()
    print(f"Answer:\n{data.get('answer')}\n")
    print("Citations:")
    for cit in data.get("citations", []):
        print(f"  [{cit.get('citation_number') or cit.get('document_id')}] {cit.get('source')} (Similarity: {cit.get('similarity')})")
else:
    print(f"Failed query: {res_query.status_code} {res_query.text}")
