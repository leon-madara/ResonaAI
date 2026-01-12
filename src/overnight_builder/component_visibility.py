"""
Component Visibility Engine

Determines which UI components to show, hide, or emphasize based on user patterns.
Implements progressive disclosure - only show what's relevant now.
"""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from src.pattern_analysis.pattern_aggregator import AggregatedPatterns


@dataclass
class ComponentConfig:
    """Configuration for a single UI component"""
    component_name: str
    visible: bool
    prominence: str  # 'hidden', 'minimal', 'sidebar', 'card', 'top', 'modal'
    props: Dict  # Component-specific properties
    urgency: str  # 'none', 'low', 'medium', 'high', 'critical'


class ComponentVisibilityEngine:
    """
    Determines component visibility and prominence based on patterns

    Components managed:
    - VoiceRecorder: Primary input (always visible)
    - CulturalGreeting: Personalized greeting (always visible)
    - DissonanceIndicator: Shows word-voice gap (if high dissonance)
    - CrisisResources: Crisis support (if medium+ risk)
    - GentleObservations: Pattern insights (if deflection or triggers)
    - WhatsWorking: Effective coping strategies (if any identified)
    - ProgressCelebration: Improvement celebration (if improving)
    - TriggerAwareness: Trigger education (if triggers identified)
    - SafetyCheck: Direct safety assessment (if critical risk)
    """

    def __init__(self):
        # Visibility rules for each component
        self.rules = {
            'VoiceRecorder': self._voice_recorder_config,
            'CulturalGreeting': self._cultural_greeting_config,
            'DissonanceIndicator': self._dissonance_indicator_config,
            'CrisisResources': self._crisis_resources_config,
            'GentleObservations': self._gentle_observations_config,
            'WhatsWorking': self._whats_working_config,
            'ProgressCelebration': self._progress_celebration_config,
            'TriggerAwareness': self._trigger_awareness_config,
            'SafetyCheck': self._safety_check_config,
            'PersonalizedResources': self._personalized_resources_config,
        }

    def generate_components(
        self,
        patterns: AggregatedPatterns
    ) -> Dict[str, ComponentConfig]:
        """
        Generate component configurations for all components

        Args:
            patterns: Aggregated user patterns

        Returns:
            Dict mapping component name to configuration
        """
        components = {}

        for component_name, rule_func in self.rules.items():
            config = rule_func(patterns)
            if config:  # Only include if config is returned
                components[component_name] = config

        return components

    # ========================================================================
    # COMPONENT RULES
    # ========================================================================

    def _voice_recorder_config(self, patterns: AggregatedPatterns) -> ComponentConfig:
        """VoiceRecorder: Always visible, primary input"""

        # Determine prompt based on patterns
        if patterns.cultural_context.primary_language == 'swahili':
            if patterns.cultural_context.code_switching_detected:
                prompt = "Niambie hali yako halisi? (Tell me how you're really doing?)"
            else:
                prompt = "Habari yako? Niambie kitu..."
        else:
            prompt = "How are you really doing?"

        # Urgency based on risk
        urgency_map = {
            'low': 'low',
            'medium': 'medium',
            'high': 'high',
            'critical': 'critical'
        }

        return ComponentConfig(
            component_name='VoiceRecorder',
            visible=True,
            prominence='top',
            urgency=urgency_map.get(patterns.current_risk.risk_level, 'medium'),
            props={
                'prompt': prompt,
                'culturalMode': patterns.cultural_context.primary_language,
                'encouragement': self._get_encouragement(patterns)
            }
        )

    def _cultural_greeting_config(self, patterns: AggregatedPatterns) -> ComponentConfig:
        """CulturalGreeting: Always visible, personalized"""

        # Determine language
        language = 'mixed' if patterns.cultural_context.code_switching_detected else patterns.cultural_context.primary_language

        # Personalization based on trajectory
        if patterns.emotional_patterns.trajectory == 'declining':
            personalization = "Your voice has been different lately. We're here."
        elif patterns.emotional_patterns.trajectory == 'improving':
            personalization = "We hear the strength in your voice today."
        elif patterns.current_risk.risk_level in ['high', 'critical']:
            personalization = "We're concerned about you. Let's talk."
        else:
            personalization = "We're listening."

        return ComponentConfig(
            component_name='CulturalGreeting',
            visible=True,
            prominence='top',
            urgency='none',
            props={
                'language': language,
                'personalization': personalization,
                'mood': self._get_greeting_mood(patterns)
            }
        )

    def _dissonance_indicator_config(self, patterns: AggregatedPatterns) -> Optional[ComponentConfig]:
        """DissonanceIndicator: Show if high dissonance detected"""

        dissonance_score = patterns.current_dissonance.dissonance_score if patterns.current_dissonance else 0.0

        # Only show if dissonance is significant
        if dissonance_score < 0.6:
            return None

        # Prominence based on score
        if dissonance_score >= 0.8:
            prominence = 'card'
        else:
            prominence = 'sidebar'

        return ComponentConfig(
            component_name='DissonanceIndicator',
            visible=True,
            prominence=prominence,
            urgency='medium' if dissonance_score >= 0.8 else 'low',
            props={
                'dissonance_score': dissonance_score,
                'gap_explanation': patterns.current_dissonance.gap_explanation,
                'truth_signal': patterns.current_dissonance.truth_signal,
                'example': patterns.current_dissonance.dissonance_examples[0] if patterns.current_dissonance.dissonance_examples else None
            }
        )

    def _crisis_resources_config(self, patterns: AggregatedPatterns) -> Optional[ComponentConfig]:
        """CrisisResources: Show if risk is medium or above"""

        risk_level = patterns.current_risk.risk_level

        # Only show for medium+ risk
        if risk_level in ('low', 'unknown'):
            return None

        # Prominence based on risk
        prominence_map = {
            'medium': 'sidebar',
            'high': 'card',
            'critical': 'modal'
        }

        urgency_map = {
            'medium': 'medium',
            'high': 'high',
            'critical': 'critical'
        }

        return ComponentConfig(
            component_name='CrisisResources',
            visible=True,
            prominence=prominence_map.get(risk_level, 'sidebar'),
            urgency=urgency_map.get(risk_level, 'medium'),
            props={
                'risk_level': risk_level,
                'resources': self._get_crisis_resources(patterns),
                'tone': 'urgent' if risk_level == 'critical' else 'supportive'
            }
        )

    def _gentle_observations_config(self, patterns: AggregatedPatterns) -> Optional[ComponentConfig]:
        """GentleObservations: Show if deflection or triggers detected"""

        deflection_freq = patterns.cultural_context.deflection_frequency
        has_triggers = patterns.triggers.trigger_count > 0

        # Only show if there are observations to share
        if deflection_freq < 0.3 and not has_triggers:
            return None

        observations = []

        # Deflection observations
        if deflection_freq >= 0.5:
            common_phrase = patterns.cultural_context.deflection_phrases[0] if patterns.cultural_context.deflection_phrases else 'sawa'
            observations.append(f"You've said '{common_phrase}' several times, but your voice showed sadness.")

        # Trigger observations
        if has_triggers and patterns.triggers.most_severe_trigger:
            trigger = patterns.triggers.most_severe_trigger
            observations.append(f"We notice your voice changes when you mention {trigger}.")

        return ComponentConfig(
            component_name='GentleObservations',
            visible=True,
            prominence='card',
            urgency='low',
            props={
                'observations': observations,
                'tone': 'gentle',
                'culturalSensitivity': 'high' if patterns.cultural_context.stoicism_level == 'high' else 'medium'
            }
        )

    def _whats_working_config(self, patterns: AggregatedPatterns) -> Optional[ComponentConfig]:
        """WhatsWorking: Show if effective coping strategies identified"""

        effective_strategies = patterns.coping_profile.effective_strategies

        # Only show if we have identified effective strategies
        if not effective_strategies:
            return None

        return ComponentConfig(
            component_name='WhatsWorking',
            visible=True,
            prominence='card',
            urgency='none',
            props={
                'strategies': [s.name for s in effective_strategies[:3]],  # Top 3
                'effectiveness': [s.effectiveness_score for s in effective_strategies[:3]],
                'encouragement': "These have helped you before. Keep going."
            }
        )

    def _progress_celebration_config(self, patterns: AggregatedPatterns) -> Optional[ComponentConfig]:
        """ProgressCelebration: Show only if improving"""

        trajectory = patterns.emotional_patterns.trajectory

        # Only show if improving
        if trajectory != 'improving':
            return None

        return ComponentConfig(
            component_name='ProgressCelebration',
            visible=True,
            prominence='card',
            urgency='none',
            props={
                'message': "Your voice tells us you're doing better. We hear the change.",
                'trajectory': trajectory,
                'show_chart': True
            }
        )

    def _trigger_awareness_config(self, patterns: AggregatedPatterns) -> Optional[ComponentConfig]:
        """TriggerAwareness: Show if triggers identified"""

        triggers = patterns.triggers

        # Only show if triggers exist
        if triggers.trigger_count == 0:
            return None

        # Don't show if risk is critical (too much info)
        if patterns.current_risk.risk_level == 'critical':
            return None

        return ComponentConfig(
            component_name='TriggerAwareness',
            visible=True,
            prominence='sidebar',
            urgency='low',
            props={
                'triggers': list(triggers.triggers.keys())[:3],  # Top 3
                'most_severe': triggers.most_severe_trigger,
                'educational': True
            }
        )

    def _safety_check_config(self, patterns: AggregatedPatterns) -> Optional[ComponentConfig]:
        """SafetyCheck: Direct safety questions for critical risk"""

        # Only show for critical risk
        if patterns.current_risk.risk_level != 'critical':
            return None

        return ComponentConfig(
            component_name='SafetyCheck',
            visible=True,
            prominence='modal',
            urgency='critical',
            props={
                'questions': [
                    "Are you safe right now?",
                    "Do you have thoughts of hurting yourself?",
                    "Can we connect you with someone who can help?"
                ],
                'resources_immediate': True
            }
        )

    def _personalized_resources_config(self, patterns: AggregatedPatterns) -> ComponentConfig:
        """PersonalizedResources: Always show, tailored to concerns"""

        resources = []

        # Add resources based on primary concerns
        if 'depression' in patterns.mental_health_profile.primary_concerns:
            resources.append('Understanding Depression')

        if 'anxiety' in patterns.mental_health_profile.primary_concerns:
            resources.append('Managing Anxiety')

        # Cultural resources
        if patterns.cultural_context.primary_language == 'swahili':
            resources.append('Swahili Mental Health Resources')

        return ComponentConfig(
            component_name='PersonalizedResources',
            visible=True,
            prominence='sidebar',
            urgency='none',
            props={
                'resources': resources,
                'language': patterns.cultural_context.primary_language
            }
        )

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _get_encouragement(self, patterns: AggregatedPatterns) -> str:
        """Get encouragement message for voice recorder"""
        if patterns.current_risk.risk_level in ['high', 'critical']:
            return "Your voice matters. We're here to listen."
        elif patterns.emotional_patterns.trajectory == 'declining':
            return "Take your time. We hear you."
        else:
            return "Tell us what's on your mind."

    def _get_greeting_mood(self, patterns: AggregatedPatterns) -> str:
        """Determine greeting mood"""
        if patterns.current_risk.risk_level in ['high', 'critical']:
            return 'concerned'
        elif patterns.emotional_patterns.trajectory == 'improving':
            return 'celebratory'
        elif patterns.emotional_patterns.trajectory == 'declining':
            return 'gentle'
        else:
            return 'warm'

    def _get_crisis_resources(self, patterns: AggregatedPatterns) -> List[Dict]:
        """Get appropriate crisis resources"""
        # Kenya crisis lines (example)
        resources = [
            {
                'name': 'Kenya Red Cross Counseling',
                'phone': '1199',
                'available': '24/7'
            },
            {
                'name': 'Befrienders Kenya',
                'phone': '+254 722 178 177',
                'available': '24/7'
            }
        ]

        return resources
