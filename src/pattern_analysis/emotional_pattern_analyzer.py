"""
Emotional Pattern Analyzer

Analyzes emotional patterns across voice sessions to detect trends,
trajectories, and temporal patterns.
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass

@dataclass
class EmotionalPattern:
    """Detected emotional patterns"""
    primary_emotions: List[str]  # Most frequent emotions
    emotion_distribution: Dict[str, float]  # % time in each emotion
    temporal_patterns: Dict[str, str]  # time_of_day -> typical_emotion
    trajectory: str  # 'improving', 'declining', 'stable', 'volatile'
    trajectory_confidence: float
    variability_score: float  # 0-1 (low variability = consistent)
    recent_shift: Optional[str]  # Recent change detected?

class EmotionalPatternAnalyzer:
    """
    Analyzes emotional patterns across sessions
    """

    def __init__(self):
        self.window_days = 30  # Analyze last 30 days
        self.recent_window_days = 7  # Recent trend window

    async def analyze(
        self,
        sessions: List[Dict],
        user_id: str
    ) -> EmotionalPattern:
        """
        Analyze emotional patterns from session history

        Args:
            sessions: List of session data with emotions
            user_id: User identifier

        Returns:
            EmotionalPattern with detected patterns
        """
        if not sessions:
            return self._default_pattern()

        # 1. Calculate emotion distribution
        emotion_dist = self._calculate_emotion_distribution(sessions)

        # 2. Identify primary emotions (>20% of time)
        primary = [
            emotion for emotion, pct in emotion_dist.items()
            if pct > 0.20
        ]

        # 3. Detect temporal patterns (time of day)
        temporal = self._detect_temporal_patterns(sessions)

        # 4. Calculate trajectory (improving/declining/stable)
        trajectory, confidence = self._calculate_trajectory(sessions)

        # 5. Calculate emotional variability
        variability = self._calculate_variability(sessions)

        # 6. Detect recent shifts
        recent_shift = self._detect_recent_shift(sessions)

        return EmotionalPattern(
            primary_emotions=primary,
            emotion_distribution=emotion_dist,
            temporal_patterns=temporal,
            trajectory=trajectory,
            trajectory_confidence=confidence,
            variability_score=variability,
            recent_shift=recent_shift
        )

    def _calculate_emotion_distribution(
        self,
        sessions: List[Dict]
    ) -> Dict[str, float]:
        """Calculate % of time in each emotion"""
        emotion_counts = {}
        total = len(sessions)

        for session in sessions:
            emotion = session.get('voice_emotion', 'neutral')
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        # Convert to percentages
        return {
            emotion: count / total
            for emotion, count in emotion_counts.items()
        }

    def _detect_temporal_patterns(
        self,
        sessions: List[Dict]
    ) -> Dict[str, str]:
        """Detect if certain times of day have typical emotions"""
        time_buckets = {
            'morning': [],    # 5am-11am
            'afternoon': [],  # 11am-5pm
            'evening': [],    # 5pm-10pm
            'night': []       # 10pm-5am
        }

        for session in sessions:
            timestamp = session.get('timestamp')
            if not timestamp:
                continue

            # Parse timestamp
            dt = datetime.fromisoformat(timestamp)
            hour = dt.hour

            # Categorize time
            if 5 <= hour < 11:
                bucket = 'morning'
            elif 11 <= hour < 17:
                bucket = 'afternoon'
            elif 17 <= hour < 22:
                bucket = 'evening'
            else:
                bucket = 'night'

            emotion = session.get('voice_emotion', 'neutral')
            time_buckets[bucket].append(emotion)

        # Find most common emotion for each time
        patterns = {}
        for time_period, emotions in time_buckets.items():
            if not emotions:
                continue

            # Most common emotion
            most_common = max(set(emotions), key=emotions.count)
            patterns[time_period] = most_common

        return patterns

    def _calculate_trajectory(
        self,
        sessions: List[Dict]
    ) -> tuple[str, float]:
        """
        Calculate if emotional state is improving, declining, or stable

        Returns: (trajectory, confidence)
        """
        if len(sessions) < 7:
            return 'insufficient_data', 0.0

        # Map emotions to valence scores
        emotion_valence = {
            'happy': 1.0,
            'surprise': 0.5,
            'neutral': 0.0,
            'sad': -0.7,
            'angry': -0.6,
            'fear': -0.8,
            'disgust': -0.5,
            'hopeless': -1.0,
            'resigned': -0.9,
            'numb': -0.8
        }

        # Sort sessions by timestamp
        sorted_sessions = sorted(
            sessions,
            key=lambda s: s.get('timestamp', '')
        )

        # Get valence scores over time
        valences = [
            emotion_valence.get(s.get('voice_emotion', 'neutral'), 0.0)
            for s in sorted_sessions
        ]

        # Split into first half and second half
        mid = len(valences) // 2
        first_half = valences[:mid]
        second_half = valences[mid:]

        # Calculate averages
        avg_first = np.mean(first_half)
        avg_second = np.mean(second_half)

        # Calculate change
        change = avg_second - avg_first

        # Determine trajectory
        if abs(change) < 0.15:
            trajectory = 'stable'
            confidence = 0.8
        elif change > 0.15:
            trajectory = 'improving'
            confidence = min(change / 0.5, 1.0)  # Normalize to 0-1
        else:
            trajectory = 'declining'
            confidence = min(abs(change) / 0.5, 1.0)

        return trajectory, confidence

    def _calculate_variability(
        self,
        sessions: List[Dict]
    ) -> float:
        """
        Calculate emotional variability (consistency)

        Returns: 0 (very consistent) to 1 (highly variable)
        """
        if len(sessions) < 3:
            return 0.5  # Neutral

        emotions = [s.get('voice_emotion', 'neutral') for s in sessions]

        # Calculate entropy (diversity of emotions)
        unique_emotions = set(emotions)
        total = len(emotions)

        entropy = 0.0
        for emotion in unique_emotions:
            count = emotions.count(emotion)
            probability = count / total
            if probability > 0:
                entropy -= probability * np.log2(probability)

        # Normalize entropy to 0-1
        # Max entropy = log2(num_possible_emotions) ≈ 3 for 8 emotions
        max_entropy = np.log2(len(unique_emotions)) if unique_emotions else 1
        variability = min(entropy / max_entropy, 1.0) if max_entropy > 0 else 0.0

        return variability

    def _detect_recent_shift(
        self,
        sessions: List[Dict]
    ) -> Optional[str]:
        """
        Detect if there's been a recent significant shift

        Returns: Description of shift or None
        """
        if len(sessions) < 14:
            return None

        # Sort by timestamp
        sorted_sessions = sorted(
            sessions,
            key=lambda s: s.get('timestamp', '')
        )

        # Last 7 days vs previous 7 days
        recent = sorted_sessions[-7:]
        previous = sorted_sessions[-14:-7]

        # Get dominant emotions
        recent_emotions = [s.get('voice_emotion') for s in recent]
        previous_emotions = [s.get('voice_emotion') for s in previous]

        recent_dominant = max(set(recent_emotions), key=recent_emotions.count)
        previous_dominant = max(set(previous_emotions), key=previous_emotions.count)

        # Detect significant shifts
        if recent_dominant != previous_dominant:
            # Check if it's a meaningful shift
            if recent_dominant in ['sad', 'hopeless', 'resigned', 'numb']:
                if previous_dominant in ['happy', 'neutral']:
                    return f"Recent decline: {previous_dominant} → {recent_dominant}"
            elif recent_dominant in ['happy', 'neutral']:
                if previous_dominant in ['sad', 'hopeless', 'resigned']:
                    return f"Recent improvement: {previous_dominant} → {recent_dominant}"

        return None

    def _default_pattern(self) -> EmotionalPattern:
        """Return default pattern for new users"""
        return EmotionalPattern(
            primary_emotions=[],
            emotion_distribution={},
            temporal_patterns={},
            trajectory='insufficient_data',
            trajectory_confidence=0.0,
            variability_score=0.5,
            recent_shift=None
        )
