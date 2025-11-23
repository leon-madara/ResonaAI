"""
Layout Prioritizer

Orders UI components based on urgency, risk level, and user needs.
Risk-based prioritization ensures critical components are always visible first.
"""

from typing import List, Dict, Tuple
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pattern_analysis.pattern_aggregator import AggregatedPatterns
from .component_visibility import ComponentConfig


class LayoutPrioritizer:
    """
    Prioritizes component layout based on risk and importance

    Priority Levels:
    1. CRITICAL (100): Safety check, crisis resources for critical risk
    2. HIGH (80-90): Crisis resources for high risk, dissonance indicators
    3. MEDIUM (60-70): Voice recorder, monitoring components
    4. LOW (40-50): Insights, progress, coping strategies
    5. MINIMAL (20-30): Resources, educational content
    """

    def __init__(self):
        # Base priority scores for each component type
        self.base_priorities = {
            'SafetyCheck': 100,  # Always highest when present
            'CrisisResources': 90,
            'DissonanceIndicator': 85,
            'VoiceRecorder': 80,
            'CulturalGreeting': 75,
            'GentleObservations': 60,
            'WhatsWorking': 55,
            'ProgressCelebration': 50,
            'TriggerAwareness': 45,
            'PersonalizedResources': 40,
        }

    def prioritize(
        self,
        components: Dict[str, ComponentConfig],
        patterns: AggregatedPatterns
    ) -> List[str]:
        """
        Prioritize component layout order

        Args:
            components: Dict of component configurations
            patterns: User patterns for context

        Returns:
            List of component names in priority order (highest first)
        """

        priorities: List[Tuple[str, int]] = []

        for component_name, config in components.items():
            if not config.visible:
                continue

            # Calculate priority score
            priority = self._calculate_priority(
                component_name,
                config,
                patterns
            )

            priorities.append((component_name, priority))

        # Sort by priority (descending)
        sorted_components = sorted(priorities, key=lambda x: x[1], reverse=True)

        # Return component names only
        return [name for name, _ in sorted_components]

    def _calculate_priority(
        self,
        component_name: str,
        config: ComponentConfig,
        patterns: AggregatedPatterns
    ) -> int:
        """
        Calculate priority score for a component

        Args:
            component_name: Name of component
            config: Component configuration
            patterns: User patterns

        Returns:
            Priority score (0-100)
        """

        # Start with base priority
        base = self.base_priorities.get(component_name, 50)

        # Adjust based on urgency
        urgency_adjustments = {
            'critical': +15,
            'high': +10,
            'medium': +5,
            'low': 0,
            'none': 0
        }
        urgency_bonus = urgency_adjustments.get(config.urgency, 0)

        # Adjust based on prominence
        prominence_adjustments = {
            'modal': +10,
            'top': +5,
            'card': +3,
            'sidebar': 0,
            'minimal': -5,
            'hidden': -100  # Effectively removes from layout
        }
        prominence_bonus = prominence_adjustments.get(config.prominence, 0)

        # Risk-based adjustments
        risk_bonus = self._calculate_risk_bonus(component_name, patterns)

        # Trajectory-based adjustments
        trajectory_bonus = self._calculate_trajectory_bonus(component_name, patterns)

        # Calculate final priority
        priority = base + urgency_bonus + prominence_bonus + risk_bonus + trajectory_bonus

        # Clamp to 0-100
        return max(0, min(100, priority))

    def _calculate_risk_bonus(
        self,
        component_name: str,
        patterns: AggregatedPatterns
    ) -> int:
        """Calculate risk-based priority bonus"""

        risk_level = patterns.current_risk.risk_level

        # Critical risk: Prioritize safety and crisis resources
        if risk_level == 'critical':
            if component_name in ['SafetyCheck', 'CrisisResources']:
                return +20
            elif component_name == 'VoiceRecorder':
                return +10
            else:
                return -10  # De-prioritize other components

        # High risk: Prioritize crisis support and monitoring
        elif risk_level == 'high':
            if component_name in ['CrisisResources', 'DissonanceIndicator']:
                return +15
            elif component_name == 'VoiceRecorder':
                return +5
            elif component_name in ['ProgressCelebration', 'TriggerAwareness']:
                return -5  # Less important during high risk

        # Medium risk: Balanced approach
        elif risk_level == 'medium':
            if component_name in ['CrisisResources', 'DissonanceIndicator']:
                return +5
            elif component_name == 'ProgressCelebration':
                return -3

        # Low risk: Prioritize growth and progress
        else:
            if component_name in ['ProgressCelebration', 'WhatsWorking']:
                return +5
            elif component_name == 'CrisisResources':
                return -10  # De-prioritize crisis resources

        return 0

    def _calculate_trajectory_bonus(
        self,
        component_name: str,
        patterns: AggregatedPatterns
    ) -> int:
        """Calculate trajectory-based priority bonus"""

        trajectory = patterns.emotional_patterns.trajectory

        # Declining: Prioritize support and monitoring
        if trajectory == 'declining':
            if component_name in ['GentleObservations', 'DissonanceIndicator', 'CrisisResources']:
                return +5
            elif component_name == 'ProgressCelebration':
                return -10  # Don't celebrate during decline

        # Improving: Prioritize progress and strengths
        elif trajectory == 'improving':
            if component_name in ['ProgressCelebration', 'WhatsWorking']:
                return +10
            elif component_name in ['CrisisResources', 'SafetyCheck']:
                return -5  # De-prioritize crisis components

        # Volatile: Prioritize grounding and stability
        elif trajectory == 'volatile':
            if component_name in ['VoiceRecorder', 'CulturalGreeting', 'WhatsWorking']:
                return +5
            elif component_name == 'ProgressCelebration':
                return -5

        return 0

    def generate_layout_sections(
        self,
        prioritized_components: List[str],
        components: Dict[str, ComponentConfig]
    ) -> Dict[str, List[str]]:
        """
        Organize components into layout sections

        Args:
            prioritized_components: Component names in priority order
            components: Component configurations

        Returns:
            Dict mapping section names to component lists
        """

        sections = {
            'hero': [],      # Critical, top of page
            'primary': [],   # Main content area
            'sidebar': [],   # Secondary content
            'footer': []     # Resources, low priority
        }

        for component_name in prioritized_components:
            config = components[component_name]

            # Route to section based on prominence
            if config.prominence == 'modal':
                sections['hero'].append(component_name)
            elif config.prominence in ['top', 'card']:
                if config.urgency in ['critical', 'high']:
                    sections['hero'].append(component_name)
                else:
                    sections['primary'].append(component_name)
            elif config.prominence == 'sidebar':
                sections['sidebar'].append(component_name)
            else:
                sections['footer'].append(component_name)

        return sections

    def get_mobile_layout(
        self,
        prioritized_components: List[str],
        patterns: AggregatedPatterns
    ) -> List[str]:
        """
        Generate mobile-optimized layout (single column)

        On mobile, only show top 5-7 most important components
        to avoid overwhelming on small screens.

        Args:
            prioritized_components: Component names in priority order
            patterns: User patterns

        Returns:
            Mobile layout component order
        """

        risk_level = patterns.current_risk.risk_level

        # Critical risk: Show only essential components
        if risk_level == 'critical':
            return prioritized_components[:3]  # Top 3 only

        # High risk: Show 5 components
        elif risk_level == 'high':
            return prioritized_components[:5]

        # Normal: Show up to 7 components
        else:
            return prioritized_components[:7]
