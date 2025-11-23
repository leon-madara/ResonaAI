"""
API Gateway Service for Mental Health Platform
Central entry point for all client requests with authentication, rate limiting, and routing
"""

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import httpx
import redis
import jwt
import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import os
from contextlib import asynccontextmanager

from config import settings
from middleware.rate_limiter import RateLimiter
from middleware.auth import AuthMiddleware
from middleware.logging import LoggingMiddleware
from utils.health_check import HealthChecker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service URLs
SERVICE_URLS = {
    "speech_processing": "http://speech-processing:8000",
    "emotion_analysis": "http://emotion-analysis:8000", 
    "conversation_engine": "http://conversation-engine:8000",
    "crisis_detection": "http://crisis-detection:8000",
    "safety_moderation": "http://safety-moderation:8000",
    "sync_service": "http://sync-service:8000",
    "cultural_context": "http://cultural-context:8000"
}

# Initialize Redis for rate limiting
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True
)

# Initialize HTTP client for service communication
http_client = httpx.AsyncClient(timeout=30.0)

# Health checker
health_checker = HealthChecker(SERVICE_URLS)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting API Gateway Service")
    
    # Check service health
    await health_checker.check_all_services()
    
    yield
    
    # Shutdown
    logger.info("Shutting down API Gateway Service")
    await http_client.aclose()

# Create FastAPI app
app = FastAPI(
    title="Mental Health Platform - API Gateway",
    description="Central API gateway for voice-first mental health support platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Security
security = HTTPBearer()

# Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(RateLimiter, redis_client=redis_client)

# Routes
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Redis connection
        redis_client.ping()
        
        # Check service health
        service_health = await health_checker.check_all_services()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "services": service_health,
            "redis": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )

@app.post("/auth/login")
async def login(request: Request):
    """User login endpoint"""
    try:
        body = await request.json()
        email = body.get("email")
        password = body.get("password")
        
        if not email or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password required"
            )
        
        # TODO: Implement actual authentication logic
        # For now, return a mock JWT token
        token_data = {
            "user_id": "user_123",
            "email": email,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        
        token = jwt.encode(
            token_data,
            settings.JWT_SECRET_KEY,
            algorithm="HS256"
        )
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 86400
        }
        
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@app.post("/auth/register")
async def register(request: Request):
    """User registration endpoint"""
    try:
        body = await request.json()
        
        # Validate required fields
        required_fields = ["email", "password", "consent_version"]
        for field in required_fields:
            if field not in body:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Field '{field}' is required"
                )
        
        # TODO: Implement actual user registration logic
        # For now, return success
        return {
            "message": "User registered successfully",
            "user_id": "user_123"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@app.post("/speech/transcribe")
async def transcribe_speech(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Route to speech processing service"""
    return await route_to_service("speech_processing", "/transcribe", request, credentials)

@app.post("/emotion/analyze")
async def analyze_emotion(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Route to emotion analysis service"""
    return await route_to_service("emotion_analysis", "/analyze", request, credentials)

@app.post("/conversation/chat")
async def chat(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Route to conversation engine service"""
    return await route_to_service("conversation_engine", "/chat", request, credentials)

@app.post("/crisis/detect")
async def detect_crisis(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Route to crisis detection service"""
    return await route_to_service("crisis_detection", "/detect", request, credentials)

@app.post("/safety/validate")
async def validate_response(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Route to safety moderation service"""
    return await route_to_service("safety_moderation", "/validate", request, credentials)

@app.post("/sync/upload")
async def upload_data(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Route to sync service"""
    return await route_to_service("sync_service", "/upload", request, credentials)

@app.get("/cultural/context")
async def get_cultural_context(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Route to cultural context service"""
    return await route_to_service("cultural_context", "/context", request, credentials)

async def route_to_service(
    service_name: str, 
    endpoint: str, 
    request: Request, 
    credentials: HTTPAuthorizationCredentials
) -> Dict[str, Any]:
    """Route request to appropriate microservice"""
    try:
        service_url = SERVICE_URLS.get(service_name)
        if not service_url:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service {service_name} not available"
            )
        
        # Get request body
        body = await request.body()
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {credentials.credentials}",
            "Content-Type": request.headers.get("Content-Type", "application/json"),
            "X-Forwarded-For": request.client.host,
            "X-User-Agent": request.headers.get("User-Agent", "")
        }
        
        # Make request to microservice
        response = await http_client.post(
            f"{service_url}{endpoint}",
            content=body,
            headers=headers
        )
        
        # Return response
        return response.json()
        
    except httpx.TimeoutException:
        logger.error(f"Timeout calling {service_name}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Service {service_name} timeout"
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error calling {service_name}: {e.response.status_code}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Service {service_name} error"
        )
    except Exception as e:
        logger.error(f"Error calling {service_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error"
        )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
