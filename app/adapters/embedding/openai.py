"""
OpenAI Embedding Adapter
Uses OpenAI's text-embedding models for generating embeddings
"""
import logging
from typing import List
from openai import AsyncOpenAI
from app.adapters.embedding.base import BaseEmbeddingAdapter
from app.config import settings

logger = logging.getLogger(__name__)


class OpenAIEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    OpenAI Embedding adapter using text-embedding-3-small/large models.
    
    Models available:
    - text-embedding-3-small: 1536 dimensions, cheaper
    - text-embedding-3-large: 3072 dimensions, more accurate
    - text-embedding-ada-002: 1536 dimensions (legacy)
    
    Pricing (as of 2024):
    - text-embedding-3-small: $0.00002 / 1K tokens
    - text-embedding-3-large: $0.00013 / 1K tokens
    """
    
    # Model dimension mapping
    MODEL_DIMENSIONS = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
    }
    
    def __init__(self, model: str = None):
        """
        Initialize OpenAI embedding adapter.
        
        Args:
            model: Model name, defaults to settings.OPENAI_EMBEDDING_MODEL
        """
        self.model = model or getattr(settings, 'OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        if self.model not in self.MODEL_DIMENSIONS:
            logger.warning(f"Unknown model {self.model}, assuming 1536 dimensions")
        
        logger.info(f"OpenAI Embedding adapter initialized with model: {self.model}")
    
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: The text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch.
        
        OpenAI API supports batching natively, which is more efficient.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        try:
            # OpenAI handles batching automatically
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            
            # Sort by index to maintain order
            embeddings = [None] * len(texts)
            for item in response.data:
                embeddings[item.index] = item.embedding
            
            return embeddings
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embedding vectors."""
        return self.MODEL_DIMENSIONS.get(self.model, 1536)
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "OpenAI"
    
    def get_model_name(self) -> str:
        """Get model name."""
        return self.model