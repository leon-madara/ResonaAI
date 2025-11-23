"""
Tests for API endpoints
"""

import pytest
import io
import numpy as np
import soundfile as sf
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
from main import app

class TestAPI:
    """Test cases for API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_audio_file(self):
        """Create sample audio file for testing"""
        # Generate 2 seconds of audio
        duration = 2.0
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave
        
        # Save to bytes buffer
        buffer = io.BytesIO()
        sf.write(buffer, audio, sample_rate, format='WAV')
        buffer.seek(0)
        
        return ("audio.wav", buffer.getvalue(), "audio/wav")
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data
        assert "version" in data
    
    @pytest.mark.asyncio
    async def test_detect_emotion_from_file(self, client, sample_audio_file):
        """Test emotion detection from file upload"""
        with patch('main.emotion_detector') as mock_detector:
            # Mock the emotion detection result
            from src.models import EmotionResult
            mock_result = EmotionResult(
                emotion="happy",
                confidence=0.8,
                timestamp=None,
                features={"mfcc": [1, 2, 3]}
            )
            mock_detector.detect_emotion.return_value = mock_result
            
            # Mock the audio processor
            with patch('main.audio_processor') as mock_processor:
                mock_processor.preprocess_audio.return_value = np.random.randn(32000)
                
                # Make the request
                files = {"file": sample_audio_file}
                response = client.post("/detect-emotion/file", files=files)
                
                assert response.status_code == 200
                data = response.json()
                assert data["emotion"] == "happy"
                assert data["confidence"] == 0.8
                assert "features" in data
    
    @pytest.mark.asyncio
    async def test_detect_emotion_batch(self, client, sample_audio_file):
        """Test batch emotion detection"""
        with patch('main.emotion_detector') as mock_detector:
            # Mock the emotion detection result
            from src.models import EmotionResult
            mock_result = EmotionResult(
                emotion="sad",
                confidence=0.7,
                timestamp=None,
                features={"spectral": {"centroid": 1000}}
            )
            mock_detector.detect_emotion.return_value = mock_result
            
            # Mock the audio processor
            with patch('main.audio_processor') as mock_processor:
                mock_processor.preprocess_audio.return_value = np.random.randn(32000)
                
                # Create multiple files
                files = [
                    ("files", sample_audio_file),
                    ("files", sample_audio_file)
                ]
                
                response = client.post("/detect-emotion/batch", files=files)
                
                assert response.status_code == 200
                data = response.json()
                assert data["total_files"] == 2
                assert data["successful_analyses"] == 2
                assert len(data["results"]) == 2
                
                for result in data["results"]:
                    assert result["emotion"] == "sad"
                    assert result["confidence"] == 0.7
    
    @pytest.mark.asyncio
    async def test_detect_emotion_stream(self, client):
        """Test streaming emotion detection"""
        with patch('main.streaming_processor') as mock_processor:
            # Mock the streaming processor result
            from src.models import EmotionResult
            mock_result = EmotionResult(
                emotion="angry",
                confidence=0.9,
                timestamp=None,
                features={"prosodic": {"pitch_mean": 200}}
            )
            mock_processor.process_audio_chunk.return_value = mock_result
            
            # Create audio data
            audio_data = np.random.randn(1024).astype(np.float32).tobytes()
            
            response = client.post("/detect-emotion/stream", content=audio_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["emotion"] == "angry"
            assert data["confidence"] == 0.9
    
    def test_detect_emotion_file_error(self, client):
        """Test error handling in file emotion detection"""
        # Send invalid file data
        files = {"file": ("invalid.wav", b"invalid audio data", "audio/wav")}
        
        response = client.post("/detect-emotion/file", files=files)
        
        # Should return 500 error
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
    
    def test_detect_emotion_batch_error(self, client):
        """Test error handling in batch emotion detection"""
        # Send invalid file data
        files = [("files", ("invalid.wav", b"invalid audio data", "audio/wav"))]
        
        response = client.post("/detect-emotion/batch", files=files)
        
        # Should return 500 error
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
    
    def test_detect_emotion_stream_error(self, client):
        """Test error handling in streaming emotion detection"""
        with patch('main.streaming_processor') as mock_processor:
            # Mock an exception
            mock_processor.process_audio_chunk.side_effect = Exception("Processing error")
            
            # Create audio data
            audio_data = np.random.randn(1024).astype(np.float32).tobytes()
            
            response = client.post("/detect-emotion/stream", content=audio_data)
            
            # Should return 500 error
            assert response.status_code == 500
            data = response.json()
            assert "error" in data
    
    @pytest.mark.asyncio
    async def test_websocket_emotion_stream(self, client):
        """Test WebSocket emotion streaming"""
        with patch('main.streaming_processor') as mock_processor:
            # Mock the streaming processor result
            from src.models import EmotionResult
            mock_result = EmotionResult(
                emotion="surprise",
                confidence=0.85,
                timestamp=None,
                features={"temporal": {"duration": 2.0}}
            )
            mock_processor.process_audio_chunk.return_value = mock_result
            
            # Create audio data
            audio_data = np.random.randn(1024).astype(np.float32).tobytes()
            
            with client.websocket_connect("/ws/emotion-stream") as websocket:
                # Send audio data
                websocket.send_bytes(audio_data)
                
                # Receive result
                data = websocket.receive_json()
                
                assert data["emotion"] == "surprise"
                assert data["confidence"] == 0.85
                assert "timestamp" in data
                assert "features" in data
    
    def test_cors_headers(self, client):
        """Test CORS headers"""
        response = client.options("/health")
        
        # Should not fail due to CORS
        assert response.status_code in [200, 405]  # 405 is also acceptable for OPTIONS
    
    def test_api_documentation(self, client):
        """Test API documentation endpoints"""
        # Test OpenAPI docs
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Test ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200
        
        # Test OpenAPI JSON
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
