"""
Structured Logging Configuration
Production-ready logging with JSON output and request tracking
"""
import logging
import sys
from contextvars import ContextVar
from typing import Any, Dict, Optional
from functools import wraps
import time

import structlog
from structlog.types import Processor

# Context variable for request ID tracking
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def get_request_id() -> Optional[str]:
    """Get current request ID from context."""
    return request_id_ctx.get()


def set_request_id(request_id: str) -> None:
    """Set request ID in context."""
    request_id_ctx.set(request_id)


class RequestIdProcessor:
    """Add request_id to all log entries."""
    
    def __call__(
        self, logger: logging.Logger, method_name: str, event_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        request_id = get_request_id()
        if request_id:
            event_dict["request_id"] = request_id
        return event_dict


class MetricsProcessor:
    """Add metrics-friendly fields to log entries."""
    
    def __call__(
        self, logger: logging.Logger, method_name: str, event_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Add log level as string for filtering
        event_dict["level"] = method_name.upper()
        return event_dict


class ExceptionProcessor:
    """Format exceptions for structured logging."""
    
    def __call__(
        self, logger: logging.Logger, method_name: str, event_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        exc_info = event_dict.pop("exc_info", None)
        if exc_info:
            if isinstance(exc_info, BaseException):
                event_dict["exception_type"] = type(exc_info).__name__
                event_dict["exception_message"] = str(exc_info)
            elif exc_info is True:
                import traceback
                event_dict["exception_traceback"] = traceback.format_exc()
        return event_dict


def configure_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    service_name: str = "aip"
) -> None:
    """
    Configure structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_format: Output format ('json' for production, 'console' for development)
        service_name: Service name to include in logs
    """
    # Shared processors for all outputs
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        RequestIdProcessor(),
        MetricsProcessor(),
        ExceptionProcessor(),
    ]
    
    if log_format == "json":
        # Production: JSON output
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ]
    else:
        # Development: Colored console output
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging to work with structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


# Decorator for logging function execution time
def log_execution_time(logger_name: str = None):
    """
    Decorator to log function execution time.
    
    Usage:
        @log_execution_time("my_service")
        async def my_function():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger.info(
                    f"{func.__name__} completed",
                    function=func.__name__,
                    duration_ms=round(duration_ms, 2),
                    status="success"
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"{func.__name__} failed",
                    function=func.__name__,
                    duration_ms=round(duration_ms, 2),
                    status="error",
                    error=str(e)
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger.info(
                    f"{func.__name__} completed",
                    function=func.__name__,
                    duration_ms=round(duration_ms, 2),
                    status="success"
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"{func.__name__} failed",
                    function=func.__name__,
                    duration_ms=round(duration_ms, 2),
                    status="error",
                    error=str(e)
                )
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def log_api_call(provider: str):
    """
    Decorator specifically for logging external API calls.
    
    Usage:
        @log_api_call("anthropic")
        async def call_claude():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger = get_logger("api_calls")
            start_time = time.time()
            
            logger.info(
                f"API call started: {provider}",
                provider=provider,
                function=func.__name__,
                event="api_call_start"
            )
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                logger.info(
                    f"API call completed: {provider}",
                    provider=provider,
                    function=func.__name__,
                    duration_ms=round(duration_ms, 2),
                    event="api_call_success"
                )
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"API call failed: {provider}",
                    provider=provider,
                    function=func.__name__,
                    duration_ms=round(duration_ms, 2),
                    event="api_call_error",
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
                raise
        
        return wrapper
    return decorator


class LogContext:
    """Helper class for building structured log context."""
    
    def __init__(self, **initial_context):
        self._context = initial_context
    
    def add(self, **kwargs) -> "LogContext":
        """Add fields to context."""
        self._context.update(kwargs)
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Get context as dictionary."""
        return self._context.copy()