"""
Data ingestion service - handles fetching data from various sources
"""
import logging
from typing import List, Dict, Any
from datetime import datetime

from app.adapters.source import get_source_adapter
from app.schemas.paper import Paper, PaperCollection
from app.schemas.news import NewsArticle, NewsCollection

logger = logging.getLogger(__name__)


class IngestionService:
    """
    Service for ingesting data from various sources
    Handles data fetching and initial processing
    """
    
    def __init__(self):
        self.source_adapter = get_source_adapter()
    
    async def fetch_papers(
        self,
        query: str,
        max_results: int = 10,
        date_from: datetime = None,
        date_to: datetime = None
    ) -> PaperCollection:
        """
        Fetch academic papers from source
        
        Args:
            query: Search query
            max_results: Maximum number of results
            date_from: Start date
            date_to: End date
            
        Returns:
            PaperCollection with fetched papers
        """
        logger.info(f"Fetching papers: query='{query}', max={max_results}")
        
        try:
            # Fetch raw data from adapter
            raw_data = await self.source_adapter.fetch(
                query=query,
                max_results=max_results,
                date_from=date_from,
                date_to=date_to
            )
            
            # Convert to Paper objects
            papers = []
            for item in raw_data:
                try:
                    paper = Paper(
                        id=item.get("id"),
                        title=item.get("title"),
                        authors=item.get("authors", []),
                        abstract=item.get("content", ""),
                        published_date=datetime.fromisoformat(item.get("published_date")),
                        updated_date=datetime.fromisoformat(item["metadata"].get("updated")) if item["metadata"].get("updated") else None,
                        categories=item["metadata"].get("categories", []),
                        primary_category=item["metadata"].get("primary_category"),
                        pdf_url=item["metadata"].get("pdf_url"),
                        abs_url=item.get("url"),
                        comment=item["metadata"].get("comment"),
                        journal_ref=item["metadata"].get("journal_ref")
                    )
                    papers.append(paper)
                except Exception as e:
                    logger.warning(f"Failed to parse paper: {e}")
                    continue
            
            collection = PaperCollection(
                papers=papers,
                total_count=len(papers),
                query=query,
                date_from=date_from,
                date_to=date_to
            )
            
            logger.info(f"Successfully fetched {len(papers)} papers")
            return collection
            
        except Exception as e:
            logger.error(f"Error fetching papers: {e}", exc_info=True)
            raise
    
    async def fetch_news(
        self,
        query: str,
        max_results: int = 20,
        date_from: datetime = None,
        date_to: datetime = None
    ) -> NewsCollection:
        """
        Fetch news articles from source
        
        Args:
            query: Search query
            max_results: Maximum number of results
            date_from: Start date
            date_to: End date
            
        Returns:
            NewsCollection with fetched articles
        """
        logger.info(f"Fetching news: query='{query}', max={max_results}")
        
        try:
            # Fetch raw data from adapter
            raw_data = await self.source_adapter.fetch(
                query=query,
                max_results=max_results,
                date_from=date_from,
                date_to=date_to
            )
            
            # Convert to NewsArticle objects
            articles = []
            for item in raw_data:
                try:
                    # Extract source info
                    source_data = item.get("metadata", {}).get("source", {})
                    if isinstance(source_data, dict):
                        source = {
                            "id": source_data.get("id"),
                            "name": source_data.get("name", item.get("source", "Unknown"))
                        }
                    else:
                        source = {
                            "id": None,
                            "name": item.get("source", "Unknown")
                        }
                    
                    article = NewsArticle(
                        id=item.get("id"),
                        title=item.get("title"),
                        description=item.get("summary"),
                        content=item.get("content", ""),
                        author=item.get("metadata", {}).get("author"),
                        source=source,
                        published_at=datetime.fromisoformat(item.get("published_date")),
                        url=item.get("url"),
                        url_to_image=item.get("metadata", {}).get("image_url"),
                        language=item.get("metadata", {}).get("language", "en"),
                        country=item.get("metadata", {}).get("country"),
                        category=item.get("metadata", {}).get("category")
                    )
                    articles.append(article)
                except Exception as e:
                    logger.warning(f"Failed to parse news article: {e}")
                    continue
            
            collection = NewsCollection(
                articles=articles,
                total_count=len(articles),
                query=query,
                date_from=date_from,
                date_to=date_to
            )
            
            logger.info(f"Successfully fetched {len(articles)} news articles")
            return collection
            
        except Exception as e:
            logger.error(f"Error fetching news: {e}", exc_info=True)
            raise
    
    def get_source_info(self) -> Dict[str, Any]:
        """Get information about the current data source"""
        return {
            "source_name": self.source_adapter.get_source_name(),
            "source_type": type(self.source_adapter).__name__
        }