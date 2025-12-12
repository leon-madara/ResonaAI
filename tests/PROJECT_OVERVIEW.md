# ResonaAI Project Overview

**Last Updated**: December 12, 2025

## Project Description

ResonaAI is a comprehensive voice-first mental health support platform specifically designed for East African communities. The platform provides empathetic AI-driven mental health support through voice interactions, with a strong emphasis on data privacy, cultural sensitivity, and accessibility in low-connectivity environments.

## Key Features

### Core Capabilities

- **Real-time Emotion Detection**: Analyze emotional states from voice input in real-time
- **Speech-to-Text Processing**: Convert voice to text with accent adaptation for East African English and Swahili
- **AI Conversation Engine**: GPT-4 powered empathetic responses with cultural context awareness
- **Crisis Detection & Safety**: Multi-layer risk assessment with automatic human escalation
- **Offline Functionality**: Complete offline support with encrypted local storage and sync
- **Multi-language Support**: English and Swahili with regional accent adaptation

### Technical Features

- **Microservices Architecture**: Scalable, containerized services
- **REST & WebSocket APIs**: Real-time streaming and batch processing
- **Progressive Web App**: Installable PWA with offline capabilities
- **Docker Deployment**: Complete containerization with Docker Compose
- **Comprehensive Testing**: Unit, integration, and performance tests
- **Monitoring & Observability**: Prometheus, Grafana, and ELK stack integration

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                     │
├─────────────────────────────────────────────────────────────────┤
│  Web App (PWA)  │  Mobile App  │  Counselor Dashboard  │  Admin │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway Layer                       │
├─────────────────────────────────────────────────────────────────┤
│  Authentication  │  Rate Limiting  │  Load Balancing  │  CORS  │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                      Microservices Layer                       │
├─────────────────────────────────────────────────────────────────┤
│ Speech Processing │ Emotion Analysis │ Conversation Engine │ Sync │
│ Crisis Detection  │ Safety Filters   │ Cultural Context   │      │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                        Data Layer                              │
├─────────────────────────────────────────────────────────────────┤
│ PostgreSQL │ Redis Cache │ S3/Blob Storage │ Encrypted Storage │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                           │
├─────────────────────────────────────────────────────────────────┤
│ OpenAI GPT-4 │ Azure Cognitive │ Hume AI │ Twilio │ Monitoring │
└─────────────────────────────────────────────────────────────────┘
```

## Microservices

### 1. API Gateway Service
**Purpose**: Central entry point for all client requests  
**Responsibilities**:
- Authentication and authorization
- Rate limiting and DDoS protection
- Request routing to appropriate services
- CORS handling and security headers
- Request/response logging

**Technology Stack**:
- FastAPI with middleware
- JWT authentication
- Redis for rate limiting
- Nginx for load balancing

### 2. Speech Processing Service
**Purpose**: Convert voice input to text with accent adaptation  
**Responsibilities**:
- Audio preprocessing (noise reduction, normalization)
- Speech-to-text conversion (Whisper, Azure)
- Language detection and switching
- Audio quality assessment
- Accent adaptation for East African English

**Technology Stack**:
- Python with FastAPI
- OpenAI Whisper API
- Azure Speech Services
- Librosa for audio processing
- Redis for caching

### 3. Emotion Analysis Service
**Purpose**: Detect emotional state from voice and text  
**Responsibilities**:
- Voice emotion detection (Hume AI, Azure)
- Text sentiment analysis
- Ensemble emotion classification
- Emotion confidence scoring
- Emotional state tracking over time

**Technology Stack**:
- Python with FastAPI
- Hume AI API
- Azure Cognitive Services
- Scikit-learn for ensemble methods
- PostgreSQL for emotion history

### 4. Conversation Engine Service
**Purpose**: Generate empathetic, culturally-aware responses  
**Responsibilities**:
- GPT-4 integration with therapeutic prompts
- Emotion-conditioned response generation
- Cultural context injection
- Conversation context management
- Crisis detection and escalation

**Technology Stack**:
- Python with FastAPI
- OpenAI GPT-4 API
- Vector database for cultural context
- Redis for conversation caching
- PostgreSQL for session management

### 5. Crisis Detection Service
**Purpose**: Identify high-risk situations requiring intervention  
**Responsibilities**:
- Multi-layer crisis detection (keywords, sentiment, LLM)
- Risk assessment and scoring
- Escalation workflow management
- Emergency resource coordination
- Alert generation and routing

**Technology Stack**:
- Python with FastAPI
- Pattern matching algorithms
- Machine learning classifiers
- PostgreSQL for crisis logs
- Real-time alerting system

### 6. Safety & Content Moderation Service
**Purpose**: Ensure AI responses are safe and appropriate  
**Responsibilities**:
- Response validation and filtering
- Content moderation and blocklists
- Hallucination detection
- Human review queue management
- User feedback processing

**Technology Stack**:
- Python with FastAPI
- Content filtering algorithms
- PostgreSQL for moderation logs
- Queue system for human review
- Analytics for safety metrics

### 7. Sync Service
**Purpose**: Handle offline data synchronization  
**Responsibilities**:
- Background data processing
- Conflict resolution for deferred operations
- Sync queue management
- Data integrity validation
- User notification for sync status

**Technology Stack**:
- Python with FastAPI
- Background job processing (Celery)
- PostgreSQL for sync queues
- Redis for job coordination
- WebSocket for real-time updates

### 8. Cultural Context Service
**Purpose**: Provide culturally relevant information and responses  
**Responsibilities**:
- Cultural knowledge base management
- Retrieval-augmented generation (RAG)
- Bias detection and mitigation
- Local resource integration
- Cultural advisory board feedback

**Technology Stack**:
- Python with FastAPI
- Vector database (Pinecone/Weaviate)
- Embedding models for semantic search
- PostgreSQL for cultural data
- Analytics for bias monitoring

### 9. Encryption Service
**Purpose**: Provide encryption and key management  
**Responsibilities**:
- Data encryption/decryption
- Key rotation and management
- User-specific key generation
- End-to-end encryption
- Secure key storage

**Technology Stack**:
- Python with FastAPI
- Cryptography library (AES-256)
- Fernet for symmetric encryption
- Secure key management

### 10. Dissonance Detector Service
**Purpose**: Detect emotional dissonance between voice and text  
**Responsibilities**:
- Dissonance analysis (voice vs text emotion)
- Defensive concealment detection
- Authenticity scoring
- Dissonance tracking over time

**Technology Stack**:
- Python with FastAPI
- Sentiment analysis
- Emotion detection integration
- Machine learning models

### 11. Baseline Tracker Service
**Purpose**: Track user baseline emotional and voice patterns  
**Responsibilities**:
- Baseline calculation and storage
- Deviation detection from baseline
- Voice fingerprint creation
- Emotion baseline tracking

**Technology Stack**:
- Python with FastAPI
- Statistical analysis
- Pattern recognition
- PostgreSQL for baseline storage

### 12. Consent Management Service
**Purpose**: Manage user consent and privacy preferences  
**Responsibilities**:
- Consent creation and tracking
- Consent revocation
- Consent versioning
- Privacy preference management

**Technology Stack**:
- Python with FastAPI
- PostgreSQL for consent storage
- Consent tracking and auditing

## Core Principles

### 1. Offline-First Design
- All user interactions work without internet connectivity
- Local data storage with encrypted synchronization
- Deferred processing when connectivity is restored
- Progressive enhancement for online features

### 2. Data Sovereignty
- Primary data storage in Kenya/South Africa regions
- Minimal cross-border data transfers
- PII anonymization before external API calls
- End-to-end encryption for sensitive data

### 3. Cultural Sensitivity
- East African cultural context integration
- Swahili language support
- Local mental health resource awareness
- Bias detection and mitigation

### 4. Safety-First Approach
- Multi-layer crisis detection
- Human escalation pathways
- Response validation and filtering
- Continuous safety monitoring

## Security & Privacy

### Data Protection
- **Encryption**: AES-256 encryption for data at rest, TLS 1.3 for data in transit
- **Compliance**: Full compliance with Kenya Data Protection Act 2019
- **Data Sovereignty**: Primary data storage in Kenya/South Africa regions
- **Anonymization**: PII removal before external API calls
- **Consent Management**: Granular consent tracking and user rights

### Security Features
- JWT authentication with short expiration times
- Multi-factor authentication for counselors and admins
- Role-based access control (RBAC)
- End-to-end encryption for sensitive conversations
- Secure key management with AWS KMS/Azure Key Vault

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+
- **Message Queue**: Celery with Redis
- **Authentication**: JWT tokens
- **API Documentation**: OpenAPI/Swagger

### Frontend
- **Framework**: React 18.2+
- **Language**: TypeScript
- **State Management**: Context API, Zustand
- **Styling**: CSS Modules, Tailwind CSS
- **PWA**: Service Workers, IndexedDB

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **Orchestration**: Kubernetes (planned)
- **Monitoring**: Prometheus, Grafana
- **Logging**: ELK Stack
- **CI/CD**: GitHub Actions (planned)

### External Services
- **AI**: OpenAI GPT-4
- **Speech**: Azure Cognitive Services, OpenAI Whisper
- **Emotion**: Hume AI, Azure Cognitive Services
- **Communication**: Twilio (planned)

## Project Structure

```
ResonaAI/
├── architecture/              # Architecture documentation
│   └── system-design.md     # System design document
├── services/                 # Microservices
│   ├── api-gateway/         # API Gateway service
│   ├── speech-processing/   # Speech processing service
│   ├── emotion-analysis/    # Emotion analysis service
│   ├── conversation-engine/ # Conversation engine service
│   ├── crisis-detection/   # Crisis detection service
│   ├── encryption-service/  # Encryption service
│   ├── dissonance-detector/ # Dissonance detector service
│   ├── baseline-tracker/   # Baseline tracker service
│   ├── consent-management/  # Consent management service
│   └── ...                  # Other services
├── web-app/                 # Frontend React application
├── tests/                   # Test suites
│   ├── services/            # Service-specific tests
│   ├── integration/         # Integration tests
│   └── ...                  # Other tests
├── docs/                    # Documentation
├── infrastructure/          # Infrastructure as code
│   ├── terraform/           # Terraform configurations
│   ├── kubernetes/          # Kubernetes manifests
│   └── helm/                # Helm charts
└── monitoring/              # Monitoring configurations
```

## Testing Overview

### Test Coverage
- **Unit Tests**: 63+ test cases
- **Integration Tests**: 3 test suites
- **Service Tests**: 17+ test files
- **Test Status**: Comprehensive coverage for all microservices

### Test Execution
- Tests run individually per service (recommended)
- Module caching conflicts when running all together
- All tests pass when run individually

See [README.md](README.md) for detailed testing documentation.

## Compliance & Legal

### Data Protection Compliance
- **Kenya DPA 2019**: Full compliance with data protection requirements
- **Uganda DPPA 2019**: Compliance with privacy regulations
- **GDPR**: Alignment with international standards
- **Data Residency**: Primary storage in African regions

### Healthcare Regulations
- **Kenya Digital Health Act**: Compliance with digital health requirements
- **Medical Device Regulations**: Appropriate disclaimers and limitations
- **Professional Standards**: Counselor licensing and verification
- **Crisis Intervention**: Legal framework for emergency responses

### Ethical AI Framework
- **Bias Detection**: Regular audits for algorithmic bias
- **Transparency**: Clear AI disclosure to users
- **Human Oversight**: Human-in-the-loop for critical decisions
- **Continuous Monitoring**: Ongoing safety and effectiveness assessment

## Deployment

### Cloud Infrastructure
- **Primary Region**: Kenya (Nairobi) or South Africa (Cape Town)
- **Secondary Region**: South Africa for disaster recovery
- **CDN**: CloudFlare for global content delivery
- **Load Balancing**: Application Load Balancer with health checks

### Container Orchestration
- **Kubernetes**: For container management
- **Docker**: For containerization
- **Helm**: For deployment management
- **Istio**: For service mesh (optional)

## Monitoring & Observability

- **Application Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing**: Jaeger for distributed tracing
- **Alerting**: PagerDuty for critical alerts

## Roadmap

### Short-term
- [ ] Fix batch encryption endpoints
- [ ] Resolve module caching conflicts
- [ ] Add end-to-end tests
- [ ] Set up CI/CD pipeline

### Medium-term
- [ ] Mobile app (React Native/Flutter)
- [ ] Self-hosted AI models
- [ ] Performance testing
- [ ] Security audit

### Long-term
- [ ] Multi-modal input (voice, text, images)
- [ ] Group therapy sessions
- [ ] Wearable device integration
- [ ] Advanced analytics dashboard

## Related Documentation

- [System Design](../../architecture/system-design.md) - Comprehensive system architecture
- [API Documentation](../../docs/API.md) - Complete API reference
- [Architecture Documentation](../../docs/ARCHITECTURE.md) - System architecture details
- [Testing Documentation](README.md) - Testing infrastructure and test suites
- [Compliance Documentation](../../docs/compliance/) - Data protection and compliance

## Contact & Support

For questions, support, or collaboration opportunities:
- **GitHub Issues**: Open an issue on GitHub
- **Documentation**: See the [docs](../../docs/) directory

---

**Last Updated**: December 12, 2025  
**Project Status**: Active Development  
**Version**: 1.0.0

