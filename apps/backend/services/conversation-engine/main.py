"""
Conversation Engine Service
Main FastAPI application for generating empathetic responses
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
from datetime import datetime
import uuid

from config import settings
from models.conversation_models import ChatRequest, ChatResponse
from services.gpt_service import GPTService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Initialize GPT service
gpt_service = GPTService(
    api_key=settings.OPENAI_API_KEY,
    model=settings.OPENAI_MODEL,
    max_tokens=settings.MAX_TOKENS,
    temperature=settings.TEMPERATURE
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    logger.info("Starting Conversation Engine Service...")
    logger.info("Conversation Engine Service started successfully")
    yield
    logger.info("Shutting down Conversation Engine Service...")


# Create FastAPI app
app = FastAPI(
    title="Conversation Engine Service",
    description="Generates empathetic, culturally-aware responses",
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
        "service": "conversation-engine",
        "gpt_configured": bool(settings.OPENAI_API_KEY)
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Generate empathetic response to user message
    
    Request:
    {
        "user_id": "uuid",
        "message": "I'm feeling really down today",
        "emotion_context": {"emotion": "sad", "confidence": 0.85},
        "dissonance_context": {...},
        "cultural_context": {...}
    }
    """
    try:
        logger.info(f"Generating response for user: {request.user_id}")
        
        # Generate response using GPT
        response_text = await gpt_service.generate_response(
            user_message=request.message,
            conversation_history=None,  # TODO: Fetch from database
            emotion_context=request.emotion_context,
            dissonance_context=request.dissonance_context,
            cultural_context=request.cultural_context
        )
        
        # Determine response type
        response_type = "empathetic"
        if request.dissonance_context and request.dissonance_context.get("risk_level") in ["medium-high", "high"]:
            response_type = "crisis_intervention"
        elif request.emotion_context and request.emotion_context.get("emotion") in ["sad", "anxious"]:
            response_type = "supportive"
        
        # Generate or use existing conversation ID
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        response = ChatResponse(
            conversation_id=conversation_id,
            message=response_text,
            emotion_detected=request.emotion_context.get("emotion") if request.emotion_context else None,
            response_type=response_type,
            timestamp=datetime.utcnow(),
            metadata={
                "model": settings.OPENAI_MODEL,
                "has_cultural_context": bool(request.cultural_context),
                "has_dissonance_context": bool(request.dissonance_context)
            }
        )
        
        logger.info(f"Response generated successfully for conversation: {conversation_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate response: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=settings.DEBUG
    )

