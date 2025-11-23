# ResonaAI - Voice Emotion Detection Pipeline

A comprehensive voice emotion detection system that analyzes audio input to identify emotional states in real-time and batch processing modes.

## Features

- **Real-time Emotion Detection**: Process live audio streams with low latency
- **Batch Processing**: Analyze pre-recorded audio files
- **Multiple Emotion Categories**: Detect happiness, sadness, anger, fear, surprise, disgust, neutral
- **Confidence Scoring**: Provide confidence levels for each emotion prediction
- **REST API**: Easy integration with web applications
- **WebSocket Support**: Real-time streaming for live applications
- **Audio Preprocessing**: Noise reduction, normalization, and feature extraction

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Run the API Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## API Endpoints

### Real-time Emotion Detection
- `POST /detect-emotion/stream` - Process audio stream in real-time
- `WebSocket /ws/emotion-stream` - WebSocket connection for live streaming

### Batch Processing
- `POST /detect-emotion/batch` - Analyze pre-recorded audio files
- `POST /detect-emotion/file` - Upload and analyze audio file

### Health Check
- `GET /health` - System health status

## Usage Examples

### Python Client

```python
import requests
import json

# Analyze audio file
with open('audio.wav', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/detect-emotion/file',
        files={'file': f}
    )
    result = response.json()
    print(f"Detected emotion: {result['emotion']} (confidence: {result['confidence']:.2f})")
```

### JavaScript/WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/emotion-stream');

ws.onmessage = function(event) {
    const result = JSON.parse(event.data);
    console.log(`Emotion: ${result.emotion}, Confidence: ${result.confidence}`);
};
```

## Architecture

The system consists of several key components:

1. **Audio Preprocessing**: Noise reduction, normalization, and feature extraction
2. **Feature Extraction**: MFCC, spectral features, and prosodic analysis
3. **Emotion Classification**: Deep learning models for emotion detection
4. **API Layer**: REST and WebSocket endpoints for integration
5. **Streaming Processor**: Real-time audio processing pipeline

## Model Information

The system uses pre-trained transformer models (Wav2Vec2/HuBERT) fine-tuned for emotion recognition, combined with traditional audio features for robust emotion detection.

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black .
flake8 .
```

## License

MIT License
