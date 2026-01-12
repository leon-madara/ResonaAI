# 📋 Task 3: Pinecone Setup - Complete Guide

## 🎯 What You Need to Do

Set up Pinecone vector database to enable semantic search for cultural context.

---

## 📁 Files Created

✅ **Setup Guides**:
- `PINECONE_QUICK_START.md` - 5-minute quick start guide
- `PINECONE_SETUP_GUIDE.md` - Detailed step-by-step guide
- `.env.pinecone.template` - Environment configuration template

✅ **Testing Tools**:
- `apps/backend/services/cultural-context/scripts/test_pinecone_connection.py` - Connection test script

---

## 🚀 Choose Your Path

### Path A: Quick Setup (5 minutes) ⚡
**Best for**: Getting started fast

1. Read: `PINECONE_QUICK_START.md`
2. Follow 3 simple steps
3. Test and go!

### Path B: Detailed Setup (15 minutes) 📚
**Best for**: Understanding everything

1. Read: `PINECONE_SETUP_GUIDE.md`
2. Follow all 5 phases
3. Complete verification

---

## 📝 What You'll Do

### Phase 1: Pinecone Account (2 min)
- Sign up at pinecone.io
- Create index named `cultural-context`
- Get API key

### Phase 2: Environment Config (1 min)
- Copy `.env.pinecone.template` to `.env`
- Add your API key
- Save file

### Phase 3: Install Dependencies (2 min)
- Run: `pip install -r requirements.txt`
- Installs Pinecone SDK and embedding model

### Phase 4: Test Connection (2 min)
- Run: `python scripts/test_pinecone_connection.py`
- Verify all checks pass

### Phase 5: Start Service (1 min)
- Run: `python main.py`
- Test: `curl http://localhost:8000/health`

---

## ✅ Success Criteria

You're done when:
- [ ] Pinecone index `cultural-context` exists
- [ ] `.env` file has your API key
- [ ] Test script shows: `✅ All Tests Passed!`
- [ ] Health endpoint shows: `"connected": true`
- [ ] Vector count shows: `22` (or more)

---

## 🎯 Index Configuration

**Critical Settings** (must match exactly):
```
Name:       cultural-context
Dimensions: 384
Metric:     cosine
Cloud:      AWS
Region:     us-east-1 (or your preferred region)
```

**Why 384 dimensions?**
- Matches `sentence-transformers/all-MiniLM-L6-v2` model
- This model converts text to 384-dimensional vectors
- Mismatch will cause errors!

---

## 🔧 Environment Variables

**Required**:
```bash
PINECONE_API_KEY=your-api-key-here
PINECONE_INDEX_NAME=cultural-context
```

**Recommended**:
```bash
AUTO_INDEX_KB=true          # Auto-index on startup
USE_RAG=true                # Enable semantic search
KB_INDEX_BATCH_SIZE=100     # Batch size for indexing
```

---

## 🧪 Testing Commands

### Test Connection
```bash
cd apps/backend/services/cultural-context
python scripts/test_pinecone_connection.py
```

### Start Service
```bash
python main.py
```

### Health Check
```bash
curl http://localhost:8000/health
```

### Test Query
```bash
curl -X GET "http://localhost:8000/context?query=nimechoka&language=sw" \
  -H "Authorization: Bearer test-token"
```

---

## 🐛 Common Issues

### "API key not found"
**Fix**: Check `.env` file exists and has `PINECONE_API_KEY=...`

### "Index not found"
**Fix**: Create index in Pinecone Console with exact name `cultural-context`

### "Dimension mismatch"
**Fix**: Delete and recreate index with 384 dimensions

### "Vector count is 0"
**Fix**: Wait 30 seconds for auto-indexing, or manually trigger:
```bash
curl -X POST "http://localhost:8000/index-kb?clear_existing=true" \
  -H "Authorization: Bearer test-token"
```

---

## 📊 What Gets Indexed

When you start the service with `AUTO_INDEX_KB=true`:

1. **Knowledge Base** (22 entries):
   - Trauma/PTSD, Grief, Substance Abuse, etc.
   - Each entry becomes a vector in Pinecone

2. **Swahili Patterns** (28 patterns):
   - Not indexed in Pinecone (used for pattern matching)
   - Loaded into memory for fast lookup

3. **Total Vectors**: 22 (from kb.json)

---

## 🎓 How It Works

1. **User Query**: "I'm feeling nimechoka"
2. **Embedding**: Text → 384-dimensional vector
3. **Search**: Find similar vectors in Pinecone
4. **Results**: Return relevant cultural context
5. **Response**: AI uses context to provide culturally-aware support

---

## 💡 Tips

- **Free Tier**: 1 index, 100K vectors (plenty for this project)
- **Security**: `.env` is in `.gitignore` (never commit API keys!)
- **Performance**: us-east-1 region has best free tier performance
- **Monitoring**: Check Pinecone Console for usage stats

---

## 📚 Next Steps After Setup

Once Pinecone is working:

1. ✅ **Day 1 Complete**: You've finished all Day 1 tasks!
   - 22 KB entries ✅
   - 28 Swahili patterns ✅
   - Pinecone configured ✅

2. **Day 2**: Add more content
   - 8 more KB entries (→ 30 total)
   - 2 more patterns (→ 30 total)

3. **Day 3**: Integration testing
   - Test conversation engine
   - Test crisis detection
   - Test RAG service

---

## 🔗 Resources

- **Pinecone Console**: https://app.pinecone.io/
- **Pinecone Docs**: https://docs.pinecone.io/
- **Quick Start**: `PINECONE_QUICK_START.md`
- **Full Guide**: `PINECONE_SETUP_GUIDE.md`
- **Integration Guide**: `apps/backend/services/cultural-context/docs/INTEGRATION_GUIDE.md`

---

## ❓ Need Help?

1. Check troubleshooting section in `PINECONE_SETUP_GUIDE.md`
2. Run test script for detailed diagnostics
3. Check service logs for error messages
4. Verify all environment variables are set

---

**Ready to start?** Open `PINECONE_QUICK_START.md` for the fastest path! ⚡
