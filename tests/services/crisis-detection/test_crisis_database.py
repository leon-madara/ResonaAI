"""
Database integration tests for Crisis Detection Service
"""

import pytest
import sys
import os
from uuid import uuid4
from datetime import datetime
import importlib.util
import types

# Add service directory to path
service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'apps', 'backend', 'services', 'crisis-detection'))
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import after path setup
models_spec = importlib.util.spec_from_file_location(
    "crisis_detection_models",
    os.path.join(service_dir, "models", "database_models.py"),
)
models_module = importlib.util.module_from_spec(models_spec)
assert models_spec.loader is not None
models_spec.loader.exec_module(models_module)
Base = models_module.Base
CrisisEvent = models_module.CrisisEvent

# Ensure service-local `models.database_models` resolves for repository imports.
models_pkg = types.ModuleType("models")
models_pkg.database_models = models_module
sys.modules["models"] = models_pkg
sys.modules["models.database_models"] = models_module

repo_spec = importlib.util.spec_from_file_location(
    "crisis_detection_repo",
    os.path.join(service_dir, "repositories", "crisis_repository.py"),
)
repo_module = importlib.util.module_from_spec(repo_spec)
assert repo_spec.loader is not None
repo_spec.loader.exec_module(repo_module)
CrisisRepository = repo_module.CrisisRepository


@pytest.fixture
def test_db():
    """Create test database session"""
    # Use in-memory SQLite for testing
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


class TestCrisisRepository:
    """Test CrisisRepository database operations"""
    
    def test_create_crisis_event(self, test_db, test_user_id):
        """Test creating a crisis event"""
        repo = CrisisRepository(test_db)
        
        crisis_event = repo.create_crisis_event(
            user_id=test_user_id,
            risk_level="high",
            detection_method="keyword_detection",
            escalation_required=True
        )
        
        assert crisis_event.id is not None
        assert crisis_event.user_id == test_user_id
        assert crisis_event.risk_level == "high"
        assert crisis_event.detection_method == "keyword_detection"
        assert crisis_event.escalation_required is True
        assert crisis_event.human_reviewed is False
    
    def test_get_crisis_event(self, test_db, test_user_id):
        """Test retrieving a crisis event by ID"""
        repo = CrisisRepository(test_db)
        
        # Create event
        created = repo.create_crisis_event(
            user_id=test_user_id,
            risk_level="critical",
            detection_method="sentiment_analysis"
        )
        
        # Retrieve it
        retrieved = repo.get_crisis_event(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.risk_level == "critical"
    
    def test_get_user_crisis_events(self, test_db, test_user_id):
        """Test retrieving user's crisis events"""
        repo = CrisisRepository(test_db)
        
        # Create multiple events
        repo.create_crisis_event(
            user_id=test_user_id,
            risk_level="low",
            detection_method="method1"
        )
        repo.create_crisis_event(
            user_id=test_user_id,
            risk_level="medium",
            detection_method="method2"
        )
        
        # Get user events
        events = repo.get_user_crisis_events(test_user_id)
        
        assert len(events) == 2
        assert all(e.user_id == test_user_id for e in events)
    
    def test_mark_as_reviewed(self, test_db, test_user_id):
        """Test marking crisis event as reviewed"""
        repo = CrisisRepository(test_db)
        
        # Create event
        event = repo.create_crisis_event(
            user_id=test_user_id,
            risk_level="high",
            detection_method="test"
        )
        
        assert event.human_reviewed is False
        
        # Mark as reviewed
        result = repo.mark_as_reviewed(event.id)
        
        assert result is True
        retrieved = repo.get_crisis_event(event.id)
        assert retrieved.human_reviewed is True
    
    def test_get_escalation_required_events(self, test_db, test_user_id):
        """Test retrieving events requiring escalation"""
        repo = CrisisRepository(test_db)
        
        # Create events with and without escalation
        repo.create_crisis_event(
            user_id=test_user_id,
            risk_level="high",
            detection_method="test1",
            escalation_required=True
        )
        repo.create_crisis_event(
            user_id=test_user_id,
            risk_level="low",
            detection_method="test2",
            escalation_required=False
        )
        
        # Get escalation required events
        events = repo.get_escalation_required_events()
        
        assert len(events) == 1
        assert events[0].escalation_required is True

