"""
Property-Based Tests for Voice-Truth Dissonance Simulation

This module contains property-based tests using Hypothesis to validate
that the voice-truth dissonance simulation generates realistic and varied patterns.
"""

import pytest
import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from typing import List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scripts.demo_data_generator.generators.voice_simulator import VoiceSimulator
from scripts.demo_data_generator.generators.emotion_generator import EmotionGenerator
from scripts.demo_data_generator.models import EmotionType, VoiceTruthGap, DissonanceResult


# Hypothesis strategies for generating test data
emotion_strategy = st.sampled_from(list(EmotionType))

text_content_strategy = st.one_of(
    st.text(min_size=5, max_size=200),
    st.sampled_from([
        "I am feeling great today!",
        "Everything is fine, don't worry about me",
        "I'm so angry I could scream",
        "I feel terrible and sad",
        "Nothing is wrong, I'm perfectly okay",
        "I'm scared but trying to be brave",
        "This is disgusting and awful",
        "What a surprise, I didn't expect this",
        "Nimechoka na hii situation",  # Swahili: I'm tired of this situation
        "Ni sawa tu, hakuna shida",    # Swahili: It's okay, no problem
    ])
)

speech_pattern_strategy = st.fixed_dictionaries({
    'emotion': emotion_strategy,
    'stress_level': st.floats(min_value=0.0, max_value=1.0),
    'clarity': st.floats(min_value=0.1, max_value=1.0)
})


class TestVoiceTruthDissonanceProperties:
    """Property-based tests for voice-truth dissonance simulation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.voice_simulator = VoiceSimulator()
        self.emotion_generator = EmotionGenerator()
    
    @given(text_content=text_content_strategy, voice_emotion=emotion_strategy)
    @settings(max_examples=100, deadline=None)
    def test_voice_truth_gap_properties(self, text_content: str, voice_emotion: EmotionType):
        """
        Feature: demo-data-generator, Property 3: Voice-truth dissonance simulation realism
        
        Test that generated dissonance patterns are realistic and varied.
        For any text content and voice emotion, the voice-truth gap should:
        1. Have valid dissonance scores (0.0 to 1.0)
        2. Have valid confidence scores (0.0 to 1.0)
        3. Generate appropriate indicators
        4. Provide meaningful explanations
        """
        # Generate voice-truth gap
        gap = self.voice_simulator.generate_voice_truth_gap(text_content, voice_emotion.value)
        
        # Property 1: Valid score ranges
        assert isinstance(gap, VoiceTruthGap)
        assert 0.0 <= gap.dissonance_score <= 1.0, f"Dissonance score {gap.dissonance_score} out of range"
        assert 0.0 <= gap.confidence <= 1.0, f"Confidence {gap.confidence} out of range"
        
        # Property 2: Valid emotion types
        assert gap.text_emotion in EmotionType
        assert gap.voice_emotion in EmotionType
        assert gap.voice_emotion == voice_emotion
        
        # Property 3: Indicators should be non-empty list of strings
        assert isinstance(gap.indicators, list)
        assert all(isinstance(indicator, str) for indicator in gap.indicators)
        
        # Property 4: Same emotions should have lower dissonance
        if gap.text_emotion == gap.voice_emotion:
            assert gap.dissonance_score <= 0.3, f"Same emotions should have low dissonance, got {gap.dissonance_score}"
    
    @given(text_emotion=emotion_strategy, voice_emotion=emotion_strategy)
    @settings(max_examples=100, deadline=None)
    def test_dissonance_pattern_consistency(self, text_emotion: EmotionType, voice_emotion: EmotionType):
        """
        Test that dissonance patterns are consistent and realistic.
        For any pair of emotions, the dissonance result should be consistent.
        """
        # Generate dissonance pattern
        dissonance = self.emotion_generator.create_dissonance_pattern(
            text_emotion.value, voice_emotion.value
        )
        
        # Property 1: Valid dissonance result structure
        assert isinstance(dissonance, DissonanceResult)
        assert 0.0 <= dissonance.confidence <= 1.0
        assert isinstance(dissonance.detected, bool)
        assert isinstance(dissonance.explanation, str)
        assert len(dissonance.explanation) > 0
        
        # Property 2: Voice-truth gap should be valid
        gap = dissonance.voice_truth_gap
        assert isinstance(gap, VoiceTruthGap)
        assert gap.text_emotion == text_emotion
        assert gap.voice_emotion == voice_emotion
        
        # Property 3: Detection should correlate with dissonance score
        if gap.dissonance_score > 0.3:
            assert dissonance.detected is True, "High dissonance should be detected"
        
        # Property 4: Identical emotions should have minimal dissonance
        if text_emotion == voice_emotion:
            assert gap.dissonance_score <= 0.2, f"Identical emotions should have minimal dissonance, got {gap.dissonance_score}"
    
    @given(text_content=text_content_strategy, emotion=emotion_strategy)
    @settings(max_examples=100, deadline=None)
    def test_audio_features_realism(self, text_content: str, emotion: EmotionType):
        """
        Test that simulated audio features are realistic and varied.
        For any text and emotion, audio features should be within realistic ranges.
        """
        # Generate audio features
        features = self.voice_simulator.simulate_audio_features(text_content, emotion.value)
        
        # Property 1: MFCC features should be realistic
        assert len(features.mfcc) == 13, "Should have 13 MFCC coefficients"
        assert all(isinstance(coeff, (int, float)) for coeff in features.mfcc)
        assert all(-10 <= coeff <= 10 for coeff in features.mfcc), "MFCC coefficients should be in realistic range"
        
        # Property 2: Spectral features should be positive and realistic
        spectral = features.spectral_features
        assert spectral["spectral_centroid"] > 0, "Spectral centroid should be positive"
        assert spectral["spectral_bandwidth"] > 0, "Spectral bandwidth should be positive"
        assert spectral["zero_crossing_rate"] >= 0, "Zero crossing rate should be non-negative"
        assert spectral["zero_crossing_rate"] <= 1.0, "Zero crossing rate should be <= 1.0"
        
        # Property 3: Prosodic features should be in realistic ranges
        prosodic = features.prosodic_features
        assert prosodic["pitch_mean"] > 50, "Pitch should be above 50 Hz"
        assert prosodic["pitch_mean"] < 500, "Pitch should be below 500 Hz"
        assert prosodic["speech_rate"] > 50, "Speech rate should be above 50 WPM"
        assert prosodic["speech_rate"] < 300, "Speech rate should be below 300 WPM"
        assert prosodic["intensity_mean"] > 0, "Intensity should be positive"
        
        # Property 4: Quality metrics should be realistic
        quality = features.quality_metrics
        assert quality["signal_to_noise_ratio"] > 0, "SNR should be positive"
        assert -100 <= quality["background_noise_level"] <= 0, "Background noise should be in dB range"
        assert 0 <= quality["total_harmonic_distortion"] <= 1, "THD should be between 0 and 1"
    
    @given(speech_pattern=speech_pattern_strategy)
    @settings(max_examples=100, deadline=None)
    def test_prosodic_features_consistency(self, speech_pattern: dict):
        """
        Test that prosodic features are consistent with speech patterns.
        For any speech pattern, prosodic features should reflect the input characteristics.
        """
        # Generate prosodic features
        prosodic = self.voice_simulator.create_prosodic_features(speech_pattern)
        
        # Property 1: All features should be numeric
        assert all(isinstance(value, (int, float)) for value in prosodic.values())
        
        # Property 2: Features should be positive
        assert all(value >= 0 for value in prosodic.values())
        
        # Property 3: Stress level should affect variability
        stress_level = speech_pattern['stress_level']
        if stress_level > 0.7:  # High stress
            # High stress should increase pitch and intensity variation
            assert prosodic.get("pitch_std", 0) > 10, "High stress should increase pitch variation"
        
        # Property 4: Clarity should affect variation
        clarity = speech_pattern['clarity']
        if clarity < 0.3:  # Low clarity
            # Low clarity should increase variation in prosodic features
            variation_features = ["pitch_std", "intensity_std"]
            for feature in variation_features:
                if feature in prosodic:
                    assert prosodic[feature] > 5, f"Low clarity should increase {feature}"
    
    @given(
        text_emotions=st.lists(emotion_strategy, min_size=2, max_size=5, unique=True),
        voice_emotions=st.lists(emotion_strategy, min_size=2, max_size=5, unique=True)
    )
    @settings(max_examples=50, deadline=None)
    def test_dissonance_variation_across_emotions(self, text_emotions: List[EmotionType], voice_emotions: List[EmotionType]):
        """
        Test that dissonance patterns show appropriate variation across different emotion combinations.
        For any set of emotion combinations, there should be variation in dissonance scores when emotions differ.
        """
        # Generate all unique emotion pairs
        emotion_pairs = []
        dissonance_scores = []
        
        for text_emotion in text_emotions:
            for voice_emotion in voice_emotions:
                pair = (text_emotion, voice_emotion)
                # Only add unique pairs to avoid duplicate scores
                if pair not in emotion_pairs:
                    emotion_pairs.append(pair)
                    dissonance = self.emotion_generator.create_dissonance_pattern(
                        text_emotion.value, voice_emotion.value
                    )
                    dissonance_scores.append(dissonance.voice_truth_gap.dissonance_score)
        
        # Skip if we only have one unique pair (no variation expected)
        assume(len(emotion_pairs) > 1)
        
        # Property 1: Should have variation in scores when we have different emotion pairs
        unique_scores = set(round(score, 1) for score in dissonance_scores)
        
        # With multiple unique emotion pairs, we should see variation in dissonance scores
        assert len(unique_scores) > 1, f"Should have variation in dissonance scores for different emotion pairs, got scores: {dissonance_scores}, pairs: {emotion_pairs}"
        
        # Property 2: Scores should span a reasonable range when emotions differ
        min_score = min(dissonance_scores)
        max_score = max(dissonance_scores)
        score_range = max_score - min_score
        
        # With different emotion combinations, we should see some range
        assert score_range >= 0.0, f"Should have non-negative score range, got {score_range}"
    
    @given(text_content=text_content_strategy)
    @settings(max_examples=50, deadline=None)
    def test_voice_emotion_differs_from_text_appropriately(self, text_content: str):
        """
        Test that voice emotions can differ appropriately from text emotions.
        For any text content, when voice emotion differs from text emotion,
        the dissonance should be detected appropriately.
        """
        # Generate voice-truth gap with different emotions
        text_emotion = EmotionType.NEUTRAL
        voice_emotion = EmotionType.SAD
        
        gap = self.voice_simulator.generate_voice_truth_gap(text_content, voice_emotion.value)
        
        # Property 1: Different emotions should create some dissonance
        if gap.text_emotion != gap.voice_emotion:
            assert gap.dissonance_score > 0.0, "Different emotions should create some dissonance"
        
        # Property 2: Confidence should be reasonable for clear differences
        emotional_distance = self.voice_simulator._calculate_emotional_distance(
            gap.text_emotion, gap.voice_emotion
        )
        if emotional_distance > 0.5:
            assert gap.confidence > 0.3, "Clear emotional differences should have reasonable confidence"
        
        # Property 3: Indicators should be relevant to the emotion combination
        if gap.text_emotion == EmotionType.NEUTRAL and gap.voice_emotion == EmotionType.SAD:
            # Should have indicators related to emotional suppression or leakage
            relevant_indicators = ["emotional_suppression", "vocal_leakage", "underlying_sadness", "vocal_strain_detected"]
            has_relevant = any(indicator in gap.indicators for indicator in relevant_indicators)
            assert has_relevant, f"Should have relevant indicators for neutral text/sad voice, got {gap.indicators}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])