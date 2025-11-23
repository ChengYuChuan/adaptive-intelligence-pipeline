from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime


class PipelineRequest(BaseModel):
    """Pipeline execution request"""
    
    query: str = Field(..., description="Search keywords")
    template: Literal["academic", "financial"] = Field(..., description="Report template type")
    max_results: int = Field(10, ge=1, le=50, description="Maximum number of results to fetch")
    date_range: Optional[str] = Field(None, description="Date range: 'today', 'yesterday', 'last_week', 'last_month'")
    output_title: Optional[str] = Field(None, description="Title for the output")
    output_tags: Optional[List[str]] = Field(default_factory=list, description="Tags for the output")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "machine learning OR transformers",
                "template": "academic",
                "max_results": 10,
                "date_range": "last_week",
                "output_title": "Weekly ML Paper Summary",
                "output_tags": ["ML", "research"]
            }
        }


class PipelineResponse(BaseModel):
    """Pipeline execution result"""
    
    status: Literal["success", "partial", "failed"]
    message: str
    
    # Results from each stage
    data_fetched: int = Field(..., description="Number of data items fetched")
    report: Optional[str] = Field(None, description="Generated report")
    output_url: Optional[str] = Field(None, description="URL of the output location")
    
    # Services used
    providers: Dict[str, str] = Field(..., description="Providers used")
    
    # Timestamps
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Pipeline executed successfully",
                "data_fetched": 10,
                "report": "# Weekly ML Paper Summary\n\n...",
                "output_url": "https://notion.so/...",
                "providers": {
                    "llm": "Claude API",
                    "source": "arXiv",
                    "output": "Notion"
                },
                "started_at": "2024-01-15T10:00:00",
                "completed_at": "2024-01-15T10:01:30",
                "duration_seconds": 90.5
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    
    status: str
    providers: Dict[str, str]
    timestamp: datetime