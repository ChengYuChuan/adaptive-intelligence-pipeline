"""
Report generation service - handles creating structured reports from analysis
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

from app.adapters.output import get_output_adapter
from app.schemas.paper import PaperCollection
from app.schemas.news import NewsCollection
from app.schemas.report import (
    AcademicReport,
    FinancialReport,
    ReportMetadata,
    GeneratedReport,
    ReportType,
    ReportSection,
    KeyInsight
)

logger = logging.getLogger(__name__)


class ReportGenerationService:
    """
    Service for generating and outputting reports
    Handles report formatting and delivery
    """
    
    def __init__(self):
        self.output_adapter = get_output_adapter()
    
    async def generate_academic_report(
        self,
        papers: PaperCollection,
        analysis: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> GeneratedReport:
        """
        Generate an academic research report
        
        Args:
            papers: Collection of papers
            analysis: Analysis results from AnalysisService
            metadata: Additional metadata (llm_provider, etc.)
            
        Returns:
            GeneratedReport with all details
        """
        logger.info("Generating academic report")
        start_time = datetime.now()
        
        try:
            # Create report ID
            report_id = f"academic_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Build sections
            sections = []
            
            # Section 1: Executive Summary
            sections.append(ReportSection(
                title="整體概述",
                content=analysis.get("summary", "No summary available"),
                order=1
            ))
            
            # Section 2: Trending Topics
            sections.append(ReportSection(
                title="研究趨勢",
                content=analysis.get("trends", "No trends identified"),
                order=2
            ))
            
            # Section 3: Key Papers
            papers_section = self._format_papers_section(papers)
            sections.append(ReportSection(
                title="重點論文",
                content=papers_section,
                order=3
            ))
            
            # Section 4: Recommendations
            sections.append(ReportSection(
                title="推薦閱讀",
                content=analysis.get("recommendations", "No recommendations"),
                order=4
            ))
            
            # Extract key insights
            insights = []
            insight_texts = analysis.get("insights", [])
            for i, insight_text in enumerate(insight_texts[:5], 1):
                insights.append(KeyInsight(
                    insight=insight_text,
                    importance="high" if i <= 2 else "medium",
                    related_items=[]
                ))
            
            # Create academic report
            academic_report = AcademicReport(
                report_id=report_id,
                title=f"{papers.query} - Academic Research Summary",
                generated_at=datetime.now(),
                query=papers.query,
                date_range=f"{papers.date_from} to {papers.date_to}" if papers.date_from else "Not specified",
                total_papers=papers.total_count,
                executive_summary=analysis.get("summary", ""),
                sections=sections,
                key_insights=insights,
                trending_topics=[],  # Could extract from analysis
                recommended_papers=[],  # Could extract paper IDs
                llm_provider=metadata.get("llm_provider", "Unknown"),
                generation_time_seconds=0  # Will update later
            )
            
            # Generate text content
            text_content = self._format_academic_text(academic_report)
            
            # Create metadata
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            academic_report.generation_time_seconds = duration
            
            report_metadata = ReportMetadata(
                report_type=ReportType.ACADEMIC,
                data_sources=[metadata.get("source", "Unknown")],
                llm_provider=metadata.get("llm_provider", "Unknown"),
                output_destination=self.output_adapter.get_output_name(),
                generation_started=start_time,
                generation_completed=end_time,
                total_duration_seconds=duration,
                success=True
            )
            
            # Create final report
            generated_report = GeneratedReport(
                metadata=report_metadata,
                report=academic_report.model_dump(),
                raw_content=text_content,
                output_url=None  # Will be set after sending
            )
            
            logger.info(f"Academic report generated in {duration:.2f}s")
            return generated_report
            
        except Exception as e:
            logger.error(f"Failed to generate academic report: {e}", exc_info=True)
            raise
    
    async def generate_financial_report(
        self,
        news: NewsCollection,
        analysis: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> GeneratedReport:
        """
        Generate a financial analysis report
        
        Args:
            news: Collection of news articles
            analysis: Analysis results from AnalysisService
            metadata: Additional metadata
            
        Returns:
            GeneratedReport with all details
        """
        logger.info("Generating financial report")
        start_time = datetime.now()
        
        try:
            # Create report ID
            report_id = f"financial_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Build sections
            sections = []
            
            # Section 1: Market Summary
            sentiment_data = analysis.get("sentiment", {})
            market_summary = f"市場情緒: {sentiment_data.get('sentiment', 'neutral')}\n"
            market_summary += f"信心程度: {sentiment_data.get('confidence', 0.5):.2%}\n"
            market_summary += f"理由: {sentiment_data.get('reasoning', 'N/A')}"
            
            sections.append(ReportSection(
                title="市場概況",
                content=market_summary,
                order=1
            ))
            
            # Section 2: Key Developments
            key_devs = analysis.get("key_developments", [])
            key_devs_text = "\n".join([f"• {dev}" for dev in key_devs])
            sections.append(ReportSection(
                title="重要動態",
                content=key_devs_text,
                order=2
            ))
            
            # Section 3: Risk Factors
            sections.append(ReportSection(
                title="風險因素",
                content=analysis.get("risks", "No risks identified"),
                order=3
            ))
            
            # Section 4: Opportunities
            sections.append(ReportSection(
                title="投資機會",
                content=analysis.get("opportunities", "No opportunities identified"),
                order=4
            ))
            
            # Extract key insights
            insights = []
            for i, dev in enumerate(key_devs[:5], 1):
                insights.append(KeyInsight(
                    insight=dev,
                    importance="high" if i <= 2 else "medium",
                    related_items=[]
                ))
            
            # Create financial report
            financial_report = FinancialReport(
                report_id=report_id,
                title=f"{news.query} - Financial Analysis",
                generated_at=datetime.now(),
                query=news.query,
                date_range=f"{news.date_from} to {news.date_to}" if news.date_from else "Not specified",
                total_articles=news.total_count,
                market_summary=market_summary,
                sections=sections,
                key_insights=insights,
                overall_sentiment=sentiment_data.get("sentiment", "neutral"),
                sentiment_confidence=sentiment_data.get("confidence", 0.5),
                key_entities={},  # Could extract from news
                risk_factors=[],  # Could parse from risks section
                opportunities=[],  # Could parse from opportunities section
                llm_provider=metadata.get("llm_provider", "Unknown"),
                generation_time_seconds=0  # Will update later
            )
            
            # Generate text content
            text_content = self._format_financial_text(financial_report)
            
            # Create metadata
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            financial_report.generation_time_seconds = duration
            
            report_metadata = ReportMetadata(
                report_type=ReportType.FINANCIAL,
                data_sources=[metadata.get("source", "Unknown")],
                llm_provider=metadata.get("llm_provider", "Unknown"),
                output_destination=self.output_adapter.get_output_name(),
                generation_started=start_time,
                generation_completed=end_time,
                total_duration_seconds=duration,
                success=True
            )
            
            # Create final report
            generated_report = GeneratedReport(
                metadata=report_metadata,
                report=financial_report.model_dump(),
                raw_content=text_content,
                output_url=None  # Will be set after sending
            )
            
            logger.info(f"Financial report generated in {duration:.2f}s")
            return generated_report
            
        except Exception as e:
            logger.error(f"Failed to generate financial report: {e}", exc_info=True)
            raise
    
    async def send_report(
        self,
        report: GeneratedReport,
        output_title: Optional[str] = None,
        output_tags: Optional[list] = None
    ) -> str:
        """
        Send report to output destination
        
        Args:
            report: Generated report to send
            output_title: Optional custom title
            output_tags: Optional tags
            
        Returns:
            URL or identifier of sent report
        """
        logger.info(f"Sending report to {self.output_adapter.get_output_name()}")
        
        try:
            # Prepare metadata for output
            metadata = {
                "title": output_title or f"Report {report.metadata.report_type.value}",
                "tags": output_tags or [report.metadata.report_type.value],
                "generated_at": report.metadata.generation_completed.isoformat()
            }
            
            # Send via output adapter
            result = await self.output_adapter.send(
                content=report.raw_content,
                metadata=metadata
            )
            
            if result["status"] == "success":
                logger.info(f"Report sent successfully: {result.get('url', 'No URL')}")
                return result.get("url", "")
            else:
                logger.error(f"Failed to send report: {result.get('message')}")
                raise Exception(f"Output failed: {result.get('message')}")
                
        except Exception as e:
            logger.error(f"Error sending report: {e}", exc_info=True)
            raise
    
    def _format_papers_section(self, papers: PaperCollection) -> str:
        """Format papers into a readable section"""
        content = ""
        for i, paper in enumerate(papers.papers[:10], 1):  # Top 10
            content += f"\n{i}. **{paper.title}**\n"
            content += f"   作者: {', '.join(paper.authors[:3])}"
            if len(paper.authors) > 3:
                content += " et al."
            content += f"\n"
            content += f"   分類: {', '.join(paper.categories)}\n"
            content += f"   連結: {paper.abs_url}\n"
        
        return content
    
    def _format_academic_text(self, report: AcademicReport) -> str:
        """Format academic report as text"""
        text = f"# {report.title}\n\n"
        text += f"生成時間: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        text += f"查詢: {report.query}\n"
        text += f"論文數量: {report.total_papers}\n"
        text += f"分析引擎: {report.llm_provider}\n\n"
        text += "=" * 80 + "\n\n"
        
        # Add sections
        for section in sorted(report.sections, key=lambda x: x.order):
            text += f"## {section.title}\n\n"
            text += f"{section.content}\n\n"
            text += "-" * 80 + "\n\n"
        
        # Add key insights
        if report.key_insights:
            text += "## 重要見解\n\n"
            for i, insight in enumerate(report.key_insights, 1):
                text += f"{i}. [{insight.importance.upper()}] {insight.insight}\n"
            text += "\n"
        
        return text
    
    def _format_financial_text(self, report: FinancialReport) -> str:
        """Format financial report as text"""
        text = f"# {report.title}\n\n"
        text += f"生成時間: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        text += f"查詢: {report.query}\n"
        text += f"新聞數量: {report.total_articles}\n"
        text += f"整體情緒: {report.overall_sentiment} ({report.sentiment_confidence:.2%})\n"
        text += f"分析引擎: {report.llm_provider}\n\n"
        text += "=" * 80 + "\n\n"
        
        # Add sections
        for section in sorted(report.sections, key=lambda x: x.order):
            text += f"## {section.title}\n\n"
            text += f"{section.content}\n\n"
            text += "-" * 80 + "\n\n"
        
        # Add key insights
        if report.key_insights:
            text += "## 關鍵洞察\n\n"
            for i, insight in enumerate(report.key_insights, 1):
                text += f"{i}. [{insight.importance.upper()}] {insight.insight}\n"
            text += "\n"
        
        return text
    
    def get_output_info(self) -> Dict[str, Any]:
        """Get information about the current output adapter"""
        return {
            "output_name": self.output_adapter.get_output_name(),
            "output_type": type(self.output_adapter).__name__
        }