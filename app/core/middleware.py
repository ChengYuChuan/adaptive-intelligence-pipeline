"""
HTTP Middleware for request tracking and logging
"""
import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger, set_request_id, get_request_id

logger = get_logger(__name__)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware to ensure every request has a unique request ID."""
    
    HEADER_NAME = "X-Request-ID"
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get(self.HEADER_NAME)
        if not request_id:
            request_id = str(uuid.uuid4())
        
        set_request_id(request_id)
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers[self.HEADER_NAME] = request_id
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests with timing information."""
    
    EXCLUDED_PATHS = {"/health", "/metrics", "/ready", "/favicon.ico"}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)
        
        method = request.method
        path = request.url.path
        query = str(request.query_params) if request.query_params else None
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # 修正：第一個參數就是 event
        logger.info(
            "request_start",
            method=method,
            path=path,
            query=query,
            client_ip=client_ip,
            user_agent=user_agent[:100] if user_agent else None
        )
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000
            
            logger.info(
                "request_end",
                method=method,
                path=path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2)
            )
            
            return response
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            logger.error(
                "request_error",
                method=method,
                path=path,
                duration_ms=round(duration_ms, 2),
                error_type=type(e).__name__,
                error_message=str(e)
            )
            raise


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to catch and log unhandled exceptions."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            logger.exception(
                "unhandled_exception",
                method=request.method,
                path=request.url.path,
                error_type=type(e).__name__,
                error_message=str(e)
            )
            raise


def setup_logging_middleware(app: FastAPI) -> None:
    """Set up all logging-related middleware."""
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(ErrorLoggingMiddleware)
    app.add_middleware(RequestIdMiddleware)