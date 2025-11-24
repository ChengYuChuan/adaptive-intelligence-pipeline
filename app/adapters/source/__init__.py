from app.adapters.source.base import BaseSourceAdapter
from app.config import settings


def get_source_adapter() -> BaseSourceAdapter:
    """
    Factory function to get the appropriate source adapter based on settings
    
    Returns:
        Instance of the configured source adapter
        
    Raises:
        ValueError: If the configured provider is not supported
    """
    provider = settings.SOURCE_PROVIDER
    
    if provider == "arxiv":
        from app.adapters.source.arxiv import ArXivAdapter
        return ArXivAdapter()
    
    elif provider == "newsapi":
        from app.adapters.source.newsapi import NewsAPIAdapter
        raise NotImplementedError("NewsAPI adapter coming in Week 2")
    
    elif provider == "internal":
        # Week 2: Internal database implementation
        raise NotImplementedError("Internal database adapter coming in Week 2")
    
    else:
        raise ValueError(
            f"Unknown source provider: {provider}. "
            f"Supported providers: arxiv, newsapi, internal"
        )


__all__ = ["BaseSourceAdapter", "get_source_adapter"]