# Service-Specific API Documentation

**Detailed API documentation for each ResonaAI microservice**

---

## 🎯 Service API Overview

Each ResonaAI microservice provides specialized functionality through well-defined REST APIs. All services are accessed through the API Gateway with consistent authentication and error handling.

### Service Categories
- **Core Innovation**: Voice processing and analysis services
- **Privacy & Security**: Data protection and user management
- **Infrastructure**: System support and monitoring services

---

## 📡 Available Service APIs

### Core Innovation Services

#### [Speech Processing](speech-processing.md)
**Voice-to-text conversion with accent adaptation**
- `POST /transcribe` - Convert speech to text
- `POST /detect-language` - Identify spoken language
- `GET /health` - Service health check

#### [Emotion Analysis](emotion-analysis.md)
**Voice emotion detection and analysis**
- `POST /analyze` - Detect emotion from audio
- `POST /batch` - Batch emotion analysis
- `WebSocket /stream` - Real-time emotion streaming
- `GET /health` - Service health check

#### [Dissonance Detection](dissonance-detection.md)
**Voice-truth gap analysis (Core Innovation)**
- `POST /analyze` - Analyze voice-text dissonance
- `GET /health` - Service health check

#### [Baseline Tracker](baseline-tracker.md)
**Personal voice fingerprinting and deviation detection**
- `POST /update-baseline` - Update user baseline
- `POST /detect-deviation` - Compare to baseline
- `GET /baseline/{user_id}` - Retrieve baseline
- `GET /deviations/{user_id}` - Get deviation history

#### [Crisis Detection](crisis-detection.md)
**Mental health risk assessment and escalation**
- `POST /assess` - Assess crisis risk
- `POST /escalate` - Trigger escalation
- `GET /resources/{location}` - Get local resources

#### [Conversation Engine](conversation-engine.md)
**AI-powered therapeutic conversations**
- `POST /chat` - Generate AI response
- `POST /context` - Update conversation context

### Privacy & Security Services

#### [Consent Management](consent-management.md)
**GDPR-compliant consent tracking**
- `POST /consent` - Record user consent
- `GET /consent/{user_id}` - Get consent status
- `PUT /consent/{user_id}` - Update consent
- `DELETE /consent/{user_id}` - Withdraw consent

#### [Encryption Service](encryption-service.md)
**End-to-end encryption for sensitive data**
- `POST /encrypt` - Encrypt data
- `POST /decrypt` - Decrypt data
- `POST /generate-key` - Generate user key
- `POST /rotate-key` - Rotate encryption key

#### [Safety Moderation](safety-moderation.md)
**Content filtering and safety validation**
- `POST /moderate` - Check content safety
- `POST /validate` - Validate AI response
- `GET /policies` - Get moderation policies

### Infrastructure Services

#### [Sync Service](sync-service.md)
**Background job processing and data synchronization**
- `POST /sync` - Trigger data sync
- `GET /status/{job_id}` - Check sync status
- `POST /queue` - Add background job

### In Development

#### [Cultural Context](cultural-context.md) 🔄
**Swahili pattern detection and cultural analysis**
- `POST /analyze/deflections` - Detect cultural deflections
- `POST /analyze/code-switching` - Analyze language switching
- `GET /context` - Get cultural context
- **Status**: 5% complete, 2-3 weeks to completion

### Needs Verification

#### Breach Notification ❓
**Security incident handling**
- Status: Unknown - needs audit

#### PII Anonymization ❓
**Privacy protection service**
- Status: Unknown - needs audit

#### Security Monitoring ❓
**Threat detection and monitoring**
- Status: Unknown - needs audit

---

## 🔒 Common API Patterns

### Authentication
All service APIs require JWT authentication:
```bash
curl -X POST http://localhost:8000/api/service/endpoint \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### Error Responses
Consistent error format across all services:
```json
{
  "error": "Error description",
  "error_code": "SERVICE_ERROR_CODE",
  "status_code": 400,
  "timestamp": "2025-01-11T10:00:00Z",
  "request_id": "req_123456789"
}
```

### Health Checks
All services provide health check endpoints:
```bash
curl -X GET http://localhost:8000/api/service/health
```

Response format:
```json
{
  "status": "healthy",
  "service": "service-name",
  "version": "1.0.0",
  "timestamp": "2025-01-11T10:00:00Z",
  "dependencies": {
    "database": "healthy",
    "redis": "healthy"
  }
}
```

---

## 📊 Service Status Matrix

| Service | API Status | Endpoints | Documentation | Production Ready |
|---------|------------|-----------|---------------|------------------|
| **Speech Processing** | ✅ Complete | 3 | ✅ Complete | ✅ Yes |
| **Emotion Analysis** | ✅ Complete | 4 | ✅ Complete | ✅ Yes |
| **Dissonance Detection** | ✅ Complete | 2 | ✅ Complete | ✅ Yes |
| **Baseline Tracker** | ✅ Complete | 4 | ✅ Complete | ✅ Yes |
| **Crisis Detection** | ✅ Complete | 3 | ✅ Complete | ✅ Yes |
| **Conversation Engine** | ✅ Complete | 2 | ✅ Complete | ✅ Yes |
| **Consent Management** | ✅ Complete | 5 | ✅ Complete | ✅ Yes |
| **Encryption Service** | ✅ Complete | 4 | ✅ Complete | ✅ Yes |
| **Safety Moderation** | ✅ Complete | 3 | 🟡 Partial | 🟡 Tests needed |
| **Sync Service** | ✅ Complete | 3 | 🟡 Partial | 🟡 Tests needed |
| **Cultural Context** | 🔴 5% | 3 planned | 🔄 In progress | ❌ In development |

---

## 🚀 Quick Service Testing

### Test All Services Health
```bash
# Test all service health endpoints
services=("speech-processing" "emotion-analysis" "dissonance-detection" "baseline-tracker" "crisis-detection" "conversation-engine" "consent-management" "encryption-service" "safety-moderation" "sync-service")

for service in "${services[@]}"; do
  echo "Testing $service..."
  curl -s http://localhost:8000/api/$service/health | jq .
done
```

### Test Core Workflow
```bash
# 1. Authenticate
TOKEN=$(curl -s -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}' | jq -r .access_token)

# 2. Analyze emotion
curl -X POST http://localhost:8000/api/emotion/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test-audio.wav"

# 3. Transcribe speech
curl -X POST http://localhost:8000/api/speech/transcribe \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test-audio.wav"

# 4. Analyze dissonance
curl -X POST http://localhost:8000/api/dissonance/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"transcript":"I am fine","voice_emotion":{"emotion":"sad","confidence":0.85}}'
```

---

## 📖 Related Documentation

### API Integration
- [API Overview](../overview.md) - General API information
- [Authentication](../authentication.md) - Auth implementation
- [Examples](../examples.md) - Usage examples

### Technical Implementation
- [Architecture](../../architecture/microservices.md) - Service architecture
- [Development](../../development/setup-guide.md) - Development setup
- [Testing](../../development/testing-guide.md) - API testing

### Project Context
- [Project Status](../../project-status/current-status.md) - Current status
- [Frontend Integration](../../frontend/architecture.md) - UI integration

---

**Service API Team**: Backend Engineering, API Design, Technical Writing  
**Last Updated**: January 11, 2025  
**Next Review**: After Cultural Context Service completion