"""
Emotion Analysis Service
Main FastAPI application wrapping emotion detector
"""

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import logging
import numpy as np
import io
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel
import sys
import os
import uuid
import time

# Ensure repo root is importable for shared `src.*` modules (monorepo layout).
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

try:
    from src.emotion_detector import EmotionDetector
    from src.audio_processor import AudioProcessor
except ImportError:
    # Fallback if src modules not available
    EmotionDetector = None
    AudioProcessor = None

from config import settings
from database import get_db
from repositories.emotion_repository import EmotionRepository

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
    use_hume: bool = False,
    user_id: Optional[str] = Query(None),
    conversation_id: Optional[str] = Query(None),
    message_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Analyze emotion from audio file"""
    try:
        # Read audio file
        audio_bytes = await file.read()
        emotion_result = None
        features_used = []
        
        # Try Hume AI first if requested and available
        if use_hume:
            try:
                from services.hume_integration import get_hume_integration
                hume = get_hume_integration()
                
                if hume.is_available():
                    result = hume.analyze_audio(audio_bytes, audio_format=file.filename.split('.')[-1] if file.filename else "wav")
                    emotion_result = {
                        "emotion": result["emotion"],
                        "confidence": result["confidence"],
                        "probabilities": result["probabilities"],
                        "features_used": ["hume_ai_prosody"]
                    }
                    features_used = ["hume_ai_prosody"]
            except Exception as e:
                logger.warning(f"Hume AI analysis failed, falling back: {e}")
        
        # Fallback to local emotion detector
        if not emotion_result and emotion_detector:
            if not audio_processor:
                raise RuntimeError("AudioProcessor not initialized")

            # Explicit audio feature extraction pipeline:
            # bytes -> waveform -> preprocessing (noise reduce/normalize/trim) -> feature extraction -> classification
            #
            # Local performance budget (dev guidance):
            # - Target: <200ms wall-clock for ~2s @ 16kHz on a typical dev laptop (excluding model download).
            t0 = time.perf_counter()
            processed_audio = audio_processor.preprocess_audio(audio_bytes)
            result = await emotion_detector.detect_emotion(processed_audio)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            logger.info(f"Local emotion pipeline time: {elapsed_ms:.1f}ms (bytes={len(audio_bytes)})")

            # Normalize result to dict for response construction
            if hasattr(result, "model_dump"):
                result_dict = result.model_dump()
            elif isinstance(result, dict):
                result_dict = result
            else:
                result_dict = {}

            emotion_result = {
                "emotion": result_dict.get("emotion", "neutral"),
                "confidence": result_dict.get("confidence", 0.5),
                "probabilities": result_dict.get("probabilities", {"neutral": 1.0}),
                # Prefer explicit feature keys when available
                "features_used": list((result_dict.get("features") or {}).keys()) or result_dict.get("features_used", []),
            }
            features_used = emotion_result.get("features_used", [])
        
        # Final fallback: mock response
        if not emotion_result:
            logger.warning("No emotion detector available, returning mock response")
            emotion_result = {
                "emotion": "neutral",
                "confidence": 0.5,
                "probabilities": {"neutral": 1.0},
                "features_used": []
            }
            features_used = []
        
        # Log emotion history to database if user_id is provided
        if user_id:
            try:
                emotion_repo = EmotionRepository(db)
                user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
                conversation_uuid = None
                if conversation_id:
                    conversation_uuid = uuid.UUID(conversation_id) if isinstance(conversation_id, str) else conversation_id
                message_uuid = None
                if message_id:
                    message_uuid = uuid.UUID(message_id) if isinstance(message_id, str) else message_id
                
                emotion_repo.create_emotion_record(
                    user_id=user_uuid,
                    emotion_type=emotion_result["emotion"],
                    confidence_score=emotion_result["confidence"],
                    voice_emotion=emotion_result.get("probabilities"),
                    text_sentiment=None,  # Audio-only analysis
                    conversation_id=conversation_uuid,
                    message_id=message_uuid
                )
            except Exception as db_error:
                # Log database error but don't fail the request
                logger.error(f"Failed to log emotion history to database: {db_error}")
        
        return EmotionAnalysisResponse(
            emotion=emotion_result["emotion"],
            confidence=emotion_result["confidence"],
            probabilities=emotion_result["probabilities"],
            timestamp=datetime.utcnow(),
            features_used=features_used
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

