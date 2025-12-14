"""
Simple test server for frontend testing
Provides basic authentication endpoints
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from typing import Optional

app = FastAPI(title="ResonaAI Test API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing - using simple hash for testing
import hashlib

def hash_password(password: str) -> str:
    """Simple password hashing for testing"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return hash_password(plain_password) == hashed_password

# JWT settings
SECRET_KEY = "test-secret-key-for-development-only"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Test user database (in-memory)
TEST_USERS = {
    "leon.madara@outlook.com": {
        "id": "test-user-123",
        "email": "leon.madara@outlook.com",
        "name": "Leon Madara",
        "password_hash": hash_password("12345"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
}

# Request/Response models
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    consent_version: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    created_at: str

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.get("/")
async def root():
    return {"message": "ResonaAI Test API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.post("/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login endpoint"""
    user = TEST_USERS.get(request.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "user_id": user["id"]},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "created_at": user["created_at"]
        }
    )

@app.post("/auth/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """Register endpoint"""
    if request.email in TEST_USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user_id = f"user-{len(TEST_USERS) + 1}"
    new_user = {
        "id": user_id,
        "email": request.email,
        "name": request.email.split("@")[0],
        "password_hash": hash_password(request.password),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    TEST_USERS[request.email] = new_user
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user["email"], "user_id": new_user["id"]},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": new_user["id"],
            "email": new_user["email"],
            "name": new_user["name"],
            "created_at": new_user["created_at"]
        }
    )

@app.get("/users/me", response_model=UserResponse)
async def get_current_user():
    """Get current user (simplified - no auth check for testing)"""
    user = TEST_USERS["leon.madara@outlook.com"]
    return UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        created_at=user["created_at"]
    )

# Placeholder endpoints for other services
@app.get("/users/{user_id}/settings")
async def get_user_settings(user_id: str):
    return {}

@app.put("/users/{user_id}/settings")
async def save_user_settings(user_id: str, settings: dict):
    return settings

@app.get("/consent-management/consents")
async def get_consents():
    return []

@app.get("/conversations/{user_id}/sessions")
async def get_sessions(user_id: str):
    return []

@app.get("/baseline-tracker/baseline/{user_id}")
async def get_baseline(user_id: str):
    return {"user_id": user_id}

# Speech Processing endpoints
@app.post("/speech/transcribe")
async def transcribe_audio():
    """Mock speech transcription endpoint"""
    # Return mock transcription and emotion data
    return {
        "text": "This is a test transcription. I'm feeling okay today.",
        "language": "en",
        "confidence": 0.95,
        "emotion_data": {
            "emotion": "neutral",
            "confidence": 0.8,
            "valence": 0.5,
            "arousal": 0.4
        },
        "duration": 3.5,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Dissonance Analysis endpoint
@app.post("/dissonance-detector/analyze")
async def analyze_dissonance_endpoint():
    """Mock dissonance analysis endpoint"""
    return {
        "dissonance_level": "low",
        "dissonance_score": 0.2,
        "stated_emotion": "neutral",
        "actual_emotion": "neutral",
        "interpretation": "Your words and tone are aligned",
        "risk_level": "low",
        "confidence": 0.85,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": {
            "sentiment_score": 0.5,
            "emotion_score": 0.5,
            "gap": 0.0,
            "normalized_gap": 0.0
        }
    }

# Baseline Tracker endpoints
@app.post("/baseline-tracker/baseline/update")
async def update_baseline_endpoint():
    """Mock baseline update endpoint"""
    return {
        "user_id": "test-user-123",
        "deviation_detected": False,
        "message": "Baseline updated successfully"
    }

# Conversation endpoints
class ChatRequest(BaseModel):
    message: str
    user_id: str
    session_id: Optional[str] = None
    emotion_context: Optional[dict] = None

@app.post("/conversation/chat")
async def chat_endpoint(request: ChatRequest):
    """Mock conversation endpoint - returns AI response"""
    # Generate a contextual response based on the message
    user_message = request.message.lower()
    
    # Simple response logic
    if "hello" in user_message or "hi" in user_message:
        response_text = "Hello! I'm here to listen and support you. How are you feeling today?"
    elif "sad" in user_message or "depressed" in user_message:
        response_text = "I hear that you're going through a difficult time. It's okay to feel sad. Would you like to talk about what's been weighing on you?"
    elif "anxious" in user_message or "worried" in user_message:
        response_text = "Anxiety can be really challenging. Let's take this one step at a time. What's making you feel anxious right now?"
    elif "happy" in user_message or "good" in user_message or "great" in user_message:
        response_text = "That's wonderful to hear! I'm glad you're feeling positive. What's been going well for you?"
    elif "help" in user_message:
        response_text = "I'm here to help. You can talk to me about anything that's on your mind. What would you like to discuss?"
    else:
        response_text = "Thank you for sharing that with me. I'm listening. Can you tell me more about how you're feeling?"
    
    return {
        "message": response_text,  # Frontend expects 'message' not 'response'
        "response": response_text,  # Keep both for compatibility
        "message_id": f"msg-{datetime.now(timezone.utc).timestamp()}",
        "session_id": request.session_id or f"session-{datetime.now(timezone.utc).timestamp()}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "emotion_detected": request.emotion_context.get("emotion") if request.emotion_context else "neutral",
        "confidence": 0.85,
        "response_type": "normal"
    }

@app.get("/conversations/{user_id}/history")
async def get_conversation_history(user_id: str, limit: int = 50):
    """Mock conversation history endpoint"""
    return {
        "user_id": user_id,
        "conversations": [],
        "total": 0
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting ResonaAI Test Server on http://localhost:8000")
    print("Test credentials: leon.madara@outlook.com / 12345")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
