# 🚀 Pinecone Setup Guide for Cultural Context Service

This guide walks you through setting up Pinecone vector database for the Cultural Context Service.

---

## 📝 Prerequisites

- A Pinecone account (free tier available)
- Python 3.8+ installed
- Cultural Context Service files ready

---

## Phase 1: Create Pinecone Account & Index

### Step 1: Sign Up for Pinecone

1. Go to [https://www.pinecone.io](https://www.pinecone.io)
2. Click "Sign Up" or "Get Started Free"
3. Create account with email or Google/GitHub
4. Verify your email address
5. Complete onboarding (select "Starter" free plan)

### Step 2: Create Your Index

1. **Log in to Pinecone Console**: [https://app.pinecone.io/](https://app.pinecone.io/)

2. **Click "Create Index"** button

3. **Configure Index Settings**:
   ```
   Index Name:     cultural-context
   Dimensions:     384
   Metric:         cosine
   Cloud Provider: AWS
   Region:         us-east-1 (or closest to you)
   ```

4. **Why these settings?**
   - **384 dimensions**: Matches `sentence-transformers/all-MiniLM-L6-v2` model
   - **cosine metric**: Best for semantic similarity
   - **AWS us-east-1**: Free tier available, good global performance

5. **Click "Create Index"** and wait 1-2 minutes for provisioning

### Step 3: Get Your API Key

1. In Pinecone Console, click **"API Keys"** in left sidebar
2. You'll see your default API key
3. Click **"Copy"** to copy the key
4. **Keep this safe** - you'll need it in Phase 2

---

## Phase 2: Configure Environment

### Step 1: Create .env File

1. **Copy the template**:
   ```bash
   cd ResonaAI
   copy .env.pinecone.template .env
   ```

2. **Edit .env file** and replace `your-pinecone-api-key-here` with your actual API key:
   ```bash
   PINECONE_API_KEY=pcsk_abc123_YourActualKeyHere
   PINECONE_INDEX_NAME=cultural-context
   AUTO_INDEX_KB=true
   KB_INDEX_BATCH_SIZE=100
   USE_RAG=true
   ```

### Step 2: Verify Configuration

Your `.env` file should look like this:
```env
PINECONE_API_KEY=pcsk_abc123_YourActualKeyHere
PINECONE_INDEX_NAME=cultural-context
AUTO_INDEX_KB=true
KB_INDEX_BATCH_SIZE=100
USE_RAG=true
```

---

## Phase 3: Install Dependencies

### Step 1: Install Required Packages

```bash
cd apps/backend/services/cultural-context
pip install -r requirements.txt
```

This installs:
- `pinecone-client` - Pinecone SDK
- `sentence-transformers` - Embedding model
- `fastapi` - API framework
- Other dependencies

### Step 2: Verify Installation

```bash
python -c "import pinecone; print('Pinecone version:', pinecone.__version__)"
```

Should output: `Pinecone version: 5.x.x` (or similar)

---

## Phase 4: Test Connection

### Step 1: Start the Service

```bash
cd apps/backend/services/cultural-context
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Check Health Endpoint

Open a new terminal and run:

```bash
curl http://localhost:8000/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "service": "cultural-context",
  "version": "2.0",
  "vector_db": {
    "vector_db_type": "pinecone",
    "connected": true,
    "index_name": "cultural-context",
    "vector_count": 22
  },
  "knowledge_base": {
    "total_entries": 22,
    "categories": 17
  }
}
```

**Key indicators**:
- ✅ `"connected": true` - Pinecone is connected
- ✅ `"vector_count": 22` - Knowledge base is indexed
- ✅ `"total_entries": 22` - All KB entries loaded

### Step 3: Test Vector Search

```bash
curl -X GET "http://localhost:8000/context?query=nimechoka&language=sw" \
  -H "Authorization: Bearer test-token"
```

**Expected Response**: Should return relevant cultural context about "nimechoka" (I am tired)

---

## Phase 5: Verify Indexing

### Check Index Stats in Pinecone Console

1. Go to [https://app.pinecone.io/](https://app.pinecone.io/)
2. Click on your `cultural-context` index
3. You should see:
   - **Vector Count**: 22 (or more)
   - **Dimension**: 384
   - **Status**: Ready

### Test Semantic Search

```bash
curl -X POST "http://localhost:8000/cultural-analysis" \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I am feeling sawa but nimechoka",
    "language": "en",
    "emotion": "sad"
  }'
```

Should return cultural analysis with relevant context.

---

## 🎯 Success Checklist

- [ ] Pinecone account created
- [ ] Index `cultural-context` created with 384 dimensions
- [ ] API key obtained and saved
- [ ] `.env` file configured
- [ ] Dependencies installed
- [ ] Service starts without errors
- [ ] Health check shows `"connected": true`
- [ ] Vector count shows 22+ vectors
- [ ] Test queries return relevant results

---

## 🐛 Troubleshooting

### Issue: "Pinecone API key not found"

**Solution**: Check your `.env` file:
```bash
# Make sure this line exists and has your actual key
PINECONE_API_KEY=pcsk_abc123_YourActualKeyHere
```

### Issue: "Index not found"

**Solution**: Verify index name matches:
```bash
# In .env file
PINECONE_INDEX_NAME=cultural-context

# In Pinecone Console, check your index name
```

### Issue: "Dimension mismatch"

**Solution**: Your index must have 384 dimensions. If you created it with different dimensions:
1. Delete the index in Pinecone Console
2. Create a new one with 384 dimensions

### Issue: "Vector count is 0"

**Solution**: Auto-indexing might have failed. Manually trigger indexing:
```bash
curl -X POST "http://localhost:8000/index-kb?clear_existing=true" \
  -H "Authorization: Bearer test-token"
```

### Issue: Service won't start

**Solution**: Check logs for specific error. Common issues:
- Missing dependencies: `pip install -r requirements.txt`
- Port already in use: Change `SERVICE_PORT` in `.env`
- Invalid API key: Double-check your Pinecone API key

---

## 📚 Next Steps

After successful setup:

1. **Test the service** with various queries
2. **Add more content** (Day 2 tasks: 8 more KB entries)
3. **Write integration tests** (Day 3)
4. **Monitor performance** (Day 4)

---

## 🔗 Useful Links

- [Pinecone Console](https://app.pinecone.io/)
- [Pinecone Documentation](https://docs.pinecone.io/)
- [Cultural Context Service Docs](./apps/backend/services/cultural-context/docs/)
- [Integration Guide](./apps/backend/services/cultural-context/docs/INTEGRATION_GUIDE.md)

---

## 💡 Tips

- **Free Tier Limits**: 1 index, 100K vectors, 2GB storage (plenty for this project)
- **API Key Security**: Never commit `.env` to git (already in `.gitignore`)
- **Index Naming**: Use descriptive names if you plan multiple projects
- **Region Selection**: Choose region closest to your deployment for best performance
- **Monitoring**: Check Pinecone Console regularly for usage stats

---

**Need Help?** Check the troubleshooting section or review the service logs for detailed error messages.
