from app.adapters.llm.base import BaseLLMAdapter
from app.config import settings


def get_llm_adapter() -> BaseLLMAdapter:
    """
    Factory function to get the appropriate LLM adapter based on settings
    
    Returns:
        Instance of the configured LLM adapter
        
    Raises:
        ValueError: If the configured provider is not supported
    """
    provider = settings.LLM_PROVIDER
    
    if provider == "claude":
        from app.adapters.llm.claude_api import ClaudeAPIAdapter
        return ClaudeAPIAdapter()
    
    elif provider == "bedrock":
        from app.adapters.llm.bedrock import AWSBedrockAdapter
        raise NotImplementedError("AWS Bedrock adapter coming in Week 2")
    
    elif provider == "azure":
        # Week 2: Azure OpenAI implementation
        raise NotImplementedError("Azure OpenAI adapter coming in Week 2")
    
    elif provider == "sagemaker":
        # Week 4: SageMaker implementation
        raise NotImplementedError("SageMaker adapter coming in Week 4")
    
    else:
        raise ValueError(
            f"Unknown LLM provider: {provider}. "
            f"Supported providers: claude, bedrock, azure, sagemaker"
        )


__all__ = ["BaseLLMAdapter", "get_llm_adapter"]