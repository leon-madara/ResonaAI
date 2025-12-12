"""
Consent Management Service for Mental Health Platform
Handles user consent tracking and management for data processing
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import json

from config import settings
from models.consent_models import ConsentRequest, ConsentResponse, ConsentUpdateRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database models
class ConsentRecord(Base):
    __tablename__ = "consent_records"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    consent_type = Column(String, nullable=False)
    consent_version = Column(String, nullable=False)
    granted = Column(Boolean, nullable=False)
    granted_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    consent_data = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

# Security
security = HTTPBearer()

app = FastAPI(
    title="Consent Management Service",
    description="User consent tracking and management for data processing",
    version="1.0.0"
)

class ConsentManager:
    """Manages user consent records"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_consent_record(
        self,
        user_id: str,
        consent_type: str,
        consent_version: str,
        granted: bool,
        consent_data: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> ConsentRecord:
        """Create a new consent record"""
        try:
            record = ConsentRecord(
                id=f"{user_id}_{consent_type}_{consent_version}",
                user_id=user_id,
                consent_type=consent_type,
                consent_version=consent_version,
                granted=granted,
                granted_at=datetime.utcnow(),
                consent_data=consent_data,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            
            logger.info(f"Consent record created for user {user_id}, type {consent_type}")
            return record
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create consent record: {str(e)}")
            raise
    
    def get_consent_records(self, user_id: str) -> List[ConsentRecord]:
        """Get all consent records for a user"""
        try:
            records = self.db.query(ConsentRecord).filter(
                ConsentRecord.user_id == user_id
            ).order_by(ConsentRecord.granted_at.desc()).all()
            
            return records
            
        except Exception as e:
            logger.error(f"Failed to get consent records: {str(e)}")
            raise
    
    def get_active_consent(
        self,
        user_id: str,
        consent_type: str,
        consent_version: str
    ) -> Optional[ConsentRecord]:
        """Get active consent for a specific type and version"""
        try:
            record = self.db.query(ConsentRecord).filter(
                ConsentRecord.user_id == user_id,
                ConsentRecord.consent_type == consent_type,
                ConsentRecord.consent_version == consent_version,
                ConsentRecord.granted == True,
                ConsentRecord.revoked_at.is_(None)
            ).first()
            
            return record
            
        except Exception as e:
            logger.error(f"Failed to get active consent: {str(e)}")
            raise
    
    def revoke_consent(
        self,
        user_id: str,
        consent_type: str,
        consent_version: str
    ) -> bool:
        """Revoke consent for a specific type and version"""
        try:
            record = self.db.query(ConsentRecord).filter(
                ConsentRecord.user_id == user_id,
                ConsentRecord.consent_type == consent_type,
                ConsentRecord.consent_version == consent_version,
                ConsentRecord.granted == True,
                ConsentRecord.revoked_at.is_(None)
            ).first()
            
            if record:
                record.revoked_at = datetime.utcnow()
                self.db.commit()
                
                logger.info(f"Consent revoked for user {user_id}, type {consent_type}")
                return True
            
            return False
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to revoke consent: {str(e)}")
            raise
    
    def check_consent(
        self,
        user_id: str,
        consent_type: str,
        consent_version: str
    ) -> bool:
        """Check if user has active consent"""
        try:
            record = self.get_active_consent(user_id, consent_type, consent_version)
            return record is not None
            
        except Exception as e:
            logger.error(f"Failed to check consent: {str(e)}")
            return False

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract user ID from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload.get("user_id")
    except Exception as e:
        logger.error(f"Token validation failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "consent-management"
    }

@app.post("/consent", response_model=ConsentResponse)
async def create_consent(
    request: ConsentRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_from_token)
):
    """Create a new consent record"""
    try:
        consent_manager = ConsentManager(db)
        
        record = consent_manager.create_consent_record(
            user_id=user_id,
            consent_type=request.consent_type,
            consent_version=request.consent_version,
            granted=request.granted,
            consent_data=request.consent_data,
            ip_address=request.ip_address,
            user_agent=request.user_agent
        )
        
        return ConsentResponse(
            id=record.id,
            user_id=record.user_id,
            consent_type=record.consent_type,
            consent_version=record.consent_version,
            granted=record.granted,
            granted_at=record.granted_at,
            revoked_at=record.revoked_at,
            consent_data=record.consent_data
        )
        
    except Exception as e:
        logger.error(f"Consent creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Consent creation failed")

@app.get("/consent", response_model=List[ConsentResponse])
async def get_consents(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_from_token)
):
    """Get all consent records for a user"""
    try:
        consent_manager = ConsentManager(db)
        records = consent_manager.get_consent_records(user_id)
        
        return [
            ConsentResponse(
                id=record.id,
                user_id=record.user_id,
                consent_type=record.consent_type,
                consent_version=record.consent_version,
                granted=record.granted,
                granted_at=record.granted_at,
                revoked_at=record.revoked_at,
                consent_data=record.consent_data
            )
            for record in records
        ]
        
    except Exception as e:
        logger.error(f"Consent retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Consent retrieval failed")

@app.post("/consent/revoke")
async def revoke_consent(
    request: ConsentUpdateRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_from_token)
):
    """Revoke consent for a specific type and version"""
    try:
        consent_manager = ConsentManager(db)
        
        success = consent_manager.revoke_consent(
            user_id=user_id,
            consent_type=request.consent_type,
            consent_version=request.consent_version
        )
        
        if success:
            return {"success": True, "message": "Consent revoked successfully"}
        else:
            raise HTTPException(status_code=404, detail="Consent not found or already revoked")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Consent revocation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Consent revocation failed")

@app.get("/consent/check")
async def check_consent(
    consent_type: str,
    consent_version: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_from_token)
):
    """Check if user has active consent"""
    try:
        consent_manager = ConsentManager(db)
        
        has_consent = consent_manager.check_consent(
            user_id=user_id,
            consent_type=consent_type,
            consent_version=consent_version
        )
        
        return {
            "has_consent": has_consent,
            "consent_type": consent_type,
            "consent_version": consent_version,
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Consent check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Consent check failed")

@app.get("/consent/types")
async def get_consent_types():
    """Get available consent types"""
    return {
        "consent_types": [
            {
                "type": "data_processing",
                "description": "Consent for processing personal data",
                "required": True
            },
            {
                "type": "emotion_analysis",
                "description": "Consent for emotion analysis from voice",
                "required": False
            },
            {
                "type": "cultural_context",
                "description": "Consent for using cultural context in responses",
                "required": False
            },
            {
                "type": "research_participation",
                "description": "Consent for participating in research",
                "required": False
            },
            {
                "type": "crisis_intervention",
                "description": "Consent for crisis intervention and emergency contact",
                "required": True
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
