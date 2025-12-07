"""
Adaptive Intelligence Pipeline - Main Application
Week 4: Production-ready with structured logging and metrics
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Optional

from app.config import settings
from app.schemas.pipeline import PipelineRequest, PipelineResponse, HealthResponse
from app.schemas.document import DocumentUploadResponse
from app.schemas.rag import (
    AskRequest,
    AskResponse,
    CollectionStats,
    RAGHealthResponse
)
from app.services.pipeline import PipelineService
from app.services.document_processor import DocumentProcessor
from app.services.rag import RAGService
from app.adapters.llm import get_llm_adapter
from app.adapters.source import get_source_adapter
from app.adapters.output import get_output_adapter

# Week 4 imports
from app.core.logging import configure_logging, get_logger, get_request_id
from app.core.metrics import setup_metrics
from app.core.middleware import setup_logging_middleware

# Configure logging first
configure_logging(
    log_level=settings.LOG_LEVEL,
    log_format=settings.LOG_FORMAT,
    service_name="aip"
)

logger = get_logger(__name__)

# Global instances
document_processor: Optional[DocumentProcessor] = None
rag_service: Optional[RAGService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown."""
    # Startup - 移除 event= 參數，第一個字串就是 event
    logger.info(
        "startup",  # This IS the event
        version="0.4.0",
        environment=settings.APP_ENVIRONMENT,
        llm_provider=settings.LLM_PROVIDER,
        source_provider=settings.SOURCE_PROVIDER,
        output_provider=settings.OUTPUT_PROVIDER,
        vectorstore_provider=settings.VECTORSTORE_PROVIDER,
        embedding_provider=settings.EMBEDDING_PROVIDER
    )
    
    yield
    
    # Shutdown
    logger.info("shutdown")
    
    # Clean up resources
    global document_processor, rag_service
    if rag_service and hasattr(rag_service, 'vectorstore'):
        if hasattr(rag_service.vectorstore, 'close'):
            await rag_service.vectorstore.close()


# Create FastAPI app
app = FastAPI(
    title="Adaptive Intelligence Pipeline",
    description="""
    A switchable-component AI information integration system with RAG capabilities.
    
    ## Week 4 Features
    - 📊 Structured JSON logging with request tracking
    - 📈 Prometheus metrics at /metrics
    - 🐘 PostgreSQL + pgvector support
    - 🔐 Production-ready error handling
    """,
    version="0.4.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Setup middleware (order matters)
setup_logging_middleware(app)

# Setup metrics
if settings.METRICS_ENABLED:
    setup_metrics(app, path=settings.METRICS_PATH)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    request_id = get_request_id()
    
    logger.error(
        "unhandled_error",
        error_type=type(exc).__name__,
        error_message=str(exc),
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": request_id
        }
    )


# ==================== Root & Health ====================

@app.get("/", tags=["System"])
async def root():
    """Root path - API information"""
    return {
        "name": "Adaptive Intelligence Pipeline",
        "version": "0.4.0",
        "description": "Switchable-component AI system with RAG",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics" if settings.METRICS_ENABLED else None
    }


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check - shows currently used providers"""
    try:
        llm = get_llm_adapter()
        source = get_source_adapter()
        output = get_output_adapter()
        
        return HealthResponse(
            status="healthy",
            providers={
                "llm": llm.get_provider_name(),
                "source": source.get_source_name(),
                "output": output.get_output_name(),
                "vectorstore": settings.VECTORSTORE_PROVIDER,
                "embedding": settings.EMBEDDING_PROVIDER
            },
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.get("/ready", tags=["System"])
async def readiness_check():
    """Kubernetes readiness probe."""
    checks = {"api": True}
    
    global rag_service
    if rag_service:
        try:
            health = await rag_service.health_check()
            checks["vectorstore"] = health.status == "healthy"
        except Exception:
            checks["vectorstore"] = False
    
    all_ready = all(checks.values())
    
    if not all_ready:
        raise HTTPException(status_code=503, detail={"checks": checks})
    
    return {"status": "ready", "checks": checks}


@app.get("/config", tags=["System"])
async def get_config():
    """Show current configuration (excluding sensitive information)"""
    return {
        "environment": settings.APP_ENVIRONMENT,
        "llm_provider": settings.LLM_PROVIDER,
        "source_provider": settings.SOURCE_PROVIDER,
        "output_provider": settings.OUTPUT_PROVIDER,
        "vectorstore_provider": settings.VECTORSTORE_PROVIDER,
        "embedding_provider": settings.EMBEDDING_PROVIDER,
        "log_level": settings.LOG_LEVEL,
        "log_format": settings.LOG_FORMAT,
        "metrics_enabled": settings.METRICS_ENABLED,
        "debug_mode": settings.DEBUG
    }


# ==================== Pipeline Endpoints ====================

@app.post("/pipeline/run", response_model=PipelineResponse, tags=["Pipeline"])
async def run_pipeline(request: PipelineRequest):
    """Execute complete data processing pipeline"""
    logger.info(
        "pipeline_start",
        query=request.query,
        template=request.template,
        max_results=request.max_results
    )
    
    try:
        service = PipelineService()
        result = await service.run(request)
        
        logger.info(
            "pipeline_end",
            status=result.status,
            data_fetched=result.data_fetched,
            duration_seconds=result.duration_seconds
        )
        
        return result
        
    except Exception as e:
        logger.error("pipeline_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")


# ==================== RAG Endpoints ====================

@app.post("/documents/upload", response_model=DocumentUploadResponse, tags=["RAG"])
async def upload_document(
    file: UploadFile = File(...),
    tags: str = Form(default=""),
    description: str = Form(default=""),
    source: str = Form(default=""),
    collection_name: str = Form(default="default")
):
    """Upload a document for RAG processing."""
    global document_processor
    
    logger.info(
        "document_upload_start",
        filename=file.filename,
        collection=collection_name
    )
    
    if document_processor is None:
        document_processor = DocumentProcessor()
        await document_processor.initialize()
    
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    
    result = await document_processor.process_document(
        file=file.file,
        filename=file.filename,
        metadata={
            "tags": tag_list,
            "description": description,
            "source": source
        },
        collection_name=collection_name
    )
    
    if result.status == "failed":
        logger.warning(
            "document_upload_failed",
            filename=file.filename,
            reason=result.message
        )
        raise HTTPException(status_code=400, detail=result.message)
    
    logger.info(
        "document_upload_end",
        filename=file.filename,
        chunks_created=result.chunks_created,
        processing_time=result.processing_time_seconds
    )
    
    return result


@app.post("/ask", response_model=AskResponse, tags=["RAG"])
async def ask_question(request: AskRequest):
    """Ask a question about uploaded documents."""
    global rag_service
    
    logger.info(
        "rag_query_start",
        question_length=len(request.question),
        collection=request.collection_name,
        top_k=request.top_k
    )
    
    if rag_service is None:
        rag_service = RAGService()
        await rag_service.initialize()
    
    try:
        result = await rag_service.ask(request)
        
        logger.info(
            "rag_query_end",
            chunks_retrieved=result.chunks_retrieved,
            retrieval_time_ms=result.retrieval_time_ms,
            generation_time_ms=result.generation_time_ms
        )
        
        return result
        
    except Exception as e:
        logger.error("rag_query_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.get("/rag/health", response_model=RAGHealthResponse, tags=["RAG"])
async def rag_health():
    """Check health of RAG system components"""
    global rag_service
    
    if rag_service is None:
        rag_service = RAGService()
        await rag_service.initialize()
    
    return await rag_service.health_check()


@app.get("/rag/collections", tags=["RAG"])
async def list_collections():
    """List all document collections"""
    global rag_service
    
    if rag_service is None:
        rag_service = RAGService()
        await rag_service.initialize()
    
    collections = await rag_service.list_collections()
    return {"collections": collections}


@app.get("/rag/collections/{collection_name}/stats", response_model=CollectionStats, tags=["RAG"])
async def get_collection_stats(collection_name: str):
    """Get statistics about a document collection"""
    global rag_service
    
    if rag_service is None:
        rag_service = RAGService()
        await rag_service.initialize()
    
    return await rag_service.get_collection_stats(collection_name)


@app.delete("/rag/collections/{collection_name}", tags=["RAG"])
async def delete_collection(collection_name: str):
    """Delete a document collection"""
    global rag_service
    
    if rag_service is None:
        rag_service = RAGService()
        await rag_service.initialize()
    
    logger.info("collection_delete", collection=collection_name)
    
    success = await rag_service.vectorstore.delete_collection(collection_name)
    
    if success:
        return {"status": "success", "message": f"Collection '{collection_name}' deleted"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete collection")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )