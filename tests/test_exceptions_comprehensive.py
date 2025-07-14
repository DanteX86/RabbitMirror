#!/usr/bin/env python3

"""
Comprehensive tests for all exception classes.
This module aims to achieve 100% coverage of the exceptions module.
"""

import pytest

from rabbitmirror.exceptions import (
    AnalysisError,
    ClusteringError,
    ConfigurationError,
    CustomPermissionError,
    CustomTimeoutError,
    DatabaseError,
    DataProcessingError,
    DataValidationError,
    DependencyError,
    ExportError,
    FileOperationError,
    InternalError,
    InvalidFormatError,
    NetworkError,
    ParsingError,
    PatternDetectionError,
    RabbitMirrorError,
    ResourceError,
    SchemaValidationError,
    SimulationError,
    TrendAnalysisError,
    create_error_context,
    format_error_message,
    handle_file_operation_error,
    handle_json_operation_error,
    handle_network_error,
)


class TestRabbitMirrorError:
    """Test the base RabbitMirrorError class."""

    def test_init_with_minimal_args(self):
        """Test initialization with minimal arguments."""
        error = RabbitMirrorError("Test message")
        assert error.message == "Test message"
        assert error.error_code == "UNKNOWN_ERROR"
        assert error.details == {}

    def test_init_with_all_args(self):
        """Test initialization with all arguments."""
        details = {"key": "value", "number": 42}
        error = RabbitMirrorError("Test message", "TEST_001", details)
        assert error.message == "Test message"
        assert error.error_code == "TEST_001"
        assert error.details == details

    def test_to_dict(self):
        """Test conversion to dictionary."""
        error = RabbitMirrorError("Test message", "TEST_001", {"key": "value"})
        result = error.to_dict()
        expected = {
            "error_type": "RabbitMirrorError",
            "message": "Test message",
            "error_code": "TEST_001",
            "details": {"key": "value"},
        }
        assert result == expected

    def test_inheritance(self):
        """Test that RabbitMirrorError inherits from Exception."""
        error = RabbitMirrorError("Test message")
        assert isinstance(error, Exception)
        assert str(error) == "Test message"


class TestDataProcessingError:
    """Test DataProcessingError class."""

    def test_inheritance(self):
        """Test inheritance from RabbitMirrorError."""
        error = DataProcessingError("Processing failed")
        assert isinstance(error, RabbitMirrorError)
        assert error.message == "Processing failed"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        error = DataProcessingError("Processing failed", "PROC_001")
        result = error.to_dict()
        assert result["error_type"] == "DataProcessingError"
        assert result["message"] == "Processing failed"


class TestParsingError:
    """Test ParsingError class."""

    def test_init_with_file_path_and_line(self):
        """Test initialization with file path and line number."""
        error = ParsingError(
            "Parse failed",
            file_path="/test/file.html",
            line_number=42,
            error_code="PARSE_001",
        )
        assert error.file_path == "/test/file.html"
        assert error.line_number == 42
        assert error.details["file_path"] == "/test/file.html"
        assert error.details["line_number"] == 42

    def test_init_without_optional_args(self):
        """Test initialization without optional arguments."""
        error = ParsingError("Parse failed")
        assert error.file_path is None
        assert error.line_number is None
        assert "file_path" not in error.details
        assert "line_number" not in error.details

    def test_init_with_partial_args(self):
        """Test initialization with only file path."""
        error = ParsingError("Parse failed", file_path="/test/file.html")
        assert error.file_path == "/test/file.html"
        assert error.line_number is None
        assert error.details["file_path"] == "/test/file.html"
        assert "line_number" not in error.details

    def test_inheritance(self):
        """Test inheritance from DataProcessingError."""
        error = ParsingError("Parse failed")
        assert isinstance(error, DataProcessingError)
        assert isinstance(error, RabbitMirrorError)


class TestInvalidFormatError:
    """Test InvalidFormatError class."""

    def test_inheritance(self):
        """Test inheritance from ParsingError."""
        error = InvalidFormatError("Invalid format")
        assert isinstance(error, ParsingError)
        assert isinstance(error, DataProcessingError)
        assert isinstance(error, RabbitMirrorError)


class TestDataValidationError:
    """Test DataValidationError class."""

    def test_init_with_validation_errors(self):
        """Test initialization with validation errors."""
        validation_errors = ["Field required", "Invalid type"]
        error = DataValidationError(
            "Validation failed", validation_errors=validation_errors
        )
        assert error.validation_errors == validation_errors
        assert error.details["validation_errors"] == validation_errors

    def test_init_without_validation_errors(self):
        """Test initialization without validation errors."""
        error = DataValidationError("Validation failed")
        assert error.validation_errors == []
        assert "validation_errors" not in error.details

    def test_inheritance(self):
        """Test inheritance from DataProcessingError."""
        error = DataValidationError("Validation failed")
        assert isinstance(error, DataProcessingError)
        assert isinstance(error, RabbitMirrorError)


class TestSchemaValidationError:
    """Test SchemaValidationError class."""

    def test_init_with_schema_path(self):
        """Test initialization with schema path."""
        error = SchemaValidationError(
            "Schema validation failed", schema_path="/schemas/test.json"
        )
        assert error.schema_path == "/schemas/test.json"
        assert error.details["schema_path"] == "/schemas/test.json"

    def test_init_without_schema_path(self):
        """Test initialization without schema path."""
        error = SchemaValidationError("Schema validation failed")
        assert error.schema_path is None
        assert "schema_path" not in error.details

    def test_inheritance(self):
        """Test inheritance from DataValidationError."""
        error = SchemaValidationError("Schema validation failed")
        assert isinstance(error, DataValidationError)
        assert isinstance(error, DataProcessingError)
        assert isinstance(error, RabbitMirrorError)


class TestFileOperationError:
    """Test FileOperationError class."""

    def test_init_with_file_path_and_operation(self):
        """Test initialization with file path and operation."""
        error = FileOperationError(
            "File operation failed", file_path="/test/file.txt", operation="read"
        )
        assert error.file_path == "/test/file.txt"
        assert error.operation == "read"
        assert error.details["file_path"] == "/test/file.txt"
        assert error.details["operation"] == "read"

    def test_init_without_optional_args(self):
        """Test initialization without optional arguments."""
        error = FileOperationError("File operation failed")
        assert error.file_path is None
        assert error.operation is None
        assert "file_path" not in error.details
        assert "operation" not in error.details

    def test_inheritance(self):
        """Test inheritance from RabbitMirrorError."""
        error = FileOperationError("File operation failed")
        assert isinstance(error, RabbitMirrorError)


class TestConfigurationError:
    """Test ConfigurationError class."""

    def test_init_with_config_key(self):
        """Test initialization with config key."""
        error = ConfigurationError("Config error", config_key="database.host")
        assert error.config_key == "database.host"
        assert error.details["config_key"] == "database.host"

    def test_init_without_config_key(self):
        """Test initialization without config key."""
        error = ConfigurationError("Config error")
        assert error.config_key is None
        assert "config_key" not in error.details

    def test_inheritance(self):
        """Test inheritance from RabbitMirrorError."""
        error = ConfigurationError("Config error")
        assert isinstance(error, RabbitMirrorError)


class TestAnalysisError:
    """Test AnalysisError class."""

    def test_inheritance(self):
        """Test inheritance from RabbitMirrorError."""
        error = AnalysisError("Analysis failed")
        assert isinstance(error, RabbitMirrorError)


class TestClusteringError:
    """Test ClusteringError class."""

    def test_init_with_algorithm(self):
        """Test initialization with algorithm."""
        error = ClusteringError("Clustering failed", algorithm="DBSCAN")
        assert error.algorithm == "DBSCAN"
        assert error.details["algorithm"] == "DBSCAN"

    def test_init_without_algorithm(self):
        """Test initialization without algorithm."""
        error = ClusteringError("Clustering failed")
        assert error.algorithm is None
        assert "algorithm" not in error.details

    def test_inheritance(self):
        """Test inheritance from AnalysisError."""
        error = ClusteringError("Clustering failed")
        assert isinstance(error, AnalysisError)
        assert isinstance(error, RabbitMirrorError)


class TestPatternDetectionError:
    """Test PatternDetectionError class."""

    def test_inheritance(self):
        """Test inheritance from AnalysisError."""
        error = PatternDetectionError("Pattern detection failed")
        assert isinstance(error, AnalysisError)
        assert isinstance(error, RabbitMirrorError)


class TestTrendAnalysisError:
    """Test TrendAnalysisError class."""

    def test_init_with_metric(self):
        """Test initialization with metric."""
        error = TrendAnalysisError("Trend analysis failed", metric="engagement")
        assert error.metric == "engagement"
        assert error.details["metric"] == "engagement"

    def test_init_without_metric(self):
        """Test initialization without metric."""
        error = TrendAnalysisError("Trend analysis failed")
        assert error.metric is None
        assert "metric" not in error.details

    def test_inheritance(self):
        """Test inheritance from AnalysisError."""
        error = TrendAnalysisError("Trend analysis failed")
        assert isinstance(error, AnalysisError)
        assert isinstance(error, RabbitMirrorError)


class TestSimulationError:
    """Test SimulationError class."""

    def test_init_with_simulation_type(self):
        """Test initialization with simulation type."""
        error = SimulationError("Simulation failed", simulation_type="monte_carlo")
        assert error.simulation_type == "monte_carlo"
        assert error.details["simulation_type"] == "monte_carlo"

    def test_init_without_simulation_type(self):
        """Test initialization without simulation type."""
        error = SimulationError("Simulation failed")
        assert error.simulation_type is None
        assert "simulation_type" not in error.details

    def test_inheritance(self):
        """Test inheritance from RabbitMirrorError."""
        error = SimulationError("Simulation failed")
        assert isinstance(error, RabbitMirrorError)


class TestExportError:
    """Test ExportError class."""

    def test_init_with_export_format(self):
        """Test initialization with export format."""
        error = ExportError("Export failed", export_format="csv")
        assert error.export_format == "csv"
        assert error.details["export_format"] == "csv"

    def test_init_without_export_format(self):
        """Test initialization without export format."""
        error = ExportError("Export failed")
        assert error.export_format is None
        assert "export_format" not in error.details

    def test_inheritance(self):
        """Test inheritance from RabbitMirrorError."""
        error = ExportError("Export failed")
        assert isinstance(error, RabbitMirrorError)


class TestDatabaseError:
    """Test DatabaseError class."""

    def test_init_with_operation(self):
        """Test initialization with operation."""
        error = DatabaseError("Database error", operation="SELECT")
        assert error.operation == "SELECT"
        assert error.details["operation"] == "SELECT"

    def test_init_without_operation(self):
        """Test initialization without operation."""
        error = DatabaseError("Database error")
        assert error.operation is None
        assert "operation" not in error.details

    def test_inheritance(self):
        """Test inheritance from RabbitMirrorError."""
        error = DatabaseError("Database error")
        assert isinstance(error, RabbitMirrorError)


class TestNetworkError:
    """Test NetworkError class."""

    def test_init_with_url_and_status_code(self):
        """Test initialization with URL and status code."""
        error = NetworkError(
            "Network error", url="https://example.com", status_code=404
        )
        assert error.url == "https://example.com"
        assert error.status_code == 404
        assert error.details["url"] == "https://example.com"
        assert error.details["status_code"] == 404

    def test_init_without_optional_args(self):
        """Test initialization without optional arguments."""
        error = NetworkError("Network error")
        assert error.url is None
        assert error.status_code is None
        assert "url" not in error.details
        assert "status_code" not in error.details

    def test_init_with_partial_args(self):
        """Test initialization with only URL."""
        error = NetworkError("Network error", url="https://example.com")
        assert error.url == "https://example.com"
        assert error.status_code is None
        assert error.details["url"] == "https://example.com"
        assert "status_code" not in error.details

    def test_inheritance(self):
        """Test inheritance from RabbitMirrorError."""
        error = NetworkError("Network error")
        assert isinstance(error, RabbitMirrorError)


class TestResourceError:
    """Test ResourceError class."""

    def test_init_with_resource_type(self):
        """Test initialization with resource type."""
        error = ResourceError("Resource error", resource_type="memory")
        assert error.resource_type == "memory"
        assert error.details["resource_type"] == "memory"

    def test_init_without_resource_type(self):
        """Test initialization without resource type."""
        error = ResourceError("Resource error")
        assert error.resource_type is None
        assert "resource_type" not in error.details

    def test_inheritance(self):
        """Test inheritance from RabbitMirrorError."""
        error = ResourceError("Resource error")
        assert isinstance(error, RabbitMirrorError)


class TestDependencyError:
    """Test DependencyError class."""

    def test_init_with_dependency_and_version(self):
        """Test initialization with dependency and version."""
        error = DependencyError(
            "Dependency error", dependency="numpy", required_version="1.20.0"
        )
        assert error.dependency == "numpy"
        assert error.required_version == "1.20.0"
        assert error.details["dependency"] == "numpy"
        assert error.details["required_version"] == "1.20.0"

    def test_init_without_optional_args(self):
        """Test initialization without optional arguments."""
        error = DependencyError("Dependency error")
        assert error.dependency is None
        assert error.required_version is None
        assert "dependency" not in error.details
        assert "required_version" not in error.details

    def test_inheritance(self):
        """Test inheritance from RabbitMirrorError."""
        error = DependencyError("Dependency error")
        assert isinstance(error, RabbitMirrorError)


class TestCustomPermissionError:
    """Test CustomPermissionError class."""

    def test_init_with_resource_and_permission(self):
        """Test initialization with resource and permission."""
        error = CustomPermissionError(
            "Permission denied", resource="/test/file.txt", required_permission="read"
        )
        assert error.resource == "/test/file.txt"
        assert error.required_permission == "read"
        assert error.details["resource"] == "/test/file.txt"
        assert error.details["required_permission"] == "read"

    def test_init_without_optional_args(self):
        """Test initialization without optional arguments."""
        error = CustomPermissionError("Permission denied")
        assert error.resource is None
        assert error.required_permission is None
        assert "resource" not in error.details
        assert "required_permission" not in error.details

    def test_inheritance(self):
        """Test inheritance from RabbitMirrorError."""
        error = CustomPermissionError("Permission denied")
        assert isinstance(error, RabbitMirrorError)


class TestCustomTimeoutError:
    """Test CustomTimeoutError class."""

    def test_init_with_timeout_duration(self):
        """Test initialization with timeout duration."""
        error = CustomTimeoutError("Operation timed out", timeout_duration=30.5)
        assert error.timeout_duration == 30.5
        assert error.details["timeout_duration"] == 30.5

    def test_init_with_integer_timeout(self):
        """Test initialization with integer timeout duration."""
        error = CustomTimeoutError("Operation timed out", timeout_duration=30)
        assert error.timeout_duration == 30
        assert error.details["timeout_duration"] == 30

    def test_init_without_timeout_duration(self):
        """Test initialization without timeout duration."""
        error = CustomTimeoutError("Operation timed out")
        assert error.timeout_duration is None
        assert "timeout_duration" not in error.details

    def test_inheritance(self):
        """Test inheritance from RabbitMirrorError."""
        error = CustomTimeoutError("Operation timed out")
        assert isinstance(error, RabbitMirrorError)


class TestInternalError:
    """Test InternalError class."""

    def test_init_with_component(self):
        """Test initialization with component."""
        error = InternalError("Internal error", component="parser")
        assert error.component == "parser"
        assert error.details["component"] == "parser"

    def test_init_without_component(self):
        """Test initialization without component."""
        error = InternalError("Internal error")
        assert error.component is None
        assert "component" not in error.details

    def test_inheritance(self):
        """Test inheritance from RabbitMirrorError."""
        error = InternalError("Internal error")
        assert isinstance(error, RabbitMirrorError)


class TestErrorUtilities:
    """Test error handling utility functions."""

    def test_format_error_message_with_rabbit_mirror_error(self):
        """Test formatting RabbitMirror error message."""
        error = ParsingError(
            "Parse failed", file_path="/test/file.html", error_code="PARSE_001"
        )
        message = format_error_message(error)
        assert "[PARSE_001]" in message
        assert "Parse failed" in message
        assert "file_path: /test/file.html" in message

    def test_format_error_message_with_empty_details(self):
        """Test formatting error message with empty details."""
        error = RabbitMirrorError("Test error", "TEST_001", {})
        message = format_error_message(error)
        assert "[TEST_001]" in message
        assert "Test error" in message
        assert "Details:" not in message

    def test_format_error_message_with_standard_error(self):
        """Test formatting standard error message."""
        error = ValueError("Standard error")
        message = format_error_message(error)
        assert "Unexpected error: Standard error" in message
        # The function does not include the exception type in the message
        assert message == "Unexpected error: Standard error"

    def test_format_error_message_with_traceback(self):
        """Test formatting error message with traceback."""
        try:
            raise ValueError("Standard error")
        except ValueError as error:
            message = format_error_message(error, include_traceback=True)
            assert "Unexpected error: Standard error" in message
            assert "Traceback" in message

    def test_format_error_message_without_traceback(self):
        """Test formatting error message without traceback."""
        error = ValueError("Standard error")
        message = format_error_message(error, include_traceback=False)
        assert "Unexpected error: Standard error" in message
        assert "Traceback" not in message

    def test_create_error_context_with_args(self):
        """Test creating error context with arguments."""
        context = create_error_context(
            "test_operation", file="/test/file.txt", line=42, custom_key="custom_value"
        )
        assert context["operation"] == "test_operation"
        assert context["file"] == "/test/file.txt"
        assert context["line"] == 42
        assert context["custom_key"] == "custom_value"
        assert "timestamp" in context

    def test_create_error_context_minimal(self):
        """Test creating error context with minimal arguments."""
        context = create_error_context("test_operation")
        assert context["operation"] == "test_operation"
        assert "timestamp" in context
        assert len(context) == 2  # operation and timestamp only

    def test_create_error_context_timestamp_format(self):
        """Test that create_error_context generates proper timestamp."""
        context = create_error_context("test_operation")
        timestamp = context["timestamp"]
        assert isinstance(timestamp, str)
        assert "T" in timestamp  # ISO format contains 'T'


class TestErrorDecorators:
    """Test error handling decorators."""

    def test_handle_file_operation_error_file_not_found(self):
        """Test file operation decorator with FileNotFoundError."""

        @handle_file_operation_error
        def test_function():
            # Create FileNotFoundError with proper errno and filename
            error = FileNotFoundError("test.txt")
            error.filename = "test.txt"
            raise error

        with pytest.raises(FileOperationError) as exc_info:
            test_function()

        error = exc_info.value
        assert "File not found: test.txt" in error.message
        assert error.error_code == "FILE_NOT_FOUND"
        assert error.file_path == "test.txt"
        assert error.operation == "read"

    def test_handle_file_operation_error_permission_denied(self):
        """Test file operation decorator with PermissionError."""

        @handle_file_operation_error
        def test_function():
            raise PermissionError("Permission denied")

        with pytest.raises(CustomPermissionError) as exc_info:
            test_function()

        error = exc_info.value
        assert "Permission denied" in error.message
        assert error.error_code == "PERMISSION_DENIED"
        assert error.required_permission == "read/write"

    def test_handle_file_operation_error_is_directory(self):
        """Test file operation decorator with IsADirectoryError."""

        @handle_file_operation_error
        def test_function():
            raise IsADirectoryError("Expected file but got directory")

        with pytest.raises(FileOperationError) as exc_info:
            test_function()

        error = exc_info.value
        assert "Expected file but got directory" in error.message
        assert error.error_code == "IS_DIRECTORY"
        assert error.operation == "read"

    def test_handle_file_operation_error_os_error(self):
        """Test file operation decorator with OSError."""

        @handle_file_operation_error
        def test_function():
            raise OSError("OS error occurred")

        with pytest.raises(FileOperationError) as exc_info:
            test_function()

        error = exc_info.value
        assert "File operation failed" in error.message
        assert error.error_code == "FILE_OPERATION_FAILED"

    def test_handle_file_operation_error_success(self):
        """Test file operation decorator with successful operation."""

        @handle_file_operation_error
        def test_function():
            return "success"

        result = test_function()
        assert result == "success"

    def test_handle_json_operation_error_value_error(self):
        """Test JSON operation decorator with ValueError."""

        @handle_json_operation_error
        def test_function():
            raise ValueError("Invalid JSON")

        with pytest.raises(InvalidFormatError) as exc_info:
            test_function()

        error = exc_info.value
        assert "Invalid JSON format" in error.message
        assert error.error_code == "INVALID_JSON"

    def test_handle_json_operation_error_type_error(self):
        """Test JSON operation decorator with TypeError."""

        @handle_json_operation_error
        def test_function():
            raise TypeError("JSON serialization error")

        with pytest.raises(DataProcessingError) as exc_info:
            test_function()

        error = exc_info.value
        assert "JSON serialization error" in error.message
        assert error.error_code == "JSON_SERIALIZATION_ERROR"

    def test_handle_json_operation_error_success(self):
        """Test JSON operation decorator with successful operation."""

        @handle_json_operation_error
        def test_function():
            return {"result": "success"}

        result = test_function()
        assert result == {"result": "success"}

    def test_handle_network_error_connection_error(self):
        """Test network operation decorator with ConnectionError."""

        @handle_network_error
        def test_function():
            raise ConnectionError("Connection failed")

        with pytest.raises(NetworkError) as exc_info:
            test_function()

        error = exc_info.value
        assert "Network connection failed" in error.message
        assert error.error_code == "CONNECTION_FAILED"

    def test_handle_network_error_timeout_error(self):
        """Test network operation decorator with TimeoutError."""

        @handle_network_error
        def test_function():
            raise TimeoutError("Operation timed out")

        with pytest.raises(CustomTimeoutError) as exc_info:
            test_function()

        error = exc_info.value
        assert "Network operation timed out" in error.message
        assert error.error_code == "NETWORK_TIMEOUT"

    def test_handle_network_error_generic_exception(self):
        """Test network operation decorator with generic Exception."""

        @handle_network_error
        def test_function():
            raise Exception("Generic network error")

        with pytest.raises(NetworkError) as exc_info:
            test_function()

        error = exc_info.value
        assert "Network operation failed" in error.message
        assert error.error_code == "NETWORK_ERROR"

    def test_handle_network_error_success(self):
        """Test network operation decorator with successful operation."""

        @handle_network_error
        def test_function():
            return "network_success"

        result = test_function()
        assert result == "network_success"


class TestErrorIntegration:
    """Test error integration scenarios."""

    def test_error_chaining(self):
        """Test error chaining with different exception types."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise ParsingError("Parse failed", error_code="PARSE_001") from e
        except ParsingError as error:
            assert error.message == "Parse failed"
            assert error.error_code == "PARSE_001"
            assert error.__cause__ is not None
            assert isinstance(error.__cause__, ValueError)

    def test_error_dict_serialization(self):
        """Test that error dictionaries are properly serializable."""
        import json

        error = NetworkError(
            "Network failed",
            url="https://example.com",
            status_code=404,
            error_code="NET_001",
        )
        error_dict = error.to_dict()

        # Should be JSON serializable
        json_str = json.dumps(error_dict)
        reconstructed = json.loads(json_str)

        assert reconstructed["error_type"] == "NetworkError"
        assert reconstructed["message"] == "Network failed"
        assert reconstructed["error_code"] == "NET_001"
        assert reconstructed["details"]["url"] == "https://example.com"
        assert reconstructed["details"]["status_code"] == 404
