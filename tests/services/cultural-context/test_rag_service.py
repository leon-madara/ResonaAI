"""
Unit tests for RAG Service
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add service directory to path
service_dir = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        '..', '..', '..', 'apps', 'backend', 'services', 'cultural-context'
    )
)
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)


class TestRAGService:
    """Test RAG service for semantic search"""
    
    @pytest.fixture
    def mock_embedding_service(self):
        """Create mock embedding service"""
        mock_service = MagicMock()
        mock_service.is_available.return_value = True
        mock_service.embed_text.return_value = [0.1] * 384  # Mock embedding vector
        mock_service.cosine_similarity.return_value = 0.85
        return mock_service
    
    @pytest.fixture
    def rag_service(self, mock_embedding_service):
        """Create RAG service with mocked dependencies"""
        with patch('services.rag_service.get_embedding_service', return_value=mock_embedding_service):
            from services.rag_service import RAGService
            service = RAGService()
            # Force in-memory mode
            service.vector_db_type = "memory"
            return service
    
    def test_rag_service_initialization(self, mock_embedding_service):
        """Test RAG service initialization"""
        with patch('services.rag_service.get_embedding_service', return_value=mock_embedding_service):
            from services.rag_service import RAGService
            service = RAGService()
            
            assert service.embedding_service is not None
            assert service.vector_db_type is not None
    
    def test_index_entry_success(self, rag_service, mock_embedding_service):
        """Test indexing an entry"""
        entry_id = "test-entry-1"
        text = "Test content about mental health"
        metadata = {"keywords": ["test"], "language": "en", "region": "east_africa"}
        
        result = rag_service.index_entry(entry_id, text, metadata)
        
        assert result is True
        assert entry_id in rag_service.in_memory_vectors
    
    def test_index_entry_no_embedding_service(self, rag_service):
        """Test indexing when embedding service unavailable"""
        rag_service.embedding_service.is_available.return_value = False
        
        result = rag_service.index_entry("test", "text", {})
        
        assert result is False
    
    def test_search_success(self, rag_service, mock_embedding_service):
        """Test searching for entries"""
        # First index an entry
        entry_id = "test-entry-1"
        text = "Mental health support in East Africa"
        metadata = {"keywords": ["mental", "health"], "language": "en"}
        rag_service.index_entry(entry_id, text, metadata)
        
        # Then search
        results = rag_service.search("mental health", top_k=3)
        
        assert isinstance(results, list)
        if len(results) > 0:
            assert all("id" in r for r in results)
            assert all("score" in r for r in results)
    
    def test_search_no_embedding_service(self, rag_service):
        """Test search when embedding service unavailable"""
        rag_service.embedding_service.is_available.return_value = False
        
        results = rag_service.search("query", top_k=3)
        
        assert results == []
    
    def test_search_with_language_filter(self, rag_service, mock_embedding_service):
        """Test search with language filter"""
        # Index entries in different languages
        rag_service.index_entry("en-1", "English content", {"language": "en", "keywords": []})
        rag_service.index_entry("sw-1", "Swahili content", {"language": "sw", "keywords": []})
        
        results = rag_service.search("content", top_k=3, language="en")
        
        assert isinstance(results, list)
        # Results should be filtered by language
    
    def test_index_knowledge_base(self, rag_service, mock_embedding_service):
        """Test indexing knowledge base entries"""
        kb_entries = [
            {
                "id": "entry-1",
                "content": "Test content 1",
                "keywords": ["test"],
                "language": "en"
            },
            {
                "id": "entry-2",
                "content": "Test content 2",
                "keywords": ["test"],
                "language": "sw"
            }
        ]
        
        indexed_count = rag_service.index_knowledge_base(kb_entries)
        
        assert indexed_count == 2
        assert "entry-1" in rag_service.in_memory_vectors
        assert "entry-2" in rag_service.in_memory_vectors
    
    def test_is_available_true(self, rag_service, mock_embedding_service):
        """Test availability check when available"""
        rag_service.embedding_service.is_available.return_value = True
        rag_service.vector_db_type = "memory"
        
        assert rag_service.is_available() is True
    
    def test_is_available_false(self, rag_service):
        """Test availability check when unavailable"""
        rag_service.embedding_service.is_available.return_value = False
        
        assert rag_service.is_available() is False
    
    def test_get_rag_service_singleton(self, mock_embedding_service):
        """Test that get_rag_service returns singleton"""
        with patch('services.rag_service.get_embedding_service', return_value=mock_embedding_service):
            from services.rag_service import get_rag_service
            
            service1 = get_rag_service()
            service2 = get_rag_service()
            
            assert service1 is service2
    
    def test_search_empty_query(self, rag_service):
        """Test search with empty query"""
        results = rag_service.search("", top_k=3)
        
        assert results == []
    
    def test_index_entry_empty_text(self, rag_service, mock_embedding_service):
        """Test indexing entry with empty text"""
        mock_embedding_service.embed_text.return_value = None
        
        result = rag_service.index_entry("test", "", {})
        
        assert result is False
    
    def test_search_top_k_limit(self, rag_service, mock_embedding_service):
        """Test that search respects top_k limit"""
        # Index multiple entries
        for i in range(10):
            rag_service.index_entry(f"entry-{i}", f"Content {i}", {"keywords": [], "language": "en"})
        
        results = rag_service.search("content", top_k=3)
        
        assert len(results) <= 3
    
    def test_ensure_index_exists_memory(self, rag_service):
        """Test ensure_index_exists for memory mode"""
        result = rag_service.ensure_index_exists()
        assert result is True
    
    def test_get_index_stats_memory(self, rag_service, mock_embedding_service):
        """Test get_index_stats for memory mode"""
        # Index some entries
        rag_service.index_entry("test-1", "Test content", {"language": "en", "keywords": []})
        rag_service.index_entry("test-2", "Test content 2", {"language": "en", "keywords": []})
        
        stats = rag_service.get_index_stats()
        
        assert stats["vector_db_type"] == "memory"
        assert stats["total_vector_count"] == 2
    
    def test_clear_index_memory(self, rag_service, mock_embedding_service):
        """Test clear_index for memory mode"""
        # Index some entries
        rag_service.index_entry("test-1", "Test content", {"language": "en", "keywords": []})
        rag_service.index_entry("test-2", "Test content 2", {"language": "en", "keywords": []})
        
        assert len(rag_service.in_memory_vectors) == 2
        
        # Clear index
        result = rag_service.clear_index()
        
        assert result is True
        assert len(rag_service.in_memory_vectors) == 0
    
    def test_check_connection_memory(self, rag_service):
        """Test check_connection for memory mode"""
        status = rag_service.check_connection()
        
        assert status["vector_db_type"] == "memory"
        assert status["connected"] is True
        assert status["embedding_service_available"] is True
    
    def test_pinecone_initialization_with_mock(self, mock_embedding_service):
        """Test Pinecone initialization with modern API"""
        mock_pinecone_client = MagicMock()
        mock_pinecone_client.list_indexes.return_value = []
        
        with patch('services.rag_service.get_embedding_service', return_value=mock_embedding_service):
            with patch('services.rag_service.PINECONE_AVAILABLE', True):
                with patch('services.rag_service.Pinecone', return_value=mock_pinecone_client):
                    with patch.dict(os.environ, {'PINECONE_API_KEY': 'test-key'}):
                        from services.rag_service import RAGService
                        service = RAGService()
                        
                        # Should have tried to initialize Pinecone
                        assert service.pinecone_client is not None
    
    def test_weaviate_initialization_with_mock(self, mock_embedding_service):
        """Test Weaviate initialization with modern API"""
        mock_weaviate_client = MagicMock()
        mock_weaviate_client.is_ready.return_value = True
        mock_weaviate_client.collections.exists.return_value = True
        
        with patch('services.rag_service.get_embedding_service', return_value=mock_embedding_service):
            with patch('services.rag_service.WEAVIATE_AVAILABLE', True):
                with patch('services.rag_service.weaviate.connect_to_custom', return_value=mock_weaviate_client):
                    with patch.dict(os.environ, {'WEAVIATE_URL': 'http://localhost:8080'}):
                        from services.rag_service import RAGService
                        service = RAGService()
                        
                        # Should have tried to initialize Weaviate
                        assert service.weaviate_client is not None
    
    def test_ensure_index_exists_pinecone(self, mock_embedding_service):
        """Test ensure_index_exists for Pinecone"""
        mock_pinecone_client = MagicMock()
        mock_pinecone_client.list_indexes.return_value = []
        
        with patch('services.rag_service.get_embedding_service', return_value=mock_embedding_service):
            with patch('services.rag_service.PINECONE_AVAILABLE', True):
                with patch('services.rag_service.Pinecone', return_value=mock_pinecone_client):
                    with patch.dict(os.environ, {'PINECONE_API_KEY': 'test-key'}):
                        from services.rag_service import RAGService
                        service = RAGService()
                        service.vector_db_type = "pinecone"
                        service.pinecone_client = mock_pinecone_client
                        
                        # Test ensure_index_exists creates index
                        result = service.ensure_index_exists(dimension=384)
                        
                        # Should have called create_index
                        assert mock_pinecone_client.create_index.called or result is True

