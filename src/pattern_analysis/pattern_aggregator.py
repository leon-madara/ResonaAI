"""
Pattern Aggregator

Combines all pattern analyzers into comprehensive user patterns
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from .emotional_pattern_analyzer import EmotionalPatternAnalyzer, EmotionalPattern
from .dissonance_detector import DissonanceDetector, DissonanceResult
from .cultural_context_analyzer import CulturalContextAnalyzer, CulturalContext
from .trigger_detector import TriggerDetector, TriggerPattern
from .coping_effectiveness_tracker import CopingEffectivenessTracker, CopingProfile
from .baseline_tracker import BaselineTracker, VoiceBaseline
from .risk_assessment_engine import RiskAssessmentEngine, RiskAssessment
from .mental_health_profiler import MentalHealthProfiler, MentalHealthProfile

@dataclass
class AggregatedPatterns:
    """
    Complete user patterns from all analyzers
    """
    user_id: str
    generated_at: datetime
    sessions_analyzed: int

    # Core patterns
    emotional_patterns: EmotionalPattern
    cultural_context: CulturalContext
    triggers: TriggerPattern
    coping_profile: CopingProfile
    voice_baseline: VoiceBaseline

    # Current state (from latest session)
    current_dissonance: Optional[DissonanceResult]
    current_risk: RiskAssessment

    # Overall profile
    mental_health_profile: MentalHealthProfile

    # Meta
    data_confidence: float  # 0-1, how confident in patterns

class PatternAggregator:
    """
    Aggregates patterns from all analyzers
    """

    def __init__(self):
        # Initialize all analyzers
        self.emotional_analyzer = EmotionalPatternAnalyzer()
        self.dissonance_detector = DissonanceDetector()
        self.cultural_analyzer = CulturalContextAnalyzer()
        self.trigger_detector = TriggerDetector()
        self.coping_tracker = CopingEffectivenessTracker()
        self.baseline_tracker = BaselineTracker()
        self.risk_assessor = RiskAssessmentEngine()
        self.mh_profiler = MentalHealthProfiler()

    async def aggregate(
        self,
        user_id: str,
        sessions: List[Dict],
        latest_session: Optional[Dict] = None
    ) -> AggregatedPatterns:
        """
        Run all analyzers and aggregate results

        Args:
            user_id: User identifier
            sessions: Historical sessions for pattern detection
            latest_session: Most recent session (optional, for current state)

        Returns:
            AggregatedPatterns with all detected patterns
        """
        # 1. Analyze emotional patterns
        emotional_patterns = await self.emotional_analyzer.analyze(
            sessions,
            user_id
        )

        # 2. Analyze cultural context
        cultural_context = await self.cultural_analyzer.analyze(
            sessions,
            user_id
        )

        # 3. Detect triggers
        triggers = await self.trigger_detector.detect(
            sessions,
            user_id
        )

        # 4. Track coping effectiveness
        coping_profile = await self.coping_tracker.track(
            sessions,
            user_id
        )

        # 5. Update voice baseline
        voice_baseline = await self.baseline_tracker.update_baseline(
            user_id,
            sessions
        )

        # 6. Analyze current dissonance (if latest session available)
        current_dissonance = None
        if latest_session:
            current_dissonance = await self.dissonance_detector.detect(
                transcript=latest_session.get('transcript', ''),
                voice_emotion=latest_session.get('voice_emotion', 'neutral'),
                voice_features=latest_session.get('voice_features', {}),
                audio=latest_session.get('audio', None),
                sample_rate=latest_session.get('sample_rate', 16000),
                user_baseline=voice_baseline if voice_baseline.baseline_established else None
            )

        # 7. Assess current risk
        current_risk = await self.risk_assessor.assess(
            sessions=sessions,
            latest_dissonance=current_dissonance,
            emotional_patterns=emotional_patterns,
            triggers=triggers,
            baseline=voice_baseline,
            user_id=user_id
        )

        # 8. Create mental health profile
        mental_health_profile = await self.mh_profiler.create_profile(
            emotional_patterns=emotional_patterns,
            current_risk=current_risk,
            coping_profile=coping_profile,
            triggers=triggers,
            cultural_context=cultural_context,
            user_id=user_id
        )

        # 9. Calculate data confidence
        confidence = self._calculate_confidence(len(sessions))

        return AggregatedPatterns(
            user_id=user_id,
            generated_at=datetime.now(),
            sessions_analyzed=len(sessions),
            emotional_patterns=emotional_patterns,
            cultural_context=cultural_context,
            triggers=triggers,
            coping_profile=coping_profile,
            voice_baseline=voice_baseline,
            current_dissonance=current_dissonance,
            current_risk=current_risk,
            mental_health_profile=mental_health_profile,
            data_confidence=confidence
        )

    def _calculate_confidence(self, session_count: int) -> float:
        """
        Calculate confidence in patterns based on data quantity

        More sessions = higher confidence
        """
        if session_count < 3:
            return 0.3  # Low confidence
        elif session_count < 7:
            return 0.6  # Medium confidence
        elif session_count < 14:
            return 0.8  # Good confidence
        else:
            return 0.95  # High confidence
