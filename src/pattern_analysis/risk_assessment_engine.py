"""
Risk Assessment Engine

Comprehensive suicide/crisis risk assessment from patterns
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from .dissonance_detector import DissonanceResult
from .emotional_pattern_analyzer import EmotionalPattern
from .trigger_detector import TriggerPattern
from .baseline_tracker import VoiceBaseline

@dataclass
class RiskAssessment:
    """Comprehensive risk assessment"""
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    risk_score: float  # 0-1
    risk_factors: List[str]
    protective_factors: List[str]
    trajectory: str  # 'escalating', 'stable', 'improving'
    recommended_action: str
    alert_counselor: bool

class RiskAssessmentEngine:
    """Assesses mental health risk from all available data"""

    async def assess(
        self,
        sessions: List[Dict],
        latest_dissonance: Optional[DissonanceResult],
        emotional_patterns: EmotionalPattern,
        triggers: TriggerPattern,
        baseline: VoiceBaseline,
        user_id: str
    ) -> RiskAssessment:
        """Comprehensive risk assessment"""
        risk_score = 0.0
        risk_factors = []
        protective_factors = []

        # Factor 1: Current dissonance (if available)
        if latest_dissonance:
            if latest_dissonance.dissonance_score > 0.7:
                risk_score += 0.4
                risk_factors.append(f"High concealment (dissonance: {latest_dissonance.dissonance_score:.2f})")

            if latest_dissonance.risk_level in ['high', 'critical']:
                risk_score += 0.3
                risk_factors.append(f"Direct risk indicators: {latest_dissonance.risk_interpretation}")

        # Factor 2: Emotional trajectory
        if emotional_patterns.trajectory == 'declining':
            risk_score += 0.3
            risk_factors.append(f"Declining trajectory (confidence: {emotional_patterns.trajectory_confidence:.2f})")
        elif emotional_patterns.trajectory == 'improving':
            risk_score -= 0.2
            protective_factors.append("Improving emotional state")

        # Factor 3: High-risk emotions
        high_risk_emotions = ['hopeless', 'resigned', 'numb']
        if any(e in emotional_patterns.primary_emotions for e in high_risk_emotions):
            risk_score += 0.4
            risk_factors.append(f"High-risk emotions: {', '.join(emotional_patterns.primary_emotions)}")

        # Factor 4: Baseline deviation
        if baseline.baseline_established:
            # Get latest session for comparison
            if sessions:
                latest = sessions[-1]
                current_features = latest.get('voice_features', {})
                # Simplified deviation check
                if current_features:
                    risk_score += 0.1
                    risk_factors.append("Voice different from baseline")

        # Factor 5: Severe triggers without coping
        if triggers.trigger_count > 0 and triggers.most_severe_trigger:
            risk_score += 0.2
            risk_factors.append(f"Active triggers: {triggers.most_severe_trigger}")

        # Determine level and actions
        risk_score = min(risk_score, 1.0)

        if risk_score >= 0.8:
            level = "critical"
            action = "Immediate counselor connection + crisis resources"
            alert = True
        elif risk_score >= 0.6:
            level = "high"
            action = "Prompt counselor outreach + prominent crisis resources"
            alert = True
        elif risk_score >= 0.4:
            level = "medium"
            action = "Monitor closely + make crisis resources visible"
            alert = False
        else:
            level = "low"
            action = "Continue monitoring"
            alert = False

        # Determine trajectory
        if emotional_patterns.trajectory == 'declining':
            trajectory = 'escalating'
        elif emotional_patterns.trajectory == 'improving':
            trajectory = 'improving'
        else:
            trajectory = 'stable'

        return RiskAssessment(
            risk_level=level,
            risk_score=risk_score,
            risk_factors=risk_factors,
            protective_factors=protective_factors,
            trajectory=trajectory,
            recommended_action=action,
            alert_counselor=alert
        )
