"""
Security Headers Middleware for API Gateway
Adds security headers to all responses (CSP, HSTS, XSS Protection, etc.)
"""

from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all HTTP responses
    
    Implements OWASP security best practices:
    - Content-Security-Policy (CSP)
    - Strict-Transport-Security (HSTS)
    - X-Frame-Options
    - X-Content-Type-Options
    - X-XSS-Protection
    - Referrer-Policy
    - Permissions-Policy
    """
    
    def __init__(
        self,
        app,
        enable_csp: bool = True,
        enable_hsts: bool = True,
        hsts_max_age: int = 31536000,  # 1 year
        csp_policy: str = None
    ):
        """
        Initialize security headers middleware
        
        Args:
            app: FastAPI application
            enable_csp: Whether to enable Content-Security-Policy
            enable_hsts: Whether to enable HSTS (should be True in production)
            hsts_max_age: HSTS max-age in seconds (default: 1 year)
            csp_policy: Custom CSP policy (optional)
        """
        super().__init__(app)
        self.enable_csp = enable_csp
        self.enable_hsts = enable_hsts
        self.hsts_max_age = hsts_max_age
        self.csp_policy = csp_policy or self._default_csp_policy()
    
    def _default_csp_policy(self) -> str:
        """Generate default Content-Security-Policy"""
        return "; ".join([
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # Needed for some React features
            "style-src 'self' 'unsafe-inline'",  # Needed for inline styles
            "img-src 'self' data: blob: https:",
            "font-src 'self' https://fonts.gstatic.com",
            "connect-src 'self' https://api.openai.com https://*.azure.com wss:",
            "frame-ancestors 'self'",
            "form-action 'self'",
            "base-uri 'self'",
            "object-src 'none'"
        ])
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response"""
        
        response = await call_next(request)
        
        # Strict-Transport-Security (HSTS)
        if self.enable_hsts:
            response.headers["Strict-Transport-Security"] = \
                f"max-age={self.hsts_max_age}; includeSubDomains; preload"
        
        # X-Frame-Options - Prevent clickjacking
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        
        # X-Content-Type-Options - Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # X-XSS-Protection - Legacy XSS protection (for older browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer-Policy - Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content-Security-Policy
        if self.enable_csp:
            response.headers["Content-Security-Policy"] = self.csp_policy
        
        # Permissions-Policy (formerly Feature-Policy)
        response.headers["Permissions-Policy"] = "; ".join([
            "accelerometer=()",
            "camera=(self)",  # Allow camera for voice recording with video
            "geolocation=()",
            "gyroscope=()",
            "magnetometer=()",
            "microphone=(self)",  # Allow microphone for voice input
            "payment=()",
            "usb=()"
        ])
        
        # Cache-Control for sensitive data
        if self._is_sensitive_endpoint(request.url.path):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
        # X-Permitted-Cross-Domain-Policies
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        
        # Cross-Origin headers
        response.headers["Cross-Origin-Embedder-Policy"] = "credentialless"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        
        return response
    
    def _is_sensitive_endpoint(self, path: str) -> bool:
        """Check if endpoint contains sensitive data"""
        sensitive_paths = [
            "/auth",
            "/user",
            "/conversation",
            "/messages",
            "/admin",
            "/api-keys",
            "/mfa"
        ]
        return any(sensitive in path.lower() for sensitive in sensitive_paths)


class SecurityHeadersConfig:
    """Configuration for security headers"""
    
    # Development configuration (less strict)
    DEVELOPMENT = {
        "enable_csp": False,  # CSP can interfere with hot reload
        "enable_hsts": False,  # Don't enable HSTS in development
        "hsts_max_age": 0
    }
    
    # Production configuration (strict)
    PRODUCTION = {
        "enable_csp": True,
        "enable_hsts": True,
        "hsts_max_age": 31536000,  # 1 year
        "csp_policy": "; ".join([
            "default-src 'self'",
            "script-src 'self'",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self'",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "form-action 'self'",
            "base-uri 'self'",
            "object-src 'none'",
            "upgrade-insecure-requests"
        ])
    }
    
    @classmethod
    def get_config(cls, environment: str = "development") -> dict:
        """Get configuration for environment"""
        if environment.lower() == "production":
            return cls.PRODUCTION
        return cls.DEVELOPMENT

