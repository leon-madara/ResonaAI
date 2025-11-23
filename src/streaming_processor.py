"""
Real-time streaming audio processing for emotion detection
"""

import numpy as np
import asyncio
from collections import deque
from typing import Deque, Optional, Dict, Any
import logging
from loguru import logger
from datetime import datetime

from src.config import settings
from src.models import EmotionResult, StreamingConfig
from src.audio_processor import AudioProcessor
from src.emotion_detector import EmotionDetector

class StreamingProcessor:
    """Real-time streaming audio processor for emotion detection"""
    
    def __init__(self, audio_processor: AudioProcessor, emotion_detector: EmotionDetector):
        self.audio_processor = audio_processor
        self.emotion_detector = emotion_detector
        
        # Streaming configuration
        self.config = StreamingConfig()
        
        # Audio buffer for streaming
        self.audio_buffer: Deque[float] = deque(maxlen=self.config.buffer_size)
        self.chunk_buffer: Deque[np.ndarray] = deque(maxlen=10)  # Keep last 10 chunks
        
        # Processing state
        self.is_processing = False
        self.last_emotion_result: Optional[EmotionResult] = None
        
        # Voice Activity Detection
        self.vad_enabled = settings.VAD_ENABLED
        self.vad_threshold = self.config.vad_threshold
        self.silence_frames = 0
        self.max_silence_frames = int(settings.SAMPLE_RATE * 2 / self.config.chunk_size)  # 2 seconds
        
        logger.info("StreamingProcessor initialized")
    
    async def process_audio_chunk(self, audio_chunk: bytes) -> EmotionResult:
        """
        Process a single audio chunk for real-time emotion detection
        
        Args:
            audio_chunk: Raw audio chunk bytes
            
        Returns:
            EmotionResult with detected emotion
        """
        try:
            # Convert bytes to numpy array
            audio_data = np.frombuffer(audio_chunk, dtype=np.float32)
            
            # Add to buffer
            self.audio_buffer.extend(audio_data)
            
            # Check if we have enough data for processing
            if len(self.audio_buffer) < self.config.buffer_size:
                # Return previous result or neutral
                if self.last_emotion_result:
                    return self.last_emotion_result
                else:
                    return EmotionResult(
                        emotion="neutral",
                        confidence=0.5,
                        timestamp=datetime.now(),
                        features={}
                    )
            
            # Voice Activity Detection
            if self.vad_enabled and not self._has_voice_activity():
                self.silence_frames += 1
                if self.silence_frames > self.max_silence_frames:
                    # Return neutral for extended silence
                    return EmotionResult(
                        emotion="neutral",
                        confidence=0.5,
                        timestamp=datetime.now(),
                        features={"silence": True}
                    )
            else:
                self.silence_frames = 0
            
            # Extract audio segment for processing
            audio_segment = np.array(list(self.audio_buffer))
            
            # Preprocess audio
            processed_audio = self._preprocess_streaming_audio(audio_segment)
            
            # Detect emotion
            emotion_result = await self.emotion_detector.detect_emotion(processed_audio)
            
            # Update last result
            self.last_emotion_result = emotion_result
            
            logger.debug(f"Streaming emotion: {emotion_result.emotion} (confidence: {emotion_result.confidence:.3f})")
            
            return emotion_result
            
        except Exception as e:
            logger.error(f"Error processing audio chunk: {str(e)}")
            # Return fallback result
            return EmotionResult(
                emotion="neutral",
                confidence=0.3,
                timestamp=datetime.now(),
                features={"error": str(e)}
            )
    
    def _preprocess_streaming_audio(self, audio: np.ndarray) -> np.ndarray:
        """Preprocess audio for streaming analysis"""
        try:
            # Normalize audio
            if np.max(np.abs(audio)) > 0:
                audio = audio / np.max(np.abs(audio))
            
            # Apply simple noise reduction (moving average)
            if len(audio) > 3:
                audio = np.convolve(audio, np.ones(3)/3, mode='same')
            
            # Ensure minimum length
            min_length = settings.SAMPLE_RATE  # 1 second
            if len(audio) < min_length:
                # Pad with zeros
                padding = min_length - len(audio)
                audio = np.pad(audio, (0, padding), mode='constant')
            elif len(audio) > min_length * 3:  # Max 3 seconds
                # Take the most recent segment
                audio = audio[-min_length * 3:]
            
            return audio
            
        except Exception as e:
            logger.error(f"Error preprocessing streaming audio: {str(e)}")
            return audio
    
    def _has_voice_activity(self) -> bool:
        """Simple voice activity detection"""
        try:
            if len(self.audio_buffer) == 0:
                return False
            
            # Calculate energy
            audio_array = np.array(list(self.audio_buffer))
            energy = np.mean(audio_array ** 2)
            
            # Simple threshold-based VAD
            return energy > self.vad_threshold
            
        except Exception as e:
            logger.error(f"Error in voice activity detection: {str(e)}")
            return True  # Assume voice activity on error
    
    async def process_audio_stream(self, audio_stream) -> AsyncIterator[EmotionResult]:
        """
        Process continuous audio stream
        
        Args:
            audio_stream: Async iterator of audio chunks
            
        Yields:
            EmotionResult for each processed chunk
        """
        try:
            async for audio_chunk in audio_stream:
                if audio_chunk:
                    result = await self.process_audio_chunk(audio_chunk)
                    yield result
                    
        except Exception as e:
            logger.error(f"Error processing audio stream: {str(e)}")
            # Yield error result
            yield EmotionResult(
                emotion="neutral",
                confidence=0.0,
                timestamp=datetime.now(),
                features={"error": str(e)}
            )
    
    def reset_buffer(self):
        """Reset audio buffer and processing state"""
        self.audio_buffer.clear()
        self.chunk_buffer.clear()
        self.silence_frames = 0
        self.last_emotion_result = None
        logger.info("Streaming buffer reset")
    
    def update_config(self, config: StreamingConfig):
        """Update streaming configuration"""
        self.config = config
        self.audio_buffer = deque(maxlen=config.buffer_size)
        logger.info("Streaming configuration updated")
    
    def get_streaming_stats(self) -> Dict[str, Any]:
        """Get streaming processing statistics"""
        return {
            "buffer_size": len(self.audio_buffer),
            "max_buffer_size": self.config.buffer_size,
            "chunk_buffer_size": len(self.chunk_buffer),
            "silence_frames": self.silence_frames,
            "vad_enabled": self.vad_enabled,
            "last_emotion": self.last_emotion_result.emotion if self.last_emotion_result else None,
            "last_confidence": self.last_emotion_result.confidence if self.last_emotion_result else None
        }

class AudioStreamManager:
    """Manager for multiple audio streams"""
    
    def __init__(self):
        self.active_streams: Dict[str, StreamingProcessor] = {}
        self.stream_configs: Dict[str, StreamingConfig] = {}
    
    def create_stream(self, stream_id: str, audio_processor: AudioProcessor, 
                     emotion_detector: EmotionDetector, config: Optional[StreamingConfig] = None) -> StreamingProcessor:
        """Create a new audio stream processor"""
        if config is None:
            config = StreamingConfig()
        
        processor = StreamingProcessor(audio_processor, emotion_detector)
        processor.update_config(config)
        
        self.active_streams[stream_id] = processor
        self.stream_configs[stream_id] = config
        
        logger.info(f"Created audio stream: {stream_id}")
        return processor
    
    def get_stream(self, stream_id: str) -> Optional[StreamingProcessor]:
        """Get an existing audio stream processor"""
        return self.active_streams.get(stream_id)
    
    def remove_stream(self, stream_id: str):
        """Remove an audio stream processor"""
        if stream_id in self.active_streams:
            del self.active_streams[stream_id]
        if stream_id in self.stream_configs:
            del self.stream_configs[stream_id]
        logger.info(f"Removed audio stream: {stream_id}")
    
    def get_all_streams(self) -> Dict[str, StreamingProcessor]:
        """Get all active streams"""
        return self.active_streams.copy()
    
    def cleanup_inactive_streams(self, max_age_seconds: int = 300):
        """Clean up streams that haven't been used recently"""
        # This would require tracking last activity time
        # For now, just return the current streams
        return self.active_streams
