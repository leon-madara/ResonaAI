"""
Crisis Detection Service
Main FastAPI application for crisis detection and risk assessment
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
from datetime import datetime
import uuid

from config import settings
from models.crisis_models import (
    CrisisDetectionRequest, CrisisDetectionResponse,
    EscalationRequest, EscalationResponse
)
from services.risk_calculator import RiskCalculator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Initialize risk calculator
risk_calculator = RiskCalculator(
    thresholds=settings.RISK_THRESHOLDS,
    crisis_keywords=settings.CRISIS_KEYWORDS
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    logger.info("Starting Crisis Detection Service...")
    logger.info("Crisis Detection Service started successfully")
    yield
    logger.info("Shutting down Crisis Detection Service...")


# Create FastAPI app
app = FastAPI(
    title="Crisis Detection Service",
    description="Multi-layer crisis detection and risk assessment",
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
        "service": "crisis-detection"
    }


@app.post("/detect", response_model=CrisisDetectionResponse)
async def detect_crisis(
    request: CrisisDetectionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Detect crisis and calculate risk
    
    Request:
    {
        "user_id": "uuid",
        "transcript": "I'm feeling really hopeless",
        "emotion_data": {"emotion": "sad", "confidence": 0.9},
        "dissonance_data": {...},
        "baseline_data": {...}
    }
    """
    try:
        logger.info(f"Detecting crisis for user: {request.user_id}")
        
        # Calculate risk
        risk_result = risk_calculator.calculate_risk(
            transcript=request.transcript,
            emotion_data=request.emotion_data,
            dissonance_data=request.dissonance_data,
            baseline_data=request.baseline_data
        )
        
        # Build response
        response = CrisisDetectionResponse(
            risk_level=risk_result["risk_level"],
            risk_score=risk_result["risk_score"],
            crisis_detected=risk_result["crisis_detected"],
            detection_methods=risk_result["detection_methods"],
            escalation_required=risk_result["escalation_required"],
            recommended_action=risk_result["recommended_action"],
            timestamp=datetime.utcnow(),
            details={
                "user_id": request.user_id,
                "session_id": request.session_id,
                "conversation_id": request.conversation_id
            }
        )
        
        # Log crisis detection
        if response.crisis_detected:
            logger.warning(
                f"CRISIS DETECTED - User: {request.user_id}, "
                f"Risk Level: {response.risk_level}, "
                f"Methods: {response.detection_methods}"
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Error detecting crisis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Crisis detection failed: {str(e)}"
        )


@app.post("/escalate", response_model=EscalationResponse)
async def escalate_crisis(
    request: EscalationRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Escalate crisis to human review or emergency services"""
    try:
        escalation_id = str(uuid.uuid4())
        
        # TODO: Implement actual escalation logic
        # - Send to human review queue
        # - Contact emergency services if critical
        # - Send alerts via Twilio
        
        logger.warning(
            f"CRISIS ESCALATION - ID: {escalation_id}, "
            f"User: {request.user_id}, "
            f"Risk: {request.risk_level}, "
            f"Type: {request.escalation_type}"
        )
        
        return EscalationResponse(
            escalation_id=escalation_id,
            status="initiated",
            action_taken=f"Escalated via {request.escalation_type}",
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error escalating crisis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Escalation failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=settings.DEBUG
    )

