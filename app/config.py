from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """環境設定 - 所有可切換的設定都在這裡"""
    
    # ===== LLM 設定 =====
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
    
    # ===== 資料來源設定 =====
    SOURCE_PROVIDER: Literal["arxiv", "newsapi", "internal"] = "arxiv"
    
    # NewsAPI
    NEWSAPI_KEY: str = ""
    
    # ===== 輸出設定 =====
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
    
    # ===== 通用設定 =====
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全域設定實例
settings = Settings()
