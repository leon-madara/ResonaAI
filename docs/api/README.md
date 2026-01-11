# API Documentation

**Complete API reference for ResonaAI services**

---

## 📡 API Overview

ResonaAI provides a comprehensive REST API through an **API Gateway** that routes requests to 15 specialized microservices. The API is designed for voice-first mental health applications with strong privacy and cultural sensitivity features.

### API Principles
- **RESTful Design**: Standard HTTP methods and status codes
- **Authentication Required**: JWT tokens for all protected endpoints
- **Privacy-First**: Encrypted data transmission and storage
- **Cultural Awareness**: Multi-language support (English/Swahili)
- **Rate Limited**: Protection against abuse and overuse

---

## 📚 API Documentation

### [API Overview](overview.md)
**Introduction to the ResonaAI API**
- Authentication and authorization
- Request/response formats
- Error handling and status codes
- Rate limiting and quotas
- API versioning strategy

### [Authentication](authentication.md)
**Authentication and user management endpoints**
- User registration and login
- JWT token management
- Password reset and recovery
- Account management
- Session handling

### [Services](services/)
**Service-specific API documentation**
- [Speech Processing](services/speech-processing.md) - Voice-to-text conversion
- [Emotion Analysis](services/emotion-analysis.md) - Voice emotion detection
- [Dissonance Detection](services/dissonance-detection.md) - Voice-truth gap analysis
- [Crisis Detection](services/crisis-detection.md) - Risk assessment
- [Cultural Context](services/cultural-context.md) - Cultural pattern analysis
- [Conversation Engine](services/conversation-engine.md) - AI responses

### [Examples](examples.md)
**Complete usage examples and code samples**
- Authentication flow examples
- Voice processing workflows
- Error handling patterns
- Integration examples
- SDK usage (when available)

---

## 🚀 Quick Start

### Base URL
```
Production: https://api.resonaai.com
Development: http://localhost:8000
```

### Authentication
```bash
# Register new user
curl -X POST http://localhost:8000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "consent_version": "1.0"
  }'

# Login and get token
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'

# Use token in requests
curl -X GET http://localhost:8000/api/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Voice Processing Workflow
```bash
# 1. Upload audio for emotion analysis
curl -X POST http://localhost:8000/api/emotion/analyze \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@audio.wav"

# 2. Transcribe speech to text
curl -X POST http://localhost:8000/api/speech/transcribe \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@audio.wav"

# 3. Analyze voice-truth dissonance
curl -X POST http://localhost:8000/api/dissonance/analyze \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "I am fine",
    "voice_emotion": {
      "emotion": "sad",
      "confidence": 0.85
    }
  }'
```

---

## 🎯 Core API Endpoints

### Authentication Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/register` | Register new user |
| `POST` | `/api/login` | User login |
| `POST` | `/api/logout` | User logout |
| `GET` | `/api/profile` | Get user profile |
| `PUT` | `/api/profile` | Update user profile |

### Voice Processing Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/speech/transcribe` | Speech-to-text conversion |
| `POST` | `/api/emotion/analyze` | Voice emotion detection |
| `POST` | `/api/dissonance/analyze` | Voice-truth gap analysis |
| `POST` | `/api/baseline/update` | Update user baseline |
| `GET` | `/api/baseline/{user_id}` | Get user baseline |

### Mental Health Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/crisis/assess` | Crisis risk assessment |
| `POST` | `/api/conversation/chat` | AI conversation |
| `GET` | `/api/cultural/context` | Cultural context analysis |
| `POST` | `/api/safety/moderate` | Content safety check |

### System Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | System health check |
| `GET` | `/api/status` | Service status |
| `GET` | `/api/version` | API version info |

---

## 📊 API Status by Service

### Production Ready (9 services)
| Service | Status | Endpoints | Documentation |
|---------|--------|-----------|---------------|
| **Speech Processing** | ✅ Complete | 3 endpoints | ✅ Complete |
| **Emotion Analysis** | ✅ Complete | 4 endpoints | ✅ Complete |
| **Dissonance Detection** | ✅ Complete | 2 endpoints | ✅ Complete |
| **Crisis Detection** | ✅ Complete | 3 endpoints | ✅ Complete |
| **Baseline Tracker** | ✅ Complete | 4 endpoints | ✅ Complete |
| **Conversation Engine** | ✅ Complete | 2 endpoints | ✅ Complete |
| **Consent Management** | ✅ Complete | 5 endpoints | ✅ Complete |
| **Encryption Service** | ✅ Complete | 4 endpoints | ✅ Complete |
| **Safety Moderation** | ✅ Complete | 3 endpoints | 🟡 Partial |

### In Development (1 service)
| Service | Status | Expected | Documentation |
|---------|--------|----------|---------------|
| **Cultural Context** | 🔴 5% complete | 2-3 weeks | 🔄 In progress |

### Needs Verification (3 services)
| Service | Status | Action Needed |
|---------|--------|---------------|
| **Breach Notification** | ❓ Unknown | Audit implementation |
| **PII Anonymization** | ❓ Unknown | Audit implementation |
| **Security Monitoring** | ❓ Unknown | Audit implementation |

---

## 🔒 Security & Privacy

### Authentication
- **JWT Tokens**: Secure token-based authentication
- **Token Expiration**: 24-hour token lifetime
- **Refresh Tokens**: Automatic token renewal
- **Rate Limiting**: Protection against brute force
- **HTTPS Only**: Encrypted communication in production

### Data Privacy
- **End-to-End Encryption**: AES-256 for sensitive data
- **No Audio Storage**: Audio processed in-memory only
- **Data Minimization**: Collect only necessary data
- **User Consent**: GDPR-compliant consent management
- **Data Sovereignty**: African region data storage

### API Security
- **Input Validation**: All inputs validated and sanitized
- **SQL Injection Protection**: Parameterized queries
- **XSS Protection**: Output encoding and CSP headers
- **CORS Configuration**: Proper cross-origin policies
- **Security Headers**: Comprehensive security headers

---

## 📈 API Performance

### Response Time Targets
- **Authentication**: <200ms
- **Voice Processing**: <2s for 30s audio
- **Text Analysis**: <500ms
- **Database Queries**: <100ms
- **Health Checks**: <50ms

### Rate Limits
- **Authentication**: 10 requests/minute per IP
- **Voice Processing**: 60 requests/hour per user
- **Text Analysis**: 100 requests/hour per user
- **General API**: 1000 requests/hour per user

### Availability Targets
- **Uptime**: 99.9% availability target
- **Error Rate**: <0.1% error rate
- **Response Time**: 95th percentile under targets
- **Throughput**: 100+ requests/second per service

---

## 🔄 API Versioning

### Current Version
- **Version**: v1.0
- **Release Date**: January 2025
- **Stability**: Production ready (core services)

### Versioning Strategy
- **Semantic Versioning**: Major.Minor.Patch
- **Backward Compatibility**: Maintained for 1 year
- **Deprecation Notice**: 6 months advance notice
- **Migration Guides**: Provided for breaking changes

### Version History
- **v1.0**: Initial production release
- **v0.9**: Beta release with core services
- **v0.8**: Alpha release with basic functionality

---

## 🛠️ Development Tools

### API Testing
- **Postman Collection**: Complete API collection available
- **OpenAPI Spec**: Machine-readable API specification
- **Swagger UI**: Interactive API documentation
- **Test Suite**: Comprehensive API tests

### SDKs and Libraries
- **Python SDK**: Official Python client library
- **JavaScript SDK**: Official JS/TS client library
- **React Hooks**: Custom hooks for React integration
- **CLI Tool**: Command-line interface for testing

### Monitoring and Analytics
- **API Metrics**: Request/response metrics
- **Error Tracking**: Detailed error logging
- **Performance Monitoring**: Response time tracking
- **Usage Analytics**: API usage patterns

---

## 📖 Related Documentation

### Technical Implementation
- [Architecture Overview](../architecture/system-overview.md)
- [Microservices Architecture](../architecture/microservices.md)
- [Security Architecture](../architecture/security-architecture.md)
- [Database Schema](../architecture/database-schema.md)

### Development Resources
- [Development Setup](../development/setup-guide.md)
- [Testing Guide](../development/testing-guide.md)
- [Deployment Guide](../development/deployment-guide.md)
- [Troubleshooting](../development/troubleshooting.md)

### Project Context
- [Project Status](../project-status/current-status.md)
- [Frontend Integration](../frontend/architecture.md)
- [Design System](../frontend/design-system.md)

---

**API Team**: Backend Engineering, DevOps, Technical Writing  
**Last Updated**: January 11, 2025  
**Next Review**: After Cultural Context Service completion