"""
Data models for ResonaAI Voice Emotion Detection Pipeline
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class EmotionResult(BaseModel):
    """Result of emotion detection"""
    emotion: str = Field(..., description="Detected emotion")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    # Tests (and some call sites) may pass `None` for timestamp; allow it and default to now.
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="Detection timestamp")
    features: Dict[str, Any] = Field(default_factory=dict, description="Extracted features")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")

class BatchEmotionResult(BaseModel):
    """Result of batch emotion detection"""
    total_files: int = Field(..., description="Total number of files processed")
    successful_analyses: int = Field(..., description="Number of successful analyses")
    results: List[Dict[str, Any]] = Field(..., description="Individual file results")
    processing_time: Optional[float] = Field(None, description="Total processing time")

class HealthStatus(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    message: str = Field(..., description="Status message")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.now)

class AudioFeatures(BaseModel):
    """Extracted audio features"""
    mfcc: List[List[float]] = Field(..., description="MFCC features")
    spectral_features: Dict[str, float] = Field(..., description="Spectral features")
    prosodic_features: Dict[str, float] = Field(..., description="Prosodic features")
    wav2vec2_features: Optional[List[float]] = Field(None, description="Wav2Vec2 embeddings")

class EmotionPrediction(BaseModel):
    """Emotion prediction with probabilities"""
    emotion: str = Field(..., description="Predicted emotion")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    probabilities: Dict[str, float] = Field(..., description="Probability for each emotion")
    features_used: List[str] = Field(..., description="Features used for prediction")

class StreamingConfig(BaseModel):
    """Configuration for streaming processing"""
    sample_rate: int = Field(default=16000, description="Audio sample rate")
    chunk_size: int = Field(default=1024, description="Audio chunk size")
    overlap: int = Field(default=256, description="Chunk overlap")
    buffer_size: int = Field(default=4096, description="Buffer size")
    vad_threshold: float = Field(default=0.5, description="Voice activity detection threshold")

class ModelInfo(BaseModel):
    """Information about loaded models"""
    model_name: str = Field(..., description="Model name")
    model_type: str = Field(..., description="Model type")
    version: str = Field(..., description="Model version")
    accuracy: Optional[float] = Field(None, description="Model accuracy")
    supported_emotions: List[str] = Field(..., description="Supported emotion labels")
    feature_types: List[str] = Field(..., description="Supported feature types")
