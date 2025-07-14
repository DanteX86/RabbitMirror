#!/usr/bin/env python3

"""
Custom exception classes for RabbitMirror.

This module provides a comprehensive set of custom exceptions that help
with better error handling, debugging, and user feedback throughout the
application.
"""

from typing import Any, Dict, Union


class RabbitMirrorError(Exception):
    """Base exception for all RabbitMirror errors."""

    def __init__(
        self, message: str, error_code: str = None, details: Dict[str, Any] = None
    ):
        """
        Initialize a RabbitMirror error.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
        }


class DataProcessingError(RabbitMirrorError):
    """Raised when data processing operations fail."""


class ParsingError(DataProcessingError):
    """Raised when parsing operations fail."""

    def __init__(
        self, message: str, file_path: str = None, line_number: int = None, **kwargs
    ):
        super().__init__(message, **kwargs)
        self.file_path = file_path
        self.line_number = line_number
        if file_path:
            self.details["file_path"] = file_path
        if line_number:
            self.details["line_number"] = line_number


class InvalidFormatError(ParsingError):
    """Raised when data format is invalid or unsupported."""


class DataValidationError(DataProcessingError):
    """Raised when data validation fails."""

    def __init__(self, message: str, validation_errors: list = None, **kwargs):
        super().__init__(message, **kwargs)
        self.validation_errors = validation_errors or []
        if validation_errors:
            self.details["validation_errors"] = validation_errors


class SchemaValidationError(DataValidationError):
    """Raised when schema validation fails."""

    def __init__(self, message: str, schema_path: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.schema_path = schema_path
        if schema_path:
            self.details["schema_path"] = schema_path


class FileOperationError(RabbitMirrorError):
    """Raised when file operations fail."""

    def __init__(
        self, message: str, file_path: str = None, operation: str = None, **kwargs
    ):
        super().__init__(message, **kwargs)
        self.file_path = file_path
        self.operation = operation
        if file_path:
            self.details["file_path"] = file_path
        if operation:
            self.details["operation"] = operation


class ConfigurationError(RabbitMirrorError):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str, config_key: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.config_key = config_key
        if config_key:
            self.details["config_key"] = config_key


class AnalysisError(RabbitMirrorError):
    """Raised when analysis operations fail."""


class ClusteringError(AnalysisError):
    """Raised when clustering operations fail."""

    def __init__(self, message: str, algorithm: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.algorithm = algorithm
        if algorithm:
            self.details["algorithm"] = algorithm


class PatternDetectionError(AnalysisError):
    """Raised when pattern detection fails."""


class TrendAnalysisError(AnalysisError):
    """Raised when trend analysis fails."""

    def __init__(self, message: str, metric: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.metric = metric
        if metric:
            self.details["metric"] = metric


class SimulationError(RabbitMirrorError):
    """Raised when simulation operations fail."""

    def __init__(self, message: str, simulation_type: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.simulation_type = simulation_type
        if simulation_type:
            self.details["simulation_type"] = simulation_type


class ExportError(RabbitMirrorError):
    """Raised when export operations fail."""

    def __init__(self, message: str, export_format: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.export_format = export_format
        if export_format:
            self.details["export_format"] = export_format


class DatabaseError(RabbitMirrorError):
    """Raised when database operations fail."""

    def __init__(self, message: str, operation: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.operation = operation
        if operation:
            self.details["operation"] = operation


class NetworkError(RabbitMirrorError):
    """Raised when network operations fail."""

    def __init__(
        self, message: str, url: str = None, status_code: int = None, **kwargs
    ):
        super().__init__(message, **kwargs)
        self.url = url
        self.status_code = status_code
        if url:
            self.details["url"] = url
        if status_code:
            self.details["status_code"] = status_code


class ResourceError(RabbitMirrorError):
    """Raised when resource operations fail."""

    def __init__(self, message: str, resource_type: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.resource_type = resource_type
        if resource_type:
            self.details["resource_type"] = resource_type


class DependencyError(RabbitMirrorError):
    """Raised when external dependencies are missing or incompatible."""

    def __init__(
        self,
        message: str,
        dependency: str = None,
        required_version: str = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.dependency = dependency
        self.required_version = required_version
        if dependency:
            self.details["dependency"] = dependency
        if required_version:
            self.details["required_version"] = required_version


class CustomPermissionError(RabbitMirrorError):
    """Raised when permission-related operations fail."""

    def __init__(
        self,
        message: str,
        resource: str = None,
        required_permission: str = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.resource = resource
        self.required_permission = required_permission
        if resource:
            self.details["resource"] = resource
        if required_permission:
            self.details["required_permission"] = required_permission


class CustomTimeoutError(RabbitMirrorError):
    """Raised when operations timeout."""

    def __init__(
        self, message: str, timeout_duration: Union[int, float] = None, **kwargs
    ):
        super().__init__(message, **kwargs)
        self.timeout_duration = timeout_duration
        if timeout_duration:
            self.details["timeout_duration"] = timeout_duration


class InternalError(RabbitMirrorError):
    """Raised when internal system errors occur."""

    def __init__(self, message: str, component: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.component = component
        if component:
            self.details["component"] = component


# Error handling utilities
def handle_file_operation_error(func):
    """Decorator to handle common file operation errors."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            raise FileOperationError(
                f"File not found: {e.filename}",
                file_path=e.filename,
                operation="read",
                error_code="FILE_NOT_FOUND",
            ) from e
        except PermissionError as e:
            raise CustomPermissionError(
                f"Permission denied: {e.filename}",
                resource=e.filename,
                required_permission="read/write",
                error_code="PERMISSION_DENIED",
            ) from e
        except IsADirectoryError as e:
            raise FileOperationError(
                f"Expected file but got directory: {e.filename}",
                file_path=e.filename,
                operation="read",
                error_code="IS_DIRECTORY",
            ) from e
        except OSError as e:
            raise FileOperationError(
                f"File operation failed: {str(e)}", error_code="FILE_OPERATION_FAILED"
            ) from e

    return wrapper


def handle_json_operation_error(func):
    """Decorator to handle JSON operation errors."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            raise InvalidFormatError(
                f"Invalid JSON format: {str(e)}", error_code="INVALID_JSON"
            ) from e
        except TypeError as e:
            raise DataProcessingError(
                f"JSON serialization error: {str(e)}",
                error_code="JSON_SERIALIZATION_ERROR",
            ) from e

    return wrapper


def handle_network_error(func):
    """Decorator to handle network operation errors."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ConnectionError as e:
            raise NetworkError(
                f"Network connection failed: {str(e)}", error_code="CONNECTION_FAILED"
            ) from e
        except TimeoutError as e:
            raise CustomTimeoutError(
                f"Network operation timed out: {str(e)}", error_code="NETWORK_TIMEOUT"
            ) from e
        except Exception as e:
            raise NetworkError(
                f"Network operation failed: {str(e)}", error_code="NETWORK_ERROR"
            ) from e

    return wrapper


def create_error_context(operation: str, **context) -> Dict[str, Any]:
    """Create standardized error context for logging."""
    return {
        "operation": operation,
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        **context,
    }


def format_error_message(error: Exception, include_traceback: bool = False) -> str:
    """Format error message for user display."""
    if isinstance(error, RabbitMirrorError):
        message = f"[{error.error_code}] {error.message}"
        if error.details:
            details = ", ".join(f"{k}: {v}" for k, v in error.details.items())
            message += f" ({details})"
        return message
    message = f"Unexpected error: {str(error)}"
    if include_traceback:
        import traceback  # pylint: disable=import-outside-toplevel

        tb = traceback.format_exc()
        if tb and tb.strip() != "NoneType: None":
            message += f"\n{tb}"
    return message
