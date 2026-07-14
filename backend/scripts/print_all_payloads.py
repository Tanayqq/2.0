"""
Print the raw payloads of all points in the openfda_labels collection.
"""
import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.core.config import settings
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
    response = client.scroll(
        collection_name=collection_name,
        limit=100,
        with_payload=True,
        with_vectors=False
    )
    points = response[0]
    
    print(f"\nRaw payloads for all {len(points)} points:")
    for p in points:
        print(f"\nID: {p.id}")
        print(json.dumps(p.payload, indent=2))
        
except Exception as e:
    print(f"Error querying Qdrant: {e}")
