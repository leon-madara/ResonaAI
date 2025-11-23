"""
Theme Selector

Selects UI theme based on emotional state, risk level, and trajectory.
Maps emotional patterns to visual themes that support user's current state.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class ThemeConfig:
    """UI Theme Configuration"""
    name: str  # Theme identifier
    base: str  # Base theme type
    overlay: Optional[str]  # Optional overlay for combined states

    # Color palette
    colors: Dict[str, str]

    # Visual properties
    spacing: str  # 'compressed', 'comfortable', 'spacious'
    animations: str  # 'none', 'gentle', 'moderate'
    contrast: str  # 'low', 'medium', 'high'

    # Typography
    font_scale: float  # Relative size multiplier

    # Description
    description: str


class ThemeSelector:
    """
    Selects appropriate theme based on emotional state and risk level

    Decision Matrix:
    - Anxiety (fear) + Low-Medium risk → Calm theme (blues, greens, spacious)
    - Depression (sad) + Low-Medium risk → Warm theme (oranges, yellows, energizing)
    - Any emotion + High-Critical risk → Crisis theme (high contrast, clear)
    - Neutral/improving + Low risk → Balanced theme (teals, growth-focused)
    - Mixed/volatile → Adaptive theme (mixed warm/cool)
    """

    def __init__(self):
        # Theme definitions
        self.themes = {
            'calm': {
                'name': 'Calm',
                'description': 'Spacious, slow, peaceful - for anxiety',
                'colors': {
                    'primary': '#4A90A4',  # Soft blue
                    'secondary': '#6B9F8F',  # Sage green
                    'background': '#F7F9FA',  # Light gray-blue
                    'text': '#2C3E50',
                    'accent': '#7EB09B',
                    'warning': '#E8B44C'  # Muted yellow
                },
                'spacing': 'spacious',
                'animations': 'gentle',
                'contrast': 'medium',
                'font_scale': 1.0
            },
            'warm': {
                'name': 'Warm',
                'description': 'Energizing, hopeful - for depression',
                'colors': {
                    'primary': '#E07A5F',  # Warm coral
                    'secondary': '#F2CC8F',  # Soft yellow
                    'background': '#FFFAF5',  # Warm white
                    'text': '#3D3D3D',
                    'accent': '#F4A261',
                    'warning': '#E76F51'  # Orange
                },
                'spacing': 'comfortable',
                'animations': 'moderate',
                'contrast': 'medium',
                'font_scale': 1.05
            },
            'crisis': {
                'name': 'Crisis',
                'description': 'High contrast, clear, urgent - for high risk',
                'colors': {
                    'primary': '#2C3E50',  # Dark blue-gray
                    'secondary': '#E74C3C',  # Alert red
                    'background': '#FFFFFF',  # Pure white
                    'text': '#000000',
                    'accent': '#E67E22',  # Orange
                    'warning': '#C0392B'  # Dark red
                },
                'spacing': 'compressed',
                'animations': 'none',
                'contrast': 'high',
                'font_scale': 1.1
            },
            'balanced': {
                'name': 'Balanced',
                'description': 'Growth-focused, stable - for improving state',
                'colors': {
                    'primary': '#3498DB',  # Bright blue
                    'secondary': '#1ABC9C',  # Teal
                    'background': '#F8FAFB',
                    'text': '#34495E',
                    'accent': '#16A085',
                    'warning': '#F39C12'
                },
                'spacing': 'comfortable',
                'animations': 'moderate',
                'contrast': 'medium',
                'font_scale': 1.0
            },
            'adaptive': {
                'name': 'Adaptive',
                'description': 'Mixed warm/cool - for volatile state',
                'colors': {
                    'primary': '#5D6D7E',  # Neutral gray-blue
                    'secondary': '#AF7AC5',  # Soft purple
                    'background': '#F9F9F9',
                    'text': '#2C3E50',
                    'accent': '#85929E',
                    'warning': '#E59866'
                },
                'spacing': 'comfortable',
                'animations': 'gentle',
                'contrast': 'medium',
                'font_scale': 1.0
            }
        }

    def select(
        self,
        primary_emotions: List[str],
        trajectory: str,
        risk_level: str,
        variability_score: float = 0.0
    ) -> ThemeConfig:
        """
        Select appropriate theme

        Args:
            primary_emotions: List of dominant emotions
            trajectory: 'improving', 'declining', 'stable', 'volatile'
            risk_level: 'low', 'medium', 'high', 'critical'
            variability_score: Emotional variability (0-1)

        Returns:
            ThemeConfig with selected theme
        """

        # CRITICAL RISK: Always use crisis theme
        if risk_level == 'critical':
            theme = self._build_theme('crisis', overlay='critical')
            theme.colors['warning'] = '#C0392B'  # Intensify warning color
            return theme

        # HIGH RISK: Crisis theme with slightly softer approach
        if risk_level == 'high':
            theme = self._build_theme('crisis', overlay='concerned')
            theme.colors['secondary'] = '#E67E22'  # Less intense than pure red
            theme.spacing = 'comfortable'  # Slightly less compressed
            return theme

        # VOLATILE: Adaptive theme
        if trajectory == 'volatile' or variability_score > 0.7:
            return self._build_theme('adaptive')

        # IMPROVING: Balanced theme
        if trajectory == 'improving':
            return self._build_theme('balanced')

        # Emotion-based selection for medium/low risk

        # ANXIETY: Calm theme
        if 'fear' in primary_emotions or 'anxious' in primary_emotions:
            theme = self._build_theme('calm')

            # If medium risk, add subtle alert accents
            if risk_level == 'medium':
                theme.overlay = 'alert'
                theme.colors['warning'] = '#E8B44C'  # More visible warning

            return theme

        # DEPRESSION: Warm theme
        if any(e in primary_emotions for e in ['sad', 'hopeless', 'resigned', 'numb']):
            theme = self._build_theme('warm')

            # If medium risk and declining, add alert overlay
            if risk_level == 'medium' and trajectory == 'declining':
                theme.overlay = 'concerned'
                theme.colors['warning'] = '#E76F51'  # Elevated warning

            return theme

        # ANGER: Calm theme (de-escalation)
        if 'angry' in primary_emotions:
            return self._build_theme('calm')

        # NEUTRAL/STABLE: Balanced theme
        if 'neutral' in primary_emotions or trajectory == 'stable':
            return self._build_theme('balanced')

        # DEFAULT: Balanced theme
        return self._build_theme('balanced')

    def _build_theme(
        self,
        base_theme: str,
        overlay: Optional[str] = None
    ) -> ThemeConfig:
        """
        Build ThemeConfig from theme definition

        Args:
            base_theme: Base theme key
            overlay: Optional overlay descriptor

        Returns:
            ThemeConfig instance
        """
        theme_def = self.themes[base_theme]

        return ThemeConfig(
            name=theme_def['name'],
            base=base_theme,
            overlay=overlay,
            colors=theme_def['colors'].copy(),
            spacing=theme_def['spacing'],
            animations=theme_def['animations'],
            contrast=theme_def['contrast'],
            font_scale=theme_def['font_scale'],
            description=theme_def['description']
        )

    def get_cultural_overlay(
        self,
        primary_language: str,
        stoicism_level: str
    ) -> Dict[str, any]:
        """
        Get cultural adjustments to theme

        Args:
            primary_language: User's primary language
            stoicism_level: 'low', 'medium', 'high'

        Returns:
            Cultural overlay configuration
        """
        overlay = {}

        # Swahili/East African cultural adjustments
        if primary_language == 'swahili':
            overlay['language'] = 'swahili'
            overlay['greeting_style'] = 'warm_formal'

            # High stoicism: More direct language needed
            if stoicism_level == 'high':
                overlay['directness'] = 'high'
                overlay['validation_style'] = 'subtle'
            else:
                overlay['directness'] = 'medium'
                overlay['validation_style'] = 'gentle'

        return overlay
