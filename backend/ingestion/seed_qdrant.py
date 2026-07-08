import sys
import os
import json
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.infrastructure.embedding_models import MedCPTEmbeddingModel
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, SparseVectorParams, PointStruct

def run_ingestion():
    print("Loading MVP Corpus from mvp_corpus.json...")
    corpus_path = os.path.join(os.path.dirname(__file__), "mvp_corpus.json")
    with open(corpus_path, "r", encoding="utf-8") as f:
        corpus_data = json.load(f)
        
    print("Initializing embedding models (Dense + Sparse)...")
    embedder = MedCPTEmbeddingModel()
    
    print("Connecting to Qdrant...")
    client = QdrantClient(host="localhost", port=6333)
    
    collection_name = "openfda_labels"
    
    collections = client.get_collections().collections
    if not any(c.name == collection_name for c in collections):
        print(f"Creating collection {collection_name} for Hybrid Search...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config={
                "dense": VectorParams(size=768, distance=Distance.COSINE)
            },
            sparse_vectors_config={
                "sparse": SparseVectorParams()
            }
        )
    
    points = []
    print("Embedding data sequentially...")
    for idx, item in enumerate(corpus_data):
        # Generate both vectors
        dense_vec = embedder.embed_query(item["content"])
        sparse_dict = embedder.embed_sparse(item["content"])
        
        # Format sparse for Qdrant
        sparse_vec = {
            "indices": list(sparse_dict.keys()),
            "values": list(sparse_dict.values())
        }
        
        doc_id = item.get("id", str(uuid.uuid4()))
        
        point = PointStruct(
            id=doc_id,
            vector={
                "dense": dense_vec,
                "sparse": sparse_vec
            },
            payload=item
        )
        points.append(point)
        
    print(f"Uploading {len(points)} hybrid points to Qdrant...")
    client.upsert(
        collection_name=collection_name,
        points=points
    )
    print("Ingestion complete!")

if __name__ == "__main__":
    run_ingestion()
