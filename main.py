"""
ResonaAI - Voice Emotion Detection Pipeline
Main FastAPI application entry point
"""

from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
import json
import logging
from typing import List, Dict, Any
import numpy as np
from loguru import logger
import inspect

from src.audio_processor import AudioProcessor
from src.emotion_detector import EmotionDetector
from src.streaming_processor import StreamingProcessor
from src.models import EmotionResult, HealthStatus, BatchEmotionResult
from src.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger.add("logs/app.log", rotation="1 day", retention="7 days")

app = FastAPI(
    title="ResonaAI - Voice Emotion Detection",
    description="A comprehensive voice emotion detection system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
audio_processor = AudioProcessor()
emotion_detector = EmotionDetector()
streaming_processor = StreamingProcessor(audio_processor, emotion_detector)

async def _maybe_await(value):
    """
    Await a value if it's awaitable, otherwise return it as-is.

    This makes it easier to patch async dependencies in tests using plain mocks.
    """
    if inspect.isawaitable(value):
        return await value
    return value

@app.on_event("startup")
async def startup_event():
    """Initialize models and components on startup"""
    logger.info("Starting ResonaAI Voice Emotion Detection Pipeline")
    await emotion_detector.load_models()
    logger.info("Models loaded successfully")

@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check endpoint"""
    return HealthStatus(
        status="healthy",
        message="ResonaAI Voice Emotion Detection Pipeline is running",
        version="1.0.0"
    )

@app.post("/detect-emotion/file", response_model=EmotionResult)
async def detect_emotion_from_file(file: UploadFile = File(...)):
    """
    Analyze emotion from uploaded audio file
    """
    try:
        # Read audio file
        audio_data = await file.read()
        
        # Process audio
        processed_audio = audio_processor.preprocess_audio(audio_data)
        
        # Detect emotion
        emotion_result = await _maybe_await(emotion_detector.detect_emotion(processed_audio))
        
        logger.info(f"Emotion detected: {emotion_result.emotion} (confidence: {emotion_result.confidence:.2f})")
        
        return emotion_result
        
    except Exception as e:
        logger.error(f"Error processing audio file: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process audio file: {str(e)}"}
        )

@app.post("/detect-emotion/batch", response_model=BatchEmotionResult)
async def detect_emotion_batch(files: List[UploadFile] = File(...)):
    """
    Analyze emotions from multiple audio files
    """
    try:
        results = []
        errors = []
        
        for file in files:
            try:
                # Read audio file
                audio_data = await file.read()
                
                # Process audio
                processed_audio = audio_processor.preprocess_audio(audio_data)
                
                # Detect emotion
                emotion_result = await _maybe_await(emotion_detector.detect_emotion(processed_audio))
                
                results.append({
                    "filename": file.filename,
                    "emotion": emotion_result.emotion,
                    "confidence": emotion_result.confidence,
                    "features": emotion_result.features
                })
                
            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {str(e)}")
                results.append({
                    "filename": file.filename,
                    "error": str(e)
                })
                errors.append({"filename": file.filename, "error": str(e)})

        if errors:
            # For now, fail the whole batch if any file fails (matches current tests).
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to process one or more files", "results": results},
            )
        
        return BatchEmotionResult(
            total_files=len(files),
            successful_analyses=len([r for r in results if "error" not in r]),
            results=results
        )
        
    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process batch: {str(e)}"}
        )

@app.websocket("/ws/emotion-stream")
async def websocket_emotion_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time emotion detection
    """
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            # Receive audio data
            data = await websocket.receive_bytes()
            
            # Process audio chunk
            emotion_result = await _maybe_await(streaming_processor.process_audio_chunk(data))
            
            # Send result back
            await websocket.send_text(json.dumps({
                "emotion": emotion_result.emotion,
                "confidence": emotion_result.confidence,
                "timestamp": emotion_result.timestamp.isoformat() if emotion_result.timestamp else None,
                "features": emotion_result.features
            }))
            
    except WebSocketDisconnect:
        logger.info("WebSocket connection disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close(code=1000)

@app.post("/detect-emotion/stream", response_model=EmotionResult)
async def detect_emotion_stream(request: Request):
    """
    Process audio stream for real-time emotion detection
    """
    try:
        audio_data = await request.body()
        # Process audio chunk
        emotion_result = await _maybe_await(streaming_processor.process_audio_chunk(audio_data))
        
        return emotion_result
        
    except Exception as e:
        logger.error(f"Error processing audio stream: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process audio stream: {str(e)}"}
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
