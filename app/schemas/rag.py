"""
RAG (Retrieval-Augmented Generation) schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class SourceReference(BaseModel):
    """Reference to a source document used in the answer"""
    document_id: str = Field(..., description="Source document ID")
    filename: str = Field(..., description="Original filename")
    chunk_id: str = Field(..., description="Specific chunk ID")
    content_preview: str = Field(..., description="Preview of the relevant content")
    relevance_score: float = Field(..., description="Relevance score (0-1)")
    page_number: Optional[int] = Field(None, description="Page number if available")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc123",
                "filename": "employee_handbook.pdf",
                "chunk_id": "doc123_chunk_5",
                "content_preview": "Employees are entitled to 20 days of paid leave...",
                "relevance_score": 0.92,
                "page_number": 15
            }
        }


class AskRequest(BaseModel):
    """Request schema for asking a question"""
    question: str = Field(..., min_length=3, description="The question to ask")
    collection_name: str = Field("default", description="Collection to search in")
    top_k: int = Field(5, ge=1, le=20, description="Number of sources to retrieve")
    include_sources: bool = Field(True, description="Whether to include source references")
    
    # Optional filters
    filter_tags: Optional[List[str]] = Field(None, description="Filter by document tags")
    filter_source: Optional[str] = Field(None, description="Filter by document source")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the company's remote work policy?",
                "collection_name": "default",
                "top_k": 5,
                "include_sources": True,
                "filter_tags": ["policy", "hr"]
            }
        }


class AskResponse(BaseModel):
    """Response schema for question answering"""
    question: str = Field(..., description="Original question")
    answer: str = Field(..., description="Generated answer")
    sources: List[SourceReference] = Field(default_factory=list, description="Source references")
    
    # Metadata
    confidence: Optional[float] = Field(None, description="Confidence score if available")
    model_used: str = Field(..., description="LLM model used for generation")
    retrieval_time_ms: float = Field(..., description="Time to retrieve documents")
    generation_time_ms: float = Field(..., description="Time to generate answer")
    total_time_ms: float = Field(..., description="Total processing time")
    
    # Debug info
    chunks_retrieved: int = Field(..., description="Number of chunks retrieved")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the company's remote work policy?",
                "answer": "According to the Employee Handbook, employees may work remotely up to 2 days per week with manager approval...",
                "sources": [],
                "model_used": "claude-sonnet-4-20250514",
                "retrieval_time_ms": 150.5,
                "generation_time_ms": 2500.0,
                "total_time_ms": 2650.5,
                "chunks_retrieved": 5
            }
        }


class CollectionStats(BaseModel):
    """Statistics about a document collection"""
    collection_name: str
    document_count: int = Field(..., description="Number of documents")
    chunk_count: int = Field(..., description="Number of chunks")
    total_size_bytes: Optional[int] = Field(None, description="Total storage size")
    last_updated: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "collection_name": "default",
                "document_count": 25,
                "chunk_count": 450,
                "total_size_bytes": 5242880
            }
        }


class RAGHealthResponse(BaseModel):
    """Health check response for RAG system"""
    status: str = Field(..., description="System status")
    vectorstore: Dict[str, Any] = Field(..., description="Vector store status")
    embedding: Dict[str, Any] = Field(..., description="Embedding service status")
    collections: List[str] = Field(default_factory=list, description="Available collections")