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
    
    # NewsAPI
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
    
    # ===== General Settings =====
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    # ===== RAG Settings (Week 3) =====
    # Vector Store
    VECTORSTORE_PROVIDER: Literal["chroma", "pgvector", "azure"] = "chroma"
    CHROMA_PERSIST_DIR: str = "./data/vectorstore"
    
    # Embedding
    EMBEDDING_PROVIDER: Literal["openai", "bedrock", "local"] = "openai"
    OPENAI_API_KEY: str = ""
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Document Processing
    CHUNK_SIZE: int = 1000  # Characters per chunk
    CHUNK_OVERLAP: int = 200  # Overlap between chunks
    MAX_FILE_SIZE_MB: int = 50  # Maximum upload file size


# Global settings instance
settings = Settings()