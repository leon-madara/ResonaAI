"""
Safety Moderation Service
Main FastAPI application for content moderation
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
from datetime import datetime
from typing import Dict, Any, List
from pydantic import BaseModel

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
    timestamp: datetime = datetime.utcnow()


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

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "safety-moderation"}

@app.post("/validate", response_model=ValidationResponse)
async def validate_content(
    request: ValidationRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Validate content for safety"""
    text = (request.content or "").lower()
    issues: List[str] = []

    crisis_hit = any(term in text for term in _CRISIS_TERMS)
    unsafe_advice_hit = any(term in text for term in _DISALLOWED_ADVICE_TERMS)

    # Conservative policy:
    # - User input with crisis terms → allow but flag for review
    # - AI response containing crisis/self-harm instructions → block
    if crisis_hit:
        issues.append("crisis_signal_detected")

    if unsafe_advice_hit:
        issues.append("unsafe_instruction_or_medical_advice")

    if request.content_type == "response":
        if unsafe_advice_hit:
            return ValidationResponse(
                is_safe=False,
                flagged=True,
                confidence=0.9,
                issues=issues,
                action="block",
                timestamp=datetime.utcnow(),
            )
        if crisis_hit:
            return ValidationResponse(
                is_safe=True,
                flagged=True,
                confidence=0.7,
                issues=issues,
                action="review",
                timestamp=datetime.utcnow(),
            )
    else:
        if crisis_hit:
            return ValidationResponse(
                is_safe=True,
                flagged=True,
                confidence=0.7,
                issues=issues,
                action="review",
                timestamp=datetime.utcnow(),
            )

    return ValidationResponse(
        is_safe=True,
        flagged=False,
        confidence=0.99,
        issues=[],
        action="allow",
        timestamp=datetime.utcnow(),
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

