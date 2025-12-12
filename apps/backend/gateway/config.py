"""
Configuration settings for API Gateway Service
"""

import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """API Gateway settings"""
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # Security
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://mentalhealth.ke",
        "https://www.mentalhealth.ke"
    ]
    
    # Trusted Hosts
    ALLOWED_HOSTS: List[str] = [
        "localhost",
        "127.0.0.1",
        "mentalhealth.ke",
        "www.mentalhealth.ke"
    ]
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@postgres:5432/mental_health"
    )
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Service URLs
    SPEECH_PROCESSING_URL: str = "http://speech-processing:8000"
    EMOTION_ANALYSIS_URL: str = "http://emotion-analysis:8000"
    CONVERSATION_ENGINE_URL: str = "http://conversation-engine:8000"
    CRISIS_DETECTION_URL: str = "http://crisis-detection:8000"
    SAFETY_MODERATION_URL: str = "http://safety-moderation:8000"
    SYNC_SERVICE_URL: str = "http://sync-service:8000"
    CULTURAL_CONTEXT_URL: str = "http://cultural-context:8000"
    
    # Timeouts
    SERVICE_TIMEOUT: int = 30
    HEALTH_CHECK_TIMEOUT: int = 5
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
