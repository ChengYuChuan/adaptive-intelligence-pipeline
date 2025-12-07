-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schema
CREATE SCHEMA IF NOT EXISTS aip;

-- Create collections table
CREATE TABLE IF NOT EXISTS aip.collections (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    document_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create document embeddings table
CREATE TABLE IF NOT EXISTS aip.document_embeddings (
    id VARCHAR(255) PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI text-embedding-3-small dimension
    metadata JSONB DEFAULT '{}'::jsonb,
    collection_name VARCHAR(255) NOT NULL DEFAULT 'default',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create HNSW index for fast approximate nearest neighbor search
CREATE INDEX IF NOT EXISTS idx_embedding_hnsw 
ON aip.document_embeddings 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Create index on collection_name for filtering
CREATE INDEX IF NOT EXISTS idx_collection_name 
ON aip.document_embeddings (collection_name);

-- Create GIN index on metadata for JSON queries
CREATE INDEX IF NOT EXISTS idx_metadata 
ON aip.document_embeddings 
USING gin (metadata);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION aip.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for document_embeddings
DROP TRIGGER IF EXISTS update_document_embeddings_updated_at ON aip.document_embeddings;
CREATE TRIGGER update_document_embeddings_updated_at
    BEFORE UPDATE ON aip.document_embeddings
    FOR EACH ROW
    EXECUTE FUNCTION aip.update_updated_at_column();

-- Trigger for collections
DROP TRIGGER IF EXISTS update_collections_updated_at ON aip.collections;
CREATE TRIGGER update_collections_updated_at
    BEFORE UPDATE ON aip.collections
    FOR EACH ROW
    EXECUTE FUNCTION aip.update_updated_at_column();

-- Insert default collection
INSERT INTO aip.collections (name, description) 
VALUES ('default', 'Default document collection')
ON CONFLICT (name) DO NOTHING;

-- Grant permissions (for non-superuser access)
GRANT USAGE ON SCHEMA aip TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA aip TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA aip TO postgres;