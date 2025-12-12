"""
Configuration settings for ResonaAI Voice Emotion Detection Pipeline
"""

import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # Audio Processing Settings
    SAMPLE_RATE: int = 16000
    CHUNK_SIZE: int = 1024
    CHANNELS: int = 1
    AUDIO_FORMAT: str = "wav"
    
    # Model Settings
    MODEL_NAME: str = "facebook/wav2vec2-base-960h"
    EMOTION_MODEL_PATH: str = "models/emotion_classifier.pkl"
    FEATURE_EXTRACTOR: str = "wav2vec2"
    
    # Emotion Categories
    EMOTION_LABELS: List[str] = [
        "neutral", "happy", "sad", "angry", "fear", "surprise", "disgust"
    ]
    
    # Feature Extraction Settings
    MFCC_FEATURES: int = 13
    SPECTRAL_FEATURES: bool = True
    PROSODIC_FEATURES: bool = True
    
    # Processing Settings
    NOISE_REDUCTION: bool = True
    NORMALIZATION: bool = True
    VAD_ENABLED: bool = True  # Voice Activity Detection
    
    # Confidence Thresholds
    MIN_CONFIDENCE: float = 0.3
    HIGH_CONFIDENCE: float = 0.8
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".wav", ".mp3", ".flac", ".m4a"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
