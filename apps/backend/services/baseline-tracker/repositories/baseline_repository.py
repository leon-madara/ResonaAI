"""
Repository for baseline data access operations
Handles database queries for user baselines, deviations, and historical data
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import text, and_

from models.database_models import UserBaseline, SessionDeviation

logger = logging.getLogger(__name__)


class BaselineRepository:
    """Repository for baseline-related database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_baseline(
        self, 
        user_id: UUID, 
        baseline_type: str
    ) -> Optional[UserBaseline]:
        """
        Get user baseline by type
        
        Args:
            user_id: User UUID
            baseline_type: Type of baseline ('emotion', 'voice', etc.)
        
        Returns:
            UserBaseline or None if not found
        """
        try:
            return self.db.query(UserBaseline).filter(
                and_(
                    UserBaseline.user_id == user_id,
                    UserBaseline.baseline_type == baseline_type
                )
            ).first()
        except Exception as e:
            logger.error(f"Error fetching baseline for user {user_id}, type {baseline_type}: {e}")
            raise
    
    def save_user_baseline(
        self,
        user_id: UUID,
        baseline_type: str,
        baseline_value: Dict[str, Any],
        session_count: int
    ) -> UserBaseline:
        """
        Save or update user baseline
        
        Args:
            user_id: User UUID
            baseline_type: Type of baseline
            baseline_value: Baseline data as dict (will be stored as JSONB)
            session_count: Number of sessions used to calculate baseline
        
        Returns:
            Saved UserBaseline instance
        """
        try:
            # Try to get existing baseline
            existing = self.get_user_baseline(user_id, baseline_type)
            
            if existing:
                # Update existing
                existing.baseline_value = baseline_value
                existing.session_count = session_count
                existing.updated_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(existing)
                logger.info(f"Updated baseline for user {user_id}, type {baseline_type}")
                return existing
            else:
                # Create new
                new_baseline = UserBaseline(
                    user_id=user_id,
                    baseline_type=baseline_type,
                    baseline_value=baseline_value,
                    session_count=session_count
                )
                self.db.add(new_baseline)
                self.db.commit()
                self.db.refresh(new_baseline)
                logger.info(f"Created new baseline for user {user_id}, type {baseline_type}")
                return new_baseline
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving baseline for user {user_id}, type {baseline_type}: {e}")
            raise
    
    def get_historical_emotions(
        self,
        user_id: UUID,
        window_days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get historical emotion data from voice_sessions table
        
        Args:
            user_id: User UUID
            window_days: Number of days to look back
        
        Returns:
            List of emotion records with 'emotion', 'confidence', 'timestamp'
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=window_days)
            
            # Query voice_sessions table for historical emotion data
            # Note: voice_sessions.user_id should match the user_id parameter
            query = text("""
                SELECT 
                    voice_emotion as emotion,
                    emotion_confidence as confidence,
                    session_start as timestamp
                FROM voice_sessions
                WHERE user_id = :user_id
                  AND session_start >= :cutoff_date
                  AND voice_emotion IS NOT NULL
                  AND emotion_confidence IS NOT NULL
                ORDER BY session_start DESC
            """)
            
            result = self.db.execute(
                query,
                {
                    "user_id": str(user_id),
                    "cutoff_date": cutoff_date
                }
            )
            
            emotions = []
            for row in result:
                emotions.append({
                    "emotion": row.emotion,
                    "confidence": float(row.confidence) if row.confidence else 0.5,
                    "timestamp": row.timestamp
                })
            
            logger.info(f"Retrieved {len(emotions)} emotion records for user {user_id}")
            return emotions
            
        except Exception as e:
            logger.error(f"Error fetching historical emotions for user {user_id}: {e}")
            # Return empty list on error to allow baseline calculation to continue
            return []
    
    def get_historical_voice_features(
        self,
        user_id: UUID,
        window_days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get historical voice features from voice_sessions table
        
        Args:
            user_id: User UUID
            window_days: Number of days to look back
        
        Returns:
            List of voice feature records
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=window_days)
            
            # Query voice_sessions table for voice_features JSONB
            query = text("""
                SELECT 
                    voice_features,
                    session_start as timestamp
                FROM voice_sessions
                WHERE user_id = :user_id
                  AND session_start >= :cutoff_date
                  AND voice_features IS NOT NULL
                ORDER BY session_start DESC
            """)
            
            result = self.db.execute(
                query,
                {
                    "user_id": str(user_id),
                    "cutoff_date": cutoff_date
                }
            )
            
            features = []
            for row in result:
                if row.voice_features:
                    # voice_features is JSONB, extract the values we need
                    feat_dict = dict(row.voice_features) if isinstance(row.voice_features, dict) else {}
                    feat_dict["timestamp"] = row.timestamp
                    features.append(feat_dict)
            
            logger.info(f"Retrieved {len(features)} voice feature records for user {user_id}")
            return features
            
        except Exception as e:
            logger.error(f"Error fetching historical voice features for user {user_id}: {e}")
            # Return empty list on error
            return []
    
    def save_deviation(
        self,
        user_id: UUID,
        session_id: UUID,
        deviation_type: str,
        baseline_value: Optional[Dict[str, Any]],
        current_value: Optional[Dict[str, Any]],
        deviation_score: float
    ) -> SessionDeviation:
        """
        Save a deviation record
        
        Args:
            user_id: User UUID
            session_id: Session/conversation UUID
            deviation_type: Type of deviation ('voice', 'emotion')
            baseline_value: Baseline values (JSONB)
            current_value: Current values (JSONB)
            deviation_score: Calculated deviation score
        
        Returns:
            Saved SessionDeviation instance
        """
        try:
            deviation = SessionDeviation(
                user_id=user_id,
                session_id=session_id,
                deviation_type=deviation_type,
                baseline_value=baseline_value,
                current_value=current_value,
                deviation_score=deviation_score
            )
            self.db.add(deviation)
            self.db.commit()
            self.db.refresh(deviation)
            logger.info(f"Saved deviation for user {user_id}, session {session_id}, score {deviation_score}")
            return deviation
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving deviation for user {user_id}, session {session_id}: {e}")
            raise
    
    def get_user_baselines(self, user_id: UUID) -> List[UserBaseline]:
        """
        Get all baselines for a user
        
        Args:
            user_id: User UUID
        
        Returns:
            List of UserBaseline instances
        """
        try:
            return self.db.query(UserBaseline).filter(
                UserBaseline.user_id == user_id
            ).all()
        except Exception as e:
            logger.error(f"Error fetching all baselines for user {user_id}: {e}")
            raise

