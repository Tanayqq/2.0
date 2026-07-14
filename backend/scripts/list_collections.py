"""
List all collections in the Qdrant database to see if there is another collection.
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

try:
    collections = client.get_collections().collections
    print("\nCollections found:")
    for c in collections:
        print(f"  - {c.name}")
except Exception as e:
    print(f"Error: {e}")
