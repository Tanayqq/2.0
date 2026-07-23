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
    VECTOR_DB_MODE: str = "server" # Options: local, server
    QDRANT_PATH: str = "./qdrant_data"
    QDRANT_URL: str = "https://b92d5ef7-a1fe-429b-86e0-67cb239dd428.us-west-1-0.aws.cloud.qdrant.io"
    QDRANT_API_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6MmI0NTYzY2YtNTQyOC00NDdiLWE2ZDUtYjY2YmFkNjBiYTM0In0.BODxwJ_pzKQprCOosZZcLRtrQ510diLNfOSVAtyu62U"
    
    # Embedding Configuration
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Retrieval Configuration
    DEFAULT_TOP_K: int = 5
    MULTI_SECTION_TOP_K: int = 40
    MAX_CONTEXT_CHUNKS: int = 5
    SIMILARITY_THRESHOLD: float = 0.35
    
    # Citation Configuration
    STRICT_CITATION_VALIDATION_ACTION: str = "remove" # Options: reject, remove, none
    
    # Network Configuration
    CORS_ORIGINS: str = "http://localhost:5173,https://medref-pearl.vercel.app,https://medref.vercel.app,https://*.vercel.app"
    APP_VERSION: str = "1.0.0"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
