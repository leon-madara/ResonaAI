"""
Unit tests for PII Anonymization Service
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
import jwt
from datetime import datetime, timedelta


class TestPIIAnonymization:
    """Test PII Anonymization service endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        service_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', '..', 
            'apps', 'backend', 'services', 'pii-anonymization'
        ))
        old_cwd = os.getcwd()
        os.chdir(service_dir)
        
        try:
            if service_dir not in sys.path:
                sys.path.insert(0, service_dir)
            
            # Clear cached modules
            for mod_name in list(sys.modules.keys()):
                if mod_name in ['main', 'config', 'models', 'anonymizer'] or \
                   mod_name.startswith('main.') or mod_name.startswith('anonymizer.'):
                    if mod_name in sys.modules:
                        del sys.modules[mod_name]
            
            from main import app
            yield TestClient(app)
        finally:
            os.chdir(old_cwd)
            if service_dir in sys.path:
                sys.path.remove(service_dir)
    
    @pytest.fixture
    def auth_token(self):
        """Generate a test JWT token"""
        token = jwt.encode(
            {
                "user_id": "test-user-123",
                "email": "test@example.com",
                "exp": datetime.utcnow() + timedelta(hours=1),
            },
            "test-secret-key",
            algorithm="HS256",
        )
        return f"Bearer {token}"
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "pii-anonymization"
        assert "patterns_loaded" in data
    
    def test_list_patterns(self, client):
        """Test listing available PII patterns"""
        response = client.get("/patterns")
        
        assert response.status_code == 200
        data = response.json()
        assert "patterns" in data
        assert "anonymization_methods" in data
        assert len(data["patterns"]) > 0
    
    def test_detect_email(self, client, auth_token):
        """Test detecting email addresses"""
        request_data = {
            "text": "Contact me at john.doe@example.com for more info",
            "pii_types": None
        }
        
        response = client.post(
            "/detect",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["contains_pii"] is True
        assert data["pii_count"] >= 1
        assert any(d["pii_type"] == "email" for d in data["pii_detected"])
    
    def test_detect_phone(self, client, auth_token):
        """Test detecting phone numbers"""
        request_data = {
            "text": "Call me at +254712345678 or 0712345678",
            "pii_types": None
        }
        
        response = client.post(
            "/detect",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["contains_pii"] is True
        assert data["pii_count"] >= 1
    
    def test_detect_no_pii(self, client, auth_token):
        """Test text with no PII"""
        request_data = {
            "text": "This is a normal sentence with no personal information",
            "pii_types": None
        }
        
        response = client.post(
            "/detect",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["contains_pii"] is False
        assert data["pii_count"] == 0
    
    def test_anonymize_tokenization(self, client, auth_token):
        """Test anonymization with tokenization method"""
        request_data = {
            "text": "My email is john@example.com",
            "method": "tokenization",
            "pii_types": None,
            "preserve_format": True,
            "user_id": "test-user-123"
        }
        
        response = client.post(
            "/anonymize",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["pii_count"] >= 1
        assert "john@example.com" not in data["anonymized_text"]
        assert data["tokens"] is not None
        assert len(data["tokens"]) > 0
    
    def test_anonymize_hashing(self, client, auth_token):
        """Test anonymization with hashing method"""
        request_data = {
            "text": "My email is john@example.com",
            "method": "hashing",
            "pii_types": None,
            "preserve_format": True,
            "user_id": "test-user-123"
        }
        
        response = client.post(
            "/anonymize",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["pii_count"] >= 1
        assert "john@example.com" not in data["anonymized_text"]
        assert "[HASH_" in data["anonymized_text"]
        assert data["tokens"] is None  # Hashing doesn't return tokens
    
    def test_anonymize_masking(self, client, auth_token):
        """Test anonymization with masking method"""
        request_data = {
            "text": "My email is john@example.com",
            "method": "masking",
            "pii_types": None,
            "preserve_format": True,
            "user_id": "test-user-123"
        }
        
        response = client.post(
            "/anonymize",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["pii_count"] >= 1
        assert "john@example.com" not in data["anonymized_text"]
        # Masking should partially reveal data
        assert "***" in data["anonymized_text"]
    
    def test_anonymize_redaction(self, client, auth_token):
        """Test anonymization with redaction method"""
        request_data = {
            "text": "My email is john@example.com",
            "method": "redaction",
            "pii_types": None,
            "preserve_format": True,
            "user_id": "test-user-123"
        }
        
        response = client.post(
            "/anonymize",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["pii_count"] >= 1
        assert "john@example.com" not in data["anonymized_text"]
        assert "REDACTED" in data["anonymized_text"]
    
    def test_deanonymize(self, client, auth_token):
        """Test de-anonymization (token restoration)"""
        # First anonymize
        anonymize_request = {
            "text": "My email is john@example.com",
            "method": "tokenization",
            "pii_types": None,
            "preserve_format": True,
            "user_id": "test-user-123"
        }
        
        anonymize_response = client.post(
            "/anonymize",
            json=anonymize_request,
            headers={"Authorization": auth_token}
        )
        
        assert anonymize_response.status_code == 200
        anonymize_data = anonymize_response.json()
        
        # Then de-anonymize
        deanonymize_request = {
            "text": anonymize_data["anonymized_text"],
            "tokens": anonymize_data["tokens"]
        }
        
        deanonymize_response = client.post(
            "/deanonymize",
            json=deanonymize_request,
            headers={"Authorization": auth_token}
        )
        
        assert deanonymize_response.status_code == 200
        deanonymize_data = deanonymize_response.json()
        assert "john@example.com" in deanonymize_data["text"]
        assert deanonymize_data["tokens_replaced"] > 0
    
    def test_batch_anonymize(self, client, auth_token):
        """Test batch anonymization"""
        request_data = {
            "texts": [
                "My email is john@example.com",
                "Call me at +254712345678",
                "No PII here"
            ],
            "method": "tokenization",
            "pii_types": None
        }
        
        response = client.post(
            "/batch/anonymize",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 3
        assert data["total_pii_count"] >= 2
        assert "processing_time_ms" in data
    
    def test_external_api_prepare(self, client, auth_token):
        """Test preparing text for external API"""
        request_data = {
            "text": "My email is john@example.com and phone is +254712345678",
            "method": "tokenization",
            "pii_types": None,
            "preserve_format": False,
            "user_id": "test-user-123"
        }
        
        response = client.post(
            "/external-api/prepare",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "anonymized_text" in data
        assert "tokens" in data
        assert "john@example.com" not in data["anonymized_text"]
        assert data["pii_removed"] is True
    
    def test_external_api_restore(self, client, auth_token):
        """Test restoring text from external API"""
        # First prepare
        prepare_request = {
            "text": "My email is john@example.com",
            "method": "tokenization",
            "pii_types": None,
            "preserve_format": False,
            "user_id": "test-user-123"
        }
        
        prepare_response = client.post(
            "/external-api/prepare",
            json=prepare_request,
            headers={"Authorization": auth_token}
        )
        
        assert prepare_response.status_code == 200
        prepare_data = prepare_response.json()
        
        # Then restore
        restore_request = {
            "text": prepare_data["anonymized_text"],
            "tokens": prepare_data["tokens"]
        }
        
        restore_response = client.post(
            "/external-api/restore",
            json=restore_request,
            headers={"Authorization": auth_token}
        )
        
        assert restore_response.status_code == 200
        restore_data = restore_response.json()
        assert "john@example.com" in restore_data["restored_text"]
    
    def test_specific_pii_types(self, client, auth_token):
        """Test detecting specific PII types only"""
        request_data = {
            "text": "Email: john@example.com, Phone: +254712345678",
            "pii_types": ["email"]  # Only detect emails
        }
        
        response = client.post(
            "/detect",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["contains_pii"] is True
        # Should only detect email, not phone
        assert all(d["pii_type"] == "email" for d in data["pii_detected"])
    
    def test_unauthorized_access(self, client):
        """Test that endpoints require authentication"""
        request_data = {
            "text": "My email is john@example.com",
            "pii_types": None
        }
        
        response = client.post(
            "/detect",
            json=request_data
        )
        
        assert response.status_code == 403
    
    def test_missing_required_fields(self, client, auth_token):
        """Test validation of required fields"""
        request_data = {
            "pii_types": None
            # Missing 'text' field
        }
        
        response = client.post(
            "/detect",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 422  # Validation error
