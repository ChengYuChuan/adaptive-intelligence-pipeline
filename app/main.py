from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging

from app.config import settings
from app.schemas.pipeline import PipelineRequest, PipelineResponse, HealthResponse
from app.services.pipeline import PipelineService
from app.adapters.llm import get_llm_adapter
from app.adapters.source import get_source_adapter
from app.adapters.output import get_output_adapter

# 設定 logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 建立 FastAPI app
app = FastAPI(
    title="Adaptive Intelligence Pipeline",
    description="""
    一個可抽換元件的 AI 資訊整合系統
    
    ## 特色
    - 🔌 LLM 服務可抽換（Claude API / AWS Bedrock / Azure OpenAI / SageMaker）
    - 📊 資料來源可抽換（arXiv / NewsAPI / 內部資料庫）
    - 📤 輸出格式可抽換（Console / Notion / Email / Slack）
    - 🎯 支援多種場景（學術追蹤 / 投資分析）
    
    ## 快速開始
    1. 設定 `.env` 檔案
    2. 呼叫 `/pipeline/run` 端點
    3. 查看生成的報告
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 設定（如果需要前端呼叫）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境應該限制特定 domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """根路徑 - API 資訊"""
    return {
        "name": "Adaptive Intelligence Pipeline",
        "version": "1.0.0",
        "description": "可抽換元件的 AI 資訊整合系統",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    健康檢查 - 顯示目前使用的 providers
    """
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


@app.post("/pipeline/run", response_model=PipelineResponse, tags=["Pipeline"])
async def run_pipeline(request: PipelineRequest):
    """
    執行完整的資料處理 pipeline
    
    ## 流程
    1. 從資料來源獲取資料（根據 SOURCE_PROVIDER）
    2. 使用 LLM 分析和生成報告（根據 LLM_PROVIDER）
    3. 輸出到目標位置（根據 OUTPUT_PROVIDER）
    
    ## 範例
    
    ### 學術論文追蹤
    ```json
    {
      "query": "machine learning OR transformers",
      "template": "academic",
      "max_results": 10,
      "date_range": "last_week",
      "output_title": "本週 ML 論文摘要"
    }
    ```
    
    ### 投資新聞分析
    ```json
    {
      "query": "TSMC OR NVIDIA",
      "template": "financial",
      "max_results": 20,
      "date_range": "today",
      "output_title": "今日半導體產業動態"
    }
    ```
    """
    
    logger.info(f"Pipeline started - Query: {request.query}, Template: {request.template}")
    
    try:
        service = PipelineService()
        result = await service.run(request)
        
        logger.info(f"Pipeline completed - Status: {result.status}, Duration: {result.duration_seconds}s")
        
        return result
    
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")


@app.get("/config", tags=["System"])
async def get_config():
    """
    顯示目前的設定（不包含敏感資訊）
    """
    return {
        "llm_provider": settings.LLM_PROVIDER,
        "source_provider": settings.SOURCE_PROVIDER,
        "output_provider": settings.OUTPUT_PROVIDER,
        "debug_mode": settings.DEBUG
    }


# 啟動事件
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("Adaptive Intelligence Pipeline 啟動中...")
    logger.info(f"LLM Provider: {settings.LLM_PROVIDER}")
    logger.info(f"Source Provider: {settings.SOURCE_PROVIDER}")
    logger.info(f"Output Provider: {settings.OUTPUT_PROVIDER}")
    logger.info("=" * 60)


# 關閉事件
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Adaptive Intelligence Pipeline 關閉中...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
