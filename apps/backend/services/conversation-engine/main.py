"""
Conversation Engine Service
Main FastAPI application for generating empathetic responses
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import logging
from datetime import datetime
import uuid
import httpx

from config import settings
from models.conversation_models import ChatRequest, ChatResponse
from services.gpt_service import GPTService
from services.encryption_client import EncryptionClient
from database import get_db
from repositories.conversation_repository import ConversationRepository

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

# Global HTTP + encryption client (created during lifespan)
http_client: httpx.AsyncClient | None = None
encryption_client: EncryptionClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    global http_client, encryption_client
    logger.info("Starting Conversation Engine Service...")
    logger.info("Conversation Engine Service started successfully")
    http_client = httpx.AsyncClient(timeout=10.0)
    encryption_client = EncryptionClient(settings.ENCRYPTION_SERVICE_URL, http_client=http_client)
    yield
    logger.info("Shutting down Conversation Engine Service...")
    if http_client:
        await http_client.aclose()


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
    db: Session = Depends(get_db),
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
        
        conversation_repo = ConversationRepository(db)
        # user_id may be a UUID string in production; tests may use non-UUID strings.
        try:
            user_uuid = uuid.UUID(request.user_id) if isinstance(request.user_id, str) else request.user_id
        except Exception:
            user_uuid = uuid.uuid5(uuid.NAMESPACE_URL, f"user:{request.user_id}")
        
        # Get or create conversation
        conversation = None
        conversation_id = None
        conversation_id_public: str | None = None
        if request.conversation_id:
            conversation_id_public = str(request.conversation_id)
            try:
                conversation_id_uuid = uuid.UUID(request.conversation_id) if isinstance(request.conversation_id, str) else request.conversation_id
            except Exception:
                # Stable mapping for non-UUID client IDs
                conversation_id_uuid = uuid.uuid5(uuid.NAMESPACE_URL, f"conversation:{user_uuid}:{request.conversation_id}")
            conversation = conversation_repo.get_conversation(conversation_id_uuid)
            if conversation:
                conversation_id = conversation.id
            else:
                # Create new conversation if ID provided but not found
                conversation = conversation_repo.create_conversation(
                    user_id=user_uuid,
                    emotion_summary=request.emotion_context
                )
                conversation_id = conversation.id
        else:
            # Create new conversation
            conversation = conversation_repo.create_conversation(
                user_id=user_uuid,
                emotion_summary=request.emotion_context
            )
            conversation_id = conversation.id

        if conversation_id_public is None:
            conversation_id_public = str(conversation_id)
        
        # Fetch conversation history from database
        conversation_history = None
        try:
            messages = conversation_repo.get_conversation_messages(conversation_id)
            # Build conversation history for GPT (decrypting stored ciphertext)
            history: list[dict] = []
            if encryption_client:
                for m in messages[-10:]:
                    try:
                        plaintext = await encryption_client.decrypt_text(
                            ciphertext=m.encrypted_content,
                            key_id=f"conversation:{conversation_id}",
                        )
                        history.append(
                            {
                                "role": "assistant" if m.message_type == "ai" else "user",
                                "content": plaintext,
                            }
                        )
                    except Exception as e:
                        logger.warning(f"Failed to decrypt message {getattr(m, 'id', None)}: {e}")
            conversation_history = history or None
        except Exception as e:
            logger.warning(f"Failed to fetch conversation history: {e}")
        
        # Generate response using GPT
        response_text = await gpt_service.generate_response(
            user_message=request.message,
            conversation_history=conversation_history,
            emotion_context=request.emotion_context,
            dissonance_context=request.dissonance_context,
            cultural_context=request.cultural_context
        )
        
        # Store user message (encrypted at rest via encryption-service)
        try:
            if not encryption_client:
                raise RuntimeError("Encryption client not initialized")
            enc = await encryption_client.encrypt_text(
                plaintext=request.message,
                key_id=f"conversation:{conversation_id}",
            )
            conversation_repo.create_message(
                conversation_id=conversation_id,
                message_type="user",
                encrypted_content=enc.ciphertext,
                emotion_data=request.emotion_context,
            )
        except Exception as e:
            logger.error(f"Failed to store user message: {e}")
        
        # Determine response type
        response_type = "empathetic"
        if request.dissonance_context and request.dissonance_context.get("risk_level") in ["medium-high", "high"]:
            response_type = "crisis_intervention"
        elif request.emotion_context and request.emotion_context.get("emotion") in ["sad", "anxious"]:
            response_type = "supportive"
        
        # Store AI response (encrypted at rest via encryption-service)
        try:
            if not encryption_client:
                raise RuntimeError("Encryption client not initialized")
            enc = await encryption_client.encrypt_text(
                plaintext=response_text,
                key_id=f"conversation:{conversation_id}",
            )
            conversation_repo.create_message(
                conversation_id=conversation_id,
                message_type="ai",
                encrypted_content=enc.ciphertext,
                emotion_data=request.emotion_context,
            )
        except Exception as e:
            logger.error(f"Failed to store AI message: {e}")
        
        response = ChatResponse(
            conversation_id=conversation_id_public,
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

