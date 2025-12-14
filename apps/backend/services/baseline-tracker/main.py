"""
Baseline Tracker Service
Main FastAPI application for tracking user baselines
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import logging
from datetime import datetime, timezone
from uuid import UUID

from config import settings
from database import get_db, init_db
from models.baseline_models import (
    BaselineRequest, BaselineResponse, VoiceFingerprint, EmotionBaseline,
    VoiceFeatures, DeviationAlert
)
from services.baseline_calculator import BaselineCalculator
from services.deviation_detector import DeviationDetector
from repositories.baseline_repository import BaselineRepository

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Initialize services
baseline_calculator = BaselineCalculator(
    min_samples=settings.MIN_SAMPLES_FOR_BASELINE,
    window_days=settings.BASELINE_WINDOW_DAYS
)
deviation_detector = DeviationDetector(threshold=settings.DEVIATION_THRESHOLD)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    logger.info("Starting Baseline Tracker Service...")
    # Initialize database tables if needed
    try:
        init_db()
    except Exception as e:
        logger.warning(f"Database initialization warning: {e}")
    logger.info("Baseline Tracker Service started successfully")
    yield
    logger.info("Shutting down Baseline Tracker Service...")


# Create FastAPI app
app = FastAPI(
    title="Baseline Tracker Service",
    description="Tracks personal voice fingerprint and emotional baseline",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "baseline-tracker"
    }


@app.post("/baseline/update", response_model=BaselineResponse)
async def update_baseline(
    request: BaselineRequest,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Update baseline with new data
    
    This endpoint:
    1. Fetches historical data from database
    2. Recalculates baseline if enough samples
    3. Checks for deviations
    4. Saves baseline and deviations to database
    5. Returns updated baseline info
    """
    try:
        user_id_uuid = UUID(request.user_id)
        logger.info(f"Updating baseline for user: {request.user_id}")
        
        repository = BaselineRepository(db)
        voice_fingerprint = None
        emotion_baseline = None
        deviation_score = None
        deviation_detected = False
        message = "Baseline update received."
        
        # Process voice features if provided
        if request.voice_features:
            # Get historical voice features
            historical_features = repository.get_historical_voice_features(
                user_id_uuid,
                settings.BASELINE_WINDOW_DAYS
            )
            
            # Add current features to history for calculation
            current_feature_dict = request.voice_features.dict()
            historical_features.append(current_feature_dict)
            
            # Filter to recent window
            filtered_features = baseline_calculator.filter_recent_data(
                historical_features,
                settings.BASELINE_WINDOW_DAYS
            )
            
            # Calculate baseline
            voice_baseline_data = baseline_calculator.calculate_voice_baseline(filtered_features)
            
            if voice_baseline_data:
                # Save voice baseline
                repository.save_user_baseline(
                    user_id_uuid,
                    "voice",
                    voice_baseline_data,
                    voice_baseline_data.get("sample_count", len(filtered_features))
                )
                
                # Check for deviation
                deviation_result = deviation_detector.detect_voice_deviation(
                    current_feature_dict,
                    voice_baseline_data
                )
                
                if deviation_result and deviation_result.get("deviation_detected"):
                    deviation_score = deviation_result.get("deviation_score", 0.0)
                    deviation_detected = True
                    
                    # Save deviation if we have a session_id
                    if request.session_id:
                        try:
                            session_id_uuid = UUID(request.session_id)
                            repository.save_deviation(
                                user_id_uuid,
                                session_id_uuid,
                                "voice",
                                voice_baseline_data,
                                current_feature_dict,
                                deviation_score
                            )
                        except (ValueError, Exception) as e:
                            logger.warning(f"Could not save voice deviation: {e}")
                
                # Create voice fingerprint response
                voice_fingerprint = VoiceFingerprint(
                    user_id=request.user_id,
                    features=request.voice_features,
                    confidence=0.8 if voice_baseline_data else 0.5,
                    calculated_at=datetime.now(timezone.utc)
                )
                message = f"Voice baseline calculated from {voice_baseline_data.get('sample_count', 0)} samples."
            else:
                message = f"Insufficient voice data. Need at least {settings.MIN_SAMPLES_FOR_BASELINE} samples."
        
        # Process emotion data if provided
        if request.emotion_data:
            # Get historical emotions
            historical_emotions = repository.get_historical_emotions(
                user_id_uuid,
                settings.BASELINE_WINDOW_DAYS
            )
            
            # Add current emotion to history
            if isinstance(request.emotion_data, dict):
                emotion_record = {
                    "emotion": request.emotion_data.get("emotion", "neutral"),
                    "confidence": request.emotion_data.get("confidence", 0.5),
                    "timestamp": datetime.now(timezone.utc)
                }
                historical_emotions.append(emotion_record)
            
            # Filter to recent window
            filtered_emotions = baseline_calculator.filter_recent_data(
                historical_emotions,
                settings.BASELINE_WINDOW_DAYS
            )
            
            # Calculate emotion baseline
            emotion_baseline_data = baseline_calculator.calculate_emotion_baseline(filtered_emotions)
            
            if emotion_baseline_data:
                # Save emotion baseline
                repository.save_user_baseline(
                    user_id_uuid,
                    "emotion",
                    emotion_baseline_data,
                    emotion_baseline_data.get("sample_count", len(filtered_emotions))
                )
                
                # Check for deviation
                if isinstance(request.emotion_data, dict):
                    deviation_result = deviation_detector.detect_emotion_deviation(
                        request.emotion_data,
                        emotion_baseline_data
                    )
                    
                    if deviation_result and deviation_result.get("deviation_detected"):
                        if deviation_score is None:
                            deviation_score = deviation_result.get("deviation_score", 0.0)
                        else:
                            # Use higher deviation score
                            deviation_score = max(
                                deviation_score,
                                deviation_result.get("deviation_score", 0.0)
                            )
                        deviation_detected = True
                        
                        # Save deviation if we have a session_id
                        if request.session_id:
                            try:
                                session_id_uuid = UUID(request.session_id)
                                repository.save_deviation(
                                    user_id_uuid,
                                    session_id_uuid,
                                    "emotion",
                                    emotion_baseline_data,
                                    request.emotion_data,
                                    deviation_result.get("deviation_score", 0.0)
                                )
                            except (ValueError, Exception) as e:
                                logger.warning(f"Could not save emotion deviation: {e}")
                
                # Create emotion baseline response
                emotion_baseline = EmotionBaseline(
                    user_id=request.user_id,
                    emotion_distribution=emotion_baseline_data.get("emotion_distribution", {}),
                    average_confidence=emotion_baseline_data.get("average_confidence", 0.5),
                    dominant_emotion=emotion_baseline_data.get("dominant_emotion", "neutral"),
                    baseline_period_days=settings.BASELINE_WINDOW_DAYS,
                    sample_count=emotion_baseline_data.get("sample_count", 0),
                    calculated_at=datetime.now(timezone.utc)
                )
                message = f"Emotion baseline calculated from {emotion_baseline_data.get('sample_count', 0)} samples."
            else:
                if not voice_fingerprint:
                    message = f"Insufficient emotion data. Need at least {settings.MIN_SAMPLES_FOR_BASELINE} samples."
        
        response = BaselineResponse(
            user_id=request.user_id,
            voice_fingerprint=voice_fingerprint,
            emotion_baseline=emotion_baseline,
            deviation_score=deviation_score,
            deviation_detected=deviation_detected,
            message=message
        )
        
        return response
        
    except ValueError as e:
        logger.error(f"Invalid UUID format: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user_id or session_id format: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error updating baseline: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Baseline update failed: {str(e)}"
        )


@app.get("/baseline/{user_id}", response_model=BaselineResponse)
async def get_baseline(
    user_id: str,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get current baseline for a user"""
    try:
        user_id_uuid = UUID(user_id)
        repository = BaselineRepository(db)
        
        # Get all baselines for user
        baselines = repository.get_user_baselines(user_id_uuid)
        
        voice_fingerprint = None
        emotion_baseline = None
        
        # Extract voice and emotion baselines
        for baseline in baselines:
            if baseline.baseline_type == "voice":
                baseline_value = baseline.baseline_value
                # Create VoiceFingerprint from stored baseline
                # Note: We need to reconstruct VoiceFeatures from baseline_value
                if isinstance(baseline_value, dict):
                    voice_features = VoiceFeatures(
                        pitch_mean=baseline_value.get("pitch_mean", 0.0),
                        pitch_std=baseline_value.get("pitch_std", 0.0),
                        energy_mean=baseline_value.get("energy_mean", 0.0),
                        energy_std=baseline_value.get("energy_std", 0.0),
                        speech_rate=baseline_value.get("speech_rate", 0.0),
                        pause_frequency=baseline_value.get("pause_frequency", 0.0),
                        duration=0.0  # Not stored in baseline
                    )
                    voice_fingerprint = VoiceFingerprint(
                        user_id=user_id,
                        features=voice_features,
                        confidence=0.8,
                        calculated_at=baseline.updated_at or baseline.established_at
                    )
            
            elif baseline.baseline_type == "emotion":
                baseline_value = baseline.baseline_value
                if isinstance(baseline_value, dict):
                    emotion_baseline = EmotionBaseline(
                        user_id=user_id,
                        emotion_distribution=baseline_value.get("emotion_distribution", {}),
                        average_confidence=baseline_value.get("average_confidence", 0.5),
                        dominant_emotion=baseline_value.get("dominant_emotion", "neutral"),
                        baseline_period_days=settings.BASELINE_WINDOW_DAYS,
                        sample_count=baseline_value.get("sample_count", baseline.session_count),
                        calculated_at=baseline.updated_at or baseline.established_at
                    )
        
        if not voice_fingerprint and not emotion_baseline:
            message = "Baseline not yet calculated. Need more samples."
        else:
            message = f"Retrieved baseline(s) for user. Voice: {voice_fingerprint is not None}, Emotion: {emotion_baseline is not None}."
        
        return BaselineResponse(
            user_id=user_id,
            voice_fingerprint=voice_fingerprint,
            emotion_baseline=emotion_baseline,
            deviation_score=None,
            deviation_detected=False,
            message=message
        )
        
    except ValueError as e:
        logger.error(f"Invalid UUID format: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user_id format: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error getting baseline: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get baseline: {str(e)}"
        )


@app.post("/baseline/check-deviation", response_model=DeviationAlert)
async def check_deviation(
    request: BaselineRequest,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Check for deviations from baseline"""
    try:
        user_id_uuid = UUID(request.user_id)
        repository = BaselineRepository(db)
        
        deviation_type = "unknown"
        deviation_score = 0.0
        baseline_value = None
        current_value = None
        
        # Check voice deviation if voice features provided
        if request.voice_features:
            voice_baseline = repository.get_user_baseline(user_id_uuid, "voice")
            
            if voice_baseline and voice_baseline.baseline_value:
                current_feature_dict = request.voice_features.dict()
                deviation_result = deviation_detector.detect_voice_deviation(
                    current_feature_dict,
                    voice_baseline.baseline_value
                )
                
                if deviation_result and deviation_result.get("deviation_detected"):
                    deviation_type = "voice"
                    deviation_score = deviation_result.get("deviation_score", 0.0)
                    baseline_value = voice_baseline.baseline_value
                    current_value = current_feature_dict
                    
                    # Save deviation if we have a session_id
                    if request.session_id:
                        try:
                            session_id_uuid = UUID(request.session_id)
                            repository.save_deviation(
                                user_id_uuid,
                                session_id_uuid,
                                "voice",
                                baseline_value,
                                current_value,
                                deviation_score
                            )
                        except (ValueError, Exception) as e:
                            logger.warning(f"Could not save voice deviation: {e}")
        
        # Check emotion deviation if emotion data provided
        if request.emotion_data and isinstance(request.emotion_data, dict):
            emotion_baseline = repository.get_user_baseline(user_id_uuid, "emotion")
            
            if emotion_baseline and emotion_baseline.baseline_value:
                deviation_result = deviation_detector.detect_emotion_deviation(
                    request.emotion_data,
                    emotion_baseline.baseline_value
                )
                
                if deviation_result and deviation_result.get("deviation_detected"):
                    emotion_score = deviation_result.get("deviation_score", 0.0)
                    
                    # Use the higher deviation score if both checked
                    if deviation_score < emotion_score:
                        deviation_type = "emotion"
                        deviation_score = emotion_score
                        baseline_value = emotion_baseline.baseline_value
                        current_value = request.emotion_data
                    
                    # Save deviation if we have a session_id
                    if request.session_id:
                        try:
                            session_id_uuid = UUID(request.session_id)
                            repository.save_deviation(
                                user_id_uuid,
                                session_id_uuid,
                                "emotion",
                                emotion_baseline.baseline_value,
                                request.emotion_data,
                                emotion_score
                            )
                        except (ValueError, Exception) as e:
                            logger.warning(f"Could not save emotion deviation: {e}")
        
        # If no deviation detected, return low severity
        if deviation_score == 0.0:
            deviation_type = "none"
        
        severity = deviation_detector.calculate_severity(deviation_score)
        
        return DeviationAlert(
            user_id=request.user_id,
            deviation_type=deviation_type,
            deviation_score=deviation_score,
            baseline_value=baseline_value if baseline_value else {},
            current_value=current_value if current_value else {},
            severity=severity,
            timestamp=datetime.now(timezone.utc)
        )
        
    except ValueError as e:
        logger.error(f"Invalid UUID format: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user_id or session_id format: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error checking deviation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deviation check failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=settings.DEBUG
    )

