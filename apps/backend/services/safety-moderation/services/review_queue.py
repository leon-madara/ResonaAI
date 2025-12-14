"""
Human review queue management for safety moderation
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import uuid

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres:5432/mental_health")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class ReviewQueue:
    """Manage human review queue for moderated content"""
    
    def __init__(self):
        """Initialize review queue"""
        self.db = SessionLocal()
    
    def add_to_queue(
        self,
        content: str,
        content_type: str,
        user_id: Optional[str],
        validation_result: Dict[str, Any],
        priority: str = "normal"
    ) -> str:
        """
        Add content to review queue.
        
        Args:
            content: Content to review
            content_type: "response" or "user_input"
            user_id: User ID (optional)
            validation_result: Validation result from content filter
            priority: "low", "normal", "high", "urgent"
            
        Returns:
            Review queue item ID
        """
        review_id = str(uuid.uuid4())
        
        try:
            self.db.execute(
                text("""
                    INSERT INTO moderation_queue (
                        id, content, content_type, user_id, validation_result,
                        priority, status, created_at
                    )
                    VALUES (
                        :id::uuid, :content, :content_type, :user_id::uuid,
                        :validation_result::jsonb, :priority, 'pending', NOW()
                    )
                """),
                {
                    "id": review_id,
                    "content": content,
                    "content_type": content_type,
                    "user_id": user_id,
                    "validation_result": str(validation_result),
                    "priority": priority,
                }
            )
            self.db.commit()
            logger.info(f"Added content to review queue: {review_id}")
            return review_id
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to add to review queue: {e}")
            raise
    
    def get_queue(
        self,
        status: str = "pending",
        priority: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get items from review queue.
        
        Args:
            status: Queue status ("pending", "in_review", "resolved")
            priority: Optional priority filter
            limit: Maximum number of items to return
            
        Returns:
            List of queue items
        """
        try:
            query = """
                SELECT id, content, content_type, user_id, validation_result,
                       priority, status, created_at, reviewed_at, reviewer_id
                FROM moderation_queue
                WHERE status = :status
            """
            params = {"status": status, "limit": limit}
            
            if priority:
                query += " AND priority = :priority"
                params["priority"] = priority
            
            query += " ORDER BY created_at DESC LIMIT :limit"
            
            rows = self.db.execute(text(query), params).fetchall()
            
            return [
                {
                    "id": str(row.id),
                    "content": row.content,
                    "content_type": row.content_type,
                    "user_id": str(row.user_id) if row.user_id else None,
                    "validation_result": row.validation_result,
                    "priority": row.priority,
                    "status": row.status,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "reviewed_at": row.reviewed_at.isoformat() if row.reviewed_at else None,
                    "reviewer_id": str(row.reviewer_id) if row.reviewer_id else None,
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Failed to get queue: {e}")
            return []
    
    def update_review_status(
        self,
        review_id: str,
        status: str,
        reviewer_id: Optional[str] = None,
        decision: Optional[str] = None
    ) -> bool:
        """
        Update review status.
        
        Args:
            review_id: Review queue item ID
            status: New status ("in_review", "approved", "rejected", "resolved")
            reviewer_id: ID of reviewer
            decision: Optional decision notes
            
        Returns:
            True if updated successfully
        """
        try:
            self.db.execute(
                text("""
                    UPDATE moderation_queue
                    SET status = :status,
                        reviewer_id = :reviewer_id::uuid,
                        reviewed_at = NOW(),
                        decision = :decision
                    WHERE id = :id::uuid
                """),
                {
                    "id": review_id,
                    "status": status,
                    "reviewer_id": reviewer_id,
                    "decision": decision,
                }
            )
            self.db.commit()
            logger.info(f"Updated review status: {review_id} -> {status}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update review status: {e}")
            return False
    
    def log_moderation_decision(
        self,
        content: str,
        content_type: str,
        user_id: Optional[str],
        validation_result: Dict[str, Any],
        action: str,
        reviewer_id: Optional[str] = None
    ) -> bool:
        """
        Log moderation decision for analytics.
        
        Args:
            content: Content that was moderated
            content_type: "response" or "user_input"
            user_id: User ID (optional)
            validation_result: Validation result
            action: Action taken ("allow", "block", "review")
            reviewer_id: Reviewer ID if human-reviewed
            
        Returns:
            True if logged successfully
        """
        try:
            self.db.execute(
                text("""
                    INSERT INTO moderation_logs (
                        id, content, content_type, user_id, validation_result,
                        action, reviewer_id, created_at
                    )
                    VALUES (
                        gen_random_uuid(), :content, :content_type, :user_id::uuid,
                        :validation_result::jsonb, :action, :reviewer_id::uuid, NOW()
                    )
                """),
                {
                    "content": content[:1000],  # Truncate for storage
                    "content_type": content_type,
                    "user_id": user_id,
                    "validation_result": str(validation_result),
                    "action": action,
                    "reviewer_id": reviewer_id,
                }
            )
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to log moderation decision: {e}")
            return False


# Global instance
_review_queue: Optional[ReviewQueue] = None


def get_review_queue() -> ReviewQueue:
    """Get or create review queue instance"""
    global _review_queue
    if _review_queue is None:
        _review_queue = ReviewQueue()
    return _review_queue

