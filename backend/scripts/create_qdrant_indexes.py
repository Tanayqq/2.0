"""
Create required payload indexes in Qdrant Cloud for the collection.
Without keyword indexes on 'drug', Qdrant Cloud rejects queries with filters.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.core.config import settings
from qdrant_client import QdrantClient
from qdrant_client.http import models

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

print(f"Creating keyword index on 'drug' field in collection '{collection_name}'...")
try:
    client.create_payload_index(
        collection_name=collection_name,
        field_name="drug",
        field_schema=models.PayloadSchemaType.KEYWORD
    )
    print("Keyword index on 'drug' created successfully!")
except Exception as e:
    print(f"Error creating 'drug' index: {e}")

print(f"Creating keyword index on 'category' field in collection '{collection_name}'...")
try:
    client.create_payload_index(
        collection_name=collection_name,
        field_name="category",
        field_schema=models.PayloadSchemaType.KEYWORD
    )
    print("Keyword index on 'category' created successfully!")
except Exception as e:
    print(f"Error creating 'category' index: {e}")

print(f"Creating keyword index on 'section' field in collection '{collection_name}'...")
try:
    client.create_payload_index(
        collection_name=collection_name,
        field_name="section",
        field_schema=models.PayloadSchemaType.KEYWORD
    )
    print("Keyword index on 'section' created successfully!")
except Exception as e:
    print(f"Error creating 'section' index: {e}")
