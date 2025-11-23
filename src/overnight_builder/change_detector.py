"""
Change Detector

Tracks interface changes between builds and generates human-readable explanations.
Provides transparency - users understand why their interface changed.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pattern_analysis.pattern_aggregator import AggregatedPatterns


@dataclass
class InterfaceChange:
    """Represents a single interface change"""
    change_type: str  # Type of change
    component: str  # Component affected
    reason: str  # Human-readable explanation
    severity: str  # 'low', 'medium', 'high', 'critical'


class ChangeDetector:
    """
    Detects and explains interface changes

    Change Types:
    - risk_escalation: Risk level increased
    - risk_de_escalation: Risk level decreased
    - feature_added: New component shown
    - feature_hidden: Component hidden
    - theme_changed: Visual theme changed
    - language_adapted: Language/cultural adjustment
    - baseline_established: User baseline completed
    - trigger_detected: New trigger identified
    - coping_identified: New effective coping found
    """

    def detect(
        self,
        previous_config: Optional[Dict],
        new_config: Dict,
        patterns: AggregatedPatterns
    ) -> List[InterfaceChange]:
        """
        Detect all changes between configs

        Args:
            previous_config: Previous UI configuration (None for first build)
            new_config: New UI configuration
            patterns: Current user patterns

        Returns:
            List of InterfaceChange objects
        """

        changes: List[InterfaceChange] = []

        # First time build - no changes to detect
        if not previous_config:
            changes.append(InterfaceChange(
                change_type='baseline_established',
                component='overall',
                reason="We've built your first personalized interface based on your voice patterns. "
                       "Your interface will continue to adapt as we learn more about what supports you best.",
                severity='low'
            ))
            return changes

        # Theme changes
        theme_changes = self._detect_theme_changes(previous_config, new_config, patterns)
        changes.extend(theme_changes)

        # Risk level changes
        risk_changes = self._detect_risk_changes(previous_config, new_config, patterns)
        changes.extend(risk_changes)

        # Component visibility changes
        visibility_changes = self._detect_visibility_changes(previous_config, new_config, patterns)
        changes.extend(visibility_changes)

        # Language/cultural changes
        cultural_changes = self._detect_cultural_changes(previous_config, new_config, patterns)
        changes.extend(cultural_changes)

        # Pattern-based changes
        pattern_changes = self._detect_pattern_changes(previous_config, new_config, patterns)
        changes.extend(pattern_changes)

        return changes

    def _detect_theme_changes(
        self,
        previous_config: Dict,
        new_config: Dict,
        patterns: AggregatedPatterns
    ) -> List[InterfaceChange]:
        """Detect theme changes"""

        changes = []

        prev_theme = previous_config.get('theme', {}).get('base')
        new_theme = new_config.get('theme', {}).get('base')

        if prev_theme != new_theme:
            # Generate reason based on theme transition
            reasons = {
                ('calm', 'crisis'): "We've noticed concerning patterns in your voice. The interface now prioritizes your safety and support.",
                ('warm', 'crisis'): "Your emotional state shows elevated risk. We've adjusted the interface to focus on immediate support.",
                ('crisis', 'warm'): "We hear improvement in your voice. The interface is now focused on supporting your recovery.",
                ('crisis', 'calm'): "Your risk level has decreased. We've adjusted to a calmer, more spacious interface.",
                ('balanced', 'warm'): "Your voice shows signs of depression. We've shifted to a warmer, more energizing theme.",
                ('balanced', 'calm'): "Your voice shows anxiety patterns. We've shifted to a calmer, more peaceful theme.",
                ('warm', 'balanced'): "We hear stability in your voice. The interface now reflects your progress.",
                ('calm', 'balanced'): "Your emotional state has stabilized. The interface now supports continued growth.",
            }

            reason = reasons.get((prev_theme, new_theme),
                                 f"Your emotional patterns have shifted. We've adjusted the visual theme to better support you.")

            changes.append(InterfaceChange(
                change_type='theme_changed',
                component='overall_theme',
                reason=reason,
                severity='medium' if new_theme == 'crisis' else 'low'
            ))

        return changes

    def _detect_risk_changes(
        self,
        previous_config: Dict,
        new_config: Dict,
        patterns: AggregatedPatterns
    ) -> List[InterfaceChange]:
        """Detect risk level changes"""

        changes = []

        prev_risk = previous_config.get('metadata', {}).get('risk_level', 'low')
        new_risk = patterns.current_risk.risk_level

        if prev_risk != new_risk:
            risk_order = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}

            # Risk escalation
            if risk_order[new_risk] > risk_order[prev_risk]:
                reasons = {
                    ('low', 'medium'): "We've noticed some concerning patterns in your voice over the last few sessions. "
                                       "Crisis resources are now more visible to ensure you have support if needed.",
                    ('medium', 'high'): "Your voice has been different lately—flatter, with more pauses. "
                                        "We've moved crisis resources to ensure you have immediate access to support.",
                    ('high', 'critical'): "We're very concerned about what we're hearing in your voice. "
                                          "Please know that support is available 24/7. You don't have to face this alone.",
                    ('low', 'high'): "We've noticed significant changes in your voice patterns. "
                                     "Your safety is our priority, so we've made crisis support immediately available.",
                    ('medium', 'critical'): "We're deeply concerned about you. Your voice shows signs of severe distress. "
                                            "Crisis support is now at the top of your interface. Please reach out.",
                }

                reason = reasons.get((prev_risk, new_risk),
                                     f"Your risk level has increased from {prev_risk} to {new_risk}. "
                                     f"We've adjusted the interface to prioritize your safety.")

                changes.append(InterfaceChange(
                    change_type='risk_escalation',
                    component='CrisisResources',
                    reason=reason,
                    severity=new_risk
                ))

            # Risk de-escalation
            else:
                reasons = {
                    ('critical', 'high'): "We hear some improvement in your voice. While we're still concerned, "
                                          "the intensity has decreased slightly. Support remains easily accessible.",
                    ('high', 'medium'): "Your voice shows signs of stabilization. Crisis resources are still available "
                                        "but less prominent now. We're here if you need us.",
                    ('medium', 'low'): "We hear strength returning to your voice. The changes are encouraging. "
                                       "Crisis resources remain available but are now in the background.",
                    ('critical', 'medium'): "We hear significant improvement. Your voice sounds more stable. "
                                            "This is real progress. Support is still here when you need it.",
                    ('high', 'low'): "The improvement in your voice is clear. You've moved through a difficult time. "
                                     "Crisis resources remain available but are less prominent now.",
                }

                reason = reasons.get((prev_risk, new_risk),
                                     f"Your risk level has decreased from {prev_risk} to {new_risk}. "
                                     f"We've adjusted the interface to reflect your progress.")

                changes.append(InterfaceChange(
                    change_type='risk_de_escalation',
                    component='CrisisResources',
                    reason=reason,
                    severity='low'
                ))

        return changes

    def _detect_visibility_changes(
        self,
        previous_config: Dict,
        new_config: Dict,
        patterns: AggregatedPatterns
    ) -> List[InterfaceChange]:
        """Detect component visibility changes"""

        changes = []

        prev_components = set(previous_config.get('metadata', {}).get('primary_components', []))
        new_components = set(new_config.get('metadata', {}).get('primary_components', []))

        # Features added
        added = new_components - prev_components
        for component in added:
            reason = self._get_feature_added_reason(component, patterns)
            changes.append(InterfaceChange(
                change_type='feature_added',
                component=component,
                reason=reason,
                severity='medium' if component in ['SafetyCheck', 'CrisisResources'] else 'low'
            ))

        # Features hidden
        hidden = prev_components - new_components
        for component in hidden:
            reason = self._get_feature_hidden_reason(component, patterns)
            changes.append(InterfaceChange(
                change_type='feature_hidden',
                component=component,
                reason=reason,
                severity='low'
            ))

        return changes

    def _detect_cultural_changes(
        self,
        previous_config: Dict,
        new_config: Dict,
        patterns: AggregatedPatterns
    ) -> List[InterfaceChange]:
        """Detect cultural/language changes"""

        changes = []

        prev_lang = previous_config.get('cultural', {}).get('primary_language', 'english')
        new_lang = patterns.cultural_context.primary_language

        if prev_lang != new_lang:
            if new_lang == 'swahili':
                reason = "We've noticed you've been speaking more Swahili, especially during emotional moments. " \
                         "Your interface now includes more Swahili to match how you naturally express yourself."
            elif patterns.cultural_context.code_switching:
                reason = "We notice you mix English and Swahili. Your interface now reflects this, " \
                         "using both languages naturally like you do."
            else:
                reason = f"We've adjusted the language to match how you've been speaking."

            changes.append(InterfaceChange(
                change_type='language_adapted',
                component='CulturalGreeting',
                reason=reason,
                severity='low'
            ))

        return changes

    def _detect_pattern_changes(
        self,
        previous_config: Dict,
        new_config: Dict,
        patterns: AggregatedPatterns
    ) -> List[InterfaceChange]:
        """Detect pattern-based changes (triggers, coping, etc.)"""

        changes = []

        # Check if dissonance was newly detected
        if patterns.current_dissonance.dissonance_score > 0.7:
            prev_had_dissonance = 'DissonanceIndicator' in previous_config.get('metadata', {}).get('primary_components', [])
            new_has_dissonance = 'DissonanceIndicator' in new_config.get('metadata', {}).get('primary_components', [])

            if not prev_had_dissonance and new_has_dissonance:
                example = patterns.current_dissonance.dissonance_examples[0] if patterns.current_dissonance.dissonance_examples else None
                if example:
                    reason = f"We've noticed a gap between your words and your voice. For example, you said '{example}' " \
                             f"but your voice showed {patterns.current_dissonance.embodied_emotion}. " \
                             f"We added this indicator to gently acknowledge what we're hearing."
                else:
                    reason = "We've detected differences between what you say and how your voice sounds. " \
                             "This indicator helps us acknowledge the fuller truth of what you're experiencing."

                changes.append(InterfaceChange(
                    change_type='trigger_detected',
                    component='DissonanceIndicator',
                    reason=reason,
                    severity='medium'
                ))

        return changes

    def _get_feature_added_reason(self, component: str, patterns: AggregatedPatterns) -> str:
        """Generate reason for feature being added"""

        reasons = {
            'DissonanceIndicator': "We've noticed gaps between your words and your voice. "
                                   "This helps us acknowledge what we're really hearing.",
            'CrisisResources': "Based on patterns in your voice, we want to make sure support is easily accessible.",
            'GentleObservations': "We've noticed some patterns we want to share with you gently.",
            'WhatsWorking': "We've identified some coping strategies that seem to help you. Let's build on those.",
            'ProgressCelebration': "We hear real improvement in your voice. This progress deserves acknowledgment.",
            'TriggerAwareness': "We've identified some topics that affect your voice. Understanding these can help.",
            'SafetyCheck': "We need to check in directly about your safety. Your wellbeing is our priority.",
        }

        return reasons.get(component, f"We've added {component} to better support you.")

    def _get_feature_hidden_reason(self, component: str, patterns: AggregatedPatterns) -> str:
        """Generate reason for feature being hidden"""

        reasons = {
            'ProgressCelebration': "You're going through a harder time. We'll bring back progress tracking when things stabilize.",
            'DissonanceIndicator': "The gap between words and voice has closed. This is good progress.",
            'TriggerAwareness': "Triggers have lessened. We've moved this to make room for more relevant support.",
            'CrisisResources': "Your voice shows you're more stable. Crisis support is still available but less prominent now.",
        }

        return reasons.get(component, f"We've adjusted {component} to better match where you are now.")
