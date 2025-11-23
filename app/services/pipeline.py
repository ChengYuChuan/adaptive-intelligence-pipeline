import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from app.schemas.pipeline import PipelineRequest, PipelineResponse
from app.adapters.llm import get_llm_adapter
from app.adapters.source import get_source_adapter
from app.adapters.output import get_output_adapter

logger = logging.getLogger(__name__)


class PipelineService:
    """
    Orchestrates the complete pipeline:
    1. Fetch data from source
    2. Analyze with LLM
    3. Output to destination
    """
    
    def __init__(self):
        self.llm = get_llm_adapter()
        self.source = get_source_adapter()
        self.output = get_output_adapter()
    
    def _parse_date_range(self, date_range: str = None) -> tuple:
        """
        Parse date range string to datetime objects
        
        Args:
            date_range: One of "today", "yesterday", "last_week", "last_month"
            
        Returns:
            Tuple of (date_from, date_to)
        """
        now = datetime.now()
        
        if date_range == "today":
            date_from = now.replace(hour=0, minute=0, second=0, microsecond=0)
            date_to = now
        
        elif date_range == "yesterday":
            yesterday = now - timedelta(days=1)
            date_from = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            date_to = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        elif date_range == "last_week":
            date_from = now - timedelta(days=7)
            date_to = now
        
        elif date_range == "last_month":
            date_from = now - timedelta(days=30)
            date_to = now
        
        else:
            # Default to last week
            date_from = now - timedelta(days=7)
            date_to = now
        
        return date_from, date_to
    
    async def run(self, request: PipelineRequest) -> PipelineResponse:
        """
        Execute the complete pipeline
        
        Args:
            request: Pipeline request parameters
            
        Returns:
            Pipeline execution result
        """
        started_at = datetime.now()
        
        try:
            # Stage 1: Fetch data from source
            logger.info(f"Stage 1: Fetching data from {self.source.get_source_name()}")
            date_from, date_to = self._parse_date_range(request.date_range)
            
            raw_data = await self.source.fetch(
                query=request.query,
                max_results=request.max_results,
                date_from=date_from,
                date_to=date_to
            )
            
            if not raw_data:
                logger.warning("No data fetched from source")
                return PipelineResponse(
                    status="failed",
                    message="No data found for the given query and date range",
                    data_fetched=0,
                    report=None,
                    output_url=None,
                    providers={
                        "llm": self.llm.get_provider_name(),
                        "source": self.source.get_source_name(),
                        "output": self.output.get_output_name()
                    },
                    started_at=started_at,
                    completed_at=datetime.now(),
                    duration_seconds=(datetime.now() - started_at).total_seconds()
                )
            
            logger.info(f"Fetched {len(raw_data)} items")
            
            # Stage 2: Generate report with LLM
            logger.info(f"Stage 2: Generating report with {self.llm.get_provider_name()}")
            
            # Prepare data for LLM
            data_for_llm = {
                "query": request.query,
                "date_range": request.date_range,
                "items": raw_data,
                "count": len(raw_data)
            }
            
            report = await self.llm.generate_report(
                data=data_for_llm,
                template=request.template
            )
            
            logger.info("Report generated successfully")
            
            # Stage 3: Send to output
            logger.info(f"Stage 3: Sending to {self.output.get_output_name()}")
            
            output_metadata = {
                "title": request.output_title or f"{request.template.title()} Report - {datetime.now().strftime('%Y-%m-%d')}",
                "tags": request.output_tags
            }
            
            output_result = await self.output.send(
                content=report,
                metadata=output_metadata
            )
            
            logger.info(f"Output status: {output_result['status']}")
            
            # Compile final response
            completed_at = datetime.now()
            duration = (completed_at - started_at).total_seconds()
            
            return PipelineResponse(
                status="success" if output_result["status"] == "success" else "partial",
                message=f"Pipeline executed successfully. {output_result['message']}",
                data_fetched=len(raw_data),
                report=report,
                output_url=output_result.get("url"),
                providers={
                    "llm": self.llm.get_provider_name(),
                    "source": self.source.get_source_name(),
                    "output": self.output.get_output_name()
                },
                started_at=started_at,
                completed_at=completed_at,
                duration_seconds=duration
            )
        
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}", exc_info=True)
            
            completed_at = datetime.now()
            duration = (completed_at - started_at).total_seconds()
            
            return PipelineResponse(
                status="failed",
                message=f"Pipeline execution failed: {str(e)}",
                data_fetched=0,
                report=None,
                output_url=None,
                providers={
                    "llm": self.llm.get_provider_name(),
                    "source": self.source.get_source_name(),
                    "output": self.output.get_output_name()
                },
                started_at=started_at,
                completed_at=completed_at,
                duration_seconds=duration
            )