from typing import List, Dict
from app.domain.interfaces import EmbeddingModelProtocol, CrossEncoderProtocol
from fastembed import TextEmbedding


class FastEmbedModel(EmbeddingModelProtocol):
    """
    Ultra-lightweight embedding model using fastembed (ONNX-based).
    Dense-only search to fit within Render's 512MB free tier.
    """
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.dense_model = TextEmbedding(model_name=model_name)

    def embed_query(self, text: str) -> List[float]:
        result = list(self.dense_model.embed([text]))[0]
        return result.tolist()

    def embed_sparse(self, text: str) -> Dict[int, float]:
        # Return empty sparse vector — dense-only mode for free tier
        return {}


class NoOpCrossEncoder(CrossEncoderProtocol):
    """
    Pass-through for free-tier deployment.
    Returns documents sorted by their original retrieval score.
    """
    def rerank(self, query: str, documents: list, top_k: int = 5) -> list:
        if not documents:
            return []
        documents.sort(key=lambda x: x.score, reverse=True)
        return documents[:top_k]
