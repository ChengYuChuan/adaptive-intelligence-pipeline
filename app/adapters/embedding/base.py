"""
Base class for Embedding adapters
Defines the interface for generating text embeddings
"""
from abc import ABC, abstractmethod
from typing import List


class BaseEmbeddingAdapter(ABC):
    """
    Abstract base class for all embedding adapters.
    
    Embedding adapters are responsible for:
    1. Converting text into vector representations
    2. Supporting both single and batch operations
    
    Implementations:
    - OpenAIEmbeddingAdapter: OpenAI text-embedding-3-small/large
    - BedrockEmbeddingAdapter: Amazon Titan Embeddings
    - LocalEmbeddingAdapter: Sentence Transformers (offline)
    """
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: The text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        pass
    
    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch operation).
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        pass
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.
        
        Returns:
            Integer dimension (e.g., 1536 for OpenAI, 1024 for Titan)
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of this embedding provider.
        
        Returns:
            Provider name (e.g., "OpenAI", "Bedrock", "Local")
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the model name being used.
        
        Returns:
            Model name (e.g., "text-embedding-3-small")
        """
        pass