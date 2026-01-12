"""
Configuration settings for Cultural Context Service
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Cultural Context settings"""
    
    # Service
    SERVICE_NAME: str = "cultural-context"
    SERVICE_PORT: int = 8000
    DEBUG: bool = False
    
    # Vector Database - Pinecone
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "")  # Deprecated in v5+, kept for backward compatibility
    PINECONE_INDEX_NAME: str = "cultural-context"
    
    # Vector Database - Weaviate
    WEAVIATE_URL: str = os.getenv("WEAVIATE_URL", "")
    WEAVIATE_API_KEY: str = os.getenv("WEAVIATE_API_KEY", "")
    
    # Knowledge Base Indexing
    AUTO_INDEX_KB: bool = os.getenv("AUTO_INDEX_KB", "true").lower() == "true"
    KB_INDEX_BATCH_SIZE: int = int(os.getenv("KB_INDEX_BATCH_SIZE", "100"))
    USE_RAG: bool = os.getenv("USE_RAG", "true").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@postgres:5432/mental_health"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()

