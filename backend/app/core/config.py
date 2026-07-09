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
    
    # Network Configuration
    FRONTEND_URL: str = "http://localhost:5173"
    APP_VERSION: str = "1.0.0"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
