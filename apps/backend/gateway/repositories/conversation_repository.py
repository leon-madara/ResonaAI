"""
Conversation Repository
Handles database operations for conversations and messages
"""

import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime, timezone

from models.encrypted_models import Conversation, Message
from services.encrypted_storage import get_encrypted_storage_service

logger = logging.getLogger(__name__)


class ConversationRepository:
    """Repository for conversation-related database operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.encrypted_storage = get_encrypted_storage_service()
    
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
        return conversation
    
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
            limit: Maximum number of conversations to return
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
    
    def end_conversation(self, conversation_id: UUID) -> bool:
        """
        Mark conversation as ended
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            True if successful
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        conversation.ended_at = datetime.now(timezone.utc)
        self.db.commit()
        return True
    
    def update_emotion_summary(
        self,
        conversation_id: UUID,
        emotion_summary: Dict[str, Any]
    ) -> bool:
        """
        Update conversation emotion summary
        
        Args:
            conversation_id: Conversation ID
            emotion_summary: Emotion summary data
            
        Returns:
            True if successful
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        conversation.emotion_summary = emotion_summary
        self.db.commit()
        return True
    
    def mark_crisis_detected(self, conversation_id: UUID) -> bool:
        """
        Mark conversation as having crisis detected
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            True if successful
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        conversation.crisis_detected = True
        self.db.commit()
        return True
    
    def escalate_to_human(self, conversation_id: UUID) -> bool:
        """
        Mark conversation as escalated to human
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            True if successful
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        conversation.escalated_to_human = True
        self.db.commit()
        return True
    
    async def add_message(
        self,
        conversation_id: UUID,
        message_type: str,
        content: str,
        emotion_data: Optional[Dict[str, Any]] = None
    ) -> Message:
        """
        Add encrypted message to conversation
        
        Args:
            conversation_id: Conversation ID
            message_type: 'user' or 'ai'
            content: Message content
            emotion_data: Optional emotion data
            
        Returns:
            Message model instance
        """
        return await self.encrypted_storage.save_message(
            self.db,
            str(conversation_id),
            message_type,
            content,
            emotion_data
        )
    
    async def get_messages(
        self,
        conversation_id: UUID,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get and decrypt messages for a conversation
        
        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages
            offset: Number of messages to skip
            
        Returns:
            List of decrypted message dictionaries
        """
        messages = (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .limit(limit)
            .offset(offset)
            .all()
        )
        
        decrypted_messages = []
        for message in messages:
            try:
                decrypted = await self.encrypted_storage.get_message(self.db, str(message.id))
                if decrypted:
                    decrypted_messages.append(decrypted)
            except Exception as e:
                logger.error(f"Failed to decrypt message {message.id}: {e}")
        
        return decrypted_messages

