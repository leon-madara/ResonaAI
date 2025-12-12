"""
Unit tests for API Gateway authentication endpoints
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
import jwt
from datetime import datetime, timedelta

# Add services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'services', 'api-gateway'))


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client with mocked dependencies"""
        with patch('main.redis_client') as mock_redis, \
             patch('main.health_checker') as mock_health, \
             patch('main.http_client') as mock_http:
            
            mock_redis.ping.return_value = True
            mock_health.check_all_services = Mock(return_value={})
            
            from main import app
            return TestClient(app)
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        mock_db = MagicMock()
        return mock_db
    
    def test_login_missing_fields(self, client):
        """Test login with missing email or password"""
        # Missing email
        response = client.post("/auth/login", json={"password": "test"})
        assert response.status_code == 400
        assert "required" in response.json()["detail"].lower()
        
        # Missing password
        response = client.post("/auth/login", json={"email": "test@example.com"})
        assert response.status_code == 400
        assert "required" in response.json()["detail"].lower()
    
    def test_login_invalid_credentials(self, client, mock_db_session):
        """Test login with invalid credentials"""
        with patch('main.get_db', return_value=mock_db_session), \
             patch('main.authenticate_user', return_value=None):
            
            response = client.post(
                "/auth/login",
                json={"email": "test@example.com", "password": "wrongpassword"}
            )
            assert response.status_code == 401
            assert "invalid" in response.json()["detail"].lower()
    
    def test_login_success(self, client, mock_db_session):
        """Test successful login"""
        from database import User
        import uuid
        
        test_user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            consent_version="1.0",
            is_anonymous=False,
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow()
        )
        
        with patch('main.get_db', return_value=mock_db_session), \
             patch('main.authenticate_user', return_value=test_user), \
             patch('main.settings') as mock_settings:
            
            mock_settings.JWT_SECRET_KEY = "test-secret-key"
            mock_settings.JWT_ALGORITHM = "HS256"
            mock_settings.JWT_EXPIRATION_HOURS = 24
            
            response = client.post(
                "/auth/login",
                json={"email": "test@example.com", "password": "testpassword"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            assert "expires_in" in data
    
    def test_register_missing_fields(self, client):
        """Test registration with missing required fields"""
        # Missing email
        response = client.post("/auth/register", json={
            "password": "test123",
            "consent_version": "1.0"
        })
        assert response.status_code == 400
        
        # Missing password
        response = client.post("/auth/register", json={
            "email": "test@example.com",
            "consent_version": "1.0"
        })
        assert response.status_code == 400
        
        # Missing consent_version
        response = client.post("/auth/register", json={
            "email": "test@example.com",
            "password": "test123"
        })
        assert response.status_code == 400
    
    def test_register_invalid_email(self, client, mock_db_session):
        """Test registration with invalid email"""
        with patch('main.get_db', return_value=mock_db_session), \
             patch('main.create_user', side_effect=ValueError("Invalid email format")):
            
            response = client.post("/auth/register", json={
                "email": "invalid-email",
                "password": "test123",
                "consent_version": "1.0"
            })
            assert response.status_code == 400
            assert "email" in response.json()["detail"].lower()
    
    def test_register_duplicate_email(self, client, mock_db_session):
        """Test registration with duplicate email"""
        with patch('main.get_db', return_value=mock_db_session), \
             patch('main.create_user', side_effect=ValueError("User with this email already exists")):
            
            response = client.post("/auth/register", json={
                "email": "existing@example.com",
                "password": "test123",
                "consent_version": "1.0"
            })
            assert response.status_code == 400
            assert "already exists" in response.json()["detail"].lower()
    
    def test_register_success(self, client, mock_db_session):
        """Test successful registration"""
        from database import User
        import uuid
        
        test_user = User(
            id=uuid.uuid4(),
            email="newuser@example.com",
            password_hash="hashed_password",
            consent_version="1.0",
            is_anonymous=False,
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow()
        )
        
        with patch('main.get_db', return_value=mock_db_session), \
             patch('main.create_user', return_value=test_user), \
             patch('main.settings') as mock_settings:
            
            mock_settings.JWT_SECRET_KEY = "test-secret-key"
            mock_settings.JWT_ALGORITHM = "HS256"
            mock_settings.JWT_EXPIRATION_HOURS = 24
            
            response = client.post("/auth/register", json={
                "email": "newuser@example.com",
                "password": "test123",
                "consent_version": "1.0",
                "is_anonymous": False
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert data["message"] == "User registered successfully"
            assert "user_id" in data
            assert "access_token" in data
            assert data["token_type"] == "bearer"

