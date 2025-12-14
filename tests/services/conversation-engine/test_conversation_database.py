"""
Database integration tests for Conversation Engine Service
"""

import pytest
import sys
import os
from uuid import uuid4

# Add service directory to path
service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'apps', 'backend', 'services', 'conversation-engine'))
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import after path setup
from models.database_models import Base, Conversation, Message
from repositories.conversation_repository import ConversationRepository


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


class TestConversationRepository:
    """Test ConversationRepository database operations"""
    
    def test_create_conversation(self, test_db, test_user_id):
        """Test creating a conversation"""
        repo = ConversationRepository(test_db)
        
        conversation = repo.create_conversation(
            user_id=test_user_id,
            emotion_summary={"emotion": "neutral"}
        )
        
        assert conversation.id is not None
        assert conversation.user_id == test_user_id
        assert conversation.crisis_detected is False
        assert conversation.escalated_to_human is False
    
    def test_get_conversation(self, test_db, test_user_id):
        """Test retrieving a conversation by ID"""
        repo = ConversationRepository(test_db)
        
        # Create conversation
        created = repo.create_conversation(user_id=test_user_id)
        
        # Retrieve it
        retrieved = repo.get_conversation(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.user_id == test_user_id
    
    def test_create_message(self, test_db, test_user_id):
        """Test creating a message in a conversation"""
        repo = ConversationRepository(test_db)
        
        # Create conversation first
        conversation = repo.create_conversation(user_id=test_user_id)
        
        # Create message
        message = repo.create_message(
            conversation_id=conversation.id,
            message_type="user",
            encrypted_content=b"test message",
            emotion_data={"emotion": "sad"}
        )
        
        assert message.id is not None
        assert message.conversation_id == conversation.id
        assert message.message_type == "user"
        assert message.encrypted_content == b"test message"
    
    def test_get_conversation_messages(self, test_db, test_user_id):
        """Test retrieving messages for a conversation"""
        repo = ConversationRepository(test_db)
        
        # Create conversation
        conversation = repo.create_conversation(user_id=test_user_id)
        
        # Create multiple messages
        repo.create_message(
            conversation_id=conversation.id,
            message_type="user",
            encrypted_content=b"message 1"
        )
        repo.create_message(
            conversation_id=conversation.id,
            message_type="ai",
            encrypted_content=b"message 2"
        )
        
        # Get messages
        messages = repo.get_conversation_messages(conversation.id)
        
        assert len(messages) == 2
        assert messages[0].message_type == "user"
        assert messages[1].message_type == "ai"
    
    def test_update_conversation(self, test_db, test_user_id):
        """Test updating a conversation"""
        repo = ConversationRepository(test_db)
        
        # Create conversation
        conversation = repo.create_conversation(user_id=test_user_id)
        
        # Update it
        result = repo.update_conversation(
            conversation_id=conversation.id,
            crisis_detected=True,
            escalated_to_human=True
        )
        
        assert result is True
        updated = repo.get_conversation(conversation.id)
        assert updated.crisis_detected is True
        assert updated.escalated_to_human is True

