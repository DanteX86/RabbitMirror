#!/usr/bin/env python3

"""
Security framework for RabbitMirror - Comprehensive security utilities and validators.

This module provides:
- Input validation and sanitization
- Path traversal protection
- Rate limiting
- Security headers
- Credential management
- Security logging
"""

import hashlib
import hmac
import os
import re
import secrets
import time
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from urllib.parse import urlparse

from .exceptions import SecurityError, ValidationError
from .symbolic_logger import SymbolicLogger


class SecurityConfig:
    """Configuration for security settings."""

    def __init__(self):
        # Rate limiting
        self.rate_limit_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour

        # File upload security
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", "104857600"))  # 100MB
        self.allowed_extensions = {
            "json",
            "html",
            "csv",
            "yaml",
            "yml",
            "xlsx",
            "xls",
            "pdf",
            "txt",
        }
        self.blocked_extensions = {
            "exe",
            "bat",
            "cmd",
            "com",
            "pif",
            "scr",
            "vbs",
            "js",
            "jar",
            "sh",
            "py",
            "pl",
            "php",
            "asp",
            "jsp",
            "dll",
            "so",
        }

        # Path security
        self.allowed_directories = {
            "/tmp",
            "/var/tmp",
            "/private/var/folders",
            "uploads",
            "exports",
            "cache",
        }
        self.blocked_paths = {"/etc", "/usr", "/bin", "/sbin", "/root", "/home"}

        # Content validation
        self.max_string_length = 10000
        self.max_array_length = 100000
        self.max_nesting_depth = 10

        # Credential security
        self.secret_key_min_length = 32
        self.password_min_length = 12

        # Security headers
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }


class InputValidator:
    """Comprehensive input validation and sanitization."""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.logger = SymbolicLogger()

        # Dangerous patterns
        self.dangerous_patterns = [
            r"<script[^>]*>.*?</script>",  # Script tags
            r"javascript:",  # JavaScript URLs
            r"data:.*,.*",  # Data URLs
            r"eval\s*\(",  # eval calls
            r"exec\s*\(",  # exec calls
            r"import\s+",  # import statements
            r"__.*__",  # Python magic methods
            r"\.\./|\.\\\.",  # Path traversal
            r"[;&|`$]",  # Command injection chars
        ]

        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE | re.DOTALL)
            for pattern in self.dangerous_patterns
        ]

    def validate_string(self, value: str, field_name: str = "input") -> str:
        """Validate and sanitize string input."""
        if not isinstance(value, str):
            raise ValidationError(
                f"{field_name} must be a string", field_name=field_name
            )

        if len(value) > self.config.max_string_length:
            raise ValidationError(
                f"{field_name} exceeds maximum length of {self.config.max_string_length}",
                field_name=field_name,
            )

        # Check for dangerous patterns
        for pattern in self.compiled_patterns:
            if pattern.search(value):
                self.logger.log_error(
                    "security_violation",
                    {
                        "field": field_name,
                        "pattern": pattern.pattern,
                        "value": value[:100] + "..." if len(value) > 100 else value,
                    },
                )
                raise SecurityError(
                    f"Potentially dangerous content detected in {field_name}",
                    error_code="DANGEROUS_CONTENT",
                )

        # Basic sanitization
        sanitized = value.strip()
        sanitized = re.sub(
            r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", sanitized
        )  # Remove control chars

        return sanitized

    def validate_filename(self, filename: str) -> str:
        """Validate and sanitize filename."""
        if not filename:
            raise ValidationError("Filename cannot be empty", field_name="filename")

        # Check for path traversal attempts before sanitization
        if ".." in filename or "/" in filename or "\\" in filename:
            raise SecurityError(
                f"Path traversal attempt detected in filename: {filename}",
                error_code="PATH_TRAVERSAL_FILENAME",
            )

        # Remove path components (additional safety)
        filename = os.path.basename(filename)

        # Check filename length before processing
        if len(filename) > 255:
            raise ValidationError(
                f"Filename too long: {len(filename)} characters (max 255)",
                field_name="filename",
            )

        # Check for dangerous extensions
        extension = filename.split(".")[-1].lower() if "." in filename else ""
        if extension in self.config.blocked_extensions:
            raise SecurityError(
                f"File extension '{extension}' is not allowed",
                error_code="BLOCKED_EXTENSION",
            )

        if extension not in self.config.allowed_extensions:
            raise ValidationError(
                f"File extension '{extension}' is not supported", field_name="filename"
            )

        # Sanitize filename
        sanitized = re.sub(r"[^\w\.-]", "_", filename)
        sanitized = re.sub(r"\.\.+", ".", sanitized)  # Remove multiple dots
        sanitized = re.sub(r"^[\.-]+", "", sanitized)  # Remove leading dots/dashes
        sanitized = re.sub(r"[\.-]+$", "", sanitized)  # Remove trailing dots/dashes

        # Ensure we still have a valid filename after sanitization
        if not sanitized or sanitized == extension:
            raise ValidationError(
                "Filename becomes invalid after sanitization", field_name="filename"
            )

        return sanitized

    def validate_path(self, path: Union[str, Path]) -> Path:
        """Validate file path for security."""
        path_obj = Path(path).resolve()

        # Check for path traversal
        try:
            path_obj.relative_to(Path.cwd())
        except ValueError:
            # Check if it's in allowed directories
            allowed = False
            for allowed_dir in self.config.allowed_directories:
                try:
                    path_obj.relative_to(Path(allowed_dir).resolve())
                    allowed = True
                    break
                except ValueError:
                    continue

            if not allowed:
                raise SecurityError(
                    f"Path '{path}' is outside allowed directories",
                    error_code="PATH_TRAVERSAL",
                )

        # Check for blocked paths
        for blocked_path in self.config.blocked_paths:
            try:
                path_obj.relative_to(Path(blocked_path))
                raise SecurityError(
                    f"Access to '{path}' is forbidden", error_code="FORBIDDEN_PATH"
                )
            except ValueError:
                continue

        return path_obj

    def validate_json_data(self, data: Any, max_depth: int = None) -> Any:
        """Validate JSON data structure."""
        if max_depth is None:
            max_depth = self.config.max_nesting_depth

        return self._validate_json_recursive(data, 0, max_depth)

    def _validate_json_recursive(
        self, data: Any, current_depth: int, max_depth: int
    ) -> Any:
        """Recursively validate JSON data."""
        if current_depth > max_depth:
            raise ValidationError(f"Data nesting exceeds maximum depth of {max_depth}")

        if isinstance(data, dict):
            if len(data) > self.config.max_array_length:
                raise ValidationError(
                    f"Dictionary size exceeds maximum of {self.config.max_array_length}"
                )

            validated = {}
            for key, value in data.items():
                if not isinstance(key, str):
                    raise ValidationError("Dictionary keys must be strings")

                validated_key = self.validate_string(key, "dictionary_key")
                validated_value = self._validate_json_recursive(
                    value, current_depth + 1, max_depth
                )
                validated[validated_key] = validated_value

            return validated

        elif isinstance(data, list):
            if len(data) > self.config.max_array_length:
                raise ValidationError(
                    f"Array size exceeds maximum of {self.config.max_array_length}"
                )

            return [
                self._validate_json_recursive(item, current_depth + 1, max_depth)
                for item in data
            ]

        elif isinstance(data, str):
            return self.validate_string(data)

        elif isinstance(data, (int, float, bool)) or data is None:
            return data

        else:
            raise ValidationError(f"Unsupported data type: {type(data)}")


class RateLimiter:
    """Rate limiting for API endpoints."""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.requests: Dict[str, List[float]] = {}
        self.logger = SymbolicLogger()

    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed based on rate limits."""
        now = time.time()
        window_start = now - self.config.rate_limit_window

        # Clean old requests
        if identifier in self.requests:
            self.requests[identifier] = [
                req_time
                for req_time in self.requests[identifier]
                if req_time > window_start
            ]
        else:
            self.requests[identifier] = []

        # Check rate limit
        if len(self.requests[identifier]) >= self.config.rate_limit_requests:
            self.logger.log_error(
                "rate_limit_exceeded",
                {
                    "identifier": identifier,
                    "requests": len(self.requests[identifier]),
                    "limit": self.config.rate_limit_requests,
                },
            )
            return False

        # Add current request
        self.requests[identifier].append(now)
        return True

    def get_remaining_requests(self, identifier: str) -> int:
        """Get remaining requests for identifier."""
        current_requests = len(self.requests.get(identifier, []))
        return max(0, self.config.rate_limit_requests - current_requests)


class SecretManager:
    """Secure handling of secrets and credentials."""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.logger = SymbolicLogger()

    def generate_secret_key(self, length: int = None) -> str:
        """Generate a cryptographically secure secret key."""
        if length is None:
            length = self.config.secret_key_min_length

        if length < self.config.secret_key_min_length:
            raise ValidationError(
                f"Secret key length must be at least {self.config.secret_key_min_length}"
            )

        return secrets.token_urlsafe(length)

    def validate_secret_key(self, key: str) -> bool:
        """Validate secret key strength."""
        if len(key) < self.config.secret_key_min_length:
            return False

        # Check for common weak patterns
        weak_patterns = ["password", "123", "abc", "qwerty", "admin", "secret"]
        key_lower = key.lower()
        for pattern in weak_patterns:
            if pattern in key_lower:
                return False

        return True

    def hash_secret(self, secret: str, salt: str = None) -> tuple[str, str]:
        """Securely hash a secret with salt."""
        if salt is None:
            salt = secrets.token_hex(32)

        # Use PBKDF2 with SHA-256
        hashed = hashlib.pbkdf2_hmac("sha256", secret.encode(), salt.encode(), 100000)
        return hashed.hex(), salt

    def verify_secret(self, secret: str, hashed: str, salt: str) -> bool:
        """Verify a secret against its hash."""
        computed_hash, _ = self.hash_secret(secret, salt)
        return hmac.compare_digest(computed_hash, hashed)

    def mask_secret(self, secret: str, visible_chars: int = 4) -> str:
        """Mask a secret for logging/display."""
        if len(secret) <= visible_chars * 2:
            return "*" * len(secret)

        return (
            secret[:visible_chars]
            + "*" * (len(secret) - visible_chars * 2)
            + secret[-visible_chars:]
        )


class SecurityAuditor:
    """Security auditing and monitoring."""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.logger = SymbolicLogger()
        self.security_events: List[Dict[str, Any]] = []

    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log a security event."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "details": details,
            "severity": self._get_event_severity(event_type),
        }

        self.security_events.append(event)
        self.logger.log_error(f"security_event_{event_type}", event)

    def _get_event_severity(self, event_type: str) -> str:
        """Determine event severity."""
        high_severity = ["path_traversal", "code_injection", "rate_limit_exceeded"]
        medium_severity = ["invalid_file_type", "suspicious_input"]

        if event_type in high_severity:
            return "HIGH"
        elif event_type in medium_severity:
            return "MEDIUM"
        else:
            return "LOW"

    def get_security_report(self) -> Dict[str, Any]:
        """Generate security audit report."""
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)

        recent_events = [
            event
            for event in self.security_events
            if datetime.fromisoformat(event["timestamp"]) > last_24h
        ]

        severity_counts = {}
        event_type_counts = {}

        for event in recent_events:
            severity = event["severity"]
            event_type = event["event_type"]

            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1

        return {
            "report_timestamp": now.isoformat(),
            "total_events_24h": len(recent_events),
            "severity_breakdown": severity_counts,
            "event_type_breakdown": event_type_counts,
            "recent_high_severity": [
                event for event in recent_events[-10:] if event["severity"] == "HIGH"
            ],
        }


def rate_limit(identifier_func=None):
    """Decorator for rate limiting."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            config = SecurityConfig()
            rate_limiter = RateLimiter(config)

            # Get identifier
            if identifier_func:
                identifier = identifier_func(*args, **kwargs)
            else:
                identifier = "default"

            if not rate_limiter.is_allowed(identifier):
                raise SecurityError(
                    "Rate limit exceeded. Please try again later.",
                    error_code="RATE_LIMIT_EXCEEDED",
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def validate_input(validator_func):
    """Decorator for input validation."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            config = SecurityConfig()
            validator = InputValidator(config)

            # Apply validation
            validated_args, validated_kwargs = validator_func(
                validator, *args, **kwargs
            )

            return func(*validated_args, **validated_kwargs)

        return wrapper

    return decorator


# Global security instances
security_config = SecurityConfig()
input_validator = InputValidator(security_config)
rate_limiter = RateLimiter(security_config)
secret_manager = SecretManager(security_config)
security_auditor = SecurityAuditor(security_config)
