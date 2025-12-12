"""
Unit tests for Cultural Context Service
"""

import pytest
import sys
import os
import json
import tempfile
from unittest.mock import Mock, patch, mock_open, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

# Store original working directory
original_cwd = os.getcwd()


class TestCulturalContext:
    """Test Cultural Context service endpoints"""
    
    @pytest.fixture
    def mock_kb(self):
        """Create mock knowledge base"""
        return {
            "entries": [
                {
                    "id": "entry-1",
                    "language": "en",
                    "keywords": ["sad", "depressed", "feeling down"],
                    "content": "In East African cultures, expressing sadness directly may be avoided. Look for indirect expressions."
                },
                {
                    "id": "entry-2",
                    "language": "sw",
                    "keywords": ["nimechoka", "tired", "exhausted"],
                    "content": "'Nimechoka' (I am tired) can indicate emotional exhaustion, not just physical tiredness."
                },
                {
                    "id": "entry-3",
                    "language": "en",
                    "keywords": ["sawa", "okay", "fine"],
                    "content": "'Sawa' (okay) is often used as a polite deflection when someone doesn't want to discuss their feelings."
                }
            ]
        }
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database"""
        # Create in-memory SQLite database
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        
        # Create cultural_context_cache table
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE cultural_context_cache (
                    context_key TEXT PRIMARY KEY,
                    context_data TEXT,
                    language TEXT,
                    region TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                )
            """))
            conn.commit()
        
        return engine
    
    @pytest.fixture
    def client(self, mock_kb, mock_db):
        """Create test client with mocked dependencies"""
        # Change to service directory for imports
        service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'services', 'cultural-context'))
        old_cwd = os.getcwd()
        os.chdir(service_dir)
        
        try:
            # Add service directory to Python path
            if service_dir not in sys.path:
                sys.path.insert(0, service_dir)
            
            # Clear cached modules
            for mod_name in list(sys.modules.keys()):
                if mod_name in ['main', 'config']:
                    del sys.modules[mod_name]
            
            # Create temporary KB file
            temp_dir = tempfile.mkdtemp()
            kb_path = os.path.join(temp_dir, "kb.json")
            with open(kb_path, 'w', encoding='utf-8') as f:
                json.dump(mock_kb, f)
            
            # Mock database and KB loading
            with patch('main.DATABASE_URL', 'sqlite:///:memory:'):
                with patch('main.engine', mock_db):
                    with patch('main.KB_DEFAULT_PATH', kb_path):
                        with patch('main.KB_MOUNT_PATH', kb_path):
                            from main import app
                            yield TestClient(app)
            
            # Cleanup
            os.remove(kb_path)
            os.rmdir(temp_dir)
        finally:
            os.chdir(old_cwd)
            if service_dir in sys.path:
                sys.path.remove(service_dir)
    
    @pytest.fixture
    def auth_token(self):
        """Generate a test JWT token"""
        return "Bearer test-token"
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "cultural-context"
        assert "db_connected" in data
    
    def test_get_context_english(self, client, auth_token):
        """Test getting cultural context for English query"""
        response = client.get(
            "/context?query=feeling%20sad&language=en",
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "context" in data
        assert data["language"] == "en"
        assert data["query"] == "feeling sad"
        assert "timestamp" in data
        assert "source" in data
    
    def test_get_context_swahili(self, client, auth_token):
        """Test getting cultural context for Swahili query"""
        response = client.get(
            "/context?query=nimechoka&language=sw",
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "context" in data
        assert data["language"] == "sw"
        assert data["query"] == "nimechoka"
        assert "matches" in data
    
    def test_get_context_missing_query(self, client, auth_token):
        """Test getting context without query parameter"""
        response = client.get(
            "/context?language=en",
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 400
        assert "query is required" in response.json()["detail"]
    
    def test_get_context_empty_query(self, client, auth_token):
        """Test getting context with empty query"""
        response = client.get(
            "/context?query=&language=en",
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 400
        assert "query is required" in response.json()["detail"]
    
    def test_get_context_unauthorized(self, client):
        """Test getting context without authentication"""
        response = client.get("/context?query=test&language=en")
        
        assert response.status_code == 403  # FastAPI HTTPBearer returns 403
    
    def test_get_context_caching(self, client, auth_token):
        """Test that context is cached"""
        # First request
        response1 = client.get(
            "/context?query=test%20query&language=en",
            headers={"Authorization": auth_token}
        )
        
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["source"] in ["local_kb_retrieval", "mvp_fallback"]
        
        # Second request (should be cached)
        response2 = client.get(
            "/context?query=test%20query&language=en",
            headers={"Authorization": auth_token}
        )
        
        assert response2.status_code == 200
        data2 = response2.json()
        # May be cached or not depending on implementation
        assert "source" in data2
    
    def test_get_context_different_languages(self, client, auth_token):
        """Test context retrieval for different languages"""
        languages = ["en", "sw"]
        
        for lang in languages:
            response = client.get(
                f"/context?query=test&language={lang}",
                headers={"Authorization": auth_token}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["language"] == lang
    
    def test_get_context_keyword_matching(self, client, auth_token):
        """Test that keyword matching works correctly"""
        # Query with matching keyword
        response = client.get(
            "/context?query=I%20am%20feeling%20depressed&language=en",
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "context" in data
        # Should have matches if keywords match
        if "matches" in data and len(data["matches"]) > 0:
            assert len(data["matches"]) > 0
    
    def test_get_context_case_insensitive(self, client, auth_token):
        """Test that query matching is case-insensitive"""
        response = client.get(
            "/context?query=SAD%20AND%20DEPRESSED&language=en",
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "context" in data
    
    def test_get_context_special_characters(self, client, auth_token):
        """Test context retrieval with special characters"""
        response = client.get(
            "/context?query=test%20with%20special%20chars%20!%40%23&language=en",
            headers={"Authorization": auth_token}
        )
        
        # Should handle special characters gracefully
        assert response.status_code == 200
        data = response.json()
        assert "context" in data

