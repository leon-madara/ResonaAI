"""
Database integration tests for Emotion Analysis Service
"""

import pytest
import sys
import os
from uuid import uuid4
from decimal import Decimal
import importlib.util
import types

# Add service directory to path
service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'apps', 'backend', 'services', 'emotion-analysis'))
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import after path setup (avoid cross-service module cache collisions)
models_spec = importlib.util.spec_from_file_location(
    "emotion_analysis_models",
    os.path.join(service_dir, "models", "database_models.py"),
)
models_module = importlib.util.module_from_spec(models_spec)
assert models_spec.loader is not None
models_spec.loader.exec_module(models_module)
Base = models_module.Base
EmotionHistory = models_module.EmotionHistory

models_pkg = types.ModuleType("models")
models_pkg.database_models = models_module
sys.modules["models"] = models_pkg
sys.modules["models.database_models"] = models_module

repo_spec = importlib.util.spec_from_file_location(
    "emotion_analysis_repo",
    os.path.join(service_dir, "repositories", "emotion_repository.py"),
)
repo_module = importlib.util.module_from_spec(repo_spec)
assert repo_spec.loader is not None
repo_spec.loader.exec_module(repo_module)
EmotionRepository = repo_module.EmotionRepository


@pytest.fixture
def test_db():
    """Create test database session"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user_id():
    """Create a test user ID"""
    return uuid4()


class TestEmotionRepository:
    """Test EmotionRepository database operations"""
    
    def test_create_emotion_record(self, test_db, test_user_id):
        """Test creating an emotion history record"""
        repo = EmotionRepository(test_db)
        
        emotion_record = repo.create_emotion_record(
            user_id=test_user_id,
            emotion_type="sad",
            confidence_score=0.85,
            voice_emotion={"sad": 0.85, "neutral": 0.15}
        )
        
        assert emotion_record.id is not None
        assert emotion_record.user_id == test_user_id
        assert emotion_record.emotion_type == "sad"
        assert float(emotion_record.confidence_score) == 0.85
    
    def test_get_emotion_record(self, test_db, test_user_id):
        """Test retrieving an emotion record by ID"""
        repo = EmotionRepository(test_db)
        
        # Create record
        created = repo.create_emotion_record(
            user_id=test_user_id,
            emotion_type="happy",
            confidence_score=0.9
        )
        
        # Retrieve it
        retrieved = repo.get_emotion_record(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.emotion_type == "happy"
    
    def test_get_user_emotion_history(self, test_db, test_user_id):
        """Test retrieving user's emotion history"""
        repo = EmotionRepository(test_db)
        
        # Create multiple records
        repo.create_emotion_record(
            user_id=test_user_id,
            emotion_type="sad",
            confidence_score=0.8
        )
        repo.create_emotion_record(
            user_id=test_user_id,
            emotion_type="happy",
            confidence_score=0.7
        )
        
        # Get user history
        history = repo.get_user_emotion_history(test_user_id)
        
        assert len(history) == 2
        assert all(e.user_id == test_user_id for e in history)
    
    def test_get_recent_emotions(self, test_db, test_user_id):
        """Test retrieving recent emotion records"""
        repo = EmotionRepository(test_db)
        
        # Create multiple records
        for i in range(5):
            repo.create_emotion_record(
                user_id=test_user_id,
                emotion_type="neutral",
                confidence_score=0.5
            )
        
        # Get recent (limit 3)
        recent = repo.get_recent_emotions(test_user_id, limit=3)
        
        assert len(recent) == 3

