"""
Pytest configuration and shared fixtures for all tests
"""

import pytest
import os
import sys
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
import jwt
from datetime import datetime, timedelta

# Add services to path
services_path = os.path.join(os.path.dirname(__file__), '..', 'apps', 'backend', 'gateway')
if services_path not in sys.path:
    sys.path.insert(0, services_path)

# Add repo root to path for shared `src.*` imports
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Test settings
TEST_JWT_SECRET_KEY = "test-secret-key-for-testing-only"
TEST_JWT_ALGORITHM = "HS256"


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine


@pytest.fixture(scope="function")
def test_db(test_engine) -> Generator[Session, None, None]:
    """Create test database session"""
    # Import here to avoid circular imports
    import importlib.util
    # Clear potentially-colliding top-level modules from other service tests.
    for mod_name in list(sys.modules.keys()):
        if mod_name == "models" or mod_name.startswith("models."):
            del sys.modules[mod_name]
        if mod_name == "repositories" or mod_name.startswith("repositories."):
            del sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location("database", os.path.join(os.path.dirname(__file__), '..', 'apps', 'backend', 'gateway', 'database.py'))
    database_module = importlib.util.module_from_spec(spec)
    # Ensure imports like `from database import Base` resolve to this in-memory module.
    sys.modules["database"] = database_module
    spec.loader.exec_module(database_module)
    Base = database_module.Base
    
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def test_user(test_db):
    """Create a test user"""
    import importlib.util
    import uuid
    
    # Import database module
    db_spec = importlib.util.spec_from_file_location("database", os.path.join(os.path.dirname(__file__), '..', 'apps', 'backend', 'gateway', 'database.py'))
    db_module = importlib.util.module_from_spec(db_spec)
    sys.modules["database"] = db_module
    db_spec.loader.exec_module(db_module)
    User = db_module.User
    
    # Import auth_service
    auth_spec = importlib.util.spec_from_file_location("auth_service", os.path.join(os.path.dirname(__file__), '..', 'apps', 'backend', 'gateway', 'auth_service.py'))
    auth_module = importlib.util.module_from_spec(auth_spec)
    sys.modules["auth_service"] = auth_module
    auth_spec.loader.exec_module(auth_module)
    get_password_hash = auth_module.get_password_hash
    
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        consent_version="1.0",
        is_anonymous=False,
        created_at=datetime.utcnow(),
        last_active=datetime.utcnow()
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user) -> str:
    """Generate a test JWT token"""
    token_data = {
        "user_id": str(test_user.id),
        "email": test_user.email,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(token_data, TEST_JWT_SECRET_KEY, algorithm=TEST_JWT_ALGORITHM)


@pytest.fixture
def api_gateway_client():
    """Create test client for API Gateway"""
    import importlib.util
    
    # Mock environment variables
    with patch.dict(os.environ, {
        "JWT_SECRET_KEY": TEST_JWT_SECRET_KEY,
        "DATABASE_URL": TEST_DATABASE_URL,
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
    }):
        # Import main module
        main_spec = importlib.util.spec_from_file_location("main", os.path.join(os.path.dirname(__file__), '..', 'apps', 'backend', 'gateway', 'main.py'))
        main_module = importlib.util.module_from_spec(main_spec)
        main_spec.loader.exec_module(main_module)
        return TestClient(main_module.app)


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    mock_redis = Mock()
    mock_redis.ping.return_value = True
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.incr.return_value = 1
    mock_redis.expire.return_value = True
    return mock_redis


@pytest.fixture
def mock_http_client():
    """Mock HTTP client for service calls"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {"status": "ok"}
    mock_response.raise_for_status = Mock()
    mock_client.request = AsyncMock(return_value=mock_response)
    return mock_client


@pytest.fixture
def sample_audio_file():
    """Create sample audio file for testing"""
    import io
    import numpy as np
    import soundfile as sf
    
    # Generate 2 seconds of audio
    duration = 2.0
    sample_rate = 16000
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = 0.5 * np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave
    
    # Save to bytes buffer
    buffer = io.BytesIO()
    sf.write(buffer, audio, sample_rate, format='WAV')
    buffer.seek(0)
    
    return ("audio.wav", buffer.getvalue(), "audio/wav")


@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset all mocks before each test"""
    yield
    # Cleanup if needed

