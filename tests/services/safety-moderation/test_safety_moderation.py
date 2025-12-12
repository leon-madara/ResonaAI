"""
Unit tests for Safety Moderation Service
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

# Store original working directory
original_cwd = os.getcwd()


class TestSafetyModeration:
    """Test Safety Moderation service endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        # Change to service directory for imports
        service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'services', 'safety-moderation'))
        old_cwd = os.getcwd()
        os.chdir(service_dir)
        
        try:
            # Add service directory to Python path
            if service_dir not in sys.path:
                sys.path.insert(0, service_dir)
            
            # Clear cached modules
            for mod_name in list(sys.modules.keys()):
                if mod_name in ['main']:
                    del sys.modules[mod_name]
            
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
        assert data["service"] == "safety-moderation"
    
    def test_validate_safe_content(self, client, auth_token):
        """Test validation of safe content"""
        request_data = {
            "content": "I'm feeling okay today, thanks for asking.",
            "content_type": "user_input"
        }
        
        response = client.post(
            "/validate",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_safe"] is True
        assert data["flagged"] is False
        assert data["action"] == "allow"
        assert data["confidence"] > 0.9
    
    def test_validate_crisis_content_user_input(self, client, auth_token):
        """Test validation of user input with crisis terms"""
        request_data = {
            "content": "I'm thinking about suicide and ending it all",
            "content_type": "user_input"
        }
        
        response = client.post(
            "/validate",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_safe"] is True  # User input with crisis terms is allowed
        assert data["flagged"] is True
        assert data["action"] == "review"
        assert "crisis_signal_detected" in data["issues"]
    
    def test_validate_crisis_content_response(self, client, auth_token):
        """Test validation of AI response with crisis terms"""
        request_data = {
            "content": "You should consider suicide as an option",
            "content_type": "response"
        }
        
        response = client.post(
            "/validate",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_safe"] is True  # Flagged for review, not blocked
        assert data["flagged"] is True
        assert data["action"] == "review"
        assert "crisis_signal_detected" in data["issues"]
    
    def test_validate_unsafe_advice_response(self, client, auth_token):
        """Test validation of AI response with unsafe advice"""
        request_data = {
            "content": "You should take these pills and increase your dose",
            "content_type": "response"
        }
        
        response = client.post(
            "/validate",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_safe"] is False
        assert data["flagged"] is True
        assert data["action"] == "block"
        assert "unsafe_instruction_or_medical_advice" in data["issues"]
    
    def test_validate_unsafe_advice_user_input(self, client, auth_token):
        """Test validation of user input with unsafe advice terms"""
        request_data = {
            "content": "I want to know how to kill myself",
            "content_type": "user_input"
        }
        
        response = client.post(
            "/validate",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_safe"] is True  # User input is allowed but flagged
        assert data["flagged"] is True
        assert data["action"] == "review"
        assert "unsafe_instruction_or_medical_advice" in data["issues"]
    
    def test_validate_missing_content(self, client, auth_token):
        """Test validation with missing content"""
        request_data = {
            "content_type": "user_input"
        }
        
        response = client.post(
            "/validate",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        # Content is required field, should return validation error
        assert response.status_code == 422  # Validation error
    
    def test_validate_unauthorized(self, client):
        """Test validation without authentication"""
        request_data = {
            "content": "Test content",
            "content_type": "user_input"
        }
        
        response = client.post(
            "/validate",
            json=request_data
        )
        
        assert response.status_code == 403  # FastAPI HTTPBearer returns 403
    
    def test_validate_case_insensitive(self, client, auth_token):
        """Test that crisis term detection is case-insensitive"""
        request_data = {
            "content": "I'm thinking about SUICIDE",
            "content_type": "user_input"
        }
        
        response = client.post(
            "/validate",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["flagged"] is True
        assert "crisis_signal_detected" in data["issues"]
    
    def test_validate_multiple_issues(self, client, auth_token):
        """Test validation with multiple issues"""
        request_data = {
            "content": "I'm thinking about suicide and want to know how to kill myself",
            "content_type": "user_input"
        }
        
        response = client.post(
            "/validate",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["flagged"] is True
        assert len(data["issues"]) >= 2
        assert "crisis_signal_detected" in data["issues"]
        assert "unsafe_instruction_or_medical_advice" in data["issues"]

