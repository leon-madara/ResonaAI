"""
Unit tests for Consent Management Service
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from datetime import datetime
import jwt

# Store original working directory
original_cwd = os.getcwd()


class TestConsentManagement:
    """Test Consent Management service endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client with mocked dependencies"""
        # Change to service directory for imports
        service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'services', 'consent-management'))
        old_cwd = os.getcwd()
        os.chdir(service_dir)
        
        try:
            # Add service directory to Python path
            if service_dir not in sys.path:
                sys.path.insert(0, service_dir)
            
            # Clear cached modules
            for mod_name in list(sys.modules.keys()):
                if mod_name in ['main', 'config'] or mod_name.startswith('models.consent'):
                    del sys.modules[mod_name]
            
            with patch('config.settings') as mock_settings:
                mock_settings.DATABASE_URL = "sqlite:///:memory:"
                mock_settings.JWT_SECRET_KEY = "test-secret-key"
                mock_settings.JWT_ALGORITHM = "HS256"
                
                from main import app
                yield TestClient(app)
        finally:
            os.chdir(old_cwd)
            if service_dir in sys.path:
                sys.path.remove(service_dir)
    
    @pytest.fixture
    def auth_token(self):
        """Generate a test JWT token"""
        token_data = {
            "user_id": "test-user-123",
            "email": "test@example.com",
            "exp": datetime.utcnow().timestamp() + 3600
        }
        token = jwt.encode(token_data, "test-secret-key", algorithm="HS256")
        return f"Bearer {token}"
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "consent-management"
        assert "timestamp" in data
    
    def test_create_consent(self, client, auth_token):
        """Test creating a consent record"""
        request_data = {
            "consent_type": "data_processing",
            "consent_version": "1.0",
            "granted": True,
            "consent_data": {"purpose": "mental health support"},
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0"
        }
        
        response = client.post(
            "/consent",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test-user-123"
        assert data["consent_type"] == "data_processing"
        assert data["consent_version"] == "1.0"
        assert data["granted"] is True
        assert "granted_at" in data
        assert data["revoked_at"] is None
    
    def test_create_consent_denied(self, client, auth_token):
        """Test creating a consent record with granted=False"""
        request_data = {
            "consent_type": "research_participation",
            "consent_version": "1.0",
            "granted": False
        }
        
        response = client.post(
            "/consent",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["granted"] is False
    
    def test_get_consents(self, client, auth_token):
        """Test getting all consent records for a user"""
        # First create a consent
        create_request = {
            "consent_type": "emotion_analysis",
            "consent_version": "1.0",
            "granted": True
        }
        client.post("/consent", json=create_request, headers={"Authorization": auth_token})
        
        # Then get all consents
        response = client.get("/consent", headers={"Authorization": auth_token})
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["user_id"] == "test-user-123"
    
    def test_revoke_consent(self, client, auth_token):
        """Test revoking a consent"""
        # First create a consent
        create_request = {
            "consent_type": "cultural_context",
            "consent_version": "1.0",
            "granted": True
        }
        client.post("/consent", json=create_request, headers={"Authorization": auth_token})
        
        # Then revoke it
        revoke_request = {
            "consent_type": "cultural_context",
            "consent_version": "1.0"
        }
        response = client.post(
            "/consent/revoke",
            json=revoke_request,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
    
    def test_revoke_nonexistent_consent(self, client, auth_token):
        """Test revoking a consent that doesn't exist"""
        revoke_request = {
            "consent_type": "nonexistent",
            "consent_version": "1.0"
        }
        
        response = client.post(
            "/consent/revoke",
            json=revoke_request,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 404
    
    def test_check_consent_active(self, client, auth_token):
        """Test checking active consent"""
        # First create a consent
        create_request = {
            "consent_type": "crisis_intervention",
            "consent_version": "1.0",
            "granted": True
        }
        client.post("/consent", json=create_request, headers={"Authorization": auth_token})
        
        # Then check it
        response = client.get(
            "/consent/check?consent_type=crisis_intervention&consent_version=1.0",
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["has_consent"] is True
        assert data["consent_type"] == "crisis_intervention"
        assert data["consent_version"] == "1.0"
    
    def test_check_consent_inactive(self, client, auth_token):
        """Test checking inactive consent"""
        response = client.get(
            "/consent/check?consent_type=nonexistent&consent_version=1.0",
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["has_consent"] is False
    
    def test_get_consent_types(self, client):
        """Test getting available consent types"""
        response = client.get("/consent/types")
        
        assert response.status_code == 200
        data = response.json()
        assert "consent_types" in data
        assert isinstance(data["consent_types"], list)
        assert len(data["consent_types"]) > 0
        
        # Check that required types are present
        types = [ct["type"] for ct in data["consent_types"]]
        assert "data_processing" in types
        assert "crisis_intervention" in types
        assert "emotion_analysis" in types
    
    def test_create_consent_no_auth(self, client):
        """Test creating consent without authentication"""
        request_data = {
            "consent_type": "data_processing",
            "consent_version": "1.0",
            "granted": True
        }
        
        response = client.post("/consent", json=request_data)
        assert response.status_code == 403
    
    def test_get_consents_no_auth(self, client):
        """Test getting consents without authentication"""
        response = client.get("/consent")
        assert response.status_code == 403
    
    def test_revoke_consent_no_auth(self, client):
        """Test revoking consent without authentication"""
        request_data = {
            "consent_type": "data_processing",
            "consent_version": "1.0"
        }
        
        response = client.post("/consent/revoke", json=request_data)
        assert response.status_code == 403
    
    def test_create_consent_missing_fields(self, client, auth_token):
        """Test creating consent with missing required fields"""
        # Missing consent_type
        response = client.post(
            "/consent",
            json={"consent_version": "1.0", "granted": True},
            headers={"Authorization": auth_token}
        )
        assert response.status_code == 422
        
        # Missing consent_version
        response = client.post(
            "/consent",
            json={"consent_type": "data_processing", "granted": True},
            headers={"Authorization": auth_token}
        )
        assert response.status_code == 422
    
    def test_create_multiple_consents(self, client, auth_token):
        """Test creating multiple consent records"""
        consent_types = [
            "data_processing",
            "emotion_analysis",
            "cultural_context",
            "research_participation",
            "crisis_intervention"
        ]
        
        for consent_type in consent_types:
            request_data = {
                "consent_type": consent_type,
                "consent_version": "1.0",
                "granted": True
            }
            
            response = client.post(
                "/consent",
                json=request_data,
                headers={"Authorization": auth_token}
            )
            assert response.status_code == 200
        
        # Verify all were created
        response = client.get("/consent", headers={"Authorization": auth_token})
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= len(consent_types)
    
    def test_consent_versioning(self, client, auth_token):
        """Test consent versioning"""
        # Create consent for version 1.0
        request_v1 = {
            "consent_type": "data_processing",
            "consent_version": "1.0",
            "granted": True
        }
        client.post("/consent", json=request_v1, headers={"Authorization": auth_token})
        
        # Create consent for version 2.0
        request_v2 = {
            "consent_type": "data_processing",
            "consent_version": "2.0",
            "granted": True
        }
        client.post("/consent", json=request_v2, headers={"Authorization": auth_token})
        
        # Check both versions
        response_v1 = client.get(
            "/consent/check?consent_type=data_processing&consent_version=1.0",
            headers={"Authorization": auth_token}
        )
        assert response_v1.json()["has_consent"] is True
        
        response_v2 = client.get(
            "/consent/check?consent_type=data_processing&consent_version=2.0",
            headers={"Authorization": auth_token}
        )
        assert response_v2.json()["has_consent"] is True

