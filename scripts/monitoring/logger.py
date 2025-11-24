"""
Structured Logging Module
Provides JSON-formatted structured logging for better observability.
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional


class StructuredLogger:
    """
    Structured logger that outputs JSON-formatted logs.
    
    Features:
    - JSON format for easy parsing
    - Contextual information (timestamp, level, service)
    - Support for structured data
    - Multiple log levels
    - File and console output
    """

    def __init__(
        self,
        name: str,
        level: int = logging.INFO,
        log_file: Optional[str] = None,
        service_name: str = "top-tier-global-hub-ai",
    ):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional file path for logging
            service_name: Service identifier
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.service_name = service_name
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Create JSON formatter
        formatter = JsonFormatter(service_name=service_name)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (if specified)
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message: str, **kwargs):
        """Log debug message with optional structured data."""
        self._log(logging.DEBUG, message, kwargs)

    def info(self, message: str, **kwargs):
        """Log info message with optional structured data."""
        self._log(logging.INFO, message, kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with optional structured data."""
        self._log(logging.WARNING, message, kwargs)

    def error(self, message: str, **kwargs):
        """Log error message with optional structured data."""
        self._log(logging.ERROR, message, kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message with optional structured data."""
        self._log(logging.CRITICAL, message, kwargs)

    def _log(self, level: int, message: str, extra_data: Dict[str, Any]):
        """
        Internal logging method.
        
        Args:
            level: Log level
            message: Log message
            extra_data: Additional structured data
        """
        self.logger.log(level, message, extra={"structured_data": extra_data})

    def log_request(self, method: str, path: str, status_code: int, duration_ms: float, **kwargs):
        """
        Log HTTP request with structured data.
        
        Args:
            method: HTTP method
            path: Request path
            status_code: Response status code
            duration_ms: Request duration in milliseconds
            **kwargs: Additional data
        """
        self.info(
            f"{method} {path} - {status_code}",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            **kwargs,
        )

    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """
        Log exception with context.
        
        Args:
            error: Exception object
            context: Additional context information
        """
        self.error(
            str(error),
            error_type=type(error).__name__,
            error_message=str(error),
            context=context or {},
        )

    def log_metric(self, metric_name: str, value: float, unit: str = "", **kwargs):
        """
        Log a metric value.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
            **kwargs: Additional metadata
        """
        self.info(
            f"Metric: {metric_name}",
            metric_name=metric_name,
            metric_value=value,
            metric_unit=unit,
            **kwargs,
        )


class JsonFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    """

    def __init__(self, service_name: str = "app"):
        """
        Initialize JSON formatter.
        
        Args:
            service_name: Service identifier
        """
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record
            
        Returns:
            JSON-formatted log string
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": self.service_name,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add structured data if present
        if hasattr(record, "structured_data"):
            log_data.update(record.structured_data)
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }
        
        # Add source location
        log_data["source"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }
        
        return json.dumps(log_data)


# Global logger instance
_logger_instance: Optional[StructuredLogger] = None


def get_logger(
    name: str = "app",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
) -> StructuredLogger:
    """
    Get or create a structured logger instance.
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional log file path
        
    Returns:
        StructuredLogger instance
    """
    global _logger_instance
    
    if _logger_instance is None:
        _logger_instance = StructuredLogger(name, level, log_file)
    
    return _logger_instance


# Example usage
if __name__ == "__main__":
    # Create logger
    logger = get_logger("telegram-bot", level=logging.DEBUG)
    
    # Basic logging
    logger.info("Bot started successfully")
    logger.debug("Debug information", user_id=123456, username="test_user")
    logger.warning("Rate limit approaching", current_rate=45, max_rate=50)
    
    # Log HTTP request
    logger.log_request(
        method="POST",
        path="/api/chat",
        status_code=200,
        duration_ms=156.7,
        user_id=123456,
    )
    
    # Log error
    try:
        raise ValueError("Invalid API key format")
    except Exception as e:
        logger.log_error(e, context={"api_key": "sk-***", "action": "authentication"})
    
    # Log metric
    logger.log_metric(
        metric_name="response_time",
        value=123.45,
        unit="ms",
        endpoint="/api/chat",
    )
    
    print("\n✓ Structured logging examples completed")
