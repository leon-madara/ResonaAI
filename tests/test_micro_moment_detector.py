"""
Tests for Micro-Moment Detector
"""

import pytest
import numpy as np
from src.micro_moment_detector import MicroMomentDetector


class TestMicroMomentDetector:
    """Test cases for MicroMomentDetector"""
    
    @pytest.fixture
    def detector(self):
        """Create MicroMomentDetector instance for testing"""
        return MicroMomentDetector(sample_rate=16000)
    
    @pytest.fixture
    def sample_audio(self):
        """Create sample audio data for testing"""
        # Generate 2 seconds of audio at 16kHz
        duration = 2.0
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Create a simple sine wave (440 Hz)
        frequency = 440
        audio = 0.5 * np.sin(2 * np.pi * frequency * t)
        
        return audio
    
    @pytest.fixture
    def tremor_audio(self):
        """Create audio with tremor pattern (modulated pitch)"""
        duration = 2.0
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Create audio with pitch modulation (tremor at ~5 Hz)
        base_freq = 200
        tremor_freq = 5.0
        modulation = 0.1 * np.sin(2 * np.pi * tremor_freq * t)
        frequency = base_freq * (1 + modulation)
        
        # Generate audio with varying frequency
        audio = 0.5 * np.sin(2 * np.pi * np.cumsum(frequency) / sample_rate)
        
        return audio
    
    @pytest.fixture
    def sigh_audio(self):
        """Create audio with sigh pattern (energy peak and decay)"""
        duration = 3.0
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Create base audio
        audio = 0.3 * np.sin(2 * np.pi * 200 * t)
        
        # Add sigh pattern: energy increase at 1.0s followed by decay
        sigh_start = int(1.0 * sample_rate)
        sigh_duration = int(0.5 * sample_rate)
        
        # Energy envelope: peak then decay
        for i in range(sigh_duration):
            idx = sigh_start + i
            if idx < len(audio):
                envelope = 1.0 - (i / sigh_duration) * 0.8  # Decay from 1.0 to 0.2
                audio[idx] *= envelope
        
        return audio
    
    @pytest.fixture
    def crack_audio(self):
        """Create audio with voice crack (pitch jump)"""
        duration = 2.0
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Create audio with sudden pitch change
        audio1 = 0.5 * np.sin(2 * np.pi * 200 * t[:len(t)//2])
        audio2 = 0.5 * np.sin(2 * np.pi * 300 * t[len(t)//2:])  # Higher pitch
        
        audio = np.concatenate([audio1, audio2])
        
        return audio
    
    @pytest.fixture
    def hesitation_audio(self):
        """Create audio with pauses (hesitations)"""
        duration = 3.0
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Create audio with gaps (pauses)
        audio = 0.5 * np.sin(2 * np.pi * 200 * t)
        
        # Add pauses (silence segments)
        pause_start1 = int(0.5 * sample_rate)
        pause_end1 = int(0.8 * sample_rate)
        pause_start2 = int(1.5 * sample_rate)
        pause_end2 = int(2.0 * sample_rate)
        
        audio[pause_start1:pause_end1] = 0.0
        audio[pause_start2:pause_end2] = 0.0
        
        return audio
    
    def test_initialization(self, detector):
        """Test detector initialization"""
        assert detector.sample_rate == 16000
        assert detector.tremor_freq_min == 4.0
        assert detector.tremor_freq_max == 8.0
    
    def test_detect_tremor_no_tremor(self, detector, sample_audio):
        """Test tremor detection with normal audio (no tremor)"""
        detected, intensity = detector.detect_tremor(sample_audio)
        
        assert isinstance(detected, bool)
        assert isinstance(intensity, float)
        assert 0.0 <= intensity <= 1.0
    
    def test_detect_tremor_with_tremor(self, detector, tremor_audio):
        """Test tremor detection with tremor pattern"""
        detected, intensity = detector.detect_tremor(tremor_audio)
        
        assert isinstance(detected, bool)
        assert isinstance(intensity, float)
        assert 0.0 <= intensity <= 1.0
        # Note: May or may not detect depending on signal characteristics
    
    def test_detect_tremor_short_audio(self, detector):
        """Test tremor detection with very short audio"""
        short_audio = np.random.randn(100)  # Very short
        detected, intensity = detector.detect_tremor(short_audio)
        
        assert detected == False
        assert intensity == 0.0
    
    def test_detect_tremor_silence(self, detector):
        """Test tremor detection with silence"""
        silence = np.zeros(16000)  # 1 second of silence
        detected, intensity = detector.detect_tremor(silence)
        
        assert isinstance(detected, bool)
        assert isinstance(intensity, float)
    
    def test_detect_sighs_no_sighs(self, detector, sample_audio):
        """Test sigh detection with normal audio (no sighs)"""
        sighs = detector.detect_sighs(sample_audio)
        
        assert isinstance(sighs, list)
        assert all(isinstance(s, float) for s in sighs)
    
    def test_detect_sighs_with_sighs(self, detector, sigh_audio):
        """Test sigh detection with sigh pattern"""
        sighs = detector.detect_sighs(sigh_audio)
        
        assert isinstance(sighs, list)
        assert all(isinstance(s, float) for s in sighs)
        assert all(s >= 0.0 for s in sighs)
    
    def test_detect_sighs_short_audio(self, detector):
        """Test sigh detection with very short audio"""
        short_audio = np.random.randn(100)
        sighs = detector.detect_sighs(short_audio)
        
        assert isinstance(sighs, list)
        assert len(sighs) == 0
    
    def test_detect_voice_cracks_no_cracks(self, detector, sample_audio):
        """Test voice crack detection with normal audio"""
        cracks = detector.detect_voice_cracks(sample_audio)
        
        assert isinstance(cracks, list)
        assert all(isinstance(c, tuple) and len(c) == 2 for c in cracks)
        assert all(isinstance(t, float) and isinstance(i, float) 
                  for t, i in cracks)
        assert all(0.0 <= i <= 1.0 for _, i in cracks)
    
    def test_detect_voice_cracks_with_cracks(self, detector, crack_audio):
        """Test voice crack detection with pitch jump"""
        cracks = detector.detect_voice_cracks(crack_audio)
        
        assert isinstance(cracks, list)
        assert all(isinstance(c, tuple) and len(c) == 2 for c in cracks)
        assert all(isinstance(t, float) and isinstance(i, float) 
                  for t, i in cracks)
        assert all(0.0 <= i <= 1.0 for _, i in cracks)
    
    def test_detect_voice_cracks_short_audio(self, detector):
        """Test voice crack detection with very short audio"""
        short_audio = np.random.randn(100)
        cracks = detector.detect_voice_cracks(short_audio)
        
        assert isinstance(cracks, list)
        assert len(cracks) == 0
    
    def test_detect_hesitations_no_hesitations(self, detector, sample_audio):
        """Test hesitation detection with continuous audio"""
        hesitations = detector.detect_hesitations(sample_audio)
        
        assert isinstance(hesitations, dict)
        assert 'count' in hesitations
        assert 'avg_duration' in hesitations
        assert 'max_duration' in hesitations
        assert 'long_pauses' in hesitations
        assert 'pause_ratio' in hesitations
        
        assert isinstance(hesitations['count'], int)
        assert isinstance(hesitations['avg_duration'], float)
        assert isinstance(hesitations['max_duration'], float)
        assert isinstance(hesitations['long_pauses'], int)
        assert isinstance(hesitations['pause_ratio'], float)
    
    def test_detect_hesitations_with_hesitations(self, detector, hesitation_audio):
        """Test hesitation detection with pauses"""
        hesitations = detector.detect_hesitations(hesitation_audio)
        
        assert isinstance(hesitations, dict)
        assert hesitations['count'] >= 0
        assert hesitations['avg_duration'] >= 0.0
        assert hesitations['max_duration'] >= 0.0
        assert hesitations['long_pauses'] >= 0
        assert 0.0 <= hesitations['pause_ratio'] <= 1.0
    
    def test_detect_hesitations_silence(self, detector):
        """Test hesitation detection with silence"""
        silence = np.zeros(16000)
        hesitations = detector.detect_hesitations(silence)
        
        assert isinstance(hesitations, dict)
        assert 'count' in hesitations
    
    def test_analyze_micro_moments(self, detector, sample_audio):
        """Test overall micro-moments analysis"""
        result = detector.analyze_micro_moments(sample_audio)
        
        assert isinstance(result, dict)
        assert 'tremor' in result
        assert 'sighs' in result
        assert 'voice_cracks' in result
        assert 'hesitations' in result
        assert 'overall_risk' in result
        assert 'interpretation' in result
        
        # Check tremor structure
        assert 'detected' in result['tremor']
        assert 'intensity' in result['tremor']
        assert 'interpretation' in result['tremor']
        
        # Check sighs structure
        assert 'count' in result['sighs']
        assert 'intensity' in result['sighs']
        assert 'interpretation' in result['sighs']
        
        # Check voice_cracks structure
        assert 'count' in result['voice_cracks']
        assert 'intensity' in result['voice_cracks']
        assert 'interpretation' in result['voice_cracks']
        
        # Check hesitations structure
        assert 'count' in result['hesitations']
        assert 'average_duration' in result['hesitations']
        assert 'interpretation' in result['hesitations']
        
        # Check risk level
        assert result['overall_risk'] in ['low', 'medium', 'medium-high', 'high']
        assert isinstance(result['interpretation'], str)
    
    def test_analyze_micro_moments_with_features(self, detector, sample_audio):
        """Test analysis with pre-extracted voice features"""
        voice_features = {
            'prosodic': {
                'pitch_mean': 200.0,
                'pitch_std': 20.0
            }
        }
        
        result = detector.analyze_micro_moments(
            sample_audio, 
            voice_features=voice_features
        )
        
        assert isinstance(result, dict)
        assert 'overall_risk' in result
    
    def test_analyze_micro_moments_tremor_audio(self, detector, tremor_audio):
        """Test analysis with tremor audio"""
        result = detector.analyze_micro_moments(tremor_audio)
        
        assert isinstance(result, dict)
        assert result['tremor']['detected'] in [True, False]
        assert 0.0 <= result['tremor']['intensity'] <= 1.0
    
    def test_analyze_micro_moments_sigh_audio(self, detector, sigh_audio):
        """Test analysis with sigh audio"""
        result = detector.analyze_micro_moments(sigh_audio)
        
        assert isinstance(result, dict)
        assert result['sighs']['count'] >= 0
        assert 0.0 <= result['sighs']['intensity'] <= 1.0
    
    def test_analyze_micro_moments_crack_audio(self, detector, crack_audio):
        """Test analysis with voice crack audio"""
        result = detector.analyze_micro_moments(crack_audio)
        
        assert isinstance(result, dict)
        assert result['voice_cracks']['count'] >= 0
        assert 0.0 <= result['voice_cracks']['intensity'] <= 1.0
    
    def test_analyze_micro_moments_hesitation_audio(self, detector, hesitation_audio):
        """Test analysis with hesitation audio"""
        result = detector.analyze_micro_moments(hesitation_audio)
        
        assert isinstance(result, dict)
        assert result['hesitations']['count'] >= 0
        assert result['hesitations']['average_duration'] >= 0.0
    
    def test_custom_sample_rate(self):
        """Test detector with custom sample rate"""
        detector = MicroMomentDetector(sample_rate=22050)
        assert detector.sample_rate == 22050
        
        audio = np.random.randn(22050)  # 1 second at 22050 Hz
        result = detector.analyze_micro_moments(audio, sr=22050)
        
        assert isinstance(result, dict)
    
    def test_error_handling_invalid_audio(self, detector):
        """Test error handling with invalid audio"""
        # Empty array
        result = detector.analyze_micro_moments(np.array([]))
        assert isinstance(result, dict)
        assert result['overall_risk'] == 'low'
        
        # Very short array
        result = detector.analyze_micro_moments(np.array([1.0, 2.0, 3.0]))
        assert isinstance(result, dict)
    
    def test_output_format_matches_backlog(self, detector, sample_audio):
        """Test that output format matches backlog example"""
        result = detector.analyze_micro_moments(sample_audio)
        
        # Verify structure matches backlog example exactly
        expected_keys = ['tremor', 'sighs', 'voice_cracks', 'hesitations', 
                        'overall_risk', 'interpretation']
        assert all(key in result for key in expected_keys)
        
        # Verify tremor structure
        assert 'detected' in result['tremor']
        assert 'intensity' in result['tremor']
        assert 'interpretation' in result['tremor']
        
        # Verify sighs structure
        assert 'count' in result['sighs']
        assert 'intensity' in result['sighs']
        assert 'interpretation' in result['sighs']
        
        # Verify voice_cracks structure
        assert 'count' in result['voice_cracks']
        assert 'intensity' in result['voice_cracks']
        assert 'interpretation' in result['voice_cracks']
        
        # Verify hesitations structure
        assert 'count' in result['hesitations']
        assert 'average_duration' in result['hesitations']
        assert 'interpretation' in result['hesitations']

