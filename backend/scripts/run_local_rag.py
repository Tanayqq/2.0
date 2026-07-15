"""
Run ProcessClinicalQueryUseCase locally for "Summarize Metformin contraindications"
and inspect the trace/filter decisions.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock dependencies or load real ones if possible
# Let's load the app and run the usecase using the dependency overrides
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=" * 80)
print("RUNNING LOCAL RAG QUERY")
print("=" * 80)

payload = {
    "question": "Metformin",
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
    print("\nFilter Trace (First 5):")
    for item in data.get("filter_trace", [])[:5]:
        print(f"  UUID: {item['uuid']}, Drug: {item['drug_name']}, Raw Sec: {item['raw_section']}, Norm Sec: {item['normalized_section']}, Decision: {item['decision']}, Score: {item['score']}")
else:
    print(f"Failed debug: {res_debug.status_code} {res_debug.text}")

# 2. Call main query endpoint
print("\n--- MAIN QUERY RESPONSE ---")
res_query = client.post("/api/v1/query", json=payload)
if res_query.status_code == 200:
    data = res_query.json()
    print(f"Answer:\n{data.get('answer')}\n")
    print("Metadata:")
    import json
    print(json.dumps(data.get("metadata", {}), indent=2))
    print("\nCitations:")
    for cit in data.get("citations", []):
        print(f"  [{cit.get('citation_number') or cit.get('document_id')}] {cit.get('source')} (Similarity: {cit.get('similarity')})")
else:
    print(f"Failed query: {res_query.status_code} {res_query.text}")
