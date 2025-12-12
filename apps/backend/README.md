# Backend Services

All Python backend services for ResonaAI.

## 📁 Structure

```
backend/
├── core/                   # Shared Python modules
│   ├── __init__.py
│   ├── audio_processor.py  # Audio preprocessing
│   ├── config.py           # Configuration management
│   ├── emotion_detector.py # Emotion detection engine
│   ├── models.py           # Shared data models
│   └── streaming_processor.py # Real-time processing
│
├── gateway/                # API Gateway (entry point)
│   ├── main.py             # FastAPI application
│   ├── auth_service.py     # Authentication logic
│   ├── database.py         # Database connection
│   ├── config.py           # Gateway configuration
│   ├── middleware/         # Request middleware
│   │   ├── auth.py         # JWT authentication
│   │   ├── rate_limiter.py # Rate limiting
│   │   ├── rbac.py         # Role-based access
│   │   ├── mfa.py          # Multi-factor auth
│   │   └── ...
│   ├── models/             # Pydantic models
│   ├── alembic/            # Database migrations
│   └── utils/              # Utilities
│
└── services/               # Microservices (15 services)
    ├── baseline-tracker/
    ├── breach-notification/
    ├── consent-management/
    ├── conversation-engine/
    ├── crisis-detection/
    ├── cultural-context/
    ├── data-management/
    ├── dissonance-detector/
    ├── emotion-analysis/
    ├── encryption-service/
    ├── pii-anonymization/
    ├── safety-moderation/
    ├── security-monitoring/
    ├── speech-processing/
    └── sync-service/
```

## 🔄 Migration Notes

This directory consolidates:
- `src/` → `core/`
- `services/api-gateway/` → `gateway/`
- `services/*` → `services/*`

## 🚀 Running Services

### Run Gateway
```bash
cd gateway
uvicorn main:app --reload --port 8000
```

### Run Individual Service
```bash
cd services/emotion-analysis
uvicorn main:app --reload --port 8002
```

### Run All Services (Docker)
```bash
cd ../../infra/docker
docker-compose up
```

## 📊 Service Dependencies

```
┌──────────────────────────────────────────────────────┐
│                      Gateway                          │
│  (auth, routing, rate limiting, security headers)    │
└───────────────────────┬──────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ Speech        │ │ Conversation  │ │ Crisis        │
│ Processing    │ │ Engine        │ │ Detection     │
└───────┬───────┘ └───────┬───────┘ └───────────────┘
        │                 │
        ▼                 ▼
┌───────────────┐ ┌───────────────┐
│ Emotion       │ │ Cultural      │
│ Analysis      │ │ Context       │
└───────────────┘ └───────────────┘
```

## 🔧 Shared Core Modules

### `core/audio_processor.py`
- Audio preprocessing pipeline
- Noise reduction, normalization
- Feature extraction (MFCC, spectral)

### `core/emotion_detector.py`
- Wav2Vec2 model integration
- 7-emotion classification
- Confidence scoring

### `core/streaming_processor.py`
- Real-time audio processing
- WebSocket support
- Voice activity detection

## 🧪 Testing

```bash
# Run all backend tests
pytest tests/backend/ -v

# Run specific service tests
pytest tests/backend/services/emotion-analysis/ -v

# Run with coverage
pytest tests/backend/ --cov=apps/backend --cov-report=html
```
