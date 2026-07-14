from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "MedRef API"
    DEBUG: bool = True
    
    # LLM Provider Configuration
    ACTIVE_LLM_PROVIDER: str = "groq" # Options: groq, medgemma (future)
    
    # API Keys
    GROQ_API_KEY: str = ""
    
    # Qdrant Configuration
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    
    # Embedding Configuration
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Retrieval Configuration
    DEFAULT_TOP_K: int = 5
    MULTI_SECTION_TOP_K: int = 40
    MAX_CONTEXT_CHUNKS: int = 5
    SIMILARITY_THRESHOLD: float = 0.50
    
    # Citation Configuration
    STRICT_CITATION_VALIDATION_ACTION: str = "remove" # Options: reject, remove, none
    
    # Network Configuration
    CORS_ORIGINS: str = "http://localhost:5173,https://medref-pearl.vercel.app,https://medref.vercel.app,https://*.vercel.app"
    APP_VERSION: str = "1.0.0"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
