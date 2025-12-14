"""
Unit tests for Baseline Tracker Service
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from datetime import datetime
from uuid import uuid4

# Store original working directory
original_cwd = os.getcwd()


class TestBaselineTracker:
    """Test Baseline Tracker service endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client with mocked dependencies"""
        # Change to service directory for imports
        service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'apps', 'backend', 'services', 'baseline-tracker'))
        old_cwd = os.getcwd()
        os.chdir(service_dir)
        
        try:
            # Add service directory to Python path
            if service_dir not in sys.path:
                sys.path.insert(0, service_dir)
            
            # Clear cached modules
            modules_to_remove = []
            for mod_name in list(sys.modules.keys()):
                if mod_name in ['main', 'config', 'database'] or mod_name.startswith('models.baseline') or mod_name.startswith('repositories'):
                    modules_to_remove.append(mod_name)
            for mod in modules_to_remove:
                if mod in sys.modules:
                    del sys.modules[mod]
            
            # Mock database module before importing main
            from sqlalchemy.orm import Session
            mock_db_session = Mock(spec=Session)
            
            def mock_get_db():
                """Mock database session generator"""
                yield mock_db_session
            
            mock_db_module = Mock()
            mock_db_module.get_db = mock_get_db
            mock_db_module.init_db = Mock()
            
            # Patch database module before import
            with patch.dict('sys.modules', {'database': mock_db_module}), \
                 patch('main.baseline_calculator') as mock_calculator, \
                 patch('main.deviation_detector') as mock_detector, \
                 patch('main.BaselineRepository') as mock_repo_class:
                
                # Mock repository methods
                mock_repo = Mock()
                mock_repo.get_historical_voice_features = Mock(return_value=[])
                mock_repo.get_historical_emotions = Mock(return_value=[])
                mock_repo.save_user_baseline = Mock()
                mock_repo.save_deviation = Mock()
                mock_repo.get_user_baselines = Mock(return_value=[])
                
                # Mock baseline object with baseline_value attribute
                mock_voice_baseline = Mock()
                mock_voice_baseline.baseline_value = {"pitch_mean": 150.0, "pitch_std": 20.0}
                mock_emotion_baseline = Mock()
                mock_emotion_baseline.baseline_value = {"emotion": "neutral", "confidence": 0.8}
                
                def get_user_baseline_side_effect(user_id, baseline_type):
                    if baseline_type == "voice":
                        return mock_voice_baseline
                    elif baseline_type == "emotion":
                        return mock_emotion_baseline
                    return None
                
                mock_repo.get_user_baseline = Mock(side_effect=get_user_baseline_side_effect)
                mock_repo_class.return_value = mock_repo
                
                # Mock calculator methods
                mock_calculator.filter_recent_data = Mock(side_effect=lambda data, days: data)
                mock_calculator.calculate_voice_baseline = Mock(return_value={
                    "pitch_mean": 150.0,
                    "pitch_std": 20.0,
                    "energy_mean": 0.5,
                    "energy_std": 0.1,
                    "speech_rate": 3.5,
                    "pause_frequency": 0.2,
                    "sample_count": 10
                })
                mock_calculator.calculate_emotion_baseline = Mock(return_value={
                    "emotion_distribution": {"neutral": 1.0},
                    "average_confidence": 0.8,
                    "dominant_emotion": "neutral",
                    "sample_count": 10
                })
                
                # Mock detector methods - return dicts that match what the code expects
                mock_detector.detect_voice_deviation = Mock(return_value={
                    "deviation_score": 0.5,
                    "deviation_detected": True
                })
                mock_detector.detect_emotion_deviation = Mock(return_value={
                    "deviation_score": 0.6,
                    "deviation_detected": True
                })
                mock_detector.calculate_severity = Mock(return_value="medium")
                
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
        test_user_id = str(uuid4())
        request_data = {
            "user_id": test_user_id,
            "voice_features": {
                "pitch_mean": 150.0,
                "pitch_std": 20.0,
                "energy_mean": 0.5,
                "energy_std": 0.1,
                "speech_rate": 3.5,
                "pause_frequency": 0.2,
                "duration": 5.0
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
        assert data["user_id"] == test_user_id
        assert data["voice_fingerprint"] is not None
        assert data["voice_fingerprint"]["user_id"] == test_user_id
        assert "confidence" in data["voice_fingerprint"]
        assert "calculated_at" in data["voice_fingerprint"]
    
    def test_update_baseline_with_emotion_data(self, client, auth_token):
        """Test baseline update with emotion data"""
        test_user_id = str(uuid4())
        request_data = {
            "user_id": test_user_id,
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
        assert data["user_id"] == test_user_id
        assert data["emotion_baseline"] is not None
        assert data["emotion_baseline"]["user_id"] == test_user_id
        assert "dominant_emotion" in data["emotion_baseline"]
        assert "baseline_period_days" in data["emotion_baseline"]
    
    def test_update_baseline_with_both(self, client, auth_token):
        """Test baseline update with both voice and emotion data"""
        test_user_id = str(uuid4())
        request_data = {
            "user_id": test_user_id,
            "voice_features": {
                "pitch_mean": 150.0,
                "pitch_std": 20.0,
                "energy_mean": 0.5,
                "energy_std": 0.1,
                "speech_rate": 3.5,
                "pause_frequency": 0.2,
                "duration": 5.0
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
        test_user_id = str(uuid4())
        request_data = {
            "user_id": test_user_id,
            "voice_features": {
                "pitch_mean": 150.0,
                "pitch_std": 20.0,
                "energy_mean": 0.5,
                "energy_std": 0.1,
                "speech_rate": 3.5,
                "pause_frequency": 0.2,
                "duration": 5.0
            }
        }
        
        response = client.post("/baseline/update", json=request_data)
        assert response.status_code == 403
    
    def test_get_baseline(self, client, auth_token):
        """Test getting baseline for a user"""
        test_user_id = str(uuid4())
        
        response = client.get(
            f"/baseline/{test_user_id}",
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_user_id
        assert "message" in data
    
    def test_get_baseline_no_auth(self, client):
        """Test getting baseline without authentication"""
        test_user_id = str(uuid4())
        response = client.get(f"/baseline/{test_user_id}")
        assert response.status_code == 403
    
    def test_check_deviation(self, client, auth_token):
        """Test checking for deviations from baseline"""
        test_user_id = str(uuid4())
        request_data = {
            "user_id": test_user_id,
            "voice_features": {
                "pitch_mean": 200.0,  # Different from baseline
                "pitch_std": 30.0,
                "energy_mean": 0.6,
                "energy_std": 0.15,
                "speech_rate": 4.0,
                "pause_frequency": 0.3,
                "duration": 5.0
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
        assert data["user_id"] == test_user_id
        assert "deviation_type" in data
        assert "deviation_score" in data
        assert "severity" in data
        assert "timestamp" in data
    
    def test_check_deviation_no_auth(self, client):
        """Test deviation check without authentication"""
        test_user_id = str(uuid4())
        request_data = {
            "user_id": test_user_id,
            "voice_features": {
                "pitch_mean": 200.0,
                "pitch_std": 30.0,
                "energy_mean": 0.6,
                "energy_std": 0.15,
                "speech_rate": 4.0,
                "pause_frequency": 0.3,
                "duration": 5.0
            }
        }
        
        response = client.post("/baseline/check-deviation", json=request_data)
        assert response.status_code == 403
    
    def test_update_baseline_error_handling(self, client, auth_token):
        """Test error handling in baseline update"""
        test_user_id = str(uuid4())
        with patch('main.logger') as mock_logger:
            # Simulate an error
            request_data = {
                "user_id": test_user_id,
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

