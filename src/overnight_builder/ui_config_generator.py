"""
UI Config Generator

Generates complete UI configurations from user patterns.
Orchestrates theme selection, component visibility, and layout prioritization.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from src.pattern_analysis.pattern_aggregator import AggregatedPatterns
from .theme_selector import ThemeSelector, ThemeConfig
from .component_visibility import ComponentVisibilityEngine, ComponentConfig
from .layout_prioritizer import LayoutPrioritizer
from .change_detector import ChangeDetector, InterfaceChange


@dataclass
class UIConfig:
    """Complete UI Configuration"""
    user_id: str
    generated_at: str
    version: str

    # Theme
    theme: Dict  # ThemeConfig as dict

    # Components
    components: Dict[str, Dict]  # component_name -> ComponentConfig as dict

    # Layout
    layout: Dict[str, List[str]]  # Layout sections with component lists
    mobile_layout: List[str]  # Mobile-optimized layout

    # Cultural context
    cultural: Dict

    # Changes from previous config
    changes: List[Dict]  # InterfaceChange as dict list

    # Metadata
    metadata: Dict


class UIConfigGenerator:
    """
    Generates personalized UI configurations from user patterns

    Process:
    1. Select theme based on emotional state and risk
    2. Generate component visibility and properties
    3. Prioritize layout order
    4. Detect changes from previous config
    5. Build complete UIConfig
    """

    def __init__(self):
        self.theme_selector = ThemeSelector()
        self.component_engine = ComponentVisibilityEngine()
        self.layout_prioritizer = LayoutPrioritizer()
        self.change_detector = ChangeDetector()
        self.version = "1.0.0"

    async def generate(
        self,
        user_id: str,
        patterns: AggregatedPatterns,
        previous_config: Optional[Dict] = None
    ) -> UIConfig:
        """
        Generate complete UI configuration

        Args:
            user_id: User identifier
            patterns: Aggregated user patterns
            previous_config: Previous UI config (None for first build)

        Returns:
            UIConfig object
        """

        # 1. Select theme
        theme = self.theme_selector.select(
            primary_emotions=patterns.emotional_patterns.primary_emotions,
            trajectory=patterns.emotional_patterns.trajectory,
            risk_level=patterns.current_risk.risk_level,
            variability_score=patterns.emotional_patterns.variability_score
        )

        # 2. Generate component configurations
        components = self.component_engine.generate_components(patterns)

        # 3. Prioritize layout
        component_names = self.layout_prioritizer.prioritize(components, patterns)

        # 4. Generate layout sections
        layout_sections = self.layout_prioritizer.generate_layout_sections(
            component_names,
            components
        )

        # 5. Mobile layout
        mobile_layout = self.layout_prioritizer.get_mobile_layout(
            component_names,
            patterns
        )

        # 6. Cultural overlay
        cultural_overlay = self.theme_selector.get_cultural_overlay(
            primary_language=patterns.cultural_context.primary_language,
            stoicism_level=patterns.cultural_context.stoicism_level
        )

        # 7. Build complete config dict for change detection
        new_config_dict = {
            'theme': asdict(theme),
            'components': {name: asdict(config) for name, config in components.items()},
            'layout': layout_sections,
            'mobile_layout': mobile_layout,
            'cultural': cultural_overlay,
            'metadata': {
                'risk_level': patterns.current_risk.risk_level,
                'trajectory': patterns.emotional_patterns.trajectory,
                'primary_emotions': patterns.emotional_patterns.primary_emotions,
                'primary_components': component_names,
                'dissonance_score': patterns.current_dissonance.dissonance_score,
            }
        }

        # 8. Detect changes
        changes = self.change_detector.detect(
            previous_config,
            new_config_dict,
            patterns
        )

        # 9. Build UIConfig
        config = UIConfig(
            user_id=user_id,
            generated_at=datetime.utcnow().isoformat(),
            version=self.version,
            theme=asdict(theme),
            components={name: asdict(config) for name, config in components.items()},
            layout=layout_sections,
            mobile_layout=mobile_layout,
            cultural=cultural_overlay,
            changes=[asdict(change) for change in changes],
            metadata={
                'risk_level': patterns.current_risk.risk_level,
                'trajectory': patterns.emotional_patterns.trajectory,
                'primary_emotions': patterns.emotional_patterns.primary_emotions,
                'primary_language': patterns.cultural_context.primary_language,
                'session_count': patterns.baseline.session_count,
                'dissonance_score': patterns.current_dissonance.dissonance_score,
                'trigger_count': patterns.triggers.trigger_count,
                'effective_coping_count': len(patterns.coping_profile.effective_strategies),
            }
        )

        return config

    def config_to_dict(self, config: UIConfig) -> Dict:
        """
        Convert UIConfig to dictionary

        Args:
            config: UIConfig object

        Returns:
            Dictionary representation
        """
        return asdict(config)

    def generate_changelog_summary(self, changes: List[InterfaceChange]) -> str:
        """
        Generate human-readable changelog summary

        Args:
            changes: List of interface changes

        Returns:
            Markdown-formatted changelog
        """

        if not changes:
            return "No changes to your interface."

        # Group by severity
        critical = [c for c in changes if c.severity == 'critical']
        high = [c for c in changes if c.severity == 'high']
        medium = [c for c in changes if c.severity == 'medium']
        low = [c for c in changes if c.severity == 'low']

        lines = ["# What Changed in Your Interface\n"]

        # Critical changes
        if critical:
            lines.append("## 🚨 Important Changes\n")
            for change in critical:
                lines.append(f"- **{change.component}**: {change.reason}\n")

        # High priority changes
        if high:
            lines.append("## ⚠️ Significant Changes\n")
            for change in high:
                lines.append(f"- **{change.component}**: {change.reason}\n")

        # Medium priority changes
        if medium:
            lines.append("## 📋 Adjustments\n")
            for change in medium:
                lines.append(f"- **{change.component}**: {change.reason}\n")

        # Low priority changes
        if low:
            lines.append("## ✨ Small Improvements\n")
            for change in low:
                lines.append(f"- {change.reason}\n")

        return "".join(lines)

    def get_first_time_explanation(self) -> str:
        """
        Get explanation for first-time users

        Returns:
            Explanation text
        """
        return """
# Welcome to Your Personalized Interface

This interface is uniquely yours. It was built based on patterns we've learned from your voice.

**How it works:**
- Every night while you sleep, we rebuild your interface based on what we've learned
- Components appear, move, or hide based on what supports you best right now
- Visual themes adjust to your emotional state
- Language and cultural elements match how you naturally express yourself

**What we're listening for:**
- The gap between your words and your voice (what you say vs. how you sound)
- Patterns in your emotions over time
- What helps you cope effectively
- Topics that affect you (triggers)
- Changes from your usual baseline

**Your privacy:**
- Your interface config is encrypted end-to-end
- We never store your raw audio
- Only anonymized patterns are kept
- You control your data

Your interface will continue to evolve as we learn more about what supports you best.
        """.strip()
