"""
Mental Health Profiler

Creates comprehensive mental health profile from all patterns
"""

from typing import List, Optional
from dataclasses import dataclass
from .emotional_pattern_analyzer import EmotionalPattern
from .risk_assessment_engine import RiskAssessment
from .coping_effectiveness_tracker import CopingProfile
from .trigger_detector import TriggerPattern
from .cultural_context_analyzer import CulturalContext

@dataclass
class MentalHealthProfile:
    """Comprehensive mental health profile"""
    user_id: str

    # Primary concerns
    primary_concerns: List[str]  # e.g., ['depression', 'anxiety']
    secondary_concerns: List[str]

    # Current state
    current_state: str  # 'crisis', 'struggling', 'managing', 'stable', 'improving'
    current_risk: str

    # Support needs
    support_needs: List[str]  # What kind of support they need
    communication_style: str  # How to talk to them

    # Strengths
    identified_strengths: List[str]
    effective_coping: List[str]

    # Challenges
    identified_challenges: List[str]
    ineffective_patterns: List[str]

class MentalHealthProfiler:
    """Creates comprehensive mental health profiles"""

    async def create_profile(
        self,
        emotional_patterns: EmotionalPattern,
        current_risk: RiskAssessment,
        coping_profile: CopingProfile,
        triggers: TriggerPattern,
        cultural_context: CulturalContext,
        user_id: str
    ) -> MentalHealthProfile:
        """Create comprehensive profile"""

        # 1. Identify primary concerns from emotional patterns
        primary_concerns = []
        if 'sad' in emotional_patterns.primary_emotions or 'hopeless' in emotional_patterns.primary_emotions:
            primary_concerns.append('depression')
        if 'fear' in emotional_patterns.primary_emotions:
            primary_concerns.append('anxiety')
        if 'angry' in emotional_patterns.primary_emotions:
            primary_concerns.append('anger_management')

        # 2. Determine current state
        if current_risk.risk_level == 'critical':
            state = 'crisis'
        elif current_risk.risk_level == 'high':
            state = 'struggling'
        elif emotional_patterns.trajectory == 'improving':
            state = 'improving'
        elif emotional_patterns.trajectory == 'stable':
            state = 'stable'
        else:
            state = 'managing'

        # 3. Identify support needs
        support_needs = []
        if current_risk.risk_level in ['high', 'critical']:
            support_needs.append('immediate_professional_support')
        if not coping_profile.effective_strategies:
            support_needs.append('coping_skill_development')
        if triggers.trigger_count > 0:
            support_needs.append('trigger_processing')
        if cultural_context.stoicism_level == 'high':
            support_needs.append('permission_to_be_vulnerable')

        # 4. Communication style recommendation
        comm_style = cultural_context.recommended_approach

        # 5. Identify strengths
        strengths = []
        if coping_profile.effective_strategies:
            strengths.append(f"Has {len(coping_profile.effective_strategies)} effective coping strategies")
        if coping_profile.coping_consistency > 0.5:
            strengths.append("Consistently employs coping")
        if emotional_patterns.trajectory == 'improving':
            strengths.append("Showing improvement over time")

        effective_coping = [s.name for s in coping_profile.effective_strategies]

        # 6. Identify challenges
        challenges = []
        if current_risk.risk_level in ['high', 'critical']:
            challenges.append("Elevated suicide risk")
        if triggers.trigger_count > 0:
            challenges.append(f"Multiple triggers ({triggers.most_severe_trigger} most severe)")
        if emotional_patterns.trajectory == 'declining':
            challenges.append("Declining emotional state")
        if not coping_profile.effective_strategies:
            challenges.append("No effective coping strategies identified yet")

        ineffective = [s.name for s in coping_profile.ineffective_strategies]

        return MentalHealthProfile(
            user_id=user_id,
            primary_concerns=primary_concerns,
            secondary_concerns=[],
            current_state=state,
            current_risk=current_risk.risk_level,
            support_needs=support_needs,
            communication_style=comm_style,
            identified_strengths=strengths,
            effective_coping=effective_coping,
            identified_challenges=challenges,
            ineffective_patterns=ineffective
        )
