#!/usr/bin/env python3

"""
Test core error handling functionality.
"""

from rabbitmirror.exceptions import (
    ClusteringError,
    DataValidationError,
    ExportError,
    NetworkError,
    ParsingError,
    RabbitMirrorError,
    create_error_context,
    format_error_message,
)


class TestCustomExceptions:
    """Test custom exception classes."""

    def test_rabbit_mirror_error_base(self):
        """Test base exception class."""
        error = RabbitMirrorError("Test error", "TEST_001", {"key": "value"})
        assert error.message == "Test error"
        assert error.error_code == "TEST_001"
        assert error.details == {"key": "value"}

        error_dict = error.to_dict()
        assert error_dict["error_type"] == "RabbitMirrorError"
        assert error_dict["message"] == "Test error"
        assert error_dict["error_code"] == "TEST_001"
        assert error_dict["details"] == {"key": "value"}

    def test_parsing_error_with_file_path(self):
        """Test parsing error with file path."""
        error = ParsingError(
            "Parse failed", file_path="/test/file.html", line_number=42
        )
        assert error.file_path == "/test/file.html"
        assert error.line_number == 42
        assert error.details["file_path"] == "/test/file.html"
        assert error.details["line_number"] == 42

    def test_data_validation_error_with_validation_errors(self):
        """Test data validation error with validation errors."""
        validation_errors = ["Field 'title' is required", "Field 'timestamp' invalid"]
        error = DataValidationError(
            "Validation failed", validation_errors=validation_errors
        )
        assert error.validation_errors == validation_errors
        assert error.details["validation_errors"] == validation_errors

    def test_clustering_error_with_algorithm(self):
        """Test clustering error with algorithm info."""
        error = ClusteringError("Clustering failed", algorithm="DBSCAN")
        assert error.algorithm == "DBSCAN"
        assert error.details["algorithm"] == "DBSCAN"

    def test_export_error_with_format(self):
        """Test export error with format info."""
        error = ExportError("Export failed", export_format="csv")
        assert error.export_format == "csv"
        assert error.details["export_format"] == "csv"

    def test_network_error_with_details(self):
        """Test network error with URL and status code."""
        error = NetworkError(
            "Request failed", url="https://example.com", status_code=404
        )
        assert error.url == "https://example.com"
        assert error.status_code == 404
        assert error.details["url"] == "https://example.com"
        assert error.details["status_code"] == 404


class TestErrorUtilities:
    """Test error handling utilities."""

    def test_format_error_message_with_rabbit_mirror_error(self):
        """Test formatting RabbitMirror error message."""
        error = ParsingError(
            "Parse failed", file_path="/test/file.html", error_code="PARSE_001"
        )
        message = format_error_message(error)
        assert "[PARSE_001]" in message
        assert "Parse failed" in message
        assert "file_path: /test/file.html" in message

    def test_format_error_message_with_standard_error(self):
        """Test formatting standard error message."""
        error = ValueError("Standard error")
        message = format_error_message(error)
        assert "Unexpected error: Standard error" in message

    def test_format_error_message_with_traceback(self):
        """Test formatting error message with traceback."""
        try:
            raise ValueError("Standard error")
        except ValueError as error:
            message = format_error_message(error, include_traceback=True)
            assert "Unexpected error: Standard error" in message
            assert "Traceback" in message

    def test_create_error_context(self):
        """Test creating error context."""
        context = create_error_context("test_operation", file="/test/file.txt", line=42)
        assert context["operation"] == "test_operation"
        assert context["file"] == "/test/file.txt"
        assert context["line"] == 42
        assert "timestamp" in context
