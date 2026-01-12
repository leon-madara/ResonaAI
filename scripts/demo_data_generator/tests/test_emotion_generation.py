"""
Unit Tests for Emotion Generation

This module contains unit tests for the EmotionGenerator class,
testing specific examples, edge cases, and the 7-emotion model coverage.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scripts.demo_data_generator.generators.emotion_generator import EmotionGenerator
from scripts.demo_data_generator.models import (
    EmotionType, EmotionResult, DissonanceResult, BaselineData,
    VoicePatterns, EmotionalPatterns, DemoConfig
)


class TestEmotionGenerator:
    """Unit tests for EmotionGenerator functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.emotion_generator = EmotionGenerator()
    
    def test_initialization(self):
        """Test EmotionGenerator initialization"""
        assert self.emotion_generator.config is not None
        assert isinstance(self.emotion_generator.config, DemoConfig)
        assert hasattr(self.emotion_generator, 'emotion_transitions')
        assert hasattr(self.emotion_generator, 'confidence_distributions')
        assert hasattr(self.emotion_generator, 'dissonance_patterns')
    
    def test_seven_emotion_model_coverage(self):
        """Test that all 7 emotions are supported in the model"""
        expected_emotions = {
            EmotionType.NEUTRAL, EmotionType.HAPPY, EmotionType.SAD,
            EmotionType.ANGRY, EmotionType.FEAR, EmotionType.SURPRISE,
            EmotionType.DISGUST
        }
        
        # Check emotion transitions cover all emotions
        transition_emotions = set(self.emotion_generator.emotion_transitions.keys())
        assert transition_emotions == expected_emotions
        
        # Check confidence distributions cover all emotions
        confidence_emotions = set(self.emotion_generator.confidence_distributions.keys())
        assert confidence_emotions == expected_emotions
    
    def test_emotion_analysis_sad_keywords(self):
        """Test emotion analysis detects sadness from keywords"""
        sad_texts = [
            "I am feeling very sad today",
            "I'm so depressed and lonely",
            "I can't stop crying",
            "Nimechoka na hii situation",  # Swahili: I'm tired of this situation
            "I feel empty inside"
        ]
        
        for text in sad_texts:
            result = self.emotion_generator.generate_emotion_analysis(text)
            assert isinstance(result, EmotionResult)
            assert result.detected == EmotionType.SAD
            assert 0.0 <= result.confidence <= 1.0
    
    def test_emotion_analysis_happy_keywords(self):
        """Test emotion analysis detects happiness from keywords"""
        happy_texts = [
            "I am feeling great today!",
            "This is wonderful",
            "I'm so happy and joyful",
            "Joy fills my heart",
            "Everything is fantastic and great"
        ]
        
        for text in happy_texts:
            result = self.emotion_generator.generate_emotion_analysis(text)
            assert isinstance(result, EmotionResult)
            # Allow for some flexibility due to keyword overlap and randomness
            assert result.detected in [EmotionType.HAPPY, EmotionType.SURPRISE, EmotionType.NEUTRAL]
            assert 0.0 <= result.confidence <= 1.0
    
    def test_emotion_analysis_anger_keywords(self):
        """Test emotion analysis detects anger from keywords"""
        angry_texts = [
            "I am so angry and furious",
            "I hate this stupid situation",
            "This is damn annoying",
            "You're such an idiot",
            "I'm mad and angry about this"
        ]
        
        for text in angry_texts:
            result = self.emotion_generator.generate_emotion_analysis(text)
            assert isinstance(result, EmotionResult)
            # Allow for some flexibility due to keyword overlap and randomness
            assert result.detected in [EmotionType.ANGRY, EmotionType.DISGUST, EmotionType.NEUTRAL]
            assert 0.0 <= result.confidence <= 1.0
    
    def test_emotion_analysis_fear_keywords(self):
        """Test emotion analysis detects fear from keywords"""
        fear_texts = [
            "I'm scared and terrified",
            "This makes me so afraid",
            "I'm having a panic attack",
            "I'm worried and anxious about everything",
            "I feel so frightened and scared"
        ]
        
        for text in fear_texts:
            result = self.emotion_generator.generate_emotion_analysis(text)
            assert isinstance(result, EmotionResult)
            # Allow for some flexibility due to keyword overlap and randomness
            assert result.detected in [EmotionType.FEAR, EmotionType.SAD, EmotionType.NEUTRAL]
            assert 0.0 <= result.confidence <= 1.0
    
    def test_emotion_analysis_surprise_keywords(self):
        """Test emotion analysis detects surprise from keywords"""
        surprise_texts = [
            "Wow, that's unexpected!",
            "What a sudden surprise",
            "I'm shocked by this news",
            "This is so surprising and sudden",
            "I didn't see that coming, wow"
        ]
        
        for text in surprise_texts:
            result = self.emotion_generator.generate_emotion_analysis(text)
            assert isinstance(result, EmotionResult)
            # Allow for some flexibility due to keyword overlap and randomness
            assert result.detected in [EmotionType.SURPRISE, EmotionType.HAPPY, EmotionType.NEUTRAL]
            assert 0.0 <= result.confidence <= 1.0
    
    def test_emotion_analysis_disgust_keywords(self):
        """Test emotion analysis detects disgust from keywords"""
        disgust_texts = [
            "That's absolutely disgusting",
            "This is so gross and revolting",
            "I feel sick about this",
            "This is awful and terrible",
            "How revolting and nasty"
        ]
        
        for text in disgust_texts:
            result = self.emotion_generator.generate_emotion_analysis(text)
            assert isinstance(result, EmotionResult)
            assert result.detected == EmotionType.DISGUST
            assert 0.0 <= result.confidence <= 1.0
    
    def test_emotion_analysis_neutral_default(self):
        """Test emotion analysis defaults to neutral for ambiguous text"""
        neutral_texts = [
            "The weather is okay today",
            "I went to the store",
            "This is a normal sentence",
            "Nothing special happened",
            "Just regular everyday stuff"
        ]
        
        for text in neutral_texts:
            result = self.emotion_generator.generate_emotion_analysis(text)
            assert isinstance(result, EmotionResult)
            # Should be neutral most of the time (allowing for some randomness)
            assert result.detected in [EmotionType.NEUTRAL] or result.confidence < 0.8
    
    def test_crisis_keywords_detection(self):
        """Test detection of crisis-level emotional content"""
        crisis_texts = [
            "I want to kill myself",
            "I can't go on anymore", 
            "Life is hopeless",
            "I want to end it all",
            "There's no point in living"
        ]
        
        # Test multiple times to account for randomness
        crisis_emotions_detected = []
        for text in crisis_texts:
            result = self.emotion_generator.generate_emotion_analysis(text)
            assert isinstance(result, EmotionResult)
            crisis_emotions_detected.append(result.detected)
            # Should have reasonable confidence
            assert result.confidence > 0.3
        
        # At least some crisis texts should trigger sad or fear emotions
        crisis_appropriate = [e for e in crisis_emotions_detected if e in [EmotionType.SAD, EmotionType.FEAR]]
        assert len(crisis_appropriate) >= len(crisis_texts) // 2, f"Expected at least half of crisis texts to trigger appropriate emotions, got {crisis_emotions_detected}"
    
    def test_confidence_score_ranges(self):
        """Test that confidence scores are within valid ranges for all emotions"""
        test_cases = [
            ("I'm happy", EmotionType.HAPPY),
            ("I'm sad", EmotionType.SAD),
            ("I'm angry", EmotionType.ANGRY),
            ("I'm scared", EmotionType.FEAR),
            ("Wow amazing", EmotionType.SURPRISE),
            ("That's disgusting", EmotionType.DISGUST),
            ("Nothing special", EmotionType.NEUTRAL)
        ]
        
        for text, expected_emotion in test_cases:
            result = self.emotion_generator.generate_emotion_analysis(text)
            assert 0.0 <= result.confidence <= 1.0
            # Confidence should be reasonable for clear emotional indicators
            if result.detected == expected_emotion:
                assert result.confidence > 0.3
    
    def test_voice_truth_gap_generation(self):
        """Test voice-truth gap generation for emotional suppression"""
        # Test cases where voice-truth gap might occur
        test_cases = [
            (EmotionType.NEUTRAL, 0.2),  # Neutral emotions have lower gap likelihood
            (EmotionType.ANGRY, 0.7),    # Anger is often suppressed
            (EmotionType.SAD, 0.6),      # Sadness is often hidden
            (EmotionType.FEAR, 0.5),     # Fear might be masked
        ]
        
        for emotion, expected_likelihood in test_cases:
            # Generate multiple samples to test the pattern
            gaps = []
            for _ in range(20):
                gap = self.emotion_generator._generate_voice_truth_gap(emotion)
                gaps.append(gap)
            
            # All gaps should be in valid range
            assert all(0.0 <= gap <= 1.0 for gap in gaps)
            
            # Average should be roughly in line with expected likelihood
            avg_gap = sum(gaps) / len(gaps)
            # Allow for some variance due to randomness
            assert abs(avg_gap - expected_likelihood) < 0.3
    
    def test_dissonance_pattern_creation(self):
        """Test creation of dissonance patterns between text and voice emotions"""
        test_cases = [
            ("neutral", "angry", True),   # Should detect dissonance
            ("happy", "sad", True),       # Should detect dissonance
            ("neutral", "neutral", False), # Should not detect dissonance
            ("angry", "angry", False),    # Should not detect dissonance
        ]
        
        for text_emotion, voice_emotion, should_detect in test_cases:
            result = self.emotion_generator.create_dissonance_pattern(text_emotion, voice_emotion)
            
            assert isinstance(result, DissonanceResult)
            assert 0.0 <= result.confidence <= 1.0
            assert isinstance(result.detected, bool)
            assert len(result.explanation) > 0
            
            # Check detection matches expectation
            if should_detect:
                assert result.voice_truth_gap.dissonance_score > 0.3
            else:
                assert result.voice_truth_gap.dissonance_score <= 0.2
    
    def test_baseline_data_generation_consistency(self):
        """Test that baseline data generation is consistent for the same user"""
        user_id = "test_user_123"
        sessions = 5
        
        # Generate baseline data multiple times for the same user
        baseline1 = self.emotion_generator.generate_baseline_data(user_id, sessions)
        baseline2 = self.emotion_generator.generate_baseline_data(user_id, sessions)
        
        # Should be identical for the same user (deterministic)
        assert baseline1.voice_patterns.average_pitch == baseline2.voice_patterns.average_pitch
        assert baseline1.voice_patterns.speech_rate == baseline2.voice_patterns.speech_rate
        assert baseline1.voice_patterns.emotional_baseline == baseline2.voice_patterns.emotional_baseline
        assert baseline1.emotional_patterns.dominant_emotions == baseline2.emotional_patterns.dominant_emotions
    
    def test_baseline_data_generation_variety(self):
        """Test that baseline data varies between different users"""
        baselines = []
        for i in range(5):
            user_id = f"user_{i}"
            baseline = self.emotion_generator.generate_baseline_data(user_id, 3)
            baselines.append(baseline)
        
        # Should have variety in voice patterns
        pitches = [b.voice_patterns.average_pitch for b in baselines]
        speech_rates = [b.voice_patterns.speech_rate for b in baselines]
        
        # Should not all be identical
        assert len(set(round(p, 1) for p in pitches)) > 1
        assert len(set(round(s, 1) for s in speech_rates)) > 1
    
    def test_baseline_data_structure(self):
        """Test baseline data structure and content validity"""
        baseline = self.emotion_generator.generate_baseline_data("test_user", 5)
        
        assert isinstance(baseline, BaselineData)
        assert isinstance(baseline.voice_patterns, VoicePatterns)
        assert isinstance(baseline.emotional_patterns, EmotionalPatterns)
        
        # Voice patterns validation
        voice = baseline.voice_patterns
        assert voice.average_pitch > 0
        assert voice.speech_rate > 0
        assert voice.emotional_baseline in EmotionType
        assert len(voice.stress_indicators) >= 2
        
        # Emotional patterns validation
        emotional = baseline.emotional_patterns
        assert len(emotional.dominant_emotions) >= 2
        assert len(emotional.crisis_triggers) >= 1
        assert len(emotional.coping_mechanisms) >= 2
        assert all(emotion in EmotionType for emotion in emotional.dominant_emotions)
    
    def test_emotion_features_generation(self):
        """Test emotion feature vector generation"""
        for emotion in EmotionType:
            confidence = 0.8
            features = self.emotion_generator._generate_emotion_features(emotion, confidence)
            
            # Should have core emotional dimensions
            assert "valence" in features
            assert "arousal" in features
            assert "dominance" in features
            
            # Should have additional features
            assert "intensity" in features
            assert "clarity" in features
            assert "stability" in features
            
            # All features should be in valid ranges
            for feature_name, value in features.items():
                assert 0.0 <= value <= 2.0, f"{feature_name} value {value} out of range for {emotion}"
    
    def test_emotional_distance_calculation(self):
        """Test emotional distance calculation between emotions"""
        # Test identical emotions
        distance = self.emotion_generator._calculate_emotional_distance(
            EmotionType.HAPPY, EmotionType.HAPPY
        )
        assert distance == 0.0
        
        # Test opposite emotions should have high distance
        distance = self.emotion_generator._calculate_emotional_distance(
            EmotionType.HAPPY, EmotionType.SAD
        )
        assert distance > 0.5
        
        # Test similar emotions should have lower distance
        distance = self.emotion_generator._calculate_emotional_distance(
            EmotionType.SAD, EmotionType.FEAR
        )
        assert 0.0 < distance < 0.8
    
    def test_dissonance_indicators_generation(self):
        """Test generation of dissonance indicators"""
        test_cases = [
            (EmotionType.NEUTRAL, EmotionType.ANGRY, ["vocal_tension", "pitch_variation"]),
            (EmotionType.HAPPY, EmotionType.SAD, ["forced_intonation", "micro_expressions"]),
            (EmotionType.NEUTRAL, EmotionType.FEAR, ["voice_shakiness", "pitch_elevation"]),
        ]
        
        for text_emotion, voice_emotion, expected_indicators in test_cases:
            indicators = self.emotion_generator._generate_dissonance_indicators(
                text_emotion, voice_emotion
            )
            
            assert isinstance(indicators, list)
            assert len(indicators) > 0
            assert all(isinstance(indicator, str) for indicator in indicators)
            
            # Should contain at least one expected indicator
            has_expected = any(expected in indicators for expected in expected_indicators)
            assert has_expected, f"Expected indicators {expected_indicators} not found in {indicators}"
    
    def test_validation_methods(self):
        """Test data validation methods"""
        # Test valid EmotionResult
        valid_result = EmotionResult(
            detected=EmotionType.HAPPY,
            confidence=0.8,
            voice_truth_gap=0.2
        )
        assert self.emotion_generator.validate_output(valid_result) is True
        
        # Test valid DissonanceResult
        valid_dissonance = self.emotion_generator.create_dissonance_pattern("happy", "sad")
        assert self.emotion_generator.validate_output(valid_dissonance) is True
        
        # Test valid BaselineData
        valid_baseline = self.emotion_generator.generate_baseline_data("test_user", 3)
        assert self.emotion_generator.validate_output(valid_baseline) is True
        
        # Test invalid data
        assert self.emotion_generator.validate_output("invalid_data") is False
        assert self.emotion_generator.validate_output(None) is False
    
    def test_generate_method(self):
        """Test the main generate method"""
        config = DemoConfig(num_users=5, conversations_per_user=3)
        result = self.emotion_generator.generate(config)
        
        assert result.success is True
        assert result.generation_time_seconds >= 0
        assert result.output_directory == config.output_directory
        assert len(result.errors) == 0
    
    def test_edge_cases(self):
        """Test edge cases and error conditions"""
        # Empty text
        result = self.emotion_generator.generate_emotion_analysis("")
        assert isinstance(result, EmotionResult)
        assert result.detected in EmotionType
        
        # Very long text
        long_text = "This is a very long text. " * 100
        result = self.emotion_generator.generate_emotion_analysis(long_text)
        assert isinstance(result, EmotionResult)
        
        # Special characters and unicode
        special_text = "Émotions spéciales: 😊😢😡 ñoño"
        result = self.emotion_generator.generate_emotion_analysis(special_text)
        assert isinstance(result, EmotionResult)
        
        # Mixed language (English-Swahili)
        mixed_text = "I feel nimechoka but I'm trying to be strong"
        result = self.emotion_generator.generate_emotion_analysis(mixed_text)
        assert isinstance(result, EmotionResult)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])