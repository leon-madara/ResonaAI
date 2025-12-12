"""
Unit tests for authentication service functions
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock
import uuid
from datetime import datetime

# Add services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'services', 'api-gateway'))


class TestAuthService:
    """Test authentication service functions"""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        return MagicMock()
    
    @pytest.fixture
    def test_user(self):
        """Create test user object"""
        from database import User
        
        return User(
            id=uuid.uuid4(),
            email="test@example.com",
            password_hash="$2b$12$test_hashed_password",
            consent_version="1.0",
            is_anonymous=False,
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow()
        )
    
    def test_validate_email_valid(self):
        """Test email validation with valid email"""
        from auth_service import validate_email
        
        assert validate_email("test@example.com") is True
        assert validate_email("user.name+tag@domain.co.uk") is True
    
    def test_validate_email_invalid(self):
        """Test email validation with invalid email"""
        from auth_service import validate_email
        
        assert validate_email("invalid-email") is False
        assert validate_email("@example.com") is False
        assert validate_email("test@") is False
        assert validate_email("") is False
    
    def test_validate_password_valid(self):
        """Test password validation with valid password"""
        from auth_service import validate_password
        
        is_valid, error = validate_password("validpass123")
        assert is_valid is True
        assert error == ""
    
    def test_validate_password_too_short(self):
        """Test password validation with too short password"""
        from auth_service import validate_password
        
        is_valid, error = validate_password("short")
        assert is_valid is False
        assert "6 characters" in error.lower()
    
    def test_validate_password_too_long(self):
        """Test password validation with too long password"""
        from auth_service import validate_password
        
        long_password = "a" * 129
        is_valid, error = validate_password(long_password)
        assert is_valid is False
        assert "128 characters" in error.lower()
    
    def test_get_password_hash(self):
        """Test password hashing"""
        from auth_service import get_password_hash
        
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different (bcrypt uses salt)
        assert hash1 != hash2
        # But both should be strings
        assert isinstance(hash1, str)
        assert isinstance(hash2, str)
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        from auth_service import get_password_hash, verify_password
        
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        from auth_service import get_password_hash, verify_password
        
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password("wrongpassword", hashed) is False
    
    def test_get_user_by_email_exists(self, mock_db, test_user):
        """Test getting user by email when user exists"""
        from auth_service import get_user_by_email
        
        mock_db.query.return_value.filter.return_value.first.return_value = test_user
        
        user = get_user_by_email(mock_db, "test@example.com")
        
        assert user is not None
        assert user.email == "test@example.com"
    
    def test_get_user_by_email_not_exists(self, mock_db):
        """Test getting user by email when user doesn't exist"""
        from auth_service import get_user_by_email
        
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        user = get_user_by_email(mock_db, "nonexistent@example.com")
        
        assert user is None
    
    def test_create_user_success(self, mock_db):
        """Test successful user creation"""
        from auth_service import create_user
        from database import User
        
        mock_db.query.return_value.filter.return_value.first.return_value = None  # No existing user
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        user = create_user(
            db=mock_db,
            email="newuser@example.com",
            password="testpass123",
            consent_version="1.0",
            is_anonymous=False
        )
        
        assert user is not None
        assert user.email == "newuser@example.com"
        assert user.password_hash is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_create_user_duplicate_email(self, mock_db, test_user):
        """Test user creation with duplicate email"""
        from auth_service import create_user
        
        mock_db.query.return_value.filter.return_value.first.return_value = test_user  # Existing user
        
        with pytest.raises(ValueError, match="already exists"):
            create_user(
                db=mock_db,
                email="test@example.com",
                password="testpass123",
                consent_version="1.0"
            )
    
    def test_create_user_invalid_email(self, mock_db):
        """Test user creation with invalid email"""
        from auth_service import create_user
        
        with pytest.raises(ValueError, match="email"):
            create_user(
                db=mock_db,
                email="invalid-email",
                password="testpass123",
                consent_version="1.0"
            )
    
    def test_authenticate_user_success(self, mock_db, test_user):
        """Test successful authentication"""
        from auth_service import authenticate_user, get_password_hash
        
        # Set password hash
        test_user.password_hash = get_password_hash("testpassword123")
        
        mock_db.query.return_value.filter.return_value.first.return_value = test_user
        mock_db.commit = Mock()
        
        user = authenticate_user(mock_db, "test@example.com", "testpassword123")
        
        assert user is not None
        assert user.email == "test@example.com"
        mock_db.commit.assert_called_once()  # Should update last_active
    
    def test_authenticate_user_wrong_password(self, mock_db, test_user):
        """Test authentication with wrong password"""
        from auth_service import authenticate_user, get_password_hash
        
        test_user.password_hash = get_password_hash("correctpassword")
        
        mock_db.query.return_value.filter.return_value.first.return_value = test_user
        
        user = authenticate_user(mock_db, "test@example.com", "wrongpassword")
        
        assert user is None
    
    def test_authenticate_user_not_exists(self, mock_db):
        """Test authentication when user doesn't exist"""
        from auth_service import authenticate_user
        
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        user = authenticate_user(mock_db, "nonexistent@example.com", "password")
        
        assert user is None

