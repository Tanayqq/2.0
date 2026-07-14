"""
Ingestion script — seeds the Qdrant Cloud collection with the MVP corpus.
Uses dense-only vectors (fastembed/ONNX) to match the production backend.

Usage:
    python seed_qdrant.py

Required env vars (set in .env or pass directly):
    QDRANT_URL      — your Qdrant Cloud cluster URL
    QDRANT_API_KEY  — your Qdrant Cloud API key
"""

import sys
import os
import json
import uuid

# Allow imports from backend/app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

QDRANT_URL     = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
COLLECTION     = "openfda_labels"
DENSE_DIM      = 384   # all-MiniLM-L6-v2 output dimension
MODEL_NAME     = "sentence-transformers/all-MiniLM-L6-v2"

def run_ingestion():
    # ── Load corpus ──────────────────────────────────────────────────────────
    corpus_path = os.path.join(os.path.dirname(__file__), "mvp_corpus.json")
    print(f"Loading corpus from {corpus_path} ...")
    with open(corpus_path, "r", encoding="utf-8") as f:
        corpus = json.load(f)
    print(f"  {len(corpus)} documents loaded.")

    # ── Load embedding model ──────────────────────────────────────────────────
    print(f"Loading fastembed model '{MODEL_NAME}' ...")
    embedder = TextEmbedding(model_name=MODEL_NAME)
    print("  Model ready.")

    # ── Connect to Qdrant Cloud ───────────────────────────────────────────────
    if not QDRANT_URL:
        print("ERROR: QDRANT_URL is not set. Add it to your .env file.")
        sys.exit(1)
    print(f"Connecting to Qdrant Cloud at {QDRANT_URL} ...")
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    print("  Connected.")

    # ── Create / recreate collection ─────────────────────────────────────────
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION in existing:
        print(f"Collection '{COLLECTION}' exists — deleting and recreating ...")
        client.delete_collection(COLLECTION)

    print(f"Creating collection '{COLLECTION}' (dense-only, dim={DENSE_DIM}) ...")
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config={
            "dense": VectorParams(size=DENSE_DIM, distance=Distance.COSINE)
        }
    )
    print("  Collection created.")

    # ── Embed & upload ────────────────────────────────────────────────────────
    texts   = [item["content"] for item in corpus]
    print("Embedding all documents ...")
    vectors = list(embedder.embed(texts))   # batch embed
    print(f"  {len(vectors)} vectors generated.")

    points = []
    from ingestion.pipeline.parser import MedicalParser
    parser = MedicalParser()
    for item, vec in zip(corpus, vectors):
        # Qdrant requires UUID or integer IDs — derive a stable UUID from the doc id string
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, item.get("id", str(uuid.uuid4()))))
        
        # Normalize category/section to lowercase canonical form
        normalized_item = item.copy()
        if "category" in normalized_item:
            normalized_item["category"] = parser.normalize_section_title(normalized_item["category"])
        if "section" in normalized_item:
            normalized_item["section"] = parser.normalize_section_title(normalized_item["section"])
            
        points.append(PointStruct(
            id      = point_id,
            vector  = {"dense": vec.tolist()},
            payload = normalized_item
        ))

    print(f"Uploading {len(points)} points to Qdrant Cloud ...")
    client.upsert(collection_name=COLLECTION, points=points)
    print("Ingestion complete!")

if __name__ == "__main__":
    run_ingestion()
