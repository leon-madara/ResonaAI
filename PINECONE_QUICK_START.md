# ⚡ Pinecone Quick Start (5 Minutes)

Fast track to get Pinecone running for Cultural Context Service.

---

## 🎯 Quick Setup (3 Steps)

### 1. Create Pinecone Index (2 min)

1. Go to: https://app.pinecone.io/
2. Sign up / Log in
3. Click "Create Index"
4. Fill in:
   - **Name**: `cultural-context`
   - **Dimensions**: `384`
   - **Metric**: `cosine`
5. Click "Create"
6. Copy your API key from "API Keys" tab

### 2. Configure Environment (1 min)

Create `.env` file in `ResonaAI/` directory:

```bash
PINECONE_API_KEY=your-api-key-here
PINECONE_INDEX_NAME=cultural-context
AUTO_INDEX_KB=true
USE_RAG=true
```

### 3. Test Connection (2 min)

```bash
cd ResonaAI/apps/backend/services/cultural-context
python scripts/test_pinecone_connection.py
```

Should see: `✅ All Tests Passed!`

---

## 🚀 Start Service

```bash
cd apps/backend/services/cultural-context
python main.py
```

---

## ✅ Verify Setup

```bash
# Health check
curl http://localhost:8000/health

# Should show:
# "vector_db": {"connected": true, "vector_count": 22}
```

---

## 📚 Full Guide

For detailed instructions, see: [PINECONE_SETUP_GUIDE.md](./PINECONE_SETUP_GUIDE.md)

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key not found" | Check `.env` file has `PINECONE_API_KEY=...` |
| "Index not found" | Create index in Pinecone Console with name `cultural-context` |
| "Dimension mismatch" | Index must have 384 dimensions |
| "Vector count is 0" | Wait for auto-indexing or run: `POST /index-kb` |

---

## 🎉 Done!

Your Pinecone vector database is ready for cultural context queries!
