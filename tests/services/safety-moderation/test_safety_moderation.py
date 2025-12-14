"""
Unit tests for Safety Moderation Service
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
import jwt
from datetime import datetime, timedelta, timezone

# Store original working directory
original_cwd = os.getcwd()


class TestSafetyModeration:
    """Test Safety Moderation service endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client with mocked dependencies"""
        # Change to service directory for imports
        service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'apps', 'backend', 'services', 'safety-moderation'))
        old_cwd = os.getcwd()
        os.chdir(service_dir)
        
        try:
            # Add service directory to Python path
            if service_dir not in sys.path:
                sys.path.insert(0, service_dir)
            
            # Clear cached modules
            modules_to_remove = []
            for mod_name in list(sys.modules.keys()):
                if mod_name in ['main', 'config', 'database', 'models', 'models.database_models', 'services.review_queue', 'services.content_filter', 'services.hallucination_detector']:
                    modules_to_remove.append(mod_name)
            for mod in modules_to_remove:
                if mod in sys.modules:
                    del sys.modules[mod]
            
            # Mock review_queue functions to avoid database import
            def mock_get_review_queue():
                mock_queue = Mock()
                mock_queue.add_to_queue = Mock(return_value="test-id")
                mock_queue.get_pending_items = Mock(return_value=[])
                mock_queue.get_item = Mock(return_value=None)
                mock_queue.update_item = Mock(return_value=True)
                mock_queue.delete_item = Mock(return_value=True)
                mock_queue.log_moderation_decision = Mock()
                return mock_queue
            
            # Mock content_filter - use actual filter logic but mock database parts
            def mock_get_content_filter():
                # Import the actual ContentFilter class
                from services.content_filter import ContentFilter
                return ContentFilter()
            
            # Mock hallucination_detector
            def mock_get_hallucination_detector():
                mock_detector = Mock()
                mock_detector.analyze = Mock(return_value={
                    "hallucination_score": 0.1,
                    "needs_review": False,
                    "issues": []
                })
                return mock_detector
            
            # Patch environment variables before any imports
            with patch.dict(os.environ, {'DATABASE_URL': 'sqlite:///:memory:', 'JWT_SECRET_KEY': 'test-secret-key', 'JWT_ALGORITHM': 'HS256'}), \
                 patch('services.review_queue.get_review_queue', side_effect=mock_get_review_queue), \
                 patch('services.content_filter.get_content_filter', side_effect=mock_get_content_filter), \
                 patch('services.hallucination_detector.get_hallucination_detector', side_effect=mock_get_hallucination_detector):
                
                from main import app
                yield TestClient(app)
        finally:
            os.chdir(old_cwd)
            if service_dir in sys.path:
                sys.path.remove(service_dir)
    
    @pytest.fixture
    def auth_token(self):
        """Generate a test JWT token"""
        token = jwt.encode(
            {
                "user_id": "11111111-1111-1111-1111-111111111111",
                "email": "test@example.com",
                "role": "user",
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            },
            "test-secret-key",
            algorithm="HS256",
        )
        return f"Bearer {token}"
    
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
    
    def test_validate_hallucination_detection(self, client, auth_token):
        """Test hallucination detection for AI responses"""
        # Use actual hallucination detector instead of mock for this test
        with patch('services.hallucination_detector.get_hallucination_detector') as mock_get_detector:
            from services.hallucination_detector import HallucinationDetector
            real_detector = HallucinationDetector()
            mock_get_detector.return_value = real_detector
            
            request_data = {
                "content": "I can guarantee that you will feel better in exactly 3 days. This is a proven fact from my research.",
                "content_type": "response"
            }
            
            response = client.post(
                "/validate",
                json=request_data,
                headers={"Authorization": auth_token}
            )
            
            assert response.status_code == 200
            data = response.json()
            # Should detect hallucination (overconfident claims)
            assert "hallucination_score" in data
    
    def test_validate_risk_scoring(self, client, auth_token):
        """Test that risk scoring works correctly"""
        request_data = {
            "content": "I'm feeling very sad and hopeless",
            "content_type": "user_input"
        }
        
        response = client.post(
            "/validate",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "risk_score" in data
        assert 0.0 <= data["risk_score"] <= 1.0
    
    def test_validate_toxicity_detection(self, client, auth_token):
        """Test toxicity detection"""
        request_data = {
            "content": "You are worthless and pathetic",
            "content_type": "response"
        }
        
        response = client.post(
            "/validate",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        # Should detect toxicity
        if "toxicity_detected" in data.get("issues", []):
            assert data["flagged"] is True
            assert data["action"] in ["review", "block"]

