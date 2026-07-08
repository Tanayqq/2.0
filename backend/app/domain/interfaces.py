from typing import Protocol, List, Dict, Any, Optional
from app.domain.models import ReferenceDocument

class LLMProviderProtocol(Protocol):
    """
    Strict protocol for LLM providers.
    Ensures the RAG pipeline is fully decoupled from the underlying LLM.
    """
    def generate(self, prompt: str) -> str:
        ...

class VectorDatabaseProtocol(Protocol):
    """
    Protocol for Vector Database interactions.
    """
    def search(self, query_vector: List[float], top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[ReferenceDocument]:
        ...
        
    def hybrid_search(self, dense_vector: List[float], sparse_vector: Dict[int, float], top_k: int = 20, filters: Optional[Dict[str, Any]] = None) -> List[ReferenceDocument]:
        ...

class EmbeddingModelProtocol(Protocol):
    """
    Protocol for generating text embeddings.
    """
    def embed_query(self, text: str) -> List[float]:
        ...
        
    def embed_sparse(self, text: str) -> Dict[int, float]:
        ...

class CrossEncoderProtocol(Protocol):
    """
    Protocol for re-ranking documents against a query.
    """
    def rerank(self, query: str, documents: List[ReferenceDocument], top_k: int = 5) -> List[ReferenceDocument]:
        ...
