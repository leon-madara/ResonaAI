"""
Unit tests for Crisis Detection Service
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from datetime import datetime

# Store original working directory
original_cwd = os.getcwd()


class TestCrisisDetection:
    """Test Crisis Detection service endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client with mocked dependencies"""
        # Change to service directory for imports
        service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'services', 'crisis-detection'))
        old_cwd = os.getcwd()
        os.chdir(service_dir)
        
        try:
            # Add service directory to Python path
            if service_dir not in sys.path:
                sys.path.insert(0, service_dir)
            
            # Clear cached modules
            for mod_name in list(sys.modules.keys()):
                if mod_name in ['main', 'config'] or mod_name.startswith('models.crisis'):
                    del sys.modules[mod_name]
            
            with patch('main.risk_calculator') as mock_calculator:
                mock_calculator.calculate_risk = Mock(return_value={
                    "risk_level": "medium",
                    "risk_score": 0.65,
                    "crisis_detected": False,
                    "detection_methods": ["emotion", "keyword"],
                    "escalation_required": False,
                    "recommended_action": "monitor"
                })
                
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
        assert data["service"] == "crisis-detection"
    
    def test_detect_crisis_low_risk(self, client, auth_token):
        """Test crisis detection with low risk"""
        request_data = {
            "user_id": "test-user",
            "transcript": "I'm feeling okay today",
            "emotion_data": {
                "emotion": "neutral",
                "confidence": 0.70
            },
            "dissonance_data": None,
            "baseline_data": None
        }
        
        response = client.post(
            "/detect",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["risk_level"] == "medium"
        assert data["crisis_detected"] is False
        assert "detection_methods" in data
        assert "recommended_action" in data
        assert "timestamp" in data
        assert "details" in data
    
    def test_detect_crisis_high_risk(self, client, auth_token):
        """Test crisis detection with high risk"""
        with patch('main.risk_calculator') as mock_calculator:
            mock_calculator.calculate_risk = Mock(return_value={
                "risk_level": "critical",
                "risk_score": 0.95,
                "crisis_detected": True,
                "detection_methods": ["keyword", "emotion", "dissonance"],
                "escalation_required": True,
                "recommended_action": "emergency"
            })
            
            from main import app
            test_client = TestClient(app)
            
            request_data = {
                "user_id": "test-user",
                "transcript": "I want to end it all",
                "emotion_data": {
                    "emotion": "sad",
                    "confidence": 0.95
                },
                "dissonance_data": {
                    "dissonance_level": "high",
                    "risk_level": "high"
                },
                "baseline_data": {
                    "deviation_detected": True,
                    "deviation_score": 0.85
                }
            }
            
            response = test_client.post(
                "/detect",
                json=request_data,
                headers={"Authorization": auth_token}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["risk_level"] == "critical"
            assert data["crisis_detected"] is True
            assert data["escalation_required"] is True
            assert data["recommended_action"] == "emergency"
    
    def test_detect_crisis_with_all_data(self, client, auth_token):
        """Test crisis detection with all data sources"""
        request_data = {
            "user_id": "test-user",
            "session_id": "session-123",
            "conversation_id": "conv-456",
            "transcript": "I'm struggling",
            "emotion_data": {
                "emotion": "sad",
                "confidence": 0.85
            },
            "dissonance_data": {
                "dissonance_level": "medium",
                "risk_level": "medium"
            },
            "baseline_data": {
                "deviation_detected": True,
                "deviation_score": 0.60
            }
        }
        
        response = client.post(
            "/detect",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "details" in data
        assert data["details"]["user_id"] == "test-user"
        assert data["details"]["session_id"] == "session-123"
        assert data["details"]["conversation_id"] == "conv-456"
    
    def test_detect_crisis_missing_transcript(self, client, auth_token):
        """Test crisis detection with missing transcript"""
        request_data = {
            "user_id": "test-user",
            "emotion_data": {"emotion": "sad"}
        }
        
        response = client.post(
            "/detect",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 422
    
    def test_detect_crisis_no_auth(self, client):
        """Test crisis detection without authentication"""
        request_data = {
            "user_id": "test-user",
            "transcript": "I'm feeling down"
        }
        
        response = client.post("/detect", json=request_data)
        assert response.status_code == 403
    
    def test_escalate_crisis(self, client, auth_token):
        """Test crisis escalation"""
        request_data = {
            "user_id": "test-user",
            "risk_level": "critical",
            "escalation_type": "emergency",
            "reason": "High risk detected"
        }
        
        response = client.post(
            "/escalate",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "escalation_id" in data
        assert data["status"] == "initiated"
        assert "action_taken" in data
        assert "timestamp" in data
    
    def test_escalate_crisis_different_types(self, client, auth_token):
        """Test different escalation types"""
        escalation_types = ["emergency", "human_review", "monitoring"]
        
        for esc_type in escalation_types:
            request_data = {
                "user_id": "test-user",
                "risk_level": "high",
                "escalation_type": esc_type,
                "reason": f"Escalating via {esc_type}"
            }
            
            response = client.post(
                "/escalate",
                json=request_data,
                headers={"Authorization": auth_token}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert esc_type in data["action_taken"].lower()
    
    def test_escalate_crisis_no_auth(self, client):
        """Test escalation without authentication"""
        request_data = {
            "user_id": "test-user",
            "risk_level": "high",
            "escalation_type": "emergency"
        }
        
        response = client.post("/escalate", json=request_data)
        assert response.status_code == 403
    
    def test_detect_crisis_error_handling(self, client, auth_token):
        """Test error handling in crisis detection"""
        with patch('main.risk_calculator') as mock_calculator:
            mock_calculator.calculate_risk = Mock(side_effect=Exception("Calculation failed"))
            
            from main import app
            test_client = TestClient(app)
            
            request_data = {
                "user_id": "test-user",
                "transcript": "I'm feeling down"
            }
            
            response = test_client.post(
                "/detect",
                json=request_data,
                headers={"Authorization": auth_token}
            )
            
            assert response.status_code == 500
            assert "failed" in response.json()["detail"].lower()
    
    def test_detect_crisis_medium_risk(self, client, auth_token):
        """Test crisis detection with medium risk"""
        with patch('main.risk_calculator') as mock_calculator:
            mock_calculator.calculate_risk = Mock(return_value={
                "risk_level": "medium",
                "risk_score": 0.70,
                "crisis_detected": True,
                "detection_methods": ["emotion", "dissonance"],
                "escalation_required": True,
                "recommended_action": "review"
            })
            
            from main import app
            test_client = TestClient(app)
            
            request_data = {
                "user_id": "test-user",
                "transcript": "I'm having a hard time",
                "emotion_data": {"emotion": "sad", "confidence": 0.80},
                "dissonance_data": {"dissonance_level": "medium"}
            }
            
            response = test_client.post(
                "/detect",
                json=request_data,
                headers={"Authorization": auth_token}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["risk_level"] == "medium"
            assert data["crisis_detected"] is True
            assert data["escalation_required"] is True

