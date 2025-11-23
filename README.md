# ResonaAI - Voice-First Mental Health Support Platform for East Africa

<div align="center">

**An AI-powered, culturally-sensitive mental health support platform designed for East African communities**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2+-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)

</div>

## 🌟 Overview

ResonaAI is a comprehensive voice-first mental health support platform specifically designed for East African communities. The platform provides empathetic AI-driven mental health support through voice interactions, with a strong emphasis on data privacy, cultural sensitivity, and accessibility in low-connectivity environments.

### Key Highlights

- 🎤 **Voice-First Interface**: Natural voice conversations with AI support
- 🌍 **Cultural Sensitivity**: Designed for East African cultural context with Swahili language support
- 🔒 **Privacy-First**: End-to-end encryption and compliance with Kenya DPA 2019
- 📱 **Offline-First**: Works without internet connectivity with local data storage
- 🚨 **Crisis Detection**: Multi-layer safety system with human escalation pathways
- 🏥 **Healthcare Compliant**: Adheres to digital health regulations and ethical AI frameworks

## ✨ Features

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

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│              User Interface Layer                        │
│  Web App (PWA) │ Mobile App │ Counselor Dashboard      │
└─────────────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────────────┐
│              API Gateway Layer                          │
│  Auth │ Rate Limiting │ Load Balancing │ CORS          │
└─────────────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────────────┐
│              Microservices Layer                        │
│  Speech Processing │ Emotion Analysis │ Conversation   │
│  Crisis Detection  │ Safety Filters   │ Cultural Context│
└─────────────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────────────┐
│              Data Layer                                 │
│  PostgreSQL │ Redis │ Encrypted Storage │ S3/Blob      │
└─────────────────────────────────────────────────────────┘
```

### Microservices

1. **API Gateway Service** - Authentication, rate limiting, request routing
2. **Speech Processing Service** - STT with East African accent adaptation
3. **Emotion Analysis Service** - Voice and text emotion detection
4. **Conversation Engine Service** - AI response generation with cultural context
5. **Crisis Detection Service** - Risk assessment and escalation
6. **Safety & Content Moderation** - Response validation and filtering
7. **Sync Service** - Offline data synchronization
8. **Cultural Context Service** - Cultural knowledge and bias mitigation

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/leon-madara/ResonaAI.git
   cd ResonaAI/ResonaAI
   ```

2. **Set up environment variables**
   ```bash
   cp config.env.example .env
   # Edit .env with your configuration
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install web app dependencies**
   ```bash
   cd web-app
   npm install
   cd ..
   ```

5. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

### Development Setup

1. **Run the API server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Run the web app**
   ```bash
   cd web-app
   npm start
   ```

3. **Access API documentation**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## 📡 API Endpoints

### Emotion Detection

- `POST /detect-emotion/file` - Analyze emotion from uploaded audio file
- `POST /detect-emotion/batch` - Batch process multiple audio files
- `POST /detect-emotion/stream` - Real-time emotion detection
- `WebSocket /ws/emotion-stream` - WebSocket streaming for live applications

### Speech Processing

- `POST /transcribe` - Convert speech to text with accent adaptation
- `POST /transcribe-stream` - Real-time speech-to-text
- `POST /detect-language` - Automatic language detection

### Health & Status

- `GET /health` - System health check

## 💻 Usage Examples

### Python Client

```python
import requests

# Analyze emotion from audio file
with open('audio.wav', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/detect-emotion/file',
        files={'file': f}
    )
    result = response.json()
    print(f"Emotion: {result['emotion']}")
    print(f"Confidence: {result['confidence']:.2f}")
```

### JavaScript/WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/emotion-stream');

ws.onmessage = function(event) {
    const result = JSON.parse(event.data);
    console.log(`Emotion: ${result.emotion}`);
    console.log(`Confidence: ${result.confidence}`);
};
```

## 🔒 Security & Privacy

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

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_emotion_detector.py
```

## 📚 Documentation

- [API Documentation](docs/API.md) - Complete API reference
- [Architecture Documentation](docs/ARCHITECTURE.md) - System architecture details
- [System Design](architecture/system-design.md) - Comprehensive system design
- [Compliance Documentation](docs/compliance/) - Data protection and compliance

## 🌍 Cultural Sensitivity

ResonaAI is designed with East African cultural context in mind:

- **Language Support**: English and Swahili with regional accents
- **Cultural Knowledge Base**: RAG-powered cultural context integration
- **Bias Detection**: Regular audits for algorithmic bias
- **Local Resources**: Integration with East African mental health resources
- **Cultural Advisory**: Feedback from cultural advisory board

## 🚨 Crisis Support

The platform includes comprehensive crisis detection and intervention:

- **Multi-layer Detection**: Keyword, sentiment, and LLM-based analysis
- **Risk Scoring**: Automated risk assessment and prioritization
- **Human Escalation**: Automatic routing to human counselors
- **Emergency Resources**: Integration with local emergency services
- **24/7 Monitoring**: Continuous safety monitoring and alerting

## 📊 Monitoring & Observability

- **Application Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing**: Distributed tracing with Jaeger
- **Alerting**: PagerDuty integration for critical alerts

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- Azure Cognitive Services for speech processing
- Hume AI for emotion detection
- The East African mental health community for guidance and feedback

## 📞 Contact & Support

For questions, support, or collaboration opportunities:

- **GitHub Issues**: [Open an issue](https://github.com/leon-madara/ResonaAI/issues)
- **Documentation**: See the [docs](docs/) directory

## 🗺️ Roadmap

- [ ] Mobile app (React Native/Flutter)
- [ ] Self-hosted AI models for reduced latency
- [ ] Multi-modal input (voice, text, images)
- [ ] Group therapy sessions
- [ ] Wearable device integration
- [ ] Advanced analytics dashboard

---

<div align="center">

**Built with ❤️ for East African communities**

[⭐ Star us on GitHub](https://github.com/leon-madara/ResonaAI) | [📖 Documentation](docs/) | [🐛 Report Bug](https://github.com/leon-madara/ResonaAI/issues)

</div>
