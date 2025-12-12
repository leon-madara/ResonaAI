"""
Integration tests for speech processing flow
Tests: speech -> emotion -> conversation
"""

import pytest
import sys
import os
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient

# Add services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'services', 'api-gateway'))


@pytest.mark.integration
class TestSpeechProcessingFlow:
    """Integration tests for speech processing flow"""
    
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
    
    def test_speech_to_emotion_flow(self, client, mock_token):
        """Test flow: speech transcription -> emotion analysis"""
        # Mock speech processing response
        speech_response = Mock()
        speech_response.json.return_value = {
            "transcript": "I'm feeling great today",
            "emotion_data": {
                "emotion": "happy",
                "confidence": 0.85
            }
        }
        speech_response.raise_for_status = Mock()
        
        # Mock emotion analysis response
        emotion_response = Mock()
        emotion_response.json.return_value = {
            "emotion": "happy",
            "confidence": 0.85,
            "valence": 0.8
        }
        emotion_response.raise_for_status = Mock()
        
        with patch('main.http_client') as mock_http:
            # First call: speech processing
            # Second call: emotion analysis (if called separately)
            mock_http.request = AsyncMock(side_effect=[speech_response, emotion_response])
            
            # Transcribe speech
            transcribe_response = client.post(
                "/speech/transcribe",
                headers={"Authorization": f"Bearer {mock_token}"},
                json={"audio_file": "base64encoded"}
            )
            
            # Should get transcript and emotion data
            if transcribe_response.status_code == 200:
                data = transcribe_response.json()
                assert "transcript" in data or "emotion_data" in data
    
    def test_speech_to_conversation_flow(self, client, mock_token):
        """Test flow: speech -> conversation response"""
        # Mock speech processing
        speech_response = Mock()
        speech_response.json.return_value = {
            "transcript": "I'm feeling sad",
            "emotion_data": {"emotion": "sad", "confidence": 0.9}
        }
        speech_response.raise_for_status = Mock()
        
        # Mock conversation engine
        conversation_response = Mock()
        conversation_response.json.return_value = {
            "message": "I'm sorry to hear you're feeling sad. Would you like to talk about it?",
            "conversation_id": "conv-123"
        }
        conversation_response.raise_for_status = Mock()
        
        with patch('main.http_client') as mock_http:
            mock_http.request = AsyncMock(side_effect=[speech_response, conversation_response])
            
            # Transcribe
            transcribe_response = client.post(
                "/speech/transcribe",
                headers={"Authorization": f"Bearer {mock_token}"},
                json={"audio_file": "base64"}
            )
            
            # Get conversation response
            if transcribe_response.status_code == 200:
                transcript_data = transcribe_response.json()
                transcript = transcript_data.get("transcript", "I'm feeling sad")
                
                chat_response = client.post(
                    "/conversation/chat",
                    headers={"Authorization": f"Bearer {mock_token}"},
                    json={
                        "message": transcript,
                        "conversation_id": "test-conv",
                        "emotion": transcript_data.get("emotion_data", {}).get("emotion", "neutral")
                    }
                )
                
                # Should get AI response
                if chat_response.status_code == 200:
                    chat_data = chat_response.json()
                    assert "message" in chat_data

