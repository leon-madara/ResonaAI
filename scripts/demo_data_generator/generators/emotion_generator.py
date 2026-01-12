"""
Emotion Generator for Demo Data Generator

This module generates realistic emotion analysis data including:
- 7-emotion model analysis with confidence scores
- Voice-truth dissonance patterns
- Baseline tracking data over multiple sessions
- Realistic emotional feature vectors
"""

import random
import math
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from ..interfaces import EmotionGeneratorInterface
from ..models import (
    EmotionResult, EmotionType, DissonanceResult, VoiceTruthGap,
    BaselineData, VoicePatterns, EmotionalPatterns, CrisisLevel,
    DemoConfig, GenerationResult
)


class EmotionGenerator(EmotionGeneratorInterface):
    """Generates realistic emotion analysis data for demo purposes"""
    
    def __init__(self, config: Optional[DemoConfig] = None):
        self.config = config or DemoConfig()
        self.random = random.Random(42)  # Deterministic for reproducible demos
        
        # Emotion transition probabilities for realistic progressions
        self.emotion_transitions = {
            EmotionType.NEUTRAL: {
                EmotionType.HAPPY: 0.3,
                EmotionType.SAD: 0.2,
                EmotionType.ANGRY: 0.1,
                EmotionType.FEAR: 0.15,
                EmotionType.SURPRISE: 0.15,
                EmotionType.DISGUST: 0.05,
                EmotionType.NEUTRAL: 0.05
            },
            EmotionType.HAPPY: {
                EmotionType.NEUTRAL: 0.4,
                EmotionType.SURPRISE: 0.3,
                EmotionType.SAD: 0.1,
                EmotionType.HAPPY: 0.2
            },
            EmotionType.SAD: {
                EmotionType.NEUTRAL: 0.3,
                EmotionType.ANGRY: 0.2,
                EmotionType.FEAR: 0.2,
                EmotionType.HAPPY: 0.1,
                EmotionType.SAD: 0.2
            },
            EmotionType.ANGRY: {
                EmotionType.NEUTRAL: 0.25,
                EmotionType.SAD: 0.25,
                EmotionType.DISGUST: 0.2,
                EmotionType.FEAR: 0.1,
                EmotionType.ANGRY: 0.2
            },
            EmotionType.FEAR: {
                EmotionType.NEUTRAL: 0.3,
                EmotionType.SAD: 0.25,
                EmotionType.ANGRY: 0.15,
                EmotionType.SURPRISE: 0.1,
                EmotionType.FEAR: 0.2
            },
            EmotionType.SURPRISE: {
                EmotionType.NEUTRAL: 0.35,
                EmotionType.HAPPY: 0.25,
                EmotionType.FEAR: 0.15,
                EmotionType.ANGRY: 0.1,
                EmotionType.SURPRISE: 0.15
            },
            EmotionType.DISGUST: {
                EmotionType.NEUTRAL: 0.3,
                EmotionType.ANGRY: 0.3,
                EmotionType.SAD: 0.2,
                EmotionType.DISGUST: 0.2
            }
        }
        
        # Confidence score distributions for each emotion
        self.confidence_distributions = {
            EmotionType.NEUTRAL: (0.7, 0.15),  # (mean, std)
            EmotionType.HAPPY: (0.8, 0.12),
            EmotionType.SAD: (0.75, 0.18),
            EmotionType.ANGRY: (0.85, 0.1),
            EmotionType.FEAR: (0.72, 0.2),
            EmotionType.SURPRISE: (0.68, 0.22),
            EmotionType.DISGUST: (0.78, 0.15)
        }
        
        # Voice-truth dissonance patterns
        self.dissonance_patterns = {
            "suppressed_anger": {
                "text_emotions": [EmotionType.NEUTRAL, EmotionType.SAD],
                "voice_emotions": [EmotionType.ANGRY],
                "dissonance_range": (0.6, 0.9)
            },
            "hidden_sadness": {
                "text_emotions": [EmotionType.NEUTRAL, EmotionType.HAPPY],
                "voice_emotions": [EmotionType.SAD],
                "dissonance_range": (0.5, 0.8)
            },
            "masked_fear": {
                "text_emotions": [EmotionType.NEUTRAL, EmotionType.ANGRY],
                "voice_emotions": [EmotionType.FEAR],
                "dissonance_range": (0.4, 0.7)
            },
            "forced_happiness": {
                "text_emotions": [EmotionType.HAPPY],
                "voice_emotions": [EmotionType.SAD, EmotionType.NEUTRAL],
                "dissonance_range": (0.3, 0.6)
            }
        }
    
    def generate_emotion_analysis(self, text: str, context: Optional[Dict] = None) -> EmotionResult:
        """Generate emotion analysis for given text with realistic confidence scores"""
        context = context or {}
        
        # Determine base emotion from text content and context
        base_emotion = self._analyze_text_emotion(text, context)
        
        # Generate confidence score with realistic distribution
        confidence = self._generate_confidence_score(base_emotion)
        
        # Determine if voice-truth dissonance should be present
        voice_truth_gap = None
        if self.random.random() < 0.15:  # 15% chance of dissonance
            voice_truth_gap = self._generate_voice_truth_gap(base_emotion)
        
        # Generate emotion feature vector
        features = self._generate_emotion_features(base_emotion, confidence)
        
        return EmotionResult(
            detected=base_emotion,
            confidence=confidence,
            voice_truth_gap=voice_truth_gap,
            features=features
        )
    
    def create_dissonance_pattern(self, text_emotion: str, voice_emotion: str) -> DissonanceResult:
        """Create voice-truth dissonance pattern between text and voice emotions"""
        text_emotion_enum = EmotionType(text_emotion)
        voice_emotion_enum = EmotionType(voice_emotion)
        
        # Calculate dissonance score based on emotional distance
        dissonance_score = self._calculate_emotional_distance(text_emotion_enum, voice_emotion_enum)
        
        # Generate confidence based on how clear the dissonance is
        confidence = min(0.95, 0.5 + (dissonance_score * 0.5))
        
        # Create voice-truth gap analysis
        voice_truth_gap = VoiceTruthGap(
            text_emotion=text_emotion_enum,
            voice_emotion=voice_emotion_enum,
            dissonance_score=dissonance_score,
            confidence=confidence,
            indicators=self._generate_dissonance_indicators(text_emotion_enum, voice_emotion_enum)
        )
        
        # Generate explanation
        explanation = self._generate_dissonance_explanation(text_emotion_enum, voice_emotion_enum, dissonance_score)
        
        return DissonanceResult(
            detected=dissonance_score > 0.3,
            confidence=confidence,
            voice_truth_gap=voice_truth_gap,
            explanation=explanation
        )
    
    def generate_baseline_data(self, user_id: str, sessions: int) -> BaselineData:
        """Generate baseline emotional and voice patterns for a user over multiple sessions"""
        # Generate consistent patterns for the same user
        user_seed = hash(user_id) % 1000000
        user_random = random.Random(user_seed)
        
        # Generate voice patterns
        voice_patterns = self._generate_voice_patterns(user_random)
        
        # Generate emotional patterns
        emotional_patterns = self._generate_emotional_patterns(user_random, sessions)
        
        return BaselineData(
            voice_patterns=voice_patterns,
            emotional_patterns=emotional_patterns
        )
    
    def generate(self, config: DemoConfig) -> GenerationResult:
        """Generate emotion data according to configuration"""
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
        """Validate generated emotion data meets quality standards"""
        if isinstance(data, EmotionResult):
            return (
                0.0 <= data.confidence <= 1.0 and
                (data.voice_truth_gap is None or 0.0 <= data.voice_truth_gap <= 1.0) and
                data.detected in EmotionType
            )
        elif isinstance(data, DissonanceResult):
            return (
                0.0 <= data.confidence <= 1.0 and
                0.0 <= data.voice_truth_gap.dissonance_score <= 1.0
            )
        elif isinstance(data, BaselineData):
            return (
                data.voice_patterns.average_pitch > 0 and
                data.voice_patterns.speech_rate > 0 and
                len(data.emotional_patterns.dominant_emotions) > 0
            )
        return False
    
    # Private helper methods
    
    def _analyze_text_emotion(self, text: str, context: Dict) -> EmotionType:
        """Analyze text content to determine base emotion"""
        text_lower = text.lower()
        
        # Crisis/high-stress indicators
        crisis_keywords = ["suicide", "kill myself", "end it all", "can't go on", "hopeless"]
        if any(keyword in text_lower for keyword in crisis_keywords):
            return EmotionType.SAD if self.random.random() < 0.7 else EmotionType.FEAR
        
        # Anger indicators
        anger_keywords = ["angry", "furious", "hate", "stupid", "idiot", "damn"]
        if any(keyword in text_lower for keyword in anger_keywords):
            return EmotionType.ANGRY
        
        # Sadness indicators
        sad_keywords = ["sad", "depressed", "cry", "tears", "lonely", "empty", "nimechoka"]
        if any(keyword in text_lower for keyword in sad_keywords):
            return EmotionType.SAD
        
        # Fear indicators
        fear_keywords = ["scared", "afraid", "terrified", "panic", "anxiety", "worried"]
        if any(keyword in text_lower for keyword in fear_keywords):
            return EmotionType.FEAR
        
        # Happy indicators
        happy_keywords = ["happy", "joy", "excited", "great", "wonderful", "amazing"]
        if any(keyword in text_lower for keyword in happy_keywords):
            return EmotionType.HAPPY
        
        # Surprise indicators
        surprise_keywords = ["wow", "amazing", "unexpected", "sudden", "shocked"]
        if any(keyword in text_lower for keyword in surprise_keywords):
            return EmotionType.SURPRISE
        
        # Disgust indicators
        disgust_keywords = ["disgusting", "gross", "sick", "revolting", "awful"]
        if any(keyword in text_lower for keyword in disgust_keywords):
            return EmotionType.DISGUST
        
        # Default to neutral with some randomness
        if self.random.random() < 0.7:
            return EmotionType.NEUTRAL
        else:
            return self.random.choice(list(EmotionType))
    
    def _generate_confidence_score(self, emotion: EmotionType) -> float:
        """Generate realistic confidence score for emotion"""
        mean, std = self.confidence_distributions[emotion]
        confidence = self.random.gauss(mean, std)
        return max(0.1, min(0.99, confidence))  # Clamp to reasonable range
    
    def _generate_voice_truth_gap(self, text_emotion: EmotionType) -> float:
        """Generate voice-truth gap score"""
        # Higher gap for emotions that are commonly suppressed
        suppression_likelihood = {
            EmotionType.ANGRY: 0.7,
            EmotionType.SAD: 0.6,
            EmotionType.FEAR: 0.5,
            EmotionType.DISGUST: 0.4,
            EmotionType.NEUTRAL: 0.2,
            EmotionType.HAPPY: 0.3,
            EmotionType.SURPRISE: 0.1
        }
        
        base_gap = suppression_likelihood.get(text_emotion, 0.3)
        variation = self.random.gauss(0, 0.15)
        gap = base_gap + variation
        
        return max(0.0, min(1.0, gap))
    
    def _generate_emotion_features(self, emotion: EmotionType, confidence: float) -> Dict[str, float]:
        """Generate emotion feature vector"""
        # Base feature values for each emotion
        base_features = {
            EmotionType.NEUTRAL: {"valence": 0.5, "arousal": 0.3, "dominance": 0.5},
            EmotionType.HAPPY: {"valence": 0.8, "arousal": 0.7, "dominance": 0.7},
            EmotionType.SAD: {"valence": 0.2, "arousal": 0.3, "dominance": 0.3},
            EmotionType.ANGRY: {"valence": 0.2, "arousal": 0.8, "dominance": 0.8},
            EmotionType.FEAR: {"valence": 0.1, "arousal": 0.8, "dominance": 0.2},
            EmotionType.SURPRISE: {"valence": 0.6, "arousal": 0.8, "dominance": 0.4},
            EmotionType.DISGUST: {"valence": 0.1, "arousal": 0.5, "dominance": 0.6}
        }
        
        features = base_features[emotion].copy()
        
        # Add noise based on confidence (lower confidence = more noise)
        noise_factor = (1.0 - confidence) * 0.2
        for key in features:
            noise = self.random.gauss(0, noise_factor)
            features[key] = max(0.0, min(1.0, features[key] + noise))
        
        # Add additional features
        features.update({
            "intensity": confidence * self.random.uniform(0.8, 1.2),
            "clarity": confidence,
            "stability": self.random.uniform(0.6, 0.9)
        })
        
        return features
    
    def _calculate_emotional_distance(self, emotion1: EmotionType, emotion2: EmotionType) -> float:
        """Calculate emotional distance between two emotions"""
        if emotion1 == emotion2:
            return 0.0
        
        # Emotional distance matrix (simplified)
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
    
    def _generate_dissonance_indicators(self, text_emotion: EmotionType, voice_emotion: EmotionType) -> List[str]:
        """Generate indicators that suggest voice-truth dissonance"""
        indicators = []
        
        if text_emotion == EmotionType.NEUTRAL and voice_emotion in [EmotionType.SAD, EmotionType.ANGRY]:
            indicators.extend(["vocal_tension", "pitch_variation", "speech_hesitation"])
        
        if text_emotion == EmotionType.HAPPY and voice_emotion == EmotionType.SAD:
            indicators.extend(["forced_intonation", "micro_expressions", "vocal_strain"])
        
        if voice_emotion == EmotionType.ANGRY and text_emotion != EmotionType.ANGRY:
            indicators.extend(["suppressed_intensity", "vocal_tremor", "rapid_speech"])
        
        if voice_emotion == EmotionType.FEAR and text_emotion not in [EmotionType.FEAR, EmotionType.SURPRISE]:
            indicators.extend(["voice_shakiness", "pitch_elevation", "breathing_changes"])
        
        # Add some general indicators
        general_indicators = ["prosodic_mismatch", "emotional_leakage", "vocal_masking"]
        indicators.extend(self.random.sample(general_indicators, min(2, len(general_indicators))))
        
        return list(set(indicators))  # Remove duplicates
    
    def _generate_dissonance_explanation(self, text_emotion: EmotionType, voice_emotion: EmotionType, score: float) -> str:
        """Generate human-readable explanation for dissonance"""
        if score < 0.3:
            return f"Minimal dissonance detected between text ({text_emotion.value}) and voice ({voice_emotion.value}) emotions."
        elif score < 0.6:
            return f"Moderate dissonance: text suggests {text_emotion.value} while voice indicates {voice_emotion.value}. This may indicate emotional suppression or mixed feelings."
        else:
            return f"Significant dissonance detected: strong mismatch between text ({text_emotion.value}) and voice ({voice_emotion.value}) emotions. This suggests the person may be hiding their true emotional state."
    
    def _generate_voice_patterns(self, user_random: random.Random) -> VoicePatterns:
        """Generate baseline voice patterns for a user"""
        # Generate realistic voice characteristics
        gender_factor = user_random.choice([0.8, 1.2])  # Rough gender influence on pitch
        age_factor = user_random.uniform(0.9, 1.1)  # Age influence
        
        average_pitch = user_random.uniform(120, 250) * gender_factor * age_factor
        speech_rate = user_random.uniform(120, 180)  # words per minute
        
        emotional_baseline = user_random.choice([
            EmotionType.NEUTRAL, EmotionType.NEUTRAL, EmotionType.NEUTRAL,  # Most common
            EmotionType.HAPPY, EmotionType.SAD
        ])
        
        stress_indicators = user_random.sample([
            "pitch_elevation", "speech_acceleration", "vocal_tension",
            "breathing_changes", "voice_tremor", "articulation_changes"
        ], k=user_random.randint(2, 4))
        
        return VoicePatterns(
            average_pitch=average_pitch,
            speech_rate=speech_rate,
            emotional_baseline=emotional_baseline,
            stress_indicators=stress_indicators
        )
    
    def _generate_emotional_patterns(self, user_random: random.Random, sessions: int) -> EmotionalPatterns:
        """Generate baseline emotional patterns for a user"""
        # Generate dominant emotions (most common for this user)
        all_emotions = list(EmotionType)
        dominant_emotions = user_random.sample(all_emotions, k=user_random.randint(2, 4))
        
        # Generate crisis triggers
        possible_triggers = [
            "academic_failure", "family_pressure", "relationship_issues",
            "financial_stress", "health_concerns", "social_isolation",
            "work_pressure", "cultural_conflict", "identity_crisis"
        ]
        crisis_triggers = user_random.sample(possible_triggers, k=user_random.randint(1, 3))
        
        # Generate coping mechanisms
        possible_coping = [
            "social_support", "prayer", "exercise", "music",
            "journaling", "meditation", "family_time", "nature",
            "creative_expression", "professional_help"
        ]
        coping_mechanisms = user_random.sample(possible_coping, k=user_random.randint(2, 5))
        
        return EmotionalPatterns(
            dominant_emotions=dominant_emotions,
            crisis_triggers=crisis_triggers,
            coping_mechanisms=coping_mechanisms
        )