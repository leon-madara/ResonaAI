"""
Configuration settings for Dissonance Detector Service
"""

import os
from typing import Dict
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Dissonance Detector settings"""
    
    # Service
    SERVICE_NAME: str = "dissonance-detector"
    SERVICE_PORT: int = 8000
    DEBUG: bool = False
    
    # Sentiment Analysis
    SENTIMENT_MODEL: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    SENTIMENT_CACHE_SIZE: int = 1000
    
    # Dissonance Calculation
    DISSONANCE_THRESHOLDS: Dict[str, float] = {
        "low": 0.3,
        "medium": 0.5,
        "high": 0.7
    }
    
    # Emotion Mapping
    EMOTION_VALENCE_MAP: Dict[str, float] = {
        "happy": 0.8,
        "neutral": 0.0,
        "sad": -0.7,
        "angry": -0.6,
        "fear": -0.8,
        "surprise": 0.3,
        "disgust": -0.5,
        "anxious": -0.7,
        "calm": 0.5
    }
    
    # Risk Mapping
    RISK_MAPPING: Dict[str, str] = {
        "low": "low",
        "medium": "medium",
        "high": "medium-high",
        "critical": "high"
    }
    
    # Dependencies
    EMOTION_SERVICE_URL: str = os.getenv("EMOTION_SERVICE_URL", "http://emotion-analysis:8000")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@postgres:5432/mental_health"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()

