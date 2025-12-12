"""
Configuration settings for Emotion Analysis Service
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Emotion Analysis settings"""
    
    # Service
    SERVICE_NAME: str = "emotion-analysis"
    SERVICE_PORT: int = 8000
    DEBUG: bool = False
    
    # External APIs
    HUME_API_KEY: str = os.getenv("HUME_API_KEY", "")
    AZURE_TEXT_ANALYTICS_KEY: str = os.getenv("AZURE_TEXT_ANALYTICS_KEY", "")
    AZURE_TEXT_ANALYTICS_ENDPOINT: str = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT", "")
    
    # Model
    MODEL_NAME: str = "facebook/wav2vec2-base"
    EMOTION_LABELS: list = ["happy", "sad", "angry", "fear", "surprise", "disgust", "neutral", "anxious", "calm"]
    MIN_CONFIDENCE: float = 0.5
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@postgres:5432/mental_health"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()

