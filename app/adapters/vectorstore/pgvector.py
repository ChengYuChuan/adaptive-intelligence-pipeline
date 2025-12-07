"""
PostgreSQL + pgvector Vector Store Adapter
Production-grade vector database for enterprise deployments
"""
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

import asyncpg
from pgvector.asyncpg import register_vector

from app.adapters.vectorstore.base import (
    BaseVectorStoreAdapter,
    Document,
    SearchResult
)
from app.config import settings

logger = logging.getLogger(__name__)


class PgVectorAdapter(BaseVectorStoreAdapter):
    """
    PostgreSQL + pgvector adapter for production deployments.
    
    Features:
    - ACID transactions
    - Horizontal scaling (read replicas)
    - Rich metadata filtering with JSONB
    - Connection pooling
    - Automatic index management
    
    Suitable for:
    - Production environments
    - High availability requirements
    - Complex queries with metadata filtering
    - Integration with existing PostgreSQL infrastructure
    
    Supported platforms:
    - AWS RDS PostgreSQL
    - Azure Database for PostgreSQL
    - GCP Cloud SQL for PostgreSQL
    - Self-hosted PostgreSQL 15+
    """
    
    # Default table and schema names
    SCHEMA_NAME = "aip"
    TABLE_NAME = "document_embeddings"
    COLLECTIONS_TABLE = "collections"
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        database: str = None,
        user: str = None,
        password: str = None,
        min_connections: int = 2,
        max_connections: int = 10
    ):
        """
        Initialize PgVector adapter.
        
        Connection parameters can be passed directly or loaded from settings.
        """
        self.host = host or getattr(settings, 'PGVECTOR_HOST', 'localhost')
        self.port = port or getattr(settings, 'PGVECTOR_PORT', 5432)
        self.database = database or getattr(settings, 'PGVECTOR_DATABASE', 'aip')
        self.user = user or getattr(settings, 'PGVECTOR_USER', 'postgres')
        self.password = password or getattr(settings, 'PGVECTOR_PASSWORD', '')
        self.min_connections = min_connections
        self.max_connections = max_connections
        
        self._pool: Optional[asyncpg.Pool] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize connection pool and ensure schema exists."""
        if self._initialized:
            return
        
        try:
            # Create connection pool
            self._pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                min_size=self.min_connections,
                max_size=self.max_connections,
                setup=self._setup_connection
            )
            
            # Verify schema exists
            async with self._pool.acquire() as conn:
                # Check if our schema and tables exist
                result = await conn.fetchval(
                    "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = $1)",
                    self.SCHEMA_NAME
                )
                
                if not result:
                    logger.warning(
                        f"Schema '{self.SCHEMA_NAME}' does not exist. "
                        "Please run the initialization SQL script."
                    )
            
            self._initialized = True
            logger.info(
                f"PgVector adapter initialized: {self.host}:{self.port}/{self.database}"
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize PgVector: {e}")
            raise
    
    async def _setup_connection(self, conn: asyncpg.Connection) -> None:
        """Set up each connection with pgvector extension."""
        await register_vector(conn)
    
    async def _ensure_initialized(self) -> None:
        """Ensure adapter is initialized before operations."""
        if not self._initialized:
            await self.initialize()
    
    async def add_documents(
        self,
        documents: List[Document],
        collection_name: str = "default"
    ) -> List[str]:
        """Add documents with embeddings to PostgreSQL."""
        await self._ensure_initialized()
        
        if not documents:
            return []
        
        # Ensure collection exists
        await self._ensure_collection(collection_name)
        
        added_ids = []
        
        async with self._pool.acquire() as conn:
            # Use a transaction for atomicity
            async with conn.transaction():
                for doc in documents:
                    try:
                        # Prepare metadata as JSON
                        metadata = doc.metadata.copy()
                        metadata['collection'] = collection_name
                        
                        # Insert document
                        await conn.execute(
                            f"""
                            INSERT INTO {self.SCHEMA_NAME}.{self.TABLE_NAME} 
                            (id, content, embedding, metadata, collection_name)
                            VALUES ($1, $2, $3, $4, $5)
                            ON CONFLICT (id) DO UPDATE SET
                                content = EXCLUDED.content,
                                embedding = EXCLUDED.embedding,
                                metadata = EXCLUDED.metadata,
                                updated_at = NOW()
                            """,
                            doc.id,
                            doc.content,
                            doc.embedding,
                            json.dumps(metadata),
                            collection_name
                        )
                        added_ids.append(doc.id)
                        
                    except Exception as e:
                        logger.error(f"Failed to add document {doc.id}: {e}")
                        raise
        
        logger.info(f"Added {len(added_ids)} documents to collection '{collection_name}'")
        return added_ids
    
    async def search(
        self,
        query_embedding: List[float],
        collection_name: str = "default",
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for similar documents using cosine similarity.
        
        Uses pgvector's <=> operator for cosine distance.
        """
        await self._ensure_initialized()
        
        # Build query
        query = f"""
            SELECT 
                id,
                content,
                metadata,
                1 - (embedding <=> $1::vector) as similarity
            FROM {self.SCHEMA_NAME}.{self.TABLE_NAME}
            WHERE collection_name = $2
        """
        
        params = [query_embedding, collection_name]
        param_idx = 3
        
        # Add metadata filters
        if filter_metadata:
            for key, value in filter_metadata.items():
                query += f" AND metadata->>'{key}' = ${param_idx}"
                params.append(str(value))
                param_idx += 1
        
        # Add ordering and limit
        query += f"""
            ORDER BY embedding <=> $1::vector
            LIMIT ${param_idx}
        """
        params.append(top_k)
        
        results = []
        
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            
            for row in rows:
                metadata = json.loads(row['metadata']) if row['metadata'] else {}
                
                doc = Document(
                    id=row['id'],
                    content=row['content'],
                    metadata=metadata,
                    embedding=None  # Don't return embeddings in search
                )
                
                results.append(SearchResult(
                    document=doc,
                    score=float(row['similarity'])
                ))
        
        return results
    
    async def delete_documents(
        self,
        document_ids: List[str],
        collection_name: str = "default"
    ) -> int:
        """Delete documents by ID."""
        await self._ensure_initialized()
        
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                f"""
                DELETE FROM {self.SCHEMA_NAME}.{self.TABLE_NAME}
                WHERE id = ANY($1) AND collection_name = $2
                """,
                document_ids,
                collection_name
            )
            
            # Parse "DELETE N" result
            deleted_count = int(result.split()[-1])
            
        logger.info(f"Deleted {deleted_count} documents from '{collection_name}'")
        return deleted_count
    
    async def get_document(
        self,
        document_id: str,
        collection_name: str = "default"
    ) -> Optional[Document]:
        """Get a specific document by ID."""
        await self._ensure_initialized()
        
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                f"""
                SELECT id, content, metadata, embedding
                FROM {self.SCHEMA_NAME}.{self.TABLE_NAME}
                WHERE id = $1 AND collection_name = $2
                """,
                document_id,
                collection_name
            )
            
            if not row:
                return None
            
            metadata = json.loads(row['metadata']) if row['metadata'] else {}
            
            return Document(
                id=row['id'],
                content=row['content'],
                metadata=metadata,
                embedding=list(row['embedding']) if row['embedding'] else None
            )
    
    async def list_collections(self) -> List[str]:
        """List all collection names."""
        await self._ensure_initialized()
        
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                f"""
                SELECT DISTINCT collection_name 
                FROM {self.SCHEMA_NAME}.{self.TABLE_NAME}
                ORDER BY collection_name
                """
            )
            
            return [row['collection_name'] for row in rows]
    
    async def delete_collection(self, collection_name: str) -> bool:
        """Delete all documents in a collection."""
        await self._ensure_initialized()
        
        async with self._pool.acquire() as conn:
            await conn.execute(
                f"""
                DELETE FROM {self.SCHEMA_NAME}.{self.TABLE_NAME}
                WHERE collection_name = $1
                """,
                collection_name
            )
            
            # Also remove from collections table
            await conn.execute(
                f"""
                DELETE FROM {self.SCHEMA_NAME}.{self.COLLECTIONS_TABLE}
                WHERE name = $1
                """,
                collection_name
            )
        
        logger.info(f"Deleted collection '{collection_name}'")
        return True
    
    async def get_collection_stats(
        self,
        collection_name: str = "default"
    ) -> Dict[str, Any]:
        """Get statistics about a collection."""
        await self._ensure_initialized()
        
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                f"""
                SELECT 
                    COUNT(*) as document_count,
                    pg_size_pretty(pg_total_relation_size('{self.SCHEMA_NAME}.{self.TABLE_NAME}')) as total_size
                FROM {self.SCHEMA_NAME}.{self.TABLE_NAME}
                WHERE collection_name = $1
                """,
                collection_name
            )
            
            return {
                "name": collection_name,
                "count": row['document_count'],
                "total_size": row['total_size']
            }
    
    async def _ensure_collection(self, collection_name: str) -> None:
        """Ensure a collection exists in the collections table."""
        async with self._pool.acquire() as conn:
            await conn.execute(
                f"""
                INSERT INTO {self.SCHEMA_NAME}.{self.COLLECTIONS_TABLE} (name)
                VALUES ($1)
                ON CONFLICT (name) DO NOTHING
                """,
                collection_name
            )
    
    async def vacuum_analyze(self) -> None:
        """Run VACUUM ANALYZE on the embeddings table."""
        await self._ensure_initialized()
        
        async with self._pool.acquire() as conn:
            await conn.execute(
                f"VACUUM ANALYZE {self.SCHEMA_NAME}.{self.TABLE_NAME}"
            )
        
        logger.info("VACUUM ANALYZE completed")
    
    async def reindex_vectors(self) -> None:
        """Rebuild the vector index (use during maintenance windows)."""
        await self._ensure_initialized()
        
        async with self._pool.acquire() as conn:
            await conn.execute(
                f"REINDEX INDEX {self.SCHEMA_NAME}.idx_embedding_hnsw"
            )
        
        logger.info("Vector index rebuilt")
    
    async def close(self) -> None:
        """Close the connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None
            self._initialized = False
            logger.info("PgVector connection pool closed")
    
    def get_store_name(self) -> str:
        """Get store name."""
        return "PgVector"