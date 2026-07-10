import structlog
from typing import List
from fastembed import TextEmbedding
from ...interfaces.embedding_provider import EmbeddingProvider

logger = structlog.get_logger()

class FastEmbedProvider(EmbeddingProvider):
    """
    Embedding provider using fastembed (ONNX-based all-MiniLM-L6-v2 by default).
    Extremely lightweight and fast (~90MB RAM footprint).
    """
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        logger.info("initializing_fastembed_provider", model=self.model_name)
        self.model = TextEmbedding(model_name=self.model_name)
        
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed list of texts in batch.
        """
        # fastembed handles batching natively under the hood
        embeddings_generator = self.model.embed(texts)
        return [emb.tolist() for emb in embeddings_generator]

    def get_dimension(self) -> int:
        # all-MiniLM-L6-v2 dimension is 384
        if "all-MiniLM-L6-v2" in self.model_name:
            return 384
        return 384  # Fallback
