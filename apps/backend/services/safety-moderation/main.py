"""
Safety Moderation Service
Main FastAPI application for content moderation
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import uuid

import jwt

from config import settings
from database import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

security = HTTPBearer()

class ValidationRequest(BaseModel):
    content: str
    content_type: str = "response"  # "response" or "user_input"

class ValidationResponse(BaseModel):
    is_safe: bool
    flagged: bool
    confidence: float
    issues: list = []
    action: str = "allow"  # "allow", "block", "review"
    timestamp: datetime = datetime.now(timezone.utc)
    risk_score: float = 0.0  # 0-1
    hallucination_score: float = 0.0  # 0-1


_CRISIS_TERMS: List[str] = [
    "suicide",
    "kill myself",
    "end it all",
    "better off dead",
    "self harm",
    "cut myself",
]

_DISALLOWED_ADVICE_TERMS: List[str] = [
    # MVP set: prevent explicit self-harm instructions / medical prescribing.
    "take these pills",
    "increase your dose",
    "stop your medication",
    "how to kill",
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Safety Moderation Service...")
    yield
    logger.info("Shutting down Safety Moderation Service...")

app = FastAPI(title="Safety Moderation Service", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_verified_claims(credentials: HTTPAuthorizationCredentials) -> Dict[str, Any]:
    """
    Decode and verify JWT claims from the Authorization header.

    Purpose:
    - Enforce authenticated access with a verified token
    - Provide consistent identity attribution (user_id / role) across endpoints

    Raises:
    - HTTP 401 if token is missing/invalid/expired or required claims are absent.
    """
    token = credentials.credentials
    try:
        claims = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user_id = claims.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing required claims",
        )

    return claims


def _require_admin(claims: Dict[str, Any]) -> None:
    """
    Enforce admin-only access based on verified claims.

    Rules:
    - Allow role: "admin" or "moderator"
    """
    role = claims.get("role")
    if role not in ("admin", "moderator"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "safety-moderation"}

@app.post("/validate", response_model=ValidationResponse)
async def validate_content(
    request: ValidationRequest,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Validate content for safety using advanced filtering"""
    from services.content_filter import get_content_filter
    from services.hallucination_detector import get_hallucination_detector
    from services.review_queue import get_review_queue
    from repositories.moderation_repository import ModerationRepository
    
    claims = _get_verified_claims(credentials)
    user_id_claim = claims.get("user_id")

    text = request.content or ""
    text_lower = text.lower()
    issues: List[str] = []
    
    # Use advanced content filter
    content_filter = get_content_filter()
    risk_analysis = content_filter.calculate_risk_score(text, request.content_type)
    
    # Use hallucination detector for AI responses
    hallucination_detector = get_hallucination_detector()
    hallucination_analysis = {}
    if request.content_type == "response":
        hallucination_analysis = hallucination_detector.analyze(text)
    
    # Collect issues
    if risk_analysis.get("crisis_detected"):
        issues.append("crisis_signal_detected")
    if risk_analysis.get("medical_advice_detected"):
        issues.append("unsafe_instruction_or_medical_advice")
    if risk_analysis.get("toxicity_detected"):
        issues.append("toxicity_detected")
    if hallucination_analysis.get("needs_review"):
        issues.extend(hallucination_analysis.get("issues", []))
    
    # Determine action based on risk analysis
    action = risk_analysis.get("recommended_action", "allow")
    risk_score = risk_analysis.get("risk_score", 0.0)
    hallucination_score = hallucination_analysis.get("hallucination_score", 0.0)
    
    # Calculate overall confidence
    confidence = 1.0 - max(risk_score, hallucination_score)
    confidence = max(0.1, confidence)  # Minimum 10% confidence
    
    # Determine if safe
    is_safe = action != "block"
    flagged = len(issues) > 0 or risk_score > 0.3 or hallucination_score > 0.5
    
    # Add to review queue if needed
    review_queue = get_review_queue()
    if flagged and action in ("review", "block"):
        try:
            # Extract user_id from verified JWT claims
            user_id = user_id_claim
            priority = "urgent" if risk_score > 0.7 else "high" if risk_score > 0.5 else "normal"
            review_queue.add_to_queue(
                content=text,
                content_type=request.content_type,
                user_id=user_id,
                validation_result={
                    "risk_analysis": risk_analysis,
                    "hallucination_analysis": hallucination_analysis,
                    "issues": issues,
                },
                priority=priority
            )
        except Exception as e:
            logger.warning(f"Failed to add to review queue: {e}")
    
    # Log moderation decision to database
    moderation_repo = ModerationRepository(db)
    try:
        # Determine moderation type based on what was detected
        moderation_type = "content_filter"
        if hallucination_analysis.get("needs_review"):
            moderation_type = "hallucination_detector"
        
        # Get message_id from request if available (would need to be added to ValidationRequest)
        message_id = None  # TODO: Add message_id to ValidationRequest if needed
        
        parsed_user_id: Optional[uuid.UUID] = None
        try:
            parsed_user_id = uuid.UUID(str(user_id_claim)) if user_id_claim else None
        except Exception:
            parsed_user_id = None

        moderation_repo.create_moderation_log(
            moderation_type=moderation_type,
            action_taken=action,
            user_id=parsed_user_id,
            message_id=message_id,
            flagged_content=text[:1000] if flagged else None,  # Truncate for storage
            confidence_score=confidence
        )
    except Exception as db_error:
        # Log database error but don't fail the request
        logger.error(f"Failed to log moderation decision to database: {db_error}")
    
    # Log moderation decision (legacy review_queue method)
    try:
        review_queue.log_moderation_decision(
            content=text[:1000],  # Truncate
            content_type=request.content_type,
            user_id=user_id_claim,
            validation_result={
                "risk_analysis": risk_analysis,
                "hallucination_analysis": hallucination_analysis,
            },
            action=action
        )
    except Exception as e:
        logger.warning(f"Failed to log moderation decision: {e}")
    
    return ValidationResponse(
        is_safe=is_safe,
        flagged=flagged,
        confidence=confidence,
        issues=issues,
        action=action,
        timestamp=datetime.now(timezone.utc),
        risk_score=risk_score,
        hallucination_score=hallucination_score,
    )


@app.get("/moderation/queue")
async def get_moderation_queue(
    status: str = "pending",
    priority: Optional[str] = None,
    limit: int = 50,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get moderation queue items (admin only)"""
    from services.review_queue import get_review_queue
    
    claims = _get_verified_claims(credentials)
    _require_admin(claims)

    review_queue = get_review_queue()
    items = review_queue.get_queue(status=status, priority=priority, limit=limit)
    
    return {
        "items": items,
        "count": len(items),
        "status": status
    }


@app.post("/moderation/review/{review_id}")
async def review_content(
    review_id: str,
    status: str,
    decision: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update review status (admin only)"""
    from services.review_queue import get_review_queue
    
    if status not in ("in_review", "approved", "rejected", "resolved"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status"
        )
    
    review_queue = get_review_queue()
    claims = _get_verified_claims(credentials)
    _require_admin(claims)
    reviewer_id = claims.get("user_id")
    
    success = review_queue.update_review_status(
        review_id=review_id,
        status=status,
        reviewer_id=reviewer_id,
        decision=decision
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review item not found"
        )
    
    return {"message": "Review status updated", "review_id": review_id, "status": status}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

