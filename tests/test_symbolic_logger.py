from unittest.mock import patch

from rabbitmirror.symbolic_logger import SymbolicLogger


def test_log_event():
    logger = SymbolicLogger(log_dir="test_logs")
    event_type = "test_event"
    data = {"key": "value"}
    with patch("loguru.logger.info") as mock_info:
        logger.log_event(event_type, data)
        mock_info.assert_called_once_with(f'{event_type}: {{"key": "value"}}')


def test_log_error():
    logger = SymbolicLogger(log_dir="test_logs")
    error_type = "test_error"
    error = Exception("something went wrong")
    context = {"context_key": "context_value"}
    with patch("loguru.logger.error") as mock_error:
        logger.log_error(error_type, error, context)
        # expected_call = {
        #     "error_type": error_type,
        #     "error_message": str(error),
        #     "context": context,
        # }
        mock_error.assert_called_once_with(
            'Error: {"error_type": "test_error", "error_message": "something went '
            'wrong", "context": {"context_key": "context_value"}}'
        )


def test_log_error_without_context():
    logger = SymbolicLogger(log_dir="test_logs")
    error_type = "test_error_without_context"
    error = Exception("Error without context")
    with patch("loguru.logger.error") as mock_error:
        logger.log_error(error_type, error)
        # expected_call = {
        #     "error_type": error_type,
        #     "error_message": str(error),
        #     "context": {},
        # }
        mock_error.assert_called_once_with(
            'Error: {"error_type": "test_error_without_context", "error_message": '
            '"Error without context", "context": {}}'
        )
