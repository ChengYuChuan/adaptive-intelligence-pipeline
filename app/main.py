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
    A switchable-component AI information integration system
    
    ## Features
    - 🔌 Switchable LLM services (Claude API / AWS Bedrock / Azure OpenAI / SageMaker)
    - 📊 Switchable data sources (arXiv / NewsAPI / Internal database)
    - 📤 Switchable output formats (Console / Notion / Email / Slack)
    - 🎯 Multiple scenarios (Academic tracking / Investment analysis)
    
    ## Quick Start
    1. Configure `.env` file
    2. Call `/pipeline/run` endpoint
    3. View generated report
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS settings (if frontend needs to call)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Should restrict to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Root path - API information"""
    return {
        "name": "Adaptive Intelligence Pipeline",
        "version": "1.0.0",
        "description": "Switchable-component AI information integration system",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Health check - shows currently used providers
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
    Execute complete data processing pipeline
    
    ## Process
    1. Fetch data from source (based on SOURCE_PROVIDER)
    2. Analyze and generate report with LLM (based on LLM_PROVIDER)
    3. Output to destination (based on OUTPUT_PROVIDER)
    
    ## Examples
    
    ### Academic Paper Tracking
    ```json
    {
      "query": "machine learning OR transformers",
      "template": "academic",
      "max_results": 10,
      "date_range": "last_week",
      "output_title": "Weekly ML Paper Summary"
    }
    ```
    
    ### Investment News Analysis
    ```json
    {
      "query": "TSMC OR NVIDIA",
      "template": "financial",
      "max_results": 20,
      "date_range": "today",
      "output_title": "Today's Semiconductor Industry Updates"
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
    Show current configuration (excluding sensitive information)
    """
    return {
        "llm_provider": settings.LLM_PROVIDER,
        "source_provider": settings.SOURCE_PROVIDER,
        "output_provider": settings.OUTPUT_PROVIDER,
        "debug_mode": settings.DEBUG
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("Adaptive Intelligence Pipeline starting...")
    logger.info(f"LLM Provider: {settings.LLM_PROVIDER}")
    logger.info(f"Source Provider: {settings.SOURCE_PROVIDER}")
    logger.info(f"Output Provider: {settings.OUTPUT_PROVIDER}")
    logger.info("=" * 60)


# Shutdown event
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