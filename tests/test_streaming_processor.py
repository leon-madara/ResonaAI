"""
Tests for StreamingProcessor
"""

import pytest
import numpy as np
import asyncio
from unittest.mock import Mock, AsyncMock
from src.streaming_processor import StreamingProcessor, AudioStreamManager
from src.audio_processor import AudioProcessor
from src.emotion_detector import EmotionDetector
from src.models import EmotionResult, StreamingConfig

class TestStreamingProcessor:
    """Test cases for StreamingProcessor"""
    
    @pytest.fixture
    def audio_processor(self):
        """Create AudioProcessor instance for testing"""
        return AudioProcessor()
    
    @pytest.fixture
    def emotion_detector(self):
        """Create EmotionDetector instance for testing"""
        detector = EmotionDetector()
        # Mock the async methods
        detector.detect_emotion = AsyncMock()
        return detector
    
    @pytest.fixture
    def streaming_processor(self, audio_processor, emotion_detector):
        """Create StreamingProcessor instance for testing"""
        return StreamingProcessor(audio_processor, emotion_detector)
    
    @pytest.fixture
    def sample_audio_chunk(self):
        """Create sample audio chunk for testing"""
        return np.random.randn(1024).astype(np.float32).tobytes()
    
    @pytest.mark.asyncio
    async def test_process_audio_chunk(self, streaming_processor, sample_audio_chunk):
        """Test audio chunk processing"""
        # Mock the emotion detector response
        mock_result = EmotionResult(
            emotion="happy",
            confidence=0.8,
            timestamp=None,
            features={}
        )
        streaming_processor.emotion_detector.detect_emotion.return_value = mock_result
        
        # Fill buffer with enough data
        for _ in range(5):
            await streaming_processor.process_audio_chunk(sample_audio_chunk)
        
        result = await streaming_processor.process_audio_chunk(sample_audio_chunk)
        
        assert isinstance(result, EmotionResult)
        assert result.emotion in ["happy", "neutral"]  # Could be neutral if VAD fails
        assert 0 <= result.confidence <= 1
    
    @pytest.mark.asyncio
    async def test_process_audio_chunk_insufficient_data(self, streaming_processor, sample_audio_chunk):
        """Test processing with insufficient data"""
        # Process only one chunk (not enough for full buffer)
        result = await streaming_processor.process_audio_chunk(sample_audio_chunk)
        
        # Should return neutral result
        assert isinstance(result, EmotionResult)
        assert result.emotion == "neutral"
        assert result.confidence == 0.5
    
    def test_preprocess_streaming_audio(self, streaming_processor):
        """Test streaming audio preprocessing"""
        # Create audio data
        audio = np.random.randn(16000)  # 1 second at 16kHz
        
        processed = streaming_processor._preprocess_streaming_audio(audio)
        
        assert isinstance(processed, np.ndarray)
        assert len(processed) > 0
        assert np.max(np.abs(processed)) <= 1.0  # Should be normalized
    
    def test_has_voice_activity(self, streaming_processor):
        """Test voice activity detection"""
        # Test with high energy (should detect voice)
        high_energy_audio = np.ones(1000) * 0.8
        streaming_processor.audio_buffer.extend(high_energy_audio)
        
        assert streaming_processor._has_voice_activity() == True
        
        # Test with low energy (should not detect voice)
        streaming_processor.audio_buffer.clear()
        low_energy_audio = np.ones(1000) * 0.1
        streaming_processor.audio_buffer.extend(low_energy_audio)
        
        assert streaming_processor._has_voice_activity() == False
    
    def test_reset_buffer(self, streaming_processor):
        """Test buffer reset"""
        # Add some data to buffers
        streaming_processor.audio_buffer.extend([1, 2, 3, 4, 5])
        streaming_processor.chunk_buffer.append(np.array([1, 2, 3]))
        streaming_processor.silence_frames = 10
        
        streaming_processor.reset_buffer()
        
        assert len(streaming_processor.audio_buffer) == 0
        assert len(streaming_processor.chunk_buffer) == 0
        assert streaming_processor.silence_frames == 0
        assert streaming_processor.last_emotion_result is None
    
    def test_update_config(self, streaming_processor):
        """Test configuration update"""
        new_config = StreamingConfig(
            sample_rate=22050,
            chunk_size=2048,
            buffer_size=8192
        )
        
        streaming_processor.update_config(new_config)
        
        assert streaming_processor.config.sample_rate == 22050
        assert streaming_processor.config.chunk_size == 2048
        assert streaming_processor.config.buffer_size == 8192
        assert streaming_processor.audio_buffer.maxlen == 8192
    
    def test_get_streaming_stats(self, streaming_processor):
        """Test streaming statistics"""
        # Add some data
        streaming_processor.audio_buffer.extend([1, 2, 3, 4, 5])
        streaming_processor.silence_frames = 5
        
        mock_result = EmotionResult(
            emotion="sad",
            confidence=0.7,
            timestamp=None,
            features={}
        )
        streaming_processor.last_emotion_result = mock_result
        
        stats = streaming_processor.get_streaming_stats()
        
        assert isinstance(stats, dict)
        assert 'buffer_size' in stats
        assert 'max_buffer_size' in stats
        assert 'silence_frames' in stats
        assert 'vad_enabled' in stats
        assert 'last_emotion' in stats
        assert 'last_confidence' in stats
        
        assert stats['buffer_size'] == 5
        assert stats['silence_frames'] == 5
        assert stats['last_emotion'] == "sad"
        assert stats['last_confidence'] == 0.7

class TestAudioStreamManager:
    """Test cases for AudioStreamManager"""
    
    @pytest.fixture
    def stream_manager(self):
        """Create AudioStreamManager instance for testing"""
        return AudioStreamManager()
    
    @pytest.fixture
    def audio_processor(self):
        """Create AudioProcessor instance for testing"""
        return AudioProcessor()
    
    @pytest.fixture
    def emotion_detector(self):
        """Create EmotionDetector instance for testing"""
        return EmotionDetector()
    
    def test_create_stream(self, stream_manager, audio_processor, emotion_detector):
        """Test stream creation"""
        stream_id = "test_stream"
        
        processor = stream_manager.create_stream(stream_id, audio_processor, emotion_detector)
        
        assert isinstance(processor, StreamingProcessor)
        assert stream_id in stream_manager.active_streams
        assert stream_id in stream_manager.stream_configs
    
    def test_get_stream(self, stream_manager, audio_processor, emotion_detector):
        """Test stream retrieval"""
        stream_id = "test_stream"
        stream_manager.create_stream(stream_id, audio_processor, emotion_detector)
        
        retrieved_stream = stream_manager.get_stream(stream_id)
        
        assert isinstance(retrieved_stream, StreamingProcessor)
        assert retrieved_stream == stream_manager.active_streams[stream_id]
    
    def test_get_nonexistent_stream(self, stream_manager):
        """Test retrieval of nonexistent stream"""
        result = stream_manager.get_stream("nonexistent")
        
        assert result is None
    
    def test_remove_stream(self, stream_manager, audio_processor, emotion_detector):
        """Test stream removal"""
        stream_id = "test_stream"
        stream_manager.create_stream(stream_id, audio_processor, emotion_detector)
        
        assert stream_id in stream_manager.active_streams
        
        stream_manager.remove_stream(stream_id)
        
        assert stream_id not in stream_manager.active_streams
        assert stream_id not in stream_manager.stream_configs
    
    def test_get_all_streams(self, stream_manager, audio_processor, emotion_detector):
        """Test getting all streams"""
        # Create multiple streams
        stream_ids = ["stream1", "stream2", "stream3"]
        for stream_id in stream_ids:
            stream_manager.create_stream(stream_id, audio_processor, emotion_detector)
        
        all_streams = stream_manager.get_all_streams()
        
        assert isinstance(all_streams, dict)
        assert len(all_streams) == 3
        for stream_id in stream_ids:
            assert stream_id in all_streams
            assert isinstance(all_streams[stream_id], StreamingProcessor)
    
    def test_create_stream_with_custom_config(self, stream_manager, audio_processor, emotion_detector):
        """Test stream creation with custom configuration"""
        stream_id = "custom_stream"
        custom_config = StreamingConfig(
            sample_rate=22050,
            chunk_size=2048,
            buffer_size=8192
        )
        
        processor = stream_manager.create_stream(stream_id, audio_processor, emotion_detector, custom_config)
        
        assert processor.config.sample_rate == 22050
        assert processor.config.chunk_size == 2048
        assert processor.config.buffer_size == 8192
        assert stream_manager.stream_configs[stream_id] == custom_config
