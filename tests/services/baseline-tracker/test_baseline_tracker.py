"""
Unit tests for Baseline Tracker Service
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from datetime import datetime

# Store original working directory
original_cwd = os.getcwd()


class TestBaselineTracker:
    """Test Baseline Tracker service endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client with mocked dependencies"""
        # Change to service directory for imports
        service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'services', 'baseline-tracker'))
        old_cwd = os.getcwd()
        os.chdir(service_dir)
        
        try:
            # Add service directory to Python path
            if service_dir not in sys.path:
                sys.path.insert(0, service_dir)
            
            # Clear cached modules
            for mod_name in list(sys.modules.keys()):
                if mod_name in ['main', 'config'] or mod_name.startswith('models.baseline'):
                    del sys.modules[mod_name]
            
            with patch('main.baseline_calculator') as mock_calculator, \
                 patch('main.deviation_detector') as mock_detector:
                
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
        assert data["service"] == "baseline-tracker"
    
    def test_update_baseline_with_voice_features(self, client, auth_token):
        """Test baseline update with voice features"""
        request_data = {
            "user_id": "test-user",
            "voice_features": {
                "pitch_mean": 150.0,
                "pitch_std": 20.0,
                "energy_mean": 0.5,
                "energy_std": 0.1
            },
            "emotion_data": None
        }
        
        response = client.post(
            "/baseline/update",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test-user"
        assert data["voice_fingerprint"] is not None
        assert data["voice_fingerprint"]["user_id"] == "test-user"
        assert "confidence" in data["voice_fingerprint"]
        assert "calculated_at" in data["voice_fingerprint"]
    
    def test_update_baseline_with_emotion_data(self, client, auth_token):
        """Test baseline update with emotion data"""
        request_data = {
            "user_id": "test-user",
            "voice_features": None,
            "emotion_data": {
                "emotion": "neutral",
                "confidence": 0.8
            }
        }
        
        response = client.post(
            "/baseline/update",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test-user"
        assert data["emotion_baseline"] is not None
        assert data["emotion_baseline"]["user_id"] == "test-user"
        assert "dominant_emotion" in data["emotion_baseline"]
        assert "baseline_period_days" in data["emotion_baseline"]
    
    def test_update_baseline_with_both(self, client, auth_token):
        """Test baseline update with both voice and emotion data"""
        request_data = {
            "user_id": "test-user",
            "voice_features": {
                "pitch_mean": 150.0,
                "pitch_std": 20.0
            },
            "emotion_data": {
                "emotion": "happy",
                "confidence": 0.85
            }
        }
        
        response = client.post(
            "/baseline/update",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["voice_fingerprint"] is not None
        assert data["emotion_baseline"] is not None
    
    def test_update_baseline_missing_user_id(self, client, auth_token):
        """Test baseline update with missing user_id"""
        request_data = {
            "voice_features": {"pitch_mean": 150.0}
        }
        
        response = client.post(
            "/baseline/update",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 422
    
    def test_update_baseline_no_auth(self, client):
        """Test baseline update without authentication"""
        request_data = {
            "user_id": "test-user",
            "voice_features": {"pitch_mean": 150.0}
        }
        
        response = client.post("/baseline/update", json=request_data)
        assert response.status_code == 403
    
    def test_get_baseline(self, client, auth_token):
        """Test getting baseline for a user"""
        user_id = "test-user"
        
        response = client.get(
            f"/baseline/{user_id}",
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_id
        assert "message" in data
    
    def test_get_baseline_no_auth(self, client):
        """Test getting baseline without authentication"""
        response = client.get("/baseline/test-user")
        assert response.status_code == 403
    
    def test_check_deviation(self, client, auth_token):
        """Test checking for deviations from baseline"""
        request_data = {
            "user_id": "test-user",
            "voice_features": {
                "pitch_mean": 200.0,  # Different from baseline
                "pitch_std": 30.0
            },
            "emotion_data": {
                "emotion": "sad",
                "confidence": 0.9
            }
        }
        
        response = client.post(
            "/baseline/check-deviation",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test-user"
        assert "deviation_type" in data
        assert "deviation_score" in data
        assert "severity" in data
        assert "timestamp" in data
    
    def test_check_deviation_no_auth(self, client):
        """Test deviation check without authentication"""
        request_data = {
            "user_id": "test-user",
            "voice_features": {"pitch_mean": 200.0}
        }
        
        response = client.post("/baseline/check-deviation", json=request_data)
        assert response.status_code == 403
    
    def test_update_baseline_error_handling(self, client, auth_token):
        """Test error handling in baseline update"""
        with patch('main.logger') as mock_logger:
            # Simulate an error
            request_data = {
                "user_id": "test-user",
                "voice_features": None,
                "emotion_data": None
            }
            
            # This should still work but return a message
            response = client.post(
                "/baseline/update",
                json=request_data,
                headers={"Authorization": auth_token}
            )
            
            # Should return 200 with a message
            assert response.status_code == 200
            data = response.json()
            assert "message" in data

