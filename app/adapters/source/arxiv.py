import arxiv
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.adapters.source.base import BaseSourceAdapter


class ArXivAdapter(BaseSourceAdapter):
    """
    arXiv academic paper data source
    Suitable for: Academic paper tracking scenarios
    """
    
    def __init__(self):
        self.client = arxiv.Client()
    
    async def fetch(
        self, 
        query: str,
        max_results: int = 10,
        date_from: datetime = None,
        date_to: datetime = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch papers from arXiv
        
        Example queries:
        - "machine learning"
        - "cat:cs.LG" (machine learning category)
        - "au:Hinton" (specific author)
        - "ti:transformer" (title contains transformer)
        """
        
        # Default to last week if no date range specified
        if not date_from:
            date_from = datetime.now() - timedelta(days=7)
        if not date_to:
            date_to = datetime.now()
        
        # arXiv search syntax
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        results = []
        
        for paper in self.client.results(search):
            # Filter by date
            if paper.published.replace(tzinfo=None) < date_from:
                continue
            if paper.published.replace(tzinfo=None) > date_to:
                continue
            
            # Standardize data format
            standardized = {
                "id": paper.entry_id,
                "title": paper.title,
                "content": paper.summary,  # arXiv abstract
                "summary": paper.summary[:200] + "..." if len(paper.summary) > 200 else paper.summary,
                "authors": [author.name for author in paper.authors],
                "published_date": paper.published.isoformat(),
                "url": paper.entry_id,
                "source": "arXiv",
                "metadata": {
                    "categories": paper.categories,
                    "primary_category": paper.primary_category,
                    "pdf_url": paper.pdf_url,
                    "updated": paper.updated.isoformat() if paper.updated else None,
                    "comment": paper.comment,
                    "journal_ref": paper.journal_ref
                }
            }
            
            results.append(standardized)
        
        return results
    
    def get_source_name(self) -> str:
        return "arXiv"