"""
Check Qdrant database to see what chunks and sections exist for Metformin.
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

# Let's scroll points for Metformin
from qdrant_client.http import models

filter_drug = models.Filter(
    must=[
        models.FieldCondition(
            key="drug",
            match=models.MatchValue(value="Metformin")
        )
    ]
)

try:
    response = client.scroll(
        collection_name=collection_name,
        scroll_filter=filter_drug,
        limit=100,
        with_payload=True,
        with_vectors=False
    )
    points = response[0]
    
    print(f"\nFound {len(points)} points for Metformin:")
    sections = {}
    for p in points:
        meta = p.payload.get("metadata", p.payload)
        sec = meta.get("section", meta.get("category", "unknown"))
        sections[sec] = sections.get(sec, 0) + 1
        
    for sec, count in sorted(sections.items()):
        print(f"  Section: '{sec}' -> {count} chunks")
        
except Exception as e:
    print(f"Error querying Qdrant: {e}")
