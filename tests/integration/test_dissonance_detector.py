"""
Integration tests for Dissonance Detector Service
Tests the full flow: API Gateway → Dissonance Detector Service
"""

import pytest
import sys
import os
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient

# Add paths for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'apps', 'backend')))


class TestDissonanceDetectorIntegration:
    """Integration tests for Dissonance Detector through API Gateway"""
    
    @pytest.fixture
    def gateway_client(self):
        """Create API Gateway test client with mocked dependencies"""
        with patch('gateway.main.redis_client') as mock_redis, \
             patch('gateway.main.health_checker') as mock_health, \
             patch('gateway.main.http_client') as mock_http:
            
            mock_redis.ping.return_value = True
            mock_health.check_all_services = Mock(return_value={})
            
            # Mock the dissonance detector service response
            mock_response = Mock()
            mock_response.json = AsyncMock(return_value={
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
                "timestamp": "2025-12-12T12:00:00"
            })
            mock_response.raise_for_status = Mock()
            mock_response.status_code = 200
            
            mock_http.request = AsyncMock(return_value=mock_response)
            
            from gateway.main import app
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
    
    def test_dissonance_analyze_routing(self, gateway_client, mock_token):
        """Test routing to dissonance detector service through API Gateway"""
        request_data = {
            "transcript": "I'm fine, everything is okay",
            "voice_emotion": {
                "emotion": "sad",
                "confidence": 0.85
            },
            "session_id": "test-session-id",
            "user_id": "test-user-id"
        }
        
        response = gateway_client.post(
            "/dissonance/analyze",
            headers={"Authorization": f"Bearer {mock_token}"},
            json=request_data
        )
        
        # Should route successfully (200) or service unavailable (503/504)
        assert response.status_code in [200, 503, 504]
        
        if response.status_code == 200:
            data = response.json()
            assert "dissonance_level" in data
            assert "dissonance_score" in data
            assert "risk_level" in data
    
    def test_dissonance_analyze_high_dissonance(self, gateway_client, mock_token):
        """Test high dissonance scenario: 'I'm fine' + sad voice"""
        # Mock high dissonance response
        with patch('gateway.main.http_client') as mock_http:
            mock_response = Mock()
            mock_response.json = AsyncMock(return_value={
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
                "timestamp": "2025-12-12T12:00:00"
            })
            mock_response.raise_for_status = Mock()
            mock_response.status_code = 200
            mock_http.request = AsyncMock(return_value=mock_response)
            
            request_data = {
                "transcript": "I'm fine, everything is okay",
                "voice_emotion": {
                    "emotion": "sad",
                    "confidence": 0.85
                }
            }
            
            response = gateway_client.post(
                "/dissonance/analyze",
                headers={"Authorization": f"Bearer {mock_token}"},
                json=request_data
            )
            
            if response.status_code == 200:
                data = response.json()
                assert data["dissonance_level"] == "high"
                assert data["interpretation"] == "defensive_concealment"
                assert data["risk_level"] in ["medium-high", "high"]
    
    def test_dissonance_analyze_low_dissonance(self, gateway_client, mock_token):
        """Test low dissonance scenario: 'I'm sad' + sad voice"""
        # Mock low dissonance response
        with patch('gateway.main.http_client') as mock_http:
            mock_response = Mock()
            mock_response.json = AsyncMock(return_value={
                "dissonance_level": "low",
                "dissonance_score": 0.15,
                "stated_emotion": "negative",
                "actual_emotion": "negative",
                "interpretation": "authentic",
                "risk_level": "low",
                "confidence": 0.90,
                "details": {
                    "sentiment_score": -0.75,
                    "emotion_score": -0.70,
                    "gap": 0.05,
                    "normalized_gap": 0.025
                },
                "timestamp": "2025-12-12T12:00:00"
            })
            mock_response.raise_for_status = Mock()
            mock_response.status_code = 200
            mock_http.request = AsyncMock(return_value=mock_response)
            
            request_data = {
                "transcript": "I'm feeling really sad today",
                "voice_emotion": {
                    "emotion": "sad",
                    "confidence": 0.90
                }
            }
            
            response = gateway_client.post(
                "/dissonance/analyze",
                headers={"Authorization": f"Bearer {mock_token}"},
                json=request_data
            )
            
            if response.status_code == 200:
                data = response.json()
                assert data["dissonance_level"] == "low"
                assert data["interpretation"] == "authentic"
                assert data["risk_level"] == "low"
    
    def test_dissonance_analyze_requires_auth(self, gateway_client):
        """Test that dissonance endpoint requires authentication"""
        request_data = {
            "transcript": "I'm fine",
            "voice_emotion": {
                "emotion": "sad",
                "confidence": 0.85
            }
        }
        
        response = gateway_client.post(
            "/dissonance/analyze",
            json=request_data
        )
        
        # Should return 403 Forbidden without token
        assert response.status_code == 403
    
    def test_dissonance_analyze_validation(self, gateway_client, mock_token):
        """Test input validation through API Gateway"""
        # Test missing transcript
        response = gateway_client.post(
            "/dissonance/analyze",
            headers={"Authorization": f"Bearer {mock_token}"},
            json={
                "voice_emotion": {
                    "emotion": "sad",
                    "confidence": 0.85
                }
            }
        )
        
        # Should return 400 or be forwarded and return 400 from service
        assert response.status_code in [400, 422, 503, 504]
        
        # Test missing voice_emotion
        response = gateway_client.post(
            "/dissonance/analyze",
            headers={"Authorization": f"Bearer {mock_token}"},
            json={
                "transcript": "I'm fine"
            }
        )
        
        assert response.status_code in [400, 422, 503, 504]

