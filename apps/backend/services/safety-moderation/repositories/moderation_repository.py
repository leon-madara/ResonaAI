"""
Moderation Repository
Handles database operations for moderation logs
"""

import logging
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc
from decimal import Decimal

from models.database_models import ModerationLog

logger = logging.getLogger(__name__)


class ModerationRepository:
    """Repository for moderation log database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_moderation_log(
        self,
        moderation_type: str,
        action_taken: str,
        user_id: Optional[UUID] = None,
        reviewer_id: Optional[UUID] = None,
        message_id: Optional[UUID] = None,
        flagged_content: Optional[str] = None,
        confidence_score: Optional[float] = None
    ) -> ModerationLog:
        """
        Create a new moderation log entry
        
        Args:
            moderation_type: Type of moderation (e.g., 'content_filter', 'hallucination_detector')
            action_taken: Action taken ('allow', 'block', 'review')
            message_id: Optional message ID
            flagged_content: Optional flagged content text
            confidence_score: Optional confidence score (0-1)
            
        Returns:
            ModerationLog model instance
        """
        try:
            moderation_log = ModerationLog(
                user_id=user_id,
                reviewer_id=reviewer_id,
                message_id=message_id,
                moderation_type=moderation_type,
                action_taken=action_taken,
                flagged_content=flagged_content,
                confidence_score=Decimal(str(confidence_score)) if confidence_score is not None else None,
                human_reviewed=False
            )
            self.db.add(moderation_log)
            self.db.commit()
            self.db.refresh(moderation_log)
            logger.info(f"Created moderation log, type {moderation_type}, action {action_taken}")
            return moderation_log
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating moderation log: {e}")
            raise
    
    def get_moderation_log(self, log_id: UUID) -> Optional[ModerationLog]:
        """Get moderation log by ID"""
        return self.db.query(ModerationLog).filter(ModerationLog.id == log_id).first()
    
    def get_message_moderation_logs(
        self,
        message_id: UUID
    ) -> List[ModerationLog]:
        """
        Get all moderation logs for a message
        
        Args:
            message_id: Message ID
            
        Returns:
            List of ModerationLog instances
        """
        return (
            self.db.query(ModerationLog)
            .filter(ModerationLog.message_id == message_id)
            .order_by(desc(ModerationLog.created_at))
            .all()
        )
    
    def get_unreviewed_logs(
        self,
        limit: int = 100
    ) -> List[ModerationLog]:
        """
        Get unreviewed moderation logs
        
        Args:
            limit: Maximum number of logs
            
        Returns:
            List of unreviewed ModerationLog instances
        """
        return (
            self.db.query(ModerationLog)
            .filter(ModerationLog.human_reviewed == False)
            .order_by(desc(ModerationLog.created_at))
            .limit(limit)
            .all()
        )
    
    def mark_as_reviewed(self, log_id: UUID) -> bool:
        """
        Mark moderation log as human reviewed
        
        Args:
            log_id: Moderation log ID
            
        Returns:
            True if successful
        """
        moderation_log = self.get_moderation_log(log_id)
        if not moderation_log:
            return False
        
        moderation_log.human_reviewed = True
        self.db.commit()
        return True
    
    def get_blocked_content(
        self,
        limit: int = 100
    ) -> List[ModerationLog]:
        """
        Get all blocked content logs
        
        Args:
            limit: Maximum number of logs
            
        Returns:
            List of ModerationLog instances with action 'block'
        """
        return (
            self.db.query(ModerationLog)
            .filter(ModerationLog.action_taken == 'block')
            .order_by(desc(ModerationLog.created_at))
            .limit(limit)
            .all()
        )

