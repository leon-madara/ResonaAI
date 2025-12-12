# Agent OS - AI Orchestration Framework

This directory contains the AI orchestration framework for systematic, quality-driven development.

## Directory Structure

```
.agent-os/
├── standards/          # Development standards and quality gates
│   ├── coding-standards.md
│   ├── testing-standards.md
│   └── security-standards.md
├── product/            # Product vision and architecture
│   ├── mission.md
│   ├── roadmap.md
│   └── decisions/      # Architecture Decision Records (ADRs)
└── specs/              # Feature specifications
    └── [feature-name]/ # Each feature gets a folder
        ├── spec.md
        ├── tasks.md
        └── status.md
```

## Purpose

The Agent OS framework provides:

1. **Standards Layer** - Consistent coding, testing, and security practices
2. **Product Layer** - Mission alignment and architectural decisions
3. **Specs Layer** - Detailed feature specifications and task breakdowns

## Usage

### Creating a New Feature Spec
```bash
# Create spec directory
mkdir .agent-os/specs/[feature-name]

# Copy template
cp .agent-os/specs/_template/* .agent-os/specs/[feature-name]/
```

### Recording an Architecture Decision
```bash
# Create ADR
touch .agent-os/product/decisions/NNNN-decision-title.md
```

## Integration with Cursor

The Agent OS works alongside `.cursor/rules/` to provide:
- `.cursor/rules/` → Code formatting and syntax rules
- `.agent-os/standards/` → Development process and quality gates
- `.agent-os/specs/` → Feature requirements and acceptance criteria

