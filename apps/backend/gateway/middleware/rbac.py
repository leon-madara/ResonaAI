"""
Role-Based Access Control (RBAC) middleware and service
Permission enforcement for API endpoints
"""

import logging
from functools import wraps
from typing import List, Optional, Callable, Set
from fastapi import HTTPException, status, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt

from config import settings
from database import get_db, User, Role

logger = logging.getLogger(__name__)


# Default role permissions from security-policies.yaml
DEFAULT_PERMISSIONS = {
    "admin": {"*"},
    "counselor": {"read_conversations", "write_responses", "crisis_intervention", "read_own_data", "write_own_data"},
    "user": {"read_own_data", "write_own_data", "delete_own_data"},
    "system": {"read_system_metrics", "write_logs"},
}


class RBACService:
    """
    Role-Based Access Control service
    Manages permissions and authorization checks
    """
    
    def __init__(self):
        self.permissions_cache = {}
    
    def get_role_permissions(self, role_name: str, db: Optional[Session] = None) -> Set[str]:
        """
        Get permissions for a role
        
        Args:
            role_name: Name of the role
            db: Database session (optional, uses defaults if not provided)
            
        Returns:
            Set of permission strings
        """
        # Check cache first
        if role_name in self.permissions_cache:
            return self.permissions_cache[role_name]
        
        # Try to get from database
        if db:
            role = db.query(Role).filter(Role.name == role_name).first()
            if role and role.permissions:
                permissions = set(role.permissions)
                self.permissions_cache[role_name] = permissions
                return permissions
        
        # Fall back to defaults
        return DEFAULT_PERMISSIONS.get(role_name, set())
    
    def get_user_permissions(self, user: User, db: Session) -> Set[str]:
        """
        Get all permissions for a user (from all assigned roles)
        
        Args:
            user: User object
            db: Database session
            
        Returns:
            Set of all permission strings
        """
        permissions = set()
        
        # Get permissions from user's primary role
        user_role = getattr(user, 'role', 'user')
        permissions.update(self.get_role_permissions(user_role, db))
        
        # Get permissions from additional roles (many-to-many)
        if hasattr(user, 'roles') and user.roles:
            for role in user.roles:
                permissions.update(self.get_role_permissions(role.name, db))
        
        return permissions
    
    def has_permission(
        self,
        user: User,
        permission: str,
        db: Session,
        resource_owner_id: Optional[str] = None
    ) -> bool:
        """
        Check if user has a specific permission
        
        Args:
            user: User object
            permission: Permission string to check
            db: Database session
            resource_owner_id: Optional owner ID for ownership-based permissions
            
        Returns:
            True if user has permission
        """
        user_permissions = self.get_user_permissions(user, db)
        
        # Admin has all permissions
        if "*" in user_permissions:
            return True
        
        # Check exact permission match
        if permission in user_permissions:
            # For ownership-based permissions, verify ownership
            if permission in {"read_own_data", "write_own_data", "delete_own_data"}:
                if resource_owner_id and str(user.id) != resource_owner_id:
                    return False
            return True
        
        return False
    
    def check_permission(
        self,
        user_id: str,
        permission: str,
        db: Session,
        resource_owner_id: Optional[str] = None
    ) -> bool:
        """
        Check permission by user ID
        
        Args:
            user_id: User ID string
            permission: Permission to check
            db: Database session
            resource_owner_id: Optional resource owner ID
            
        Returns:
            True if user has permission
        """
        import uuid
        try:
            user_uuid = uuid.UUID(user_id)
            user = db.query(User).filter(User.id == user_uuid).first()
            if not user:
                return False
            return self.has_permission(user, permission, db, resource_owner_id)
        except ValueError:
            return False
    
    def get_granted_by(self, user: User, permission: str, db: Session) -> Optional[str]:
        """
        Get which role grants a specific permission to a user
        
        Args:
            user: User object
            permission: Permission to check
            db: Database session
            
        Returns:
            Role name that grants the permission, or None
        """
        # Check primary role
        user_role = getattr(user, 'role', 'user')
        role_perms = self.get_role_permissions(user_role, db)
        if "*" in role_perms or permission in role_perms:
            return user_role
        
        # Check additional roles
        if hasattr(user, 'roles') and user.roles:
            for role in user.roles:
                role_perms = self.get_role_permissions(role.name, db)
                if "*" in role_perms or permission in role_perms:
                    return role.name
        
        return None
    
    def clear_cache(self, role_name: Optional[str] = None):
        """
        Clear permissions cache
        
        Args:
            role_name: Specific role to clear, or None to clear all
        """
        if role_name:
            self.permissions_cache.pop(role_name, None)
        else:
            self.permissions_cache.clear()


# Global RBAC service instance
rbac_service = RBACService()


def get_rbac_service() -> RBACService:
    """Get the RBAC service instance"""
    return rbac_service


def require_permission(*permissions: str):
    """
    Decorator to require specific permissions for an endpoint
    
    Usage:
        @app.get("/admin/users")
        @require_permission("manage_users")
        async def list_users(...):
            ...
    
    Args:
        *permissions: Required permissions (user needs at least one)
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request and credentials from kwargs
            request: Request = kwargs.get('request')
            credentials: HTTPAuthorizationCredentials = kwargs.get('credentials')
            db: Session = kwargs.get('db')
            
            if not credentials:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Decode token
            try:
                payload = jwt.decode(
                    credentials.credentials,
                    settings.JWT_SECRET_KEY,
                    algorithms=[settings.JWT_ALGORITHM]
                )
                user_id = payload.get("user_id")
            except jwt.InvalidTokenError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
            
            # Check permissions
            has_any_permission = False
            for permission in permissions:
                if rbac_service.check_permission(user_id, permission, db):
                    has_any_permission = True
                    break
            
            if not has_any_permission:
                logger.warning(f"Permission denied for user {user_id}: requires {permissions}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied. Required: {', '.join(permissions)}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_role(*roles: str):
    """
    Decorator to require specific roles for an endpoint
    
    Usage:
        @app.get("/counselor/dashboard")
        @require_role("counselor", "admin")
        async def counselor_dashboard(...):
            ...
    
    Args:
        *roles: Required roles (user needs at least one)
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get credentials from kwargs
            credentials: HTTPAuthorizationCredentials = kwargs.get('credentials')
            
            if not credentials:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Decode token
            try:
                payload = jwt.decode(
                    credentials.credentials,
                    settings.JWT_SECRET_KEY,
                    algorithms=[settings.JWT_ALGORITHM]
                )
                user_role = payload.get("role", "user")
            except jwt.InvalidTokenError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            # Check if user has required role
            if user_role not in roles:
                logger.warning(f"Role denied for user: has {user_role}, requires {roles}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required role: {', '.join(roles)}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_owner_or_permission(permission: str, user_id_param: str = "user_id"):
    """
    Decorator to require either resource ownership or a specific permission
    
    Usage:
        @app.get("/users/{user_id}/data")
        @require_owner_or_permission("read_conversations", "user_id")
        async def get_user_data(user_id: str, ...):
            ...
    
    Args:
        permission: Permission that allows access regardless of ownership
        user_id_param: Name of the path parameter containing the resource owner ID
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get credentials and db from kwargs
            credentials: HTTPAuthorizationCredentials = kwargs.get('credentials')
            db: Session = kwargs.get('db')
            resource_owner_id = kwargs.get(user_id_param)
            
            if not credentials:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Decode token
            try:
                payload = jwt.decode(
                    credentials.credentials,
                    settings.JWT_SECRET_KEY,
                    algorithms=[settings.JWT_ALGORITHM]
                )
                user_id = payload.get("user_id")
            except jwt.InvalidTokenError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            # Check if user is owner
            if user_id == resource_owner_id:
                return await func(*args, **kwargs)
            
            # Check if user has permission
            if rbac_service.check_permission(user_id, permission, db):
                return await func(*args, **kwargs)
            
            logger.warning(f"Access denied for user {user_id} to resource owned by {resource_owner_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return wrapper
    return decorator


class PermissionChecker:
    """
    Dependency class for checking permissions in FastAPI endpoints
    
    Usage:
        @app.get("/admin/users")
        async def list_users(
            permission_check: bool = Depends(PermissionChecker("manage_users"))
        ):
            ...
    """
    
    def __init__(self, *required_permissions: str):
        self.required_permissions = required_permissions
    
    async def __call__(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        db: Session = Depends(get_db)
    ) -> bool:
        # Decode token
        try:
            payload = jwt.decode(
                credentials.credentials,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            user_id = payload.get("user_id")
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Check permissions
        for permission in self.required_permissions:
            if rbac_service.check_permission(user_id, permission, db):
                return True
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied. Required: {', '.join(self.required_permissions)}"
        )


class RoleChecker:
    """
    Dependency class for checking roles in FastAPI endpoints
    
    Usage:
        @app.get("/counselor/patients")
        async def list_patients(
            role_check: bool = Depends(RoleChecker("counselor", "admin"))
        ):
            ...
    """
    
    def __init__(self, *required_roles: str):
        self.required_roles = required_roles
    
    async def __call__(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ) -> bool:
        # Decode token
        try:
            payload = jwt.decode(
                credentials.credentials,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            user_role = payload.get("role", "user")
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        if user_role not in self.required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(self.required_roles)}"
            )
        
        return True

