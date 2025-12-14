"""
Configuration settings for Conversation Engine Service
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Conversation Engine settings"""
    
    # Service
    SERVICE_NAME: str = "conversation-engine"
    SERVICE_PORT: int = 8000
    DEBUG: bool = False
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-4"
    MAX_TOKENS: int = 500
    TEMPERATURE: float = 0.7
    
    # Vector Database
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "")
    PINECONE_INDEX_NAME: str = "cultural-context"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@postgres:5432/mental_health"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379")

    # Encryption service (for encrypting message content at rest)
    ENCRYPTION_SERVICE_URL: str = os.getenv("ENCRYPTION_SERVICE_URL", "http://encryption-service:8000")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()

