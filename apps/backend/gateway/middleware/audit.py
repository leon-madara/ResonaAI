"""
Audit Logging Middleware for API Gateway
Logs all security-relevant events for compliance and forensics
"""

import json
import logging
from typing import Callable, Optional, Dict, Any
from datetime import datetime
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
import uuid
import jwt

logger = logging.getLogger(__name__)


class AuditEventType:
    """Audit event types based on security-policies.yaml"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTER = "user_register"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    ADMIN_ACTION = "admin_action"
    CRISIS_INTERVENTION = "crisis_intervention"
    MFA_SETUP = "mfa_setup"
    MFA_VERIFY = "mfa_verify"
    MFA_DISABLE = "mfa_disable"
    API_KEY_CREATE = "api_key_create"
    API_KEY_REVOKE = "api_key_revoke"
    ROLE_CHANGE = "role_change"
    PERMISSION_DENIED = "permission_denied"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    AUTH_FAILURE = "auth_failure"
    EXPORT_REQUEST = "export_request"
    DELETION_REQUEST = "deletion_request"


class AuditSeverity:
    """Audit event severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# Event type to severity mapping
EVENT_SEVERITY = {
    AuditEventType.USER_LOGIN: AuditSeverity.INFO,
    AuditEventType.USER_LOGOUT: AuditSeverity.INFO,
    AuditEventType.USER_REGISTER: AuditSeverity.INFO,
    AuditEventType.DATA_ACCESS: AuditSeverity.INFO,
    AuditEventType.DATA_MODIFICATION: AuditSeverity.WARNING,
    AuditEventType.DATA_DELETION: AuditSeverity.WARNING,
    AuditEventType.ADMIN_ACTION: AuditSeverity.WARNING,
    AuditEventType.CRISIS_INTERVENTION: AuditSeverity.CRITICAL,
    AuditEventType.MFA_SETUP: AuditSeverity.INFO,
    AuditEventType.MFA_VERIFY: AuditSeverity.INFO,
    AuditEventType.MFA_DISABLE: AuditSeverity.WARNING,
    AuditEventType.API_KEY_CREATE: AuditSeverity.WARNING,
    AuditEventType.API_KEY_REVOKE: AuditSeverity.WARNING,
    AuditEventType.ROLE_CHANGE: AuditSeverity.WARNING,
    AuditEventType.PERMISSION_DENIED: AuditSeverity.WARNING,
    AuditEventType.RATE_LIMIT_EXCEEDED: AuditSeverity.WARNING,
    AuditEventType.AUTH_FAILURE: AuditSeverity.WARNING,
    AuditEventType.EXPORT_REQUEST: AuditSeverity.INFO,
    AuditEventType.DELETION_REQUEST: AuditSeverity.WARNING,
}


# Path to event type mapping
PATH_EVENT_MAPPING = {
    "/auth/login": AuditEventType.USER_LOGIN,
    "/auth/logout": AuditEventType.USER_LOGOUT,
    "/auth/register": AuditEventType.USER_REGISTER,
    "/auth/mfa/setup": AuditEventType.MFA_SETUP,
    "/auth/mfa/verify": AuditEventType.MFA_VERIFY,
    "/auth/mfa/enable": AuditEventType.MFA_SETUP,
    "/auth/mfa/disable": AuditEventType.MFA_DISABLE,
    "/api-keys": AuditEventType.API_KEY_CREATE,
    "/admin/": AuditEventType.ADMIN_ACTION,
    "/crisis/": AuditEventType.CRISIS_INTERVENTION,
    "/deletion/": AuditEventType.DELETION_REQUEST,
    "/export/": AuditEventType.EXPORT_REQUEST,
}


class AuditLogger:
    """
    Audit logging service
    Logs security events to database and optionally to external systems
    """
    
    def __init__(self, db_session_factory=None):
        """
        Initialize audit logger
        
        Args:
            db_session_factory: SQLAlchemy session factory
        """
        self.db_session_factory = db_session_factory
    
    def log_event(
        self,
        event_type: str,
        event_action: str,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: Optional[str] = None
    ) -> Optional[str]:
        """
        Log an audit event
        
        Args:
            event_type: Type of event (from AuditEventType)
            event_action: Specific action performed
            user_id: User ID if available
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            ip_address: Client IP address
            user_agent: Client user agent
            details: Additional event details
            severity: Event severity (auto-determined if not provided)
            
        Returns:
            Audit log ID if successful
        """
        try:
            # Determine severity
            if severity is None:
                severity = EVENT_SEVERITY.get(event_type, AuditSeverity.INFO)
            
            # Create log entry
            log_id = str(uuid.uuid4())
            
            log_entry = {
                "id": log_id,
                "event_type": event_type,
                "event_action": event_action,
                "user_id": user_id,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "details": details,
                "severity": severity,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Log to standard logger
            log_message = f"AUDIT: {event_type} - {event_action}"
            if user_id:
                log_message += f" (user: {user_id})"
            
            if severity == AuditSeverity.CRITICAL:
                logger.critical(log_message)
            elif severity == AuditSeverity.ERROR:
                logger.error(log_message)
            elif severity == AuditSeverity.WARNING:
                logger.warning(log_message)
            else:
                logger.info(log_message)
            
            # Store in database if available
            if self.db_session_factory:
                self._store_to_database(log_entry)
            
            return log_id
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            return None
    
    def _store_to_database(self, log_entry: Dict[str, Any]):
        """Store audit log to database"""
        try:
            from database import AuditLog
            
            db = self.db_session_factory()
            try:
                audit_log = AuditLog(
                    id=uuid.UUID(log_entry["id"]),
                    user_id=uuid.UUID(log_entry["user_id"]) if log_entry.get("user_id") else None,
                    event_type=log_entry["event_type"],
                    event_action=log_entry["event_action"],
                    resource_type=log_entry.get("resource_type"),
                    resource_id=log_entry.get("resource_id"),
                    ip_address=log_entry.get("ip_address"),
                    user_agent=log_entry.get("user_agent"),
                    details=log_entry.get("details"),
                    severity=log_entry["severity"]
                )
                
                db.add(audit_log)
                db.commit()
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to store audit log to database: {e}")
    
    def query_logs(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """
        Query audit logs
        
        Args:
            user_id: Filter by user ID
            event_type: Filter by event type
            start_date: Filter by start date
            end_date: Filter by end date
            severity: Filter by severity
            limit: Maximum number of results
            
        Returns:
            List of audit log entries
        """
        try:
            from database import AuditLog
            from sqlalchemy import desc
            
            if not self.db_session_factory:
                return []
            
            db = self.db_session_factory()
            try:
                query = db.query(AuditLog)
                
                if user_id:
                    query = query.filter(AuditLog.user_id == uuid.UUID(user_id))
                if event_type:
                    query = query.filter(AuditLog.event_type == event_type)
                if severity:
                    query = query.filter(AuditLog.severity == severity)
                if start_date:
                    query = query.filter(AuditLog.created_at >= start_date)
                if end_date:
                    query = query.filter(AuditLog.created_at <= end_date)
                
                query = query.order_by(desc(AuditLog.created_at)).limit(limit)
                
                return [
                    {
                        "id": str(log.id),
                        "user_id": str(log.user_id) if log.user_id else None,
                        "event_type": log.event_type,
                        "event_action": log.event_action,
                        "resource_type": log.resource_type,
                        "resource_id": log.resource_id,
                        "ip_address": log.ip_address,
                        "details": log.details,
                        "severity": log.severity,
                        "created_at": log.created_at.isoformat()
                    }
                    for log in query.all()
                ]
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to query audit logs: {e}")
            return []


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically log HTTP requests for auditing
    """
    
    def __init__(self, app, audit_logger: AuditLogger, jwt_secret: str, jwt_algorithm: str = "HS256"):
        """
        Initialize audit middleware
        
        Args:
            app: FastAPI application
            audit_logger: AuditLogger instance
            jwt_secret: JWT secret key for token decoding
            jwt_algorithm: JWT algorithm
        """
        super().__init__(app)
        self.audit_logger = audit_logger
        self.jwt_secret = jwt_secret
        self.jwt_algorithm = jwt_algorithm
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response for auditing"""
        
        # Skip health checks and docs
        skip_paths = ["/health", "/docs", "/redoc", "/openapi.json"]
        if request.url.path in skip_paths:
            return await call_next(request)
        
        # Extract user ID from token
        user_id = self._extract_user_id(request)
        
        # Process request
        response = await call_next(request)
        
        # Log the request
        await self._log_request(request, response, user_id)
        
        return response
    
    def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from JWT token"""
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload.get("user_id")
            
        except Exception:
            return None
    
    async def _log_request(self, request: Request, response: Response, user_id: Optional[str]):
        """Log request for auditing"""
        try:
            path = request.url.path
            method = request.method
            status_code = response.status_code
            
            # Determine event type
            event_type = self._determine_event_type(path, method, status_code)
            if not event_type:
                return  # Skip non-auditable requests
            
            # Determine severity based on status code
            severity = None
            if status_code >= 500:
                severity = AuditSeverity.ERROR
            elif status_code == 401:
                severity = AuditSeverity.WARNING
                event_type = AuditEventType.AUTH_FAILURE
            elif status_code == 403:
                severity = AuditSeverity.WARNING
                event_type = AuditEventType.PERMISSION_DENIED
            elif status_code == 429:
                severity = AuditSeverity.WARNING
                event_type = AuditEventType.RATE_LIMIT_EXCEEDED
            
            # Get client info
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("User-Agent")
            
            # Log the event
            self.audit_logger.log_event(
                event_type=event_type,
                event_action=f"{method} {path}",
                user_id=user_id,
                resource_type=self._extract_resource_type(path),
                ip_address=ip_address,
                user_agent=user_agent,
                details={
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "query_params": dict(request.query_params) if request.query_params else None
                },
                severity=severity
            )
            
        except Exception as e:
            logger.error(f"Failed to log audit request: {e}")
    
    def _determine_event_type(self, path: str, method: str, status_code: int) -> Optional[str]:
        """Determine audit event type from request"""
        # Check explicit path mappings
        for path_prefix, event_type in PATH_EVENT_MAPPING.items():
            if path.startswith(path_prefix):
                return event_type
        
        # Determine from method and path
        if method == "GET" and "/user" in path.lower():
            return AuditEventType.DATA_ACCESS
        elif method in ("POST", "PUT", "PATCH"):
            return AuditEventType.DATA_MODIFICATION
        elif method == "DELETE":
            return AuditEventType.DATA_DELETION
        
        return None
    
    def _extract_resource_type(self, path: str) -> Optional[str]:
        """Extract resource type from path"""
        parts = path.strip("/").split("/")
        if len(parts) >= 1:
            return parts[0]
        return None


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get the global audit logger instance"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


def init_audit_logger(db_session_factory=None) -> AuditLogger:
    """Initialize the global audit logger"""
    global _audit_logger
    _audit_logger = AuditLogger(db_session_factory)
    return _audit_logger

