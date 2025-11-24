"""
NewsAPI Source Adapter - Week 2 Implementation
Fetches real-time news articles for financial/investment analysis
"""
from typing import List, Dict, Any
from datetime import datetime
from newsapi import NewsApiClient
from app.adapters.source.base import BaseSourceAdapter
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class NewsAPIAdapter(BaseSourceAdapter):
    """
    NewsAPI data source adapter
    Suitable for: Investment analysis, financial news tracking
    
    API Documentation: https://newsapi.org/docs
    Free tier: 100 requests/day, articles from last 30 days
    """
    
    def __init__(self):
        """Initialize NewsAPI client with API key from settings"""
        if not settings.NEWSAPI_KEY:
            raise ValueError("NEWSAPI_KEY not configured in environment")
        
        self.client = NewsApiClient(api_key=settings.NEWSAPI_KEY)
        logger.info("NewsAPI adapter initialized")
    
    async def fetch(
        self,
        query: str,
        max_results: int = 10,
        date_from: datetime = None,
        date_to: datetime = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch news articles from NewsAPI
        
        Query examples:
        - "TSMC OR NVIDIA" - Company names
        - "semiconductor industry" - Topic
        - "Apple AND iPhone" - Multiple keywords
        - Use OR, AND, NOT operators for complex queries
        
        Args:
            query: Search query string
            max_results: Maximum number of results (up to 100)
            date_from: Start date for filtering
            date_to: End date for filtering
            
        Returns:
            List of standardized article dictionaries
        """
        logger.info(f"Fetching news: query='{query}', max={max_results}")
        
        try:
            # Prepare parameters
            params = {
                'q': query,
                'language': 'en',  # Can be configurable
                'sort_by': 'publishedAt',  # Most recent first
                'page_size': min(max_results, 100)  # API limit is 100
            }
            
            # Add date filters if provided
            if date_from:
                params['from_param'] = date_from.strftime('%Y-%m-%d')
            if date_to:
                params['to'] = date_to.strftime('%Y-%m-%d')
            
            # Call NewsAPI (everything endpoint for comprehensive search)
            response = self.client.get_everything(**params)
            
            # Check response status
            if response.get('status') != 'ok':
                logger.error(f"NewsAPI error: {response.get('message', 'Unknown error')}")
                return []
            
            articles = response.get('articles', [])
            logger.info(f"NewsAPI returned {len(articles)} articles")
            
            # Standardize data format
            standardized_results = []
            for article in articles:
                try:
                    standardized = self._standardize_article(article)
                    standardized_results.append(standardized)
                except Exception as e:
                    logger.warning(f"Failed to parse article: {e}")
                    continue
            
            logger.info(f"Successfully standardized {len(standardized_results)} articles")
            return standardized_results
            
        except Exception as e:
            logger.error(f"Error fetching from NewsAPI: {e}", exc_info=True)
            raise
    
    def _standardize_article(self, article: dict) -> Dict[str, Any]:
        """
        Convert NewsAPI article to standardized format
        
        NewsAPI article structure:
        {
            "source": {"id": "...", "name": "..."},
            "author": "...",
            "title": "...",
            "description": "...",
            "url": "...",
            "urlToImage": "...",
            "publishedAt": "2024-01-15T10:30:00Z",
            "content": "..."
        }
        """
        # Parse published date
        published_str = article.get('publishedAt', '')
        try:
            # NewsAPI uses ISO format with 'Z' timezone
            published_date = datetime.fromisoformat(
                published_str.replace('Z', '+00:00')
            )
        except Exception:
            published_date = datetime.now()
        
        # Extract source info
        source = article.get('source', {})
        source_name = source.get('name', 'Unknown')
        
        # Create standardized format matching BaseSourceAdapter interface
        standardized = {
            "id": article.get('url', ''),  # Use URL as unique ID
            "title": article.get('title', 'No title'),
            "content": article.get('content', article.get('description', '')),
            "summary": (article.get('description', '')[:200] + "...") 
                       if len(article.get('description', '')) > 200 
                       else article.get('description', ''),
            "authors": [article.get('author', 'Unknown')] if article.get('author') else [],
            "published_date": published_date.isoformat(),
            "url": article.get('url', ''),
            "source": "NewsAPI",
            "metadata": {
                "source_id": source.get('id'),
                "source_name": source_name,
                "author": article.get('author'),
                "image_url": article.get('urlToImage'),
                "original_content": article.get('content'),  # May be truncated
                "description": article.get('description')
            }
        }
        
        return standardized
    
    def get_source_name(self) -> str:
        """Return the source name"""
        return "NewsAPI"


# Additional helper functions for financial news analysis

def filter_by_companies(
    articles: List[Dict[str, Any]], 
    companies: List[str]
) -> List[Dict[str, Any]]:
    """
    Filter articles that mention specific companies
    
    Args:
        articles: List of articles from fetch()
        companies: List of company names to filter by
        
    Returns:
        Filtered list of articles
    """
    filtered = []
    companies_lower = [c.lower() for c in companies]
    
    for article in articles:
        text = (
            article.get('title', '') + ' ' + 
            article.get('content', '') + ' ' + 
            article.get('summary', '')
        ).lower()
        
        if any(company in text for company in companies_lower):
            filtered.append(article)
    
    return filtered


def categorize_by_sentiment_keywords(
    articles: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Simple keyword-based categorization (before LLM analysis)
    
    Returns:
        Dictionary with 'positive', 'negative', 'neutral' categories
    """
    positive_keywords = [
        'surge', 'gain', 'profit', 'growth', 'success', 'win',
        'breakthrough', 'record', 'boost', 'rally', 'soar'
    ]
    
    negative_keywords = [
        'fall', 'loss', 'decline', 'crash', 'fail', 'drop',
        'crisis', 'concern', 'risk', 'warning', 'plunge'
    ]
    
    categorized = {
        'positive': [],
        'negative': [],
        'neutral': []
    }
    
    for article in articles:
        text = (
            article.get('title', '') + ' ' + 
            article.get('summary', '')
        ).lower()
        
        pos_count = sum(1 for kw in positive_keywords if kw in text)
        neg_count = sum(1 for kw in negative_keywords if kw in text)
        
        if pos_count > neg_count:
            categorized['positive'].append(article)
        elif neg_count > pos_count:
            categorized['negative'].append(article)
        else:
            categorized['neutral'].append(article)
    
    return categorized