from typing import List, Dict
from app.domain.interfaces import EmbeddingModelProtocol, CrossEncoderProtocol
from fastembed import TextEmbedding, SparseTextEmbedding


class FastEmbedModel(EmbeddingModelProtocol):
    """
    Lightweight embedding model using fastembed (ONNX-based).
    Uses ~90MB RAM instead of ~1GB+ for PyTorch-based models.
    Handles both dense and sparse embeddings for hybrid search.
    """
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.dense_model = TextEmbedding(model_name=model_name)
        self.sparse_model = SparseTextEmbedding(model_name="prithvida/Splade_PP_en_v1")

    def embed_query(self, text: str) -> List[float]:
        # Dense Embedding via ONNX (no PyTorch needed)
        result = list(self.dense_model.embed([text]))[0]
        return result.tolist()

    def embed_sparse(self, text: str) -> Dict[int, float]:
        # Sparse Embedding (SPLADE)
        sparse_result = list(self.sparse_model.embed([text]))[0]
        return {int(idx): float(val) for idx, val in zip(sparse_result.indices, sparse_result.values)}


class NoOpCrossEncoder(CrossEncoderProtocol):
    """
    Pass-through cross-encoder for free-tier deployment.
    Simply returns the top_k documents by their original retrieval score
    without loading a heavy re-ranking model (~400MB savings).
    When scaling up, swap this for MSMarcoCrossEncoder.
    """
    def rerank(self, query: str, documents: list, top_k: int = 5) -> list:
        if not documents:
            return []
        # Sort by existing retrieval score (from hybrid search)
        documents.sort(key=lambda x: x.score, reverse=True)
        return documents[:top_k]
