"""
Email service for sending verification emails and notifications
"""

import os
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
import secrets
import hashlib
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails"""
    
    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: int = 587,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None,
        use_tls: bool = True
    ):
        """
        Initialize email service.
        
        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port
            smtp_user: SMTP username
            smtp_password: SMTP password
            from_email: From email address
            use_tls: Use TLS encryption
        """
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")
        self.from_email = from_email or os.getenv("FROM_EMAIL", "noreply@resona.ai")
        self.use_tls = use_tls
        
        # Check if email is configured
        self.enabled = bool(self.smtp_user and self.smtp_password)
        if not self.enabled:
            logger.warning("Email service not configured. Email sending will be disabled.")
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None
    ) -> bool:
        """
        Send an email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body_text: Plain text email body
            body_html: Optional HTML email body
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning(f"Email service disabled. Would send to {to_email}: {subject}")
            return False
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = subject
            
            # Add text and HTML parts
            text_part = MIMEText(body_text, "plain")
            message.attach(text_part)
            
            if body_html:
                html_part = MIMEText(body_html, "html")
                message.attach(html_part)
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                use_tls=self.use_tls
            )
            
            logger.info(f"Email sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def generate_verification_token(self, email: str, secret_key: str) -> str:
        """
        Generate a verification token for email verification.
        
        Args:
            email: User email address
            secret_key: Secret key for token generation
            
        Returns:
            Verification token as string
        """
        # Create token with email, timestamp, and random component
        timestamp = datetime.now(timezone.utc).isoformat()
        random_component = secrets.token_urlsafe(16)
        
        # Create hash
        token_data = f"{email}:{timestamp}:{random_component}:{secret_key}"
        token_hash = hashlib.sha256(token_data.encode()).hexdigest()
        
        # Combine components
        token = f"{email}:{timestamp}:{random_component}:{token_hash[:16]}"
        
        return token
    
    def verify_token(self, token: str, email: str, secret_key: str, max_age_hours: int = 24) -> bool:
        """
        Verify an email verification token.
        
        Args:
            token: Verification token
            email: User email address
            secret_key: Secret key for token verification
            max_age_hours: Maximum age of token in hours
            
        Returns:
            True if token is valid, False otherwise
        """
        try:
            parts = token.split(":")
            if len(parts) != 4:
                return False
            
            token_email, token_timestamp, random_component, token_hash = parts
            
            # Verify email matches
            if token_email != email:
                return False
            
            # Verify timestamp is not too old
            token_time = datetime.fromisoformat(token_timestamp.replace('Z', '+00:00'))
            age = datetime.now(timezone.utc) - token_time
            if age > timedelta(hours=max_age_hours):
                return False
            
            # Verify hash
            token_data = f"{email}:{token_timestamp}:{random_component}:{secret_key}"
            expected_hash = hashlib.sha256(token_data.encode()).hexdigest()
            
            return token_hash == expected_hash[:16]
            
        except Exception:
            return False
    
    async def send_verification_email(
        self,
        to_email: str,
        verification_token: str,
        base_url: str = "https://resona.ai"
    ) -> bool:
        """
        Send email verification email.
        
        Args:
            to_email: Recipient email address
            verification_token: Verification token
            base_url: Base URL for verification link
            
        Returns:
            True if email sent successfully, False otherwise
        """
        verification_url = f"{base_url}/auth/verify-email?token={verification_token}&email={to_email}"
        
        subject = "Verify your ResonaAI email address"
        
        body_text = f"""
Welcome to ResonaAI!

Please verify your email address by clicking the link below:

{verification_url}

This link will expire in 24 hours.

If you did not create an account, please ignore this email.

Best regards,
The ResonaAI Team
"""
        
        body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .button {{ display: inline-block; padding: 12px 24px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Welcome to ResonaAI!</h2>
        <p>Please verify your email address by clicking the button below:</p>
        <a href="{verification_url}" class="button">Verify Email Address</a>
        <p>Or copy and paste this link into your browser:</p>
        <p>{verification_url}</p>
        <p>This link will expire in 24 hours.</p>
        <p>If you did not create an account, please ignore this email.</p>
        <div class="footer">
            <p>Best regards,<br>The ResonaAI Team</p>
        </div>
    </div>
</body>
</html>
"""
        
        return await self.send_email(to_email, subject, body_text, body_html)


# Global email service instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get or create email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service

