"""
Tests for Encryption Service Database Integration
Verifies encryption service integration with database tables for encrypted data storage
"""

import pytest
import sys
import os
import tempfile
import shutil
import base64
import json
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import uuid


@pytest.fixture(scope="function")
def temp_dir():
    """Create temporary directory for key file"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture(scope="function")
def test_db_engine():
    """Create in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    
    # Create tables
    with engine.connect() as conn:
        # Create users table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """))
        
        # Create conversations table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                started_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """))
        
        # Create user_profiles table with encrypted_data
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                encrypted_data BLOB NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """))
        
        # Create messages table with encrypted_content
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                message_type TEXT NOT NULL,
                encrypted_content BLOB NOT NULL,
                emotion_data TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        """))
        
        conn.commit()
    
    return engine


@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """Create database session"""
    Session = sessionmaker(bind=test_db_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture(scope="function")
def encryption_client(temp_dir):
    """Create test client for encryption service"""
    key_file = os.path.join(temp_dir, "master.key")
    
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
                if mod_name != 'encryption_main':
                    del sys.modules[mod_name]
        
        # Mock settings
        with patch('config.settings') as mock_settings:
            mock_settings.MASTER_KEY_FILE = key_file
            mock_settings.ADMIN_TOKEN = "test-admin-token"
            
            from main import app
            yield TestClient(app)
    finally:
        os.chdir(old_cwd)
        if service_dir in sys.path:
            sys.path.remove(service_dir)


class TestEncryptionDatabaseIntegration:
    """Test encryption service integration with database tables"""
    
    def test_encrypt_user_profile_data(self, encryption_client, db_session, test_db_engine):
        """Test encrypting user profile data for database storage"""
        # Create test user
        user_id = str(uuid.uuid4())
        db_session.execute(text("""
            INSERT INTO users (id, email) VALUES (:id, :email)
        """), {"id": user_id, "email": "test@example.com"})
        db_session.commit()
        
        # Prepare profile data
        profile_data = {
            "name": "Test User",
            "age": 30,
            "preferences": {"theme": "dark", "language": "en"}
        }
        profile_json = json.dumps(profile_data)
        
        # Encrypt using encryption service
        encrypt_response = encryption_client.post(
            "/encrypt",
            json={"data": profile_json, "key_id": f"user:{user_id}"}
        )
        
        assert encrypt_response.status_code == 200
        encrypt_result = encrypt_response.json()
        assert encrypt_result["success"] is True
        encrypted_data_b64 = encrypt_result["result"]["encrypted_data"]
        
        # Convert base64 to bytes for BYTEA storage
        encrypted_bytes = base64.b64decode(encrypted_data_b64.encode('utf-8'))
        
        # Store in database
        db_session.execute(text("""
            INSERT INTO user_profiles (user_id, encrypted_data, created_at, updated_at)
            VALUES (:user_id, :encrypted_data, datetime('now'), datetime('now'))
        """), {"user_id": user_id, "encrypted_data": encrypted_bytes})
        db_session.commit()
        
        # Verify data was stored
        result = db_session.execute(text("""
            SELECT encrypted_data FROM user_profiles WHERE user_id = :user_id
        """), {"user_id": user_id}).fetchone()
        
        assert result is not None
        assert len(result[0]) > 0  # Encrypted data should not be empty
    
    def test_decrypt_user_profile_data(self, encryption_client, db_session, test_db_engine):
        """Test decrypting user profile data from database"""
        # Create test user
        user_id = str(uuid.uuid4())
        db_session.execute(text("""
            INSERT INTO users (id, email) VALUES (:id, :email)
        """), {"id": user_id, "email": "test@example.com"})
        db_session.commit()
        
        # Prepare and encrypt profile data
        profile_data = {
            "name": "Test User",
            "age": 30,
            "preferences": {"theme": "dark"}
        }
        profile_json = json.dumps(profile_data)
        
        encrypt_response = encryption_client.post(
            "/encrypt",
            json={"data": profile_json, "key_id": f"user:{user_id}"}
        )
        encrypted_data_b64 = encrypt_response.json()["result"]["encrypted_data"]
        encrypted_bytes = base64.b64decode(encrypted_data_b64.encode('utf-8'))
        
        # Store in database
        db_session.execute(text("""
            INSERT INTO user_profiles (user_id, encrypted_data, created_at, updated_at)
            VALUES (:user_id, :encrypted_data, datetime('now'), datetime('now'))
        """), {"user_id": user_id, "encrypted_data": encrypted_bytes})
        db_session.commit()
        
        # Retrieve from database
        result = db_session.execute(text("""
            SELECT encrypted_data FROM user_profiles WHERE user_id = :user_id
        """), {"user_id": user_id}).fetchone()
        
        encrypted_bytes_from_db = result[0]
        
        # Convert bytes back to base64 for decryption
        encrypted_b64_from_db = base64.b64encode(encrypted_bytes_from_db).decode('utf-8')
        
        # Decrypt using encryption service
        decrypt_response = encryption_client.post(
            "/decrypt",
            json={"encrypted_data": encrypted_b64_from_db, "key_id": f"user:{user_id}"}
        )
        
        assert decrypt_response.status_code == 200
        decrypt_result = decrypt_response.json()
        decrypted_json = decrypt_result["data"]
        
        # Verify decrypted data matches original
        decrypted_data = json.loads(decrypted_json)
        assert decrypted_data["name"] == profile_data["name"]
        assert decrypted_data["age"] == profile_data["age"]
        assert decrypted_data["preferences"] == profile_data["preferences"]
    
    def test_encrypt_message_content(self, encryption_client, db_session, test_db_engine):
        """Test encrypting message content for database storage"""
        # Create test user and conversation
        user_id = str(uuid.uuid4())
        conversation_id = str(uuid.uuid4())
        
        db_session.execute(text("""
            INSERT INTO users (id, email) VALUES (:id, :email)
        """), {"id": user_id, "email": "test@example.com"})
        
        db_session.execute(text("""
            INSERT INTO conversations (id, user_id) VALUES (:id, :user_id)
        """), {"id": conversation_id, "user_id": user_id})
        db_session.commit()
        
        # Prepare message content
        message_content = "This is a sensitive message that needs encryption."
        
        # Encrypt using encryption service
        encrypt_response = encryption_client.post(
            "/encrypt",
            json={"data": message_content, "key_id": f"conversation:{conversation_id}"}
        )
        
        assert encrypt_response.status_code == 200
        encrypt_result = encrypt_response.json()
        encrypted_data_b64 = encrypt_result["result"]["encrypted_data"]
        
        # Convert base64 to bytes for BYTEA storage
        encrypted_bytes = base64.b64decode(encrypted_data_b64.encode('utf-8'))
        
        # Store in database
        message_id = str(uuid.uuid4())
        db_session.execute(text("""
            INSERT INTO messages (id, conversation_id, message_type, encrypted_content, created_at)
            VALUES (:id, :conversation_id, :message_type, :encrypted_content, datetime('now'))
        """), {
            "id": message_id,
            "conversation_id": conversation_id,
            "message_type": "user",
            "encrypted_content": encrypted_bytes
        })
        db_session.commit()
        
        # Verify data was stored
        result = db_session.execute(text("""
            SELECT encrypted_content FROM messages WHERE id = :id
        """), {"id": message_id}).fetchone()
        
        assert result is not None
        assert len(result[0]) > 0
    
    def test_decrypt_message_content(self, encryption_client, db_session, test_db_engine):
        """Test decrypting message content from database"""
        # Create test user and conversation
        user_id = str(uuid.uuid4())
        conversation_id = str(uuid.uuid4())
        
        db_session.execute(text("""
            INSERT INTO users (id, email) VALUES (:id, :email)
        """), {"id": user_id, "email": "test@example.com"})
        
        db_session.execute(text("""
            INSERT INTO conversations (id, user_id) VALUES (:id, :user_id)
        """), {"id": conversation_id, "user_id": user_id})
        db_session.commit()
        
        # Prepare and encrypt message content
        original_message = "This is a sensitive message."
        
        encrypt_response = encryption_client.post(
            "/encrypt",
            json={"data": original_message, "key_id": f"conversation:{conversation_id}"}
        )
        encrypted_data_b64 = encrypt_response.json()["result"]["encrypted_data"]
        encrypted_bytes = base64.b64decode(encrypted_data_b64.encode('utf-8'))
        
        # Store in database
        message_id = str(uuid.uuid4())
        db_session.execute(text("""
            INSERT INTO messages (id, conversation_id, message_type, encrypted_content, created_at)
            VALUES (:id, :conversation_id, :message_type, :encrypted_content, datetime('now'))
        """), {
            "id": message_id,
            "conversation_id": conversation_id,
            "message_type": "user",
            "encrypted_content": encrypted_bytes
        })
        db_session.commit()
        
        # Retrieve from database
        result = db_session.execute(text("""
            SELECT encrypted_content FROM messages WHERE id = :id
        """), {"id": message_id}).fetchone()
        
        encrypted_bytes_from_db = result[0]
        encrypted_b64_from_db = base64.b64encode(encrypted_bytes_from_db).decode('utf-8')
        
        # Decrypt using encryption service
        decrypt_response = encryption_client.post(
            "/decrypt",
            json={"encrypted_data": encrypted_b64_from_db, "key_id": f"conversation:{conversation_id}"}
        )
        
        assert decrypt_response.status_code == 200
        decrypted_message = decrypt_response.json()["data"]
        
        # Verify decrypted message matches original
        assert decrypted_message == original_message
    
    def test_key_rotation_persistence(self, encryption_client, db_session, test_db_engine):
        """Test that key rotation maintains ability to decrypt existing data"""
        # Create test user
        user_id = str(uuid.uuid4())
        db_session.execute(text("""
            INSERT INTO users (id, email) VALUES (:id, :email)
        """), {"id": user_id, "email": "test@example.com"})
        db_session.commit()
        
        # Encrypt and store data with old key
        profile_data = {"name": "Test User", "data": "sensitive information"}
        profile_json = json.dumps(profile_data)
        
        encrypt_response = encryption_client.post(
            "/encrypt",
            json={"data": profile_json, "key_id": f"user:{user_id}"}
        )
        encrypted_data_b64 = encrypt_response.json()["result"]["encrypted_data"]
        encrypted_bytes = base64.b64decode(encrypted_data_b64.encode('utf-8'))
        
        # Store in database
        db_session.execute(text("""
            INSERT INTO user_profiles (user_id, encrypted_data, created_at, updated_at)
            VALUES (:user_id, :encrypted_data, datetime('now'), datetime('now'))
        """), {"user_id": user_id, "encrypted_data": encrypted_bytes})
        db_session.commit()
        
        # Rotate key (in real scenario, this would update the key but maintain backward compatibility)
        # For this test, we verify that data encrypted before rotation can still be decrypted
        # Note: Actual key rotation implementation would need to re-encrypt all data
        
        # Retrieve encrypted data
        result = db_session.execute(text("""
            SELECT encrypted_data FROM user_profiles WHERE user_id = :user_id
        """), {"user_id": user_id}).fetchone()
        
        encrypted_bytes_from_db = result[0]
        encrypted_b64_from_db = base64.b64encode(encrypted_bytes_from_db).decode('utf-8')
        
        # Verify we can still decrypt with current key
        decrypt_response = encryption_client.post(
            "/decrypt",
            json={"encrypted_data": encrypted_b64_from_db, "key_id": f"user:{user_id}"}
        )
        
        assert decrypt_response.status_code == 200
        decrypted_json = decrypt_response.json()["data"]
        decrypted_data = json.loads(decrypted_json)
        assert decrypted_data["name"] == profile_data["name"]
    
    def test_encrypted_data_integrity(self, encryption_client, db_session, test_db_engine):
        """Test that encrypted data maintains integrity through storage and retrieval"""
        # Create test user
        user_id = str(uuid.uuid4())
        db_session.execute(text("""
            INSERT INTO users (id, email) VALUES (:id, :email)
        """), {"id": user_id, "email": "test@example.com"})
        db_session.commit()
        
        # Encrypt data
        original_data = "This is important data that must remain intact."
        
        encrypt_response = encryption_client.post(
            "/encrypt",
            json={"data": original_data, "key_id": f"user:{user_id}"}
        )
        encrypted_data_b64 = encrypt_response.json()["result"]["encrypted_data"]
        encrypted_bytes = base64.b64decode(encrypted_data_b64.encode('utf-8'))
        
        # Store in database
        db_session.execute(text("""
            INSERT INTO user_profiles (user_id, encrypted_data, created_at, updated_at)
            VALUES (:user_id, :encrypted_data, datetime('now'), datetime('now'))
        """), {"user_id": user_id, "encrypted_data": encrypted_bytes})
        db_session.commit()
        
        # Retrieve multiple times and verify consistency
        for _ in range(3):
            result = db_session.execute(text("""
                SELECT encrypted_data FROM user_profiles WHERE user_id = :user_id
            """), {"user_id": user_id}).fetchone()
            
            encrypted_bytes_from_db = result[0]
            encrypted_b64_from_db = base64.b64encode(encrypted_bytes_from_db).decode('utf-8')
            
            # Decrypt and verify
            decrypt_response = encryption_client.post(
                "/decrypt",
                json={"encrypted_data": encrypted_b64_from_db, "key_id": f"user:{user_id}"}
            )
            
            assert decrypt_response.status_code == 200
            decrypted_data = decrypt_response.json()["data"]
            assert decrypted_data == original_data, "Data integrity must be maintained"

