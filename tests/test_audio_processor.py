"""
Tests for AudioProcessor
"""

import pytest
import numpy as np
import io
import soundfile as sf
from src.audio_processor import AudioProcessor

class TestAudioProcessor:
    """Test cases for AudioProcessor"""
    
    @pytest.fixture
    def audio_processor(self):
        """Create AudioProcessor instance for testing"""
        return AudioProcessor()
    
    @pytest.fixture
    def sample_audio(self):
        """Create sample audio data for testing"""
        # Generate 2 seconds of audio at 16kHz
        duration = 2.0
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Create a simple sine wave with some noise
        frequency = 440  # A4 note
        audio = 0.5 * np.sin(2 * np.pi * frequency * t)
        audio += 0.1 * np.random.randn(len(audio))  # Add noise
        
        return audio
    
    @pytest.fixture
    def sample_audio_bytes(self, sample_audio):
        """Convert sample audio to bytes"""
        buffer = io.BytesIO()
        sf.write(buffer, sample_audio, 16000, format='WAV')
        return buffer.getvalue()
    
    def test_preprocess_audio(self, audio_processor, sample_audio_bytes):
        """Test audio preprocessing"""
        processed_audio = audio_processor.preprocess_audio(sample_audio_bytes)
        
        assert isinstance(processed_audio, np.ndarray)
        assert len(processed_audio) > 0
        assert np.max(np.abs(processed_audio)) <= 1.0  # Should be normalized
    
    def test_extract_features(self, audio_processor, sample_audio):
        """Test feature extraction"""
        features = audio_processor.extract_features(sample_audio)
        
        assert isinstance(features, dict)
        assert 'mfcc' in features
        assert 'spectral' in features
        assert 'prosodic' in features
        assert 'temporal' in features
        assert 'statistical' in features
        
        # Check MFCC features
        assert features['mfcc'].shape[1] == 13  # 13 MFCC coefficients
        
        # Check spectral features
        assert 'spectral_centroid' in features['spectral']
        assert 'spectral_rolloff' in features['spectral']
        assert 'zero_crossing_rate' in features['spectral']
        
        # Check prosodic features
        assert 'pitch_mean' in features['prosodic']
        assert 'energy_mean' in features['prosodic']
        assert 'voiced_ratio' in features['prosodic']
    
    def test_noise_reduction(self, audio_processor, sample_audio):
        """Test noise reduction"""
        # Add significant noise
        noisy_audio = sample_audio + 0.5 * np.random.randn(len(sample_audio))
        
        reduced_audio = audio_processor._reduce_noise(noisy_audio, 16000)
        
        assert isinstance(reduced_audio, np.ndarray)
        assert len(reduced_audio) == len(noisy_audio)
    
    def test_normalize_audio(self, audio_processor):
        """Test audio normalization"""
        # Create audio with amplitude > 1
        audio = 2.0 * np.random.randn(1000)
        
        normalized = audio_processor._normalize_audio(audio)
        
        assert np.max(np.abs(normalized)) <= 1.0
        assert np.max(np.abs(normalized)) > 0.9  # Should be close to 1
    
    def test_trim_silence(self, audio_processor):
        """Test silence trimming"""
        # Create audio with silence at beginning and end
        silence = np.zeros(1000)
        signal = 0.5 * np.random.randn(2000)
        audio = np.concatenate([silence, signal, silence])
        
        trimmed = audio_processor._trim_silence(audio)
        
        assert len(trimmed) <= len(audio)
        assert len(trimmed) > 0
    
    def test_pad_audio(self, audio_processor):
        """Test audio padding"""
        short_audio = np.random.randn(1000)
        target_length = 2000
        
        padded = audio_processor._pad_audio(short_audio, target_length)
        
        assert len(padded) == target_length
        assert np.array_equal(padded[:1000], short_audio)
        assert np.all(padded[1000:] == 0)  # Should be padded with zeros
    
    def test_process_audio_chunk(self, audio_processor):
        """Test audio chunk processing"""
        # Create audio chunk
        chunk_data = np.random.randn(1024).astype(np.float32).tobytes()
        
        processed = audio_processor.process_audio_chunk(chunk_data)
        
        assert isinstance(processed, np.ndarray)
        assert len(processed) == 1024
    
    def test_extract_mfcc(self, audio_processor, sample_audio):
        """Test MFCC extraction"""
        mfcc = audio_processor._extract_mfcc(sample_audio)
        
        assert isinstance(mfcc, np.ndarray)
        assert mfcc.shape[1] == 13  # 13 MFCC coefficients
        assert mfcc.shape[0] > 0  # Should have time frames
    
    def test_extract_spectral_features(self, audio_processor, sample_audio):
        """Test spectral feature extraction"""
        features = audio_processor._extract_spectral_features(sample_audio)
        
        assert isinstance(features, dict)
        assert 'spectral_centroid' in features
        assert 'spectral_rolloff' in features
        assert 'spectral_bandwidth' in features
        assert 'zero_crossing_rate' in features
        
        # Check that values are reasonable
        assert features['spectral_centroid'] > 0
        assert features['zero_crossing_rate'] >= 0
    
    def test_extract_prosodic_features(self, audio_processor, sample_audio):
        """Test prosodic feature extraction"""
        features = audio_processor._extract_prosodic_features(sample_audio)
        
        assert isinstance(features, dict)
        assert 'pitch_mean' in features
        assert 'pitch_std' in features
        assert 'energy_mean' in features
        assert 'voiced_ratio' in features
        
        # Check that values are reasonable
        assert features['pitch_mean'] >= 0
        assert features['energy_mean'] >= 0
        assert 0 <= features['voiced_ratio'] <= 1
    
    def test_extract_temporal_features(self, audio_processor, sample_audio):
        """Test temporal feature extraction"""
        features = audio_processor._extract_temporal_features(sample_audio)
        
        assert isinstance(features, dict)
        assert 'duration' in features
        assert 'speech_rate' in features
        assert 'pause_ratio' in features
        
        # Check that values are reasonable
        assert features['duration'] > 0
        assert features['speech_rate'] > 0
        assert 0 <= features['pause_ratio'] <= 1
    
    def test_extract_statistical_features(self, audio_processor, sample_audio):
        """Test statistical feature extraction"""
        features = audio_processor._extract_statistical_features(sample_audio)
        
        assert isinstance(features, dict)
        assert 'mean' in features
        assert 'std' in features
        assert 'var' in features
        assert 'min' in features
        assert 'max' in features
        assert 'range' in features
        assert 'skewness' in features
        assert 'kurtosis' in features
        
        # Check that range = max - min
        assert abs(features['range'] - (features['max'] - features['min'])) < 1e-10
