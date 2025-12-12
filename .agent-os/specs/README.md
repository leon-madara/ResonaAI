# Feature Specifications

## Overview
This directory contains detailed specifications for features being developed in ResonaAI.

## Directory Structure

```
specs/
├── _template/              # Template for new specs
│   ├── spec.md             # Specification template
│   ├── tasks.md            # Task breakdown template
│   └── status.md           # Status tracking template
├── [feature-name]/         # One folder per feature
│   ├── spec.md             # Feature specification
│   ├── tasks.md            # Implementation tasks
│   ├── status.md           # Current status
│   └── assets/             # Diagrams, mockups, etc.
└── README.md               # This file
```

## Creating a New Spec

1. **Create directory**: `mkdir specs/[feature-name]`
2. **Copy templates**: `cp -r specs/_template/* specs/[feature-name]/`
3. **Fill in spec.md**: Requirements, acceptance criteria, design
4. **Create tasks.md**: Break down into implementable tasks
5. **Initialize status.md**: Set initial status

## Spec Lifecycle

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Draft   │───▶│  Review  │───▶│ Approved │───▶│ Complete │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                     │                │
                     ▼                ▼
                ┌──────────┐    ┌──────────┐
                │ Revision │    │  Active  │
                └──────────┘    └──────────┘
```

## Active Specs

| Feature | Status | Priority | Owner |
|---------|--------|----------|-------|
| Dissonance Detector | In Progress | P1 | TBD |
| Baseline Tracker | In Progress | P1 | TBD |
| Cultural Context | In Progress | P1 | TBD |
| Adaptive Interface | Planned | P2 | TBD |

## Completed Specs

| Feature | Completed | Documentation |
|---------|-----------|---------------|
| Emotion Analysis | 2024-10 | `docs/architecture/emotion-analysis.md` |
| Crisis Detection | 2024-11 | `docs/architecture/crisis-detection.md` |
| Voice Processing | 2024-10 | `docs/architecture/voice-processing.md` |

