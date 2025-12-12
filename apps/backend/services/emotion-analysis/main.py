"""
Emotion Analysis Service
Main FastAPI application wrapping emotion detector
"""

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
import numpy as np
import io
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel
import sys
import os

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

try:
    from src.emotion_detector import EmotionDetector
    from src.audio_processor import AudioProcessor
except ImportError:
    # Fallback if src modules not available
    EmotionDetector = None
    AudioProcessor = None

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

security = HTTPBearer()

class EmotionAnalysisRequest(BaseModel):
    audio_data: Dict[str, Any]  # Base64 encoded or file reference
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class EmotionAnalysisResponse(BaseModel):
    emotion: str
    confidence: float
    probabilities: Dict[str, float]
    timestamp: datetime
    features_used: list = []

# Initialize services
emotion_detector = None
audio_processor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global emotion_detector, audio_processor
    logger.info("Starting Emotion Analysis Service...")
    
    if EmotionDetector:
        emotion_detector = EmotionDetector()
        await emotion_detector.load_models()
    
    if AudioProcessor:
        audio_processor = AudioProcessor()
    
    logger.info("Emotion Analysis Service started successfully")
    yield
    logger.info("Shutting down Emotion Analysis Service...")

app = FastAPI(title="Emotion Analysis Service", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "emotion-analysis",
        "model_loaded": emotion_detector is not None
    }

@app.post("/analyze", response_model=EmotionAnalysisResponse)
async def analyze_emotion(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Analyze emotion from audio file"""
    try:
        if not emotion_detector:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Emotion detector not available"
            )
        
        # Read audio file
        audio_bytes = await file.read()
        
        # TODO: Process audio bytes to numpy array
        # For now, return mock response
        return EmotionAnalysisResponse(
            emotion="neutral",
            confidence=0.5,
            probabilities={"neutral": 1.0},
            timestamp=datetime.utcnow(),
            features_used=[]
        )
        
    except Exception as e:
        logger.error(f"Error analyzing emotion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Emotion analysis failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.SERVICE_PORT)

