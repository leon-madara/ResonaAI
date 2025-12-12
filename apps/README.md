# Applications

All application code for ResonaAI, organized as a monorepo.

## 📁 Structure

```
apps/
├── backend/                    # All Python backend services
│   ├── core/                   # Shared modules (6 files)
│   │   ├── __init__.py
│   │   ├── audio_processor.py
│   │   ├── config.py
│   │   ├── emotion_detector.py
│   │   ├── models.py
│   │   └── streaming_processor.py
│   ├── gateway/                # API Gateway service
│   │   ├── main.py
│   │   ├── middleware/         # Auth, rate limiting, RBAC, etc.
│   │   ├── models/
│   │   ├── alembic/            # Database migrations
│   │   └── utils/
│   └── services/               # 15 microservices
│       ├── baseline-tracker/
│       ├── breach-notification/
│       ├── consent-management/
│       ├── conversation-engine/
│       ├── crisis-detection/
│       ├── cultural-context/
│       ├── data-management/
│       ├── dissonance-detector/
│       ├── emotion-analysis/
│       ├── encryption-service/
│       ├── pii-anonymization/
│       ├── safety-moderation/
│       ├── security-monitoring/
│       ├── speech-processing/
│       └── sync-service/
│
└── frontend/                   # React web application
    ├── public/
    ├── src/
    │   ├── components/         # UI components
    │   ├── contexts/           # React contexts
    │   ├── pages/              # Page components
    │   ├── utils/              # Utilities
    │   └── __tests__/          # Frontend tests
    └── package.json
```

## 🔄 Migration Notes

This structure consolidates code from:
- `src/` → `apps/backend/core/`
- `services/api-gateway/` → `apps/backend/gateway/`
- `services/*` → `apps/backend/services/*`
- `web-app/` → `apps/frontend/`

## 🚀 Getting Started

### Backend
```bash
cd apps/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r gateway/requirements.txt

# Run gateway
cd gateway
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd apps/frontend
npm install
npm start
```

## 🏗️ Service Architecture

```
┌─────────────────────────────────────────────────┐
│                  API Gateway                     │
│            (Authentication, Routing)             │
└─────────────┬───────────────────────┬───────────┘
              │                       │
    ┌─────────▼─────────┐   ┌────────▼────────┐
    │ Conversation      │   │ Speech          │
    │ Engine            │   │ Processing      │
    └─────────┬─────────┘   └────────┬────────┘
              │                       │
    ┌─────────▼─────────┐   ┌────────▼────────┐
    │ Emotion           │   │ Crisis          │
    │ Analysis          │   │ Detection       │
    └───────────────────┘   └─────────────────┘
```

## 📊 Service Summary

| Service | Description | Port |
|---------|-------------|------|
| gateway | API entry point, auth, routing | 8000 |
| speech-processing | Voice-to-text, audio analysis | 8001 |
| emotion-analysis | Emotion detection from voice | 8002 |
| conversation-engine | GPT-4 therapeutic responses | 8003 |
| crisis-detection | Risk assessment, escalation | 8004 |
| cultural-context | Cultural adaptation, Swahili | 8005 |
| baseline-tracker | User emotional baselines | 8006 |
| dissonance-detector | Voice-text mismatch analysis | 8007 |
| consent-management | GDPR, consent tracking | 8008 |
| encryption-service | Data encryption, key management | 8009 |
| data-management | Data lifecycle, retention | 8010 |
| pii-anonymization | PII detection and masking | 8011 |
| safety-moderation | Content filtering, safety | 8012 |
| security-monitoring | Security events, alerts | 8013 |
| sync-service | Offline data sync | 8014 |
| breach-notification | Breach alerts, notifications | 8015 |
