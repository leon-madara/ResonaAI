"""
Dissonance Detector Service
Main FastAPI application for detecting dissonance between transcript sentiment and voice emotion
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
from datetime import datetime, timezone

from config import settings
from models.dissonance_models import DissonanceRequest, DissonanceResponse, SentimentResult, DissonanceDetails
from services.sentiment_analyzer import SentimentAnalyzer
from services.dissonance_calculator import DissonanceCalculator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Initialize services
sentiment_analyzer = SentimentAnalyzer(settings.SENTIMENT_MODEL)
dissonance_calculator = DissonanceCalculator(
    settings.EMOTION_VALENCE_MAP,
    settings.DISSONANCE_THRESHOLDS
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup
    logger.info("Starting Dissonance Detector Service...")
    await sentiment_analyzer.load_model()
    logger.info("Dissonance Detector Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Dissonance Detector Service...")


# Create FastAPI app
app = FastAPI(
    title="Dissonance Detector Service",
    description="Detects dissonance between transcript sentiment and voice emotion",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - Configure appropriately for production
debug_mode = getattr(settings, 'DEBUG', False)
cors_origins = ["*"] if debug_mode else [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://mentalhealth.ke",
    "https://www.mentalhealth.ke"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        model_status = "loaded" if sentiment_analyzer._model_loaded else "not_loaded"
        status = "healthy" if sentiment_analyzer._model_loaded else "degraded"
        
        return {
            "status": status,
            "service": "dissonance-detector",
            "model_loaded": sentiment_analyzer._model_loaded,
            "model_status": model_status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "dissonance-detector",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@app.post("/analyze", response_model=DissonanceResponse)
async def analyze_dissonance(
    request: DissonanceRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Analyze dissonance between transcript sentiment and voice emotion
    
    Request:
    {
        "transcript": "I'm fine, everything is okay",
        "voice_emotion": {
            "emotion": "sad",
            "confidence": 0.85
        },
        "session_id": "uuid",
        "user_id": "uuid"
    }
    
    Response:
    {
        "dissonance_level": "high",
        "dissonance_score": 0.82,
        "stated_emotion": "positive",
        "actual_emotion": "negative",
        "interpretation": "defensive_concealment",
        "risk_level": "medium-high",
        "confidence": 0.82,
        "details": {
            "sentiment_score": 0.75,
            "emotion_score": -0.65,
            "gap": 1.40,
            "normalized_gap": 0.70
        },
        "timestamp": "2025-12-12T12:00:00"
    }
    """
    try:
        # Validate input
        if not request.transcript or not request.transcript.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transcript is required and cannot be empty"
            )
        
        if not request.voice_emotion:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="voice_emotion is required"
            )
        
        if "emotion" not in request.voice_emotion:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="voice_emotion must contain 'emotion' field"
            )
        
        logger.info(
            f"Analyzing dissonance for user {request.user_id or 'unknown'}, "
            f"session {request.session_id or 'unknown'}, "
            f"transcript: {request.transcript[:50]}..."
        )
        
        # Analyze sentiment from transcript
        sentiment_result = await sentiment_analyzer.analyze(request.transcript)
        logger.debug(f"Sentiment analysis result: {sentiment_result}")
        
        # Calculate dissonance
        dissonance_result = dissonance_calculator.calculate(
            sentiment_result,
            request.voice_emotion
        )
        logger.debug(f"Dissonance calculation result: {dissonance_result}")
        
        # Build response
        response = DissonanceResponse(
            dissonance_level=dissonance_result["dissonance_level"],
            dissonance_score=dissonance_result["dissonance_score"],
            stated_emotion=dissonance_result["stated_emotion"],
            actual_emotion=dissonance_result["actual_emotion"],
            interpretation=dissonance_result["interpretation"],
            risk_level=dissonance_result["risk_level"],
            confidence=dissonance_result["confidence"],
            details=DissonanceDetails(**dissonance_result["details"]),
            timestamp=request.timestamp or datetime.utcnow()
        )
        
        logger.info(
            f"Dissonance analysis complete for user {request.user_id or 'unknown'}: "
            f"{response.dissonance_level} (score: {response.dissonance_score:.2f}, "
            f"risk: {response.risk_level})"
        )
        
        return response
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error analyzing dissonance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error analyzing dissonance: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Dissonance analysis failed. Please try again later."
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=settings.DEBUG if hasattr(settings, 'DEBUG') else False
    )

