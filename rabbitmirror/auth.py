"""
Authentication and authorization module for RabbitMirror.

Provides comprehensive user authentication, session management,
and security features including password validation, rate limiting,
and audit logging.
"""

import re
import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any, Dict, Optional, Tuple

from flask import current_app, flash, redirect, request, session, url_for
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from .database.session import db_session
from .exceptions import SecurityError, ValidationError
from .security import rate_limiter, security_auditor

# Note: Complex multi-user authentication models (User, Session, AuditLog) have been
# removed in favor of simple_auth.py for single-user mode


class PasswordValidator:
    """Enhanced password validation with security rules."""

    MIN_LENGTH = 8
    MAX_LENGTH = 128

    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        Validate password strength and security.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"

        if len(password) < PasswordValidator.MIN_LENGTH:
            return (
                False,
                f"Password must be at least {PasswordValidator.MIN_LENGTH} characters long",
            )

        if len(password) > PasswordValidator.MAX_LENGTH:
            return (
                False,
                f"Password must be no more than {PasswordValidator.MAX_LENGTH} characters long",
            )

        # Check for at least one uppercase letter
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"

        # Check for at least one lowercase letter
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"

        # Check for at least one digit
        if not re.search(r"\d", password):
            return False, "Password must contain at least one number"

        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return (
                False,
                'Password must contain at least one special character (!@#$%^&*(),.?":{}|<>)',
            )

        # Check for common weak passwords
        weak_passwords = [
            "password",
            "12345678",
            "qwerty123",
            "admin123",
            "letmein123",
            "welcome123",
            "password123",
        ]
        if password.lower() in weak_passwords:
            return (
                False,
                "This password is too common. Please choose a stronger password",
            )

        return True, ""

    @staticmethod
    def generate_secure_password(length: int = 16) -> str:
        """Generate a cryptographically secure password."""
        alphabet = (
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        )
        return "".join(secrets.choice(alphabet) for _ in range(length))


# REMOVED: Complex SessionManager for multi-user authentication
# This has been replaced with simple Flask session-based authentication
# for single-user mode. See simple_auth.py for the replacement.

# class SessionManager:
#     """Enhanced session management with security features."""
#     SESSION_TIMEOUT = timedelta(hours=24)
#     MAX_SESSIONS_PER_USER = 5
#     # ... (methods removed for single-user simplification)


# REMOVED: Complex multi-user authentication method
# This has been replaced with simple password verification in simple_auth.py
# for single-user mode.

# def authenticate_user(email: str, password: str, request_info: Dict[str, Any]) -> Tuple[bool, str, Optional[User]]:
#     """Multi-user authentication - removed in single-user mode"""
#     # ... (method removed for single-user simplification)

# REMOVED: Complex password change method for multi-user system
# In single-user mode, password changes are handled through simple_auth.py
# configuration methods.

# @staticmethod
# def change_password(user: User, current_password: str, new_password: str) -> Tuple[bool, str]:
#     """Multi-user password change - removed in single-user mode"""
#     # ... (method removed for single-user simplification)


# REMOVED: Flask-Login based authentication decorator
# This has been replaced with require_simple_auth decorator in the web app
# for single-user mode.

# def require_auth(f):
#     """Multi-user authentication decorator - removed in single-user mode"""
#     # ... (decorator removed for single-user simplification)


def get_request_info() -> Dict[str, Any]:
    """Get request information for security logging."""
    return {
        "ip_address": request.environ.get(
            "HTTP_X_FORWARDED_FOR", request.environ.get("REMOTE_ADDR", "unknown")
        ),
        "user_agent": request.headers.get("User-Agent", ""),
        "endpoint": request.endpoint,
        "method": request.method,
        "url": request.url,
    }
