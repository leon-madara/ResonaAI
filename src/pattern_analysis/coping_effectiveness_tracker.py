"""
Coping Effectiveness Tracker

Identifies which coping strategies actually work for each individual user
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import numpy as np
from datetime import datetime, timedelta

@dataclass
class CopingStrategy:
    """A coping strategy and its effectiveness"""
    name: str  # e.g., "breathing exercises", "nature walks"
    category: str  # 'activity', 'social', 'relaxation', 'expression'
    effectiveness_score: float  # 0-1, how much it helps
    evidence: str  # Why we think it works
    mention_count: int  # How many times mentioned
    improvement_rate: float  # % of times voice improved after
    sample_mention: str  # Example of when they mentioned it

@dataclass
class CopingProfile:
    """User's coping strategy profile"""
    effective_strategies: List[CopingStrategy]  # What works (>0.6)
    ineffective_strategies: List[CopingStrategy]  # What doesn't (<0.4)
    untried_suggestions: List[str]  # Strategies they haven't tried
    coping_consistency: float  # Do they regularly use coping?
    primary_coping_style: str  # 'active', 'social', 'avoidant', 'mixed'

class CopingEffectivenessTracker:
    """
    Tracks what coping strategies actually help each user
    """

    def __init__(self):
        # Coping strategy keywords
        self.coping_keywords = {
            # Physical/Activity
            'exercise': {
                'keywords': ['exercise', 'gym', 'workout', 'run', 'walk', 'yoga'],
                'category': 'activity'
            },
            'nature': {
                'keywords': ['nature', 'outside', 'walk', 'park', 'outdoors', 'fresh air'],
                'category': 'activity'
            },

            # Relaxation
            'breathing': {
                'keywords': ['breathing', 'breathe', 'breath work', 'deep breaths'],
                'category': 'relaxation'
            },
            'meditation': {
                'keywords': ['meditate', 'meditation', 'mindfulness', 'calm app'],
                'category': 'relaxation'
            },
            'sleep': {
                'keywords': ['sleep', 'rest', 'nap', 'lie down'],
                'category': 'relaxation'
            },

            # Social
            'talking_to_someone': {
                'keywords': ['talked to', 'called', 'text', 'reached out', 'friend'],
                'category': 'social'
            },
            'therapy': {
                'keywords': ['therapy', 'therapist', 'counselor', 'counseling'],
                'category': 'social'
            },

            # Expression
            'journaling': {
                'keywords': ['journal', 'write', 'writing', 'diary'],
                'category': 'expression'
            },
            'music': {
                'keywords': ['music', 'song', 'listen', 'playlist'],
                'category': 'expression'
            },
            'prayer': {
                'keywords': ['pray', 'prayer', 'church', 'faith', 'god', 'maombi'],
                'category': 'expression'
            },

            # Distraction
            'work_distraction': {
                'keywords': ['threw myself into work', 'stayed busy', 'distracted', 'kept busy'],
                'category': 'distraction'
            },
            'entertainment': {
                'keywords': ['movie', 'tv', 'show', 'watch', 'netflix'],
                'category': 'distraction'
            }
        }

    async def track(
        self,
        sessions: List[Dict],
        user_id: str
    ) -> CopingProfile:
        """
        Analyze which coping strategies are effective

        Args:
            sessions: List of session data (sorted by timestamp)
            user_id: User identifier

        Returns:
            CopingProfile with effective/ineffective strategies
        """
        if len(sessions) < 3:
            return self._default_profile()

        # Sort sessions by timestamp
        sessions = sorted(sessions, key=lambda s: s.get('timestamp', ''))

        # 1. Find coping strategy mentions
        coping_mentions = self._extract_coping_mentions(sessions)

        # 2. Analyze effectiveness of each strategy
        strategies = []
        for strategy_name, mentions in coping_mentions.items():
            if not mentions:
                continue

            effectiveness = self._calculate_effectiveness(
                strategy_name,
                mentions,
                sessions
            )

            if effectiveness:
                strategies.append(effectiveness)

        # 3. Separate effective vs ineffective
        effective = [s for s in strategies if s.effectiveness_score >= 0.6]
        ineffective = [s for s in strategies if s.effectiveness_score < 0.4]

        # Sort by effectiveness
        effective.sort(key=lambda s: s.effectiveness_score, reverse=True)
        ineffective.sort(key=lambda s: s.effectiveness_score)

        # 4. Suggest untried strategies
        tried_strategies = set(coping_mentions.keys())
        all_strategies = set(self.coping_keywords.keys())
        untried = list(all_strategies - tried_strategies)

        # 5. Assess coping consistency
        consistency = self._assess_coping_consistency(coping_mentions, sessions)

        # 6. Identify primary coping style
        primary_style = self._identify_coping_style(strategies)

        return CopingProfile(
            effective_strategies=effective,
            ineffective_strategies=ineffective,
            untried_suggestions=untried[:5],  # Top 5 suggestions
            coping_consistency=consistency,
            primary_coping_style=primary_style
        )

    def _extract_coping_mentions(
        self,
        sessions: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """
        Extract coping strategy mentions from sessions

        Returns: {strategy_name: [list of mentions]}
        """
        mentions = {strategy: [] for strategy in self.coping_keywords.keys()}

        for i, session in enumerate(sessions):
            transcript = session.get('transcript', '').lower()

            # Check each strategy
            for strategy_name, strategy_info in self.coping_keywords.items():
                keywords = strategy_info['keywords']

                # Check if any keyword present
                for keyword in keywords:
                    if keyword in transcript:
                        # Extract phrase
                        phrase = self._extract_phrase(transcript, keyword)

                        mention = {
                            'session_index': i,
                            'session_id': session.get('session_id'),
                            'timestamp': session.get('timestamp'),
                            'phrase': phrase,
                            'voice_emotion': session.get('voice_emotion'),
                            'voice_features': session.get('voice_features'),
                            'category': strategy_info['category']
                        }
                        mentions[strategy_name].append(mention)
                        break  # Only count once per session

        return mentions

    def _extract_phrase(
        self,
        text: str,
        keyword: str,
        context_words: int = 8
    ) -> str:
        """Extract phrase around keyword"""
        words = text.split()
        try:
            index = next(i for i, word in enumerate(words) if keyword in word)
            start = max(0, index - context_words)
            end = min(len(words), index + context_words + 1)
            return ' '.join(words[start:end])
        except StopIteration:
            return text[:80]

    def _calculate_effectiveness(
        self,
        strategy_name: str,
        mentions: List[Dict],
        all_sessions: List[Dict]
    ) -> Optional[CopingStrategy]:
        """
        Calculate how effective this strategy is

        Method: Check if voice improved in next session after mentioning strategy
        """
        if len(mentions) < 2:
            return None  # Need multiple mentions to assess

        improvements = []
        category = mentions[0]['category']

        emotion_valence = {
            'happy': 1.0,
            'neutral': 0.0,
            'sad': -0.7,
            'angry': -0.6,
            'fear': -0.8,
            'disgust': -0.5,
            'hopeless': -1.0,
            'resigned': -0.9
        }

        for mention in mentions:
            current_index = mention['session_index']

            # Need a next session to compare
            if current_index + 1 >= len(all_sessions):
                continue

            current_session = all_sessions[current_index]
            next_session = all_sessions[current_index + 1]

            # Get emotional valence
            current_emotion = current_session.get('voice_emotion', 'neutral')
            next_emotion = next_session.get('voice_emotion', 'neutral')

            current_valence = emotion_valence.get(current_emotion, 0.0)
            next_valence = emotion_valence.get(next_emotion, 0.0)

            # Calculate improvement
            improvement = next_valence - current_valence

            improvements.append(improvement)

        if not improvements:
            return None

        # Calculate effectiveness score
        avg_improvement = np.mean(improvements)
        improvement_rate = sum(1 for i in improvements if i > 0) / len(improvements)

        # Normalize to 0-1 scale
        # Improvement range is typically -2 to 2
        effectiveness_score = (avg_improvement + 1.0) / 2.0
        effectiveness_score = np.clip(effectiveness_score, 0.0, 1.0)

        # Boost if consistent improvement
        if improvement_rate > 0.7:
            effectiveness_score = min(effectiveness_score + 0.1, 1.0)

        # Generate evidence
        if avg_improvement > 0.2:
            evidence = f"Your voice improves {improvement_rate:.0%} of the time after {strategy_name}"
        elif avg_improvement > 0:
            evidence = f"Shows small positive effect on your mood"
        else:
            evidence = f"Doesn't seem to improve your voice/mood"

        return CopingStrategy(
            name=strategy_name.replace('_', ' ').title(),
            category=category,
            effectiveness_score=effectiveness_score,
            evidence=evidence,
            mention_count=len(mentions),
            improvement_rate=improvement_rate,
            sample_mention=mentions[0]['phrase']
        )

    def _assess_coping_consistency(
        self,
        coping_mentions: Dict[str, List[Dict]],
        sessions: List[Dict]
    ) -> float:
        """
        How consistently does user employ coping strategies?

        Returns: 0 (never) to 1 (regularly)
        """
        # Count sessions where at least one coping strategy mentioned
        sessions_with_coping = set()

        for mentions in coping_mentions.values():
            for mention in mentions:
                sessions_with_coping.add(mention['session_id'])

        if not sessions:
            return 0.0

        consistency = len(sessions_with_coping) / len(sessions)
        return consistency

    def _identify_coping_style(
        self,
        strategies: List[CopingStrategy]
    ) -> str:
        """
        Identify primary coping style from used strategies

        Returns: 'active', 'social', 'avoidant', 'mixed'
        """
        if not strategies:
            return 'undefined'

        # Count strategies by category
        category_counts = {}
        for strategy in strategies:
            cat = strategy.category
            category_counts[cat] = category_counts.get(cat, 0) + 1

        if not category_counts:
            return 'undefined'

        # Find dominant category
        dominant = max(category_counts, key=category_counts.get)

        # Map to coping style
        style_map = {
            'activity': 'active',
            'relaxation': 'calming',
            'social': 'social',
            'expression': 'expressive',
            'distraction': 'avoidant'
        }

        # Check if mixed (multiple categories with similar counts)
        max_count = max(category_counts.values())
        high_categories = [
            cat for cat, count in category_counts.items()
            if count >= max_count * 0.7
        ]

        if len(high_categories) > 2:
            return 'mixed'

        return style_map.get(dominant, 'mixed')

    def _default_profile(self) -> CopingProfile:
        """Default profile for new users"""
        return CopingProfile(
            effective_strategies=[],
            ineffective_strategies=[],
            untried_suggestions=list(self.coping_keywords.keys())[:5],
            coping_consistency=0.0,
            primary_coping_style='undefined'
        )
