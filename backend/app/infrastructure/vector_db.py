from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, Prefetch, models
from typing import List, Dict, Any, Optional
from app.domain.interfaces import VectorDatabaseProtocol
from app.domain.models import ReferenceDocument

class QdrantAdapter(VectorDatabaseProtocol):
    """
    Adapter for Qdrant vector database supporting Hybrid Search and Metadata Filtering.
    """
    def __init__(self, url: str = "http://localhost:6333", api_key: str = "", collection_name: str = "openfda_labels"):
        if api_key:
            self.client = QdrantClient(url=url, api_key=api_key, timeout=60.0)
        else:
            self.client = QdrantClient(url=url, timeout=60.0)
        self.collection_name = collection_name

    def _build_filter(self, filters: Optional[Dict[str, Any]]) -> Optional[Filter]:
        if not filters:
            return None
        
        conditions = []
        for key, value in filters.items():
            if isinstance(value, list):
                # Use MatchAny for list/OR logic in Qdrant keyword payloads
                conditions.append(FieldCondition(key=key, match=models.MatchAny(any=value)))
            else:
                conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
                
        return Filter(must=conditions)

    def search(self, query_vector: List[float], top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[ReferenceDocument]:
        qdrant_filter = self._build_filter(filters)
        
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            using="dense",
            limit=top_k,
            query_filter=qdrant_filter
        )
        
        return self._map_results(search_result.points)

    def hybrid_search(self, dense_vector: List[float], sparse_vector: Dict[int, float], top_k: int = 20, filters: Optional[Dict[str, Any]] = None) -> List[ReferenceDocument]:
        """
        Executes a true hybrid search using Qdrant's Reciprocal Rank Fusion (RRF) 
        combining semantic meaning (dense) and exact keyword matches (sparse).
        """
        qdrant_filter = self._build_filter(filters)
        
        # Build Qdrant sparse vector format
        sparse_indices = list(sparse_vector.keys())
        sparse_values = list(sparse_vector.values())
        qdrant_sparse = models.SparseVector(indices=sparse_indices, values=sparse_values)
        
        # Qdrant Query API for Hybrid Search (combining multiple prefetch vectors)
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            prefetch=[
                models.Prefetch(
                    query=dense_vector,
                    using="dense",
                    limit=top_k,
                    filter=qdrant_filter
                ),
                models.Prefetch(
                    query=models.SparseVector(indices=sparse_indices, values=sparse_values),
                    using="sparse",
                    limit=top_k,
                    filter=qdrant_filter
                )
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=top_k
        )
        
        return self._map_results(search_result.points)

    def _map_results(self, search_result) -> List[ReferenceDocument]:
        documents = []
        for hit in search_result:
            payload = hit.payload or {}
            doc = ReferenceDocument(
                id=str(hit.id),
                content=payload.get("content", ""),
                source=payload.get("source", "Unknown"),
                metadata=payload,
                score=hit.score
            )
            documents.append(doc)
        return documents
