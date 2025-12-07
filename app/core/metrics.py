"""
Prometheus Metrics Collection
Comprehensive metrics for monitoring application performance
"""
import time
from typing import Optional, Callable
from functools import wraps
from contextlib import contextmanager

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Summary,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
    multiprocess,
    REGISTRY
)
from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware

# Use default registry
registry = REGISTRY

# ==================== HTTP Metrics ====================

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
    registry=registry
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=registry
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests in progress",
    ["method", "endpoint"],
    registry=registry
)

# ==================== LLM Metrics ====================

llm_calls_total = Counter(
    "llm_calls_total",
    "Total LLM API calls",
    ["provider", "operation", "status"],
    registry=registry
)

llm_call_duration_seconds = Histogram(
    "llm_call_duration_seconds",
    "LLM API call duration in seconds",
    ["provider", "operation"],
    buckets=(0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0),
    registry=registry
)

llm_tokens_total = Counter(
    "llm_tokens_total",
    "Total tokens processed by LLM",
    ["provider", "token_type"],  # token_type: input, output
    registry=registry
)

# ==================== Embedding Metrics ====================

embedding_calls_total = Counter(
    "embedding_calls_total",
    "Total embedding API calls",
    ["provider", "status"],
    registry=registry
)

embedding_duration_seconds = Histogram(
    "embedding_duration_seconds",
    "Embedding generation duration in seconds",
    ["provider"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
    registry=registry
)

embedding_batch_size = Summary(
    "embedding_batch_size",
    "Size of embedding batches",
    ["provider"],
    registry=registry
)

# ==================== Vector Store Metrics ====================

vectorstore_operations_total = Counter(
    "vectorstore_operations_total",
    "Total vector store operations",
    ["store", "operation", "status"],  # operation: add, search, delete
    registry=registry
)

vectorstore_search_duration_seconds = Histogram(
    "vectorstore_search_duration_seconds",
    "Vector store search duration in seconds",
    ["store"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
    registry=registry
)

vectorstore_documents_total = Gauge(
    "vectorstore_documents_total",
    "Total documents in vector store",
    ["store", "collection"],
    registry=registry
)

# ==================== RAG Metrics ====================

rag_queries_total = Counter(
    "rag_queries_total",
    "Total RAG queries",
    ["status"],
    registry=registry
)

rag_query_duration_seconds = Histogram(
    "rag_query_duration_seconds",
    "RAG query duration in seconds",
    [],
    buckets=(0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
    registry=registry
)

rag_retrieval_duration_seconds = Histogram(
    "rag_retrieval_duration_seconds",
    "RAG document retrieval duration in seconds",
    [],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0),
    registry=registry
)

rag_chunks_retrieved = Summary(
    "rag_chunks_retrieved",
    "Number of chunks retrieved per RAG query",
    registry=registry
)

# ==================== Document Processing Metrics ====================

documents_processed_total = Counter(
    "documents_processed_total",
    "Total documents processed",
    ["document_type", "status"],  # document_type: pdf, docx, md
    registry=registry
)

document_processing_duration_seconds = Histogram(
    "document_processing_duration_seconds",
    "Document processing duration in seconds",
    ["document_type"],
    buckets=(0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0),
    registry=registry
)

document_chunks_created = Summary(
    "document_chunks_created",
    "Number of chunks created per document",
    ["document_type"],
    registry=registry
)

# ==================== Pipeline Metrics ====================

pipeline_runs_total = Counter(
    "pipeline_runs_total",
    "Total pipeline runs",
    ["template", "status"],
    registry=registry
)

pipeline_duration_seconds = Histogram(
    "pipeline_duration_seconds",
    "Pipeline execution duration in seconds",
    ["template"],
    buckets=(5.0, 10.0, 30.0, 60.0, 120.0, 300.0),
    registry=registry
)


# ==================== Context Managers for Tracking ====================

@contextmanager
def track_llm_call(provider: str, operation: str):
    """
    Context manager for tracking LLM calls.
    
    Usage:
        with track_llm_call("claude", "generate_report") as tracker:
            result = await llm.generate_report(...)
            tracker.set_tokens(input=100, output=500)
    """
    class Tracker:
        def __init__(self):
            self.input_tokens = 0
            self.output_tokens = 0
        
        def set_tokens(self, input: int = 0, output: int = 0):
            self.input_tokens = input
            self.output_tokens = output
    
    tracker = Tracker()
    start_time = time.time()
    status = "success"
    
    try:
        yield tracker
    except Exception:
        status = "error"
        raise
    finally:
        duration = time.time() - start_time
        
        llm_calls_total.labels(provider=provider, operation=operation, status=status).inc()
        llm_call_duration_seconds.labels(provider=provider, operation=operation).observe(duration)
        
        if tracker.input_tokens:
            llm_tokens_total.labels(provider=provider, token_type="input").inc(tracker.input_tokens)
        if tracker.output_tokens:
            llm_tokens_total.labels(provider=provider, token_type="output").inc(tracker.output_tokens)


@contextmanager
def track_embedding_call(provider: str, batch_size: int = 1):
    """Context manager for tracking embedding calls."""
    start_time = time.time()
    status = "success"
    
    try:
        yield
    except Exception:
        status = "error"
        raise
    finally:
        duration = time.time() - start_time
        
        embedding_calls_total.labels(provider=provider, status=status).inc()
        embedding_duration_seconds.labels(provider=provider).observe(duration)
        embedding_batch_size.labels(provider=provider).observe(batch_size)


@contextmanager
def track_vectorstore_operation(store: str, operation: str):
    """Context manager for tracking vector store operations."""
    start_time = time.time()
    status = "success"
    
    try:
        yield
    except Exception:
        status = "error"
        raise
    finally:
        duration = time.time() - start_time
        
        vectorstore_operations_total.labels(store=store, operation=operation, status=status).inc()
        
        if operation == "search":
            vectorstore_search_duration_seconds.labels(store=store).observe(duration)


# ==================== Middleware ====================

class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically track HTTP request metrics."""
    
    # Endpoints to exclude from metrics (reduce noise)
    EXCLUDED_PATHS = {"/health", "/metrics", "/ready"}
    
    async def dispatch(self, request: Request, call_next):
        # Skip excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)
        
        method = request.method
        # Normalize path (replace IDs with placeholders)
        path = self._normalize_path(request.url.path)
        
        # Track in-progress requests
        http_requests_in_progress.labels(method=method, endpoint=path).inc()
        
        start_time = time.time()
        status_code = 500  # Default for errors
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration = time.time() - start_time
            
            # Update metrics
            http_requests_total.labels(
                method=method,
                endpoint=path,
                status_code=status_code
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=path
            ).observe(duration)
            
            http_requests_in_progress.labels(method=method, endpoint=path).dec()
    
    def _normalize_path(self, path: str) -> str:
        """
        Normalize path by replacing dynamic segments.
        /documents/abc123 -> /documents/{id}
        /rag/collections/default/stats -> /rag/collections/{name}/stats
        """
        parts = path.split("/")
        normalized = []
        
        for i, part in enumerate(parts):
            if not part:
                normalized.append(part)
                continue
            
            # Check if it looks like an ID (UUID, hash, etc.)
            if self._looks_like_id(part):
                # Use context-aware placeholder
                if i > 0 and parts[i-1] == "collections":
                    normalized.append("{name}")
                elif i > 0 and parts[i-1] == "documents":
                    normalized.append("{id}")
                else:
                    normalized.append("{id}")
            else:
                normalized.append(part)
        
        return "/".join(normalized)
    
    def _looks_like_id(self, part: str) -> bool:
        """Check if a path segment looks like a dynamic ID."""
        # UUID pattern
        if len(part) == 36 and part.count("-") == 4:
            return True
        # Hash-like (32+ hex chars)
        if len(part) >= 32 and all(c in "0123456789abcdef" for c in part.lower()):
            return True
        # Document ID pattern (doc_timestamp_name_hash)
        if part.startswith("doc_") and len(part) > 20:
            return True
        return False


# ==================== FastAPI Integration ====================

def setup_metrics(app: FastAPI, path: str = "/metrics") -> None:
    """
    Set up Prometheus metrics endpoint and middleware.
    
    Args:
        app: FastAPI application instance
        path: Path for metrics endpoint (default: /metrics)
    """
    # Add middleware
    app.add_middleware(PrometheusMiddleware)
    
    # Add metrics endpoint
    @app.get(path, include_in_schema=False)
    async def metrics():
        return Response(
            content=generate_latest(registry),
            media_type=CONTENT_TYPE_LATEST
        )


def get_metrics_summary() -> dict:
    """Get a summary of current metrics for health checks."""
    return {
        "http_requests": {
            "description": "Total HTTP requests processed"
        },
        "llm_calls": {
            "description": "Total LLM API calls made"
        },
        "rag_queries": {
            "description": "Total RAG queries processed"
        },
        "documents_processed": {
            "description": "Total documents processed"
        }
    }