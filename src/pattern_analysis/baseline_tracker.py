"""
Baseline Tracker

Learns each user's "normal" voice to detect when they're different from usual
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import numpy as np

@dataclass
class VoiceBaseline:
    """User's voice baseline (their "normal")"""
    user_id: str
    sessions_analyzed: int
    baseline_established: bool  # True after 3+ sessions

    # Prosodic baseline
    typical_pitch_mean: float
    typical_pitch_std: float
    typical_pitch_range: float

    # Energy baseline
    typical_energy_mean: float
    typical_energy_std: float

    # Temporal baseline
    typical_speech_rate: float
    typical_pause_ratio: float

    # Emotional baseline
    typical_prosody_variance: float  # How expressive they typically are
    typical_emotion_distribution: Dict[str, float]

    # Personal markers
    stress_markers: Dict[str, any]  # Individual stress patterns
    # e.g., {"faster_when_anxious": True, "quieter_when_sad": True}

class BaselineTracker:
    """
    Tracks user's voice baseline over time
    """

    def __init__(self):
        self.min_sessions_for_baseline = 3

    async def update_baseline(
        self,
        user_id: str,
        sessions: List[Dict]
    ) -> VoiceBaseline:
        """
        Calculate or update user's voice baseline

        Args:
            user_id: User identifier
            sessions: All user sessions (for baseline calculation)

        Returns:
            VoiceBaseline with typical voice characteristics
        """
        if len(sessions) < self.min_sessions_for_baseline:
            return self._insufficient_data_baseline(user_id, len(sessions))

        # Extract features from all sessions
        pitch_means = []
        pitch_stds = []
        pitch_ranges = []
        energy_means = []
        energy_stds = []
        speech_rates = []
        pause_ratios = []
        prosody_variances = []
        emotions = []

        for session in sessions:
            features = session.get('voice_features', {})
            prosodic = features.get('prosodic', {})
            temporal = features.get('temporal', {})

            # Prosodic
            pitch_means.append(prosodic.get('pitch_mean', 0))
            pitch_stds.append(prosodic.get('pitch_std', 0))
            pitch_ranges.append(prosodic.get('pitch_range', 0))

            # Energy
            energy_means.append(prosodic.get('energy_mean', 0))
            energy_stds.append(prosodic.get('energy_std', 0))

            # Temporal
            speech_rates.append(temporal.get('speech_rate', 0))
            pause_ratios.append(temporal.get('pause_ratio', 0))

            # Prosody variance (expressiveness)
            prosody_variances.append(pitch_stds[-1] if pitch_stds else 0)

            # Emotions
            emotion = session.get('voice_emotion', 'neutral')
            emotions.append(emotion)

        # Calculate typical values
        typical_pitch_mean = np.mean(pitch_means)
        typical_pitch_std = np.mean(pitch_stds)
        typical_pitch_range = np.mean(pitch_ranges)
        typical_energy_mean = np.mean(energy_means)
        typical_energy_std = np.mean(energy_stds)
        typical_speech_rate = np.mean(speech_rates)
        typical_pause_ratio = np.mean(pause_ratios)
        typical_prosody_variance = np.mean(prosody_variances)

        # Calculate emotion distribution
        emotion_dist = {}
        for emotion in set(emotions):
            emotion_dist[emotion] = emotions.count(emotion) / len(emotions)

        # Detect personal stress markers
        stress_markers = self._detect_stress_markers(sessions)

        return VoiceBaseline(
            user_id=user_id,
            sessions_analyzed=len(sessions),
            baseline_established=True,
            typical_pitch_mean=typical_pitch_mean,
            typical_pitch_std=typical_pitch_std,
            typical_pitch_range=typical_pitch_range,
            typical_energy_mean=typical_energy_mean,
            typical_energy_std=typical_energy_std,
            typical_speech_rate=typical_speech_rate,
            typical_pause_ratio=typical_pause_ratio,
            typical_prosody_variance=typical_prosody_variance,
            typical_emotion_distribution=emotion_dist,
            stress_markers=stress_markers
        )

    def _detect_stress_markers(
        self,
        sessions: List[Dict]
    ) -> Dict[str, any]:
        """
        Detect individual stress patterns

        e.g., "This person speaks faster when anxious"
        """
        markers = {}

        # Analyze correlation between emotions and voice features
        anxious_sessions = []
        sad_sessions = []
        angry_sessions = []

        for session in sessions:
            emotion = session.get('voice_emotion')
            features = session.get('voice_features', {})

            if emotion == 'fear':
                anxious_sessions.append(features)
            elif emotion == 'sad':
                sad_sessions.append(features)
            elif emotion == 'angry':
                angry_sessions.append(features)

        # Check speech rate patterns
        if anxious_sessions:
            anxious_rates = [
                f.get('temporal', {}).get('speech_rate', 0)
                for f in anxious_sessions
            ]
            avg_anxious_rate = np.mean(anxious_rates)

            # Compare to overall average
            all_rates = [
                s.get('voice_features', {}).get('temporal', {}).get('speech_rate', 0)
                for s in sessions
            ]
            avg_rate = np.mean(all_rates)

            if avg_anxious_rate > avg_rate * 1.2:
                markers['faster_when_anxious'] = True
            elif avg_anxious_rate < avg_rate * 0.8:
                markers['slower_when_anxious'] = True

        # Check pitch patterns for sadness
        if sad_sessions:
            sad_pitches = [
                f.get('prosodic', {}).get('pitch_mean', 0)
                for f in sad_sessions
            ]
            avg_sad_pitch = np.mean(sad_pitches)

            all_pitches = [
                s.get('voice_features', {}).get('prosodic', {}).get('pitch_mean', 0)
                for s in sessions
            ]
            avg_pitch = np.mean(all_pitches)

            if avg_sad_pitch < avg_pitch * 0.9:
                markers['lower_pitch_when_sad'] = True

        # Check energy patterns
        if sad_sessions:
            sad_energies = [
                f.get('prosodic', {}).get('energy_mean', 0)
                for f in sad_sessions
            ]
            avg_sad_energy = np.mean(sad_energies)

            all_energies = [
                s.get('voice_features', {}).get('prosodic', {}).get('energy_mean', 0)
                for s in sessions
            ]
            avg_energy = np.mean(all_energies)

            if avg_sad_energy < avg_energy * 0.7:
                markers['quieter_when_sad'] = True

        return markers

    def _insufficient_data_baseline(
        self,
        user_id: str,
        session_count: int
    ) -> VoiceBaseline:
        """Return baseline indicating insufficient data"""
        return VoiceBaseline(
            user_id=user_id,
            sessions_analyzed=session_count,
            baseline_established=False,
            typical_pitch_mean=0.0,
            typical_pitch_std=0.0,
            typical_pitch_range=0.0,
            typical_energy_mean=0.0,
            typical_energy_std=0.0,
            typical_speech_rate=0.0,
            typical_pause_ratio=0.0,
            typical_prosody_variance=0.0,
            typical_emotion_distribution={},
            stress_markers={}
        )
