"""
Adaptive Intelligence Pipeline - Main Application
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List, Optional
import logging
import json

from app.config import settings
from app.schemas.pipeline import PipelineRequest, PipelineResponse, HealthResponse
from app.schemas.document import (
    DocumentUploadRequest,
    DocumentUploadResponse,
    DocumentListResponse
)
from app.schemas.rag import (
    AskRequest,
    AskResponse,
    CollectionStats,
    RAGHealthResponse
)
from app.services.pipeline import PipelineService
from app.services.document_processor import DocumentProcessor
from app.services.rag import RAGService, get_rag_service
from app.adapters.llm import get_llm_adapter
from app.adapters.source import get_source_adapter
from app.adapters.output import get_output_adapter

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Adaptive Intelligence Pipeline",
    description="""
    A switchable-component AI information integration system with RAG capabilities.
    
    ## Features
    - 🔌 Switchable LLM services (Claude API / AWS Bedrock / Azure OpenAI)
    - 📊 Switchable data sources (arXiv / NewsAPI / Internal documents)
    - 📤 Switchable output formats (Console / Notion / Email / Slack)
    - 🔍 RAG: Document upload and question answering with source citations
    
    ## New in Week 3
    - Upload documents (PDF, Word, Markdown)
    - Ask questions about your documents
    - Get answers with source references
    """,
    version="0.3.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
document_processor: Optional[DocumentProcessor] = None
rag_service: Optional[RAGService] = None


# ==================== Root & Health ====================

@app.get("/", tags=["Root"])
async def root():
    """Root path - API information"""
    return {
        "name": "Adaptive Intelligence Pipeline",
        "version": "0.3.0",
        "description": "Switchable-component AI system with RAG",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "pipeline": "/pipeline/run",
            "rag": {
                "upload": "/documents/upload",
                "ask": "/ask",
                "health": "/rag/health"
            }
        }
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
                "output": output.get_output_name()
            },
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.get("/config", tags=["System"])
async def get_config():
    """Show current configuration (excluding sensitive information)"""
    return {
        "llm_provider": settings.LLM_PROVIDER,
        "source_provider": settings.SOURCE_PROVIDER,
        "output_provider": settings.OUTPUT_PROVIDER,
        "vectorstore_provider": getattr(settings, 'VECTORSTORE_PROVIDER', 'chroma'),
        "embedding_provider": getattr(settings, 'EMBEDDING_PROVIDER', 'openai'),
        "debug_mode": settings.DEBUG
    }


# ==================== Pipeline Endpoints ====================

@app.post("/pipeline/run", response_model=PipelineResponse, tags=["Pipeline"])
async def run_pipeline(request: PipelineRequest):
    """Execute complete data processing pipeline"""
    logger.info(f"Pipeline started - Query: {request.query}, Template: {request.template}")
    
    try:
        service = PipelineService()
        result = await service.run(request)
        logger.info(f"Pipeline completed - Status: {result.status}")
        return result
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")


# ==================== RAG Endpoints ====================

@app.post("/documents/upload", response_model=DocumentUploadResponse, tags=["RAG"])
async def upload_document(
    file: UploadFile = File(..., description="Document file (PDF, Word, or Markdown)"),
    tags: str = Form(default="", description="Comma-separated tags"),
    description: str = Form(default="", description="Document description"),
    source: str = Form(default="", description="Document source"),
    collection_name: str = Form(default="default", description="Collection name")
):
    """
    Upload a document for RAG processing.
    
    Supported formats:
    - PDF (.pdf)
    - Word (.docx)
    - Markdown (.md)
    - Plain text (.txt)
    
    The document will be:
    1. Parsed to extract text
    2. Split into chunks
    3. Embedded using the configured embedding model
    4. Stored in the vector database
    """
    global document_processor
    
    # Initialize processor if needed
    if document_processor is None:
        document_processor = DocumentProcessor()
        await document_processor.initialize()
    
    # Parse tags
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    
    # Process document
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
        raise HTTPException(status_code=400, detail=result.message)
    
    return result


@app.post("/ask", response_model=AskResponse, tags=["RAG"])
async def ask_question(request: AskRequest):
    """
    Ask a question about uploaded documents.
    
    The system will:
    1. Find relevant document chunks using semantic search
    2. Use the LLM to generate an answer based on the found context
    3. Return the answer with source references
    
    Example:
```json
    {
        "question": "What is the company's vacation policy?",
        "collection_name": "default",
        "top_k": 5,
        "include_sources": true
    }
```
    """
    global rag_service
    
    # Initialize service if needed
    if rag_service is None:
        rag_service = RAGService()
        await rag_service.initialize()
    
    try:
        result = await rag_service.ask(request)
        return result
    except Exception as e:
        logger.error(f"RAG query failed: {e}", exc_info=True)
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
    
    success = await rag_service.vectorstore.delete_collection(collection_name)
    
    if success:
        return {"status": "success", "message": f"Collection '{collection_name}' deleted"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete collection")


# ==================== Events ====================

@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("Adaptive Intelligence Pipeline v0.3.0 starting...")
    logger.info(f"LLM Provider: {settings.LLM_PROVIDER}")
    logger.info(f"Source Provider: {settings.SOURCE_PROVIDER}")
    logger.info(f"Output Provider: {settings.OUTPUT_PROVIDER}")
    logger.info(f"VectorStore: {getattr(settings, 'VECTORSTORE_PROVIDER', 'chroma')}")
    logger.info(f"Embedding: {getattr(settings, 'EMBEDDING_PROVIDER', 'openai')}")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Adaptive Intelligence Pipeline shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )