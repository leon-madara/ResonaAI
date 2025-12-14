"""
Unit tests for Sync Service
"""

import pytest
import sys
import os
import uuid
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
        
        # Create minimal tables needed for sync processing (SQLite compatible)
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE users (
                    id TEXT PRIMARY KEY,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("""
                CREATE TABLE conversations (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("""
                CREATE TABLE messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    encrypted_content BLOB NOT NULL,
                    emotion_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
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
            conn.execute(text("""
                CREATE TABLE emotion_history (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    conversation_id TEXT,
                    message_id TEXT,
                    emotion_type TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    voice_emotion TEXT,
                    text_sentiment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("""
                CREATE TABLE user_baselines (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    baseline_type TEXT NOT NULL,
                    baseline_value TEXT NOT NULL,
                    session_count INTEGER DEFAULT 0,
                    established_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("""
                CREATE TABLE user_preferences (
                    user_id TEXT PRIMARY KEY,
                    preferences TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
        
        # Seed a test user (UUID-like, matches service validation).
        with engine.connect() as conn:
            test_user_id = str(uuid.uuid4())
            conn.execute(text("INSERT INTO users (id, email) VALUES (:id, :email)"), {"id": test_user_id, "email": "test@example.com"})
            conn.commit()
        engine.test_user_id = test_user_id  # attach for fixtures

        return engine
    
    @pytest.fixture
    def client(self, mock_db):
        """Create test client with mocked database and Celery"""
        # Change to service directory for imports
        service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'apps', 'backend', 'services', 'sync-service'))
        old_cwd = os.getcwd()
        os.chdir(service_dir)
        
        try:
            # Add service directory to Python path
            if service_dir not in sys.path:
                sys.path.insert(0, service_dir)
            
            # Clear cached modules
            modules_to_remove = []
            for mod_name in list(sys.modules.keys()):
                if mod_name in ['main'] or mod_name.startswith('main.') or \
                   mod_name.startswith('workers.') or mod_name == 'celery':
                    modules_to_remove.append(mod_name)
            for mod in modules_to_remove:
                if mod in sys.modules:
                    del sys.modules[mod]
            
            # Mock Celery before importing main
            mock_celery = Mock()
            mock_celery_app = Mock()
            mock_celery_app.send_task = Mock(return_value=Mock(id='test-task-id'))
            mock_celery.Celery = Mock(return_value=mock_celery_app)
            
            # Mock celery_app module
            mock_celery_module = Mock()
            mock_celery_module.celery_app = mock_celery_app
            
            # Mock sync_tasks module
            mock_sync_tasks_module = Mock()
            mock_sync_tasks_module.process_sync_operation = Mock()
            
            # Set environment variable to use SQLite before import
            with patch.dict(os.environ, {'DATABASE_URL': 'sqlite:///:memory:'}), \
                 patch.dict('sys.modules', {
                     'celery': mock_celery,
                     'workers.celery_app': mock_celery_module,
                     'workers.sync_tasks': mock_sync_tasks_module
                 }), \
                 patch('sqlalchemy.create_engine', return_value=mock_db):
                
                # Create SessionLocal with mock_db
                TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mock_db)
                
                # Import main module
                from main import app

                # Expose seeded test user id to tests
                app.state.test_user_id = getattr(mock_db, "test_user_id", None)
                
                # Patch SessionLocal in main module if it exists
                if hasattr(app, 'SessionLocal'):
                    with patch.object(app, 'SessionLocal', TestSessionLocal):
                        yield TestClient(app)
                else:
                    yield TestClient(app)
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
            "user_id": client.app.state.test_user_id,
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
        """Test upload with minimal required data"""
        request_data = {
            "user_id": client.app.state.test_user_id,
            "operation_type": "conversation_sync",
            "data": {
                "conversation_id": "conv-123",
                "messages": []  # Empty messages list is valid
            }
        }
        
        response = client.post(
            "/upload",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        # Should succeed with minimal required fields
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"
    
    def test_upload_data_different_operation_types(self, client, auth_token):
        """Test upload with different operation types"""
        test_cases = [
            {
                "operation_type": "conversation_sync",
                "data": {
                    "conversation_id": "conv-123",
                    "messages": [{"id": "msg-1", "content": "Hello"}]
                }
            },
            {
                "operation_type": "emotion_data_sync",
                "data": {
                    "emotion_data": [{"emotion": "happy", "confidence": 0.8}]
                }
            },
            {
                "operation_type": "baseline_update",
                "data": {
                    "baseline_data": {"baseline_type": "voice", "pitch_mean": 150.0, "session_count": 3}
                }
            },
            {
                "operation_type": "user_preference_sync",
                "data": {
                    "preferences": {"theme": "dark", "language": "en"}
                }
            }
        ]
        
        for test_case in test_cases:
            request_data = {
                "user_id": client.app.state.test_user_id,
                "operation_type": test_case["operation_type"],
                "data": test_case["data"]
            }
            
            response = client.post(
                "/upload",
                json=request_data,
                headers={"Authorization": auth_token}
            )
            
            assert response.status_code == 200, f"Failed for {test_case['operation_type']}: {response.text}"
            data = response.json()
            assert data["status"] == "queued"
            assert data["stored"] is True
    
    def test_upload_data_large_payload(self, client, auth_token):
        """Test upload with large data payload"""
        large_data = {
            "conversation_id": "conv-large",
            "messages": [{"id": f"msg-{i}", "content": f"Message {i}"} for i in range(100)]
        }
        
        request_data = {
            "user_id": client.app.state.test_user_id,
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

