"""
Vector store adapter factory
"""
from app.adapters.vectorstore.base import (
    BaseVectorStoreAdapter,
    Document,
    SearchResult
)
from app.config import settings


def get_vectorstore_adapter() -> BaseVectorStoreAdapter:
    """
    Factory function to get the appropriate vector store adapter.
    
    Returns:
        Instance of the configured vector store adapter
        
    Raises:
        ValueError: If the configured provider is not supported
    """
    provider = getattr(settings, 'VECTORSTORE_PROVIDER', 'chroma')
    
    if provider == "chroma":
        from app.adapters.vectorstore.chroma import ChromaAdapter
        return ChromaAdapter()
    
    elif provider == "pgvector":
        from app.adapters.vectorstore.pgvector import PgVectorAdapter
        return PgVectorAdapter()
    
    elif provider == "azure":
        # Future: Azure AI Search
        raise NotImplementedError("Azure AI Search adapter coming soon")
    
    else:
        raise ValueError(
            f"Unknown vector store provider: {provider}. "
            f"Supported providers: chroma, pgvector, azure"
        )


__all__ = [
    "BaseVectorStoreAdapter",
    "Document",
    "SearchResult",
    "get_vectorstore_adapter"
]