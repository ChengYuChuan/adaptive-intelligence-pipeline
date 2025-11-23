from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ReportType(str, Enum):
    """Report type enumeration"""
    ACADEMIC = "academic"
    FINANCIAL = "financial"
    GENERAL = "general"


class ReportSection(BaseModel):
    """A section within a report"""
    title: str
    content: str
    order: int = Field(..., description="Section order in report")


class KeyInsight(BaseModel):
    """Key insight or finding"""
    insight: str
    importance: str = Field(..., description="high/medium/low")
    related_items: List[str] = Field(default_factory=list, description="Related paper/news IDs")


class AcademicReport(BaseModel):
    """Academic literature review report"""
    
    report_id: str
    title: str
    generated_at: datetime
    
    # Query information
    query: str
    date_range: str
    total_papers: int
    
    # Report content
    executive_summary: str = Field(..., description="High-level summary")
    sections: List[ReportSection] = Field(default_factory=list)
    key_insights: List[KeyInsight] = Field(default_factory=list)
    
    # Categorized papers
    trending_topics: List[str] = Field(default_factory=list)
    recommended_papers: List[str] = Field(default_factory=list, description="Paper IDs")
    
    # Metadata
    llm_provider: str
    generation_time_seconds: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "report_20240115_001",
                "title": "Weekly Machine Learning Research Summary",
                "generated_at": "2024-01-15T12:00:00",
                "query": "machine learning",
                "date_range": "last_week",
                "total_papers": 15,
                "executive_summary": "This week saw significant advances in...",
                "trending_topics": ["transformers", "reinforcement learning"],
                "llm_provider": "ClaudeAPI",
                "generation_time_seconds": 12.5
            }
        }


class FinancialReport(BaseModel):
    """Financial/Investment analysis report"""
    
    report_id: str
    title: str
    generated_at: datetime
    
    # Query information
    query: str
    date_range: str
    total_articles: int
    
    # Report content
    market_summary: str = Field(..., description="Overall market situation")
    sections: List[ReportSection] = Field(default_factory=list)
    key_insights: List[KeyInsight] = Field(default_factory=list)
    
    # Sentiment analysis
    overall_sentiment: str = Field(..., description="bullish/bearish/neutral")
    sentiment_confidence: float = Field(..., ge=0.0, le=1.0)
    
    # Key companies/topics mentioned
    key_entities: Dict[str, int] = Field(default_factory=dict, description="Entity: mention count")
    risk_factors: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    
    # Metadata
    llm_provider: str
    generation_time_seconds: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "report_20240115_002",
                "title": "Daily Semiconductor Industry Analysis",
                "generated_at": "2024-01-15T12:00:00",
                "query": "TSMC NVIDIA",
                "date_range": "today",
                "total_articles": 25,
                "market_summary": "Semiconductor stocks rallied today...",
                "overall_sentiment": "bullish",
                "sentiment_confidence": 0.75,
                "key_entities": {"TSMC": 15, "NVIDIA": 12, "ASML": 8},
                "llm_provider": "ClaudeAPI",
                "generation_time_seconds": 15.3
            }
        }


class ReportMetadata(BaseModel):
    """Metadata about report generation"""
    
    report_type: ReportType
    data_sources: List[str]
    llm_provider: str
    output_destination: str
    
    generation_started: datetime
    generation_completed: datetime
    total_duration_seconds: float
    
    success: bool
    error_message: Optional[str] = None


class GeneratedReport(BaseModel):
    """Complete generated report with all metadata"""
    
    metadata: ReportMetadata
    report: Dict[str, Any] = Field(..., description="Actual report data (AcademicReport or FinancialReport)")
    raw_content: str = Field(..., description="Raw text content of report")
    output_url: Optional[str] = Field(None, description="URL where report was published")