"""
Voice Simulator for Demo Data Generator

This module simulates voice processing and analysis without requiring actual audio files.
It generates realistic audio features, voice-truth dissonance patterns, and prosodic features
that demonstrate the ResonaAI voice analysis capabilities.
"""

import random
import math
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from ..interfaces import VoiceGeneratorInterface
from ..models import (
    AudioFeatures, VoiceTruthGap, EmotionType, DemoConfig, GenerationResult
)


class VoiceSimulator(VoiceGeneratorInterface):
    """Simulates voice analysis and audio feature extraction for demo purposes"""
    
    def __init__(self, config: Optional[DemoConfig] = None):
        self.config = config or DemoConfig()
        self.random = random.Random(42)  # Deterministic for reproducible demos
        
        # MFCC feature ranges for different emotions
        self.mfcc_emotion_profiles = {
            EmotionType.NEUTRAL: {"mean_range": (-2, 2), "std_range": (0.5, 1.5)},
            EmotionType.HAPPY: {"mean_range": (-1, 3), "std_range": (0.8, 2.0)},
            EmotionType.SAD: {"mean_range": (-3, 1), "std_range": (0.3, 1.0)},
            EmotionType.ANGRY: {"mean_range": (-1, 4), "std_range": (1.0, 2.5)},
            EmotionType.FEAR: {"mean_range": (-2, 2), "std_range": (1.2, 2.2)},
            EmotionType.SURPRISE: {"mean_range": (-1, 3), "std_range": (0.9, 2.1)},
            EmotionType.DISGUST: {"mean_range": (-2, 1), "std_range": (0.6, 1.4)}
        }
        
        # Spectral feature profiles for emotions
        self.spectral_emotion_profiles = {
            EmotionType.NEUTRAL: {
                "spectral_centroid": (1500, 2500),
                "spectral_bandwidth": (800, 1200),
                "spectral_rolloff": (3000, 4000),
                "zero_crossing_rate": (0.05, 0.15)
            },
            EmotionType.HAPPY: {
                "spectral_centroid": (2000, 3000),
                "spectral_bandwidth": (1000, 1500),
                "spectral_rolloff": (3500, 4500),
                "zero_crossing_rate": (0.08, 0.18)
            },
            EmotionType.SAD: {
                "spectral_centroid": (1200, 2000),
                "spectral_bandwidth": (600, 1000),
                "spectral_rolloff": (2500, 3500),
                "zero_crossing_rate": (0.03, 0.10)
            },
            EmotionType.ANGRY: {
                "spectral_centroid": (2200, 3200),
                "spectral_bandwidth": (1200, 1800),
                "spectral_rolloff": (4000, 5000),
                "zero_crossing_rate": (0.10, 0.25)
            },
            EmotionType.FEAR: {
                "spectral_centroid": (1800, 2800),
                "spectral_bandwidth": (900, 1400),
                "spectral_rolloff": (3200, 4200),
                "zero_crossing_rate": (0.12, 0.22)
            },
            EmotionType.SURPRISE: {
                "spectral_centroid": (2100, 3100),
                "spectral_bandwidth": (1100, 1600),
                "spectral_rolloff": (3800, 4800),
                "zero_crossing_rate": (0.09, 0.19)
            },
            EmotionType.DISGUST: {
                "spectral_centroid": (1400, 2200),
                "spectral_bandwidth": (700, 1100),
                "spectral_rolloff": (2800, 3800),
                "zero_crossing_rate": (0.04, 0.12)
            }
        }
        
        # Prosodic feature profiles for emotions
        self.prosodic_emotion_profiles = {
            EmotionType.NEUTRAL: {
                "pitch_mean": (150, 200),
                "pitch_std": (15, 25),
                "intensity_mean": (60, 70),
                "intensity_std": (5, 10),
                "speech_rate": (140, 160),
                "pause_duration": (0.3, 0.8)
            },
            EmotionType.HAPPY: {
                "pitch_mean": (180, 250),
                "pitch_std": (20, 35),
                "intensity_mean": (65, 75),
                "intensity_std": (8, 15),
                "speech_rate": (160, 200),
                "pause_duration": (0.2, 0.5)
            },
            EmotionType.SAD: {
                "pitch_mean": (120, 170),
                "pitch_std": (10, 20),
                "intensity_mean": (50, 60),
                "intensity_std": (3, 8),
                "speech_rate": (100, 130),
                "pause_duration": (0.5, 1.2)
            },
            EmotionType.ANGRY: {
                "pitch_mean": (170, 220),
                "pitch_std": (25, 40),
                "intensity_mean": (70, 85),
                "intensity_std": (10, 20),
                "speech_rate": (180, 220),
                "pause_duration": (0.1, 0.4)
            },
            EmotionType.FEAR: {
                "pitch_mean": (160, 210),
                "pitch_std": (20, 35),
                "intensity_mean": (55, 65),
                "intensity_std": (8, 15),
                "speech_rate": (120, 150),
                "pause_duration": (0.4, 0.9)
            },
            EmotionType.SURPRISE: {
                "pitch_mean": (190, 260),
                "pitch_std": (25, 40),
                "intensity_mean": (65, 75),
                "intensity_std": (10, 18),
                "speech_rate": (150, 180),
                "pause_duration": (0.2, 0.6)
            },
            EmotionType.DISGUST: {
                "pitch_mean": (140, 190),
                "pitch_std": (15, 25),
                "intensity_mean": (55, 65),
                "intensity_std": (5, 12),
                "speech_rate": (130, 160),
                "pause_duration": (0.3, 0.7)
            }
        }
    
    def simulate_audio_features(self, text: str, emotion: str) -> AudioFeatures:
        """Simulate audio feature extraction for given text and emotion"""
        emotion_enum = EmotionType(emotion)
        
        # Generate MFCC features
        mfcc_features = self._generate_mfcc_features(emotion_enum, len(text))
        
        # Generate spectral features
        spectral_features = self._generate_spectral_features(emotion_enum, text)
        
        # Generate prosodic features
        prosodic_features = self._generate_prosodic_features(emotion_enum, text)
        
        # Generate quality metrics
        quality_metrics = self._generate_quality_metrics(text)
        
        return AudioFeatures(
            mfcc=mfcc_features,
            spectral_features=spectral_features,
            prosodic_features=prosodic_features,
            quality_metrics=quality_metrics
        )
    
    def generate_voice_truth_gap(self, text_content: str, emotional_state: str) -> VoiceTruthGap:
        """Generate voice-truth gap analysis"""
        text_emotion = self._analyze_text_emotion(text_content)
        voice_emotion = EmotionType(emotional_state)
        
        # Calculate dissonance score based on emotional distance
        dissonance_score = self._calculate_emotional_distance(text_emotion, voice_emotion)
        
        # Add some randomness to make it more realistic
        dissonance_score += self.random.gauss(0, 0.1)
        dissonance_score = max(0.0, min(1.0, dissonance_score))
        
        # Generate confidence based on clarity of the gap
        confidence = self._calculate_gap_confidence(dissonance_score, text_content)
        
        # Generate indicators
        indicators = self._generate_gap_indicators(text_emotion, voice_emotion, dissonance_score)
        
        return VoiceTruthGap(
            text_emotion=text_emotion,
            voice_emotion=voice_emotion,
            dissonance_score=dissonance_score,
            confidence=confidence,
            indicators=indicators
        )
    
    def create_prosodic_features(self, speech_pattern: Dict[str, Any]) -> Dict[str, float]:
        """Create prosodic feature data from speech pattern"""
        # Extract emotion from speech pattern or default to neutral
        emotion = speech_pattern.get("emotion", EmotionType.NEUTRAL)
        if isinstance(emotion, str):
            emotion = EmotionType(emotion)
        
        # Get base prosodic profile for emotion
        profile = self.prosodic_emotion_profiles[emotion]
        
        # Generate features with realistic variation
        features = {}
        for feature_name, (min_val, max_val) in profile.items():
            base_value = self.random.uniform(min_val, max_val)
            
            # Add variation based on speech pattern characteristics
            if "stress_level" in speech_pattern:
                stress_factor = speech_pattern["stress_level"]
                if feature_name in ["pitch_std", "intensity_std"]:
                    base_value *= (1 + stress_factor * 0.3)
                elif feature_name == "speech_rate":
                    base_value *= (1 + stress_factor * 0.2)
            
            if "clarity" in speech_pattern:
                clarity = speech_pattern["clarity"]
                if feature_name in ["pitch_std", "intensity_std"]:
                    base_value *= (2 - clarity)  # Lower clarity = more variation
            
            features[feature_name] = base_value
        
        # Add derived features
        features["pitch_range"] = features["pitch_std"] * 4  # Approximate range
        features["intensity_range"] = features["intensity_std"] * 3
        features["articulation_rate"] = features["speech_rate"] * 0.8  # Slightly lower than speech rate
        features["pause_frequency"] = 1.0 / features["pause_duration"] if features["pause_duration"] > 0 else 0
        
        return features
    
    def generate(self, config: DemoConfig) -> GenerationResult:
        """Generate voice simulation data according to configuration"""
        start_time = datetime.now()
        
        try:
            # This would be called by the main orchestrator
            # For now, return a basic result
            generation_time = (datetime.now() - start_time).total_seconds()
            
            return GenerationResult(
                success=True,
                users_generated=0,  # This generator doesn't create users directly
                conversations_generated=0,  # This generator doesn't create conversations directly
                cultural_scenarios_generated=0,
                swahili_patterns_generated=0,
                output_directory=config.output_directory,
                generation_time_seconds=generation_time
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                users_generated=0,
                conversations_generated=0,
                cultural_scenarios_generated=0,
                swahili_patterns_generated=0,
                output_directory=config.output_directory,
                generation_time_seconds=(datetime.now() - start_time).total_seconds(),
                errors=[str(e)]
            )
    
    def validate_output(self, data: Any) -> bool:
        """Validate generated voice simulation data meets quality standards"""
        if isinstance(data, AudioFeatures):
            return (
                len(data.mfcc) > 0 and
                len(data.spectral_features) > 0 and
                len(data.prosodic_features) > 0 and
                all(isinstance(v, (int, float)) for v in data.mfcc) and
                all(isinstance(v, (int, float)) for v in data.spectral_features.values()) and
                all(isinstance(v, (int, float)) for v in data.prosodic_features.values())
            )
        elif isinstance(data, VoiceTruthGap):
            return (
                0.0 <= data.dissonance_score <= 1.0 and
                0.0 <= data.confidence <= 1.0 and
                data.text_emotion in EmotionType and
                data.voice_emotion in EmotionType
            )
        return False
    
    # Private helper methods
    
    def _generate_mfcc_features(self, emotion: EmotionType, text_length: int) -> List[float]:
        """Generate MFCC (Mel-Frequency Cepstral Coefficients) features"""
        profile = self.mfcc_emotion_profiles[emotion]
        
        # Number of MFCC coefficients (typically 12-13)
        num_coefficients = 13
        
        # Generate coefficients based on emotion profile
        mfcc_features = []
        for i in range(num_coefficients):
            # First coefficient (C0) represents energy, others represent spectral shape
            if i == 0:
                # Energy coefficient - higher for louder emotions
                energy_emotions = [EmotionType.ANGRY, EmotionType.HAPPY, EmotionType.SURPRISE]
                if emotion in energy_emotions:
                    coeff = self.random.uniform(2, 5)
                else:
                    coeff = self.random.uniform(-1, 2)
            else:
                # Spectral shape coefficients
                mean_min, mean_max = profile["mean_range"]
                std_min, std_max = profile["std_range"]
                
                mean = self.random.uniform(mean_min, mean_max)
                std = self.random.uniform(std_min, std_max)
                
                coeff = self.random.gauss(mean, std)
                
                # Add some correlation with text length (longer text = more variation)
                length_factor = min(1.0, text_length / 100.0)
                coeff += self.random.gauss(0, length_factor * 0.5)
            
            mfcc_features.append(coeff)
        
        return mfcc_features
    
    def _generate_spectral_features(self, emotion: EmotionType, text: str) -> Dict[str, float]:
        """Generate spectral features based on emotion and text"""
        profile = self.spectral_emotion_profiles[emotion]
        features = {}
        
        for feature_name, (min_val, max_val) in profile.items():
            base_value = self.random.uniform(min_val, max_val)
            
            # Adjust based on text characteristics
            if "!" in text or "?" in text:
                # Exclamation or question - increase spectral energy
                if feature_name in ["spectral_centroid", "spectral_bandwidth"]:
                    base_value *= 1.1
            
            if text.isupper():
                # All caps - simulate shouting
                if feature_name in ["spectral_centroid", "zero_crossing_rate"]:
                    base_value *= 1.2
            
            # Add some noise for realism
            noise = self.random.gauss(0, base_value * 0.05)
            features[feature_name] = max(0, base_value + noise)
        
        # Add derived spectral features
        features["spectral_contrast"] = self.random.uniform(10, 25)
        features["spectral_flatness"] = self.random.uniform(0.01, 0.1)
        features["spectral_flux"] = self.random.uniform(0.1, 0.5)
        
        return features
    
    def _generate_prosodic_features(self, emotion: EmotionType, text: str) -> Dict[str, float]:
        """Generate prosodic features based on emotion and text"""
        profile = self.prosodic_emotion_profiles[emotion]
        features = {}
        
        for feature_name, (min_val, max_val) in profile.items():
            base_value = self.random.uniform(min_val, max_val)
            
            # Adjust based on text characteristics
            text_length = len(text.split())
            
            if feature_name == "speech_rate":
                # Longer texts might have slightly different speech rates
                if text_length > 20:
                    base_value *= 0.95  # Slightly slower for longer texts
                elif text_length < 5:
                    base_value *= 1.05  # Slightly faster for short texts
            
            if feature_name in ["pitch_mean", "pitch_std"]:
                # Questions typically have higher pitch
                if "?" in text:
                    base_value *= 1.1
                # Statements might be lower
                elif "." in text and "!" not in text:
                    base_value *= 0.95
            
            if feature_name == "intensity_mean":
                # Exclamations are typically louder
                if "!" in text:
                    base_value *= 1.15
            
            features[feature_name] = base_value
        
        return features
    
    def _generate_quality_metrics(self, text: str) -> Dict[str, float]:
        """Generate audio quality metrics"""
        # Simulate realistic audio quality metrics
        base_snr = self.random.uniform(15, 35)  # Signal-to-noise ratio in dB
        
        # Longer texts might have slightly different quality
        length_factor = len(text) / 100.0
        quality_variation = self.random.gauss(0, length_factor * 2)
        
        return {
            "signal_to_noise_ratio": max(10, base_snr + quality_variation),
            "total_harmonic_distortion": self.random.uniform(0.01, 0.05),
            "dynamic_range": self.random.uniform(20, 40),
            "frequency_response_flatness": self.random.uniform(0.8, 0.98),
            "phase_coherence": self.random.uniform(0.85, 0.99),
            "clipping_detected": self.random.random() < 0.05,  # 5% chance of clipping
            "background_noise_level": self.random.uniform(-50, -30)  # dB
        }
    
    def _analyze_text_emotion(self, text: str) -> EmotionType:
        """Analyze text to determine likely emotion (simplified version)"""
        text_lower = text.lower()
        
        # Simple keyword-based emotion detection
        if any(word in text_lower for word in ["happy", "joy", "great", "wonderful", "excited"]):
            return EmotionType.HAPPY
        elif any(word in text_lower for word in ["sad", "depressed", "cry", "lonely", "empty"]):
            return EmotionType.SAD
        elif any(word in text_lower for word in ["angry", "furious", "hate", "mad", "annoyed"]):
            return EmotionType.ANGRY
        elif any(word in text_lower for word in ["scared", "afraid", "terrified", "worried", "anxious"]):
            return EmotionType.FEAR
        elif any(word in text_lower for word in ["wow", "amazing", "unexpected", "sudden", "shocked"]):
            return EmotionType.SURPRISE
        elif any(word in text_lower for word in ["disgusting", "gross", "sick", "revolting", "awful"]):
            return EmotionType.DISGUST
        else:
            return EmotionType.NEUTRAL
    
    def _calculate_emotional_distance(self, emotion1: EmotionType, emotion2: EmotionType) -> float:
        """Calculate emotional distance between two emotions"""
        if emotion1 == emotion2:
            return 0.0
        
        # Simplified emotional distance matrix
        distances = {
            (EmotionType.HAPPY, EmotionType.SAD): 0.9,
            (EmotionType.HAPPY, EmotionType.ANGRY): 0.7,
            (EmotionType.HAPPY, EmotionType.FEAR): 0.8,
            (EmotionType.HAPPY, EmotionType.DISGUST): 0.6,
            (EmotionType.HAPPY, EmotionType.SURPRISE): 0.3,
            (EmotionType.HAPPY, EmotionType.NEUTRAL): 0.4,
            
            (EmotionType.SAD, EmotionType.ANGRY): 0.5,
            (EmotionType.SAD, EmotionType.FEAR): 0.4,
            (EmotionType.SAD, EmotionType.DISGUST): 0.6,
            (EmotionType.SAD, EmotionType.SURPRISE): 0.7,
            (EmotionType.SAD, EmotionType.NEUTRAL): 0.5,
            
            (EmotionType.ANGRY, EmotionType.FEAR): 0.6,
            (EmotionType.ANGRY, EmotionType.DISGUST): 0.3,
            (EmotionType.ANGRY, EmotionType.SURPRISE): 0.8,
            (EmotionType.ANGRY, EmotionType.NEUTRAL): 0.7,
            
            (EmotionType.FEAR, EmotionType.DISGUST): 0.5,
            (EmotionType.FEAR, EmotionType.SURPRISE): 0.4,
            (EmotionType.FEAR, EmotionType.NEUTRAL): 0.6,
            
            (EmotionType.DISGUST, EmotionType.SURPRISE): 0.7,
            (EmotionType.DISGUST, EmotionType.NEUTRAL): 0.5,
            
            (EmotionType.SURPRISE, EmotionType.NEUTRAL): 0.4
        }
        
        # Try both directions
        key = (emotion1, emotion2)
        reverse_key = (emotion2, emotion1)
        
        return distances.get(key, distances.get(reverse_key, 0.5))
    
    def _calculate_gap_confidence(self, dissonance_score: float, text: str) -> float:
        """Calculate confidence in voice-truth gap detection"""
        # Base confidence increases with dissonance score
        base_confidence = 0.3 + (dissonance_score * 0.6)
        
        # Longer texts provide more data for analysis
        length_factor = min(1.0, len(text.split()) / 20.0)
        confidence_boost = length_factor * 0.2
        
        # Add some randomness
        noise = self.random.gauss(0, 0.1)
        
        final_confidence = base_confidence + confidence_boost + noise
        return max(0.1, min(0.95, final_confidence))
    
    def _generate_gap_indicators(self, text_emotion: EmotionType, voice_emotion: EmotionType, 
                                dissonance_score: float) -> List[str]:
        """Generate indicators that suggest voice-truth gap"""
        indicators = []
        
        # Base indicators based on dissonance score
        if dissonance_score > 0.7:
            indicators.extend(["strong_prosodic_mismatch", "significant_vocal_tension"])
        elif dissonance_score > 0.4:
            indicators.extend(["moderate_prosodic_mismatch", "vocal_strain_detected"])
        elif dissonance_score > 0.2:
            indicators.extend(["subtle_prosodic_inconsistency"])
        
        # Specific indicators based on emotion combinations
        if text_emotion == EmotionType.NEUTRAL and voice_emotion in [EmotionType.SAD, EmotionType.ANGRY]:
            indicators.extend(["emotional_suppression", "vocal_leakage"])
        
        if text_emotion == EmotionType.HAPPY and voice_emotion == EmotionType.SAD:
            indicators.extend(["forced_positivity", "underlying_sadness"])
        
        if voice_emotion == EmotionType.ANGRY and text_emotion != EmotionType.ANGRY:
            indicators.extend(["suppressed_anger", "vocal_intensity_mismatch"])
        
        if voice_emotion == EmotionType.FEAR and text_emotion not in [EmotionType.FEAR, EmotionType.SURPRISE]:
            indicators.extend(["hidden_anxiety", "vocal_tremor"])
        
        # Add some general technical indicators
        technical_indicators = [
            "pitch_contour_anomaly", "intensity_pattern_mismatch", 
            "spectral_inconsistency", "temporal_pattern_disruption"
        ]
        indicators.extend(self.random.sample(technical_indicators, 
                                           min(2, len(technical_indicators))))
        
        return list(set(indicators))  # Remove duplicates