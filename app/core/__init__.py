"""
Core utilities for the Adaptive Intelligence Pipeline
"""
from app.core.logging import (
    configure_logging,
    get_logger,
    get_request_id,
    set_request_id,
    log_execution_time,
    log_api_call,
    LogContext
)
from app.core.metrics import (
    setup_metrics,
    track_llm_call,
    track_embedding_call,
    track_vectorstore_operation,
    http_requests_total,
    llm_calls_total,
    rag_queries_total
)
from app.core.middleware import setup_logging_middleware

__all__ = [
    # Logging
    "configure_logging",
    "get_logger",
    "get_request_id",
    "set_request_id",
    "log_execution_time",
    "log_api_call",
    "LogContext",
    # Metrics
    "setup_metrics",
    "track_llm_call",
    "track_embedding_call",
    "track_vectorstore_operation",
    # Middleware
    "setup_logging_middleware",
]