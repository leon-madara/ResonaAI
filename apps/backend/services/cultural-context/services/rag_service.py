"""
RAG (Retrieval-Augmented Generation) service for cultural context
Supports both vector database (Pinecone/Weaviate) and in-memory fallback
"""

import os
import logging
from typing import List, Dict, Any, Optional
import json

from .embeddings import get_embedding_service

logger = logging.getLogger(__name__)

# Try to import Pinecone (modern API v5+)
try:
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    logger.warning("Pinecone not available, will use fallback")
    # Provide placeholders so tests can patch these attributes even when deps are missing.
    Pinecone = None
    ServerlessSpec = None

# Try to import Weaviate (v4+)
try:
    import weaviate
    from weaviate.classes.init import Auth
    from weaviate.classes.config import Configure, Property, DataType
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False
    logger.warning("Weaviate not available, will use fallback")
    # Provide placeholders so tests can patch these attributes even when deps are missing.
    from types import SimpleNamespace
    weaviate = SimpleNamespace(connect_to_custom=None)
    Auth = None
    Configure = None
    Property = None
    DataType = None


class RAGService:
    """Service for semantic search and RAG"""
    
    def __init__(self):
        """Initialize RAG service"""
        self.vector_db_type = None
        self.pinecone_client = None
        self.pinecone_index = None
        self.weaviate_client = None
        self.embedding_service = get_embedding_service()
        self.in_memory_vectors: Dict[str, List[float]] = {}
        
        # Try Pinecone first (modern API - no environment needed)
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        if PINECONE_AVAILABLE and pinecone_api_key:
            try:
                self.pinecone_client = Pinecone(api_key=pinecone_api_key)
                index_name = os.getenv("PINECONE_INDEX_NAME", "cultural-context")
                
                # Check if index exists, get it if it does
                if index_name in [idx.name for idx in self.pinecone_client.list_indexes()]:
                    self.pinecone_index = self.pinecone_client.Index(index_name)
                    self.vector_db_type = "pinecone"
                    logger.info(f"Using Pinecone index '{index_name}' for vector storage")
                else:
                    logger.warning(f"Pinecone index '{index_name}' does not exist. Call ensure_index_exists() to create it.")
                    # Don't set vector_db_type yet - index needs to be created first
            except Exception as e:
                logger.warning(f"Failed to initialize Pinecone: {e}")
        
        # Try Weaviate (v4+ client)
        weaviate_url = os.getenv("WEAVIATE_URL")
        weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
        if WEAVIATE_AVAILABLE and weaviate_url and not self.vector_db_type:
            try:
                # Initialize Weaviate client with v4 API
                auth_config = Auth.api_key(weaviate_api_key) if weaviate_api_key else None
                self.weaviate_client = weaviate.connect_to_custom(
                    http_host=weaviate_url.replace("https://", "").replace("http://", ""),
                    http_port=443 if "https://" in weaviate_url else 80,
                    http_secure="https://" in weaviate_url,
                    grpc_host=weaviate_url.replace("https://", "").replace("http://", ""),
                    grpc_port=443 if "https://" in weaviate_url else 80,
                    grpc_secure="https://" in weaviate_url,
                    auth_credentials=auth_config
                )
                
                # Ensure schema exists
                self._ensure_weaviate_schema()
                
                self.vector_db_type = "weaviate"
                logger.info("Using Weaviate for vector storage")
            except Exception as e:
                logger.warning(f"Failed to initialize Weaviate: {e}")
        
        # Fallback to in-memory storage
        if not self.vector_db_type:
            self.vector_db_type = "memory"
            logger.info("Using in-memory vector storage (fallback)")
    
    def _ensure_weaviate_schema(self):
        """Ensure Weaviate schema exists for CulturalContext class"""
        if not self.weaviate_client:
            return
        
        try:
            # Check if collection exists
            if not self.weaviate_client.collections.exists("CulturalContext"):
                # Create collection with schema
                self.weaviate_client.collections.create(
                    name="CulturalContext",
                    properties=[
                        Property(name="text", data_type=DataType.TEXT),
                        Property(name="keywords", data_type=DataType.TEXT_ARRAY),
                        Property(name="language", data_type=DataType.TEXT),
                        Property(name="region", data_type=DataType.TEXT),
                    ],
                    vectorizer_config=Configure.Vectorizer.none()  # We provide our own vectors
                )
                logger.info("Created Weaviate CulturalContext schema")
        except Exception as e:
            logger.warning(f"Failed to ensure Weaviate schema: {e}")
    
    def ensure_index_exists(self, dimension: Optional[int] = None) -> bool:
        """
        Ensure Pinecone index exists, create if needed.
        
        Args:
            dimension: Embedding dimension (auto-detected if not provided)
            
        Returns:
            True if index exists or was created successfully
        """
        if self.vector_db_type == "pinecone" and self.pinecone_client:
            try:
                index_name = os.getenv("PINECONE_INDEX_NAME", "cultural-context")
                
                # Check if index exists
                if index_name in [idx.name for idx in self.pinecone_client.list_indexes()]:
                    if not self.pinecone_index:
                        self.pinecone_index = self.pinecone_client.Index(index_name)
                    return True
                
                # Detect dimension from embedding service if not provided
                if dimension is None:
                    # Generate a test embedding to detect dimension
                    test_embedding = self.embedding_service.embed_text("test")
                    if test_embedding:
                        dimension = len(test_embedding)
                    else:
                        logger.error("Cannot detect embedding dimension")
                        return False
                
                # Create serverless index (default for new Pinecone)
                logger.info(f"Creating Pinecone index '{index_name}' with dimension {dimension}")
                spec = None
                if ServerlessSpec is not None:
                    spec = ServerlessSpec(cloud="aws", region="us-east-1")  # Default region
                self.pinecone_client.create_index(
                    name=index_name,
                    dimension=dimension,
                    metric="cosine",
                    spec=spec
                )
                
                # Get the index client
                self.pinecone_index = self.pinecone_client.Index(index_name)
                logger.info(f"Successfully created Pinecone index '{index_name}'")
                return True
                
            except Exception as e:
                logger.error(f"Failed to ensure Pinecone index exists: {e}")
                return False
        
        return True  # For other vector DBs, assume ready
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get vector count and statistics from vector DB.
        
        Returns:
            Dictionary with stats (vector_count, etc.)
        """
        try:
            if self.vector_db_type == "pinecone" and self.pinecone_index:
                stats = self.pinecone_index.describe_index_stats()
                return {
                    "vector_db_type": "pinecone",
                    "total_vector_count": stats.get("total_vector_count", 0),
                    "dimension": stats.get("dimension", 0),
                    "index_fullness": stats.get("index_fullness", 0),
                    "namespaces": stats.get("namespaces", {})
                }
            
            elif self.vector_db_type == "weaviate" and self.weaviate_client:
                try:
                    collection = self.weaviate_client.collections.get("CulturalContext")
                    # Get aggregate count
                    result = collection.aggregate.over_all(total_count=True)
                    return {
                        "vector_db_type": "weaviate",
                        "total_vector_count": result.total_count if result else 0
                    }
                except:
                    return {"vector_db_type": "weaviate", "total_vector_count": 0}
            
            elif self.vector_db_type == "memory":
                return {
                    "vector_db_type": "memory",
                    "total_vector_count": len(self.in_memory_vectors)
                }
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
        
        return {"vector_db_type": self.vector_db_type or "unknown", "total_vector_count": 0}
    
    def clear_index(self, namespace: str = "") -> bool:
        """
        Clear all vectors from index (for testing/re-indexing).
        
        Args:
            namespace: Namespace to clear (Pinecone only)
            
        Returns:
            True if cleared successfully
        """
        try:
            if self.vector_db_type == "pinecone" and self.pinecone_index:
                self.pinecone_index.delete(delete_all=True, namespace=namespace)
                logger.info(f"Cleared Pinecone index namespace '{namespace}'")
                return True
            
            elif self.vector_db_type == "weaviate" and self.weaviate_client:
                collection = self.weaviate_client.collections.get("CulturalContext")
                collection.data.delete_many(where=None)  # Delete all
                logger.info("Cleared Weaviate collection")
                return True
            
            elif self.vector_db_type == "memory":
                self.in_memory_vectors.clear()
                logger.info("Cleared in-memory vectors")
                return True
                
        except Exception as e:
            logger.error(f"Failed to clear index: {e}")
            return False
        
        return False
    
    def check_connection(self) -> Dict[str, Any]:
        """
        Health check for vector DB connection.
        
        Returns:
            Dictionary with connection status
        """
        status = {
            "vector_db_type": self.vector_db_type,
            "connected": False,
            "embedding_service_available": self.embedding_service.is_available()
        }
        
        try:
            if self.vector_db_type == "pinecone" and self.pinecone_client:
                # Try to list indexes as a connection check
                indexes = self.pinecone_client.list_indexes()
                status["connected"] = True
                status["indexes"] = [idx.name for idx in indexes]
            
            elif self.vector_db_type == "weaviate" and self.weaviate_client:
                # Try to check if client is ready
                status["connected"] = self.weaviate_client.is_ready()
            
            elif self.vector_db_type == "memory":
                status["connected"] = True
                status["vector_count"] = len(self.in_memory_vectors)
        except Exception as e:
            status["error"] = str(e)
        
        return status
    
    def index_entry(self, entry_id: str, text: str, metadata: Dict[str, Any]) -> bool:
        """
        Index a knowledge base entry.
        
        Args:
            entry_id: Unique identifier for the entry
            text: Text content to index
            metadata: Additional metadata (keywords, language, etc.)
            
        Returns:
            True if indexed successfully
        """
        if not self.embedding_service.is_available():
            logger.warning("Embedding service not available, cannot index")
            return False
        
        embedding = self.embedding_service.embed_text(text)
        if not embedding:
            return False
        
        try:
            if self.vector_db_type == "pinecone" and self.pinecone_index:
                # Modern Pinecone API uses upsert with list of tuples
                self.pinecone_index.upsert(
                    vectors=[(entry_id, embedding, metadata)],
                    namespace=""  # Default namespace
                )
                return True
            
            elif self.vector_db_type == "weaviate" and self.weaviate_client:
                # Weaviate v4 uses collections API
                collection = self.weaviate_client.collections.get("CulturalContext")
                collection.data.insert(
                    properties={
                        "text": text,
                        "keywords": metadata.get("keywords", []),
                        "language": metadata.get("language", "en"),
                        "region": metadata.get("region", "east_africa")
                    },
                    vector=embedding,
                    uuid=entry_id
                )
                return True
            
            elif self.vector_db_type == "memory":
                self.in_memory_vectors[entry_id] = {
                    "embedding": embedding,
                    "text": text,
                    "metadata": metadata
                }
                return True
            
        except Exception as e:
            logger.error(f"Failed to index entry {entry_id}: {e}")
            return False
        
        return False
    
    def search(self, query: str, top_k: int = 3, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for relevant cultural context entries.
        
        Args:
            query: Search query
            top_k: Number of results to return
            language: Optional language filter
            
        Returns:
            List of relevant entries with scores
        """
        if not self.embedding_service.is_available():
            logger.warning("Embedding service not available, falling back to keyword search")
            return []
        
        query_embedding = self.embedding_service.embed_text(query)
        if not query_embedding:
            return []
        
        try:
            if self.vector_db_type == "pinecone" and self.pinecone_index:
                # Modern Pinecone API
                filter_dict = {"language": {"$eq": language}} if language else None
                results = self.pinecone_index.query(
                    vector=query_embedding,
                    top_k=top_k,
                    include_metadata=True,
                    filter=filter_dict,
                    namespace=""  # Default namespace
                )
                return [
                    {
                        "id": match["id"],
                        "score": match["score"],
                        "metadata": match.get("metadata", {})
                    }
                    for match in results.get("matches", [])
                ]
            
            elif self.vector_db_type == "weaviate" and self.weaviate_client:
                # Weaviate v4 uses collections API
                from weaviate.classes.query import Filter
                
                collection = self.weaviate_client.collections.get("CulturalContext")
                
                # Build filter if language specified
                where_filter = Filter.by_property("language").equal(language) if language else None
                
                # Query with near vector
                response = collection.query.near_vector(
                    near_vector=query_embedding,
                    limit=top_k,
                    filters=where_filter,
                    return_metadata=["distance"]
                )
                
                return [
                    {
                        "id": str(obj.uuid),
                        "score": 1 - obj.metadata.distance if obj.metadata and obj.metadata.distance else 0,  # Convert distance to similarity
                        "metadata": {
                            "text": obj.properties.get("text", ""),
                            "keywords": obj.properties.get("keywords", []),
                            "language": obj.properties.get("language", "")
                        }
                    }
                    for obj in response.objects
                ]
            
            elif self.vector_db_type == "memory":
                # Calculate similarity for all entries
                scored_entries = []
                for entry_id, entry_data in self.in_memory_vectors.items():
                    # Filter by language if specified
                    if language and entry_data["metadata"].get("language") != language:
                        continue
                    
                    similarity = self.embedding_service.cosine_similarity(
                        query_embedding,
                        entry_data["embedding"]
                    )
                    scored_entries.append({
                        "id": entry_id,
                        "score": similarity,
                        "metadata": entry_data["metadata"],
                        "text": entry_data["text"]
                    })
                
                # Sort by score and return top_k
                scored_entries.sort(key=lambda x: x["score"], reverse=True)
                return scored_entries[:top_k]
        
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
        
        return []
    
    def index_knowledge_base(self, kb_entries: List[Dict[str, Any]]) -> int:
        """
        Index all entries from knowledge base.
        
        Args:
            kb_entries: List of knowledge base entries
            
        Returns:
            Number of entries successfully indexed
        """
        indexed_count = 0
        for entry in kb_entries:
            entry_id = entry.get("id", str(hash(entry.get("content", ""))))
            text = entry.get("content", "")
            metadata = {
                "keywords": entry.get("keywords", []),
                "language": entry.get("language", "en"),
                "region": entry.get("region", "east_africa")
            }
            
            if self.index_entry(entry_id, text, metadata):
                indexed_count += 1
        
        logger.info(f"Indexed {indexed_count}/{len(kb_entries)} entries")
        return indexed_count
    
    def is_available(self) -> bool:
        """Check if RAG service is available"""
        return self.embedding_service.is_available() and self.vector_db_type is not None


# Global instance
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Get or create RAG service instance"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service

