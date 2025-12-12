"""
Baseline Tracker Service
Main FastAPI application for tracking user baselines
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from config import settings
from models.baseline_models import (
    BaselineRequest, BaselineResponse, VoiceFingerprint, EmotionBaseline,
    VoiceFeatures, DeviationAlert
)
from services.baseline_calculator import BaselineCalculator
from services.deviation_detector import DeviationDetector

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
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Update baseline with new data
    
    This endpoint would typically:
    1. Store voice features and emotion data
    2. Recalculate baseline if enough samples
    3. Check for deviations
    4. Return updated baseline info
    """
    try:
        logger.info(f"Updating baseline for user: {request.user_id}")
        
        # TODO: Fetch historical data from database
        # For now, return a mock response
        response = BaselineResponse(
            user_id=request.user_id,
            voice_fingerprint=None,
            emotion_baseline=None,
            deviation_score=None,
            deviation_detected=False,
            message="Baseline update received. Historical data required for calculation."
        )
        
        # If we have voice features, calculate fingerprint
        if request.voice_features:
            # TODO: Calculate from historical data
            response.voice_fingerprint = VoiceFingerprint(
                user_id=request.user_id,
                features=request.voice_features,
                confidence=0.5,
                calculated_at=datetime.utcnow()
            )
        
        # If we have emotion data, calculate baseline
        if request.emotion_data:
            # TODO: Calculate from historical data
            response.emotion_baseline = EmotionBaseline(
                user_id=request.user_id,
                emotion_distribution={},
                average_confidence=0.5,
                dominant_emotion="neutral",
                baseline_period_days=settings.BASELINE_WINDOW_DAYS,
                sample_count=0,
                calculated_at=datetime.utcnow()
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Error updating baseline: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Baseline update failed: {str(e)}"
        )


@app.get("/baseline/{user_id}", response_model=BaselineResponse)
async def get_baseline(
    user_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get current baseline for a user"""
    try:
        # TODO: Fetch from database
        return BaselineResponse(
            user_id=user_id,
            voice_fingerprint=None,
            emotion_baseline=None,
            deviation_score=None,
            deviation_detected=False,
            message="Baseline not yet calculated. Need more samples."
        )
    except Exception as e:
        logger.error(f"Error getting baseline: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get baseline: {str(e)}"
        )


@app.post("/baseline/check-deviation", response_model=DeviationAlert)
async def check_deviation(
    request: BaselineRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Check for deviations from baseline"""
    try:
        # TODO: Implement full deviation checking
        return DeviationAlert(
            user_id=request.user_id,
            deviation_type="emotion",
            deviation_score=0.0,
            baseline_value=0.0,
            current_value=0.0,
            severity="low",
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Error checking deviation: {str(e)}")
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

