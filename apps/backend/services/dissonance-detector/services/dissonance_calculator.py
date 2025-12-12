"""
Dissonance Calculator Service
Calculates dissonance between stated and actual emotion
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class DissonanceCalculator:
    """Calculate dissonance between stated and actual emotion"""
    
    def __init__(self, emotion_valence_map: Dict[str, float], thresholds: Dict[str, float]):
        self.emotion_valence_map = emotion_valence_map
        self.thresholds = thresholds
    
    def calculate(
        self,
        sentiment_result: Dict,
        voice_emotion: Dict[str, Any]
    ) -> Dict:
        """
        Calculate dissonance between sentiment and voice emotion
        
        Returns:
        {
            "dissonance_level": "high",
            "dissonance_score": 0.82,
            "stated_emotion": "positive",
            "actual_emotion": "negative",
            "interpretation": "defensive_concealment",
            "risk_level": "medium-high",
            "confidence": 0.82,
            "details": {
                "sentiment_score": 0.75,
                "emotion_score": -0.65,
                "gap": 1.40,
                "normalized_gap": 0.70
            }
        }
        """
        try:
            # Extract sentiment valence
            sentiment_valence = sentiment_result.get('valence', 0.0)
            
            # Extract emotion valence
            emotion_name = voice_emotion.get('emotion', 'neutral').lower()
            emotion_confidence = voice_emotion.get('confidence', 0.5)
            emotion_valence = self.emotion_valence_map.get(emotion_name, 0.0)
            
            # Weight emotion by confidence
            weighted_emotion_valence = emotion_valence * emotion_confidence
            
            # Calculate gap
            gap = abs(sentiment_valence - weighted_emotion_valence)
            
            # Normalize gap (0 to 1 scale)
            # Max gap is 2.0 (sentiment +1, emotion -1)
            normalized_gap = gap / 2.0
            
            # Determine dissonance level
            dissonance_level = self._get_dissonance_level(normalized_gap)
            
            # Determine interpretation
            interpretation = self._get_interpretation(
                sentiment_valence,
                weighted_emotion_valence,
                dissonance_level
            )
            
            # Map to risk level
            risk_level = self._map_to_risk(dissonance_level, interpretation)
            
            # Calculate overall confidence
            sentiment_score = sentiment_result.get('score', 0.5)
            confidence = min(sentiment_score, emotion_confidence)
            
            return {
                "dissonance_level": dissonance_level,
                "dissonance_score": normalized_gap,
                "stated_emotion": self._get_emotion_label(sentiment_valence),
                "actual_emotion": self._get_emotion_label(weighted_emotion_valence),
                "interpretation": interpretation,
                "risk_level": risk_level,
                "confidence": confidence,
                "details": {
                    "sentiment_score": sentiment_valence,
                    "emotion_score": weighted_emotion_valence,
                    "gap": gap,
                    "normalized_gap": normalized_gap
                }
            }
        except Exception as e:
            logger.error(f"Error calculating dissonance: {e}")
            # Return low dissonance as fallback
            return {
                "dissonance_level": "low",
                "dissonance_score": 0.0,
                "stated_emotion": "neutral",
                "actual_emotion": "neutral",
                "interpretation": "unclear",
                "risk_level": "low",
                "confidence": 0.0,
                "details": {
                    "sentiment_score": 0.0,
                    "emotion_score": 0.0,
                    "gap": 0.0,
                    "normalized_gap": 0.0
                }
            }
    
    def _get_dissonance_level(self, normalized_gap: float) -> str:
        """Get dissonance level from normalized gap"""
        if normalized_gap >= self.thresholds['high']:
            return "high"
        elif normalized_gap >= self.thresholds['medium']:
            return "medium"
        else:
            return "low"
    
    def _get_interpretation(
        self,
        sentiment_valence: float,
        emotion_valence: float,
        dissonance_level: str
    ) -> str:
        """Interpret the dissonance pattern"""
        if dissonance_level == "low":
            return "authentic"
        
        # Positive sentiment, negative emotion = defensive concealment
        if sentiment_valence > 0.3 and emotion_valence < -0.3:
            return "defensive_concealment"
        
        # Negative sentiment, positive emotion = recovery/improvement
        if sentiment_valence < -0.3 and emotion_valence > 0.3:
            return "recovery_indicator"
        
        # Both negative but different intensities
        if sentiment_valence < 0 and emotion_valence < 0:
            return "intensity_mismatch"
        
        return "unclear"
    
    def _get_emotion_label(self, valence: float) -> str:
        """Get emotion label from valence"""
        if valence > 0.3:
            return "positive"
        elif valence < -0.3:
            return "negative"
        else:
            return "neutral"
    
    def _map_to_risk(self, dissonance_level: str, interpretation: str) -> str:
        """Map dissonance to risk level"""
        if dissonance_level == "high" and interpretation == "defensive_concealment":
            return "medium-high"
        elif dissonance_level == "high":
            return "medium"
        elif dissonance_level == "medium":
            return "low"
        else:
            return "low"

