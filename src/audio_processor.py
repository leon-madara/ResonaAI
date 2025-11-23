"""
Audio preprocessing and feature extraction for voice emotion detection
"""

import numpy as np
import librosa
import soundfile as sf
import noisereduce as nr
from typing import Tuple, Dict, Any, Optional
import io
import logging
from loguru import logger

from src.config import settings

class AudioProcessor:
    """Audio preprocessing and feature extraction"""
    
    def __init__(self):
        self.sample_rate = settings.SAMPLE_RATE
        self.chunk_size = settings.CHUNK_SIZE
        self.channels = settings.CHANNELS
        
    def preprocess_audio(self, audio_data: bytes) -> np.ndarray:
        """
        Preprocess audio data for emotion detection
        
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
                audio = self._reduce_noise(audio, sr)
            
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
    
    def extract_features(self, audio: np.ndarray) -> Dict[str, Any]:
        """
        Extract comprehensive audio features for emotion detection
        
        Args:
            audio: Preprocessed audio array
            
        Returns:
            Dictionary of extracted features
        """
        try:
            features = {}
            
            # MFCC features
            if settings.MFCC_FEATURES > 0:
                features['mfcc'] = self._extract_mfcc(audio)
            
            # Spectral features
            if settings.SPECTRAL_FEATURES:
                features['spectral'] = self._extract_spectral_features(audio)
            
            # Prosodic features
            if settings.PROSODIC_FEATURES:
                features['prosodic'] = self._extract_prosodic_features(audio)
            
            # Additional features
            features['temporal'] = self._extract_temporal_features(audio)
            features['statistical'] = self._extract_statistical_features(audio)
            
            logger.debug(f"Extracted {len(features)} feature groups")
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features: {str(e)}")
            raise
    
    def _reduce_noise(self, audio: np.ndarray, sr: int) -> np.ndarray:
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
    
    def _extract_mfcc(self, audio: np.ndarray) -> np.ndarray:
        """Extract MFCC features"""
        mfcc = librosa.feature.mfcc(
            y=audio, 
            sr=self.sample_rate, 
            n_mfcc=settings.MFCC_FEATURES,
            n_fft=2048,
            hop_length=512
        )
        return mfcc.T  # Transpose to get (time, features)
    
    def _extract_spectral_features(self, audio: np.ndarray) -> Dict[str, float]:
        """Extract spectral features"""
        features = {}
        
        # Spectral centroid
        features['spectral_centroid'] = np.mean(librosa.feature.spectral_centroid(y=audio, sr=self.sample_rate))
        
        # Spectral rolloff
        features['spectral_rolloff'] = np.mean(librosa.feature.spectral_rolloff(y=audio, sr=self.sample_rate))
        
        # Spectral bandwidth
        features['spectral_bandwidth'] = np.mean(librosa.feature.spectral_bandwidth(y=audio, sr=self.sample_rate))
        
        # Zero crossing rate
        features['zero_crossing_rate'] = np.mean(librosa.feature.zero_crossing_rate(audio))
        
        # Spectral contrast
        spectral_contrast = librosa.feature.spectral_contrast(y=audio, sr=self.sample_rate)
        for i, contrast in enumerate(spectral_contrast):
            features[f'spectral_contrast_{i}'] = np.mean(contrast)
        
        # Chroma features
        chroma = librosa.feature.chroma_stft(y=audio, sr=self.sample_rate)
        for i, chroma_val in enumerate(chroma):
            features[f'chroma_{i}'] = np.mean(chroma_val)
        
        return features
    
    def _extract_prosodic_features(self, audio: np.ndarray) -> Dict[str, float]:
        """Extract prosodic features (pitch, energy, etc.)"""
        features = {}
        
        # Fundamental frequency (pitch)
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio, 
            fmin=librosa.note_to_hz('C2'), 
            fmax=librosa.note_to_hz('C7'),
            sr=self.sample_rate
        )
        
        # Remove unvoiced segments
        f0_voiced = f0[voiced_flag]
        
        if len(f0_voiced) > 0:
            features['pitch_mean'] = np.mean(f0_voiced)
            features['pitch_std'] = np.std(f0_voiced)
            features['pitch_min'] = np.min(f0_voiced)
            features['pitch_max'] = np.max(f0_voiced)
            features['pitch_range'] = features['pitch_max'] - features['pitch_min']
        else:
            features['pitch_mean'] = 0.0
            features['pitch_std'] = 0.0
            features['pitch_min'] = 0.0
            features['pitch_max'] = 0.0
            features['pitch_range'] = 0.0
        
        # Energy features
        rms = librosa.feature.rms(y=audio)
        features['energy_mean'] = np.mean(rms)
        features['energy_std'] = np.std(rms)
        features['energy_max'] = np.max(rms)
        
        # Voiced/unvoiced ratio
        features['voiced_ratio'] = np.mean(voiced_flag)
        
        return features
    
    def _extract_temporal_features(self, audio: np.ndarray) -> Dict[str, float]:
        """Extract temporal features"""
        features = {}
        
        # Duration
        features['duration'] = len(audio) / self.sample_rate
        
        # Speech rate (approximate)
        # This is a simplified calculation
        features['speech_rate'] = len(audio) / (self.sample_rate * features['duration'])
        
        # Pause ratio (simplified)
        # Calculate based on low energy segments
        rms = librosa.feature.rms(y=audio)
        energy_threshold = np.percentile(rms, 20)
        low_energy_frames = np.sum(rms < energy_threshold)
        features['pause_ratio'] = low_energy_frames / len(rms)
        
        return features
    
    def _extract_statistical_features(self, audio: np.ndarray) -> Dict[str, float]:
        """Extract statistical features"""
        features = {}
        
        # Basic statistics
        features['mean'] = np.mean(audio)
        features['std'] = np.std(audio)
        features['var'] = np.var(audio)
        features['min'] = np.min(audio)
        features['max'] = np.max(audio)
        features['range'] = features['max'] - features['min']
        
        # Higher order statistics
        features['skewness'] = self._calculate_skewness(audio)
        features['kurtosis'] = self._calculate_kurtosis(audio)
        
        # Percentiles
        features['p25'] = np.percentile(audio, 25)
        features['p50'] = np.percentile(audio, 50)
        features['p75'] = np.percentile(audio, 75)
        features['p90'] = np.percentile(audio, 90)
        
        return features
    
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calculate skewness"""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0.0
        return np.mean(((data - mean) / std) ** 3)
    
    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Calculate kurtosis"""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0.0
        return np.mean(((data - mean) / std) ** 4) - 3
    
    def process_audio_chunk(self, audio_chunk: bytes) -> np.ndarray:
        """
        Process a single audio chunk for streaming
        
        Args:
            audio_chunk: Raw audio chunk bytes
            
        Returns:
            Processed audio array
        """
        try:
            # Convert bytes to numpy array
            audio = np.frombuffer(audio_chunk, dtype=np.float32)
            
            # Apply basic preprocessing
            if settings.NORMALIZATION:
                audio = self._normalize_audio(audio)
            
            return audio
            
        except Exception as e:
            logger.error(f"Error processing audio chunk: {str(e)}")
            raise
