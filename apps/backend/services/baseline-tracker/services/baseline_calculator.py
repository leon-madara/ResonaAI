"""
Baseline Calculator Service
Calculates emotional and voice baselines for users
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import Counter
import statistics

logger = logging.getLogger(__name__)


class BaselineCalculator:
    """Calculate baselines from historical data"""
    
    def __init__(self, min_samples: int = 10, window_days: int = 30):
        self.min_samples = min_samples
        self.window_days = window_days
    
    def calculate_emotion_baseline(
        self,
        emotion_history: List[Dict]
    ) -> Optional[Dict]:
        """
        Calculate emotional baseline from history
        
        Args:
            emotion_history: List of emotion records with 'emotion' and 'confidence'
        
        Returns:
            {
                "emotion_distribution": {"happy": 0.4, "sad": 0.3, ...},
                "average_confidence": 0.75,
                "dominant_emotion": "happy",
                "sample_count": 50
            }
        """
        if len(emotion_history) < self.min_samples:
            return None
        
        # Count emotions
        emotion_counts = Counter()
        confidences = []
        
        for record in emotion_history:
            emotion = record.get('emotion', 'neutral')
            confidence = record.get('confidence', 0.5)
            emotion_counts[emotion] += 1
            confidences.append(confidence)
        
        # Calculate distribution
        total = sum(emotion_counts.values())
        emotion_distribution = {
            emotion: count / total
            for emotion, count in emotion_counts.items()
        }
        
        # Find dominant emotion
        dominant_emotion = emotion_counts.most_common(1)[0][0] if emotion_counts else "neutral"
        
        # Calculate average confidence
        average_confidence = statistics.mean(confidences) if confidences else 0.5
        
        return {
            "emotion_distribution": emotion_distribution,
            "average_confidence": average_confidence,
            "dominant_emotion": dominant_emotion,
            "sample_count": len(emotion_history)
        }
    
    def calculate_voice_baseline(
        self,
        voice_features_history: List[Dict]
    ) -> Optional[Dict]:
        """
        Calculate voice baseline from history
        
        Args:
            voice_features_history: List of voice feature records
        
        Returns:
            {
                "pitch_mean": 150.0,
                "pitch_std": 20.0,
                "energy_mean": 0.5,
                "energy_std": 0.1,
                "speech_rate": 3.5,
                "pause_frequency": 0.2,
                "sample_count": 50
            }
        """
        if len(voice_features_history) < self.min_samples:
            return None
        
        # Extract features
        features = {
            "pitch_mean": [],
            "pitch_std": [],
            "energy_mean": [],
            "energy_std": [],
            "speech_rate": [],
            "pause_frequency": []
        }
        
        for record in voice_features_history:
            for feature in features.keys():
                if feature in record:
                    features[feature].append(record[feature])
        
        # Calculate averages
        baseline = {}
        for feature, values in features.items():
            if values:
                baseline[feature] = statistics.mean(values)
            else:
                baseline[feature] = 0.0
        
        baseline["sample_count"] = len(voice_features_history)
        
        return baseline
    
    def filter_recent_data(
        self,
        data: List[Dict],
        window_days: int
    ) -> List[Dict]:
        """Filter data to recent window"""
        cutoff_date = datetime.utcnow() - timedelta(days=window_days)
        
        filtered = []
        for record in data:
            record_date = record.get('timestamp') or record.get('created_at')
            if isinstance(record_date, str):
                try:
                    record_date = datetime.fromisoformat(record_date.replace('Z', '+00:00'))
                except:
                    continue
            
            if isinstance(record_date, datetime) and record_date >= cutoff_date:
                filtered.append(record)
        
        return filtered

