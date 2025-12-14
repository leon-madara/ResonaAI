"""
Integration tests for Encrypted Storage Service
Tests encrypted storage integration with database tables and key rotation workflow
"""

import pytest
import sys
import os
import uuid
import base64
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from datetime import datetime, timezone
import httpx

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'apps', 'backend', 'gateway'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'apps', 'backend', 'services', 'encryption-service'))

# Store original working directory
original_cwd = os.getcwd()


class TestEncryptedStorageIntegration:
    """Integration tests for encrypted storage and key rotation"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for key file"""
        import tempfile
        import shutil
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def encryption_service_client(self, temp_dir):
        """Create test client for encryption service"""
        key_file = os.path.join(temp_dir, "master.key")
        
        # Get service directory
        service_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "..",
                "apps",
                "backend",
                "services",
                "encryption-service",
            )
        )
        
        old_cwd = os.getcwd()
        os.chdir(service_dir)
        
        if service_dir not in sys.path:
            sys.path.insert(0, service_dir)
        
        try:
            # Clear cached modules
            for mod_name in list(sys.modules.keys()):
                if mod_name.startswith('main') or mod_name.startswith('config'):
                    if 'encryption' in mod_name:
                        del sys.modules[mod_name]
            
            with patch('config.settings') as mock_settings:
                mock_settings.MASTER_KEY_FILE = key_file
                mock_settings.ADMIN_TOKEN = "test-admin-token"
                
                from main import app
                from fastapi.testclient import TestClient
                client = TestClient(app)
                
                # Store the encryption manager for later use
                from main import encryption_manager
                client.encryption_manager = encryption_manager
                
                yield client
        finally:
            os.chdir(old_cwd)
            if service_dir in sys.path:
                sys.path.remove(service_dir)
    
    @pytest.fixture
    def test_db(self):
        """Create test database session"""
        # Import database models
        import importlib.util
        
        gateway_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..',
            'apps', 'backend', 'gateway'
        )
        
        # Import database
        db_spec = importlib.util.spec_from_file_location(
            "database",
            os.path.join(gateway_path, "database.py")
        )
        if db_spec is None:
            # Try alternative path
            db_spec = importlib.util.spec_from_file_location(
                "database",
                os.path.join(gateway_path, "src", "database", "__init__.py")
            )
        
        if db_spec and db_spec.loader:
            db_module = importlib.util.module_from_spec(db_spec)
            db_spec.loader.exec_module(db_module)
            Base = db_module.Base
        else:
            # Create minimal Base if import fails
            from sqlalchemy.ext.declarative import declarative_base
            Base = declarative_base()
        
        # Create in-memory SQLite database
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        try:
            yield session
        finally:
            session.close()
            Base.metadata.drop_all(bind=engine)
    
    @pytest.fixture
    def test_user(self, test_db):
        """Create a test user"""
        import importlib.util
        
        gateway_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..',
            'apps', 'backend', 'gateway'
        )
        
        # Try to import User model
        try:
            models_spec = importlib.util.spec_from_file_location(
                "models",
                os.path.join(gateway_path, "models", "user.py")
            )
            if models_spec and models_spec.loader:
                models_module = importlib.util.module_from_spec(models_spec)
                models_spec.loader.exec_module(models_module)
                User = models_module.User
            else:
                # Create minimal User model
                from sqlalchemy import Column, String
                from sqlalchemy.dialects.postgresql import UUID
                from sqlalchemy.ext.declarative import declarative_base
                Base = declarative_base()
                
                class User(Base):
                    __tablename__ = "users"
                    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
                    email = Column(String(255))
                    password_hash = Column(String(255))
                    consent_version = Column(String(10))
                    is_anonymous = Column(String(5), default="false")
                    created_at = Column(String(50), default=lambda: datetime.now(timezone.utc).isoformat())
                    last_active = Column(String(50), default=lambda: datetime.now(timezone.utc).isoformat())
        except:
            # Create minimal User model
            from sqlalchemy import Column, String
            from sqlalchemy.ext.declarative import declarative_base
            Base = declarative_base()
            
            class User(Base):
                __tablename__ = "users"
                id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
                email = Column(String(255))
                password_hash = Column(String(255))
                consent_version = Column(String(10))
                is_anonymous = Column(String(5), default="false")
                created_at = Column(String(50), default=lambda: datetime.now(timezone.utc).isoformat())
                last_active = Column(String(50), default=lambda: datetime.now(timezone.utc).isoformat())
        
        user = User(
            id=str(uuid.uuid4()),
            email="test@example.com",
            password_hash="test_hash",
            consent_version="1.0",
            is_anonymous="false"
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        return user
    
    @pytest.fixture
    def encrypted_storage_service(self, encryption_service_client):
        """Create encrypted storage service with mocked HTTP client"""
        import importlib.util
        
        gateway_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..',
            'apps', 'backend', 'gateway'
        )
        
        # Import encrypted storage service
        storage_spec = importlib.util.spec_from_file_location(
            "encrypted_storage",
            os.path.join(gateway_path, "services", "encrypted_storage.py")
        )
        storage_module = importlib.util.module_from_spec(storage_spec)
        storage_spec.loader.exec_module(storage_module)
        EncryptedStorageService = storage_module.EncryptedStorageService
        
        # Get the encryption service URL (use test client's base URL)
        service_url = "http://test-encryption-service"
        
        # Create service with mocked client that calls the test client
        service = EncryptedStorageService(encryption_service_url=service_url)
        
        # Mock the HTTP client to use the test client
        async def mock_post(url, **kwargs):
            # Extract path from URL
            path = url.replace(service_url, "")
            if not path.startswith("/"):
                path = "/" + path
            
            # Make request to test client
            if "json" in kwargs:
                response = encryption_service_client.post(path, json=kwargs["json"])
            else:
                response = encryption_service_client.post(path, **kwargs)
            
            # Create mock response
            mock_response = Mock()
            mock_response.status_code = response.status_code
            mock_response.json = lambda: response.json()
            
            def raise_for_status():
                if response.status_code >= 400:
                    raise Exception(f"HTTP {response.status_code}")
            
            mock_response.raise_for_status = raise_for_status
            
            return mock_response
        
        service.client.post = AsyncMock(side_effect=mock_post)
        
        return service
    
    @pytest.mark.asyncio
    async def test_save_and_get_user_profile(self, encrypted_storage_service, test_db, test_user):
        """Test saving and retrieving encrypted user profile"""
        profile_data = {
            "name": "Test User",
            "age": 30,
            "preferences": {"theme": "dark"}
        }
        
        # Save profile
        profile = await encrypted_storage_service.save_user_profile(
            test_db,
            str(test_user.id),
            profile_data
        )
        
        assert profile is not None
        assert profile.user_id == test_user.id
        assert profile.encrypted_data is not None
        assert len(profile.encrypted_data) > 0
        
        # Get profile
        retrieved_data = await encrypted_storage_service.get_user_profile(
            test_db,
            str(test_user.id)
        )
        
        assert retrieved_data is not None
        assert retrieved_data["name"] == "Test User"
        assert retrieved_data["age"] == 30
        assert retrieved_data["preferences"]["theme"] == "dark"
    
    @pytest.mark.asyncio
    async def test_save_and_get_message(self, encrypted_storage_service, test_db, test_user):
        """Test saving and retrieving encrypted message"""
        import importlib.util
        
        # Create conversation first
        gateway_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..',
            'apps', 'backend', 'gateway'
        )
        
        try:
            models_spec = importlib.util.spec_from_file_location(
                "encrypted_models",
                os.path.join(gateway_path, "models", "encrypted_models.py")
            )
            if models_spec and models_spec.loader:
                models_module = importlib.util.module_from_spec(models_spec)
                models_spec.loader.exec_module(models_module)
                Conversation = models_module.Conversation
            else:
                # Create minimal Conversation model
                from sqlalchemy import Column, String, Boolean
                from sqlalchemy.dialects.postgresql import UUID, JSONB
                from sqlalchemy.ext.declarative import declarative_base
                Base = declarative_base()
                
                class Conversation(Base):
                    __tablename__ = "conversations"
                    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
                    user_id = Column(String(36))
                    started_at = Column(String(50), default=lambda: datetime.now(timezone.utc).isoformat())
                    ended_at = Column(String(50))
                    emotion_summary = Column(String(500))
                    crisis_detected = Column(String(5), default="false")
                    escalated_to_human = Column(String(5), default="false")
        except:
            from sqlalchemy import Column, String, Boolean
            from sqlalchemy.ext.declarative import declarative_base
            Base = declarative_base()
            
            class Conversation(Base):
                __tablename__ = "conversations"
                id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
                user_id = Column(String(36))
                started_at = Column(String(50), default=lambda: datetime.now(timezone.utc).isoformat())
                ended_at = Column(String(50))
                emotion_summary = Column(String(500))
                crisis_detected = Column(String(5), default="false")
                escalated_to_human = Column(String(5), default="false")
        
        conversation = Conversation(
            id=str(uuid.uuid4()),
            user_id=str(test_user.id)
        )
        test_db.add(conversation)
        test_db.commit()
        
        # Save message
        message_content = "This is a test message"
        message = await encrypted_storage_service.save_message(
            test_db,
            str(conversation.id),
            "user",
            message_content
        )
        
        assert message is not None
        assert message.conversation_id == conversation.id
        assert message.encrypted_content is not None
        assert len(message.encrypted_content) > 0
        
        # Get message
        retrieved_message = await encrypted_storage_service.get_message(
            test_db,
            str(message.id)
        )
        
        assert retrieved_message is not None
        assert retrieved_message["content"] == message_content
        assert retrieved_message["message_type"] == "user"
    
    @pytest.mark.asyncio
    async def test_save_and_get_sync_operation(self, encrypted_storage_service, test_db, test_user):
        """Test saving and retrieving encrypted sync operation"""
        operation_data = {
            "operation": "create_message",
            "data": {"message": "Test sync operation"}
        }
        
        # Save sync operation
        sync_entry = await encrypted_storage_service.enqueue_sync_operation(
            test_db,
            str(test_user.id),
            "create_message",
            operation_data
        )
        
        assert sync_entry is not None
        assert sync_entry.user_id == test_user.id
        assert sync_entry.encrypted_data is not None
        assert len(sync_entry.encrypted_data) > 0
        
        # Get sync operation
        retrieved_data = await encrypted_storage_service.get_sync_operation(
            test_db,
            str(sync_entry.id)
        )
        
        assert retrieved_data is not None
        assert retrieved_data["operation"] == "create_message"
        assert retrieved_data["data"]["message"] == "Test sync operation"
    
    @pytest.mark.asyncio
    async def test_key_rotation_workflow(self, encrypted_storage_service, test_db, test_user, encryption_service_client):
        """Test complete key rotation workflow"""
        # Step 1: Create encrypted data
        profile_data = {
            "name": "Test User",
            "sensitive_info": "This should remain encrypted"
        }
        
        profile = await encrypted_storage_service.save_user_profile(
            test_db,
            str(test_user.id),
            profile_data
        )
        
        # Verify data is encrypted
        assert profile.encrypted_data is not None
        
        # Step 2: Verify data can be decrypted with current key
        retrieved_before = await encrypted_storage_service.get_user_profile(
            test_db,
            str(test_user.id)
        )
        assert retrieved_before["name"] == "Test User"
        
        # Step 3: Rotate key and re-encrypt data
        rotation_result = await encrypted_storage_service.rotate_key_and_reencrypt_data(
            test_db,
            "test-admin-token",
            batch_size=10
        )
        
        assert rotation_result["success"] is True
        assert "rotation_record" in rotation_result
        assert "reencryption_results" in rotation_result
        
        # Step 4: Verify data can still be decrypted with new key
        retrieved_after = await encrypted_storage_service.get_user_profile(
            test_db,
            str(test_user.id)
        )
        assert retrieved_after["name"] == "Test User"
        assert retrieved_after["sensitive_info"] == "This should remain encrypted"
    
    @pytest.mark.asyncio
    async def test_key_rotation_with_multiple_tables(self, encrypted_storage_service, test_db, test_user):
        """Test key rotation re-encrypts all tables"""
        # Create data in all tables
        profile_data = {"name": "User 1"}
        await encrypted_storage_service.save_user_profile(test_db, str(test_user.id), profile_data)
        
        # Create conversation and message
        import importlib.util
        gateway_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'apps', 'backend', 'gateway')
        
        try:
            models_spec = importlib.util.spec_from_file_location(
                "encrypted_models",
                os.path.join(gateway_path, "models", "encrypted_models.py")
            )
            if models_spec and models_spec.loader:
                models_module = importlib.util.module_from_spec(models_spec)
                models_spec.loader.exec_module(models_module)
                Conversation = models_module.Conversation
            else:
                from sqlalchemy import Column, String
                from sqlalchemy.ext.declarative import declarative_base
                Base = declarative_base()
                class Conversation(Base):
                    __tablename__ = "conversations"
                    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
                    user_id = Column(String(36))
        except:
            from sqlalchemy import Column, String
            from sqlalchemy.ext.declarative import declarative_base
            Base = declarative_base()
            class Conversation(Base):
                __tablename__ = "conversations"
                id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
                user_id = Column(String(36))
        
        conversation = Conversation(id=str(uuid.uuid4()), user_id=str(test_user.id))
        test_db.add(conversation)
        test_db.commit()
        
        await encrypted_storage_service.save_message(test_db, str(conversation.id), "user", "Test message")
        
        sync_data = {"operation": "test"}
        await encrypted_storage_service.enqueue_sync_operation(test_db, str(test_user.id), "test", sync_data)
        
        # Rotate key
        rotation_result = await encrypted_storage_service.rotate_key_and_reencrypt_data(
            test_db,
            "test-admin-token",
            batch_size=10
        )
        
        # Verify all tables were processed
        assert rotation_result["success"] is True
        results = rotation_result["reencryption_results"]
        assert results["user_profiles"]["processed"] >= 1
        assert results["messages"]["processed"] >= 1
        assert results["sync_queue"]["processed"] >= 1
    
    def test_encryption_service_reencrypt_endpoint(self, encryption_service_client):
        """Test the re-encrypt endpoint of encryption service"""
        # First encrypt some data
        encrypt_response = encryption_service_client.post(
            "/encrypt",
            json={"data": "Test data to re-encrypt", "key_id": "test-key"}
        )
        assert encrypt_response.status_code == 200
        encrypted_data = encrypt_response.json()["result"]["encrypted_data"]
        
        # Re-encrypt the data
        reencrypt_response = encryption_service_client.post(
            "/re-encrypt",
            json={"encrypted_data": encrypted_data}
        )
        
        assert reencrypt_response.status_code == 200
        result = reencrypt_response.json()
        assert result["success"] is True
        assert "encrypted_data" in result["result"]
        
        # Verify the re-encrypted data is different
        new_encrypted_data = result["result"]["encrypted_data"]
        assert new_encrypted_data != encrypted_data

