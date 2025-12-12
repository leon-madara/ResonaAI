"""
Configuration settings for Encryption Service
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Encryption Service settings"""
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # Encryption Settings
    MASTER_KEY_FILE: str = "/app/keys/master.key"
    KEY_ROTATION_INTERVAL: int = 90  # days
    ENCRYPTION_ALGORITHM: str = "AES-256"
    
    # Security
    ADMIN_TOKEN: str = os.getenv("ADMIN_TOKEN", "admin-token-here")
    KEY_BACKUP_LOCATION: str = "/app/keys/backup/"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/encryption-service.log"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
