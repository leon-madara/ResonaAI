"""
Tests for EmotionDetector
"""

import pytest
import numpy as np
import asyncio
from unittest.mock import Mock, patch
from src.emotion_detector import EmotionDetector
from src.models import EmotionResult

class TestEmotionDetector:
    """Test cases for EmotionDetector"""
    
    @pytest.fixture
    def emotion_detector(self):
        """Create EmotionDetector instance for testing"""
        return EmotionDetector()
    
    @pytest.fixture
    def sample_audio(self):
        """Create sample audio data for testing"""
        # Generate 2 seconds of audio at 16kHz
        duration = 2.0
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Create a simple sine wave
        frequency = 440  # A4 note
        audio = 0.5 * np.sin(2 * np.pi * frequency * t)
        
        return audio
    
    @pytest.mark.asyncio
    async def test_load_models(self, emotion_detector):
        """Test model loading"""
        # Mock the model loading to avoid downloading actual models
        with patch.object(emotion_detector, '_load_wav2vec2_model') as mock_wav2vec2, \
             patch.object(emotion_detector, '_load_emotion_classifier') as mock_classifier:
            
            await emotion_detector.load_models()
            
            mock_wav2vec2.assert_called_once()
            mock_classifier.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_detect_emotion(self, emotion_detector, sample_audio):
        """Test emotion detection"""
        # Mock the feature extraction and prediction methods
        with patch.object(emotion_detector, '_extract_all_features') as mock_features, \
             patch.object(emotion_detector, '_predict_emotion') as mock_predict:
            
            # Setup mocks
            mock_features.return_value = {
                'mfcc': np.random.randn(13),
                'spectral': {'centroid': 1000, 'rolloff': 2000},
                'prosodic': {'pitch_mean': 200, 'energy_mean': 0.5}
            }
            
            from src.models import EmotionPrediction
            mock_predict.return_value = EmotionPrediction(
                emotion="happy",
                confidence=0.8,
                probabilities={"happy": 0.8, "sad": 0.2},
                features_used=["mfcc", "spectral"]
            )
            
            result = await emotion_detector.detect_emotion(sample_audio)
            
            assert isinstance(result, EmotionResult)
            assert result.emotion == "happy"
            assert result.confidence == 0.8
            assert result.processing_time is not None
            assert result.features is not None
    
    @pytest.mark.asyncio
    async def test_extract_all_features(self, emotion_detector, sample_audio):
        """Test feature extraction"""
        # Mock the individual feature extraction methods
        with patch.object(emotion_detector, '_extract_wav2vec2_features') as mock_wav2vec2, \
             patch.object(emotion_detector, '_extract_mfcc_features') as mock_mfcc, \
             patch.object(emotion_detector, '_extract_spectral_features') as mock_spectral, \
             patch.object(emotion_detector, '_extract_prosodic_features') as mock_prosodic, \
             patch.object(emotion_detector, '_extract_temporal_features') as mock_temporal, \
             patch.object(emotion_detector, '_extract_statistical_features') as mock_statistical:
            
            # Setup mocks
            mock_wav2vec2.return_value = np.random.randn(768)
            mock_mfcc.return_value = np.random.randn(13)
            mock_spectral.return_value = np.random.randn(4)
            mock_prosodic.return_value = np.random.randn(4)
            mock_temporal.return_value = np.random.randn(4)
            mock_statistical.return_value = np.random.randn(6)
            
            features = await emotion_detector._extract_all_features(sample_audio)
            
            assert isinstance(features, dict)
            assert 'wav2vec2' in features
            assert 'mfcc' in features
            assert 'spectral' in features
            assert 'prosodic' in features
            assert 'temporal' in features
            assert 'statistical' in features
    
    def test_combine_features(self, emotion_detector):
        """Test feature combination"""
        features = {
            'wav2vec2': np.array([1, 2, 3]),
            'mfcc': np.array([4, 5, 6]),
            'spectral': {'centroid': 7, 'rolloff': 8},
            'prosodic': [9, 10]
        }
        
        combined = emotion_detector._combine_features(features)
        
        assert isinstance(combined, np.ndarray)
        assert len(combined) == 10  # 3 + 3 + 2 + 2
        assert np.array_equal(combined, np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
    
    @pytest.mark.asyncio
    async def test_predict_emotion(self, emotion_detector):
        """Test emotion prediction"""
        features = {
            'mfcc': np.random.randn(13),
            'spectral': np.random.randn(4),
            'prosodic': np.random.randn(4)
        }
        
        # Mock the classifier
        emotion_detector.emotion_classifier = Mock()
        emotion_detector.emotion_classifier.predict_proba.return_value = np.array([[0.1, 0.2, 0.3, 0.4, 0.0, 0.0, 0.0]])
        
        emotion_detector.feature_scaler = Mock()
        emotion_detector.feature_scaler.transform.return_value = np.random.randn(1, 21)
        
        result = await emotion_detector._predict_emotion(features)
        
        assert result.emotion in emotion_detector.emotion_labels
        assert 0 <= result.confidence <= 1
        assert len(result.probabilities) == len(emotion_detector.emotion_labels)
        assert isinstance(result.features_used, list)
    
    def test_get_model_info(self, emotion_detector):
        """Test model info retrieval"""
        info = emotion_detector.get_model_info()
        
        assert isinstance(info, dict)
        assert 'wav2vec2_model' in info
        assert 'supported_emotions' in info
        assert 'feature_weights' in info
        assert 'min_confidence' in info
        
        assert info['supported_emotions'] == emotion_detector.emotion_labels
        assert info['min_confidence'] == emotion_detector.min_confidence
    
    @pytest.mark.asyncio
    async def test_create_default_classifier(self, emotion_detector):
        """Test default classifier creation"""
        await emotion_detector._create_default_classifier()
        
        assert emotion_detector.emotion_classifier is not None
        assert emotion_detector.feature_scaler is not None
    
    def test_extract_mfcc_features(self, emotion_detector, sample_audio):
        """Test MFCC feature extraction"""
        with patch('librosa.feature.mfcc') as mock_mfcc:
            mock_mfcc.return_value = np.random.randn(13, 100)
            
            features = emotion_detector._extract_mfcc_features(sample_audio)
            
            assert isinstance(features, np.ndarray)
            assert len(features) == 13
            mock_mfcc.assert_called_once()
    
    def test_extract_spectral_features(self, emotion_detector, sample_audio):
        """Test spectral feature extraction"""
        with patch('librosa.feature.spectral_centroid') as mock_centroid, \
             patch('librosa.feature.spectral_rolloff') as mock_rolloff, \
             patch('librosa.feature.spectral_bandwidth') as mock_bandwidth, \
             patch('librosa.feature.zero_crossing_rate') as mock_zcr:
            
            mock_centroid.return_value = np.array([1000])
            mock_rolloff.return_value = np.array([2000])
            mock_bandwidth.return_value = np.array([500])
            mock_zcr.return_value = np.array([0.1])
            
            features = emotion_detector._extract_spectral_features(sample_audio)
            
            assert isinstance(features, np.ndarray)
            assert len(features) == 4
            assert features[0] == 1000  # spectral centroid
            assert features[1] == 2000  # spectral rolloff
            assert features[2] == 500   # spectral bandwidth
            assert features[3] == 0.1   # zero crossing rate
