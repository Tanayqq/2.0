from functools import lru_cache
from app.core.config import settings
from app.infrastructure.llm_providers import GroqProvider, MedGemmaProvider
from app.infrastructure.embedding_models import FastEmbedModel, NoOpCrossEncoder
from app.infrastructure.vector_db import QdrantAdapter
from app.domain.interfaces import LLMProviderProtocol, VectorDatabaseProtocol, EmbeddingModelProtocol, CrossEncoderProtocol

@lru_cache()
def get_llm_provider() -> LLMProviderProtocol:
    """Dependency injection for LLM Provider based on config."""
    if settings.ACTIVE_LLM_PROVIDER == "groq":
        return GroqProvider(api_key=settings.GROQ_API_KEY)
    elif settings.ACTIVE_LLM_PROVIDER == "medgemma":
        return MedGemmaProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {settings.ACTIVE_LLM_PROVIDER}")

@lru_cache()
def get_embedding_model() -> EmbeddingModelProtocol:
    return FastEmbedModel(model_name=settings.EMBEDDING_MODEL_NAME)

@lru_cache()
def get_vector_db() -> VectorDatabaseProtocol:
    return QdrantAdapter(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)

@lru_cache()
def get_cross_encoder() -> CrossEncoderProtocol:
    return NoOpCrossEncoder()

