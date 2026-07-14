"""
Run ProcessClinicalQueryUseCase locally for Lisinopril contraindications.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=" * 80)
print("RUNNING LOCAL RAG QUERY FOR LISINOPRIL CONTRAINDICATIONS")
print("=" * 80)

payload = {
    "question": "Summarize Lisinopril contraindications",
    "filters": {}
}

res_query = client.post("/api/v1/query", json=payload)
if res_query.status_code == 200:
    data = res_query.json()
    print(f"Answer:\n{data.get('answer')}\n")
    print("Citations:")
    for cit in data.get("citations", []):
        print(f"  [{cit.get('citation_number') or cit.get('document_id')}] {cit.get('source')} (Similarity: {cit.get('similarity')})")
else:
    print(f"Failed query: {res_query.status_code} {res_query.text}")
