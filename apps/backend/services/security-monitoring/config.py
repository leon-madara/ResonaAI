"""
Configuration settings for Security Monitoring Service
"""

import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Security Monitoring Service settings"""
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # Security
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
    JWT_ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@postgres:5432/mental_health"
    )
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    
    # Alert thresholds (from security-policies.yaml)
    FAILED_LOGIN_THRESHOLD: int = 5
    FAILED_LOGIN_WINDOW: int = 300  # 5 minutes
    
    DATA_BREACH_THRESHOLD: int = 1
    DATA_BREACH_WINDOW: int = 60  # 1 minute
    
    UNUSUAL_ACCESS_THRESHOLD: int = 10
    UNUSUAL_ACCESS_WINDOW: int = 3600  # 1 hour
    
    # Alert contacts (from security-policies.yaml)
    SECURITY_TEAM_EMAIL: str = os.getenv("SECURITY_TEAM_EMAIL", "security@mentalhealth.ke")
    LEGAL_TEAM_EMAIL: str = os.getenv("LEGAL_TEAM_EMAIL", "legal@mentalhealth.ke")
    MANAGEMENT_EMAIL: str = os.getenv("MANAGEMENT_EMAIL", "management@mentalhealth.ke")
    
    # SMTP settings
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "alerts@mentalhealth.ke")
    
    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()

