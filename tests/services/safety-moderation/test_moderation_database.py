"""
Database integration tests for Safety Moderation Service
"""

import pytest
import sys
import os
from uuid import uuid4

# Add service directory to path
service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'apps', 'backend', 'services', 'safety-moderation'))
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

# Clear cached module names that collide across services (gateway also has `models`).
for mod_name in ["models", "models.database_models", "repositories", "repositories.moderation_repository"]:
    if mod_name in sys.modules:
        del sys.modules[mod_name]

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import after path setup
from models.database_models import Base, ModerationLog
from repositories.moderation_repository import ModerationRepository


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


class TestModerationRepository:
    """Test ModerationRepository database operations"""
    
    def test_create_moderation_log(self, test_db):
        """Test creating a moderation log"""
        repo = ModerationRepository(test_db)
        
        log = repo.create_moderation_log(
            moderation_type="content_filter",
            action_taken="block",
            flagged_content="test content",
            confidence_score=0.9
        )
        
        assert log.id is not None
        assert log.moderation_type == "content_filter"
        assert log.action_taken == "block"
        assert log.flagged_content == "test content"
        assert float(log.confidence_score) == 0.9
        assert log.human_reviewed is False

    def test_create_moderation_log_with_attribution(self, test_db):
        """Test creating a moderation log with identity attribution"""
        repo = ModerationRepository(test_db)

        user_id = uuid4()
        reviewer_id = uuid4()

        log = repo.create_moderation_log(
            moderation_type="content_filter",
            action_taken="review",
            user_id=user_id,
            reviewer_id=reviewer_id,
            flagged_content="flagged content",
            confidence_score=0.5,
        )

        assert log.user_id == user_id
        assert log.reviewer_id == reviewer_id
    
    def test_get_moderation_log(self, test_db):
        """Test retrieving a moderation log by ID"""
        repo = ModerationRepository(test_db)
        
        # Create log
        created = repo.create_moderation_log(
            moderation_type="hallucination_detector",
            action_taken="review",
            confidence_score=0.7
        )
        
        # Retrieve it
        retrieved = repo.get_moderation_log(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.action_taken == "review"
    
    def test_get_unreviewed_logs(self, test_db):
        """Test retrieving unreviewed moderation logs"""
        repo = ModerationRepository(test_db)
        
        # Create logs
        repo.create_moderation_log(
            moderation_type="content_filter",
            action_taken="block"
        )
        repo.create_moderation_log(
            moderation_type="content_filter",
            action_taken="allow"
        )
        
        # Mark one as reviewed
        log1 = repo.get_moderation_log(repo.get_unreviewed_logs()[0].id)
        repo.mark_as_reviewed(log1.id)
        
        # Get unreviewed
        unreviewed = repo.get_unreviewed_logs()
        
        assert len(unreviewed) == 1
    
    def test_get_blocked_content(self, test_db):
        """Test retrieving blocked content logs"""
        repo = ModerationRepository(test_db)
        
        # Create logs with different actions
        repo.create_moderation_log(
            moderation_type="content_filter",
            action_taken="block"
        )
        repo.create_moderation_log(
            moderation_type="content_filter",
            action_taken="allow"
        )
        
        # Get blocked content
        blocked = repo.get_blocked_content()
        
        assert len(blocked) == 1
        assert blocked[0].action_taken == "block"

