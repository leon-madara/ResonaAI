"""
Configuration settings for PII Anonymization Service
"""

import os
from typing import List, Dict
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """PII Anonymization Service settings"""
    
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
    
    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


# PII detection patterns from security-policies.yaml
PII_PATTERNS = {
    "email": {
        "pattern": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "description": "Email addresses"
    },
    "phone": {
        "pattern": r"\+?[1-9]\d{1,14}",
        "description": "Phone numbers (international format)"
    },
    "phone_local": {
        "pattern": r"\b0[7][0-9]{8}\b",
        "description": "Local phone numbers (Kenya/Uganda format)"
    },
    "ssn": {
        "pattern": r"\d{3}-\d{2}-\d{4}",
        "description": "Social Security Numbers (US format)"
    },
    "national_id_ke": {
        "pattern": r"\b\d{8}\b",
        "description": "Kenya National ID numbers"
    },
    "credit_card": {
        "pattern": r"\b(?:\d{4}[- ]?){3}\d{4}\b",
        "description": "Credit card numbers"
    },
    "ip_address": {
        "pattern": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        "description": "IPv4 addresses"
    },
    "date_of_birth": {
        "pattern": r"\b(?:0?[1-9]|[12][0-9]|3[01])[/-](?:0?[1-9]|1[0-2])[/-](?:19|20)\d{2}\b",
        "description": "Dates of birth"
    },
    "name_pattern": {
        "pattern": r"\b(?:Mr\.|Mrs\.|Ms\.|Dr\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b",
        "description": "Names with titles"
    }
}

# Anonymization methods
ANONYMIZATION_METHODS = ["tokenization", "hashing", "masking"]

settings = Settings()

