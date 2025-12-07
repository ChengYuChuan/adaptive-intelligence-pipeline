"""
Embedding adapter factory
"""
from app.adapters.embedding.base import BaseEmbeddingAdapter
from app.config import settings


def get_embedding_adapter() -> BaseEmbeddingAdapter:
    """
    Factory function to get the appropriate embedding adapter based on settings.
    
    Returns:
        Instance of the configured embedding adapter
        
    Raises:
        ValueError: If the configured provider is not supported
    """
    provider = getattr(settings, 'EMBEDDING_PROVIDER', 'openai')
    
    if provider == "openai":
        from app.adapters.embedding.openai import OpenAIEmbeddingAdapter
        return OpenAIEmbeddingAdapter()
    
    elif provider == "bedrock":
        # Future: Amazon Titan Embeddings
        raise NotImplementedError("Bedrock embedding adapter coming soon")
    
    elif provider == "local":
        # Future: Sentence Transformers
        raise NotImplementedError("Local embedding adapter coming soon")
    
    else:
        raise ValueError(
            f"Unknown embedding provider: {provider}. "
            f"Supported providers: openai, bedrock, local"
        )


__all__ = ["BaseEmbeddingAdapter", "get_embedding_adapter"]