import uuid
import time
import structlog
from typing import List, Dict, Any, Tuple
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from .config import ingestion_config

logger = structlog.get_logger()

class MedicalUploader:
    """
    Manages connection to Qdrant Cloud and handles idempotent batch uploads.
    Includes pre-flight embedding dimension validation.
    """
    def __init__(self):
        self.url = ingestion_config.QDRANT_URL
        self.api_key = ingestion_config.QDRANT_API_KEY
        self.collection_name = ingestion_config.QDRANT_COLLECTION
        
        logger.info("connecting_to_qdrant_cloud", url=self.url)
        if self.api_key:
            self.client = QdrantClient(url=self.url, api_key=self.api_key, timeout=120.0)
        else:
            self.client = QdrantClient(url=self.url, timeout=120.0)

    def validate_dimension(self, expected_dim: int) -> bool:
        """
        Validate that the active embedder's output dimension matches the Qdrant collection's dense vector dimension.
        """
        try:
            collections = [c.name for c in self.client.get_collections().collections]
            
            if self.collection_name not in collections:
                # If collection doesn't exist, we will create it with the correct dimension
                logger.info("qdrant_collection_does_not_exist_will_create", collection=self.collection_name, dim=expected_dim)
                return True
                
            collection_info = self.client.get_collection(self.collection_name)
            vector_params = collection_info.config.params.vectors
            
            # Retrieve size from Qdrant collection
            actual_dim = 0
            if isinstance(vector_params, dict):
                dense_val = vector_params.get("dense")
                if dense_val:
                    if isinstance(dense_val, dict):
                        actual_dim = dense_val.get("size", 0)
                    else:
                        actual_dim = getattr(dense_val, "size", 0)
                else:
                    actual_dim = vector_params.get("size", 0)
            else:
                # If it's a Models.VectorsConfig object
                dense_val = getattr(vector_params, "dense", None)
                if dense_val:
                    actual_dim = getattr(dense_val, "size", 0)
                else:
                    actual_dim = getattr(vector_params, "size", 0)
                        
            if actual_dim == 0:
                # Fallback to scroll to inspect a point or ignore if we can't parse Qdrant's internal config object
                logger.warning("could_not_parse_qdrant_dimension_skipping_check")
                return True
                
            if actual_dim != expected_dim:
                logger.error("embedding_dimension_mismatch", expected=expected_dim, actual=actual_dim, collection=self.collection_name)
                return False
                
            logger.info("embedding_dimension_validated", dimension=actual_dim)
            return True
            
        except Exception as e:
            logger.error("failed_dimension_validation", error=str(e))
            # Treat as non-blocking but warn
            return True

    def create_collection_if_not_exists(self, dimension: int):
        """
        Create the collection with named dense vectors if it doesn't already exist.
        """
        try:
            collections = [c.name for c in self.client.get_collections().collections]
            if self.collection_name not in collections:
                logger.info("creating_new_qdrant_collection", name=self.collection_name, dim=dimension)
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config={
                        "dense": VectorParams(size=dimension, distance=Distance.COSINE)
                    }
                )
                # Create payload keyword indexes to support strict metadata filters
                from qdrant_client.models import PayloadSchemaType
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="drug_name",
                    field_schema=PayloadSchemaType.KEYWORD
                )
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="generic_name",
                    field_schema=PayloadSchemaType.KEYWORD
                )
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="canonical_section",
                    field_schema=PayloadSchemaType.KEYWORD
                )
                logger.info("qdrant_collection_created_successfully", name=self.collection_name)
        except Exception as e:
            logger.error("failed_creating_collection", collection=self.collection_name, error=str(e))
            raise e

    def get_existing_chunk_hashes(self, drug_name: str) -> Dict[str, str]:
        """
        Fetch all existing chunk_hashes for a given drug.
        Returns: Dict[point_id, chunk_hash]
        """
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        hashes = {}
        offset = None
        while True:
            results, offset = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="drug_name",
                            match=MatchValue(value=drug_name)
                        )
                    ]
                ),
                with_payload=["chunk_hash"],
                with_vectors=False,
                limit=100,
                offset=offset
            )
            for p in results:
                if p.payload and "chunk_hash" in p.payload:
                    hashes[p.id] = p.payload["chunk_hash"]
            if offset is None:
                break
        return hashes

    def delete_points_by_id(self, point_ids: List[str]):
        """
        Delete specific points by their UUIDs.
        """
        if not point_ids:
            return
        from qdrant_client.models import PointIdsList
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=PointIdsList(points=point_ids)
        )

    def upload_chunks(self, chunks: List[Dict[str, Any]], batch_size: int = 25) -> Tuple[int, int]:
        """
        Upload embedded chunks to Qdrant Cloud.
        Returns:
            Tuple of (upsert_success_count: int, upsert_failure_count: int)
        """
        if not chunks:
            return 0, 0
            
        success_count = 0
        failure_count = 0
        
        logger.info("starting_qdrant_batch_upload", total_chunks=len(chunks), batch_size=batch_size)
        
        required_keys = ["drug_name", "generic_name", "section", "source", "document_id", "chunk_index", "total_chunks", "label_version", "ingested_at"]
        points = []
        for chunk in chunks:
            # Metadata Integrity Check
            is_valid = True
            for rk in required_keys:
                if rk not in chunk or chunk[rk] is None or (isinstance(chunk[rk], str) and not chunk[rk].strip()):
                    logger.error("metadata_integrity_validation_failed", missing_key=rk, chunk_id=chunk.get("content", "")[:30])
                    is_valid = False
                    break
                    
            if not is_valid:
                failure_count += 1
                continue
                
            drug = chunk["drug_name"]
            section = chunk["section"]
            chunk_idx = chunk["chunk_index"]
            
            # Generate stable deterministic UUID for idempotency (independent of version)
            unique_string = f"{drug.lower()}_{section.lower()}_{chunk_idx}"
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_string))
            
            # Keep original UUID reference in payload using canonical keys
            payload = {
                "content": chunk["content"],
                "source": chunk["source"],
                "category": "drug_label",
                "drug_name": chunk["drug_name"],
                "drug": chunk["drug_name"],  # Maintain backward compatibility
                "generic_name": chunk["generic_name"],
                "section": chunk["section"],
                "canonical_section": chunk.get("canonical_section", chunk["section"]),
                
                # Traceability & Versioning
                "source_url": chunk.get("source_url"),
                "authority": chunk.get("authority"),
                "authority_version": chunk.get("authority_version"),
                "drug_revision": chunk.get("drug_revision"),
                "retrieved_on": chunk.get("retrieved_on"),
                "document_id": chunk["document_id"],
                "effective_date": chunk.get("effective_date"),
                "revision": chunk.get("revision"),
                "label_version": chunk.get("label_version"),
                "version": chunk.get("label_version"), # Backward compatibility
                
                # Ingestion metadata
                "chunk_index": chunk["chunk_index"],
                "total_chunks": chunk["total_chunks"],
                "token_count": chunk["token_count"],
                "embedding_model": chunk["embedding_model"],
                "ingested_at": chunk["ingested_at"],
                "last_updated": chunk["ingested_at"],
                "pipeline_version": chunk.get("pipeline_version"),
                "corpus_version": chunk.get("corpus_version"),
                "parser_version": chunk.get("parser_version"),
                "embedded_at": chunk.get("embedded_at"),
                "chunk_hash": chunk.get("chunk_hash"),
                "paragraph_index": chunk.get("paragraph_index"),
                "xml_section": chunk.get("xml_section"),
                
                # Clinical metadata
                "clinical_category": chunk.get("clinical_category"),
                "patient_population": chunk.get("patient_population"),
                "document_type": chunk.get("document_type", "drug_label"),
                "structured_dosing": chunk.get("structured_dosing"),
                "chunk_id": point_id,  # New schema key
                "chunk_text": chunk["content"]  # New schema key
            }
            
            # Construct Qdrant point structure
            points.append(PointStruct(
                id=point_id,
                vector={"dense": chunk["embedding"]},
                payload=payload
            ))
            
        # Batch upsert with retry logic
        for i in range(0, len(points), batch_size):
            batch_points = points[i:i + batch_size]
            
            retries = 0
            success = False
            
            while retries <= ingestion_config.MAX_RETRIES and not success:
                try:
                    self.client.upsert(
                        collection_name=self.collection_name,
                        points=batch_points
                    )
                    success = True
                    success_count += len(batch_points)
                except Exception as e:
                    logger.warning("qdrant_batch_upsert_failed", error=str(e), retry=retries)
                    if retries == ingestion_config.MAX_RETRIES:
                        logger.error("qdrant_batch_upsert_failed_permanently", error=str(e))
                        failure_count += len(batch_points)
                    else:
                        time.sleep(ingestion_config.BACKOFF_FACTOR ** retries)
                        retries += 1
                        
        logger.info("qdrant_upload_completed", success=success_count, failures=failure_count)
        return success_count, failure_count
