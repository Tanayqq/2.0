import time
import datetime
import structlog
from typing import List, Dict, Any, Optional
from .interfaces.embedding_provider import EmbeddingProvider
from .providers.embeddings.fastembed_provider import FastEmbedProvider
from .providers.embeddings.medcpt_provider import MedCPTProvider
from .providers.embeddings.bge_provider import BGEProvider
from .config import ingestion_config

logger = structlog.get_logger()

class MedicalEmbedder:
    """
    Coordinator class to generate vector embeddings for chunks in batches.
    Decoupled from specific models via the EmbeddingProvider interface.
    """
    def __init__(self, provider: Optional[EmbeddingProvider] = None):
        if provider:
            self.provider = provider
        else:
            self.provider = self._resolve_provider()

    def _resolve_provider(self) -> EmbeddingProvider:
        prov_type = ingestion_config.ACTIVE_EMBEDDING_PROVIDER.lower()
        model_name = ingestion_config.EMBEDDING_MODEL_NAME
        
        if prov_type == "fastembed":
            return FastEmbedProvider(model_name=model_name)
        elif prov_type == "medcpt":
            return MedCPTProvider(model_name=model_name)
        elif prov_type == "bge":
            return BGEProvider()
        else:
            logger.warning("unknown_embedding_provider_falling_back_to_fastembed", provider=prov_type)
            return FastEmbedProvider()

    def get_dimension(self) -> int:
        return self.provider.get_dimension()

    def embed_chunks(self, chunks: List[Dict[str, Any]], batch_size: int = 32) -> List[Dict[str, Any]]:
        """
        Takes a list of chunk dictionaries, extracts contents, generates embeddings in batches,
        and adds the "embedding" key to each chunk.
        """
        if not chunks:
            return []
            
        logger.info("generating_embeddings_for_chunks", total_chunks=len(chunks), batch_size=batch_size)
        start_time = time.time()
        
        contents = [chunk["content"] for chunk in chunks]
        embeddings = []
        
        # Batch processing
        for i in range(0, len(contents), batch_size):
            batch_contents = contents[i:i + batch_size]
            
            # Simple retry loop for API reliability or external service call logic
            retries = 0
            success = False
            batch_embeddings = []
            
            while retries <= ingestion_config.MAX_RETRIES and not success:
                try:
                    batch_embeddings = self.provider.embed_texts(batch_contents)
                    success = True
                except Exception as e:
                    logger.warning("embedding_batch_failed", error=str(e), retry=retries)
                    if retries == ingestion_config.MAX_RETRIES:
                        logger.error("embedding_failed_permanently", error=str(e))
                        raise e
                    time.sleep(ingestion_config.BACKOFF_FACTOR ** retries)
                    retries += 1
            
            embeddings.extend(batch_embeddings)
            
        # Attach vectors and versioning stamps back to the chunk dictionaries
        embedded_at = datetime.datetime.utcnow().isoformat() + "Z"
        for chunk, vector in zip(chunks, embeddings):
            chunk["embedding"] = vector
            chunk["embedding_model"] = ingestion_config.EMBEDDING_MODEL_NAME
            chunk["embedded_at"] = embedded_at   # Refinement #5: exact embedding timestamp
            
        duration = time.time() - start_time
        logger.info("embeddings_generated_successfully", duration_sec=round(duration, 4), count=len(chunks))
        
        return chunks
