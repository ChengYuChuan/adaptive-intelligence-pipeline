from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime


class PipelineRequest(BaseModel):
    """Pipeline 執行請求"""
    
    query: str = Field(..., description="搜尋關鍵字")
    template: Literal["academic", "financial"] = Field(..., description="報告模板類型")
    max_results: int = Field(10, ge=1, le=50, description="最多獲取幾筆資料")
    date_range: Optional[str] = Field(None, description="日期範圍: 'today', 'yesterday', 'last_week', 'last_month'")
    output_title: Optional[str] = Field(None, description="輸出的標題")
    output_tags: Optional[List[str]] = Field(default_factory=list, description="輸出的標籤")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "machine learning OR transformers",
                "template": "academic",
                "max_results": 10,
                "date_range": "last_week",
                "output_title": "本週 ML 論文摘要",
                "output_tags": ["ML", "research"]
            }
        }


class PipelineResponse(BaseModel):
    """Pipeline 執行結果"""
    
    status: Literal["success", "partial", "failed"]
    message: str
    
    # 各階段的結果
    data_fetched: int = Field(..., description="獲取的資料筆數")
    report: Optional[str] = Field(None, description="生成的報告")
    output_url: Optional[str] = Field(None, description="輸出位置的 URL")
    
    # 使用的服務
    providers: Dict[str, str] = Field(..., description="使用的 provider")
    
    # 時間戳記
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Pipeline 執行成功",
                "data_fetched": 10,
                "report": "# 本週 ML 論文摘要\n\n...",
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
    """健康檢查回應"""
    
    status: str
    providers: Dict[str, str]
    timestamp: datetime
