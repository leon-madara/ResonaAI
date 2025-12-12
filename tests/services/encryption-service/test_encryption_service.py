"""
Unit tests for Encryption Service
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, mock_open
from fastapi.testclient import TestClient
import base64
import tempfile
import shutil

# Store original working directory
original_cwd = os.getcwd()


class TestEncryptionService:
    """Test Encryption Service endpoints"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for key file"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def client(self, temp_dir):
        """Create test client"""
        key_file = os.path.join(temp_dir, "master.key")
        
        # Get service directory
        service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'services', 'encryption-service'))
        
        # Save current directory and change to service directory
        old_cwd = os.getcwd()
        os.chdir(service_dir)
        
        # Add service directory to Python path
        if service_dir not in sys.path:
            sys.path.insert(0, service_dir)
        
        try:
            # Clear cached modules
            for mod_name in list(sys.modules.keys()):
                if mod_name.startswith('main') or mod_name.startswith('config') or 'encryption' in mod_name:
                    if mod_name != 'encryption_main':  # Don't delete our test module name
                        del sys.modules[mod_name]
            
            # Mock settings before importing
            with patch('config.settings') as mock_settings:
                mock_settings.MASTER_KEY_FILE = key_file
                mock_settings.ADMIN_TOKEN = "test-admin-token"
                
                # Import main module
                from main import app
                yield TestClient(app)
        finally:
            # Restore directory and path
            os.chdir(old_cwd)
            if service_dir in sys.path:
                sys.path.remove(service_dir)
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "encryption-service"
        assert "timestamp" in data
    
    def test_encrypt_data(self, client):
        """Test data encryption"""
        request_data = {
            "data": "This is sensitive information",
            "key_id": "test-key"
        }
        
        response = client.post("/encrypt", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "result" in data
        assert "encrypted_data" in data["result"]
        assert data["result"]["key_id"] == "test-key"
        assert data["result"]["algorithm"] == "AES-256"
        assert "timestamp" in data["result"]
    
    def test_encrypt_decrypt_roundtrip(self, client):
        """Test encrypt and decrypt roundtrip"""
        original_data = "This is a test message"
        
        # Encrypt
        encrypt_request = {
            "data": original_data,
            "key_id": None
        }
        encrypt_response = client.post("/encrypt", json=encrypt_request)
        assert encrypt_response.status_code == 200
        encrypted_data = encrypt_response.json()["result"]["encrypted_data"]
        
        # Decrypt
        decrypt_request = {
            "encrypted_data": encrypted_data,
            "key_id": None
        }
        decrypt_response = client.post("/decrypt", json=decrypt_request)
        assert decrypt_response.status_code == 200
        decrypted_data = decrypt_response.json()["data"]
        
        assert decrypted_data == original_data
    
    def test_decrypt_invalid_data(self, client):
        """Test decrypting invalid data"""
        request_data = {
            "encrypted_data": "invalid-base64-data!!!",
            "key_id": None
        }
        
        response = client.post("/decrypt", json=request_data)
        assert response.status_code == 500
        assert "failed" in response.json()["detail"].lower()
    
    def test_encrypt_missing_data(self, client):
        """Test encryption with missing data"""
        request_data = {
            "key_id": "test-key"
        }
        
        response = client.post("/encrypt", json=request_data)
        assert response.status_code == 422
    
    def test_rotate_key_with_admin_token(self, client):
        """Test key rotation with valid admin token"""
        request_data = {
            "admin_token": "test-admin-token"
        }
        
        response = client.post("/rotate-key", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "rotation_record" in data
        assert "old_key_hash" in data["rotation_record"]
        assert "new_key_hash" in data["rotation_record"]
        assert "timestamp" in data["rotation_record"]
    
    def test_rotate_key_invalid_token(self, client):
        """Test key rotation with invalid admin token"""
        request_data = {
            "admin_token": "invalid-token"
        }
        
        response = client.post("/rotate-key", json=request_data)
        assert response.status_code == 401
    
    def test_rotate_key_missing_token(self, client):
        """Test key rotation without admin token"""
        # FastAPI validates request body first, so we get 422 for missing required field
        request_data = {}
        
        response = client.post("/rotate-key", json=request_data)
        # FastAPI returns 422 for validation errors before checking auth
        assert response.status_code in [401, 422]
    
    def test_generate_user_key(self, client):
        """Test user-specific key generation"""
        user_id = "test-user-123"
        password = "user-password-123"
        
        response = client.post(
            f"/generate-user-key?user_id={user_id}&password={password}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "key" in data
        # Key should be base64 encoded
        assert isinstance(data["key"], str)
    
    def test_get_key_info(self, client):
        """Test getting key information"""
        response = client.get("/key-info")
        
        assert response.status_code == 200
        data = response.json()
        assert data["algorithm"] == "AES-256"
        assert "key_rotation_schedule" in data
        assert "key_file_exists" in data
    
    def test_e2e_encrypt_message(self, client):
        """Test end-to-end message encryption"""
        message = "This is a private message"
        user_id = "test-user"
        password = "user-password"
        
        response = client.post(
            f"/e2e/encrypt-message?message={message}&user_id={user_id}&password={password}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "result" in data
        assert "encrypted_content" in data["result"]
        assert data["result"]["algorithm"] == "AES-256-Fernet"
        assert data["result"]["key_id"] == f"user:{user_id}"
    
    def test_e2e_decrypt_message(self, client):
        """Test end-to-end message decryption"""
        original_message = "This is a private message"
        user_id = "test-user"
        password = "user-password"
        
        # First encrypt
        encrypt_response = client.post(
            f"/e2e/encrypt-message?message={original_message}&user_id={user_id}&password={password}"
        )
        assert encrypt_response.status_code == 200
        encrypted_content = encrypt_response.json()["result"]["encrypted_content"]
        
        # Then decrypt
        decrypt_response = client.post(
            f"/e2e/decrypt-message?encrypted_content={encrypted_content}&user_id={user_id}&password={password}"
        )
        
        assert decrypt_response.status_code == 200
        data = decrypt_response.json()
        assert data["success"] is True
        assert data["message"] == original_message
        assert "timestamp" in data
    
    def test_e2e_decrypt_wrong_password(self, client):
        """Test decrypting with wrong password"""
        original_message = "This is a private message"
        user_id = "test-user"
        correct_password = "correct-password"
        wrong_password = "wrong-password"
        
        # Encrypt with correct password
        encrypt_response = client.post(
            f"/e2e/encrypt-message?message={original_message}&user_id={user_id}&password={correct_password}"
        )
        assert encrypt_response.status_code == 200
        encrypted_content = encrypt_response.json()["result"]["encrypted_content"]
        
        # Try to decrypt with wrong password
        decrypt_response = client.post(
            f"/e2e/decrypt-message?encrypted_content={encrypted_content}&user_id={user_id}&password={wrong_password}"
        )
        
        # Should fail
        assert decrypt_response.status_code == 500
    
    def test_batch_encrypt_messages(self, client):
        """Test batch message encryption"""
        request_data = {
            "messages": ["Message 1", "Message 2", "Message 3"],
            "user_id": "test-user",
            "password": "user-password"
        }
        
        response = client.post(
            "/e2e/batch-encrypt",
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 3
        assert len(data["results"]) == 3
        assert len(data["results"]) == len(request_data["messages"])
    
    def test_batch_decrypt_messages(self, client):
        """Test batch message decryption"""
        original_messages = ["Message 1", "Message 2"]
        user_id = "test-user"
        password = "user-password"
        
        # Encrypt messages
        encrypted_contents = []
        for msg in original_messages:
            encrypt_response = client.post(
                f"/e2e/encrypt-message?message={msg}&user_id={user_id}&password={password}"
            )
            encrypted_contents.append(encrypt_response.json()["result"]["encrypted_content"])
        
        # Decrypt in batch using JSON body
        request_data = {
            "encrypted_contents": encrypted_contents,
            "user_id": user_id,
            "password": password
        }
        
        response = client.post(
            "/e2e/batch-decrypt",
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 2
        assert len(data["results"]) == 2
        assert data["results"][0]["message"] == original_messages[0]
        assert data["results"][1]["message"] == original_messages[1]

