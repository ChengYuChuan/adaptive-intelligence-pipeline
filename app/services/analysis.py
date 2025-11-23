"""
Analysis service - handles LLM-based content analysis
"""
import logging
from typing import List, Dict, Any

from app.adapters.llm import get_llm_adapter
from app.schemas.paper import PaperCollection
from app.schemas.news import NewsCollection, NewsArticle
from app.prompts.academic_summary import get_academic_prompt
from app.prompts.financial_analysis import get_financial_prompt

logger = logging.getLogger(__name__)


class AnalysisService:
    """
    Service for analyzing data using LLM
    Handles various types of analysis (sentiment, trends, insights, etc.)
    """
    
    def __init__(self):
        self.llm_adapter = get_llm_adapter()
    
    async def analyze_papers(
        self,
        papers: PaperCollection
    ) -> Dict[str, Any]:
        """
        Analyze a collection of academic papers
        
        Args:
            papers: Collection of papers to analyze
            
        Returns:
            Dictionary with analysis results:
            - summary: Overall summary
            - trends: Trending topics
            - insights: Key insights
            - recommendations: Recommended papers
        """
        logger.info(f"Analyzing {papers.total_count} papers")
        
        # Prepare papers summary for LLM
        papers_summary = self._format_papers_for_llm(papers)
        
        # Run various analyses
        results = {}
        
        # 1. Generate overall summary
        try:
            summary_prompt = get_academic_prompt(
                "summary",
                papers_summary=papers_summary
            )
            results["summary"] = await self.llm_adapter.summarize(summary_prompt)
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            results["summary"] = "Failed to generate summary"
        
        # 2. Identify trends
        try:
            trends_prompt = get_academic_prompt(
                "trends",
                papers_summary=papers_summary
            )
            trends_text = await self.llm_adapter.answer_question(
                question="What are the trending research directions?",
                context=trends_prompt
            )
            results["trends"] = trends_text
        except Exception as e:
            logger.error(f"Failed to identify trends: {e}")
            results["trends"] = "Failed to identify trends"
        
        # 3. Extract key insights
        try:
            insights_prompt = get_academic_prompt(
                "insights",
                papers_summary=papers_summary
            )
            insights_list = await self.llm_adapter.extract_key_points(
                insights_prompt,
                num_points=5
            )
            results["insights"] = insights_list
        except Exception as e:
            logger.error(f"Failed to extract insights: {e}")
            results["insights"] = []
        
        # 4. Generate recommendations
        try:
            rec_prompt = get_academic_prompt(
                "recommendation",
                papers_summary=papers_summary
            )
            recommendations = await self.llm_adapter.answer_question(
                question="Which papers should readers prioritize?",
                context=rec_prompt
            )
            results["recommendations"] = recommendations
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            results["recommendations"] = "Failed to generate recommendations"
        
        logger.info("Paper analysis completed")
        return results
    
    async def analyze_news(
        self,
        news: NewsCollection
    ) -> Dict[str, Any]:
        """
        Analyze a collection of news articles
        
        Args:
            news: Collection of news articles to analyze
            
        Returns:
            Dictionary with analysis results:
            - sentiment: Overall market sentiment
            - key_developments: Key news developments
            - company_impacts: Impact on specific companies
            - risks: Risk factors
            - opportunities: Investment opportunities
        """
        logger.info(f"Analyzing {news.total_count} news articles")
        
        # Prepare articles summary for LLM
        articles_summary = self._format_news_for_llm(news)
        
        # Run various analyses
        results = {}
        
        # 1. Sentiment analysis
        try:
            sentiment_prompt = get_financial_prompt(
                "sentiment",
                articles_summary=articles_summary
            )
            sentiment_data = await self.llm_adapter.analyze_sentiment(articles_summary)
            results["sentiment"] = sentiment_data
        except Exception as e:
            logger.error(f"Failed sentiment analysis: {e}")
            results["sentiment"] = {
                "sentiment": "neutral",
                "confidence": 0.5,
                "reasoning": "Analysis failed"
            }
        
        # 2. Key developments
        try:
            key_points = await self.llm_adapter.extract_key_points(
                articles_summary,
                num_points=7
            )
            results["key_developments"] = key_points
        except Exception as e:
            logger.error(f"Failed to extract key developments: {e}")
            results["key_developments"] = []
        
        # 3. Risk assessment
        try:
            risk_prompt = get_financial_prompt(
                "risk",
                articles_summary=articles_summary
            )
            risks = await self.llm_adapter.answer_question(
                question="What are the key risk factors?",
                context=risk_prompt
            )
            results["risks"] = risks
        except Exception as e:
            logger.error(f"Failed risk assessment: {e}")
            results["risks"] = "Failed to assess risks"
        
        # 4. Opportunities
        try:
            opp_prompt = get_financial_prompt(
                "opportunity",
                articles_summary=articles_summary
            )
            opportunities = await self.llm_adapter.answer_question(
                question="What are the investment opportunities?",
                context=opp_prompt
            )
            results["opportunities"] = opportunities
        except Exception as e:
            logger.error(f"Failed opportunity analysis: {e}")
            results["opportunities"] = "Failed to identify opportunities"
        
        logger.info("News analysis completed")
        return results
    
    async def analyze_sentiment_batch(
        self,
        articles: List[NewsArticle]
    ) -> List[NewsArticle]:
        """
        Analyze sentiment for multiple articles
        
        Args:
            articles: List of news articles
            
        Returns:
            Articles with sentiment fields populated
        """
        logger.info(f"Running sentiment analysis on {len(articles)} articles")
        
        for article in articles:
            try:
                sentiment_data = await self.llm_adapter.analyze_sentiment(
                    article.content[:1000]  # Use first 1000 chars
                )
                article.sentiment = sentiment_data.get("sentiment", "neutral")
                article.sentiment_score = sentiment_data.get("confidence", 0.5)
            except Exception as e:
                logger.warning(f"Failed sentiment for article {article.id}: {e}")
                article.sentiment = "neutral"
                article.sentiment_score = 0.5
        
        return articles
    
    def _format_papers_for_llm(self, papers: PaperCollection) -> str:
        """Format papers collection for LLM input"""
        formatted = f"Query: {papers.query}\n"
        formatted += f"Total Papers: {papers.total_count}\n\n"
        
        for i, paper in enumerate(papers.papers, 1):
            formatted += f"Paper {i}:\n"
            formatted += f"Title: {paper.title}\n"
            formatted += f"Authors: {', '.join(paper.authors[:3])}"
            if len(paper.authors) > 3:
                formatted += f" et al."
            formatted += f"\n"
            formatted += f"Categories: {', '.join(paper.categories)}\n"
            formatted += f"Abstract: {paper.abstract[:300]}...\n\n"
        
        return formatted
    
    def _format_news_for_llm(self, news: NewsCollection) -> str:
        """Format news collection for LLM input"""
        formatted = f"Query: {news.query}\n"
        formatted += f"Total Articles: {news.total_count}\n\n"
        
        for i, article in enumerate(news.articles, 1):
            formatted += f"Article {i}:\n"
            formatted += f"Title: {article.title}\n"
            formatted += f"Source: {article.source.name}\n"
            formatted += f"Published: {article.published_at.strftime('%Y-%m-%d %H:%M')}\n"
            
            # Use description if available, otherwise content
            content = article.description or article.content
            formatted += f"Content: {content[:400]}...\n\n"
        
        return formatted
    
    def get_llm_info(self) -> Dict[str, Any]:
        """Get information about the current LLM provider"""
        return {
            "provider_name": self.llm_adapter.get_provider_name(),
            "provider_type": type(self.llm_adapter).__name__
        }