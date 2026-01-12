#!/usr/bin/env python3
"""
Test Pinecone connection and verify setup
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_pinecone_connection():
    """Test Pinecone connection and configuration"""
    
    print("=" * 60)
    print("🔍 Testing Pinecone Connection")
    print("=" * 60)
    
    # Check environment variables
    print("\n1️⃣ Checking Environment Variables...")
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "cultural-context")
    
    if not api_key:
        print("❌ PINECONE_API_KEY not found in environment")
        print("   Please set it in your .env file")
        return False
    
    print(f"✅ PINECONE_API_KEY: {api_key[:10]}...{api_key[-4:]}")
    print(f"✅ PINECONE_INDEX_NAME: {index_name}")
    
    # Test Pinecone import
    print("\n2️⃣ Testing Pinecone Import...")
    try:
        from pinecone import Pinecone, ServerlessSpec
        print(f"✅ Pinecone imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Pinecone: {e}")
        print("   Run: pip install pinecone-client")
        return False
    
    # Initialize Pinecone
    print("\n3️⃣ Initializing Pinecone Client...")
    try:
        pc = Pinecone(api_key=api_key)
        print("✅ Pinecone client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Pinecone: {e}")
        return False
    
    # List indexes
    print("\n4️⃣ Listing Available Indexes...")
    try:
        indexes = pc.list_indexes()
        print(f"✅ Found {len(indexes)} index(es):")
        for idx in indexes:
            print(f"   - {idx.name}")
    except Exception as e:
        print(f"❌ Failed to list indexes: {e}")
        return False
    
    # Check if our index exists
    print(f"\n5️⃣ Checking for '{index_name}' Index...")
    index_names = [idx.name for idx in indexes]
    
    if index_name not in index_names:
        print(f"❌ Index '{index_name}' not found")
        print(f"\n📝 To create the index:")
        print(f"   1. Go to https://app.pinecone.io/")
        print(f"   2. Click 'Create Index'")
        print(f"   3. Use these settings:")
        print(f"      - Name: {index_name}")
        print(f"      - Dimensions: 384")
        print(f"      - Metric: cosine")
        print(f"      - Cloud: AWS")
        print(f"      - Region: us-east-1")
        return False
    
    print(f"✅ Index '{index_name}' exists")
    
    # Connect to index
    print(f"\n6️⃣ Connecting to Index...")
    try:
        index = pc.Index(index_name)
        print(f"✅ Connected to index '{index_name}'")
    except Exception as e:
        print(f"❌ Failed to connect to index: {e}")
        return False
    
    # Get index stats
    print(f"\n7️⃣ Getting Index Statistics...")
    try:
        stats = index.describe_index_stats()
        print(f"✅ Index Stats:")
        print(f"   - Total Vectors: {stats.total_vector_count}")
        print(f"   - Dimension: {stats.dimension}")
        
        if stats.total_vector_count == 0:
            print(f"\n⚠️  Warning: Index is empty (0 vectors)")
            print(f"   The knowledge base will be auto-indexed on service startup")
            print(f"   Or manually trigger: POST /index-kb")
    except Exception as e:
        print(f"❌ Failed to get index stats: {e}")
        return False
    
    # Test embedding model
    print(f"\n8️⃣ Testing Embedding Model...")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        test_text = "nimechoka"
        embedding = model.encode(test_text)
        print(f"✅ Embedding model loaded")
        print(f"   - Model: sentence-transformers/all-MiniLM-L6-v2")
        print(f"   - Embedding dimension: {len(embedding)}")
        
        if len(embedding) != 384:
            print(f"❌ Dimension mismatch! Expected 384, got {len(embedding)}")
            return False
    except Exception as e:
        print(f"❌ Failed to load embedding model: {e}")
        print("   Run: pip install sentence-transformers")
        return False
    
    # Test query
    print(f"\n9️⃣ Testing Vector Query...")
    try:
        if stats.total_vector_count > 0:
            results = index.query(
                vector=embedding.tolist(),
                top_k=3,
                include_metadata=True
            )
            print(f"✅ Query successful")
            print(f"   - Returned {len(results.matches)} results")
            if results.matches:
                print(f"   - Top match score: {results.matches[0].score:.4f}")
        else:
            print(f"⚠️  Skipping query test (index is empty)")
    except Exception as e:
        print(f"❌ Failed to query index: {e}")
        return False
    
    # Success!
    print("\n" + "=" * 60)
    print("✅ All Tests Passed!")
    print("=" * 60)
    print("\n🎉 Pinecone is configured correctly!")
    print("\n📝 Next Steps:")
    print("   1. Start the service: python main.py")
    print("   2. Test health endpoint: curl http://localhost:8000/health")
    print("   3. Test cultural context: curl http://localhost:8000/context?query=nimechoka")
    print("\n")
    
    return True


if __name__ == "__main__":
    success = test_pinecone_connection()
    sys.exit(0 if success else 1)
