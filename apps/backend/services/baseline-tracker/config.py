"""
Configuration settings for Baseline Tracker Service
"""

import os
from typing import Dict
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Baseline Tracker settings"""
    
    # Service
    SERVICE_NAME: str = "baseline-tracker"
    SERVICE_PORT: int = 8000
    DEBUG: bool = False
    
    # Baseline Calculation
    MIN_SAMPLES_FOR_BASELINE: int = 10
    BASELINE_WINDOW_DAYS: int = 30
    DEVIATION_THRESHOLD: float = 0.3
    
    # Voice Fingerprint
    FINGERPRINT_FEATURES: list = [
        "pitch_mean",
        "pitch_std",
        "energy_mean",
        "energy_std",
        "speech_rate",
        "pause_frequency"
    ]
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@postgres:5432/mental_health"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()

