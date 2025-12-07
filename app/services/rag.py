"""
RAG (Retrieval-Augmented Generation) Service
Handles question answering with source retrieval
"""
import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.adapters.vectorstore import get_vectorstore_adapter
from app.adapters.vectorstore.base import SearchResult
from app.adapters.embedding import get_embedding_adapter
from app.adapters.llm import get_llm_adapter
from app.schemas.rag import (
    AskRequest,
    AskResponse,
    SourceReference,
    CollectionStats,
    RAGHealthResponse
)
from app.config import settings

logger = logging.getLogger(__name__)


# RAG prompt template
RAG_SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided context documents.

Important guidelines:
1. Only answer based on the information provided in the context
2. If the context doesn't contain enough information to answer, say so clearly
3. Always cite which document(s) you're referencing in your answer
4. Use the same language as the question for your response
5. Be concise but thorough

Context documents will be provided in the following format:
[Document: filename, Page: X]
Content...

When referencing sources, use this format: (Source: filename, Page X)"""


RAG_USER_PROMPT_TEMPLATE = """Based on the following context documents, please answer the question.

Context:
{context}

Question: {question}

Please provide a clear, accurate answer based only on the above context. If the context doesn't contain enough information, indicate what's missing."""


class RAGService:
    """
    RAG Service for question answering with document retrieval.
    
    Flow:
    1. Embed the question
    2. Retrieve relevant document chunks
    3. Build context from chunks
    4. Generate answer with LLM
    5. Return answer with source references
    """
    
    def __init__(self):
        self.vectorstore = None
        self.embedding = None
        self.llm = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize all required services."""
        if self._initialized:
            return
        
        self.vectorstore = get_vectorstore_adapter()
        await self.vectorstore.initialize()
        
        self.embedding = get_embedding_adapter()
        self.llm = get_llm_adapter()
        
        self._initialized = True
        logger.info("RAG service initialized")
    
    async def ask(self, request: AskRequest) -> AskResponse:
        """
        Answer a question using RAG.
        
        Args:
            request: AskRequest containing question and parameters
            
        Returns:
            AskResponse with answer and source references
        """
        if not self._initialized:
            await self.initialize()
        
        total_start = time.time()
        
        try:
            # Step 1: Embed the question
            retrieval_start = time.time()
            logger.info(f"Processing question: {request.question[:50]}...")
            
            query_embedding = await self.embedding.embed_text(request.question)
            
            # Step 2: Retrieve relevant chunks
            # Build metadata filter if specified
            filter_metadata = None
            if request.filter_tags or request.filter_source:
                filter_metadata = {}
                if request.filter_tags:
                    filter_metadata["tags"] = {"$in": request.filter_tags}
                if request.filter_source:
                    filter_metadata["source"] = request.filter_source
            
            search_results = await self.vectorstore.search(
                query_embedding=query_embedding,
                collection_name=request.collection_name,
                top_k=request.top_k,
                filter_metadata=filter_metadata
            )
            
            retrieval_time = (time.time() - retrieval_start) * 1000
            logger.info(f"Retrieved {len(search_results)} chunks in {retrieval_time:.2f}ms")
            
            # Step 3: Build context from retrieved chunks
            context = self._build_context(search_results)
            
            if not context:
                return AskResponse(
                    question=request.question,
                    answer="I couldn't find any relevant documents to answer your question. Please make sure documents have been uploaded to the system.",
                    sources=[],
                    model_used=self.llm.get_provider_name(),
                    retrieval_time_ms=retrieval_time,
                    generation_time_ms=0,
                    total_time_ms=(time.time() - total_start) * 1000,
                    chunks_retrieved=0
                )
            
            # Step 4: Generate answer with LLM
            generation_start = time.time()
            
            user_prompt = RAG_USER_PROMPT_TEMPLATE.format(
                context=context,
                question=request.question
            )
            
            answer = await self.llm.answer_question(
                question=user_prompt,
                context=RAG_SYSTEM_PROMPT
            )
            
            generation_time = (time.time() - generation_start) * 1000
            logger.info(f"Generated answer in {generation_time:.2f}ms")
            
            # Step 5: Build source references
            sources = []
            if request.include_sources:
                sources = self._build_source_references(search_results)
            
            total_time = (time.time() - total_start) * 1000
            
            return AskResponse(
                question=request.question,
                answer=answer,
                sources=sources,
                model_used=self.llm.get_provider_name(),
                retrieval_time_ms=retrieval_time,
                generation_time_ms=generation_time,
                total_time_ms=total_time,
                chunks_retrieved=len(search_results)
            )
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}", exc_info=True)
            raise
    
    def _build_context(self, search_results: List[SearchResult]) -> str:
        """Build context string from search results."""
        if not search_results:
            return ""
        
        context_parts = []
        
        for result in search_results:
            doc = result.document
            metadata = doc.metadata
            
            filename = metadata.get('filename', 'Unknown')
            page = metadata.get('page_number', 'N/A')
            
            context_parts.append(
                f"[Document: {filename}, Page: {page}]\n{doc.content}"
            )
        
        return "\n\n---\n\n".join(context_parts)
    
    def _build_source_references(
        self, 
        search_results: List[SearchResult]
    ) -> List[SourceReference]:
        """Build source reference objects from search results."""
        sources = []
        
        for result in search_results:
            doc = result.document
            metadata = doc.metadata
            
            # Create preview (first 200 chars)
            preview = doc.content[:200]
            if len(doc.content) > 200:
                preview += "..."
            
            source = SourceReference(
                document_id=metadata.get('document_id', ''),
                filename=metadata.get('filename', 'Unknown'),
                chunk_id=doc.id,
                content_preview=preview,
                relevance_score=result.score,
                page_number=metadata.get('page_number')
            )
            sources.append(source)
        
        return sources
    
    async def get_collection_stats(
        self, 
        collection_name: str = "default"
    ) -> CollectionStats:
        """Get statistics about a collection."""
        if not self._initialized:
            await self.initialize()
        
        stats = await self.vectorstore.get_collection_stats(collection_name)
        
        return CollectionStats(
            collection_name=collection_name,
            document_count=0,  # Would need separate metadata store
            chunk_count=stats.get('count', 0),
            last_updated=datetime.now()
        )
    
    async def list_collections(self) -> List[str]:
        """List all available collections."""
        if not self._initialized:
            await self.initialize()
        
        return await self.vectorstore.list_collections()
    
    async def health_check(self) -> RAGHealthResponse:
        """Check health of RAG system components."""
        try:
            if not self._initialized:
                await self.initialize()
            
            # Check vector store
            collections = await self.vectorstore.list_collections()
            vectorstore_status = {
                "status": "healthy",
                "provider": self.vectorstore.get_store_name(),
                "collections": len(collections)
            }
            
            # Check embedding service
            embedding_status = {
                "status": "healthy",
                "provider": self.embedding.get_provider_name(),
                "model": self.embedding.get_model_name(),
                "dimension": self.embedding.get_embedding_dimension()
            }
            
            return RAGHealthResponse(
                status="healthy",
                vectorstore=vectorstore_status,
                embedding=embedding_status,
                collections=collections
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return RAGHealthResponse(
                status="unhealthy",
                vectorstore={"status": "error", "message": str(e)},
                embedding={"status": "unknown"},
                collections=[]
            )
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the RAG service configuration."""
        return {
            "initialized": self._initialized,
            "vectorstore": self.vectorstore.get_store_name() if self.vectorstore else None,
            "embedding_provider": self.embedding.get_provider_name() if self.embedding else None,
            "llm_provider": self.llm.get_provider_name() if self.llm else None
        }


# Singleton instance for reuse
_rag_service: Optional[RAGService] = None


async def get_rag_service() -> RAGService:
    """Get or create RAG service instance."""
    global _rag_service
    
    if _rag_service is None:
        _rag_service = RAGService()
        await _rag_service.initialize()
    
    return _rag_service