"""
Crisis Detection Service
Main FastAPI application for crisis detection and risk assessment
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import logging
from datetime import datetime
import uuid

from config import settings
from models.crisis_models import (
    CrisisDetectionRequest, CrisisDetectionResponse,
    EscalationRequest, EscalationResponse
)
from services.risk_calculator import RiskCalculator
from database import get_db
from repositories.crisis_repository import CrisisRepository

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
    db: Session = Depends(get_db),
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
        
        # Log crisis detection to database
        crisis_repo = CrisisRepository(db)
        try:
            # Determine detection method string
            detection_method = ", ".join(risk_result["detection_methods"]) if risk_result["detection_methods"] else "unknown"
            
            # Convert user_id and conversation_id to UUID if they're strings
            user_id = uuid.UUID(request.user_id) if isinstance(request.user_id, str) else request.user_id
            conversation_id = None
            if request.conversation_id:
                conversation_id = uuid.UUID(request.conversation_id) if isinstance(request.conversation_id, str) else request.conversation_id
            
            crisis_repo.create_crisis_event(
                user_id=user_id,
                risk_level=risk_result["risk_level"],
                detection_method=detection_method,
                conversation_id=conversation_id,
                escalation_required=risk_result["escalation_required"]
            )
        except Exception as db_error:
            # Log database error but don't fail the request
            logger.error(f"Failed to log crisis event to database: {db_error}")
        
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
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Escalate crisis to human review or emergency services"""
    try:
        crisis_repo = CrisisRepository(db)

        crisis_id = uuid.UUID(request.crisis_id) if isinstance(request.crisis_id, str) else request.crisis_id
        user_id = uuid.UUID(request.user_id) if isinstance(request.user_id, str) else request.user_id

        # Ensure the crisis event is marked as requiring escalation (best-effort)
        try:
            crisis_repo.update_escalation_status(
                crisis_id=crisis_id,
                escalation_required=True,
            )
        except Exception as db_error:
            logger.error(f"Failed to update crisis event escalation flag: {db_error}")

        # Idempotency: either caller-provided or deterministic default
        idempotency_key = request.idempotency_key or f"{str(crisis_id)}:{request.escalation_type}"
        existing = crisis_repo.get_escalation_by_idempotency_key(idempotency_key)
        if existing:
            return EscalationResponse(
                escalation_id=str(existing.id),
                status=existing.status,
                action_taken=existing.action_taken or "Escalation already recorded",
                timestamp=datetime.utcnow(),
            )

        provider = settings.ESCALATION_PROVIDER if settings.ESCALATION_PROVIDER_ENABLED else "stub"

        escalation = crisis_repo.create_escalation(
            crisis_event_id=crisis_id,
            user_id=user_id,
            escalation_type=request.escalation_type,
            idempotency_key=idempotency_key,
            reason=request.reason,
            provider=provider,
        )

        # Route escalation behind env flags (dev stub ok)
        try:
            if provider == "stub":
                action_taken = f"Stub-routed escalation ({request.escalation_type})"
            else:
                # Provider integrations should be implemented behind env flags.
                # For now, route deterministically and record provider name.
                action_taken = f"Routed escalation via provider={provider} ({request.escalation_type})"

            crisis_repo.update_escalation_state(
                escalation_id=escalation.id,
                new_status="routed",
                action_taken=action_taken,
            )

            logger.warning(
                f"CRISIS ESCALATION - ID: {escalation.id}, "
                f"User: {request.user_id}, "
                f"Risk: {request.risk_level}, "
                f"Type: {request.escalation_type}, "
                f"Provider: {provider}"
            )

            return EscalationResponse(
                escalation_id=str(escalation.id),
                status="routed",
                action_taken=action_taken,
                timestamp=datetime.utcnow(),
            )
        except Exception as route_error:
            # Failure handling: persist failure state
            try:
                crisis_repo.update_escalation_state(
                    escalation_id=escalation.id,
                    new_status="failed",
                    action_taken="Escalation routing failed",
                    error_message=str(route_error),
                )
            except Exception:
                logger.error("Failed to persist escalation failure state")

            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to route escalation",
            )
        
    except HTTPException:
        raise
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

