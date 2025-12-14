"""
Integration tests for authentication flow
Tests the complete flow: register -> login -> protected route
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
import jwt
from datetime import datetime, timedelta

# Add services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'apps', 'backend', 'gateway'))


@pytest.mark.integration
class TestAuthFlow:
    """Integration tests for authentication flow"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        with patch('main.redis_client') as mock_redis, \
             patch('main.health_checker') as mock_health, \
             patch('main.http_client') as mock_http:
            
            mock_redis.ping.return_value = True
            mock_health.check_all_services = Mock(return_value={})
            
            from main import app
            return TestClient(app)
    
    @pytest.fixture
    def test_db(self):
        """Create test database session"""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from database import Base
        
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        yield session
        
        session.close()
        Base.metadata.drop_all(engine)
    
    def test_complete_auth_flow(self, client, test_db):
        """Test complete authentication flow: register -> login -> use token"""
        from auth_service import create_user, authenticate_user
        from database import User
        import uuid
        
        # Step 1: Register a new user
        with patch('main.get_db', return_value=test_db), \
             patch('main.settings') as mock_settings:
            
            mock_settings.JWT_SECRET_KEY = "test-secret-key"
            mock_settings.JWT_ALGORITHM = "HS256"
            mock_settings.JWT_EXPIRATION_HOURS = 24
            
            register_response = client.post("/auth/register", json={
                "email": "newuser@example.com",
                "password": "testpass123",
                "consent_version": "1.0",
                "is_anonymous": False
            })
            
            assert register_response.status_code == 200
            register_data = register_response.json()
            assert "access_token" in register_data
            assert "user_id" in register_data
            
            token = register_data["access_token"]
            user_id = register_data["user_id"]
        
        # Step 2: Use the token to access a protected endpoint
        with patch('main.http_client') as mock_http:
            mock_response = Mock()
            mock_response.json.return_value = {"transcript": "test"}
            mock_response.raise_for_status = Mock()
            mock_http.request = AsyncMock(return_value=mock_response)
            
            protected_response = client.post(
                "/speech/transcribe",
                headers={"Authorization": f"Bearer {token}"},
                json={"audio": "base64"}
            )
            
            # Should be able to access protected route with valid token
            assert protected_response.status_code in [200, 503, 504]  # 503/504 if service unavailable
    
    def test_login_after_registration(self, client, test_db):
        """Test logging in after registration"""
        from auth_service import create_user
        from database import User
        import uuid
        
        # Register user
        with patch('main.get_db', return_value=test_db), \
             patch('main.settings') as mock_settings:
            
            mock_settings.JWT_SECRET_KEY = "test-secret-key"
            mock_settings.JWT_ALGORITHM = "HS256"
            mock_settings.JWT_EXPIRATION_HOURS = 24
            
            # Register
            register_response = client.post("/auth/register", json={
                "email": "loginuser@example.com",
                "password": "loginpass123",
                "consent_version": "1.0"
            })
            
            assert register_response.status_code == 200
        
        # Login with same credentials
        with patch('main.get_db', return_value=test_db), \
             patch('main.settings') as mock_settings:
            
            mock_settings.JWT_SECRET_KEY = "test-secret-key"
            mock_settings.JWT_ALGORITHM = "HS256"
            mock_settings.JWT_EXPIRATION_HOURS = 24
            
            login_response = client.post("/auth/login", json={
                "email": "loginuser@example.com",
                "password": "loginpass123"
            })
            
            assert login_response.status_code == 200
            login_data = login_response.json()
            assert "access_token" in login_data
            assert login_data["token_type"] == "bearer"
    
    def test_invalid_token_rejected(self, client):
        """Test that invalid tokens are rejected"""
        # Try to access protected route with invalid token
        response = client.post(
            "/speech/transcribe",
            headers={"Authorization": "Bearer invalid-token"},
            json={"audio": "base64"}
        )
        
        # Should be rejected (403 or 401)
        assert response.status_code in [401, 403]
    
    def test_expired_token_rejected(self, client):
        """Test that expired tokens are rejected"""
        # Create expired token
        expired_token = jwt.encode(
            {
                "user_id": "test-user",
                "email": "test@example.com",
                "exp": datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
            },
            "test-secret-key",
            algorithm="HS256"
        )
        
        response = client.post(
            "/speech/transcribe",
            headers={"Authorization": f"Bearer {expired_token}"},
            json={"audio": "base64"}
        )
        
        # Should be rejected
        assert response.status_code in [401, 403]

