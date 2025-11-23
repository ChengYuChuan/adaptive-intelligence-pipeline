import app.adapters.source.arxiv as arxiv
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.adapters.source.base import BaseSourceAdapter


class ArXivAdapter(BaseSourceAdapter):
    """
    arXiv 學術論文資料來源
    適合：學術論文追蹤場景
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
        從 arXiv 獲取論文
        
        範例 query:
        - "machine learning"
        - "cat:cs.LG" (機器學習類別)
        - "au:Hinton" (特定作者)
        - "ti:transformer" (標題包含 transformer)
        """
        
        # 如果沒有指定日期範圍，預設最近一週
        if not date_from:
            date_from = datetime.now() - timedelta(days=7)
        if not date_to:
            date_to = datetime.now()
        
        # arXiv 的搜尋語法
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        results = []
        
        for paper in self.client.results(search):
            # 過濾日期
            if paper.published.replace(tzinfo=None) < date_from:
                continue
            if paper.published.replace(tzinfo=None) > date_to:
                continue
            
            # 標準化資料格式
            standardized = {
                "id": paper.entry_id,
                "title": paper.title,
                "content": paper.summary,  # arXiv 的 abstract
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
