# Dissonance Detector Service

## Overview

The Dissonance Detector Service is the core innovation of ResonaAI. It detects discrepancies between what users **say** (transcript sentiment) and how they **sound** (voice emotion) to identify hidden emotional distress.

**Key Innovation**: Detects truth gaps like "I'm fine" said with a sad voice, revealing concealed emotional states that traditional text-based analysis would miss.

## Architecture

The service compares:
- **Stated Emotion** (from transcript sentiment analysis using RoBERTa)
- **Actual Emotion** (from voice emotion detection)

When these diverge significantly, it indicates potential emotional concealment or distress.

## API Endpoints

### Health Check

**GET** `/health`

Returns service health status and model loading state.

**Response**:
```json
{
  "status": "healthy",
  "service": "dissonance-detector",
  "model_loaded": true,
  "model_status": "loaded",
  "timestamp": "2025-12-12T12:00:00"
}
```

### Analyze Dissonance

**POST** `/analyze`

Analyzes dissonance between transcript sentiment and voice emotion.

**Request Body**:
```json
{
  "transcript": "I'm fine, everything is okay",
  "voice_emotion": {
    "emotion": "sad",
    "confidence": 0.85
  },
  "session_id": "uuid-optional",
  "user_id": "uuid-optional",
  "timestamp": "2025-12-12T12:00:00"
}
```

**Response**:
```json
{
  "dissonance_level": "high",
  "dissonance_score": 0.82,
  "stated_emotion": "positive",
  "actual_emotion": "negative",
  "interpretation": "defensive_concealment",
  "risk_level": "medium-high",
  "confidence": 0.82,
  "details": {
    "sentiment_score": 0.75,
    "emotion_score": -0.65,
    "gap": 1.40,
    "normalized_gap": 0.70
  },
  "timestamp": "2025-12-12T12:00:00"
}
```

**Dissonance Levels**:
- `low`: Normal alignment (score < 0.3)
- `medium`: Moderate discrepancy (score 0.3-0.7)
- `high`: Significant discrepancy (score > 0.7)

**Interpretations**:
- `authentic`: Low dissonance, aligned emotions
- `defensive_concealment`: Positive words, negative emotion (highest risk)
- `recovery_indicator`: Negative words, positive emotion
- `intensity_mismatch`: Both negative but different intensities
- `unclear`: Pattern doesn't fit known categories

**Risk Levels**:
- `low`: Minimal concern
- `medium`: Moderate concern
- `medium-high`: Elevated concern (high dissonance + concealment)
- `high`: High concern, potential crisis

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SERVICE_PORT` | Service port | `8000` |
| `DEBUG` | Debug mode | `False` |
| `SENTIMENT_MODEL` | HuggingFace model name | `cardiffnlp/twitter-roberta-base-sentiment-latest` |
| `SENTIMENT_CACHE_SIZE` | Cache size for sentiment results | `1000` |
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_URL` | Redis connection string | `redis://redis:6379` |
| `EMOTION_SERVICE_URL` | Emotion analysis service URL | `http://emotion-analysis:8000` |

### Configuration File

Settings are defined in `config.py` using Pydantic Settings:

- **Dissonance Thresholds**: Configure when dissonance is considered low/medium/high
- **Emotion Valence Map**: Maps emotion names to valence scores (-1 to 1)
- **Risk Mapping**: Maps dissonance levels to risk levels

## Dependencies

### Python Dependencies

- `fastapi==0.104.1` - Web framework
- `transformers==4.36.0` - HuggingFace transformers for sentiment analysis
- `torch==2.1.1` - PyTorch for ML models
- `pydantic==2.5.0` - Data validation

See `requirements.txt` for complete list.

### External Services

- **Emotion Analysis Service**: Provides voice emotion data
- **Speech Processing Service**: Provides transcript data (indirect dependency)
- **PostgreSQL**: Database (currently configured but not actively used)
- **Redis**: Caching (currently configured but not actively used)

## Integration

### API Gateway

The service is accessible through the API Gateway at:

```
POST /api/dissonance/analyze
```

Authentication is required via Bearer token.

### Downstream Services

The dissonance detector output is consumed by:

1. **Crisis Detection Service**: Uses `dissonance_score` and `risk_level` for risk assessment
2. **Conversation Engine**: Uses dissonance context for empathetic response generation
3. **Baseline Tracker**: Stores dissonance patterns for user-specific analysis

### Integration Example

```python
import httpx

async def analyze_user_dissonance(transcript: str, voice_emotion: dict, token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://dissonance-detector:8000/analyze",
            json={
                "transcript": transcript,
                "voice_emotion": voice_emotion
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
```

## Development

### Running Locally

```bash
cd apps/backend/services/dissonance-detector
pip install -r requirements.txt
python main.py
```

Service will start on `http://localhost:8000`

### Running with Docker

```bash
docker-compose -f ../../../infra/docker/docker-compose.yml up dissonance-detector
```

### Testing

Run tests:

```bash
pytest ../../../tests/services/dissonance-detector/ -v
```

Current test coverage: 7/7 tests passing

## Performance

### Response Time

- Target: < 500ms (95th percentile)
- Model loading: < 5 seconds on startup
- Sentiment analysis: ~100-200ms (with caching)
- Dissonance calculation: < 10ms

### Resource Usage

- Memory: ~2GB (includes RoBERTa model)
- CPU: Moderate during sentiment analysis
- Caching: Reduces repeated sentiment analysis by 90%+

## Troubleshooting

### Model Not Loading

**Symptom**: Health check shows `model_loaded: false`

**Solutions**:
1. Check internet connection (model downloads from HuggingFace)
2. Verify sufficient disk space (~500MB for model)
3. Check logs for specific error messages
4. Verify `SENTIMENT_MODEL` environment variable is correct

### Slow Response Times

**Symptom**: Requests take > 1 second

**Solutions**:
1. Check if model is loaded (health endpoint)
2. Verify caching is working (check logs for cache hits)
3. Consider GPU support for faster inference
4. Check network latency to dependencies

### High Memory Usage

**Symptom**: Service using > 3GB memory

**Solutions**:
1. Reduce `SENTIMENT_CACHE_SIZE` if needed
2. Use smaller sentiment model (trade-off: accuracy)
3. Enable model quantization

## Security

- All endpoints require authentication via Bearer token
- Input validation on all requests
- Sensitive data is not logged
- CORS configured based on DEBUG mode

## Monitoring

### Health Checks

Monitor `/health` endpoint for:
- Service availability
- Model loading status
- Service degradation

### Logs

Key log events:
- Model loading (startup)
- Dissonance analysis (info level)
- Errors (error level with stack traces)

### Metrics to Monitor

- Request rate
- Response time (p50, p95, p99)
- Error rate
- Model loading status
- Cache hit rate

## License

Part of ResonaAI platform. See main project license.

