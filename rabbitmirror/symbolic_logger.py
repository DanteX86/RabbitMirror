from loguru import logger
from typing import Any, Dict
from pathlib import Path
import json

class SymbolicLogger:
    def __init__(self, log_dir: str = 'logs'):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure loguru logger
        logger.add(
            self.log_dir / 'rabbitmirror.log',
            rotation='1 day',
            retention='1 month',
            level='INFO'
        )

    def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log an event with structured data."""
        logger.info(f"{event_type}: {json.dumps(data)}")

    def log_error(self, error_type: str, error: Exception, context: Dict[str, Any] = None):
        """Log an error with context."""
        error_data = {
            'error_type': error_type,
            'error_message': str(error),
            'context': context or {}
        }
        logger.error(f"Error: {json.dumps(error_data)}")
