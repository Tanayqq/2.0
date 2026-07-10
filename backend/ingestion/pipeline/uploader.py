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
                logger.info("qdrant_collection_created_successfully", name=self.collection_name)
        except Exception as e:
            logger.error("failed_creating_collection", collection=self.collection_name, error=str(e))
            raise e

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
        
        points = []
        for chunk in chunks:
            drug = chunk["drug"]
            section = chunk["section"]
            chunk_idx = chunk["chunk_index"]
            version = chunk["version"]
            
            # Generate stable deterministic UUID for idempotency
            unique_string = f"{drug.lower()}_{section.lower()}_{chunk_idx}_{version}"
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_string))
            
            # Keep original UUID reference in payload
            payload = {
                "content": chunk["content"],
                "source": chunk["source"],
                "category": "drug_label",
                "drug": chunk["drug"],
                "generic_name": chunk["generic_name"],
                "section": chunk["section"],
                "country": chunk["country"],
                "version": chunk["version"],
                "effective_date": chunk.get("effective_date"),
                "revision": chunk.get("revision"),
                "token_count": chunk["token_count"],
                "embedding_model": chunk["embedding_model"],
                "ingested_at": chunk["ingested_at"]
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
