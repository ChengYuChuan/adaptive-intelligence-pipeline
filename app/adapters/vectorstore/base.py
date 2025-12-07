"""
Base class for Vector Store adapters
Defines the interface for storing and retrieving document embeddings
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Document:
    """
    Represents a document chunk with its content and metadata
    """
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


@dataclass
class SearchResult:
    """
    Represents a search result with relevance score
    """
    document: Document
    score: float  # Similarity score (higher = more relevant)


class BaseVectorStoreAdapter(ABC):
    """
    Abstract base class for all vector store adapters.
    
    Vector stores are responsible for:
    1. Storing document embeddings
    2. Performing similarity search
    3. Managing document lifecycle (add, update, delete)
    
    Implementations:
    - ChromaAdapter: Local development (lightweight, no setup)
    - PgVectorAdapter: Production (PostgreSQL + pgvector extension)
    - AzureAISearchAdapter: Azure-native solution
    """
    
    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the vector store connection and create collection if needed.
        Should be called before any other operations.
        """
        pass
    
    @abstractmethod
    async def add_documents(
        self,
        documents: List[Document],
        collection_name: str = "default"
    ) -> List[str]:
        """
        Add documents with their embeddings to the vector store.
        
        Args:
            documents: List of Document objects with embeddings
            collection_name: Name of the collection to store documents
            
        Returns:
            List of document IDs that were added
        """
        pass
    
    @abstractmethod
    async def search(
        self,
        query_embedding: List[float],
        collection_name: str = "default",
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query_embedding: The embedding vector of the query
            collection_name: Name of the collection to search
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of SearchResult objects sorted by relevance
        """
        pass
    
    @abstractmethod
    async def delete_documents(
        self,
        document_ids: List[str],
        collection_name: str = "default"
    ) -> int:
        """
        Delete documents by their IDs.
        
        Args:
            document_ids: List of document IDs to delete
            collection_name: Name of the collection
            
        Returns:
            Number of documents deleted
        """
        pass
    
    @abstractmethod
    async def get_document(
        self,
        document_id: str,
        collection_name: str = "default"
    ) -> Optional[Document]:
        """
        Retrieve a specific document by ID.
        
        Args:
            document_id: The document ID
            collection_name: Name of the collection
            
        Returns:
            Document if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def list_collections(self) -> List[str]:
        """
        List all available collections.
        
        Returns:
            List of collection names
        """
        pass
    
    @abstractmethod
    async def delete_collection(self, collection_name: str) -> bool:
        """
        Delete an entire collection.
        
        Args:
            collection_name: Name of the collection to delete
            
        Returns:
            True if deleted successfully
        """
        pass
    
    @abstractmethod
    async def get_collection_stats(
        self, 
        collection_name: str = "default"
    ) -> Dict[str, Any]:
        """
        Get statistics about a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary with stats like document count, etc.
        """
        pass
    
    @abstractmethod
    def get_store_name(self) -> str:
        """
        Get the name of this vector store implementation.
        
        Returns:
            Store name (e.g., "Chroma", "PgVector", "AzureAISearch")
        """
        pass