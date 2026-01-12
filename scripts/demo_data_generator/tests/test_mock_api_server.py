"""
Tests for Mock API Server

This module contains tests for the MockAPIServer implementation.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock

from ..api.mock_api_server import MockAPIServer
from ..models import ServiceConfig


class TestMockAPIServer:
    """Test cases for MockAPIServer"""
    
    @pytest.fixture
    def mock_storage(self):
        """Create a mock storage interface"""
        storage = Mock()
        storage.load_data.return_value = {
            "users": [{
                "id": "test_user",
                "profile": {
                    "age": 25,
                    "gender": "female",
                    "location": "Nairobi, Kenya"
                },
                "baseline_data": {
                    "voice_patterns": {
                        "average_pitch": 180.5,
                        "speech_rate": 145.2
                    }
                }
            }],
            "conversations": [{
                "id": "conv_001",
                "user_id": "test_user",
                "messages": []
            }]
        }
        return storage
    
    @pytest.fixture
    def api_server(self, mock_storage):
        """Create MockAPIServer instance"""
        return MockAPIServer(mock_storage)
    
    @pytest.fixture
    def client(self, api_server):
        """Create test client"""
        return TestClient(api_server.app)
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "demo-api"
        assert "timestamp" in data
    
    def test_login_endpoint(self, client):
        """Test login endpoint"""
        response = client.post("/auth/login", json={
            "username": "test_user",
            "password": "test_password"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "demo_token"
        assert data["token_type"] == "bearer"
    
    def test_register_endpoint(self, client):
        """Test registration endpoint"""
        response = client.post("/auth/register", json={
            "username": "new_user",
            "email": "test@example.com",
            "password": "test_password"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "demo_token"
    
    def test_current_user_endpoint(self, client):
        """Test get current user endpoint"""
        headers = {"Authorization": "Bearer demo_token"}
        response = client.get("/users/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "profile" in data
    
    def test_chat_endpoint(self, client):
        """Test chat endpoint"""
        headers = {"Authorization": "Bearer demo_token"}
        response = client.post("/conversation/chat", 
            headers=headers,
            json={
                "message": "I'm feeling stressed about my exams",
                "user_id": "test_user"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "response" in data["data"]
    
    def test_emotion_analysis_endpoint(self, client):
        """Test emotion analysis endpoint"""
        headers = {"Authorization": "Bearer demo_token"}
        response = client.post("/emotion-analysis/analyze",
            headers=headers,
            json={
                "text": "I'm feeling very sad today",
                "user_id": "test_user",
                "include_voice_analysis": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "emotion_result" in data
        assert data["emotion_result"]["detected"] == "sad"
    
    def test_cultural_context_endpoint(self, client):
        """Test cultural context endpoint"""
        headers = {"Authorization": "Bearer demo_token"}
        response = client.get("/cultural-context/context?query=nimechoka sana",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "cultural_context" in data
        assert "nimechoka" in data["cultural_context"]["patterns"]
    
    def test_dissonance_analysis_endpoint(self, client):
        """Test voice-truth dissonance analysis endpoint"""
        headers = {"Authorization": "Bearer demo_token"}
        response = client.post("/dissonance-detector/analyze",
            headers=headers,
            json={
                "text": "I'm fine, everything is okay",
                "user_id": "test_user"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "dissonance_result" in data
    
    def test_safety_validation_endpoint(self, client):
        """Test safety content validation endpoint"""
        headers = {"Authorization": "Bearer demo_token"}
        response = client.post("/safety-moderation/validate",
            headers=headers,
            json={
                "text": "I want to kill myself"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["safe"] is False
        assert data["data"]["crisis_level"] == "high"
        assert data["data"]["intervention_required"] is True
    
    def test_baseline_endpoints(self, client):
        """Test baseline tracker endpoints"""
        headers = {"Authorization": "Bearer demo_token"}
        
        # Test get baseline
        response = client.get("/baseline-tracker/baseline/test_user", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "voice_patterns" in data["data"]
        
        # Test update baseline
        response = client.post("/baseline-tracker/baseline/update",
            headers=headers,
            json={"emotion": "happy", "confidence": 0.9}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_server_lifecycle(self, api_server):
        """Test server start/stop lifecycle"""
        config = ServiceConfig(
            mock_api_port=8001,
            processing_delay_ms=100
        )
        
        # Test start server
        result = api_server.start_server(config)
        assert result is True
        
        # Test get server info
        info = api_server.get_server_info()
        assert info.port == 8001
        assert info.name == "mock-api-server"
        
        # Test stop server
        result = api_server.stop_server()
        assert result is True
    
    def test_processing_delay_simulation(self, api_server):
        """Test processing delay simulation"""
        config = ServiceConfig(processing_delay_ms=500)
        api_server.config = config
        
        # Test different endpoint delays
        delay = api_server.simulate_processing_delay("/emotion-analysis/analyze")
        assert delay > 0
        
        delay = api_server.simulate_processing_delay("/unknown-endpoint")
        assert delay >= 0