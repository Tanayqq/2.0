"""
Check Qdrant database to see all drugs and their sections/categories.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from backend.app.core.config import settings
from qdrant_client import QdrantClient

# Load dotenv if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

qdrant_url = os.getenv("QDRANT_URL", settings.QDRANT_URL)
qdrant_api_key = os.getenv("QDRANT_API_KEY", settings.QDRANT_API_KEY)

print(f"Connecting to Qdrant at: {qdrant_url}")
client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

collection_name = "openfda_labels"

try:
    # Scroll points up to 1000 to list all drugs/sections
    response = client.scroll(
        collection_name=collection_name,
        limit=1000,
        with_payload=True,
        with_vectors=False
    )
    points = response[0]
    
    print(f"\nFound {len(points)} total points in collection '{collection_name}':")
    drug_sections = {}
    for p in points:
        meta = p.payload.get("metadata", p.payload)
        drug = meta.get("drug", meta.get("drug_name", "unknown")).lower()
        sec = meta.get("section", meta.get("category", "unknown"))
        
        if drug not in drug_sections:
            drug_sections[drug] = {}
        drug_sections[drug][sec] = drug_sections[drug].get(sec, 0) + 1
        
    for drug, secs in sorted(drug_sections.items()):
        print(f"\nDrug: '{drug}'")
        for sec, count in sorted(secs.items()):
            print(f"  Section: '{sec}' -> {count} chunks")
            
except Exception as e:
    print(f"Error querying Qdrant: {e}")
