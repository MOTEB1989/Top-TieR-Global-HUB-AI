"""
Centralized structured logging for backend services.
Supports both Arabic and English messages with key=value format.
"""
import logging
import sys
import time
from typing import Any, Dict, Optional


# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name"""
    return logging.getLogger(name)


def format_log_message(
    action: str,
    status: str,
    **kwargs: Any
) -> str:
    """
    Format log message in structured key=value format.
    
    Args:
        action: The action being performed (e.g., "ingestion", "gpt_request")
        status: Status of the action (e.g., "start", "success", "error")
        **kwargs: Additional key-value pairs to include in the log
    
    Returns:
        Formatted log message string
    
    Examples:
        >>> format_log_message("ingestion", "start", source="sama", limit=10)
        'action=ingestion status=start source=sama limit=10'
        
        >>> format_log_message("gpt_request", "success", duration_ms=123.45, tokens=50)
        'action=gpt_request status=success duration_ms=123.45 tokens=50'
    """
    parts = [f"action={action}", f"status={status}"]
    for key, value in kwargs.items():
        if value is not None:
            parts.append(f"{key}={value}")
    return " ".join(parts)


class LogTimer:
    """Context manager for timing operations and logging duration"""
    
    def __init__(self, logger: logging.Logger, action: str, **context: Any):
        """
        Initialize timer for logging operation duration.
        
        Args:
            logger: Logger instance to use
            action: Action being timed
            **context: Additional context to include in logs
        """
        self.logger = logger
        self.action = action
        self.context = context
        self.start_time: Optional[float] = None
    
    def __enter__(self) -> "LogTimer":
        """Start timing and log start message"""
        self.start_time = time.time()
        msg = format_log_message(self.action, "start", **self.context)
        self.logger.info(msg)
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Stop timing and log completion with duration"""
        if self.start_time is None:
            return
        
        duration_ms = (time.time() - self.start_time) * 1000
        
        if exc_type is None:
            # Success case
            msg = format_log_message(
                self.action,
                "success",
                duration_ms=f"{duration_ms:.2f}",
                **self.context
            )
            self.logger.info(msg)
        else:
            # Error case
            msg = format_log_message(
                self.action,
                "error",
                duration_ms=f"{duration_ms:.2f}",
                error=str(exc_val),
                **self.context
            )
            self.logger.error(msg)


# Pre-configured loggers for different modules
api_logger = get_logger("backend.api")
ingestion_logger = get_logger("backend.ingestion")
gpt_logger = get_logger("backend.gpt")
db_logger = get_logger("backend.db")


# Example usage and bilingual messages
EXAMPLE_MESSAGES = {
    "ingestion_start_en": "Starting data ingestion",
    "ingestion_start_ar": "بدء استيعاب البيانات",
    "ingestion_complete_en": "Data ingestion completed successfully",
    "ingestion_complete_ar": "اكتمل استيعاب البيانات بنجاح",
    "gpt_request_en": "Processing GPT request",
    "gpt_request_ar": "معالجة طلب GPT",
    "gpt_response_en": "GPT response generated",
    "gpt_response_ar": "تم إنشاء استجابة GPT",
    "health_check_en": "Performing health check",
    "health_check_ar": "إجراء فحص الصحة",
    "db_connection_en": "Connecting to database",
    "db_connection_ar": "الاتصال بقاعدة البيانات",
}
