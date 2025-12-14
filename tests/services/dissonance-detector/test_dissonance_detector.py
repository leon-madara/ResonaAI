"""
Unit tests for Dissonance Detector Service
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from datetime import datetime

# Store original working directory
original_cwd = os.getcwd()


class TestDissonanceDetector:
    """Test Dissonance Detector service endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client with mocked dependencies"""
        # Change to service directory for imports
        service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'apps', 'backend', 'services', 'dissonance-detector'))
        old_cwd = os.getcwd()
        os.chdir(service_dir)
        
        try:
            # Add service directory to Python path
            if service_dir not in sys.path:
                sys.path.insert(0, service_dir)
            
            # Clear cached modules to avoid conflicts - be selective
            modules_to_remove = []
            for mod_name in list(sys.modules.keys()):
                # Only remove modules that could conflict with this service
                if mod_name == 'main' or mod_name == 'config':
                    modules_to_remove.append(mod_name)
                elif mod_name.startswith('models.dissonance') or mod_name.startswith('services.sentiment') or mod_name.startswith('services.dissonance'):
                    modules_to_remove.append(mod_name)
            for mod in modules_to_remove:
                del sys.modules[mod]
            
            with patch('main.sentiment_analyzer') as mock_sentiment, \
                 patch('main.dissonance_calculator') as mock_calculator:
                
                # Mock sentiment analyzer
                mock_sentiment._model_loaded = True
                mock_sentiment.load_model = AsyncMock()
                mock_sentiment.analyze = AsyncMock(return_value={
                    "label": "positive",
                    "score": 0.75,
                    "valence": 0.75
                })
                
                # Mock dissonance calculator
                mock_calculator.calculate = Mock(return_value={
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
                    }
                })
                
                from main import app
                yield TestClient(app)
        finally:
            os.chdir(old_cwd)
            if service_dir in sys.path:
                sys.path.remove(service_dir)
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
        assert data["service"] == "dissonance-detector"
        assert "model_loaded" in data
    
    def test_analyze_dissonance_success(self, client, auth_token):
        """Test successful dissonance analysis"""
        request_data = {
            "transcript": "I'm fine, everything is okay",
            "voice_emotion": {
                "emotion": "sad",
                "confidence": 0.85
            },
            "session_id": "test-session",
            "user_id": "test-user"
        }
        
        response = client.post(
            "/analyze",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["dissonance_level"] == "high"
        assert data["dissonance_score"] == 0.82
        assert data["stated_emotion"] == "positive"
        assert data["actual_emotion"] == "negative"
        assert data["interpretation"] == "defensive_concealment"
        assert data["risk_level"] == "medium-high"
        assert "timestamp" in data
        assert "details" in data
    
    def test_analyze_dissonance_missing_fields(self, client, auth_token):
        """Test dissonance analysis with missing required fields"""
        # Missing transcript
        response = client.post(
            "/analyze",
            json={
                "voice_emotion": {"emotion": "sad", "confidence": 0.85}
            },
            headers={"Authorization": auth_token}
        )
        assert response.status_code == 422
        
        # Missing voice_emotion
        response = client.post(
            "/analyze",
            json={"transcript": "I'm fine"},
            headers={"Authorization": auth_token}
        )
        assert response.status_code == 422
    
    def test_analyze_dissonance_no_auth(self, client):
        """Test dissonance analysis without authentication"""
        request_data = {
            "transcript": "I'm fine",
            "voice_emotion": {"emotion": "sad", "confidence": 0.85}
        }
        
        response = client.post("/analyze", json=request_data)
        assert response.status_code == 403
    
    def test_analyze_dissonance_low_dissonance(self, client, auth_token):
        """Test dissonance analysis with low dissonance (authentic)"""
        with patch('main.sentiment_analyzer') as mock_sentiment, \
             patch('main.dissonance_calculator') as mock_calculator:
            
            mock_sentiment.analyze = AsyncMock(return_value={
                "label": "positive",
                "score": 0.70,
                "valence": 0.70
            })
            
            mock_calculator.calculate = Mock(return_value={
                "dissonance_level": "low",
                "dissonance_score": 0.15,
                "stated_emotion": "positive",
                "actual_emotion": "positive",
                "interpretation": "authentic",
                "risk_level": "low",
                "confidence": 0.90,
                "details": {
                    "sentiment_score": 0.70,
                    "emotion_score": 0.65,
                    "gap": 0.05,
                    "normalized_gap": 0.15
                }
            })
            
            from main import app
            test_client = TestClient(app)
            
            request_data = {
                "transcript": "I'm feeling great today",
                "voice_emotion": {"emotion": "happy", "confidence": 0.90}
            }
            
            response = test_client.post(
                "/analyze",
                json=request_data,
                headers={"Authorization": auth_token}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["dissonance_level"] == "low"
            assert data["interpretation"] == "authentic"
    
    def test_analyze_dissonance_error_handling(self, client, auth_token):
        """Test error handling in dissonance analysis"""
        with patch('main.sentiment_analyzer') as mock_sentiment:
            mock_sentiment.analyze = AsyncMock(side_effect=Exception("Analysis failed"))
            
            from main import app
            test_client = TestClient(app)
            
            request_data = {
                "transcript": "I'm fine",
                "voice_emotion": {"emotion": "sad", "confidence": 0.85}
            }
            
            response = test_client.post(
                "/analyze",
                json=request_data,
                headers={"Authorization": auth_token}
            )
            
            assert response.status_code == 500
            assert "failed" in response.json()["detail"].lower()
    
    def test_analyze_dissonance_with_timestamp(self, client, auth_token):
        """Test dissonance analysis with custom timestamp"""
        request_data = {
            "transcript": "I'm fine",
            "voice_emotion": {"emotion": "sad", "confidence": 0.85},
            "timestamp": "2025-12-12T12:00:00"
        }
        
        response = client.post(
            "/analyze",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data

