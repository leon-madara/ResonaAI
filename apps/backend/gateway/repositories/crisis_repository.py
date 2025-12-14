"""
Crisis Repository
Handles database operations for crisis events
"""

import logging
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime, timezone

from models.encrypted_models import CrisisEvent

logger = logging.getLogger(__name__)


class CrisisRepository:
    """Repository for crisis event database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_crisis_event(
        self,
        user_id: UUID,
        risk_level: str,
        detection_method: str,
        conversation_id: Optional[UUID] = None,
        escalation_required: bool = False
    ) -> CrisisEvent:
        """
        Create a new crisis event
        
        Args:
            user_id: User ID
            risk_level: Risk level ('low', 'medium', 'high', 'critical')
            detection_method: Method used to detect crisis
            conversation_id: Optional conversation ID
            escalation_required: Whether escalation is required
            
        Returns:
            CrisisEvent model instance
        """
        crisis_event = CrisisEvent(
            user_id=user_id,
            conversation_id=conversation_id,
            risk_level=risk_level,
            detection_method=detection_method,
            escalation_required=escalation_required,
            human_reviewed=False
        )
        self.db.add(crisis_event)
        self.db.commit()
        self.db.refresh(crisis_event)
        return crisis_event
    
    def get_crisis_event(self, crisis_id: UUID) -> Optional[CrisisEvent]:
        """Get crisis event by ID"""
        return self.db.query(CrisisEvent).filter(CrisisEvent.id == crisis_id).first()
    
    def get_user_crisis_events(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[CrisisEvent]:
        """
        Get user's crisis events ordered by most recent
        
        Args:
            user_id: User ID
            limit: Maximum number of events
            offset: Number of events to skip
            
        Returns:
            List of CrisisEvent instances
        """
        return (
            self.db.query(CrisisEvent)
            .filter(CrisisEvent.user_id == user_id)
            .order_by(desc(CrisisEvent.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )
    
    def get_unreviewed_crisis_events(
        self,
        limit: int = 100
    ) -> List[CrisisEvent]:
        """
        Get unreviewed crisis events requiring human review
        
        Args:
            limit: Maximum number of events
            
        Returns:
            List of unreviewed CrisisEvent instances
        """
        return (
            self.db.query(CrisisEvent)
            .filter(CrisisEvent.human_reviewed == False)
            .order_by(desc(CrisisEvent.created_at))
            .limit(limit)
            .all()
        )
    
    def mark_as_reviewed(self, crisis_id: UUID) -> bool:
        """
        Mark crisis event as human reviewed
        
        Args:
            crisis_id: Crisis event ID
            
        Returns:
            True if successful
        """
        crisis_event = self.get_crisis_event(crisis_id)
        if not crisis_event:
            return False
        
        crisis_event.human_reviewed = True
        self.db.commit()
        return True
    
    def get_escalation_required_events(
        self,
        limit: int = 100
    ) -> List[CrisisEvent]:
        """
        Get crisis events requiring escalation
        
        Args:
            limit: Maximum number of events
            
        Returns:
            List of CrisisEvent instances requiring escalation
        """
        return (
            self.db.query(CrisisEvent)
            .filter(CrisisEvent.escalation_required == True)
            .order_by(desc(CrisisEvent.created_at))
            .limit(limit)
            .all()
        )

