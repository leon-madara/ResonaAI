"""
Embedding service for cultural context RAG
Supports OpenAI embeddings and sentence-transformers as fallback
"""

import os
import logging
from typing import List, Optional
import numpy as np

logger = logging.getLogger(__name__)

# Try to import OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available, will use sentence-transformers")

# Try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available")


class EmbeddingService:
    """Service for generating text embeddings"""
    
    def __init__(self):
        """Initialize embedding service"""
        self.openai_client = None
        self.local_model = None
        self.embedding_model = None
        
        # Try OpenAI first
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if OPENAI_AVAILABLE and openai_api_key:
            try:
                self.openai_client = openai.OpenAI(api_key=openai_api_key)
                self.embedding_model = "text-embedding-3-small"  # Cost-effective model
                logger.info("Using OpenAI embeddings")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}")
        
        # Fallback to sentence-transformers
        if not self.openai_client and SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                # Use a multilingual model that supports English and Swahili
                self.local_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                self.embedding_model = "sentence-transformers"
                logger.info("Using sentence-transformers embeddings")
            except Exception as e:
                logger.warning(f"Failed to initialize sentence-transformers: {e}")
        
        if not self.openai_client and not self.local_model:
            logger.error("No embedding service available. RAG will not work.")
    
    def embed_text(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if service unavailable
        """
        if not text or not text.strip():
            return None
        
        # Try OpenAI first
        if self.openai_client:
            try:
                response = self.openai_client.embeddings.create(
                    model=self.embedding_model,
                    input=text
                )
                return response.data[0].embedding
            except Exception as e:
                logger.error(f"OpenAI embedding failed: {e}")
                return None
        
        # Fallback to sentence-transformers
        if self.local_model:
            try:
                embedding = self.local_model.encode(text, convert_to_numpy=True)
                return embedding.tolist()
            except Exception as e:
                logger.error(f"Sentence-transformers embedding failed: {e}")
                return None
        
        return None
    
    def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors (None for failed embeddings)
        """
        if not texts:
            return []
        
        # Try OpenAI first
        if self.openai_client:
            try:
                response = self.openai_client.embeddings.create(
                    model=self.embedding_model,
                    input=texts
                )
                return [item.embedding for item in response.data]
            except Exception as e:
                logger.error(f"OpenAI batch embedding failed: {e}")
                # Fall through to individual embeddings
                return [self.embed_text(text) for text in texts]
        
        # Fallback to sentence-transformers
        if self.local_model:
            try:
                embeddings = self.local_model.encode(texts, convert_to_numpy=True)
                return [emb.tolist() for emb in embeddings]
            except Exception as e:
                logger.error(f"Sentence-transformers batch embedding failed: {e}")
                return [self.embed_text(text) for text in texts]
        
        return [None] * len(texts)
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First embedding vector
            vec2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            
            dot_product = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
        except Exception as e:
            logger.error(f"Cosine similarity calculation failed: {e}")
            return 0.0
    
    def is_available(self) -> bool:
        """Check if embedding service is available"""
        return self.openai_client is not None or self.local_model is not None


# Global instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

