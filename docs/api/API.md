# ResonaAI Voice Emotion Detection API Documentation

## Overview

The ResonaAI Voice Emotion Detection API provides comprehensive emotion analysis from audio input. It supports real-time streaming, batch processing, and file upload analysis with multiple emotion categories and confidence scoring.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required. All endpoints are publicly accessible.

## Endpoints

### Health Check

#### GET /health

Check the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "message": "ResonaAI Voice Emotion Detection Pipeline is running",
  "version": "1.0.0",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### File Emotion Detection

#### POST /detect-emotion/file

Analyze emotion from an uploaded audio file.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: Audio file (WAV, MP3, FLAC, M4A)

**Parameters:**
- `file` (required): Audio file to analyze

**Response:**
```json
{
  "emotion": "happy",
  "confidence": 0.85,
  "timestamp": "2024-01-01T12:00:00Z",
  "features": {
    "mfcc": [[...]],
    "spectral": {...},
    "prosodic": {...}
  },
  "processing_time": 0.123
}
```

**Error Response:**
```json
{
  "error": "Failed to process audio file: Invalid audio format"
}
```

### Batch Emotion Detection

#### POST /detect-emotion/batch

Analyze emotions from multiple audio files.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: Multiple audio files

**Parameters:**
- `files` (required): Array of audio files to analyze

**Response:**
```json
{
  "total_files": 3,
  "successful_analyses": 2,
  "results": [
    {
      "filename": "audio1.wav",
      "emotion": "happy",
      "confidence": 0.85,
      "features": {...}
    },
    {
      "filename": "audio2.wav",
      "emotion": "sad",
      "confidence": 0.72,
      "features": {...}
    },
    {
      "filename": "audio3.wav",
      "error": "Invalid audio format"
    }
  ],
  "processing_time": 0.456
}
```

### Streaming Emotion Detection

#### POST /detect-emotion/stream

Process audio stream for real-time emotion detection.

**Request:**
- Method: `POST`
- Content-Type: `application/octet-stream`
- Body: Raw audio bytes (float32)

**Response:**
```json
{
  "emotion": "neutral",
  "confidence": 0.65,
  "timestamp": "2024-01-01T12:00:00Z",
  "features": {
    "temporal": {...},
    "statistical": {...}
  }
}
```

### WebSocket Emotion Streaming

#### WebSocket /ws/emotion-stream

Real-time emotion detection via WebSocket connection.

**Connection:**
```
ws://localhost:8000/ws/emotion-stream
```

**Message Format:**
- Send: Raw audio bytes (float32)
- Receive: JSON emotion result

**Example:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/emotion-stream');

ws.onopen = function() {
    // Send audio data
    ws.send(audioBytes);
};

ws.onmessage = function(event) {
    const result = JSON.parse(event.data);
    console.log(`Emotion: ${result.emotion}, Confidence: ${result.confidence}`);
};
```

## Emotion Categories

The API detects the following emotions:

- `neutral` - Neutral emotional state
- `happy` - Happiness, joy, contentment
- `sad` - Sadness, melancholy, grief
- `angry` - Anger, frustration, irritation
- `fear` - Fear, anxiety, worry
- `surprise` - Surprise, astonishment, shock
- `disgust` - Disgust, revulsion, contempt

## Confidence Scoring

Confidence scores range from 0.0 to 1.0:
- `0.0 - 0.3`: Low confidence
- `0.3 - 0.7`: Medium confidence
- `0.7 - 1.0`: High confidence

## Audio Requirements

### Supported Formats
- WAV (recommended)
- MP3
- FLAC
- M4A

### Audio Specifications
- Sample Rate: 16kHz (recommended)
- Channels: Mono
- Duration: 0.1s - 30s
- File Size: Max 10MB

### Audio Quality
- Clear audio with minimal background noise
- Speech should be the primary audio content
- Avoid heavily compressed or distorted audio

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 500 | Internal Server Error - Processing failed |

## Rate Limits

Currently, no rate limits are enforced. However, for production use, consider implementing rate limiting based on your requirements.

## Examples

### Python Example

```python
import requests

# Analyze audio file
with open('audio.wav', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/detect-emotion/file', files=files)
    result = response.json()
    print(f"Emotion: {result['emotion']}, Confidence: {result['confidence']}")
```

### JavaScript Example

```javascript
const formData = new FormData();
formData.append('file', audioFile);

fetch('http://localhost:8000/detect-emotion/file', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log(`Emotion: ${data.emotion}, Confidence: ${data.confidence}`);
});
```

### cURL Example

```bash
curl -X POST "http://localhost:8000/detect-emotion/file" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@audio.wav"
```

## Performance Considerations

### Processing Times
- File analysis: 0.1 - 0.5 seconds
- Streaming analysis: 0.05 - 0.2 seconds
- Batch processing: 0.1 - 0.5 seconds per file

### Optimization Tips
- Use WAV format for best performance
- Keep audio files under 5MB
- Use 16kHz sample rate
- Minimize background noise

## Troubleshooting

### Common Issues

1. **"Invalid audio format" error**
   - Ensure audio file is in supported format
   - Check file is not corrupted
   - Verify audio has content (not empty)

2. **Low confidence scores**
   - Check audio quality and clarity
   - Ensure speech is the primary content
   - Reduce background noise

3. **Processing timeouts**
   - Reduce file size
   - Check server resources
   - Verify network connectivity

### Debug Mode

Enable debug logging by setting `DEBUG=true` in your environment configuration.

## Support

For technical support or questions, please refer to the project documentation or create an issue in the project repository.
