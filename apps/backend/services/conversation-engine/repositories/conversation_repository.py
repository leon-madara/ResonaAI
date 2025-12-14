"""
Conversation Repository
Handles database operations for conversations and messages
"""

import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timezone

from models.database_models import Conversation, Message

logger = logging.getLogger(__name__)


class ConversationRepository:
    """Repository for conversation-related database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_conversation(
        self,
        user_id: UUID,
        emotion_summary: Optional[Dict[str, Any]] = None
    ) -> Conversation:
        """
        Create a new conversation
        
        Args:
            user_id: User ID
            emotion_summary: Optional initial emotion summary
            
        Returns:
            Conversation model instance
        """
        try:
            conversation = Conversation(
                user_id=user_id,
                started_at=datetime.now(timezone.utc),
                emotion_summary=emotion_summary,
                crisis_detected=False,
                escalated_to_human=False
            )
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)
            logger.info(f"Created conversation {conversation.id} for user {user_id}")
            return conversation
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating conversation: {e}")
            raise
    
    def get_conversation(self, conversation_id: UUID) -> Optional[Conversation]:
        """Get conversation by ID"""
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    def get_user_conversations(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[Conversation]:
        """
        Get user's conversations ordered by most recent
        
        Args:
            user_id: User ID
            limit: Maximum number of conversations
            offset: Number of conversations to skip
            
        Returns:
            List of Conversation instances
        """
        return (
            self.db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(desc(Conversation.started_at))
            .limit(limit)
            .offset(offset)
            .all()
        )
    
    def update_conversation(
        self,
        conversation_id: UUID,
        emotion_summary: Optional[Dict[str, Any]] = None,
        crisis_detected: Optional[bool] = None,
        escalated_to_human: Optional[bool] = None,
        ended_at: Optional[datetime] = None
    ) -> bool:
        """
        Update conversation
        
        Args:
            conversation_id: Conversation ID
            emotion_summary: Optional emotion summary to update
            crisis_detected: Optional crisis detected flag
            escalated_to_human: Optional escalation flag
            ended_at: Optional end timestamp
            
        Returns:
            True if successful
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        if emotion_summary is not None:
            conversation.emotion_summary = emotion_summary
        if crisis_detected is not None:
            conversation.crisis_detected = crisis_detected
        if escalated_to_human is not None:
            conversation.escalated_to_human = escalated_to_human
        if ended_at is not None:
            conversation.ended_at = ended_at
        
        self.db.commit()
        return True
    
    def create_message(
        self,
        conversation_id: UUID,
        message_type: str,
        encrypted_content: bytes,
        emotion_data: Optional[Dict[str, Any]] = None
    ) -> Message:
        """
        Create a new message in a conversation
        
        Args:
            conversation_id: Conversation ID
            message_type: Message type ('user' or 'ai')
            encrypted_content: Encrypted message content
            emotion_data: Optional emotion data
            
        Returns:
            Message model instance
        """
        try:
            message = Message(
                conversation_id=conversation_id,
                message_type=message_type,
                encrypted_content=encrypted_content,
                emotion_data=emotion_data
            )
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            logger.info(f"Created message {message.id} in conversation {conversation_id}")
            return message
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating message: {e}")
            raise
    
    def get_conversation_messages(
        self,
        conversation_id: UUID,
        limit: int = 100
    ) -> List[Message]:
        """
        Get all messages for a conversation
        
        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages
            
        Returns:
            List of Message instances ordered by creation time
        """
        return (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .limit(limit)
            .all()
        )
    
    def get_message(self, message_id: UUID) -> Optional[Message]:
        """Get message by ID"""
        return self.db.query(Message).filter(Message.id == message_id).first()

