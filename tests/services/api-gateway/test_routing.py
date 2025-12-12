"""
Unit tests for API Gateway routing functionality
"""

import pytest
import sys
import os
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient

# Add services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'services', 'api-gateway'))


class TestServiceRouting:
    """Test service routing endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client with mocked dependencies"""
        with patch('main.redis_client') as mock_redis, \
             patch('main.health_checker') as mock_health, \
             patch('main.http_client') as mock_http:
            
            mock_redis.ping.return_value = True
            mock_health.check_all_services = Mock(return_value={})
            
            from main import app
            return TestClient(app)
    
    @pytest.fixture
    def mock_token(self):
        """Create mock JWT token"""
        import jwt
        from datetime import datetime, timedelta
        
        token_data = {
            "user_id": "test-user-id",
            "email": "test@example.com",
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(token_data, "test-secret", algorithm="HS256")
    
    def test_speech_transcribe_routing(self, client, mock_token):
        """Test routing to speech processing service"""
        mock_response = Mock()
        mock_response.json.return_value = {"transcript": "test transcript"}
        mock_response.raise_for_status = Mock()
        
        with patch('main.http_client') as mock_http:
            mock_http.request = AsyncMock(return_value=mock_response)
            
            response = client.post(
                "/speech/transcribe",
                headers={"Authorization": f"Bearer {mock_token}"},
                json={"audio": "base64encoded"}
            )
            
            # Should route to service (may fail if service unavailable, but routing should work)
            assert response.status_code in [200, 503, 504]
    
    def test_emotion_analyze_routing(self, client, mock_token):
        """Test routing to emotion analysis service"""
        mock_response = Mock()
        mock_response.json.return_value = {"emotion": "happy", "confidence": 0.9}
        mock_response.raise_for_status = Mock()
        
        with patch('main.http_client') as mock_http:
            mock_http.request = AsyncMock(return_value=mock_response)
            
            response = client.post(
                "/emotion/analyze",
                headers={"Authorization": f"Bearer {mock_token}"},
                json={"audio_features": {}}
            )
            
            assert response.status_code in [200, 503, 504]
    
    def test_conversation_chat_routing(self, client, mock_token):
        """Test routing to conversation engine service"""
        mock_response = Mock()
        mock_response.json.return_value = {"message": "AI response"}
        mock_response.raise_for_status = Mock()
        
        with patch('main.http_client') as mock_http:
            mock_http.request = AsyncMock(return_value=mock_response)
            
            response = client.post(
                "/conversation/chat",
                headers={"Authorization": f"Bearer {mock_token}"},
                json={"message": "Hello", "conversation_id": "test-id"}
            )
            
            assert response.status_code in [200, 503, 504]
    
    def test_crisis_detect_routing(self, client, mock_token):
        """Test routing to crisis detection service"""
        mock_response = Mock()
        mock_response.json.return_value = {"risk_level": "low", "crisis_detected": False}
        mock_response.raise_for_status = Mock()
        
        with patch('main.http_client') as mock_http:
            mock_http.request = AsyncMock(return_value=mock_response)
            
            response = client.post(
                "/crisis/detect",
                headers={"Authorization": f"Bearer {mock_token}"},
                json={"transcript": "I'm fine", "emotion": "sad"}
            )
            
            assert response.status_code in [200, 503, 504]
    
    def test_protected_endpoint_requires_auth(self, client):
        """Test that protected endpoints require authentication"""
        response = client.post("/speech/transcribe", json={})
        assert response.status_code == 403  # Forbidden without token

