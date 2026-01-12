"""
Mock API Server for Demo Data Generator

This module implements a FastAPI-based mock server that serves generated test data
and simulates the ResonaAI backend API for demonstration purposes.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from ..interfaces import APIServerInterface, StorageInterface
from ..models import (
    ServiceConfig, ProcessInfo, APIResponse, ConversationResponse,
    EmotionAnalysisResponse, CulturalAnalysisResponse, VoiceAnalysisResponse,
    ConversationThread, EmotionResult, CulturalContext, AudioFeatures,
    DissonanceResult, DeflectionResult, UserProfile
)


# Request/Response Models for API endpoints
class LoginRequest(BaseModel):
    """Login request model"""
    username: str
    password: str


class RegisterRequest(BaseModel):
    """Registration request model"""
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    user_id: str
    session_id: Optional[str] = None
    emotion_context: Optional[Dict[str, Any]] = None


class EmotionAnalysisRequest(BaseModel):
    """Emotion analysis request model"""
    text: str
    user_id: str
    include_voice_analysis: bool = False


class CulturalAnalysisRequest(BaseModel):
    """Cultural analysis request model"""
    text: str
    user_id: str
    language: str = "auto"


class VoiceAnalysisRequest(BaseModel):
    """Voice analysis request model"""
    audio_data: Optional[str] = None  # Base64 encoded audio
    text: str
    user_id: str


class WebSocketManager:
    """Manages WebSocket connections for real-time features"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logging.error(f"Error sending WebSocket message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connected WebSockets"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logging.error(f"Error broadcasting to WebSocket: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)


class MockAPIServer(APIServerInterface):
    """FastAPI-based mock server for demo data"""
    
    def __init__(self, storage: StorageInterface):
        self.storage = storage
        self.app = FastAPI(
            title="ResonaAI Demo API",
            description="Mock API server for ResonaAI demonstration",
            version="1.0.0"
        )
        self.server = None
        self.config: Optional[ServiceConfig] = None
        self.websocket_manager = WebSocketManager()
        self.security = HTTPBearer(auto_error=False)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Register endpoints and middleware
        self._setup_middleware()
        self.register_endpoints()
    
    def _setup_middleware(self):
        """Setup CORS and other middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Will be configured properly in start_server
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    async def _verify_token(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))):
        """Mock token verification - always returns success for demo"""
        if not credentials:
            # For demo purposes, allow some endpoints without auth
            return None
        
        # Mock token validation - in real implementation would verify JWT
        if credentials.credentials == "demo_token":
            return {"user_id": "demo_user", "username": "demo"}
        
        # For demo, accept any token
        return {"user_id": "demo_user", "username": "demo"}
    
    def simulate_processing_delay(self, endpoint: str) -> float:
        """Simulate realistic processing delays"""
        if not self.config:
            return 0.0
        
        delay_ms = self.config.processing_delay_ms
        
        # Different endpoints have different processing times
        endpoint_delays = {
            "/emotion-analysis/analyze": delay_ms * 1.5,
            "/dissonance-detector/analyze": delay_ms * 2.0,
            "/cultural-context/analyze": delay_ms * 1.2,
            "/conversation/chat": delay_ms * 2.5,
            "/speech/transcribe": delay_ms * 3.0,
        }
        
        actual_delay = endpoint_delays.get(endpoint, delay_ms) / 1000.0
        time.sleep(actual_delay)
        return actual_delay
    
    def register_endpoints(self) -> None:
        """Register all API endpoints"""
        
        # Health check endpoint
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "service": "demo-api",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "version": "1.0.0"
            }
        
        # Authentication endpoints
        @self.app.post("/auth/login", response_model=TokenResponse)
        async def login(request: LoginRequest):
            """Mock login endpoint"""
            self.simulate_processing_delay("/auth/login")
            
            # For demo, accept any credentials
            return TokenResponse(
                access_token="demo_token",
                token_type="bearer",
                expires_in=3600
            )
        
        @self.app.post("/auth/register", response_model=TokenResponse)
        async def register(request: RegisterRequest):
            """Mock registration endpoint"""
            self.simulate_processing_delay("/auth/register")
            
            # For demo, always succeed
            return TokenResponse(
                access_token="demo_token",
                token_type="bearer",
                expires_in=3600
            )
        
        # User endpoints
        @self.app.get("/users/me")
        async def get_current_user(user=Depends(self._verify_token)):
            """Get current user profile"""
            # Load a demo user profile from storage
            users_data = self.storage.load_data("users")
            if users_data and "users" in users_data:
                # Return first user as demo user
                demo_user = users_data["users"][0]
                return {
                    "id": demo_user["id"],
                    "username": "demo_user",
                    "email": "demo@resonaai.com",
                    "full_name": "Demo User",
                    "profile": demo_user["profile"]
                }
            
            return {
                "id": "demo_user",
                "username": "demo_user",
                "email": "demo@resonaai.com",
                "full_name": "Demo User"
            }
        
        # Conversation endpoints
        @self.app.post("/conversation/chat")
        async def chat_endpoint(request: ChatRequest, user=Depends(self._verify_token)):
            """Mock conversation endpoint - returns AI response with cultural context"""
            self.simulate_processing_delay("/conversation/chat")
            
            # Load conversation data from storage
            conversations_data = self.storage.load_data("conversations")
            if not conversations_data or "conversations" not in conversations_data:
                raise HTTPException(status_code=500, detail="No conversation data available")
            
            # Find a relevant conversation or use the first one
            conversations = conversations_data["conversations"]
            demo_conversation = conversations[0] if conversations else None
            
            if not demo_conversation:
                raise HTTPException(status_code=500, detail="No demo conversations available")
            
            # Simulate AI response based on the request
            response_message = {
                "id": f"msg_{int(time.time())}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "speaker": "assistant",
                "text": "I understand you're going through a challenging time. Can you tell me more about what's been on your mind lately?",
                "emotion": {
                    "detected": "empathetic",
                    "confidence": 0.92
                },
                "cultural_adaptation": {
                    "acknowledged_language_switch": "Swahili" in request.message,
                    "culturally_sensitive_response": True
                }
            }
            
            return {
                "success": True,
                "message": "Response generated successfully",
                "data": {
                    "response": response_message,
                    "session_id": request.session_id or f"session_{int(time.time())}",
                    "conversation_id": demo_conversation["id"]
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        @self.app.get("/conversations/{user_id}/history")
        async def get_conversation_history(user_id: str, limit: int = 50, user=Depends(self._verify_token)):
            """Get conversation history for a user"""
            conversations_data = self.storage.load_data("conversations")
            if not conversations_data or "conversations" not in conversations_data:
                return {"success": True, "data": {"conversations": []}}
            
            # Filter conversations for the user (or return demo data)
            user_conversations = [
                conv for conv in conversations_data["conversations"]
                if conv.get("user_id") == user_id
            ][:limit]
            
            return {
                "success": True,
                "data": {"conversations": user_conversations},
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Emotion Analysis endpoints
        @self.app.post("/emotion-analysis/analyze", response_model=EmotionAnalysisResponse)
        async def analyze_emotion(request: EmotionAnalysisRequest, user=Depends(self._verify_token)):
            """Analyze emotion in text with optional voice analysis"""
            self.simulate_processing_delay("/emotion-analysis/analyze")
            
            # Load emotion data from storage or generate on-the-fly
            emotions_data = self.storage.load_data("emotions")
            
            # Simulate emotion analysis result
            emotion_result = {
                "detected": "sad" if any(word in request.text.lower() for word in ["sad", "tired", "stressed", "nimechoka"]) else "neutral",
                "confidence": 0.78,
                "voice_truth_gap": 0.23 if request.include_voice_analysis else None,
                "features": {
                    "text_sentiment": -0.3,
                    "emotional_intensity": 0.6,
                    "cultural_markers": 1 if any(word in request.text for word in ["nimechoka", "sijui", "sawa"]) else 0
                }
            }
            
            return EmotionAnalysisResponse(
                success=True,
                message="Emotion analysis completed",
                emotion_result=emotion_result,
                timestamp=datetime.now(timezone.utc)
            )
        
        # Cultural Context endpoints
        @self.app.get("/cultural-context/context")
        async def get_cultural_context(query: str, language: str = "auto", user=Depends(self._verify_token)):
            """Get cultural context for text"""
            self.simulate_processing_delay("/cultural-context/analyze")
            
            # Load cultural patterns from storage
            cultural_data = self.storage.load_data("cultural_patterns")
            
            cultural_context = {
                "patterns": [],
                "deflection_detected": False,
                "cultural_significance": "low",
                "language_switches": []
            }
            
            # Check for Swahili patterns
            swahili_words = ["nimechoka", "sijui", "sawa", "tu", "hivi"]
            found_patterns = [word for word in swahili_words if word in query.lower()]
            
            if found_patterns:
                cultural_context.update({
                    "patterns": found_patterns,
                    "cultural_significance": "high",
                    "language_switches": ["swahili"],
                    "deflection_detected": "sawa tu" in query.lower() or "ni sawa" in query.lower()
                })
            
            return CulturalAnalysisResponse(
                success=True,
                message="Cultural analysis completed",
                cultural_context=cultural_context,
                timestamp=datetime.now(timezone.utc)
            )
        
        @self.app.post("/cultural-context/analyze")
        async def analyze_cultural_context(request: CulturalAnalysisRequest, user=Depends(self._verify_token)):
            """Analyze cultural context in text"""
            self.simulate_processing_delay("/cultural-context/analyze")
            
            # Load cultural data
            cultural_data = self.storage.load_data("cultural_patterns")
            
            # Simulate deflection detection
            deflection_patterns = ["sawa tu", "ni sawa", "hakuna matata", "it's fine"]
            deflection_detected = any(pattern in request.text.lower() for pattern in deflection_patterns)
            
            deflection_result = {
                "detected": deflection_detected,
                "confidence": 0.85 if deflection_detected else 0.1,
                "patterns": [pattern for pattern in deflection_patterns if pattern in request.text.lower()],
                "cultural_context": "East African cultural tendency to minimize problems",
                "suggested_response": "Gently probe deeper while respecting cultural boundaries"
            }
            
            return CulturalAnalysisResponse(
                success=True,
                message="Cultural deflection analysis completed",
                deflection_result=deflection_result,
                timestamp=datetime.now(timezone.utc)
            )
        
        # Voice Analysis endpoints
        @self.app.post("/speech/transcribe")
        async def transcribe_audio(request: VoiceAnalysisRequest, user=Depends(self._verify_token)):
            """Mock speech transcription endpoint"""
            self.simulate_processing_delay("/speech/transcribe")
            
            # For demo, return the provided text as if transcribed
            return {
                "success": True,
                "message": "Audio transcribed successfully",
                "data": {
                    "transcription": request.text,
                    "confidence": 0.95,
                    "language": "en-sw",  # English-Swahili mix
                    "duration_seconds": len(request.text) * 0.1  # Rough estimate
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        @self.app.post("/dissonance-detector/analyze")
        async def analyze_dissonance(request: VoiceAnalysisRequest, user=Depends(self._verify_token)):
            """Analyze voice-truth dissonance"""
            self.simulate_processing_delay("/dissonance-detector/analyze")
            
            # Load voice analysis data
            voice_data = self.storage.load_data("voice_analysis")
            
            # Simulate dissonance detection
            text_emotion = "sad" if any(word in request.text.lower() for word in ["sad", "tired", "stressed"]) else "neutral"
            voice_emotion = "happy" if "fine" in request.text.lower() or "okay" in request.text.lower() else text_emotion
            
            dissonance_detected = text_emotion != voice_emotion
            
            dissonance_result = {
                "text_emotion": text_emotion,
                "voice_emotion": voice_emotion,
                "dissonance_score": 0.7 if dissonance_detected else 0.1,
                "confidence": 0.82,
                "indicators": ["pitch_elevation", "speech_rate_increase"] if dissonance_detected else []
            }
            
            return VoiceAnalysisResponse(
                success=True,
                message="Voice-truth dissonance analysis completed",
                dissonance_result={
                    "detected": dissonance_detected,
                    "confidence": 0.82,
                    "voice_truth_gap": dissonance_result,
                    "explanation": "Voice tone suggests different emotion than text content" if dissonance_detected else "Voice and text emotions are aligned"
                },
                timestamp=datetime.now(timezone.utc)
            )
        
        # Baseline Tracker endpoints
        @self.app.get("/baseline-tracker/baseline/{user_id}")
        async def get_baseline(user_id: str, user=Depends(self._verify_token)):
            """Get user baseline data"""
            users_data = self.storage.load_data("users")
            if users_data and "users" in users_data:
                # Find user or return demo baseline
                user_profile = next((u for u in users_data["users"] if u["id"] == user_id), None)
                if user_profile and "baseline_data" in user_profile:
                    return {
                        "success": True,
                        "data": user_profile["baseline_data"],
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
            
            # Return demo baseline
            return {
                "success": True,
                "data": {
                    "voice_patterns": {
                        "average_pitch": 180.5,
                        "speech_rate": 145.2,
                        "emotional_baseline": "neutral",
                        "stress_indicators": ["pitch_elevation", "speech_acceleration"]
                    },
                    "emotional_patterns": {
                        "dominant_emotions": ["neutral", "happy", "stressed"],
                        "crisis_triggers": ["academic_failure", "family_pressure"],
                        "coping_mechanisms": ["social_support", "prayer"]
                    }
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        @self.app.post("/baseline-tracker/baseline/update")
        async def update_baseline(request: dict, user=Depends(self._verify_token)):
            """Update user baseline data"""
            self.simulate_processing_delay("/baseline-tracker/baseline/update")
            
            return {
                "success": True,
                "message": "Baseline updated successfully",
                "data": request,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        @self.app.post("/baseline-tracker/baseline/check-deviation")
        async def check_deviation(request: dict, user=Depends(self._verify_token)):
            """Check for baseline deviation"""
            self.simulate_processing_delay("/baseline-tracker/baseline/check-deviation")
            
            # Simulate deviation detection
            deviation_detected = request.get("current_emotion") not in ["neutral", "happy"]
            
            return {
                "success": True,
                "message": "Deviation check completed",
                "data": {
                    "deviation_detected": deviation_detected,
                    "severity": "medium" if deviation_detected else "low",
                    "confidence": 0.78,
                    "recommendations": ["Monitor closely", "Consider intervention"] if deviation_detected else ["Continue normal monitoring"]
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Crisis Detection and Safety endpoints
        @self.app.post("/safety-moderation/validate")
        async def validate_content(request: dict, user=Depends(self._verify_token)):
            """Validate content for safety concerns"""
            self.simulate_processing_delay("/safety-moderation/validate")
            
            text = request.get("text", "")
            crisis_keywords = [
                "suicide", "kill myself", "end it all", "ending it all", 
                "can't go on", "no point", "want to die", "disappear forever"
            ]
            crisis_detected = any(keyword in text.lower() for keyword in crisis_keywords)
            
            return {
                "success": True,
                "message": "Content validation completed",
                "data": {
                    "safe": not crisis_detected,
                    "crisis_level": "high" if crisis_detected else "none",
                    "intervention_required": crisis_detected,
                    "safety_resources": [
                        {
                            "name": "Kenya Crisis Helpline",
                            "phone": "+254-722-178-177",
                            "available": "24/7"
                        }
                    ] if crisis_detected else []
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # User Settings endpoints
        @self.app.get("/users/{user_id}/settings")
        async def get_user_settings(user_id: str, user=Depends(self._verify_token)):
            """Get user settings"""
            return {
                "success": True,
                "data": {
                    "language": "en-sw",
                    "cultural_context": "east_african",
                    "privacy_level": "standard",
                    "notifications": True,
                    "crisis_contacts": []
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        @self.app.put("/users/{user_id}/settings")
        async def save_user_settings(user_id: str, settings: dict, user=Depends(self._verify_token)):
            """Save user settings"""
            return {
                "success": True,
                "message": "Settings saved successfully",
                "data": settings,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Consent Management endpoints
        @self.app.get("/consent-management/consents")
        async def get_consents(user=Depends(self._verify_token)):
            """Get user consents"""
            return {
                "success": True,
                "data": {
                    "consents": [
                        {
                            "type": "data_processing",
                            "granted": True,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        },
                        {
                            "type": "voice_analysis",
                            "granted": True,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
                    ]
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # WebSocket endpoint for real-time features
        @self.app.websocket("/ws/{user_id}")
        async def websocket_endpoint(websocket: WebSocket, user_id: str):
            """WebSocket endpoint for real-time communication"""
            await self.websocket_manager.connect(websocket)
            try:
                while True:
                    # Wait for messages from client
                    data = await websocket.receive_text()
                    message_data = json.loads(data)
                    
                    # Echo back with processing simulation
                    response = {
                        "type": "response",
                        "user_id": user_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "data": message_data
                    }
                    
                    await self.websocket_manager.send_personal_message(
                        json.dumps(response), websocket
                    )
                    
            except WebSocketDisconnect:
                self.websocket_manager.disconnect(websocket)
            except Exception as e:
                self.logger.error(f"WebSocket error: {e}")
                self.websocket_manager.disconnect(websocket)
    
    def start_server(self, config: ServiceConfig) -> bool:
        """Start the mock API server"""
        try:
            self.config = config
            
            # Update CORS origins
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=config.cors_origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            
            # Start server in a separate thread/process
            self.logger.info(f"Starting mock API server on port {config.mock_api_port}")
            
            # For demo purposes, we'll use uvicorn programmatically
            # In production, this would be handled differently
            uvicorn_config = uvicorn.Config(
                self.app,
                host="0.0.0.0",
                port=config.mock_api_port,
                log_level="info"
            )
            
            self.server = uvicorn.Server(uvicorn_config)
            
            # Start server in background task
            # Note: This is a simplified implementation for demo purposes
            self.logger.info(f"Mock API server started on http://localhost:{config.mock_api_port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start mock API server: {e}")
            return False
    
    def stop_server(self) -> bool:
        """Stop the mock API server"""
        try:
            if self.server:
                self.server.should_exit = True
                self.logger.info("Mock API server stopped")
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop mock API server: {e}")
            return False
    
    def get_server_info(self) -> ProcessInfo:
        """Get server process information"""
        if not self.config:
            raise RuntimeError("Server not configured")
        
        return ProcessInfo(
            process_id=0,  # Placeholder - would be actual PID in production
            name="mock-api-server",
            port=self.config.mock_api_port,
            status="running" if self.server else "stopped",
            start_time=datetime.now(timezone.utc),
            url=f"http://localhost:{self.config.mock_api_port}"
        )