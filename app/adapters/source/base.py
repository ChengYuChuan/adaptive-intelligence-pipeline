from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime


class BaseSourceAdapter(ABC):
    """
    Abstract base class for all data source adapters
    All source providers must implement this interface
    """
    
    @abstractmethod
    async def fetch(
        self,
        query: str,
        max_results: int = 10,
        date_from: datetime = None,
        date_to: datetime = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch data from the source
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            date_from: Start date for filtering (inclusive)
            date_to: End date for filtering (inclusive)
            
        Returns:
            List of dictionaries with standardized format:
            {
                "id": str,
                "title": str,
                "content": str,
                "summary": str,
                "authors": List[str],
                "published_date": str (ISO format),
                "url": str,
                "source": str (source name),
                "metadata": Dict[str, Any] (source-specific metadata)
            }
        """
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """
        Get the name of this data source
        
        Returns:
            Source name (e.g., "arXiv", "NewsAPI")
        """
        pass