# Cultural Context Service - API Documentation

**Version**: 2.0  
**Base URL**: `http://localhost:8000`  
**Authentication**: Bearer token required for all endpoints

---

## Table of Contents

1. [Authentication](#authentication)
2. [Endpoints](#endpoints)
   - [Health Check](#health-check)
   - [Get Cultural Context](#get-cultural-context)
   - [Cultural Analysis](#cultural-analysis)
   - [Index Knowledge Base](#index-knowledge-base)
   - [Bias Check](#bias-check)
3. [Data Models](#data-models)
4. [Error Handling](#error-handling)
5. [Examples](#examples)

---

## Authentication

All endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <your-token>
```

For testing, use: `Bearer test-token`

---

## Endpoints

### Health Check

Check service health and vector database status.

**Endpoint**: `GET /health`  
**Authentication**: Not required

**Response**:
```json
{
  "status": "healthy",
  "service": "cultural-context",
  "db_connected": true,
  "vector_db": {
    "vector_db_type": "memory",
    "connected": true,
    "embedding_service_available": true,
    "vector_count": 30
  }
}
```

**cURL Example**:
```bash
curl http://localhost:8000/health
```

**PowerShell Example**:
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/health" | Select-Object -ExpandProperty Content
```

---

### Get Cultural Context

Retrieve cultural context for a given query using RAG-based semantic search.

**Endpoint**: `GET /context`  
**Authentication**: Required

**Query Parameters**:
- `query` (required): Text query to search for cultural context
- `language` (optional): Language code (`en`, `sw`, or `auto`). Default: `auto`

**Response**:
```json
{
  "cultural_context": [
    {
      "id": "swahili_deflection_nimechoka",
      "content": "The phrase 'nimechoka' (I am tired) in Swahili often indicates emotional exhaustion...",
      "keywords": ["nimechoka", "tired", "exhaustion", "burnout", "depression"],
      "language": "sw",
      "region": "east_africa",
      "category": "emotional_expressions",
      "severity": "medium",
      "cultural_significance": "high"
    }
  ],
  "context": "Be mindful of East African norms around privacy...",
  "language": "sw",
  "query": "nimechoka",
  "source": "local_kb_retrieval",
  "matches": [...],
  "deflection_analysis": {
    "deflection_detected": true,
    "deflection_count": 1,
    "deflections": [...],
    "risk_assessment": {...},
    "probe_suggestions": [...]
  },
  "code_switching_analysis": {...},
  "timestamp": "2026-01-12T10:30:00+00:00"
}
```

**cURL Example**:
```bash
curl "http://localhost:8000/context?query=nimechoka&language=sw" \
  -H "Authorization: Bearer test-token"
```

**PowerShell Example**:
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/context?query=nimechoka&language=sw" `
  -Headers @{"Authorization"="Bearer test-token"} | 
  Select-Object -ExpandProperty Content | ConvertFrom-Json
```

**Python Example**:
```python
import requests

response = requests.get(
    "http://localhost:8000/context",
    params={"query": "nimechoka", "language": "sw"},
    headers={"Authorization": "Bearer test-token"}
)
data = response.json()
print(f"Deflection detected: {data['deflection_analysis']['deflection_detected']}")
```

---

### Cultural Analysis

Perform comprehensive cultural analysis including deflection detection, code-switching analysis, voice contradiction detection, and risk assessment.

**Endpoint**: `POST /cultural-analysis`  
**Authentication**: Required  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "text": "Nimechoka sana, lakini sawa tu",
  "language": "sw",
  "emotion": "sad",
  "voice_features": {
    "tone": "sad",
    "energy": "low",
    "pitch": "low"
  }
}
```

**Parameters**:
- `text` (required): Text to analyze
- `language` (optional): Language code. Default: `"en"`
- `emotion` (optional): Detected emotion from voice
- `voice_features` (optional): Voice analysis features

**Response**:
```json
{
  "text": "Nimechoka sana, lakini sawa tu",
  "language": "sw",
  "emotion": "sad",
  "cultural_context": {
    "cultural_context": [...],
    "deflection_analysis": {
      "deflection_detected": true,
      "deflection_count": 2,
      "deflections": [
        {
          "pattern": "nimechoka",
          "type": "emotional_exhaustion",
          "severity": "medium",
          "cultural_meaning": "I am tired - can indicate emotional exhaustion...",
          "interpretation": "The user is expressing significant fatigue...",
          "confidence": 0.8,
          "position": 0,
          "context": "Nimechoka sana, lakini sawa tu"
        },
        {
          "pattern": "sawa tu",
          "type": "minimization",
          "severity": "medium",
          "cultural_meaning": "It's just okay - minimization phrase...",
          "interpretation": "The user is actively minimizing their distress...",
          "confidence": 0.7,
          "position": 22,
          "context": "Nimechoka sana, lakini sawa tu"
        }
      ],
      "risk_assessment": {
        "risk_level": "medium",
        "risk_score": 0.45,
        "factors": [
          "Medium-severity deflection: nimechoka",
          "Medium-severity deflection: sawa tu"
        ],
        "interpretation": "Medium risk detected: 2 medium-severity deflections...",
        "severity_breakdown": {
          "low": 0,
          "medium": 2,
          "high": 0,
          "critical": 0
        }
      },
      "probe_suggestions": [
        "I hear you're tired. Can you tell me more about what kind of tiredness you're feeling?",
        "I hear you say it's 'just okay'. Sometimes we use 'tu' to make things seem smaller than they are. How are things really?"
      ],
      "recommended_action": "Patient, gentle approach. Don't push, but offer opportunities to open up."
    },
    "code_switching_analysis": {...}
  },
  "risk_factors": [
    {
      "type": "medium_risk_deflection",
      "patterns": [...],
      "recommendation": "Supportive exploration recommended"
    }
  ],
  "conversation_guidance": {
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
    }
  ],
  "overall_risk_level": "medium",
  "timestamp": "2026-01-12T10:30:00+00:00"
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/cultural-analysis" \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Nimechoka sana, lakini sawa tu",
    "language": "sw",
    "emotion": "sad"
  }'
```

**PowerShell Example**:
```powershell
$body = @{
    text = "Nimechoka sana, lakini sawa tu"
    language = "sw"
    emotion = "sad"
} | ConvertTo-Json

Invoke-WebRequest -Method POST `
  -Uri "http://localhost:8000/cultural-analysis" `
  -Headers @{
    "Authorization" = "Bearer test-token"
    "Content-Type" = "application/json"
  } `
  -Body $body | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

**Python Example**:
```python
import requests

response = requests.post(
    "http://localhost:8000/cultural-analysis",
    headers={
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    },
    json={
        "text": "Nimechoka sana, lakini sawa tu",
        "language": "sw",
        "emotion": "sad"
    }
)

data = response.json()
print(f"Overall risk level: {data['overall_risk_level']}")
print(f"Deflections detected: {data['cultural_context']['deflection_analysis']['deflection_count']}")

for deflection in data['cultural_context']['deflection_analysis']['deflections']:
    print(f"  - {deflection['pattern']}: {deflection['severity']}")
```

---

### Index Knowledge Base

Index or re-index the cultural knowledge base into the vector database.

**Endpoint**: `POST /index-kb`  
**Authentication**: Required

**Query Parameters**:
- `clear_existing` (optional): Clear existing index before indexing. Default: `false`

**Response**:
```json
{
  "success": true,
  "message": "Successfully indexed 30/30 entries",
  "indexed_count": 30,
  "total_entries": 30,
  "vector_db_type": "memory",
  "stats": {
    "vector_db_type": "memory",
    "total_vector_count": 30
  }
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/index-kb?clear_existing=true" \
  -H "Authorization: Bearer test-token"
```

**PowerShell Example**:
```powershell
Invoke-WebRequest -Method POST `
  -Uri "http://localhost:8000/index-kb?clear_existing=true" `
  -Headers @{"Authorization"="Bearer test-token"} |
  Select-Object -ExpandProperty Content | ConvertFrom-Json
```

---

### Bias Check

Check text for cultural bias and sensitivity issues.

**Endpoint**: `POST /bias-check`  
**Authentication**: Required

**Query Parameters**:
- `text` (required): Text to check for bias

**Response**:
```json
{
  "overall_sensitivity": "appropriate",
  "issues": [],
  "suggestions": [],
  "timestamp": "2026-01-12T10:30:00+00:00"
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/bias-check?text=This is appropriate text" \
  -H "Authorization: Bearer test-token"
```

---

## Data Models

### Deflection Pattern

```typescript
{
  pattern: string;           // The detected pattern (e.g., "nimechoka")
  type: string;             // Pattern type (e.g., "emotional_exhaustion")
  severity: string;         // "low" | "medium" | "high" | "critical"
  cultural_meaning: string; // Cultural interpretation
  interpretation: string;   // Psychological interpretation
  confidence: number;       // 0.0 to 1.0
  position: number;         // Position in text
  context: string;          // Surrounding context
}
```

### Risk Assessment

```typescript
{
  risk_level: string;       // "low" | "medium" | "high" | "critical"
  risk_score: number;       // 0.0 to 1.0
  factors: string[];        // List of risk factors
  interpretation: string;   // Risk interpretation
  severity_breakdown: {
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
  contradiction_count: number;
}
```

### Cultural Context Entry

```typescript
{
  id: string;
  content: string;
  keywords: string[];
  language: string;         // "en" | "sw" | "mixed"
  region: string;           // "east_africa"
  category: string;
  severity: string;
  cultural_significance: string;
}
```

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message description"
}
```

### HTTP Status Codes

- `200 OK`: Successful request
- `400 Bad Request`: Invalid parameters or missing required fields
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Common Errors

**Missing Query Parameter**:
```json
{
  "detail": "query is required"
}
```

**Missing Text Parameter**:
```json
{
  "detail": "text is required"
}
```

**Authentication Error**:
```json
{
  "detail": "Not authenticated"
}
```

---

## Examples

### Example 1: Crisis Detection

**Request**:
```bash
curl -X POST "http://localhost:8000/cultural-analysis" \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Nataka kufa, sina sababu ya kuishi",
    "language": "sw",
    "emotion": "hopeless"
  }'
```

**Response** (abbreviated):
```json
{
  "overall_risk_level": "critical",
  "risk_factors": [
    {
      "type": "critical_risk_deflection",
      "recommendation": "CRISIS INTERVENTION REQUIRED: Suicide ideation or severe hopelessness detected. Assess safety immediately."
    }
  ],
  "cultural_context": {
    "deflection_analysis": {
      "deflections": [
        {
          "pattern": "nataka kufa",
          "severity": "critical",
          "cultural_meaning": "I want to die - direct expression of suicidal ideation..."
        },
        {
          "pattern": "sina sababu ya kuishi",
          "severity": "critical",
          "cultural_meaning": "I have no reason to live - expression of profound hopelessness..."
        }
      ],
      "probe_suggestions": [
        "I hear you're in a lot of pain right now. You're not alone. Can you tell me if you're safe right now?",
        "Thank you for trusting me with this. I want to help keep you safe. Do you have thoughts about how you might hurt yourself?"
      ],
      "recommended_action": "CRISIS INTERVENTION: Assess immediate safety. Ask about suicide plan and means. Provide crisis hotline. Do not leave user alone."
    }
  }
}
```

### Example 2: Voice Contradiction Detection

**Request**:
```python
import requests

response = requests.post(
    "http://localhost:8000/cultural-analysis",
    headers={
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    },
    json={
        "text": "Sijambo, everything is sawa",
        "language": "sw",
        "emotion": "sad",
        "voice_features": {
            "tone": "sad",
            "energy": "low"
        }
    }
)

data = response.json()
print(f"Risk level: {data['overall_risk_level']}")

# Check for voice contradictions
for risk_factor in data['risk_factors']:
    if risk_factor['type'] == 'voice_text_contradiction':
        print(f"Voice contradiction detected: {risk_factor['recommendation']}")
```

### Example 3: Code-Switching Analysis

**Request**:
```powershell
$body = @{
    text = "I am feeling nimechoka and wasiwasi about my familia"
    language = "en"
    emotion = "anxious"
} | ConvertTo-Json

$response = Invoke-WebRequest -Method POST `
  -Uri "http://localhost:8000/cultural-analysis" `
  -Headers @{
    "Authorization" = "Bearer test-token"
    "Content-Type" = "application/json"
  } `
  -Body $body

$data = $response.Content | ConvertFrom-Json

# Check code-switching
if ($data.cultural_context.code_switching_analysis.code_switching_detected) {
    Write-Output "Code-switching detected!"
    Write-Output "Intensity: $($data.cultural_context.code_switching_analysis.intensity)"
}

# Check response adaptations
foreach ($adaptation in $data.response_adaptations) {
    if ($adaptation.type -eq "language_preference") {
        Write-Output "Suggestion: $($adaptation.suggestion)"
    }
}
```

### Example 4: Batch Processing

**Python Script**:
```python
import requests

messages = [
    {"text": "Nimechoka sana", "language": "sw", "emotion": "tired"},
    {"text": "Familia yangu hawanielewi", "language": "sw", "emotion": "sad"},
    {"text": "Sina nguvu", "language": "sw", "emotion": "exhausted"},
    {"text": "Nataka kusema something", "language": "en", "emotion": "neutral"}
]

results = []
for message in messages:
    response = requests.post(
        "http://localhost:8000/cultural-analysis",
        headers={
            "Authorization": "Bearer test-token",
            "Content-Type": "application/json"
        },
        json=message
    )
    
    data = response.json()
    results.append({
        "text": message["text"],
        "risk_level": data["overall_risk_level"],
        "deflections": data["cultural_context"]["deflection_analysis"]["deflection_count"]
    })

# Print summary
for result in results:
    print(f"{result['text']}: {result['risk_level']} risk, {result['deflections']} deflections")
```

---

## Integration Guide

### Integrating with Conversation Engine

```python
import requests

class CulturalContextClient:
    def __init__(self, base_url="http://localhost:8000", token="test-token"):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def analyze_message(self, text, language="auto", emotion=None, voice_features=None):
        """Analyze a user message for cultural context"""
        response = requests.post(
            f"{self.base_url}/cultural-analysis",
            headers=self.headers,
            json={
                "text": text,
                "language": language,
                "emotion": emotion,
                "voice_features": voice_features
            }
        )
        return response.json()
    
    def get_probe_suggestions(self, analysis):
        """Extract probe suggestions from analysis"""
        deflection = analysis.get("cultural_context", {}).get("deflection_analysis", {})
        return deflection.get("probe_suggestions", [])
    
    def get_risk_level(self, analysis):
        """Get overall risk level"""
        return analysis.get("overall_risk_level", "low")
    
    def should_escalate(self, analysis):
        """Check if crisis escalation is needed"""
        return analysis.get("overall_risk_level") in ["critical", "high"]

# Usage
client = CulturalContextClient()

# Analyze user message
analysis = client.analyze_message(
    text="Nimechoka sana, sina nguvu",
    language="sw",
    emotion="sad"
)

# Check risk level
if client.should_escalate(analysis):
    print("ALERT: Crisis intervention needed!")
    print(f"Risk level: {client.get_risk_level(analysis)}")
    
    # Get crisis-specific probes
    probes = client.get_probe_suggestions(analysis)
    for probe in probes:
        print(f"  - {probe}")
else:
    # Normal conversation flow
    probes = client.get_probe_suggestions(analysis)
    print(f"Suggested probes: {probes}")
```

---

## Rate Limiting

Currently, no rate limiting is implemented. For production use, consider implementing rate limiting based on your requirements.

---

## Support

For issues or questions:
- Check the integration guide: `docs/INTEGRATION_GUIDE.md`
- Review test examples: `tests/services/cultural-context/`
- Contact: Development Team

---

**Last Updated**: January 12, 2026  
**API Version**: 2.0  
**Service Version**: 1.0.0
