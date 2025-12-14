# API Configuration Guide

This guide explains how to configure external API integrations for the ResonaAI platform.

## Overview

ResonaAI integrates with several external services for:
- **OpenAI**: GPT-4 conversation engine
- **Azure Cognitive Services**: Speech-to-text and emotion analysis
- **Hume AI**: Advanced emotion detection
- **Twilio**: Emergency alerts and notifications
- **Vector Databases**: RAG (Retrieval-Augmented Generation) for cultural context

## Configuration

All API keys and credentials are configured via environment variables. See `config.env.example` for the complete list.

### Environment Variables

Copy `config.env.example` to `.env` and fill in your API keys:

```bash
cp config.env.example .env
```

## Required API Keys

### 1. OpenAI API

**Purpose**: GPT-4 integration for conversation engine

**Required Variable**: `OPENAI_API_KEY`

**Setup**:
1. Sign up at https://platform.openai.com
2. Create an API key in your account settings
3. Add to `.env`:
   ```
   OPENAI_API_KEY=sk-...
   ```

**Usage**: Used by `apps/backend/services/conversation-engine/services/gpt_service.py`

**Testing**:
```bash
curl -X POST http://localhost:8000/conversation/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "user_id": "test-user"}'
```

---

### 2. Azure Cognitive Services

**Purpose**: Speech-to-text and emotion analysis

**Required Variables**:
- `AZURE_SPEECH_KEY`: Azure Speech Service API key
- `AZURE_SPEECH_REGION`: Azure region (e.g., `eastus`)
- `AZURE_COGNITIVE_SERVICES_KEY`: Azure Cognitive Services API key
- `AZURE_COGNITIVE_SERVICES_ENDPOINT`: Azure Cognitive Services endpoint URL

**Setup**:
1. Create Azure account at https://azure.microsoft.com
2. Create Speech Services resource
3. Create Cognitive Services resource
4. Get API keys from Azure Portal
5. Add to `.env`:
   ```
   AZURE_SPEECH_KEY=your-speech-key
   AZURE_SPEECH_REGION=eastus
   AZURE_COGNITIVE_SERVICES_KEY=your-cognitive-key
   AZURE_COGNITIVE_SERVICES_ENDPOINT=https://your-region.api.cognitive.microsoft.com
   ```

**Usage**: 
- Speech-to-text: `apps/backend/services/speech-processing/`
- Emotion analysis: `apps/backend/services/emotion-analysis/services/azure_integration.py`

---

### 3. Hume AI

**Purpose**: Advanced emotion detection from voice

**Required Variable**: `HUME_AI_API_KEY`

**Setup**:
1. Sign up at https://www.hume.ai
2. Get API key from dashboard
3. Add to `.env`:
   ```
   HUME_AI_API_KEY=your-hume-api-key
   ```

**Usage**: `apps/backend/services/emotion-analysis/services/hume_integration.py`

**Note**: Hume AI is optional. The system will work with basic emotion detection if not configured.

---

### 4. Twilio

**Purpose**: Emergency SMS/voice alerts for crisis situations

**Required Variables**:
- `TWILIO_ACCOUNT_SID`: Twilio account SID
- `TWILIO_AUTH_TOKEN`: Twilio authentication token
- `TWILIO_PHONE_NUMBER`: Twilio phone number (format: +1234567890)

**Setup**:
1. Sign up at https://www.twilio.com
2. Get Account SID and Auth Token from dashboard
3. Purchase a phone number
4. Add to `.env`:
   ```
   TWILIO_ACCOUNT_SID=AC...
   TWILIO_AUTH_TOKEN=your-auth-token
   TWILIO_PHONE_NUMBER=+1234567890
   ```

**Usage**: `apps/backend/services/crisis-detection/` (alert service)

**Testing**:
```python
from twilio.rest import Client

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
message = client.messages.create(
    to="+1234567890",
    from_=TWILIO_PHONE_NUMBER,
    body="Test alert"
)
```

---

### 5. Vector Database (RAG)

**Purpose**: Semantic search for cultural context service using vector databases

**Option A: Pinecone (Recommended)**

**Required Variables**:
- `PINECONE_API_KEY`: Pinecone API key
- `PINECONE_INDEX_NAME`: Index name (optional, defaults to `cultural-context`)

**Important**: `PINECONE_ENVIRONMENT` is **deprecated** in Pinecone SDK v5+. The new API automatically determines the environment based on your API key. If you have `PINECONE_ENVIRONMENT` in your config, it will be ignored.

**Setup**:
1. Sign up at https://www.pinecone.io
2. Get API key from the Pinecone console
3. Add to `.env`:
   ```
   PINECONE_API_KEY=your-pinecone-key
   PINECONE_INDEX_NAME=cultural-context
   ```
4. The index will be **automatically created** on first startup with the correct dimension based on your embedding service (OpenAI: 1536, sentence-transformers: 384)

**Option B: Weaviate (Self-hosted option)**

**Required Variables**:
- `WEAVIATE_URL`: Weaviate instance URL (with protocol, e.g., `https://`)
- `WEAVIATE_API_KEY`: Weaviate API key (optional, only if authentication is enabled)

**Setup**:
1. Set up Weaviate instance (cloud at https://console.weaviate.cloud or self-hosted)
2. Get URL and API key (if using authentication)
3. Add to `.env`:
   ```
   WEAVIATE_URL=https://your-instance.weaviate.network
   WEAVIATE_API_KEY=your-weaviate-key
   ```
4. The schema will be **automatically created** on first startup

**Knowledge Base Indexing Configuration**:
- `AUTO_INDEX_KB`: Enable/disable automatic indexing on startup (default: `true`)
- `KB_INDEX_BATCH_SIZE`: Batch size for indexing (default: `100`)
- `USE_RAG`: Enable/disable RAG-based retrieval (default: `true`)

**Auto-Indexing Behavior**:
- When the Cultural Context Service starts, it automatically:
  1. Initializes the vector database connection
  2. Creates the index/schema if it doesn't exist
  3. Loads the knowledge base from `data/kb.json`
  4. Indexes all entries into the vector database
  5. Logs progress and statistics

**Manual Re-indexing**:
To manually trigger re-indexing, use the endpoint:
```bash
POST /index-kb?clear_existing=true
```

This allows you to:
- Re-index the knowledge base after updates
- Clear and rebuild the index (`clear_existing=true`)
- Check indexing status and statistics

**Usage**: `apps/backend/services/cultural-context/services/rag_service.py`

**Fallback**: RAG is optional. The system gracefully falls back to keyword-based search if:
- No vector database is configured
- Vector database connection fails
- Embedding service is unavailable

**Health Check**: The `/health` endpoint includes vector database status:
```json
{
  "status": "healthy",
  "service": "cultural-context",
  "db_connected": true,
  "vector_db": {
    "vector_db_type": "pinecone",
    "connected": true,
    "embedding_service_available": true
  }
}
```

---

## Email Configuration

**Purpose**: Email verification and notifications

**Required Variables**:
- `SMTP_HOST`: SMTP server hostname (default: `smtp.gmail.com`)
- `SMTP_PORT`: SMTP port (default: `587`)
- `SMTP_USER`: SMTP username (your email)
- `SMTP_PASSWORD`: SMTP password or app password
- `FROM_EMAIL`: From email address
- `BASE_URL`: Base URL for verification links

**Setup**:
1. For Gmail: Use app password (not regular password)
   - Enable 2FA
   - Generate app password at https://myaccount.google.com/apppasswords
2. Add to `.env`:
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   FROM_EMAIL=noreply@resona.ai
   BASE_URL=https://resona.ai
   ```

**Usage**: `apps/backend/gateway/services/email_service.py`

---

## Testing API Integrations

### Test OpenAI

```bash
# Test conversation engine
curl -X POST http://localhost:8000/conversation/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "user_id": "test-user",
    "emotion": "neutral"
  }'
```

### Test Azure Speech

```bash
# Test speech-to-text
curl -X POST http://localhost:8000/speech/transcribe \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "audio=@test-audio.wav"
```

### Test Twilio

```python
# Test SMS sending
from twilio.rest import Client
import os

client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

message = client.messages.create(
    to="+1234567890",
    from_=os.getenv("TWILIO_PHONE_NUMBER"),
    body="Test alert from ResonaAI"
)
print(f"Message SID: {message.sid}")
```

---

## Security Best Practices

1. **Never commit API keys to version control**
   - Use `.env` file (already in `.gitignore`)
   - Use environment variables in production
   - Use secrets management (AWS Secrets Manager, Azure Key Vault, etc.)

2. **Rotate API keys regularly**
   - Set up key rotation schedule
   - Monitor API usage for anomalies

3. **Use least privilege**
   - Only grant necessary permissions
   - Use separate keys for different environments

4. **Monitor API usage**
   - Set up billing alerts
   - Monitor rate limits
   - Track API errors

---

## Troubleshooting

### OpenAI API Errors

**Error**: `Invalid API key`
- Check that `OPENAI_API_KEY` is set correctly
- Verify key has not expired
- Check account billing status

**Error**: `Rate limit exceeded`
- Implement exponential backoff
- Check usage limits in OpenAI dashboard

### Azure API Errors

**Error**: `401 Unauthorized`
- Verify API keys are correct
- Check region matches endpoint
- Verify resource is active in Azure Portal

### Twilio Errors

**Error**: `Authentication failed`
- Verify Account SID and Auth Token
- Check phone number format (must include country code)
- Verify phone number is verified in Twilio

### Email Service Errors

**Error**: `SMTP authentication failed`
- For Gmail: Use app password, not regular password
- Check SMTP credentials
- Verify firewall allows SMTP connections

---

## Cost Estimation

Approximate monthly costs (varies by usage):

- **OpenAI GPT-4**: $0.03 per 1K input tokens, $0.06 per 1K output tokens
- **Azure Speech**: ~$1 per 1,000 audio minutes
- **Azure Cognitive Services**: ~$1 per 1,000 transactions
- **Hume AI**: Contact for pricing
- **Twilio**: ~$0.0075 per SMS, ~$0.013 per minute for voice
- **Pinecone**: Free tier available, paid plans start at $70/month
- **Weaviate**: Free tier available, paid plans vary

---

## Next Steps

1. Set up all required API keys
2. Test each integration individually
3. Monitor API usage and costs
4. Set up alerts for API failures
5. Document any custom configurations

---

**Last Updated**: December 2024  
**Maintained By**: ResonaAI Development Team

