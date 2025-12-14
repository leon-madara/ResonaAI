"""
Unit tests for API Gateway authentication endpoints
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
import jwt
from datetime import datetime, timedelta

# Add services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'apps', 'backend', 'gateway'))


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client with mocked dependencies"""
        # Ensure a clean import of the gateway app with deterministic settings/mocks.
        for mod_name in list(sys.modules.keys()):
            if mod_name in ["main", "config"] or mod_name.startswith("middleware."):
                del sys.modules[mod_name]

        with patch.dict(os.environ, {
            "JWT_SECRET_KEY": "test-secret-key",
            "JWT_ALGORITHM": "HS256",
            "JWT_EXPIRATION_HOURS": "24",
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "6379",
        }), patch("redis.Redis") as mock_redis_cls, patch("httpx.AsyncClient") as mock_httpx_cls:

            # Redis mock used by rate limiter middleware
            mock_redis = Mock()
            mock_pipe = Mock()
            mock_pipe.zremrangebyscore.return_value = None
            mock_pipe.zcard.return_value = None
            mock_pipe.zadd.return_value = None
            mock_pipe.expire.return_value = None
            mock_pipe.execute.return_value = [None, 0, None, None]
            mock_redis.pipeline.return_value = mock_pipe
            mock_redis.zcount.return_value = 0
            mock_redis.ping.return_value = True
            mock_redis_cls.return_value = mock_redis

            # httpx client mock used by gateway routing
            mock_http = AsyncMock()
            mock_http.aclose = AsyncMock()
            mock_httpx_cls.return_value = mock_http

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
        """Test successful login (mocked auth + mocked DB)."""
        fake_user = Mock()
        fake_user.id = "user-123"
        fake_user.email = "test@example.com"

        with patch('main.get_db', return_value=mock_db_session), \
             patch('main.authenticate_user', return_value=fake_user), \
             patch('main.settings') as mock_settings:

            mock_settings.JWT_SECRET_KEY = "test-secret-key"
            mock_settings.JWT_ALGORITHM = "HS256"
            mock_settings.JWT_EXPIRATION_HOURS = 24

            response = client.post(
                "/auth/login",
                json={"email": "test@example.com", "password": "testpassword123"}
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
        """Test successful registration (mocked create_user + mocked email + mocked DB)."""
        fake_user = Mock()
        fake_user.id = "user-456"
        fake_user.email = "newuser@example.com"

        with patch('main.get_db', return_value=mock_db_session), \
             patch('main.create_user', return_value=fake_user), \
             patch('main.get_email_service') as mock_email, \
             patch('main.settings') as mock_settings:

            # Mock email service to avoid actual email sending
            mock_email_service = Mock()
            mock_email_service.generate_verification_token.return_value = "test-token"
            mock_email_service.send_verification_email = AsyncMock(return_value=True)
            mock_email.return_value = mock_email_service

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
            assert "user_id" in data
            assert data["email"] == "newuser@example.com"
            assert "access_token" in data
            assert data["token_type"] == "bearer"

