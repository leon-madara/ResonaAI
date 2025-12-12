"""
Unit tests for Sync Service
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Store original working directory
original_cwd = os.getcwd()


class TestSyncService:
    """Test Sync Service endpoints"""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database"""
        # Create in-memory SQLite database
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        
        # Create sync_queue table
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE sync_queue (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    operation_type TEXT NOT NULL,
                    encrypted_data BLOB,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP,
                    retry_count INTEGER DEFAULT 0
                )
            """))
            conn.commit()
        
        return engine
    
    @pytest.fixture
    def client(self, mock_db):
        """Create test client with mocked database"""
        # Change to service directory for imports
        service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'services', 'sync-service'))
        old_cwd = os.getcwd()
        os.chdir(service_dir)
        
        try:
            # Add service directory to Python path
            if service_dir not in sys.path:
                sys.path.insert(0, service_dir)
            
            # Clear cached modules
            for mod_name in list(sys.modules.keys()):
                if mod_name in ['main'] or mod_name.startswith('main.'):
                    del sys.modules[mod_name]
            
            # Mock environment variable and engine before import
            with patch.dict(os.environ, {'DATABASE_URL': 'sqlite:///:memory:'}):
                with patch('main.create_engine', return_value=mock_db):
                    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mock_db)
                    with patch('main.sessionmaker', return_value=SessionLocal):
                        # Import after mocking
                        import importlib
                        if 'main' in sys.modules:
                            importlib.reload(sys.modules['main'])
                        else:
                            from main import app
                        yield TestClient(sys.modules['main'].app)
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
        assert data["service"] == "sync-service"
        # db_connected may be True or False depending on mock setup
        assert "db_connected" in data
    
    def test_upload_data(self, client, auth_token):
        """Test uploading data for synchronization"""
        request_data = {
            "user_id": "test-user-123",
            "operation_type": "conversation_sync",
            "data": {
                "conversation_id": "conv-123",
                "messages": [
                    {"id": "msg-1", "content": "Hello", "timestamp": "2025-12-12T10:00:00Z"}
                ]
            }
        }
        
        response = client.post(
            "/upload",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"
        assert data["stored"] is True
        assert "sync_id" in data
        assert "message" in data
        assert "timestamp" in data
    
    def test_upload_data_missing_user_id(self, client, auth_token):
        """Test upload with missing user_id"""
        request_data = {
            "operation_type": "conversation_sync",
            "data": {"test": "data"}
        }
        
        response = client.post(
            "/upload",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        # Should fail validation
        assert response.status_code == 422  # Validation error
    
    def test_upload_data_missing_operation_type(self, client, auth_token):
        """Test upload with missing operation_type"""
        request_data = {
            "user_id": "test-user-123",
            "data": {"test": "data"}
        }
        
        response = client.post(
            "/upload",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        # Should fail validation
        assert response.status_code == 422  # Validation error
    
    def test_upload_data_missing_data(self, client, auth_token):
        """Test upload with missing data"""
        request_data = {
            "user_id": "test-user-123",
            "operation_type": "conversation_sync"
        }
        
        response = client.post(
            "/upload",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        # Should fail validation
        assert response.status_code == 422  # Validation error
    
    def test_upload_data_unauthorized(self, client):
        """Test upload without authentication"""
        request_data = {
            "user_id": "test-user-123",
            "operation_type": "conversation_sync",
            "data": {"test": "data"}
        }
        
        response = client.post(
            "/upload",
            json=request_data
        )
        
        assert response.status_code == 403  # FastAPI HTTPBearer returns 403
    
    def test_upload_data_empty_data(self, client, auth_token):
        """Test upload with empty data"""
        request_data = {
            "user_id": "test-user-123",
            "operation_type": "conversation_sync",
            "data": {}
        }
        
        response = client.post(
            "/upload",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        # Should still succeed (empty data is valid)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"
    
    def test_upload_data_different_operation_types(self, client, auth_token):
        """Test upload with different operation types"""
        operation_types = [
            "conversation_sync",
            "emotion_data_sync",
            "baseline_update",
            "user_preference_sync"
        ]
        
        for op_type in operation_types:
            request_data = {
                "user_id": "test-user-123",
                "operation_type": op_type,
                "data": {"test": "data"}
            }
            
            response = client.post(
                "/upload",
                json=request_data,
                headers={"Authorization": auth_token}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "queued"
            assert data["stored"] is True
    
    def test_upload_data_large_payload(self, client, auth_token):
        """Test upload with large data payload"""
        large_data = {
            "messages": [{"id": f"msg-{i}", "content": f"Message {i}"} for i in range(100)]
        }
        
        request_data = {
            "user_id": "test-user-123",
            "operation_type": "conversation_sync",
            "data": large_data
        }
        
        response = client.post(
            "/upload",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"
        assert data["stored"] is True

