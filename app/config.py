from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Environment settings - all switchable configurations are here"""
    
    # ===== LLM Settings =====
    LLM_PROVIDER: Literal["claude", "bedrock", "azure", "sagemaker"] = "claude"
    
    # Claude API
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    
    # AWS Bedrock
    AWS_REGION: str = "us-west-2"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_KEY: str = ""
    AZURE_OPENAI_DEPLOYMENT: str = ""
    AZURE_API_VERSION: str = "2024-02-15-preview"
    
    # SageMaker
    SAGEMAKER_ENDPOINT: str = ""
    
    # ===== Data Source Settings =====
    SOURCE_PROVIDER: Literal["arxiv", "newsapi", "internal"] = "arxiv"
    NEWSAPI_KEY: str = ""
    
    # ===== Output Settings =====
    OUTPUT_PROVIDER: Literal["notion", "email", "slack", "console"] = "console"
    
    # Notion
    NOTION_API_KEY: str = ""
    NOTION_DATABASE_ID: str = ""
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = ""
    EMAIL_TO: str = ""
    
    # Slack
    SLACK_WEBHOOK_URL: str = ""
    
    # ===== RAG Settings (Week 3) =====
    # Vector Store
    VECTORSTORE_PROVIDER: Literal["chroma", "pgvector", "azure"] = "chroma"
    CHROMA_PERSIST_DIR: str = "./data/vectorstore"
    
    # PgVector (Week 4)
    PGVECTOR_HOST: str = "localhost"
    PGVECTOR_PORT: int = 5432
    PGVECTOR_DATABASE: str = "aip"
    PGVECTOR_USER: str = "postgres"
    PGVECTOR_PASSWORD: str = ""
    PGVECTOR_MIN_CONNECTIONS: int = 2
    PGVECTOR_MAX_CONNECTIONS: int = 10
    
    # Embedding
    EMBEDDING_PROVIDER: Literal["openai", "bedrock", "local"] = "openai"
    OPENAI_API_KEY: str = ""
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Bedrock Embedding (Week 4)
    BEDROCK_EMBEDDING_MODEL: str = "amazon.titan-embed-text-v2:0"
    
    # Document Processing
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MAX_FILE_SIZE_MB: int = 50
    
    # ===== Logging & Monitoring (Week 4) =====
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "console"
    
    # Metrics
    METRICS_ENABLED: bool = True
    METRICS_PATH: str = "/metrics"
    
    # ===== General Settings =====
    DEBUG: bool = False
    APP_ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()