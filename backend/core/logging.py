"""
Enhanced Logging Configuration

This module provides structured logging with trace IDs and context.
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
from contextvars import ContextVar
from uuid import uuid4

from core.config import settings


# Context variable for trace ID
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs structured JSON logs.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON formatted log string
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": trace_id_var.get(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data)


class ContextFilter(logging.Filter):
    """
    Filter that adds context information to log records.
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add context information to record.
        
        Args:
            record: Log record to filter
            
        Returns:
            True to include record
        """
        record.trace_id = trace_id_var.get()
        return True


def setup_logging() -> None:
    """
    Configure application logging.
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Set formatter based on environment
    if settings.ENVIRONMENT == "production":
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(trace_id)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    console_handler.addFilter(ContextFilter())
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger
    """
    return logging.getLogger(name)


def set_trace_id(trace_id: str = None) -> str:
    """
    Set trace ID for current context.
    
    Args:
        trace_id: Optional trace ID (generated if not provided)
        
    Returns:
        Trace ID that was set
    """
    if not trace_id:
        trace_id = str(uuid4())
    
    trace_id_var.set(trace_id)
    return trace_id


def get_trace_id() -> str:
    """
    Get current trace ID.
    
    Returns:
        Current trace ID
    """
    return trace_id_var.get()


def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    **kwargs: Any
) -> None:
    """
    Log message with additional context.
    
    Args:
        logger: Logger to use
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        message: Log message
        **kwargs: Additional context fields
    """
    log_func = getattr(logger, level.lower())
    
    # Create log record with extra fields
    extra = {"extra_fields": kwargs}
    log_func(message, extra=extra)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter that adds context to all log messages.
    """
    
    def process(self, msg: str, kwargs: Dict) -> tuple:
        """
        Process log message and kwargs.
        
        Args:
            msg: Log message
            kwargs: Log kwargs
            
        Returns:
            Processed message and kwargs
        """
        # Add trace ID to message
        trace_id = get_trace_id()
        if trace_id:
            msg = f"[{trace_id}] {msg}"
        
        # Add extra context
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        
        kwargs["extra"].update(self.extra)
        
        return msg, kwargs

