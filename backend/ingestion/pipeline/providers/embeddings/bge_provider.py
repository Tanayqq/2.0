import structlog
from typing import List
from fastembed import TextEmbedding
from ...interfaces.embedding_provider import EmbeddingProvider

logger = structlog.get_logger()

class BGEProvider(EmbeddingProvider):
    """
    Embedding provider using fastembed's BGE-small model (BAAI/bge-small-en-v1.5).
    Very fast and lightweight (~133MB footprint).
    """
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        logger.info("initializing_bge_provider", model=self.model_name)
        self.model = TextEmbedding(model_name=self.model_name)
        
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        embeddings_generator = self.model.embed(texts)
        return [emb.tolist() for emb in embeddings_generator]

    def get_dimension(self) -> int:
        return 384  # bge-small-en-v1.5 dimension is 384
