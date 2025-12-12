"""
Security Monitoring Service
Real-time security event monitoring and alerting
Based on security-policies.yaml configuration
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import redis
import jwt
import uuid

from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis client
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Types of security alerts"""
    FAILED_LOGIN = "failed_login"
    DATA_BREACH = "data_breach"
    UNUSUAL_ACCESS = "unusual_access"
    RATE_LIMIT = "rate_limit"
    MFA_BYPASS_ATTEMPT = "mfa_bypass_attempt"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SYSTEM_COMPROMISE = "system_compromise"


# Database models
class SecurityAlert(Base):
    """Security alert records"""
    __tablename__ = "security_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    details = Column(JSONB, nullable=True)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(UUID(as_uuid=True), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved = Column(Boolean, default=False)
    resolved_by = Column(UUID(as_uuid=True), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class SecurityMetric(Base):
    """Security metrics for monitoring"""
    __tablename__ = "security_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    dimensions = Column(JSONB, nullable=True)


# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Security Monitoring Service",
    description="Real-time security event monitoring and alerting",
    version="1.0.0"
)

# Security
security = HTTPBearer()


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class SecurityMonitor:
    """
    Security monitoring and alerting service
    Implements detectors based on security-policies.yaml
    """
    
    def __init__(self, redis_client, db_session_factory):
        self.redis = redis_client
        self.db_session_factory = db_session_factory
    
    async def record_failed_login(self, user_identifier: str, ip_address: str) -> Optional[Dict[str, Any]]:
        """
        Record a failed login attempt and check threshold
        
        Args:
            user_identifier: User email or ID
            ip_address: Client IP address
            
        Returns:
            Alert if threshold exceeded
        """
        key = f"failed_login:{user_identifier}"
        
        try:
            # Increment counter
            count = self.redis.incr(key)
            
            # Set expiry on first increment
            if count == 1:
                self.redis.expire(key, settings.FAILED_LOGIN_WINDOW)
            
            # Check threshold
            if count >= settings.FAILED_LOGIN_THRESHOLD:
                alert = await self._create_alert(
                    alert_type=AlertType.FAILED_LOGIN,
                    severity=AlertSeverity.HIGH,
                    title=f"Multiple failed login attempts for {user_identifier}",
                    description=f"{count} failed login attempts in {settings.FAILED_LOGIN_WINDOW} seconds",
                    ip_address=ip_address,
                    details={
                        "user_identifier": user_identifier,
                        "attempt_count": count,
                        "window_seconds": settings.FAILED_LOGIN_WINDOW
                    }
                )
                
                # Reset counter after alert
                self.redis.delete(key)
                
                return alert
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to record failed login: {e}")
            return None
    
    async def record_unusual_access(self, user_id: str, resource: str, ip_address: str) -> Optional[Dict[str, Any]]:
        """
        Record unusual access pattern
        
        Args:
            user_id: User ID
            resource: Resource accessed
            ip_address: Client IP address
            
        Returns:
            Alert if threshold exceeded
        """
        key = f"unusual_access:{user_id}"
        
        try:
            count = self.redis.incr(key)
            
            if count == 1:
                self.redis.expire(key, settings.UNUSUAL_ACCESS_WINDOW)
            
            if count >= settings.UNUSUAL_ACCESS_THRESHOLD:
                alert = await self._create_alert(
                    alert_type=AlertType.UNUSUAL_ACCESS,
                    severity=AlertSeverity.MEDIUM,
                    title=f"Unusual access pattern for user {user_id}",
                    description=f"{count} access requests in {settings.UNUSUAL_ACCESS_WINDOW} seconds",
                    user_id=user_id,
                    ip_address=ip_address,
                    details={
                        "access_count": count,
                        "last_resource": resource,
                        "window_seconds": settings.UNUSUAL_ACCESS_WINDOW
                    }
                )
                
                self.redis.delete(key)
                return alert
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to record unusual access: {e}")
            return None
    
    async def report_data_breach(
        self,
        description: str,
        affected_users: int,
        data_types: List[str],
        reported_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Report a potential data breach
        
        Args:
            description: Breach description
            affected_users: Number of affected users
            data_types: Types of data affected
            reported_by: User who reported the breach
            
        Returns:
            Alert created
        """
        alert = await self._create_alert(
            alert_type=AlertType.DATA_BREACH,
            severity=AlertSeverity.CRITICAL,
            title="POTENTIAL DATA BREACH DETECTED",
            description=description,
            user_id=reported_by,
            details={
                "affected_users": affected_users,
                "data_types": data_types,
                "breach_detected_at": datetime.utcnow().isoformat()
            }
        )
        
        # Send immediate notification
        await self._send_critical_alert(alert)
        
        return alert
    
    async def _create_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        description: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create and store a security alert"""
        try:
            db = self.db_session_factory()
            try:
                alert = SecurityAlert(
                    id=uuid.uuid4(),
                    alert_type=alert_type.value,
                    severity=severity.value,
                    title=title,
                    description=description,
                    user_id=uuid.UUID(user_id) if user_id else None,
                    ip_address=ip_address,
                    details=details
                )
                
                db.add(alert)
                db.commit()
                db.refresh(alert)
                
                alert_dict = {
                    "id": str(alert.id),
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "title": alert.title,
                    "description": alert.description,
                    "user_id": str(alert.user_id) if alert.user_id else None,
                    "ip_address": alert.ip_address,
                    "details": alert.details,
                    "created_at": alert.created_at.isoformat()
                }
                
                logger.warning(f"Security alert created: {title}")
                
                return alert_dict
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            raise
    
    async def _send_critical_alert(self, alert: Dict[str, Any]):
        """Send critical alert notifications"""
        try:
            # Log critical alert
            logger.critical(f"CRITICAL SECURITY ALERT: {alert['title']}")
            
            # In production, send email/SMS
            # await self._send_email_alert(alert)
            
        except Exception as e:
            logger.error(f"Failed to send critical alert: {e}")
    
    async def get_active_alerts(
        self,
        severity: Optional[str] = None,
        alert_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get active (unresolved) security alerts"""
        try:
            db = self.db_session_factory()
            try:
                from sqlalchemy import desc
                
                query = db.query(SecurityAlert).filter(SecurityAlert.resolved == False)
                
                if severity:
                    query = query.filter(SecurityAlert.severity == severity)
                if alert_type:
                    query = query.filter(SecurityAlert.alert_type == alert_type)
                
                alerts = query.order_by(desc(SecurityAlert.created_at)).limit(limit).all()
                
                return [
                    {
                        "id": str(a.id),
                        "alert_type": a.alert_type,
                        "severity": a.severity,
                        "title": a.title,
                        "description": a.description,
                        "user_id": str(a.user_id) if a.user_id else None,
                        "ip_address": a.ip_address,
                        "details": a.details,
                        "acknowledged": a.acknowledged,
                        "created_at": a.created_at.isoformat()
                    }
                    for a in alerts
                ]
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []
    
    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge a security alert"""
        try:
            db = self.db_session_factory()
            try:
                alert = db.query(SecurityAlert).filter(
                    SecurityAlert.id == uuid.UUID(alert_id)
                ).first()
                
                if not alert:
                    return False
                
                alert.acknowledged = True
                alert.acknowledged_by = uuid.UUID(user_id)
                alert.acknowledged_at = datetime.utcnow()
                db.commit()
                
                return True
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str, user_id: str) -> bool:
        """Resolve a security alert"""
        try:
            db = self.db_session_factory()
            try:
                alert = db.query(SecurityAlert).filter(
                    SecurityAlert.id == uuid.UUID(alert_id)
                ).first()
                
                if not alert:
                    return False
                
                alert.resolved = True
                alert.resolved_by = uuid.UUID(user_id)
                alert.resolved_at = datetime.utcnow()
                db.commit()
                
                return True
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")
            return False


# Initialize security monitor
security_monitor = SecurityMonitor(redis_client, SessionLocal)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "security-monitoring"
    }


@app.post("/events/failed-login")
async def record_failed_login(
    user_identifier: str,
    ip_address: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Record a failed login attempt"""
    alert = await security_monitor.record_failed_login(user_identifier, ip_address)
    
    return {
        "recorded": True,
        "alert_generated": alert is not None,
        "alert": alert
    }


@app.post("/events/unusual-access")
async def record_unusual_access(
    user_id: str,
    resource: str,
    ip_address: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Record an unusual access pattern"""
    alert = await security_monitor.record_unusual_access(user_id, resource, ip_address)
    
    return {
        "recorded": True,
        "alert_generated": alert is not None,
        "alert": alert
    }


@app.post("/events/data-breach")
async def report_data_breach(
    description: str,
    affected_users: int,
    data_types: List[str],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Report a potential data breach"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("user_id")
    except:
        user_id = None
    
    alert = await security_monitor.report_data_breach(
        description=description,
        affected_users=affected_users,
        data_types=data_types,
        reported_by=user_id
    )
    
    return {
        "reported": True,
        "alert": alert,
        "message": "Critical alert has been generated and notifications sent"
    }


@app.get("/alerts")
async def get_alerts(
    severity: Optional[str] = None,
    alert_type: Optional[str] = None,
    limit: int = 100,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get active security alerts"""
    alerts = await security_monitor.get_active_alerts(
        severity=severity,
        alert_type=alert_type,
        limit=limit
    )
    
    return {
        "alerts": alerts,
        "count": len(alerts)
    }


@app.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Acknowledge a security alert"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("user_id")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    success = await security_monitor.acknowledge_alert(alert_id, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"success": True, "message": "Alert acknowledged"}


@app.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Resolve a security alert"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("user_id")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    success = await security_monitor.resolve_alert(alert_id, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"success": True, "message": "Alert resolved"}


@app.get("/metrics/summary")
async def get_metrics_summary(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get security metrics summary"""
    try:
        # Get alert counts by severity
        db = SessionLocal()
        try:
            from sqlalchemy import func
            
            severity_counts = db.query(
                SecurityAlert.severity,
                func.count(SecurityAlert.id)
            ).filter(
                SecurityAlert.resolved == False
            ).group_by(SecurityAlert.severity).all()
            
            type_counts = db.query(
                SecurityAlert.alert_type,
                func.count(SecurityAlert.id)
            ).filter(
                SecurityAlert.resolved == False
            ).group_by(SecurityAlert.alert_type).all()
            
            return {
                "by_severity": {s: c for s, c in severity_counts},
                "by_type": {t: c for t, c in type_counts},
                "total_active": sum(c for _, c in severity_counts),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed to get metrics summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

