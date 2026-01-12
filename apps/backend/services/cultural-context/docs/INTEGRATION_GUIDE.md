# Cultural Context Service Integration Guide

This guide explains how to integrate the Cultural Context Service with other ResonaAI services, particularly the Conversation Engine.

## Overview

The Cultural Context Service provides deep cultural analysis for East African mental health support, including:

- **Swahili deflection pattern detection** - Identifies cultural ways of avoiding direct emotional expression
- **Code-switching analysis** - Detects emotional significance of language mixing
- **Cultural context retrieval** - Provides relevant cultural knowledge via RAG
- **Voice-text contradiction detection** - Identifies when voice tone contradicts spoken words
- **Risk assessment with cultural factors** - Evaluates risk levels considering cultural context

## API Endpoints

### 1. Basic Cultural Context (`GET /context`)

Retrieves cultural context for a user query with caching support.

```http
GET /context?query=nimechoka&language=sw
Authorization: Bearer <token>
```

**Response:**
```json
{
  "cultural_context": [
    {
      "id": "swahili_deflection_nimechoka",
      "content": "The phrase 'nimechoka' often indicates emotional exhaustion...",
      "keywords": ["nimechoka", "tired", "exhaustion"],
      "cultural_significance": "high"
    }
  ],
  "deflection_analysis": {
    "deflection_detected": true,
    "patterns": [
      {
        "pattern": "nimechoka",
        "type": "emotional_exhaustion",
        "severity": "medium",
        "cultural_meaning": "I am tired - can indicate emotional exhaustion",
        "probe_suggestions": [
          "I hear you're tired. Can you tell me more about what kind of tiredness you're feeling?"
        ]
      }
    ]
  },
  "code_switching_analysis": {
    "code_switching_detected": false,
    "intensity": "low"
  },
  "source": "rag_retrieval",
  "timestamp": "2025-01-12T10:30:00Z"
}
```

### 2. Comprehensive Cultural Analysis (`POST /cultural-analysis`)

**Recommended for Conversation Engine integration** - provides complete analysis with conversation guidance.

```http
POST /cultural-analysis
Authorization: Bearer <token>
Content-Type: application/json

{
  "text": "Nimechoka sana, but I'm fine",
  "language": "sw",
  "emotion": "sad",
  "voice_features": {
    "tone": "sad",
    "energy": "low"
  }
}
```

**Response:**
```json
{
  "text": "Nimechoka sana, but I'm fine",
  "language": "sw",
  "emotion": "sad",
  "cultural_context": { /* Basic context response */ },
  "risk_factors": [
    {
      "type": "medium_risk_deflection",
      "patterns": [
        {
          "pattern": "nimechoka",
          "severity": "medium"
        }
      ],
      "recommendation": "Supportive exploration recommended"
    },
    {
      "type": "voice_text_contradiction",
      "details": [
        {
          "type": "sad_voice_positive_words",
          "description": "Voice indicates sadness but words suggest being okay",
          "severity_multiplier": 1.5
        }
      ],
      "recommendation": "Voice and words don't match - gentle exploration needed"
    }
  ],
  "conversation_guidance": {
    "code_switching": {
      "detected": true,
      "intensity": "medium",
      "recommendation": "Code-switching indicates medium emotional intensity. Consider mirroring language preference."
    },
    "privacy": {
      "importance": "high",
      "recommendation": "Emphasize confidentiality and frame help-seeking as protecting family"
    },
    "spirituality": {
      "importance": "high",
      "recommendation": "Respect spiritual beliefs and integrate them into support"
    }
  },
  "response_adaptations": [
    {
      "type": "language_preference",
      "suggestion": "Consider incorporating Swahili phrases or acknowledging code-switching"
    },
    {
      "type": "deflection_response",
      "pattern": "nimechoka",
      "suggestions": [
        "I hear you're tired. Can you tell me more about what kind of tiredness you're feeling?",
        "Sometimes 'nimechoka' means more than just physical tiredness. What's been wearing you down?"
      ]
    }
  ],
  "overall_risk_level": "medium",
  "timestamp": "2025-01-12T10:30:00Z"
}
```

### 3. Bias Detection (`POST /bias-check`)

Checks text for cultural biases and insensitivities.

```http
POST /bias-check?text=Your culture is the problem
Authorization: Bearer <token>
```

**Response:**
```json
{
  "overall_sensitivity": "problematic",
  "issues": [
    {
      "type": "cultural_insensitivity",
      "severity": "medium",
      "pattern": "your culture is the problem",
      "suggestion": "Consider rephrasing to focus on specific challenges rather than blaming culture"
    }
  ],
  "suggestions": [
    "Replace 'your culture is the problem' with 'there may be cultural factors to consider'"
  ]
}
```

## Integration with Conversation Engine

### Recommended Integration Flow

1. **User Input Processing**
   ```python
   # In conversation engine
   async def process_user_input(text: str, emotion: str, voice_features: dict):
       # Get cultural analysis
       cultural_analysis = await call_cultural_context_service(
           text=text,
           emotion=emotion,
           voice_features=voice_features
       )
       
       # Use analysis to adapt response
       response = await generate_culturally_aware_response(
           text=text,
           emotion=emotion,
           cultural_analysis=cultural_analysis
       )
       
       return response
   ```

2. **Cultural Context Integration**
   ```python
   async def call_cultural_context_service(text: str, emotion: str, voice_features: dict):
       async with httpx.AsyncClient() as client:
           response = await client.post(
               f"{CULTURAL_CONTEXT_URL}/cultural-analysis",
               json={
                   "text": text,
                   "language": detect_language(text),
                   "emotion": emotion,
                   "voice_features": voice_features
               },
               headers={"Authorization": f"Bearer {token}"}
           )
           return response.json()
   ```

3. **Response Adaptation**
   ```python
   async def generate_culturally_aware_response(text: str, emotion: str, cultural_analysis: dict):
       # Extract guidance
       risk_level = cultural_analysis.get("overall_risk_level", "low")
       adaptations = cultural_analysis.get("response_adaptations", [])
       guidance = cultural_analysis.get("conversation_guidance", {})
       
       # Build culturally-aware prompt
       prompt = build_cultural_prompt(
           text=text,
           emotion=emotion,
           risk_level=risk_level,
           adaptations=adaptations,
           guidance=guidance
       )
       
       # Generate response with GPT
       response = await gpt_service.generate_response(prompt)
       
       # Apply cultural adaptations
       adapted_response = apply_cultural_adaptations(response, adaptations)
       
       return adapted_response
   ```

### Cultural Prompt Engineering

Use cultural analysis to enhance GPT prompts:

```python
def build_cultural_prompt(text: str, emotion: str, risk_level: str, adaptations: list, guidance: dict):
    prompt = f"""
    You are providing mental health support to someone from East African culture.
    
    User input: "{text}"
    Detected emotion: {emotion}
    Risk level: {risk_level}
    
    Cultural considerations:
    """
    
    # Add deflection guidance
    deflection_adaptations = [a for a in adaptations if a["type"] == "deflection_response"]
    if deflection_adaptations:
        prompt += f"""
    - The user may be using cultural deflection patterns. Consider these gentle probes:
      {deflection_adaptations[0]["suggestions"]}
    """
    
    # Add language preference
    language_adaptations = [a for a in adaptations if a["type"] == "language_preference"]
    if language_adaptations:
        prompt += f"""
    - {language_adaptations[0]["suggestion"]}
    """
    
    # Add privacy guidance
    if "privacy" in guidance:
        prompt += f"""
    - Privacy is very important in East African culture. {guidance["privacy"]["recommendation"]}
    """
    
    # Add spirituality guidance
    if "spirituality" in guidance:
        prompt += f"""
    - Spiritual beliefs are significant. {guidance["spirituality"]["recommendation"]}
    """
    
    prompt += """
    
    Respond with empathy, cultural sensitivity, and appropriate level of concern based on the risk level.
    """
    
    return prompt
```

## Vector Database Setup

### Production Setup with Pinecone

1. **Environment Variables**
   ```bash
   PINECONE_API_KEY=your-pinecone-api-key
   PINECONE_INDEX_NAME=cultural-context
   OPENAI_API_KEY=your-openai-api-key  # For embeddings
   ```

2. **Initialize Vector Database**
   ```bash
   cd apps/backend/services/cultural-context
   python scripts/setup_vector_db.py --provider pinecone --create-index --index-kb
   ```

3. **Verify Setup**
   ```bash
   python scripts/setup_vector_db.py --status
   ```

### Development Setup (In-Memory)

For development, the service automatically falls back to in-memory storage:

```bash
# No additional setup needed
# Service will use in-memory vectors automatically
```

## Error Handling

### Common Integration Patterns

```python
async def safe_cultural_analysis(text: str, emotion: str = None):
    try:
        response = await call_cultural_context_service(text, emotion)
        return response
    except httpx.TimeoutException:
        logger.warning("Cultural context service timeout, using fallback")
        return create_fallback_analysis(text, emotion)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            logger.warning("Cultural context service not available")
            return create_fallback_analysis(text, emotion)
        raise
    except Exception as e:
        logger.error(f"Cultural context service error: {e}")
        return create_fallback_analysis(text, emotion)

def create_fallback_analysis(text: str, emotion: str = None):
    """Fallback analysis when service is unavailable"""
    return {
        "overall_risk_level": "low",
        "response_adaptations": [],
        "conversation_guidance": {},
        "risk_factors": [],
        "source": "fallback"
    }
```

## Performance Considerations

### Caching Strategy

The service implements intelligent caching:

- **Database caching** for repeated queries (24-hour TTL)
- **Vector search caching** for similar semantic queries
- **Pattern detection caching** for common deflection patterns

### Response Times

Expected response times:
- **Basic context retrieval**: 100-300ms
- **Comprehensive analysis**: 200-500ms
- **Vector search (Pinecone)**: 50-150ms
- **Vector search (in-memory)**: 10-50ms

### Rate Limiting

Consider implementing rate limiting for production:

```python
# In conversation engine
from asyncio import Semaphore

cultural_context_semaphore = Semaphore(10)  # Max 10 concurrent requests

async def call_cultural_context_with_limit(*args, **kwargs):
    async with cultural_context_semaphore:
        return await call_cultural_context_service(*args, **kwargs)
```

## Monitoring and Observability

### Key Metrics to Track

1. **Response Times**
   - Cultural analysis endpoint latency
   - Vector search performance
   - Cache hit rates

2. **Cultural Pattern Detection**
   - Deflection pattern detection rates
   - Code-switching detection accuracy
   - Risk level distribution

3. **Service Health**
   - Vector database connectivity
   - Embedding service availability
   - Cache performance

### Logging

Enable structured logging for cultural context:

```python
import structlog

logger = structlog.get_logger("cultural_context")

# Log cultural analysis results
logger.info(
    "cultural_analysis_completed",
    user_id=user_id,
    risk_level=analysis["overall_risk_level"],
    deflection_detected=bool(analysis.get("deflection_analysis", {}).get("deflection_detected")),
    code_switching_detected=bool(analysis.get("code_switching_analysis", {}).get("code_switching_detected")),
    response_time_ms=response_time
)
```

## Testing Integration

### Unit Tests

```python
@pytest.mark.asyncio
async def test_conversation_with_cultural_context():
    with patch('conversation_engine.call_cultural_context_service') as mock_cultural:
        mock_cultural.return_value = {
            "overall_risk_level": "medium",
            "response_adaptations": [
                {
                    "type": "deflection_response",
                    "suggestions": ["Can you tell me more?"]
                }
            ]
        }
        
        response = await process_user_input("Nimechoka", "sad", {})
        
        assert "tell me more" in response.lower()
        mock_cultural.assert_called_once()
```

### Integration Tests

```python
@pytest.mark.integration
async def test_full_cultural_context_flow():
    # Test actual service integration
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{CULTURAL_CONTEXT_URL}/cultural-analysis",
            json={
                "text": "Nimechoka sana",
                "language": "sw",
                "emotion": "sad"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "overall_risk_level" in data
        assert "response_adaptations" in data
```

## Deployment Checklist

- [ ] Vector database configured (Pinecone recommended for production)
- [ ] Knowledge base indexed successfully
- [ ] Environment variables set
- [ ] Service health checks passing
- [ ] Integration tests passing
- [ ] Monitoring and logging configured
- [ ] Rate limiting implemented (if needed)
- [ ] Fallback mechanisms tested

## Support and Troubleshooting

### Common Issues

1. **Vector Database Connection Failed**
   - Check environment variables
   - Verify API keys
   - Test connection with setup script

2. **Low Cultural Pattern Detection**
   - Verify knowledge base is indexed
   - Check Swahili patterns file
   - Review embedding service configuration

3. **High Response Times**
   - Check vector database performance
   - Review cache hit rates
   - Consider scaling vector database

### Getting Help

- Check service logs for detailed error messages
- Use the setup script's `--status` flag for diagnostics
- Review the health endpoint for service status
- Consult the API documentation for endpoint details

For additional support, refer to the main ResonaAI documentation or contact the development team.