from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseLLMAdapter(ABC):
    """
    Abstract base class for all LLM adapters
    All LLM providers must implement this interface
    """
    
    @abstractmethod
    async def summarize(self, text: str, max_length: int = 300) -> str:
        """
        Generate a summary of the given text
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary in characters
            
        Returns:
            Summarized text
        """
        pass
    
    @abstractmethod
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of the text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with keys:
                - sentiment: "positive" | "negative" | "neutral"
                - confidence: float between 0.0 and 1.0
                - reasoning: str explaining the sentiment
        """
        pass
    
    @abstractmethod
    async def extract_key_points(self, text: str, num_points: int = 5) -> List[str]:
        """
        Extract key points from the text
        
        Args:
            text: Text to extract key points from
            num_points: Number of key points to extract
            
        Returns:
            List of key points as strings
        """
        pass
    
    @abstractmethod
    async def generate_report(
        self, 
        data: Dict[str, Any], 
        template: str,
        language: str = "zh-TW"
    ) -> str:
        """
        Generate a comprehensive report from structured data
        
        Args:
            data: Structured data to generate report from
            template: Report template type ("academic" or "financial")
            language: Output language (default: Traditional Chinese)
            
        Returns:
            Generated report as formatted text
        """
        pass
    
    @abstractmethod
    async def answer_question(self, question: str, context: str) -> str:
        """
        Answer a question based on given context
        
        Args:
            question: Question to answer
            context: Context information
            
        Returns:
            Answer to the question
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of this LLM provider
        
        Returns:
            Provider name (e.g., "ClaudeAPI", "AWSBedrock")
        """
        pass