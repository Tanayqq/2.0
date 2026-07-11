import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Dict

class IngestionSettings(BaseSettings):
    # Ingestion Directories
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    RAW_DATA_DIR: str = os.path.join(BASE_DIR, "data", "raw")
    DLQ_DIR: str = os.path.join(BASE_DIR, "data", "dlq")
    
    # Target Clinical Sections to Extract
    TARGET_SECTIONS: List[str] = [
        "Indications",
        "Dosage",
        "Contraindications",
        "Warnings",
        "Precautions",
        "Drug Interactions",
        "Pregnancy",
        "Lactation",
        "Pediatric Use",
        "Geriatric Use",
        "Adverse Reactions",
        "Overdosage",
        "Storage",
        "Patient Counseling Information"
    ]
    
    # Source Configuration
    ACTIVE_SOURCES: List[str] = ["dailymed", "openfda"]
    # Source priority for conflict resolution (first has highest priority)
    SOURCE_PRIORITY: List[str] = ["dailymed", "openfda"]
    
    # Active Embedding Provider Configuration
    ACTIVE_EMBEDDING_PROVIDER: str = "fastembed"  # Options: fastembed, medcpt, bge
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # Qdrant Database Configuration
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION: str = "openfda_labels"
    
    # Chunker Configuration
    MIN_CHUNK_TOKENS: int = 30
    MAX_CHUNK_TOKENS: int = 450
    TARGET_CHUNK_TOKENS: int = 350
    OVERLAP: int = 50
    
    # Retry & DLQ Policies
    MAX_RETRIES: int = 3
    BACKOFF_FACTOR: float = 2.0  # Exponential factor
    
    # Versioning
    PIPELINE_VERSION: str = "1.6.0"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

ingestion_config = IngestionSettings()

# Ensure directories exist
os.makedirs(ingestion_config.RAW_DATA_DIR, exist_ok=True)
os.makedirs(ingestion_config.DLQ_DIR, exist_ok=True)
