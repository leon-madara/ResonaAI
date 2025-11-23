"""
Trigger Detector

Identifies topics, situations, and patterns that cause emotional distress
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import numpy as np
from collections import defaultdict

@dataclass
class Trigger:
    """A detected trigger"""
    topic: str  # e.g., "family", "work", "money"
    frequency: int  # How many times mentioned
    severity: float  # 0-1, how much distress it causes
    voice_markers: List[str]  # Voice changes when topic appears
    sample_phrases: List[str]  # Example phrases that contain trigger

@dataclass
class TriggerPattern:
    """Collection of detected triggers"""
    triggers: List[Trigger]
    trigger_count: int
    most_severe_trigger: Optional[str]
    trigger_combinations: List[tuple]  # Topics that appear together

class TriggerDetector:
    """
    Detects what topics/situations trigger emotional distress
    """

    def __init__(self):
        # Common trigger topics
        self.topic_keywords = {
            'family': [
                'family', 'mother', 'father', 'parents', 'siblings',
                'wife', 'husband', 'children', 'kids', 'familia'
            ],
            'work': [
                'work', 'job', 'boss', 'colleague', 'career',
                'office', 'project', 'deadline', 'kazi'
            ],
            'money': [
                'money', 'financial', 'debt', 'bills', 'rent',
                'afford', 'income', 'salary', 'pesa'
            ],
            'relationships': [
                'relationship', 'partner', 'dating', 'love',
                'breakup', 'alone', 'lonely', 'mahusiano'
            ],
            'health': [
                'health', 'sick', 'illness', 'pain', 'hospital',
                'doctor', 'medication', 'afya'
            ],
            'future': [
                'future', 'tomorrow', 'next', 'plan', 'goal',
                'hope', 'dream', 'kesho'
            ],
            'past': [
                'past', 'before', 'used to', 'remember', 'then',
                'ago', 'zamani'
            ]
        }

    async def detect(
        self,
        sessions: List[Dict],
        user_id: str
    ) -> TriggerPattern:
        """
        Detect triggers from session history

        Args:
            sessions: List of session data with transcripts and voice data
            user_id: User identifier

        Returns:
            TriggerPattern with detected triggers
        """
        if not sessions:
            return self._default_pattern()

        # 1. Extract topics mentioned with voice data
        topic_mentions = self._extract_topic_mentions(sessions)

        # 2. Analyze voice response to each topic
        triggers = []
        for topic, mentions in topic_mentions.items():
            if len(mentions) < 2:
                continue  # Need at least 2 mentions to establish pattern

            # Calculate severity based on voice changes
            severity = self._calculate_trigger_severity(mentions)

            if severity > 0.4:  # Only keep significant triggers
                # Extract voice markers
                voice_markers = self._extract_voice_markers(mentions)

                # Get sample phrases
                sample_phrases = [m['phrase'] for m in mentions[:3]]

                trigger = Trigger(
                    topic=topic,
                    frequency=len(mentions),
                    severity=severity,
                    voice_markers=voice_markers,
                    sample_phrases=sample_phrases
                )
                triggers.append(trigger)

        # 3. Sort by severity
        triggers.sort(key=lambda t: t.severity, reverse=True)

        # 4. Find trigger combinations
        combinations = self._find_trigger_combinations(topic_mentions)

        # 5. Identify most severe
        most_severe = triggers[0].topic if triggers else None

        return TriggerPattern(
            triggers=triggers,
            trigger_count=len(triggers),
            most_severe_trigger=most_severe,
            trigger_combinations=combinations
        )

    def _extract_topic_mentions(
        self,
        sessions: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """
        Extract topic mentions with associated voice data

        Returns: {topic: [list of mentions with voice data]}
        """
        topic_mentions = defaultdict(list)

        for session in sessions:
            transcript = session.get('transcript', '').lower()
            voice_features = session.get('voice_features', {})
            voice_emotion = session.get('voice_emotion', 'neutral')

            # Find which topics are mentioned
            for topic, keywords in self.topic_keywords.items():
                for keyword in keywords:
                    if keyword in transcript:
                        # Extract the phrase around the keyword
                        phrase = self._extract_phrase_around_keyword(
                            transcript,
                            keyword
                        )

                        mention = {
                            'session_id': session.get('session_id'),
                            'phrase': phrase,
                            'voice_emotion': voice_emotion,
                            'voice_features': voice_features,
                            'timestamp': session.get('timestamp')
                        }
                        topic_mentions[topic].append(mention)
                        break  # Only count topic once per session

        return dict(topic_mentions)

    def _extract_phrase_around_keyword(
        self,
        text: str,
        keyword: str,
        context_words: int = 10
    ) -> str:
        """Extract phrase around keyword for context"""
        words = text.split()
        try:
            index = next(i for i, word in enumerate(words) if keyword in word)
            start = max(0, index - context_words)
            end = min(len(words), index + context_words + 1)
            return ' '.join(words[start:end])
        except StopIteration:
            return text[:100]  # First 100 chars if keyword not found

    def _calculate_trigger_severity(
        self,
        mentions: List[Dict]
    ) -> float:
        """
        Calculate how much distress this trigger causes

        Based on:
        - Voice emotion when topic mentioned
        - Voice feature changes (stress markers)
        - Consistency across mentions
        """
        severities = []

        for mention in mentions:
            voice_emotion = mention['voice_emotion']
            voice_features = mention['voice_features']

            # Base severity from emotion
            emotion_severity = {
                'neutral': 0.0,
                'happy': 0.0,
                'sad': 0.7,
                'angry': 0.6,
                'fear': 0.8,
                'disgust': 0.5,
                'hopeless': 0.9,
                'resigned': 0.8
            }
            base_severity = emotion_severity.get(voice_emotion, 0.0)

            # Amplify based on voice features
            prosodic = voice_features.get('prosodic', {})

            # High pitch (stress)
            pitch_mean = prosodic.get('pitch_mean', 0)
            if pitch_mean > 200:
                base_severity += 0.1

            # Tremor (distress)
            pitch_std = prosodic.get('pitch_std', 0)
            if pitch_std > 50:
                base_severity += 0.15

            # Low energy (depression)
            energy_mean = prosodic.get('energy_mean', 0)
            if energy_mean < 0.1:
                base_severity += 0.1

            severities.append(min(base_severity, 1.0))

        # Average severity across mentions
        return np.mean(severities) if severities else 0.0

    def _extract_voice_markers(
        self,
        mentions: List[Dict]
    ) -> List[str]:
        """
        Extract common voice markers when trigger mentioned

        Returns: List of voice changes (e.g., "pitch increases", "energy drops")
        """
        markers = []

        # Analyze prosodic features across mentions
        pitch_means = []
        energy_means = []
        emotions = []

        for mention in mentions:
            prosodic = mention['voice_features'].get('prosodic', {})
            pitch_means.append(prosodic.get('pitch_mean', 0))
            energy_means.append(prosodic.get('energy_mean', 0))
            emotions.append(mention['voice_emotion'])

        # Check for consistent patterns
        avg_pitch = np.mean(pitch_means) if pitch_means else 0
        avg_energy = np.mean(energy_means) if energy_means else 0

        if avg_pitch > 200:
            markers.append("voice_pitch_increases")

        if avg_pitch < 150:
            markers.append("voice_pitch_drops")

        if avg_energy < 0.1:
            markers.append("energy_decreases")

        # Most common emotion
        if emotions:
            most_common_emotion = max(set(emotions), key=emotions.count)
            if most_common_emotion != 'neutral':
                markers.append(f"becomes_{most_common_emotion}")

        return markers

    def _find_trigger_combinations(
        self,
        topic_mentions: Dict[str, List[Dict]]
    ) -> List[tuple]:
        """
        Find topics that are often mentioned together
        (co-occurring triggers)
        """
        combinations = []

        topics = list(topic_mentions.keys())

        for i, topic1 in enumerate(topics):
            for topic2 in topics[i+1:]:
                # Find sessions where both topics mentioned
                sessions1 = set(m['session_id'] for m in topic_mentions[topic1])
                sessions2 = set(m['session_id'] for m in topic_mentions[topic2])

                overlap = sessions1.intersection(sessions2)

                if len(overlap) >= 2:  # Co-occur in at least 2 sessions
                    combinations.append((topic1, topic2, len(overlap)))

        # Sort by frequency
        combinations.sort(key=lambda x: x[2], reverse=True)

        return combinations[:5]  # Top 5 combinations

    def _default_pattern(self) -> TriggerPattern:
        """Default pattern for new users"""
        return TriggerPattern(
            triggers=[],
            trigger_count=0,
            most_severe_trigger=None,
            trigger_combinations=[]
        )
