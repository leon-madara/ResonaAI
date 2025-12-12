"""
Breach Notification Service
Handles data breach detection, documentation, and notification
Compliant with Kenya DPA Section 43 (72-hour notification requirement)
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import jwt
import uuid
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Settings
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres:5432/mental_health")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
JWT_ALGORITHM = "HS256"

# Kenya DPA requirements
BREACH_NOTIFICATION_DEADLINE_HOURS = 72
ODPC_NOTIFICATION_EMAIL = os.getenv("ODPC_EMAIL", "complaints@odpc.go.ke")
SECURITY_TEAM_EMAIL = os.getenv("SECURITY_TEAM_EMAIL", "security@mentalhealth.ke")

# Database setup
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class BreachSeverity(str, Enum):
    """Breach severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BreachStatus(str, Enum):
    """Breach handling status"""
    DETECTED = "detected"
    CONTAINED = "contained"
    INVESTIGATING = "investigating"
    NOTIFIED_AUTHORITY = "notified_authority"
    NOTIFIED_USERS = "notified_users"
    RESOLVED = "resolved"


class BreachRecord(Base):
    """Data breach record"""
    __tablename__ = "breach_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(String(50), unique=True, nullable=False)
    severity = Column(String(20), nullable=False)
    status = Column(String(30), nullable=False, default="detected")
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Breach details
    breach_type = Column(String(100), nullable=False)  # unauthorized_access, data_leak, etc.
    data_categories = Column(ARRAY(Text), nullable=True)  # Types of data affected
    affected_users_count = Column(Integer, default=0)
    affected_user_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)
    
    # Timeline
    detected_at = Column(DateTime, nullable=False)
    contained_at = Column(DateTime, nullable=True)
    authority_notified_at = Column(DateTime, nullable=True)
    users_notified_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    notification_deadline = Column(DateTime, nullable=False)
    
    # Attribution
    detected_by = Column(UUID(as_uuid=True), nullable=True)
    handled_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Documentation
    root_cause = Column(Text, nullable=True)
    impact_assessment = Column(Text, nullable=True)
    remediation_steps = Column(JSONB, nullable=True)
    lessons_learned = Column(Text, nullable=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class BreachNotification(Base):
    """Notification records for breach communications"""
    __tablename__ = "breach_notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    breach_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    notification_type = Column(String(50), nullable=False)  # authority, user, internal
    recipient_type = Column(String(50), nullable=False)  # odpc, user, security_team
    recipient = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    delivered = Column(Boolean, default=False)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# Create tables
Base.metadata.create_all(bind=engine)


# Pydantic models
class BreachReportRequest(BaseModel):
    """Request to report a data breach"""
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=10)
    breach_type: str = Field(..., description="Type of breach")
    severity: BreachSeverity
    data_categories: List[str] = Field(default=[], description="Categories of data affected")
    affected_users_count: int = Field(default=0, ge=0)
    affected_user_ids: Optional[List[str]] = None


class BreachUpdateRequest(BaseModel):
    """Request to update breach status"""
    status: Optional[BreachStatus] = None
    root_cause: Optional[str] = None
    impact_assessment: Optional[str] = None
    remediation_steps: Optional[List[str]] = None
    lessons_learned: Optional[str] = None


app = FastAPI(
    title="Breach Notification Service",
    description="Data breach detection, documentation, and notification (Kenya DPA compliant)",
    version="1.0.0"
)

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_from_token(credentials: HTTPAuthorizationCredentials) -> Optional[str]:
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload.get("user_id")
    except:
        return None


def generate_incident_id() -> str:
    """Generate a unique incident ID"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    random_part = uuid.uuid4().hex[:6].upper()
    return f"BR-{timestamp}-{random_part}"


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "breach-notification"
    }


@app.post("/breach/report")
async def report_breach(
    request: BreachReportRequest,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Report a data breach
    
    Initiates the breach response process:
    1. Creates breach record
    2. Calculates 72-hour notification deadline
    3. Notifies security team immediately
    4. Schedules authority notification
    """
    try:
        user_id = get_user_from_token(credentials)
        
        detected_at = datetime.utcnow()
        notification_deadline = detected_at + timedelta(hours=BREACH_NOTIFICATION_DEADLINE_HOURS)
        
        breach = BreachRecord(
            id=uuid.uuid4(),
            incident_id=generate_incident_id(),
            severity=request.severity.value,
            status=BreachStatus.DETECTED.value,
            title=request.title,
            description=request.description,
            breach_type=request.breach_type,
            data_categories=request.data_categories,
            affected_users_count=request.affected_users_count,
            affected_user_ids=[uuid.UUID(uid) for uid in request.affected_user_ids] if request.affected_user_ids else None,
            detected_at=detected_at,
            notification_deadline=notification_deadline,
            detected_by=uuid.UUID(user_id) if user_id else None
        )
        
        db.add(breach)
        db.commit()
        db.refresh(breach)
        
        logger.critical(f"DATA BREACH REPORTED: {breach.incident_id} - {request.title}")
        
        # Notify security team immediately
        background_tasks.add_task(
            send_internal_notification,
            str(breach.id),
            breach.incident_id,
            request.title,
            request.description,
            request.severity.value
        )
        
        return {
            "breach_id": str(breach.id),
            "incident_id": breach.incident_id,
            "status": breach.status,
            "notification_deadline": notification_deadline.isoformat(),
            "hours_remaining": BREACH_NOTIFICATION_DEADLINE_HOURS,
            "message": f"Breach reported. Authority notification required by {notification_deadline.isoformat()}"
        }
        
    except Exception as e:
        logger.error(f"Failed to report breach: {e}")
        raise HTTPException(status_code=500, detail="Failed to report breach")


@app.get("/breach/{breach_id}")
async def get_breach(
    breach_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get breach details"""
    breach = db.query(BreachRecord).filter(
        BreachRecord.id == uuid.UUID(breach_id)
    ).first()
    
    if not breach:
        raise HTTPException(status_code=404, detail="Breach not found")
    
    return {
        "id": str(breach.id),
        "incident_id": breach.incident_id,
        "severity": breach.severity,
        "status": breach.status,
        "title": breach.title,
        "description": breach.description,
        "breach_type": breach.breach_type,
        "data_categories": breach.data_categories,
        "affected_users_count": breach.affected_users_count,
        "detected_at": breach.detected_at.isoformat(),
        "contained_at": breach.contained_at.isoformat() if breach.contained_at else None,
        "authority_notified_at": breach.authority_notified_at.isoformat() if breach.authority_notified_at else None,
        "users_notified_at": breach.users_notified_at.isoformat() if breach.users_notified_at else None,
        "notification_deadline": breach.notification_deadline.isoformat(),
        "root_cause": breach.root_cause,
        "impact_assessment": breach.impact_assessment,
        "remediation_steps": breach.remediation_steps
    }


@app.put("/breach/{breach_id}")
async def update_breach(
    breach_id: str,
    request: BreachUpdateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Update breach status and documentation"""
    user_id = get_user_from_token(credentials)
    
    breach = db.query(BreachRecord).filter(
        BreachRecord.id == uuid.UUID(breach_id)
    ).first()
    
    if not breach:
        raise HTTPException(status_code=404, detail="Breach not found")
    
    if request.status:
        breach.status = request.status.value
        
        if request.status == BreachStatus.CONTAINED:
            breach.contained_at = datetime.utcnow()
        elif request.status == BreachStatus.RESOLVED:
            breach.resolved_at = datetime.utcnow()
    
    if request.root_cause:
        breach.root_cause = request.root_cause
    if request.impact_assessment:
        breach.impact_assessment = request.impact_assessment
    if request.remediation_steps:
        breach.remediation_steps = request.remediation_steps
    if request.lessons_learned:
        breach.lessons_learned = request.lessons_learned
    
    if user_id and not breach.handled_by:
        breach.handled_by = uuid.UUID(user_id)
    
    db.commit()
    
    logger.info(f"Breach {breach.incident_id} updated: {request.status}")
    
    return {"success": True, "message": "Breach updated"}


@app.post("/breach/{breach_id}/notify-authority")
async def notify_authority(
    breach_id: str,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Notify the Office of Data Protection Commissioner (Kenya)
    
    As required by Kenya DPA Section 43, notification must be made
    within 72 hours of becoming aware of a breach.
    """
    breach = db.query(BreachRecord).filter(
        BreachRecord.id == uuid.UUID(breach_id)
    ).first()
    
    if not breach:
        raise HTTPException(status_code=404, detail="Breach not found")
    
    if breach.authority_notified_at:
        return {
            "already_notified": True,
            "notified_at": breach.authority_notified_at.isoformat()
        }
    
    # Create notification content
    notification_content = f"""
DATA BREACH NOTIFICATION - Kenya DPA Section 43

Incident ID: {breach.incident_id}
Organization: ResonaAI Mental Health Platform
Date of Detection: {breach.detected_at.isoformat()}

BREACH DETAILS:
Type: {breach.breach_type}
Severity: {breach.severity}
Title: {breach.title}
Description: {breach.description}

AFFECTED DATA:
Categories: {', '.join(breach.data_categories or [])}
Number of Affected Individuals: {breach.affected_users_count}

CONTAINMENT STATUS: {breach.status}
Contained At: {breach.contained_at.isoformat() if breach.contained_at else 'Ongoing'}

ROOT CAUSE ANALYSIS:
{breach.root_cause or 'Under investigation'}

REMEDIATION MEASURES:
{', '.join(breach.remediation_steps or ['Under development'])}

Contact: {SECURITY_TEAM_EMAIL}
"""
    
    # Create notification record
    notification = BreachNotification(
        id=uuid.uuid4(),
        breach_id=breach.id,
        notification_type="authority",
        recipient_type="odpc",
        recipient=ODPC_NOTIFICATION_EMAIL,
        subject=f"Data Breach Notification - {breach.incident_id}",
        content=notification_content
    )
    
    db.add(notification)
    
    # Update breach record
    breach.authority_notified_at = datetime.utcnow()
    breach.status = BreachStatus.NOTIFIED_AUTHORITY.value
    
    db.commit()
    
    # In production, send actual email
    background_tasks.add_task(send_authority_notification, notification)
    
    logger.info(f"Authority notification initiated for breach {breach.incident_id}")
    
    return {
        "success": True,
        "notification_id": str(notification.id),
        "notified_at": breach.authority_notified_at.isoformat(),
        "recipient": ODPC_NOTIFICATION_EMAIL
    }


@app.post("/breach/{breach_id}/notify-users")
async def notify_affected_users(
    breach_id: str,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Notify affected users of the breach
    
    Required for high-risk breaches per Kenya DPA
    """
    breach = db.query(BreachRecord).filter(
        BreachRecord.id == uuid.UUID(breach_id)
    ).first()
    
    if not breach:
        raise HTTPException(status_code=404, detail="Breach not found")
    
    # Update breach record
    breach.users_notified_at = datetime.utcnow()
    breach.status = BreachStatus.NOTIFIED_USERS.value
    db.commit()
    
    # In production, send notifications to affected users
    background_tasks.add_task(send_user_notifications, str(breach.id))
    
    logger.info(f"User notifications initiated for breach {breach.incident_id}")
    
    return {
        "success": True,
        "notified_at": breach.users_notified_at.isoformat(),
        "affected_users_count": breach.affected_users_count
    }


@app.get("/breaches")
async def list_breaches(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 50,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """List all breach records"""
    from sqlalchemy import desc
    
    query = db.query(BreachRecord)
    
    if status:
        query = query.filter(BreachRecord.status == status)
    if severity:
        query = query.filter(BreachRecord.severity == severity)
    
    breaches = query.order_by(desc(BreachRecord.created_at)).limit(limit).all()
    
    return {
        "breaches": [
            {
                "id": str(b.id),
                "incident_id": b.incident_id,
                "severity": b.severity,
                "status": b.status,
                "title": b.title,
                "affected_users_count": b.affected_users_count,
                "detected_at": b.detected_at.isoformat(),
                "notification_deadline": b.notification_deadline.isoformat()
            }
            for b in breaches
        ],
        "count": len(breaches)
    }


@app.get("/breaches/pending-notifications")
async def get_pending_notifications(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get breaches that require notification (approaching deadline)"""
    deadline = datetime.utcnow() + timedelta(hours=24)  # Within 24 hours
    
    breaches = db.query(BreachRecord).filter(
        BreachRecord.authority_notified_at.is_(None),
        BreachRecord.notification_deadline <= deadline
    ).all()
    
    return {
        "pending": [
            {
                "id": str(b.id),
                "incident_id": b.incident_id,
                "title": b.title,
                "severity": b.severity,
                "hours_remaining": max(0, (b.notification_deadline - datetime.utcnow()).total_seconds() / 3600)
            }
            for b in breaches
        ],
        "count": len(breaches),
        "urgent_count": sum(1 for b in breaches if (b.notification_deadline - datetime.utcnow()).total_seconds() / 3600 < 12)
    }


# Background task functions
async def send_internal_notification(breach_id: str, incident_id: str, title: str, description: str, severity: str):
    """Send internal notification to security team"""
    logger.critical(f"INTERNAL ALERT: Breach {incident_id} - {title} (Severity: {severity})")
    # In production, send email/SMS to security team


async def send_authority_notification(notification: BreachNotification):
    """Send notification to ODPC"""
    logger.info(f"Sending authority notification for breach {notification.breach_id}")
    # In production, send email to ODPC


async def send_user_notifications(breach_id: str):
    """Send notifications to affected users"""
    logger.info(f"Sending user notifications for breach {breach_id}")
    # In production, email/SMS affected users


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

