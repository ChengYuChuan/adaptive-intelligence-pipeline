"""
Chroma Vector Store Adapter
Local vector database for development and small-scale deployments
"""
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.adapters.vectorstore.base import (
    BaseVectorStoreAdapter, 
    Document, 
    SearchResult
)
from app.config import settings

logger = logging.getLogger(__name__)


class ChromaAdapter(BaseVectorStoreAdapter):
    """
    Chroma vector store adapter for local development.
    
    Features:
    - No external dependencies (runs embedded)
    - Persistent storage option
    - Fast similarity search
    - Metadata filtering support
    
    Storage modes:
    - In-memory: Fast but not persistent
    - Persistent: Stored on disk
    """
    
    def __init__(self, persist_directory: str = None):
        """
        Initialize Chroma adapter.
        
        Args:
            persist_directory: Directory for persistent storage.
                              If None, uses in-memory storage.
        """
        self.persist_directory = persist_directory or getattr(
            settings, 'CHROMA_PERSIST_DIR', './data/vectorstore'
        )
        self.client = None
        self._collections: Dict[str, Any] = {}
    
    async def initialize(self) -> None:
        """Initialize Chroma client with persistent storage."""
        try:
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info(f"Chroma initialized with storage at: {self.persist_directory}")
        except Exception as e:
            logger.error(f"Failed to initialize Chroma: {e}")
            raise
    
    def _get_or_create_collection(self, collection_name: str):
        """Get existing collection or create new one."""
        if collection_name not in self._collections:
            self._collections[collection_name] = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
        return self._collections[collection_name]
    
    async def add_documents(
        self,
        documents: List[Document],
        collection_name: str = "default"
    ) -> List[str]:
        """
        Add documents with embeddings to Chroma.
        
        Args:
            documents: List of Document objects with embeddings
            collection_name: Name of the collection
            
        Returns:
            List of added document IDs
        """
        if not documents:
            return []
        
        collection = self._get_or_create_collection(collection_name)
        
        ids = [doc.id for doc in documents]
        embeddings = [doc.embedding for doc in documents]
        contents = [doc.content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        try:
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas
            )
            logger.info(f"Added {len(documents)} documents to collection '{collection_name}'")
            return ids
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    async def search(
        self,
        query_embedding: List[float],
        collection_name: str = "default",
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query vector
            collection_name: Collection to search
            top_k: Number of results
            filter_metadata: Optional metadata filters
            
        Returns:
            List of SearchResult objects
        """
        collection = self._get_or_create_collection(collection_name)
        
        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_metadata,
                include=["documents", "metadatas", "distances"]
            )
            
            search_results = []
            
            if results['ids'] and results['ids'][0]:
                for i, doc_id in enumerate(results['ids'][0]):
                    # Chroma returns distances, convert to similarity score
                    # For cosine distance: similarity = 1 - distance
                    distance = results['distances'][0][i] if results['distances'] else 0
                    score = 1 - distance
                    
                    doc = Document(
                        id=doc_id,
                        content=results['documents'][0][i] if results['documents'] else "",
                        metadata=results['metadatas'][0][i] if results['metadatas'] else {},
                        embedding=None  # Don't return embeddings in search results
                    )
                    
                    search_results.append(SearchResult(document=doc, score=score))
            
            return search_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    async def delete_documents(
        self,
        document_ids: List[str],
        collection_name: str = "default"
    ) -> int:
        """Delete documents by ID."""
        collection = self._get_or_create_collection(collection_name)
        
        try:
            collection.delete(ids=document_ids)
            logger.info(f"Deleted {len(document_ids)} documents from '{collection_name}'")
            return len(document_ids)
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            raise
    
    async def get_document(
        self,
        document_id: str,
        collection_name: str = "default"
    ) -> Optional[Document]:
        """Get a specific document by ID."""
        collection = self._get_or_create_collection(collection_name)
        
        try:
            results = collection.get(
                ids=[document_id],
                include=["documents", "metadatas", "embeddings"]
            )
            
            if results['ids']:
                return Document(
                    id=results['ids'][0],
                    content=results['documents'][0] if results['documents'] else "",
                    metadata=results['metadatas'][0] if results['metadatas'] else {},
                    embedding=results['embeddings'][0] if results['embeddings'] else None
                )
            return None
            
        except Exception as e:
            logger.error(f"Failed to get document: {e}")
            return None
    
    async def list_collections(self) -> List[str]:
        """List all collection names."""
        collections = self.client.list_collections()
        return [col.name for col in collections]
    
    async def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection."""
        try:
            self.client.delete_collection(collection_name)
            if collection_name in self._collections:
                del self._collections[collection_name]
            logger.info(f"Deleted collection '{collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            return False
    
    async def get_collection_stats(
        self, 
        collection_name: str = "default"
    ) -> Dict[str, Any]:
        """Get collection statistics."""
        collection = self._get_or_create_collection(collection_name)
        
        return {
            "name": collection_name,
            "count": collection.count(),
            "metadata": collection.metadata
        }
    
    def get_store_name(self) -> str:
        """Get store name."""
        return "Chroma"