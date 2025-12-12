"""
Deviation Detector Service
Detects deviations from personal baseline
"""

import logging
from typing import Dict, Optional
import math

logger = logging.getLogger(__name__)


class DeviationDetector:
    """Detect deviations from baseline"""
    
    def __init__(self, threshold: float = 0.3):
        self.threshold = threshold
    
    def detect_voice_deviation(
        self,
        current_features: Dict,
        baseline_features: Dict
    ) -> Optional[Dict]:
        """
        Detect deviation in voice features
        
        Returns:
            {
                "deviation_score": 0.45,
                "deviation_detected": True,
                "deviations": {
                    "pitch_mean": 0.35,
                    "energy_mean": 0.52
                }
            }
        """
        if not baseline_features:
            return None
        
        deviations = {}
        total_deviation = 0.0
        feature_count = 0
        
        for feature in ["pitch_mean", "pitch_std", "energy_mean", "energy_std", "speech_rate", "pause_frequency"]:
            if feature in current_features and feature in baseline_features:
                baseline_value = baseline_features[feature]
                current_value = current_features[feature]
                
                if baseline_value != 0:
                    # Calculate relative deviation
                    deviation = abs(current_value - baseline_value) / abs(baseline_value)
                    deviations[feature] = deviation
                    total_deviation += deviation
                    feature_count += 1
        
        if feature_count == 0:
            return None
        
        average_deviation = total_deviation / feature_count
        
        return {
            "deviation_score": average_deviation,
            "deviation_detected": average_deviation > self.threshold,
            "deviations": deviations
        }
    
    def detect_emotion_deviation(
        self,
        current_emotion: Dict,
        baseline: Dict
    ) -> Optional[Dict]:
        """
        Detect deviation in emotion
        
        Returns:
            {
                "deviation_score": 0.55,
                "deviation_detected": True,
                "current_emotion": "sad",
                "baseline_dominant": "happy",
                "emotion_shift": True
            }
        """
        if not baseline:
            return None
        
        current_emotion_name = current_emotion.get('emotion', 'neutral')
        baseline_dominant = baseline.get('dominant_emotion', 'neutral')
        
        # Check if emotion changed significantly
        emotion_shift = current_emotion_name != baseline_dominant
        
        # Calculate deviation based on distribution
        emotion_distribution = baseline.get('emotion_distribution', {})
        baseline_frequency = emotion_distribution.get(current_emotion_name, 0.0)
        
        # If current emotion is rare in baseline, that's a deviation
        deviation_score = 1.0 - baseline_frequency
        
        return {
            "deviation_score": deviation_score,
            "deviation_detected": deviation_score > self.threshold or emotion_shift,
            "current_emotion": current_emotion_name,
            "baseline_dominant": baseline_dominant,
            "emotion_shift": emotion_shift
        }
    
    def calculate_severity(self, deviation_score: float) -> str:
        """Calculate severity of deviation"""
        if deviation_score >= 0.7:
            return "high"
        elif deviation_score >= 0.4:
            return "medium"
        else:
            return "low"

