"""
Audio Preprocessing Service
Refactored from existing ResonaAI audio processor for mental health platform
"""

import numpy as np
import librosa
import soundfile as sf
import noisereduce as nr
import io
from typing import Dict, Any, Optional
import logging

from config import settings

logger = logging.getLogger(__name__)

class AudioPreprocessor:
    """Audio preprocessing service for speech processing"""
    
    def __init__(self):
        self.sample_rate = settings.SAMPLE_RATE
        self.chunk_size = settings.CHUNK_SIZE
        self.channels = settings.CHANNELS
    
    async def preprocess_audio(self, audio_data: bytes) -> np.ndarray:
        """
        Preprocess audio data for speech processing
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Preprocessed audio array
        """
        try:
            # Load audio from bytes
            audio, sr = librosa.load(io.BytesIO(audio_data), sr=self.sample_rate, mono=True)
            
            # Apply preprocessing steps
            if settings.NOISE_REDUCTION:
                audio = await self._reduce_noise(audio, sr)
            
            if settings.NORMALIZATION:
                audio = self._normalize_audio(audio)
            
            # Trim silence
            audio = self._trim_silence(audio)
            
            # Ensure minimum length
            if len(audio) < self.sample_rate:  # Less than 1 second
                audio = self._pad_audio(audio, self.sample_rate)
            
            logger.debug(f"Preprocessed audio: {len(audio)} samples, {len(audio)/sr:.2f}s")
            return audio
            
        except Exception as e:
            logger.error(f"Error preprocessing audio: {str(e)}")
            raise
    
    async def preprocess_audio_stream(self, audio_data: bytes) -> np.ndarray:
        """
        Preprocess audio stream for real-time processing
        
        Args:
            audio_data: Raw audio chunk bytes
            
        Returns:
            Processed audio array
        """
        try:
            # Convert bytes to numpy array
            audio = np.frombuffer(audio_data, dtype=np.float32)
            
            # Apply basic preprocessing
            if settings.NORMALIZATION:
                audio = self._normalize_audio(audio)
            
            return audio
            
        except Exception as e:
            logger.error(f"Error preprocessing audio stream: {str(e)}")
            raise
    
    async def _reduce_noise(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply noise reduction to audio"""
        try:
            # Use spectral gating for noise reduction
            reduced_audio = nr.reduce_noise(y=audio, sr=sr, stationary=False, prop_decrease=0.8)
            return reduced_audio
        except Exception as e:
            logger.warning(f"Noise reduction failed: {str(e)}, using original audio")
            return audio
    
    def _normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """Normalize audio to [-1, 1] range"""
        if np.max(np.abs(audio)) > 0:
            return audio / np.max(np.abs(audio))
        return audio
    
    def _trim_silence(self, audio: np.ndarray, top_db: int = 20) -> np.ndarray:
        """Trim silence from beginning and end of audio"""
        try:
            trimmed, _ = librosa.effects.trim(audio, top_db=top_db)
            return trimmed
        except Exception as e:
            logger.warning(f"Silence trimming failed: {str(e)}, using original audio")
            return audio
    
    def _pad_audio(self, audio: np.ndarray, target_length: int) -> np.ndarray:
        """Pad audio to minimum length"""
        if len(audio) < target_length:
            padding = target_length - len(audio)
            audio = np.pad(audio, (0, padding), mode='constant')
        return audio
    
    def get_audio_info(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Get audio file information
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Dictionary with audio information
        """
        try:
            # Load audio to get info
            audio, sr = librosa.load(io.BytesIO(audio_data), sr=None, mono=False)
            
            return {
                "duration": len(audio) / sr,
                "sample_rate": sr,
                "channels": 1 if len(audio.shape) == 1 else audio.shape[0],
                "samples": len(audio),
                "format": "unknown",  # Would need to detect from file header
                "size_bytes": len(audio_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting audio info: {str(e)}")
            return {
                "duration": 0,
                "sample_rate": 0,
                "channels": 0,
                "samples": 0,
                "format": "unknown",
                "size_bytes": len(audio_data)
            }
    
    def validate_audio(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Validate audio data
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Validation result
        """
        try:
            # Check file size
            max_size = settings.MAX_FILE_SIZE
            if len(audio_data) > max_size:
                return {
                    "valid": False,
                    "error": f"File too large: {len(audio_data)} bytes (max: {max_size})"
                }
            
            # Try to load audio
            audio, sr = librosa.load(io.BytesIO(audio_data), sr=None, mono=True)
            
            # Check duration
            duration = len(audio) / sr
            max_duration = 30 * 60  # 30 minutes
            if duration > max_duration:
                return {
                    "valid": False,
                    "error": f"Audio too long: {duration:.1f}s (max: {max_duration}s)"
                }
            
            # Check minimum duration
            min_duration = 0.1  # 100ms
            if duration < min_duration:
                return {
                    "valid": False,
                    "error": f"Audio too short: {duration:.1f}s (min: {min_duration}s)"
                }
            
            return {
                "valid": True,
                "duration": duration,
                "sample_rate": sr,
                "channels": 1,
                "samples": len(audio)
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Invalid audio format: {str(e)}"
            }
