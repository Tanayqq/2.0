import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qdrant_client import QdrantClient
from qdrant_client.models import PayloadSchemaType
from app.core.config import settings

def main():
    print(f"Connecting to Qdrant at {settings.QDRANT_URL}...")
    client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY
    )
    
    collection_name = "openfda_labels"
    print(f"Creating payload indexes for collection '{collection_name}'...")
    
    # 1. drug_name keyword index
    try:
        client.create_payload_index(
            collection_name=collection_name,
            field_name="drug_name",
            field_schema=PayloadSchemaType.KEYWORD
        )
        print("Successfully created index for 'drug_name'")
    except Exception as e:
        print(f"Failed to create index for 'drug_name': {e}")
        
    # 2. canonical_section keyword index
    try:
        client.create_payload_index(
            collection_name=collection_name,
            field_name="canonical_section",
            field_schema=PayloadSchemaType.KEYWORD
        )
        print("Successfully created index for 'canonical_section'")
    except Exception as e:
        print(f"Failed to create index for 'canonical_section': {e}")
        
    print("Done!")

if __name__ == "__main__":
    main()
