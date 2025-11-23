from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Author(BaseModel):
    """Author information"""
    name: str
    affiliation: Optional[str] = None


class Paper(BaseModel):
    """Academic paper data model"""
    
    id: str = Field(..., description="Unique identifier (e.g., arXiv ID)")
    title: str = Field(..., description="Paper title")
    authors: List[str] = Field(..., description="List of author names")
    abstract: str = Field(..., description="Paper abstract/summary")
    published_date: datetime = Field(..., description="Publication date")
    updated_date: Optional[datetime] = Field(None, description="Last update date")
    
    # arXiv specific fields
    categories: List[str] = Field(default_factory=list, description="arXiv categories (e.g., cs.LG)")
    primary_category: Optional[str] = Field(None, description="Primary category")
    
    # URLs
    pdf_url: Optional[str] = Field(None, description="PDF download URL")
    abs_url: str = Field(..., description="Abstract page URL")
    
    # Optional metadata
    comment: Optional[str] = Field(None, description="Author comments")
    journal_ref: Optional[str] = Field(None, description="Journal reference")
    doi: Optional[str] = Field(None, description="DOI")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "2301.12345",
                "title": "Attention is All You Need",
                "authors": ["Ashish Vaswani", "Noam Shazeer"],
                "abstract": "The dominant sequence transduction models...",
                "published_date": "2023-01-15T00:00:00",
                "categories": ["cs.LG", "cs.CL"],
                "primary_category": "cs.LG",
                "pdf_url": "https://arxiv.org/pdf/2301.12345",
                "abs_url": "https://arxiv.org/abs/2301.12345"
            }
        }


class PaperCollection(BaseModel):
    """Collection of papers with metadata"""
    
    papers: List[Paper]
    total_count: int
    query: str
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "papers": [],
                "total_count": 10,
                "query": "transformer",
                "date_from": "2023-01-01T00:00:00",
                "date_to": "2023-01-31T23:59:59"
            }
        }