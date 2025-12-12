"""
Unit tests for Conversation Engine Service
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from datetime import datetime

# Store original working directory
original_cwd = os.getcwd()


class TestConversationEngine:
    """Test Conversation Engine service endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client with mocked dependencies"""
        # Change to service directory for imports
        service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'services', 'conversation-engine'))
        old_cwd = os.getcwd()
        os.chdir(service_dir)
        
        try:
            # Add service directory to Python path
            if service_dir not in sys.path:
                sys.path.insert(0, service_dir)
            
            # Clear cached modules
            for mod_name in list(sys.modules.keys()):
                if mod_name in ['main', 'config'] or mod_name.startswith('models.conversation'):
                    del sys.modules[mod_name]
            
            with patch('main.gpt_service') as mock_gpt:
                mock_gpt.generate_response = AsyncMock(return_value="I understand how you're feeling. Let's talk about it.")
                
                from main import app
                yield TestClient(app)
        finally:
            os.chdir(old_cwd)
            if service_dir in sys.path:
                sys.path.remove(service_dir)
    
    @pytest.fixture
    def auth_token(self):
        """Generate a test JWT token"""
        return "Bearer test-token"
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "conversation-engine"
        assert "gpt_configured" in data
    
    def test_chat_empathetic_response(self, client, auth_token):
        """Test generating empathetic response"""
        request_data = {
            "user_id": "test-user",
            "message": "I'm feeling really down today",
            "emotion_context": {
                "emotion": "sad",
                "confidence": 0.85
            },
            "dissonance_context": None,
            "cultural_context": None
        }
        
        response = client.post(
            "/chat",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "message" in data
        assert data["emotion_detected"] == "sad"
        assert data["response_type"] == "supportive"
        assert "timestamp" in data
        assert "metadata" in data
    
    def test_chat_crisis_intervention(self, client, auth_token):
        """Test generating crisis intervention response"""
        request_data = {
            "user_id": "test-user",
            "message": "I don't want to live anymore",
            "emotion_context": {
                "emotion": "sad",
                "confidence": 0.95
            },
            "dissonance_context": {
                "risk_level": "high",
                "dissonance_score": 0.85
            },
            "cultural_context": None
        }
        
        response = client.post(
            "/chat",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["response_type"] == "crisis_intervention"
    
    def test_chat_with_cultural_context(self, client, auth_token):
        """Test generating response with cultural context"""
        request_data = {
            "user_id": "test-user",
            "message": "I'm struggling with family expectations",
            "emotion_context": {
                "emotion": "anxious",
                "confidence": 0.80
            },
            "dissonance_context": None,
            "cultural_context": {
                "region": "East Africa",
                "language": "Swahili",
                "cultural_norms": ["family_first", "respect_elders"]
            }
        }
        
        response = client.post(
            "/chat",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["has_cultural_context"] is True
    
    def test_chat_with_conversation_id(self, client, auth_token):
        """Test chat with existing conversation ID"""
        conversation_id = "existing-conversation-123"
        request_data = {
            "user_id": "test-user",
            "message": "Tell me more",
            "conversation_id": conversation_id,
            "emotion_context": None,
            "dissonance_context": None,
            "cultural_context": None
        }
        
        response = client.post(
            "/chat",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == conversation_id
    
    def test_chat_missing_message(self, client, auth_token):
        """Test chat with missing message"""
        request_data = {
            "user_id": "test-user"
        }
        
        response = client.post(
            "/chat",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 422
    
    def test_chat_no_auth(self, client):
        """Test chat without authentication"""
        request_data = {
            "user_id": "test-user",
            "message": "Hello"
        }
        
        response = client.post("/chat", json=request_data)
        assert response.status_code == 403
    
    def test_chat_error_handling(self, client, auth_token):
        """Test error handling in chat generation"""
        with patch('main.gpt_service') as mock_gpt:
            mock_gpt.generate_response = AsyncMock(side_effect=Exception("API error"))
            
            from main import app
            test_client = TestClient(app)
            
            request_data = {
                "user_id": "test-user",
                "message": "Hello"
            }
            
            response = test_client.post(
                "/chat",
                json=request_data,
                headers={"Authorization": auth_token}
            )
            
            assert response.status_code == 500
            assert "failed" in response.json()["detail"].lower()
    
    def test_chat_supportive_response(self, client, auth_token):
        """Test generating supportive response for anxious emotion"""
        request_data = {
            "user_id": "test-user",
            "message": "I'm worried about the future",
            "emotion_context": {
                "emotion": "anxious",
                "confidence": 0.80
            },
            "dissonance_context": None,
            "cultural_context": None
        }
        
        response = client.post(
            "/chat",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["response_type"] == "supportive"
        assert data["emotion_detected"] == "anxious"
    
    def test_chat_with_dissonance_context(self, client, auth_token):
        """Test chat with dissonance context"""
        request_data = {
            "user_id": "test-user",
            "message": "I'm fine, really",
            "emotion_context": {
                "emotion": "sad",
                "confidence": 0.90
            },
            "dissonance_context": {
                "dissonance_level": "high",
                "interpretation": "defensive_concealment",
                "risk_level": "medium"
            },
            "cultural_context": None
        }
        
        response = client.post(
            "/chat",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["has_dissonance_context"] is True

