"""
Configuration settings for Safety Moderation Service
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Safety Moderation settings

    Purpose:
    - Provide JWT verification settings so this service can attribute actions to a user
      using verified JWT claims (auditability).
    """

    SERVICE_NAME: str = "safety-moderation"
    SERVICE_PORT: int = 8000
    DEBUG: bool = False

    # Security
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()

