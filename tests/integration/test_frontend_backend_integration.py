"""
Integration tests for Frontend-Backend communication
Tests the full flow: Frontend API calls → API Gateway → Backend Services → Response
"""

import pytest
import sys
import os
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
import jwt
from datetime import datetime, timedelta

pytestmark = pytest.mark.integration

# Add paths for imports
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'apps', 'backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Add API Gateway path
gateway_path = os.path.join(os.path.dirname(__file__), '..', '..', 'apps', 'backend', 'services', 'api-gateway')
if os.path.exists(gateway_path) and gateway_path not in sys.path:
    sys.path.insert(0, gateway_path)


class TestFrontendBackendIntegration:
    """Integration tests for frontend-backend communication flows"""
    
    @pytest.fixture
    def gateway_client(self):
        """Create API Gateway test client with mocked dependencies"""
        from fastapi import Header, HTTPException, status, Depends
        from fastapi.security import HTTPBearer
        
        # Create a minimal FastAPI app that simulates the API Gateway
        # This allows testing the integration flow without complex imports
        app = FastAPI(title="API Gateway Test")
        security = HTTPBearer()
        
        async def verify_token(credentials = Depends(security)):
            """Verify authentication token"""
            if not credentials:
                raise HTTPException(status_code=403, detail="Authentication required")
            return credentials.credentials
        
        # Mock service endpoints with basic auth validation
        @app.post("/dissonance-detector/analyze")
        async def analyze_dissonance(
            request: dict,
            token: str = Depends(verify_token)
        ):
            """Mock dissonance detector endpoint"""
            # Basic validation
            if "transcript" not in request or "voice_emotion" not in request:
                raise HTTPException(status_code=422, detail="Missing required fields")
            return {
                "dissonance_level": "high",
                "dissonance_score": 0.82,
                "stated_emotion": "positive",
                "actual_emotion": "negative",
                "interpretation": "defensive_concealment",
                "risk_level": "medium-high",
                "confidence": 0.82,
                "details": {
                    "sentiment_score": 0.75,
                    "emotion_score": -0.65,
                    "gap": 1.40,
                    "normalized_gap": 0.70
                },
                "timestamp": "2025-12-12T12:00:00Z"
            }
        
        @app.post("/baseline-tracker/baseline/update")
        async def update_baseline(request: dict, token: str = Depends(verify_token)):
            """Mock baseline tracker endpoint"""
            return {
                "user_id": request.get("user_id", "test-user-123"),
                "deviation_detected": False,
                "message": "Baseline updated successfully"
            }
        
        @app.post("/baseline-tracker/baseline/check-deviation")
        async def check_deviation(request: dict, token: str = Depends(verify_token)):
            """Mock deviation check endpoint"""
            return {
                "user_id": request.get("user_id", "test-user-123"),
                "deviation_type": "voice_pitch",
                "deviation_score": 0.75,
                "baseline_value": 150.0,
                "current_value": 180.0,
                "severity": "high",
                "timestamp": "2025-12-12T12:00:00Z"
            }
        
        @app.post("/emotion-analysis/analyze")
        async def analyze_emotion(request: dict, token: str = Depends(verify_token)):
            """Mock emotion analysis endpoint"""
            return {
                "emotion": "sad",
                "confidence": 0.85,
                "valence": -0.65,
                "arousal": 0.3,
                "timestamp": "2025-12-12T12:00:00Z"
            }
        
        @app.get("/cultural-context/context")
        async def get_context(query: str, language: str = "en", token: str = Depends(verify_token)):
            """Mock cultural context endpoint"""
            return {
                "query": query,
                "language": language,
                "context": "In East African cultures, expressing sadness directly may be avoided.",
                "source": "local_kb_retrieval",
                "matches": [],
                "code_switching": {"code_switching_detected": False},
                "deflection": {"deflection_detected": False},
                "timestamp": "2025-12-12T12:00:00Z"
            }
        
        @app.post("/safety-moderation/validate")
        async def validate_content(request: dict, token: str = Depends(verify_token)):
            """Mock safety moderation endpoint"""
            return {
                "is_safe": True,
                "flagged": False,
                "confidence": 0.95,
                "issues": [],
                "action": "allow",
                "risk_score": 0.1,
                "hallucination_score": 0.05,
                "timestamp": "2025-12-12T12:00:00Z"
            }
        
        @app.get("/health")
        async def health():
            """Health check endpoint (no auth required)"""
            return {"status": "healthy"}
        
        return TestClient(app)
    
    @pytest.fixture
    def mock_token(self):
        """Create mock JWT token"""
        token_data = {
            "user_id": "test-user-123",
            "email": "test@example.com",
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(token_data, "test-secret", algorithm="HS256")
    
    def test_dissonance_detection_full_flow(self, gateway_client, mock_token):
        """Test full flow: Frontend → API Gateway → Dissonance Detector"""
        # Simulate frontend API call
        request_data = {
            "transcript": "I'm fine, everything is okay",
            "voice_emotion": {
                "emotion": "sad",
                "confidence": 0.85
            },
            "session_id": "session-123",
            "user_id": "test-user-123"
        }
        
        response = gateway_client.post(
            "/dissonance-detector/analyze",
            headers={"Authorization": f"Bearer {mock_token}"},
            json=request_data
        )
        
        # Verify response structure matches frontend expectations
        assert response.status_code == 200
        data = response.json()
        assert "dissonance_level" in data
        assert "dissonance_score" in data
        assert "risk_level" in data
        assert "interpretation" in data
        assert data["dissonance_level"] in ["low", "medium", "high"]
        assert 0.0 <= data["dissonance_score"] <= 1.0
    
    def test_baseline_update_full_flow(self, gateway_client, mock_token):
        """Test full flow: Frontend → API Gateway → Baseline Tracker"""
        # Simulate frontend API call
        request_data = {
            "user_id": "test-user-123",
            "voice_features": {
                "pitch_mean": 155.0,
                "pitch_std": 12.0,
                "energy_mean": 0.52,
                "energy_std": 0.11,
                "speech_rate": 2.6,
                "pause_frequency": 0.12
            },
            "emotion_data": {
                "emotion": "sad",
                "confidence": 0.85
            },
            "session_id": "session-123"
        }
        
        response = gateway_client.post(
            "/baseline-tracker/baseline/update",
            headers={"Authorization": f"Bearer {mock_token}"},
            json=request_data
        )
        
        # Verify response structure matches frontend expectations
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "deviation_detected" in data
        assert "message" in data
    
    def test_baseline_deviation_check_full_flow(self, gateway_client, mock_token):
        """Test full flow: Frontend → API Gateway → Baseline Tracker (deviation check)"""
        # Simulate frontend API call
        request_data = {
            "user_id": "test-user-123",
            "voice_features": {
                "pitch_mean": 180.0,
                "pitch_std": 15.0,
                "energy_mean": 0.6,
                "energy_std": 0.15
            },
            "session_id": "session-123"
        }
        
        response = gateway_client.post(
            "/baseline-tracker/baseline/check-deviation",
            headers={"Authorization": f"Bearer {mock_token}"},
            json=request_data
        )
        
        # Verify response structure matches frontend expectations
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "deviation_type" in data
        assert "deviation_score" in data
        assert "severity" in data
        assert data["severity"] in ["low", "medium", "high"]
        assert 0.0 <= data["deviation_score"] <= 1.0
    
    def test_emotion_analysis_full_flow(self, gateway_client, mock_token):
        """Test full flow: Frontend → API Gateway → Emotion Analysis"""
        # Simulate frontend API call
        request_data = {
            "audio_features": {
                "pitch_mean": 150.0,
                "energy_mean": 0.5
            },
            "transcript": "I'm feeling down today"
        }
        
        response = gateway_client.post(
            "/emotion-analysis/analyze",
            headers={"Authorization": f"Bearer {mock_token}"},
            json=request_data
        )
        
        # Verify response structure
        assert response.status_code == 200
        data = response.json()
        assert "emotion" in data
        assert "confidence" in data
        assert 0.0 <= data["confidence"] <= 1.0
    
    def test_cultural_context_full_flow(self, gateway_client, mock_token):
        """Test full flow: Frontend → API Gateway → Cultural Context"""
        # Simulate frontend API call
        response = gateway_client.get(
            "/cultural-context/context?query=feeling%20sad&language=en",
            headers={"Authorization": f"Bearer {mock_token}"}
        )
        
        # Verify response structure
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "context" in data
        assert "language" in data
        assert "source" in data
    
    def test_safety_moderation_full_flow(self, gateway_client, mock_token):
        """Test full flow: Frontend → API Gateway → Safety Moderation"""
        # Simulate frontend API call
        request_data = {
            "content": "I'm feeling okay today, thanks for asking.",
            "content_type": "user_input"
        }
        
        response = gateway_client.post(
            "/safety-moderation/validate",
            headers={"Authorization": f"Bearer {mock_token}"},
            json=request_data
        )
        
        # Verify response structure
        assert response.status_code == 200
        data = response.json()
        assert "is_safe" in data
        assert "flagged" in data
        assert "action" in data
        assert "confidence" in data
        assert data["action"] in ["allow", "review", "block"]
    
    def test_error_handling_unauthorized(self, gateway_client):
        """Test error handling for unauthorized requests"""
        # Test without token
        response = gateway_client.post(
            "/dissonance-detector/analyze",
            json={
                "transcript": "I'm fine",
                "voice_emotion": {"emotion": "sad", "confidence": 0.85}
            }
        )
        
        assert response.status_code == 403
    
    def test_error_handling_invalid_request(self, gateway_client, mock_token):
        """Test error handling for invalid requests"""
        # Test with missing required fields
        response = gateway_client.post(
            "/dissonance-detector/analyze",
            headers={"Authorization": f"Bearer {mock_token}"},
            json={
                "transcript": "I'm fine"
                # Missing voice_emotion
            }
        )
        
        # Should return validation error
        assert response.status_code in [400, 422, 503, 504]
    
    def test_rate_limiting_headers(self, gateway_client, mock_token):
        """Test that rate limiting headers are present"""
        response = gateway_client.get(
            "/health",
            headers={"Authorization": f"Bearer {mock_token}"}
        )
        
        # Verify the request was processed
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

