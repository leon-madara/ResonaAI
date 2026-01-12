# Overnight Interface Builder

**The Magic That Happens While You Sleep**

> "Every night, while users rest, Resona analyzes their voice patterns and rebuilds their interface to match their truth, their needs, their journey."

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Build Pipeline](#build-pipeline)
5. [Implementation](#implementation)

---

## Overview

### The Concept

Users talk during the day → Patterns detected → **Overnight, interface rebuilds** → Next morning, personalized experience awaits

### What It Does

```
11 PM: Build Process Starts
    ↓
[Fetch all active users with recent activity]
    ↓
For each user:
    ├─→ [Get current patterns from database]
    ├─→ [Select theme based on emotional state]
    ├─→ [Determine component visibility (show/hide)]
    ├─→ [Prioritize layout (risk-based ordering)]
    ├─→ [Detect what changed from previous config]
    ├─→ [Generate UI configuration]
    ├─→ [Encrypt configuration]
    └─→ [Store to database + mark as deployed]
    ↓
6 AM: All interfaces ready
    ↓
Users log in: Personalized interface awaits
```

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────┐
│  Nightly Scheduler                                  │
│  (Runs at 2 AM in each user's timezone)            │
└─────────────────────┬───────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│  Overnight Builder Orchestrator                     │
└─────────────────────┬───────────────────────────────┘
                      ↓
        ┌─────────────┴──────────────┐
        ↓                            ↓
┌──────────────────┐      ┌──────────────────┐
│  Pattern Fetcher │      │  Previous Config │
│  (from database) │      │  (for comparison)│
└────────┬─────────┘      └────────┬─────────┘
         │                         │
         └──────────┬──────────────┘
                    ↓
        ┌───────────────────────┐
        │  UI Config Generator  │
        └───────────┬───────────┘
                    ↓
        ┌───────────────────────┐
        │  Theme Selector       │
        │  (emotional → theme)  │
        └───────────┬───────────┘
                    ↓
        ┌───────────────────────┐
        │  Component Visibility │
        │  (show/hide logic)    │
        └───────────┬───────────┘
                    ↓
        ┌───────────────────────┐
        │  Layout Prioritizer   │
        │  (risk-based order)   │
        └───────────┬───────────┘
                    ↓
        ┌───────────────────────┐
        │  Change Detector      │
        │  (what changed & why) │
        └───────────┬───────────┘
                    ↓
        ┌───────────────────────┐
        │  Encryption Service   │
        │  (E2E encrypt config) │
        └───────────┬───────────┘
                    ↓
        ┌───────────────────────┐
        │  Database Storage     │
        │  (save + deploy)      │
        └───────────────────────┘
```

---

## Core Components

### 1. UIConfigGenerator

**Purpose**: Generate complete UI configuration from patterns

**Input**: AggregatedPatterns + Previous Config
**Output**: UIConfig (theme, components, layout, prompts)

**Example**:
```python
patterns = {
    'emotional': {'trajectory': 'declining', 'primary': ['sad']},
    'risk': {'level': 'medium-high'},
    'cultural': {'language': 'mixed', 'stoicism': 'high'},
    'triggers': {'family': 0.8},
    'coping': {'effective': ['breathing']}
}

config = UIConfigGenerator.generate(patterns)

# Output:
{
    'theme': 'depression',  # Warm, energizing
    'greeting': {
        'text': 'Habari Sarah',
        'personalization': 'Your evenings have been harder lately'
    },
    'components': {
        'VoiceRecorder': {
            'visible': True,
            'prompt': 'Niambie hali yako halisi?',
            'urgency': 'medium'
        },
        'DissonanceIndicator': {
            'visible': True,  # High dissonance detected
            'prominence': 'card'
        },
        'CrisisResources': {
            'visible': True,  # Risk elevated
            'prominence': 'sidebar'
        },
        'WhatsWorking': {
            'visible': True,
            'strategies': ['Breathing exercises']
        },
        'GentleObservations': {
            'visible': True,
            'observations': [
                'You said "sawa" 4 times but voice showed sadness',
                'Family mentions bring tension to your voice'
            ]
        },
        'ProgressCelebration': {
            'visible': False  # Declining, not appropriate
        }
    },
    'layout': {
        'priority': [
            'VoiceRecorder',
            'DissonanceIndicator',
            'CrisisResources',
            'GentleObservations',
            'WhatsWorking'
        ]
    }
}
```

---

### 2. ThemeSelector

**Purpose**: Choose theme based on emotional state and risk

**Decision Matrix**:

| Primary Emotion | Risk Level | Theme | Colors | Tone |
|----------------|-----------|-------|--------|------|
| Anxiety (fear) | Low-Medium | **Calm** | Blues, greens | Spacious, slow |
| Depression (sad, hopeless) | Low-Medium | **Warm** | Oranges, yellows | Energizing |
| Any | High-Critical | **Crisis** | High contrast, alert | Clear, urgent |
| Neutral, improving | Low | **Balanced** | Teals | Growth-focused |
| Mixed/volatile | Medium | **Adaptive** | Mixed warm/cool | Balanced |

**Example**:
```python
# User: Sad + declining + medium-high risk
theme = ThemeSelector.select(
    primary_emotions=['sad', 'hopeless'],
    trajectory='declining',
    risk_level='medium-high'
)

# Returns:
{
    'name': 'Warm + Alert',
    'base': 'depression',  # Warm colors
    'overlay': 'concerned',  # Add alert accents
    'colors': {
        'primary': '#E07A5F',  # Warm coral
        'secondary': '#F2CC8F',  # Yellow
        'warning': '#E76F51'  # Alert orange (elevated)
    },
    'spacing': 'comfortable',
    'animations': 'gentle'
}
```

---

### 3. ComponentVisibilityEngine

**Purpose**: Decide what to show, hide, or emphasize

**Rules**:

```python
visibility_rules = {
    # Crisis resources
    'CrisisResources': {
        'show_if': lambda p: p.risk_level in ['medium', 'high', 'critical'],
        'prominence': lambda p: {
            'medium': 'sidebar',
            'high': 'card',
            'critical': 'modal'
        }[p.risk_level]
    },

    # Dissonance indicator
    'DissonanceIndicator': {
        'show_if': lambda p: p.current_dissonance.dissonance_score > 0.6,
        'prominence': 'card'
    },

    # Progress celebration
    'ProgressCelebration': {
        'show_if': lambda p: p.emotional_patterns.trajectory == 'improving',
        'hide_if': lambda p: p.emotional_patterns.trajectory == 'declining'
    },

    # What's working
    'WhatsWorking': {
        'show_if': lambda p: len(p.coping_profile.effective_strategies) > 0
    },

    # Gentle observations
    'GentleObservations': {
        'show_if': lambda p: (
            p.cultural_context.deflection_frequency > 0.3 or
            p.triggers.trigger_count > 0
        )
    },

    # Cultural greeting
    'CulturalGreeting': {
        'always': True,
        'language': lambda p: p.cultural_context.primary_language
    }
}
```

---

### 4. LayoutPrioritizer

**Purpose**: Order components by importance (risk-based)

**Priority System**:

```python
def prioritize_layout(patterns, visible_components):
    """
    Order components by urgency and importance
    """
    priorities = []

    # 1. CRITICAL RISK: Crisis resources at top
    if patterns.risk_level == 'critical':
        priorities.append(('CrisisResources', 100))
        priorities.append(('SafetyCheck', 95))

    # 2. HIGH RISK: Crisis + dissonance prominent
    elif patterns.risk_level == 'high':
        priorities.append(('CrisisResources', 90))
        priorities.append(('DissonanceIndicator', 85))

    # 3. MEDIUM RISK: Monitor + support
    elif patterns.risk_level == 'medium':
        priorities.append(('DissonanceIndicator', 75))
        priorities.append(('CrisisResources', 70))

    # 4. Always high priority: Voice input
    priorities.append(('VoiceRecorder', 80))

    # 5. Insights (medium priority)
    if 'GentleObservations' in visible_components:
        priorities.append(('GentleObservations', 60))

    if 'WhatsWorking' in visible_components:
        priorities.append(('WhatsWorking', 55))

    # 6. Progress (lower priority, but motivating)
    if 'ProgressCelebration' in visible_components:
        priorities.append(('ProgressCelebration', 50))

    # 7. Resources (lowest priority)
    priorities.append(('PersonalizedResources', 40))
    priorities.append(('Navigation', 30))

    # Sort by priority (descending)
    sorted_components = sorted(priorities, key=lambda x: x[1], reverse=True)

    return [comp for comp, _ in sorted_components if comp in visible_components]
```

**Example Output**:

```python
# Low risk user:
layout = ['VoiceRecorder', 'ProgressCelebration', 'WhatsWorking', 'Resources']

# Medium-high risk user:
layout = ['DissonanceIndicator', 'VoiceRecorder', 'CrisisResources',
          'GentleObservations', 'WhatsWorking']

# Critical risk user:
layout = ['CrisisResources', 'SafetyCheck', 'VoiceRecorder']
# Everything else hidden
```

---

### 5. ChangeDetector

**Purpose**: Track what changed from previous config and explain why

**Process**:
```python
def detect_changes(previous_config, new_config, patterns):
    """
    Identify all changes and generate explanations
    """
    changes = []

    # 1. Theme changed?
    if previous_config.theme != new_config.theme:
        changes.append({
            'type': 'theme_changed',
            'component': 'overall_theme',
            'reason': f"Your emotional state shifted from {previous_config.theme} "
                      f"to {new_config.theme} patterns. "
                      f"We adjusted colors to better support you."
        })

    # 2. Risk escalation?
    if new_config.risk_level > previous_config.risk_level:
        changes.append({
            'type': 'risk_escalation',
            'component': 'CrisisResources',
            'reason': f"We've noticed concerning patterns (risk: {new_config.risk_level}). "
                      f"Crisis resources are now more visible to ensure you have support."
        })

    # 3. Features added?
    new_components = set(new_config.visible_components) - set(previous_config.visible_components)
    for component in new_components:
        reason = get_component_add_reason(component, patterns)
        changes.append({
            'type': 'feature_added',
            'component': component,
            'reason': reason
        })

    # 4. Features hidden?
    hidden_components = set(previous_config.visible_components) - set(new_config.visible_components)
    for component in hidden_components:
        reason = get_component_hide_reason(component, patterns)
        changes.append({
            'type': 'feature_hidden',
            'component': component,
            'reason': reason
        })

    return changes
```

**Example Change Log**:
```json
[
    {
        "type": "risk_escalation",
        "component": "CrisisResources",
        "reason": "We've noticed your voice has been different the last 3 sessions—flatter, more pauses. We moved crisis resources up to ensure you have support if needed."
    },
    {
        "type": "feature_added",
        "component": "DissonanceIndicator",
        "reason": "You've said 'sawa' several times but your voice showed sadness. We added this to gently acknowledge the gap."
    },
    {
        "type": "feature_hidden",
        "component": "ProgressCelebration",
        "reason": "Your emotional trajectory shows you're going through a harder time. We'll bring back progress tracking when things stabilize."
    },
    {
        "type": "language_adapted",
        "component": "CulturalGreeting",
        "reason": "We noticed you've been code-switching to Swahili when emotional. We adapted your greeting to include more Swahili."
    }
]
```

---

## Build Pipeline

### Complete Overnight Process

```python
"""
Overnight Interface Builder Pipeline
"""

from typing import List, Dict
from datetime import datetime
import asyncio

class OvernightBuilder:
    """
    Orchestrates the overnight interface building process
    """

    def __init__(self, db_session, encryptor):
        self.db = db_session
        self.encryptor = encryptor

        # Initialize components
        self.theme_selector = ThemeSelector()
        self.visibility_engine = ComponentVisibilityEngine()
        self.layout_prioritizer = LayoutPrioritizer()
        self.change_detector = ChangeDetector()
        self.config_generator = UIConfigGenerator(
            self.theme_selector,
            self.visibility_engine,
            self.layout_prioritizer
        )

    async def run_nightly_build(self, target_timezone: str = None):
        """
        Main overnight build process

        Args:
            target_timezone: If specified, only build for users in this timezone
        """
        print(f"[{datetime.now()}] Starting overnight build...")

        # 1. Get users needing rebuild
        users = await self.get_users_for_build(target_timezone)
        print(f"Found {len(users)} users with recent activity")

        # 2. Build interfaces for all users (parallel)
        results = await asyncio.gather(*[
            self.build_interface_for_user(user)
            for user in users
        ])

        # 3. Summary
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful

        print(f"[{datetime.now()}] Build complete:")
        print(f"  ✓ Successful: {successful}")
        print(f"  ✗ Failed: {failed}")

        return {
            'total': len(users),
            'successful': successful,
            'failed': failed,
            'results': results
        }

    async def build_interface_for_user(self, user: Dict) -> Dict:
        """
        Build interface for one user

        Returns: Build result with status
        """
        user_id = user['user_id']
        anonymous_id = user['anonymous_id']

        try:
            # 1. Fetch current patterns
            patterns = await self.db.get_current_patterns(user_id)

            if not patterns or not patterns['pattern']:
                return {
                    'user_id': anonymous_id,
                    'success': False,
                    'reason': 'No patterns available'
                }

            # 2. Fetch previous config (for comparison)
            previous_config = patterns['config']

            # 3. Generate new UI config
            new_config = await self.config_generator.generate(
                patterns=patterns['pattern'],
                baseline=patterns['baseline'],
                previous_config=previous_config
            )

            # 4. Detect changes
            if previous_config:
                changes = await self.change_detector.detect(
                    previous_config,
                    new_config,
                    patterns['pattern']
                )
            else:
                changes = []

            # 5. Encrypt config
            encrypted_config = await self.encryptor.encrypt(
                new_config,
                user_id
            )

            # 6. Store to database
            await self.db.store_interface_config(
                user_id=user_id,
                pattern_id=patterns['pattern']['pattern_id'],
                config=encrypted_config,
                metadata={
                    'theme': new_config['theme'],
                    'primary_components': list(new_config['components'].keys()),
                    'crisis_prominence': new_config.get('crisis_prominence', 'hidden')
                }
            )

            # 7. Store changes (for transparency)
            await self.db.store_interface_changes(
                user_id=user_id,
                changes=changes
            )

            return {
                'user_id': anonymous_id,
                'success': True,
                'version': new_config['version'],
                'theme': new_config['theme'],
                'changes_count': len(changes)
            }

        except Exception as e:
            print(f"Error building interface for {anonymous_id}: {e}")
            return {
                'user_id': anonymous_id,
                'success': False,
                'reason': str(e)
            }

    async def get_users_for_build(self, timezone: str = None) -> List[Dict]:
        """
        Get users who need interface rebuild

        Args:
            timezone: Optional timezone filter

        Returns: List of user records
        """
        # Query users with activity in last 24 hours
        users = await self.db.query("""
            SELECT DISTINCT
                u.user_id,
                u.anonymous_id,
                u.timezone
            FROM users u
            INNER JOIN voice_sessions s ON u.user_id = s.user_id
            WHERE u.account_status = 'active'
              AND s.session_start > NOW() - INTERVAL '24 hours'
              AND s.patterns_extracted = TRUE
              AND (:timezone IS NULL OR u.timezone = :timezone)
        """, {'timezone': timezone})

        return users
```

---

## Implementation Continues...

This is the architecture. Next, I'll implement:
1. Complete UIConfigGenerator
2. ThemeSelector logic
3. ComponentVisibilityEngine
4. LayoutPrioritizer
5. ChangeDetector
6. NightlyScheduler (cron setup)

Ready to continue with implementations?
