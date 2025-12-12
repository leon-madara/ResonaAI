"""
PII Anonymization Service
Centralized service for detecting and anonymizing personally identifiable information
"""

import time
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from config import settings, PII_PATTERNS
from models import (
    AnonymizeRequest, AnonymizeResponse,
    DetectRequest, DetectResponse,
    DeanonymizeRequest, DeanonymizeResponse,
    BatchAnonymizeRequest, BatchAnonymizeResponse,
    PIIDetection, AnonymizationMethod
)
from anonymizer import get_anonymizer, PIIAnonymizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PII Anonymization Service",
    description="Service for detecting and anonymizing personally identifiable information",
    version="1.0.0"
)

# Security
security = HTTPBearer()


def get_user_from_token(credentials: HTTPAuthorizationCredentials) -> Optional[str]:
    """Extract user ID from JWT token"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload.get("user_id")
    except jwt.InvalidTokenError:
        return None


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "pii-anonymization",
        "patterns_loaded": len(PII_PATTERNS)
    }


@app.get("/patterns")
async def list_patterns():
    """List available PII detection patterns"""
    return {
        "patterns": [
            {
                "type": pii_type,
                "description": config["description"]
            }
            for pii_type, config in PII_PATTERNS.items()
        ],
        "anonymization_methods": [m.value for m in AnonymizationMethod]
    }


@app.post("/detect", response_model=DetectResponse)
async def detect_pii(
    request: DetectRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Detect PII in text without anonymizing
    
    Returns locations and types of PII found
    """
    try:
        anonymizer = get_anonymizer()
        
        detections = anonymizer.detect_pii(
            request.text,
            request.pii_types
        )
        
        return DetectResponse(
            text_length=len(request.text),
            pii_detected=detections,
            pii_count=len(detections),
            contains_pii=len(detections) > 0
        )
        
    except Exception as e:
        logger.error(f"PII detection failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PII detection failed"
        )


@app.post("/anonymize", response_model=AnonymizeResponse)
async def anonymize_text(
    request: AnonymizeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Anonymize PII in text
    
    Supports multiple anonymization methods:
    - tokenization: Reversible, creates tokens that can be mapped back
    - hashing: Irreversible, creates hash values
    - masking: Partially reveals data (e.g., email: j***@g***.com)
    - redaction: Completely removes data, leaves placeholders
    """
    try:
        start_time = time.time()
        
        user_id = request.user_id or get_user_from_token(credentials)
        anonymizer = get_anonymizer()
        
        anonymized_text, detections, tokens = anonymizer.anonymize(
            text=request.text,
            method=request.method,
            pii_types=request.pii_types,
            preserve_format=request.preserve_format,
            user_id=user_id
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        logger.info(f"Anonymized {len(detections)} PII instances using {request.method.value}")
        
        return AnonymizeResponse(
            original_length=len(request.text),
            anonymized_text=anonymized_text,
            pii_detected=detections,
            pii_count=len(detections),
            method=request.method.value,
            processing_time_ms=processing_time,
            tokens=tokens
        )
        
    except Exception as e:
        logger.error(f"Anonymization failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Anonymization failed"
        )


@app.post("/deanonymize", response_model=DeanonymizeResponse)
async def deanonymize_text(
    request: DeanonymizeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Reverse tokenization to restore original values
    
    Only works with tokenization method
    """
    try:
        anonymizer = get_anonymizer()
        
        restored_text, tokens_replaced = anonymizer.deanonymize(
            request.text,
            request.tokens
        )
        
        logger.info(f"De-anonymized {tokens_replaced} tokens")
        
        return DeanonymizeResponse(
            text=restored_text,
            tokens_replaced=tokens_replaced
        )
        
    except Exception as e:
        logger.error(f"De-anonymization failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="De-anonymization failed"
        )


@app.post("/batch/anonymize", response_model=BatchAnonymizeResponse)
async def batch_anonymize(
    request: BatchAnonymizeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Anonymize multiple texts in a single request
    """
    try:
        start_time = time.time()
        
        user_id = get_user_from_token(credentials)
        anonymizer = get_anonymizer()
        
        results = []
        total_pii = 0
        
        for text in request.texts:
            text_start = time.time()
            
            anonymized_text, detections, tokens = anonymizer.anonymize(
                text=text,
                method=request.method,
                pii_types=request.pii_types,
                user_id=user_id
            )
            
            text_time = (time.time() - text_start) * 1000
            
            result = AnonymizeResponse(
                original_length=len(text),
                anonymized_text=anonymized_text,
                pii_detected=detections,
                pii_count=len(detections),
                method=request.method.value,
                processing_time_ms=text_time,
                tokens=tokens
            )
            
            results.append(result)
            total_pii += len(detections)
        
        processing_time = (time.time() - start_time) * 1000
        
        logger.info(f"Batch anonymized {len(request.texts)} texts, {total_pii} total PII instances")
        
        return BatchAnonymizeResponse(
            results=results,
            total_pii_count=total_pii,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Batch anonymization failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch anonymization failed"
        )


@app.post("/external-api/prepare")
async def prepare_for_external_api(
    request: AnonymizeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Prepare text for sending to external APIs (OpenAI, Azure, Hume)
    
    Uses tokenization for reversible anonymization
    """
    try:
        anonymizer = get_anonymizer()
        
        anonymized_text, tokens = anonymizer.anonymize_for_external_api(
            request.text,
            api_name="external"
        )
        
        return {
            "anonymized_text": anonymized_text,
            "tokens": tokens,
            "original_length": len(request.text),
            "anonymized_length": len(anonymized_text),
            "pii_removed": len(tokens) > 0
        }
        
    except Exception as e:
        logger.error(f"External API preparation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="External API preparation failed"
        )


@app.post("/external-api/restore")
async def restore_from_external_api(
    request: DeanonymizeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Restore text received from external APIs
    
    Replaces tokens with original values
    """
    try:
        anonymizer = get_anonymizer()
        
        restored_text = anonymizer.restore_from_external_api(
            request.text,
            request.tokens
        )
        
        return {
            "restored_text": restored_text,
            "tokens_restored": len(request.tokens)
        }
        
    except Exception as e:
        logger.error(f"External API restoration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="External API restoration failed"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

