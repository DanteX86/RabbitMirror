# Comprehensive Error Handling in RabbitMirror

This document outlines the comprehensive error handling system implemented in RabbitMirror, providing better debugging, user feedback, and system robustness.

## Overview

RabbitMirror now includes a robust error handling system with:

- **Custom exception hierarchy** for domain-specific errors
- **Structured error context** with detailed information
- **Consistent error formatting** across all modules
- **Comprehensive logging** with error context
- **Graceful error recovery** where possible
- **User-friendly error messages** with actionable information

## Custom Exception Hierarchy

### Base Exception
- `RabbitMirrorError`: Base exception for all RabbitMirror errors
  - Includes error code, message, and context details
  - Provides serialization to dictionary for logging

### Data Processing Errors
- `DataProcessingError`: General data processing failures
- `ParsingError`: HTML/data parsing failures
- `InvalidFormatError`: Invalid file format or data structure
- `DataValidationError`: Data validation failures
- `SchemaValidationError`: Schema validation failures

### File and I/O Errors
- `FileOperationError`: File system operations
- `ConfigurationError`: Configuration-related errors
- `ExportError`: Data export failures

### Analysis Errors
- `AnalysisError`: General analysis failures
- `ClusteringError`: Clustering algorithm errors
- `PatternDetectionError`: Pattern detection failures
- `TrendAnalysisError`: Trend analysis errors
- `SimulationError`: Profile simulation errors

### System Errors
- `NetworkError`: Network operation failures
- `ResourceError`: Resource allocation/access errors
- `DependencyError`: Missing or incompatible dependencies
- `PermissionError`: Permission-related failures
- `TimeoutError`: Operation timeouts
- `InternalError`: Internal system errors

## Error Handling Features

### 1. Structured Error Context
```python
# Errors include comprehensive context
error = ParsingError(
    "Invalid timestamp format",
    file_path="/path/to/file.html",
    line_number=42,
    error_code="INVALID_TIMESTAMP"
)

# Context is automatically included in error details
error.details  # {"file_path": "/path/to/file.html", "line_number": 42}
```

### 2. Error Utilities
```python
# Error message formatting
from rabbitmirror.exceptions import format_error_message

formatted_msg = format_error_message(error)
# Output: "[INVALID_TIMESTAMP] Invalid timestamp format (file_path: /path/to/file.html, line_number: 42)"

# Error context creation
from rabbitmirror.exceptions import create_error_context

context = create_error_context("parse_operation", file="input.html", user_id="123")
# Creates standardized context with timestamp and operation details
```

### 3. Decorator-based Error Handling
```python
from rabbitmirror.exceptions import handle_file_operation_error

@handle_file_operation_error
def read_file(path):
    # Automatically handles FileNotFoundError, PermissionError, etc.
    # and converts them to appropriate RabbitMirror exceptions
    pass
```

## Module-Specific Improvements

### Parser Module (`parser.py`)
- **File not found**: Clear error when input file doesn't exist
- **Invalid HTML**: Graceful handling of malformed HTML
- **Timestamp parsing**: Specific errors for invalid date formats
- **Encoding issues**: Proper handling of file encoding problems

### Export Formatter (`export_formatter.py`)
- **Format validation**: Early validation of export formats
- **File permissions**: Clear errors for write permission issues
- **Data structure validation**: Validation of input data structure
- **Format-specific errors**: Specific handling for JSON, YAML, CSV, Excel errors

### Cluster Engine (`cluster_engine.py`)
- **Parameter validation**: Validation of clustering parameters
- **Data validation**: Comprehensive validation of input data
- **Algorithm errors**: Specific handling of scikit-learn errors
- **Empty data handling**: Graceful handling of empty datasets

### CLI Module (`cli.py`)
- **Command validation**: Validation of CLI arguments
- **Error propagation**: Proper error propagation with context
- **User-friendly messages**: Clear error messages for end users
- **Exit codes**: Proper exit codes for different error types

## Error Logging

### Structured Logging
```python
# Errors are logged with full context
symbolic_logger.log_error("operation_failed", error.to_dict())

# Includes:
# - Error type and code
# - Error message
# - Context details (file paths, parameters, etc.)
# - Timestamp
# - Stack trace (when appropriate)
```

### Log Levels
- **ERROR**: Actual errors that prevent operation completion
- **WARNING**: Issues that don't prevent operation but may indicate problems
- **INFO**: Operational information about error handling

## User Experience Improvements

### 1. Clear Error Messages
```bash
# Before
❌ Error: list index out of range

# After
❌ [INVALID_ENTRY_TYPE] Entry 0 is not a dictionary (file_path: /path/to/file.html)
```

### 2. Actionable Feedback
```bash
# File not found
❌ [FILE_NOT_FOUND] File not found: /path/to/file.html
   → Check if the file exists and you have read permissions

# Invalid format
❌ [UNSUPPORTED_FORMAT] Unsupported file format: .txt
   → Supported formats: .json, .yaml, .yml, .csv, .xlsx, .xls
```

### 3. Context-Aware Errors
```bash
# Clustering error with parameters
❌ [INVALID_EPS_PARAMETER] eps parameter must be positive (algorithm: DBSCAN, eps: -0.1)

# Export error with format
❌ [EXPORT_FAILED] Export failed for format csv (export_format: csv, file_path: /output/data.csv)
```

## Testing

### Comprehensive Test Coverage
- **Unit tests**: Test each exception type and error condition
- **Integration tests**: Test error propagation across modules
- **Edge case tests**: Test error handling in unusual scenarios
- **CLI tests**: Test command-line error handling

### Test Files
- `tests/test_error_handling.py`: Comprehensive error handling tests
- Module-specific tests updated to handle new exceptions
- CLI tests updated for new error messages

## Best Practices

### 1. Error Raising
```python
# Good: Specific error with context
raise DataValidationError(
    "Missing required field",
    validation_errors=["Field 'title' is required"],
    error_code="MISSING_FIELD"
)

# Bad: Generic error
raise ValueError("Invalid data")
```

### 2. Error Handling
```python
# Good: Handle specific errors
try:
    result = process_data(data)
except DataValidationError as e:
    logger.log_error("validation_failed", e.to_dict())
    return handle_validation_error(e)
except ParsingError as e:
    logger.log_error("parsing_failed", e.to_dict())
    return handle_parsing_error(e)

# Bad: Catch all exceptions
try:
    result = process_data(data)
except Exception as e:
    print(f"Error: {e}")
```

### 3. Error Context
```python
# Good: Include relevant context
context = create_error_context(
    "cluster_analysis",
    file_path=input_file,
    algorithm="DBSCAN",
    parameters={"eps": 0.5, "min_samples": 5}
)

# Bad: No context
# Just raise the error without context
```

## Performance Considerations

### 1. Lazy Error Context Creation
- Error context is only created when needed
- Expensive operations (like file stats) are deferred

### 2. Error Caching
- Error messages are formatted on-demand
- Repeated errors don't regenerate context

### 3. Minimal Overhead
- Error handling adds minimal overhead to normal operations
- Only active during error conditions

## Migration Guide

### For Existing Code
1. **Update imports**: Add exception imports where needed
2. **Update exception handling**: Replace generic exceptions with specific ones
3. **Update tests**: Modify tests to expect new exception types
4. **Update error messages**: Use new error formatting utilities

### For New Code
1. **Use specific exceptions**: Choose the most appropriate exception type
2. **Include context**: Always include relevant context information
3. **Use error utilities**: Leverage formatting and context creation utilities
4. **Test error paths**: Ensure error conditions are tested

## Future Enhancements

### Planned Features
1. **Error recovery strategies**: Automatic retry and recovery mechanisms
2. **Error reporting**: Built-in error reporting to external services
3. **Error analytics**: Analysis of error patterns and frequencies
4. **Internationalization**: Multi-language error messages

### Extension Points
1. **Custom error handlers**: Plugin system for custom error handling
2. **Error transforms**: Custom error message transformations
3. **Context providers**: Custom context information providers
4. **Error filters**: Filtering and routing of errors

## Conclusion

The comprehensive error handling system in RabbitMirror provides:

- **Better debugging**: Clear error messages with context
- **Improved user experience**: Actionable error messages
- **System robustness**: Graceful handling of error conditions
- **Maintainability**: Consistent error handling patterns
- **Observability**: Comprehensive error logging and monitoring

This system ensures that RabbitMirror can handle errors gracefully while providing users and developers with the information they need to understand and resolve issues quickly.
