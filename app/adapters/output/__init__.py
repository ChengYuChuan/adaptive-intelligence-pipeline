from app.adapters.output.base import BaseOutputAdapter
from app.config import settings


def get_output_adapter() -> BaseOutputAdapter:
    """
    Factory function to get the appropriate output adapter based on settings
    
    Returns:
        Instance of the configured output adapter
        
    Raises:
        ValueError: If the configured provider is not supported
    """
    provider = settings.OUTPUT_PROVIDER
    
    if provider == "console":
        from app.adapters.output.console import ConsoleOutputAdapter
        return ConsoleOutputAdapter()
    
    elif provider == "notion":
        from app.adapters.output.notion import NotionAdapter
        return NotionAdapter()
    
    elif provider == "email":
        # Week 2: Email implementation
        raise NotImplementedError("Email adapter coming in Week 2")
    
    elif provider == "slack":
        # Week 2: Slack implementation
        raise NotImplementedError("Slack adapter coming in Week 2")
    
    else:
        raise ValueError(
            f"Unknown output provider: {provider}. "
            f"Supported providers: console, notion, email, slack"
        )


__all__ = ["BaseOutputAdapter", "get_output_adapter"]