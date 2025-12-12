# ResonaAI Voice Emotion Detection - Architecture Documentation

## System Overview

ResonaAI is a comprehensive voice emotion detection pipeline that analyzes audio input to identify emotional states in real-time and batch processing modes. The system combines traditional audio processing techniques with modern deep learning approaches for robust emotion recognition.

## Architecture Components

### 1. API Layer (FastAPI)

**Location:** `main.py`

The API layer provides RESTful endpoints and WebSocket connections for emotion detection services.

**Key Features:**
- REST API endpoints for file upload, batch processing, and streaming
- WebSocket support for real-time emotion detection
- Automatic API documentation (OpenAPI/Swagger)
- CORS support for web applications
- Error handling and logging

**Endpoints:**
- `GET /health` - Health check
- `POST /detect-emotion/file` - File upload analysis
- `POST /detect-emotion/batch` - Batch processing
- `POST /detect-emotion/stream` - Streaming analysis
- `WebSocket /ws/emotion-stream` - Real-time streaming

### 2. Audio Processing Layer

**Location:** `src/audio_processor.py`

Handles audio preprocessing and feature extraction from raw audio data.

**Key Features:**
- Audio normalization and noise reduction
- Silence trimming and padding
- Comprehensive feature extraction:
  - MFCC (Mel-Frequency Cepstral Coefficients)
  - Spectral features (centroid, rolloff, bandwidth)
  - Prosodic features (pitch, energy, voiced ratio)
  - Temporal features (duration, speech rate)
  - Statistical features (mean, std, percentiles)

**Processing Pipeline:**
1. Load audio from bytes/array
2. Apply noise reduction (spectral gating)
3. Normalize audio amplitude
4. Trim silence from beginning/end
5. Pad to minimum length if needed
6. Extract comprehensive feature set

### 3. Emotion Detection Engine

**Location:** `src/emotion_detector.py`

Core emotion detection using ensemble of traditional and deep learning approaches.

**Key Features:**
- Wav2Vec2 transformer model for deep audio features
- Traditional audio feature classification
- Ensemble approach combining multiple feature types
- Confidence scoring and thresholding
- Support for 7 emotion categories

**Model Architecture:**
- **Feature Extraction:** Wav2Vec2 + Traditional features
- **Classification:** Random Forest ensemble
- **Post-processing:** Confidence thresholding
- **Output:** Emotion label + confidence score

**Emotion Categories:**
- Neutral, Happy, Sad, Angry, Fear, Surprise, Disgust

### 4. Streaming Processor

**Location:** `src/streaming_processor.py`

Real-time audio processing for live emotion detection applications.

**Key Features:**
- Audio buffering and chunk processing
- Voice Activity Detection (VAD)
- Real-time feature extraction
- Streaming emotion detection
- WebSocket integration

**Processing Flow:**
1. Receive audio chunks via WebSocket
2. Buffer audio data
3. Apply VAD to detect speech
4. Extract features from buffered audio
5. Detect emotion and return result
6. Maintain processing state

### 5. Configuration Management

**Location:** `src/config.py`

Centralized configuration management using Pydantic settings.

**Configuration Areas:**
- API settings (host, port, debug)
- Audio processing parameters
- Model configuration
- Feature extraction settings
- Confidence thresholds
- File upload limits

### 6. Data Models

**Location:** `src/models.py`

Pydantic models for request/response validation and data structures.

**Key Models:**
- `EmotionResult` - Single emotion detection result
- `BatchEmotionResult` - Batch processing results
- `AudioFeatures` - Extracted audio features
- `EmotionPrediction` - Model prediction with probabilities
- `StreamingConfig` - Streaming processing configuration

## Data Flow

### File Processing Flow

```
Audio File → AudioProcessor → Feature Extraction → EmotionDetector → EmotionResult
```

1. **Input:** Audio file (WAV, MP3, FLAC, M4A)
2. **Preprocessing:** Noise reduction, normalization, silence trimming
3. **Feature Extraction:** MFCC, spectral, prosodic, temporal, statistical features
4. **Emotion Detection:** Ensemble classification with confidence scoring
5. **Output:** Emotion label, confidence score, processing metadata

### Streaming Processing Flow

```
Audio Chunks → StreamingProcessor → Audio Buffer → VAD → Feature Extraction → Emotion Detection → WebSocket Response
```

1. **Input:** Real-time audio chunks via WebSocket
2. **Buffering:** Accumulate audio data in circular buffer
3. **VAD:** Detect voice activity to filter silence
4. **Processing:** Extract features and detect emotion
5. **Output:** Real-time emotion results via WebSocket

### Batch Processing Flow

```
Multiple Files → Parallel Processing → Individual Results → Aggregated Response
```

1. **Input:** Multiple audio files
2. **Parallel Processing:** Process each file independently
3. **Error Handling:** Handle individual file failures gracefully
4. **Aggregation:** Combine results with success/failure statistics

## Technology Stack

### Core Technologies
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation and settings management
- **NumPy** - Numerical computing
- **Librosa** - Audio analysis and feature extraction
- **Transformers** - Hugging Face transformer models
- **Scikit-learn** - Machine learning algorithms

### Audio Processing
- **Librosa** - Audio loading, preprocessing, feature extraction
- **SoundFile** - Audio file I/O
- **NoiseReduce** - Noise reduction algorithms
- **PyAudio** - Real-time audio input/output

### Machine Learning
- **PyTorch** - Deep learning framework
- **Transformers** - Pre-trained transformer models
- **Scikit-learn** - Traditional ML algorithms
- **Joblib** - Model serialization

### Testing & Development
- **Pytest** - Testing framework
- **Pytest-asyncio** - Async testing support
- **Black** - Code formatting
- **Flake8** - Code linting

## Performance Characteristics

### Processing Times
- **File Analysis:** 0.1 - 0.5 seconds (depending on file size)
- **Streaming Analysis:** 0.05 - 0.2 seconds per chunk
- **Batch Processing:** 0.1 - 0.5 seconds per file (parallel)

### Resource Requirements
- **CPU:** Multi-core recommended for batch processing
- **Memory:** 2-4GB RAM for model loading and processing
- **Storage:** ~1GB for models and dependencies
- **Network:** Low latency for real-time streaming

### Scalability Considerations
- **Horizontal Scaling:** Stateless design supports multiple instances
- **Load Balancing:** Can be deployed behind load balancer
- **Caching:** Model caching reduces initialization time
- **Async Processing:** Non-blocking I/O for concurrent requests

## Security Considerations

### Input Validation
- File type validation for uploaded audio
- File size limits to prevent abuse
- Audio content validation

### Data Privacy
- No persistent storage of audio data
- Processing happens in memory only
- Configurable logging levels

### API Security
- CORS configuration for web applications
- Rate limiting capabilities (configurable)
- Error message sanitization

## Deployment Architecture

### Development Environment
```
Local Machine → FastAPI Dev Server → Local Models → Local Processing
```

### Production Environment
```
Load Balancer → Multiple API Instances → Shared Model Storage → Database (Optional)
```

### Container Deployment
- **Docker** - Containerization
- **Docker Compose** - Multi-service orchestration
- **Kubernetes** - Container orchestration (optional)

## Monitoring and Observability

### Logging
- Structured logging with Loguru
- Configurable log levels
- File and console output
- Request/response logging

### Metrics
- Processing time tracking
- Success/failure rates
- Model performance metrics
- Resource utilization

### Health Checks
- API health endpoint
- Model loading status
- System resource checks

## Future Enhancements

### Planned Features
- **Model Fine-tuning** - Custom emotion models
- **Multi-language Support** - Language-specific models
- **Emotion Intensity** - Continuous emotion scoring
- **Speaker Identification** - Multi-speaker scenarios
- **Real-time Visualization** - Live emotion dashboards

### Technical Improvements
- **GPU Acceleration** - CUDA support for faster processing
- **Model Optimization** - Quantization and pruning
- **Caching Layer** - Redis for model and result caching
- **Database Integration** - Persistent storage for analytics

## Development Guidelines

### Code Organization
- Modular design with clear separation of concerns
- Comprehensive type hints
- Docstring documentation
- Error handling and logging

### Testing Strategy
- Unit tests for individual components
- Integration tests for API endpoints
- Performance tests for scalability
- Mock-based testing for external dependencies

### Code Quality
- Automated formatting with Black
- Linting with Flake8
- Type checking with mypy
- Test coverage reporting

This architecture provides a robust, scalable foundation for voice emotion detection with clear separation of concerns and extensibility for future enhancements.
