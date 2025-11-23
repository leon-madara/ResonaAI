"""
Configuration settings for Speech Processing Service
"""

import os
from typing import List
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Speech Processing Service settings"""
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # Audio Processing Settings
    SAMPLE_RATE: int = 16000
    CHUNK_SIZE: int = 1024
    CHANNELS: int = 1
    AUDIO_FORMAT: str = "wav"
    
    # STT Provider Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    AZURE_SPEECH_KEY: str = os.getenv("AZURE_SPEECH_KEY", "")
    AZURE_SPEECH_REGION: str = os.getenv("AZURE_SPEECH_REGION", "eastus")
    
    # Language Settings
    DEFAULT_LANGUAGE: str = "en"
    DEFAULT_ACCENT: str = "kenyan"
    SUPPORTED_LANGUAGES: List[str] = ["en", "sw"]
    SUPPORTED_ACCENTS: List[str] = ["kenyan", "ugandan", "tanzanian"]
    
    # Processing Settings
    NOISE_REDUCTION: bool = True
    NORMALIZATION: bool = True
    VAD_ENABLED: bool = True  # Voice Activity Detection
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".wav", ".mp3", ".flac", ".m4a", ".ogg"]
    MAX_DURATION: int = 30 * 60  # 30 minutes
    
    # Quality Settings
    MIN_CONFIDENCE: float = 0.3
    HIGH_CONFIDENCE: float = 0.8
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/speech-processing.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
