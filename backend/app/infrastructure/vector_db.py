from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny, Prefetch, models
from typing import List, Dict, Any, Optional
from app.domain.interfaces import VectorDatabaseProtocol
from app.domain.models import ReferenceDocument

class QdrantAdapter(VectorDatabaseProtocol):
    """
    Adapter for Qdrant vector database supporting Hybrid Search and Metadata Filtering.
    """
    def __init__(
        self, 
        client: Optional[QdrantClient] = None,
        mode: str = "local",
        path: str = "./qdrant_data",
        url: str = "http://localhost:6333", 
        api_key: str = "", 
        collection_name: str = "openfda_labels"
    ):
        if client:
            self.client = client
        elif mode == "local":
            self.client = QdrantClient(path=path)
        else:
            if api_key:
                self.client = QdrantClient(url=url, api_key=api_key, timeout=60.0)
            else:
                self.client = QdrantClient(url=url, timeout=60.0)
        
        self.collection_name = collection_name
        
        # Ensure payload indexes exist for metadata filtering (required by Qdrant Cloud)
        try:
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="drug_name",
                field_schema=models.PayloadSchemaType.KEYWORD
            )
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="canonical_section",
                field_schema=models.PayloadSchemaType.KEYWORD
            )
        except Exception:
            pass

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
        
        try:
            search_result = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                using="dense",
                limit=top_k,
                query_filter=qdrant_filter
            )
            return self._map_results(search_result.points)
        except Exception as e:
            if "Index required" in str(e) or "400" in str(e):
                try:
                    self.client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name="drug_name",
                        field_schema=models.PayloadSchemaType.KEYWORD
                    )
                    search_result = self.client.query_points(
                        collection_name=self.collection_name,
                        query=query_vector,
                        using="dense",
                        limit=top_k,
                        query_filter=qdrant_filter
                    )
                    return self._map_results(search_result.points)
                except Exception:
                    # Fallback to unfiltered search if index creation fails
                    search_result = self.client.query_points(
                        collection_name=self.collection_name,
                        query=query_vector,
                        using="dense",
                        limit=top_k
                    )
                    return self._map_results(search_result.points)
            raise e

    def hybrid_search(self, dense_vector: List[float], sparse_vector: Dict[int, float], top_k: int = 20, filters: Optional[Dict[str, Any]] = None) -> List[ReferenceDocument]:
        """
        Executes a true hybrid search using Qdrant's Reciprocal Rank Fusion (RRF) 
        combining semantic meaning (dense) and exact keyword matches (sparse).
        """
        qdrant_filter = self._build_filter(filters)
        
        # Build Qdrant sparse vector format
        sparse_indices = list(sparse_vector.keys())
        sparse_values = list(sparse_vector.values())
        
        def _execute(filter_obj):
            return self.client.query_points(
                collection_name=self.collection_name,
                prefetch=[
                    models.Prefetch(
                        query=dense_vector,
                        using="dense",
                        limit=top_k,
                        filter=filter_obj
                    ),
                    models.Prefetch(
                        query=models.SparseVector(indices=sparse_indices, values=sparse_values),
                        using="sparse",
                        limit=top_k,
                        filter=filter_obj
                    )
                ],
                query=models.FusionQuery(fusion=models.Fusion.RRF),
                limit=top_k
            )

        try:
            search_result = _execute(qdrant_filter)
            return self._map_results(search_result.points)
        except Exception as e:
            if "Index required" in str(e) or "400" in str(e):
                try:
                    self.client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name="drug_name",
                        field_schema=models.PayloadSchemaType.KEYWORD
                    )
                    search_result = _execute(qdrant_filter)
                    return self._map_results(search_result.points)
                except Exception:
                    search_result = _execute(None)
                    return self._map_results(search_result.points)
            raise e

    def scroll_by_drug_sections(self, drug_name: str, canonical_sections: List[str], limit_per_section: int = 3) -> List[ReferenceDocument]:
        """
        Direct metadata-filtered scroll — NO vector similarity needed.
        Guarantees retrieval of chunks for the given drug + section list.
        Used to force-populate required UI cards (Dosing, Interactions, Warnings, Overview).
        Returns a flat list of ReferenceDocuments with score=1.0 (exact match marker).
        Drug names are stored as Title Case in Qdrant (e.g. 'Albuterol'), so we normalize.
        """
        results = []
        # Drug names stored as Title Case in Qdrant
        drug_title = drug_name.strip().title()
        
        # Query in batches of sections to avoid Qdrant filter size limits
        batch_size = 10
        for i in range(0, len(canonical_sections), batch_size):
            section_batch = canonical_sections[i:i+batch_size]
            qdrant_filter = Filter(
                must=[
                    FieldCondition(key="drug_name", match=MatchValue(value=drug_title)),
                    FieldCondition(key="canonical_section", match=MatchAny(any=section_batch))
                ]
            )
            try:
                scroll_result, _ = self.client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=qdrant_filter,
                    limit=limit_per_section * len(section_batch),
                    with_payload=True,
                    with_vectors=False
                )
                for point in scroll_result:
                    payload = point.payload or {}
                    doc = ReferenceDocument(
                        id=str(point.id),
                        content=payload.get("content", payload.get("chunk_text", "")),
                        source=payload.get("source", "Unknown"),
                        metadata=payload,
                        score=1.0  # Exact match — no similarity scoring needed
                    )
                    results.append(doc)
            except Exception as e:
                if "Index required" in str(e) or "400" in str(e):
                    try:
                        self.client.create_payload_index(
                            collection_name=self.collection_name,
                            field_name="drug_name",
                            field_schema=models.PayloadSchemaType.KEYWORD
                        )
                        self.client.create_payload_index(
                            collection_name=self.collection_name,
                            field_name="canonical_section",
                            field_schema=models.PayloadSchemaType.KEYWORD
                        )
                        scroll_result, _ = self.client.scroll(
                            collection_name=self.collection_name,
                            scroll_filter=qdrant_filter,
                            limit=limit_per_section * len(section_batch),
                            with_payload=True,
                            with_vectors=False
                        )
                        for point in scroll_result:
                            payload = point.payload or {}
                            doc = ReferenceDocument(
                                id=str(point.id),
                                content=payload.get("content", payload.get("chunk_text", "")),
                                source=payload.get("source", "Unknown"),
                                metadata=payload,
                                score=1.0
                            )
                            results.append(doc)
                    except Exception:
                        pass
                else:
                    pass  # Silently skip if index not available for this batch
        return results

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

