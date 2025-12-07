"""
Document schemas for RAG system
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Supported document types"""
    PDF = "pdf"
    WORD = "docx"
    MARKDOWN = "md"
    TEXT = "txt"


class DocumentChunk(BaseModel):
    """A chunk of a document after splitting"""
    chunk_id: str = Field(..., description="Unique chunk identifier")
    document_id: str = Field(..., description="Parent document ID")
    content: str = Field(..., description="Chunk text content")
    chunk_index: int = Field(..., description="Position in original document")
    
    # Metadata
    page_number: Optional[int] = Field(None, description="Page number (for PDF)")
    section_title: Optional[str] = Field(None, description="Section heading if available")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chunk_id": "doc123_chunk_0",
                "document_id": "doc123",
                "content": "This is the content of the first chunk...",
                "chunk_index": 0,
                "page_number": 1,
                "section_title": "Introduction"
            }
        }


class DocumentMetadata(BaseModel):
    """Metadata about an uploaded document"""
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    document_type: DocumentType = Field(..., description="Document type")
    file_size: int = Field(..., description="File size in bytes")
    
    # Processing info
    total_chunks: int = Field(0, description="Number of chunks created")
    total_pages: Optional[int] = Field(None, description="Number of pages (PDF)")
    total_characters: int = Field(0, description="Total character count")
    
    # Timestamps
    uploaded_at: datetime = Field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    
    # Custom metadata (user-provided)
    tags: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    source: Optional[str] = Field(None, description="Source of the document")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_20240115_abc123",
                "filename": "company_policy.pdf",
                "document_type": "pdf",
                "file_size": 1024000,
                "total_chunks": 25,
                "total_pages": 10,
                "tags": ["policy", "hr"],
                "source": "HR Department"
            }
        }


class DocumentUploadRequest(BaseModel):
    """Request schema for document upload"""
    tags: List[str] = Field(default_factory=list, description="Tags for the document")
    description: Optional[str] = Field(None, description="Document description")
    source: Optional[str] = Field(None, description="Document source")
    collection_name: str = Field("default", description="Collection to store in")


class DocumentUploadResponse(BaseModel):
    """Response after document upload and processing"""
    status: str = Field(..., description="Upload status")
    message: str = Field(..., description="Status message")
    document: Optional[DocumentMetadata] = None
    chunks_created: int = Field(0, description="Number of chunks created")
    processing_time_seconds: float = Field(0, description="Processing duration")


class DocumentListResponse(BaseModel):
    """Response for listing documents"""
    documents: List[DocumentMetadata]
    total_count: int
    collection_name: str