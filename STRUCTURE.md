# ResonaAI Project Structure

> **📍 This document has been moved to the centralized documentation hub**  
> **New Location**: [`docs/architecture/project-structure.md`](docs/architecture/project-structure.md)  
> **Please update your bookmarks and references**

This document provides a comprehensive overview of the project organization.

## 🏗️ Directory Overview

```
ResonaAI/
│
├── 📁 .cursor/                    # Cursor AI Configuration
│   └── rules/                     # AI assistant rules
│       ├── general.mdc            # Core coding principles
│       ├── backend.mdc            # Python/FastAPI rules
│       ├── frontend.mdc           # React/TypeScript rules
│       └── security.mdc           # Security requirements
│
├── 📁 .agent-os/                  # AI Orchestration Framework
│   ├── standards/                 # Development standards
│   │   ├── coding-standards.md
│   │   ├── testing-standards.md
│   │   └── security-standards.md
│   ├── product/                   # Product vision
│   │   ├── mission.md
│   │   ├── roadmap.md
│   │   └── decisions/             # ADRs
│   └── specs/                     # Feature specifications
│       └── _template/
│
├── 📁 apps/                       # Application Code
│   ├── backend/                   # Python services
│   │   ├── core/                  # Shared modules (6 files)
│   │   │   ├── audio_processor.py
│   │   │   ├── emotion_detector.py
│   │   │   ├── streaming_processor.py
│   │   │   ├── models.py
│   │   │   └── config.py
│   │   ├── gateway/               # API Gateway
│   │   │   ├── main.py
│   │   │   ├── middleware/        # (9 middleware modules)
│   │   │   ├── models/
│   │   │   └── alembic/           # DB migrations
│   │   └── services/              # 15 Microservices
│   │       ├── baseline-tracker/
│   │       ├── breach-notification/
│   │       ├── consent-management/
│   │       ├── conversation-engine/
│   │       ├── crisis-detection/
│   │       ├── cultural-context/
│   │       ├── data-management/
│   │       ├── dissonance-detector/
│   │       ├── emotion-analysis/
│   │       ├── encryption-service/
│   │       ├── pii-anonymization/
│   │       ├── safety-moderation/
│   │       ├── security-monitoring/
│   │       ├── speech-processing/
│   │       └── sync-service/
│   └── frontend/                  # React Web Application
│       ├── src/
│       │   ├── components/        # UI components
│       │   ├── contexts/          # React contexts (4)
│       │   ├── pages/             # Page components (9)
│       │   └── utils/             # Utilities
│       └── package.json
│
├── 📁 tests/                      # Testing
│   ├── integration/               # Integration tests
│   ├── services/                  # Service unit tests (11)
│   └── utils/                     # Test utilities
│
├── 📁 infra/                      # Infrastructure as Code
│   ├── docker/                    # Docker configs
│   │   └── docker-compose.yml
│   ├── kubernetes/                # K8s manifests
│   │   ├── base/                  # Base configs
│   │   ├── overlays/              # Environment overrides
│   │   └── helm/                  # Helm charts
│   ├── terraform/                 # Cloud infrastructure
│   │   ├── environments/
│   │   └── modules/
│   └── nginx/                     # Reverse proxy
│
├── 📁 docs/                       # Documentation
│   ├── architecture/              # Architecture docs (7)
│   ├── api/                       # API reference
│   ├── guides/                    # How-to guides (3)
│   ├── security/                  # Security docs
│   ├── compliance/                # Compliance docs (2)
│   └── runbooks/                  # Operations (6)
│
├── 📁 project/                    # Project Management
│   ├── plans/
│   │   ├── active/                # Active plans (7)
│   │   ├── archive/               # Completed phases (6)
│   │   └── templates/
│   ├── progress/
│   │   └── reports/               # Progress reports (13)
│   ├── backlog/                   # To-do items (7)
│   └── completed/                 # Completed features (7)
│
├── 📁 monitoring/                 # Observability
│   ├── prometheus/
│   ├── grafana/
│   └── alertmanager/
│
├── 📁 scripts/                    # Utility Scripts
├── 📁 examples/                   # Usage Examples
├── 📁 database/                   # DB Schemas
├── 📁 config/                     # Configurations
│
└── 📄 Root Files
    ├── README.md                  # Project overview
    ├── STRUCTURE.md               # This file
    ├── Makefile                   # Common commands
    ├── requirements.txt           # Python dependencies
    ├── pytest.ini                 # Test configuration
    └── main.py                    # Entry point
```

## 🎯 Key Principles

### 1. Separation of Concerns
| Directory | Purpose | Who Uses It |
|-----------|---------|-------------|
| `.cursor/` | AI assistant rules | Cursor AI |
| `.agent-os/` | Development standards | AI + Developers |
| `apps/` | Application code | Developers |
| `tests/` | Test code | QA + Developers |
| `infra/` | Deployment | DevOps |
| `docs/` | Documentation | Everyone |
| `project/` | Project management | PM + Team |

### 2. Monorepo for Applications
```
apps/
├── backend/     → All Python services
└── frontend/    → React application
```

### 3. Environment Separation
```
infra/kubernetes/overlays/
├── dev/         → Development
├── staging/     → Pre-production
└── prod/        → Production
```

## 📊 Statistics

| Category | Count |
|----------|-------|
| Microservices | 15 |
| Frontend Pages | 9 |
| React Contexts | 4 |
| API Middleware | 9 |
| DB Migrations | 6 |
| Test Folders | 11 |
| Documentation Files | 20+ |
| Runbooks | 6 |

## 🔗 Quick Navigation

### Development
- Code: `apps/backend/` and `apps/frontend/`
- Tests: `tests/`
- Config: `config/` and `.env` files

### Documentation
- Start here: `docs/guides/QUICK_START_GUIDE.md`
- Architecture: `docs/architecture/system-design.md`
- API: `docs/api/API.md`

### Operations
- Docker: `infra/docker/docker-compose.yml`
- K8s: `infra/kubernetes/`
- Runbooks: `docs/runbooks/`

### Project Status
- Active work: `project/plans/active/`
- Backlog: `project/backlog/`
- Reports: `project/progress/reports/`
