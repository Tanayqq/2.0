from typing import Protocol, List

class EmbeddingProvider(Protocol):
    """
    Protocol for embedding providers (e.g. FastEmbed, MedCPT, BGE).
    Decoupled from specific backend implementations.
    """
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Batch generate embeddings for list of texts.
        """
        ...

    def get_dimension(self) -> int:
        """
        Return the dimension of generated embeddings.
        """
        ...
