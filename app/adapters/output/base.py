from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseOutputAdapter(ABC):
    """
    Abstract base class for all output adapters
    All output destinations must implement this interface
    """
    
    @abstractmethod
    async def send(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Send content to the output destination
        
        Args:
            content: The content to send (usually a report or analysis)
            metadata: Optional metadata (e.g., title, tags, recipients)
            
        Returns:
            Dictionary with result information:
            {
                "status": "success" | "failed",
                "message": str,
                "url": Optional[str],  # URL where content can be accessed
                "timestamp": str (ISO format)
            }
        """
        pass
    
    @abstractmethod
    def get_output_name(self) -> str:
        """
        Get the name of this output destination
        
        Returns:
            Output name (e.g., "Email", "Notion", "Slack")
        """
        pass