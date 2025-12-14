# Vector Database Setup Guide

This guide explains how to configure vector database integration for the Cultural Context Service's RAG (Retrieval-Augmented Generation) functionality.

## Overview

The Cultural Context Service supports two vector database options:
1. **Pinecone** (recommended for production)
2. **Weaviate** (alternative option)
3. **In-memory fallback** (default when no vector DB is configured)

When a vector database is not configured, the service automatically falls back to keyword-based search, which still provides functional cultural context retrieval.

## Pinecone Setup

### Prerequisites

1. Create a Pinecone account at [https://www.pinecone.io](https://www.pinecone.io)
2. Obtain your API key from the Pinecone dashboard
3. Choose a cloud region (recommended: `us-east-1` or `eu-west-1`)

### Configuration Steps

1. **Set Environment Variables**

   Add the following to your `.env` file or environment:

   ```bash
   PINECONE_API_KEY=your-pinecone-api-key-here
   PINECONE_INDEX_NAME=cultural-context
   ```

2. **Create Pinecone Index**

   The service will automatically check if the index exists. If it doesn't exist, you can create it manually:

   ```python
   from pinecone import Pinecone, ServerlessSpec
   
   pc = Pinecone(api_key="your-api-key")
   
   pc.create_index(
       name="cultural-context",
       dimension=384,  # Dimension depends on embedding model (default: 384 for sentence-transformers)
       metric="cosine",
       spec=ServerlessSpec(
           cloud="aws",
           region="us-east-1"
       )
   )
   ```

   Or use the Pinecone web console to create the index.

3. **Verify Configuration**

   The service will automatically detect Pinecone configuration on startup. Check the health endpoint:

   ```bash
   curl http://localhost:8000/health
   ```

   The response should include:
   ```json
   {
     "vector_db": {
       "vector_db_type": "pinecone",
       "connected": true,
       "embedding_service_available": true,
       "indexes": ["cultural-context"]
     }
   }
   ```

### Indexing Knowledge Base

Once configured, index your cultural knowledge base:

```bash
curl -X POST http://localhost:8000/index-kb?clear_existing=true \
  -H "Authorization: Bearer your-token"
```

This will:
- Load entries from `data/kb.json`
- Generate embeddings for each entry
- Store vectors in Pinecone index
- Return indexing statistics

## Weaviate Setup

### Prerequisites

1. Set up a Weaviate instance (cloud or self-hosted)
2. Obtain your Weaviate URL and API key (if using cloud)

### Configuration Steps

1. **Set Environment Variables**

   Add the following to your `.env` file:

   ```bash
   WEAVIATE_URL=https://your-cluster.weaviate.network
   WEAVIATE_API_KEY=your-weaviate-api-key
   ```

   For self-hosted Weaviate without authentication:

   ```bash
   WEAVIATE_URL=http://localhost:8080
   ```

2. **Create Collection**

   The service will automatically create the `CulturalContext` collection on first use. The collection schema includes:

   - `text` (text): The cultural context text
   - `keywords` (text[]): Keywords for the entry
   - `language` (text): Language code (en, sw, etc.)
   - `region` (text): Region identifier (east_africa, etc.)

3. **Verify Configuration**

   Check the health endpoint to verify Weaviate connection:

   ```bash
   curl http://localhost:8000/health
   ```

   The response should include:
   ```json
   {
     "vector_db": {
       "vector_db_type": "weaviate",
       "connected": true,
       "embedding_service_available": true
     }
   }
   ```

## In-Memory Fallback

If neither Pinecone nor Weaviate is configured, the service automatically uses an in-memory vector store. This is suitable for:

- Development and testing
- Small-scale deployments
- Environments where external services are not available

**Limitations of in-memory fallback:**
- Vectors are lost on service restart
- Not suitable for production at scale
- Limited to single-instance deployments

**When in-memory is used:**
- No environment variables are set
- Vector DB connection fails
- Embedding service is unavailable

The service will still function using keyword-based search as a fallback.

## Embedding Service

The RAG service uses an embedding service to generate vector representations of text. The default implementation uses sentence-transformers models.

### Default Embedding Model

- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimension**: 384
- **Language**: Multilingual (supports English and Swahili)

### Custom Embedding Model

To use a different embedding model, modify `services/embeddings.py`:

```python
from sentence_transformers import SentenceTransformer

# Use a different model
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
```

## Environment Variables Summary

### Required for Pinecone
```bash
PINECONE_API_KEY=your-api-key
PINECONE_INDEX_NAME=cultural-context  # Optional, defaults to "cultural-context"
```

### Required for Weaviate
```bash
WEAVIATE_URL=https://your-cluster.weaviate.network
WEAVIATE_API_KEY=your-api-key  # Optional for self-hosted
```

### Optional
```bash
USE_RAG=true  # Enable/disable RAG (default: true)
```

## Example .env File

```bash
# Vector Database Configuration
# Choose one: Pinecone OR Weaviate (or neither for in-memory fallback)

# Option 1: Pinecone
PINECONE_API_KEY=pc-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
PINECONE_INDEX_NAME=cultural-context

# Option 2: Weaviate
# WEAVIATE_URL=https://your-cluster.weaviate.network
# WEAVIATE_API_KEY=your-api-key

# RAG Settings
USE_RAG=true

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/resonaai
```

## Troubleshooting

### Pinecone Connection Issues

1. **Verify API Key**: Check that `PINECONE_API_KEY` is set correctly
2. **Check Index Exists**: Ensure the index name matches `PINECONE_INDEX_NAME`
3. **Verify Region**: Make sure your Pinecone account has access to the specified region
4. **Check Network**: Ensure the service can reach Pinecone API (check firewall rules)

### Weaviate Connection Issues

1. **Verify URL**: Check that `WEAVIATE_URL` is correct and accessible
2. **Check Authentication**: Verify API key if using Weaviate Cloud
3. **Verify Collection**: Ensure the `CulturalContext` collection can be created
4. **Check Network**: Ensure the service can reach Weaviate instance

### Embedding Service Issues

1. **Model Download**: First run may take time to download the embedding model
2. **Memory**: Ensure sufficient memory for the embedding model (~500MB)
3. **Dependencies**: Verify `sentence-transformers` is installed

### Fallback Behavior

If vector DB is unavailable, the service will:
1. Log a warning message
2. Fall back to keyword-based search
3. Continue to function normally (with reduced semantic search capability)

## Performance Considerations

### Pinecone
- **Latency**: ~50-100ms per query (depending on region)
- **Throughput**: High (scales automatically)
- **Cost**: Pay-per-use pricing model

### Weaviate
- **Latency**: ~20-50ms per query (self-hosted) or ~50-100ms (cloud)
- **Throughput**: High (depends on instance size)
- **Cost**: Self-hosted (infrastructure) or cloud pricing

### In-Memory
- **Latency**: ~5-10ms per query
- **Throughput**: Limited by single instance
- **Cost**: No additional cost (but not production-ready)

## Best Practices

1. **Production**: Use Pinecone or Weaviate for production deployments
2. **Development**: In-memory fallback is fine for local development
3. **Indexing**: Re-index knowledge base after major updates
4. **Monitoring**: Monitor vector DB health via `/health` endpoint
5. **Backup**: Consider backing up vector indexes for disaster recovery

## Additional Resources

- [Pinecone Documentation](https://docs.pinecone.io/)
- [Weaviate Documentation](https://weaviate.io/developers/weaviate)
- [Sentence Transformers Documentation](https://www.sbert.net/)

