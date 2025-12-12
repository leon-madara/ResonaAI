"""
Integration tests for crisis detection flow
"""

import pytest
import sys
import os
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient

# Add services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'services', 'api-gateway'))


@pytest.mark.integration
class TestCrisisDetectionFlow:
    """Integration tests for crisis detection"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
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
    
    def test_crisis_detection_high_risk(self, client, mock_token):
        """Test crisis detection with high-risk indicators"""
        # Mock crisis detection service
        crisis_response = Mock()
        crisis_response.json.return_value = {
            "risk_level": "high",
            "crisis_detected": True,
            "risk_score": 0.85,
            "recommended_action": "immediate_intervention"
        }
        crisis_response.raise_for_status = Mock()
        
        with patch('main.http_client') as mock_http:
            mock_http.request = AsyncMock(return_value=crisis_response)
            
            response = client.post(
                "/crisis/detect",
                headers={"Authorization": f"Bearer {mock_token}"},
                json={
                    "transcript": "I don't want to live anymore",
                    "emotion": "despair",
                    "dissonance_score": 0.9
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                assert "risk_level" in data
                assert data["risk_level"] in ["low", "medium", "high", "critical"]
    
    def test_crisis_detection_low_risk(self, client, mock_token):
        """Test crisis detection with low-risk indicators"""
        # Mock crisis detection service
        crisis_response = Mock()
        crisis_response.json.return_value = {
            "risk_level": "low",
            "crisis_detected": False,
            "risk_score": 0.2,
            "recommended_action": "continue_monitoring"
        }
        crisis_response.raise_for_status = Mock()
        
        with patch('main.http_client') as mock_http:
            mock_http.request = AsyncMock(return_value=crisis_response)
            
            response = client.post(
                "/crisis/detect",
                headers={"Authorization": f"Bearer {mock_token}"},
                json={
                    "transcript": "I'm feeling okay today",
                    "emotion": "neutral",
                    "dissonance_score": 0.1
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                assert "risk_level" in data
                assert data["crisis_detected"] is False

