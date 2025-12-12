"""
Configuration settings for Crisis Detection Service
"""

import os
from typing import Dict
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Crisis Detection settings"""
    
    # Service
    SERVICE_NAME: str = "crisis-detection"
    SERVICE_PORT: int = 8000
    DEBUG: bool = False
    
    # Risk Thresholds
    RISK_THRESHOLDS: Dict[str, float] = {
        "low": 0.3,
        "medium": 0.5,
        "high": 0.7,
        "critical": 0.9
    }
    
    # Crisis Keywords
    CRISIS_KEYWORDS: list = [
        "suicide", "kill myself", "end it all", "not worth living",
        "want to die", "better off dead", "self harm", "cut myself"
    ]
    
    # Twilio (for emergency alerts)
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@postgres:5432/mental_health"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()

