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

## 📁 Project Structure

```
ResonaAI/
├── apps/                    # Application code (monorepo)
│   ├── backend/             # Python services
│   │   ├── core/            # Shared modules
│   │   ├── gateway/         # API Gateway
│   │   └── services/        # 15 microservices
│   └── frontend/            # React web app
├── tests/                   # Test suites
├── infra/                   # Infrastructure as Code
│   ├── docker/              # Docker configs
│   ├── kubernetes/          # K8s manifests
│   └── terraform/           # Cloud infrastructure
├── docs/                    # Documentation
├── project/                 # Project management
└── monitoring/              # Observability stack
```

See [docs/architecture/project-structure.md](docs/architecture/project-structure.md) for detailed project organization.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│              User Interface Layer                        │
│  Web App (PWA) │ Mobile App │ Counselor Dashboard       │
└─────────────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────────────┐
│              API Gateway Layer                          │
│  Auth │ Rate Limiting │ Load Balancing │ CORS          │
└─────────────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────────────┐
│              Microservices Layer (15 services)          │
│  Speech Processing │ Emotion Analysis │ Conversation   │
│  Crisis Detection  │ Safety Filters   │ Cultural Context│
└─────────────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────────────┐
│              Data Layer                                 │
│  PostgreSQL │ Redis │ Encrypted Storage │ S3/Blob      │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- Docker & Docker Compose

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

3. **Install dependencies**
   ```bash
   # Backend
   pip install -r requirements.txt
   
   # Frontend
   cd apps/frontend
   npm install
   ```

4. **Run with Docker Compose**
   ```bash
   cd infra/docker
   docker-compose up -d
   ```

### Development

```bash
# Run API Gateway
cd apps/backend/gateway
uvicorn main:app --reload --port 8000

# Run Frontend
cd apps/frontend
npm start

# Run Tests
pytest tests/ -v
```

### Using Makefile

```bash
make help          # Show all commands
make install       # Install all dependencies
make dev           # Start development servers
make test          # Run all tests
make docker-up     # Start Docker containers
```

## 📡 API Endpoints

### Emotion Detection
- `POST /detect-emotion/file` - Analyze emotion from audio file
- `POST /detect-emotion/batch` - Batch process multiple files
- `WebSocket /ws/emotion-stream` - Real-time streaming

### Speech Processing
- `POST /transcribe` - Speech-to-text with accent adaptation
- `POST /detect-language` - Automatic language detection

### Health
- `GET /health` - System health check

## 🔒 Security & Privacy

- **Encryption**: AES-256 at rest, TLS 1.3 in transit
- **Compliance**: Kenya Data Protection Act 2019
- **Data Sovereignty**: African region storage
- **Consent Management**: GDPR-style user rights

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Documentation Hub](docs/README.md) | Central documentation navigation |
| [Quick Start Guide](docs/development/getting-started.md) | Get started quickly |
| [System Architecture](docs/architecture/system-overview.md) | Architecture overview |
| [API Reference](docs/api/README.md) | Complete API docs |
| [Project Status](docs/project-status/current-status.md) | Current completion status |
| [Deployment Guide](docs/development/deployment-guide.md) | Deploy to production |

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=apps/backend --cov-report=html

# Run specific service tests
pytest tests/services/emotion-analysis/ -v
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🗺️ Roadmap

- [ ] Mobile app (React Native/Flutter)
- [ ] Self-hosted AI models
- [ ] Group therapy sessions
- [ ] Wearable device integration
- [ ] Advanced analytics dashboard

---

<div align="center">

**Built with ❤️ for East African communities**

[⭐ Star us on GitHub](https://github.com/leon-madara/ResonaAI) | [📖 Documentation](docs/README.md) | [🐛 Report Bug](https://github.com/leon-madara/ResonaAI/issues)

</div>
