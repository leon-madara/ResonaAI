"""
Emotion Repository
Handles database operations for emotion history
"""

import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from decimal import Decimal

from models.database_models import EmotionHistory

logger = logging.getLogger(__name__)


class EmotionRepository:
    """Repository for emotion history database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_emotion_record(
        self,
        user_id: UUID,
        emotion_type: str,
        confidence_score: float,
        voice_emotion: Optional[Dict[str, Any]] = None,
        text_sentiment: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[UUID] = None,
        message_id: Optional[UUID] = None
    ) -> EmotionHistory:
        """
        Create a new emotion history record
        
        Args:
            user_id: User ID
            emotion_type: Type of emotion detected
            confidence_score: Confidence score (0-1)
            voice_emotion: Optional voice emotion data
            text_sentiment: Optional text sentiment data
            conversation_id: Optional conversation ID
            message_id: Optional message ID
            
        Returns:
            EmotionHistory model instance
        """
        try:
            emotion_record = EmotionHistory(
                user_id=user_id,
                conversation_id=conversation_id,
                message_id=message_id,
                emotion_type=emotion_type,
                confidence_score=Decimal(str(confidence_score)),
                voice_emotion=voice_emotion,
                text_sentiment=text_sentiment
            )
            self.db.add(emotion_record)
            self.db.commit()
            self.db.refresh(emotion_record)
            logger.info(f"Created emotion record for user {user_id}, emotion {emotion_type}")
            return emotion_record
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating emotion record: {e}")
            raise
    
    def get_emotion_record(self, emotion_id: UUID) -> Optional[EmotionHistory]:
        """Get emotion record by ID"""
        return self.db.query(EmotionHistory).filter(EmotionHistory.id == emotion_id).first()
    
    def get_user_emotion_history(
        self,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0
    ) -> List[EmotionHistory]:
        """
        Get user's emotion history ordered by most recent
        
        Args:
            user_id: User ID
            limit: Maximum number of records
            offset: Number of records to skip
            
        Returns:
            List of EmotionHistory instances
        """
        return (
            self.db.query(EmotionHistory)
            .filter(EmotionHistory.user_id == user_id)
            .order_by(desc(EmotionHistory.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )
    
    def get_conversation_emotions(
        self,
        conversation_id: UUID
    ) -> List[EmotionHistory]:
        """
        Get all emotion records for a conversation
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List of EmotionHistory instances
        """
        return (
            self.db.query(EmotionHistory)
            .filter(EmotionHistory.conversation_id == conversation_id)
            .order_by(EmotionHistory.created_at)
            .all()
        )
    
    def get_recent_emotions(
        self,
        user_id: UUID,
        limit: int = 10
    ) -> List[EmotionHistory]:
        """
        Get most recent emotion records for a user
        
        Args:
            user_id: User ID
            limit: Maximum number of records
            
        Returns:
            List of EmotionHistory instances
        """
        return (
            self.db.query(EmotionHistory)
            .filter(EmotionHistory.user_id == user_id)
            .order_by(desc(EmotionHistory.created_at))
            .limit(limit)
            .all()
        )

