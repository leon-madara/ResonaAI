"""
Speech Processing Service for Mental Health Platform
Handles speech-to-text conversion with accent adaptation for East African English and Swahili
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
import logging
from typing import Dict, Any, Optional
import numpy as np
import io
import tempfile
import os
from datetime import datetime

from config import settings
from services.stt_service import STTService
from services.language_detector import LanguageDetector
from services.audio_preprocessor import AudioPreprocessor
from models.stt_models import STTRequest, STTResponse, LanguageDetectionRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
stt_service = STTService()
language_detector = LanguageDetector()
audio_preprocessor = AudioPreprocessor()

app = FastAPI(
    title="Speech Processing Service",
    description="Speech-to-text conversion with accent adaptation for East African languages",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Speech Processing Service")
    await stt_service.initialize()
    await language_detector.initialize()
    logger.info("Speech Processing Service started successfully")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check service health
        stt_health = await stt_service.health_check()
        language_health = await language_detector.health_check()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "stt_service": stt_health,
                "language_detector": language_health
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@app.post("/transcribe", response_model=STTResponse)
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    language: Optional[str] = Form(None),
    accent: Optional[str] = Form("kenyan"),
    enable_emotion_detection: bool = Form(False)
):
    """
    Transcribe audio to text with accent adaptation
    """
    try:
        # Validate audio file
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid audio file format"
            )
        
        # Read audio data
        audio_data = await audio_file.read()
        
        # Preprocess audio
        processed_audio = await audio_preprocessor.preprocess_audio(audio_data)
        
        # Detect language if not specified
        if not language:
            detected_language = await language_detector.detect_language(processed_audio)
            language = detected_language.language
            confidence = detected_language.confidence
        else:
            confidence = 1.0
        
        # Transcribe audio
        transcription_result = await stt_service.transcribe(
            audio=processed_audio,
            language=language,
            accent=accent,
            enable_emotion_detection=enable_emotion_detection
        )
        
        return STTResponse(
            text=transcription_result.text,
            language=language,
            language_confidence=confidence,
            accent=accent,
            confidence=transcription_result.confidence,
            processing_time=transcription_result.processing_time,
            emotion_data=transcription_result.emotion_data if enable_emotion_detection else None,
            segments=transcription_result.segments,
            metadata={
                "file_size": len(audio_data),
                "duration": transcription_result.duration,
                "sample_rate": transcription_result.sample_rate,
                "channels": transcription_result.channels
            }
        )
        
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )

@app.post("/transcribe-stream")
async def transcribe_audio_stream(
    audio_data: bytes,
    language: Optional[str] = None,
    accent: str = "kenyan"
):
    """
    Transcribe audio stream for real-time processing
    """
    try:
        # Preprocess audio
        processed_audio = await audio_preprocessor.preprocess_audio_stream(audio_data)
        
        # Detect language if not specified
        if not language:
            detected_language = await language_detector.detect_language(processed_audio)
            language = detected_language.language
        
        # Transcribe audio
        transcription_result = await stt_service.transcribe_stream(
            audio=processed_audio,
            language=language,
            accent=accent
        )
        
        return {
            "text": transcription_result.text,
            "language": language,
            "confidence": transcription_result.confidence,
            "is_final": transcription_result.is_final,
            "processing_time": transcription_result.processing_time
        }
        
    except Exception as e:
        logger.error(f"Stream transcription failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Stream transcription failed: {str(e)}"
        )

@app.post("/detect-language")
async def detect_language(audio_file: UploadFile = File(...)):
    """
    Detect language from audio
    """
    try:
        # Read audio data
        audio_data = await audio_file.read()
        
        # Preprocess audio
        processed_audio = await audio_preprocessor.preprocess_audio(audio_data)
        
        # Detect language
        result = await language_detector.detect_language(processed_audio)
        
        return {
            "language": result.language,
            "confidence": result.confidence,
            "alternatives": result.alternatives,
            "processing_time": result.processing_time
        }
        
    except Exception as e:
        logger.error(f"Language detection failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Language detection failed: {str(e)}"
        )

@app.get("/supported-languages")
async def get_supported_languages():
    """
    Get list of supported languages and accents
    """
    return {
        "languages": [
            {
                "code": "en",
                "name": "English",
                "accents": ["kenyan", "ugandan", "tanzanian", "general"]
            },
            {
                "code": "sw",
                "name": "Swahili",
                "accents": ["kenyan", "tanzanian", "ugandan"]
            }
        ],
        "default_language": "en",
        "default_accent": "kenyan"
    }

@app.get("/model-info")
async def get_model_info():
    """
    Get information about loaded models
    """
    return {
        "stt_models": await stt_service.get_model_info(),
        "language_detection_models": await language_detector.get_model_info(),
        "supported_formats": ["wav", "mp3", "flac", "m4a", "ogg"],
        "max_file_size": "10MB",
        "max_duration": "30 minutes"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
