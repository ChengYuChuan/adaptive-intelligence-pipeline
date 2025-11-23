import anthropic
from typing import List, Dict, Any
from app.adapters.llm.base import BaseLLMAdapter
from app.config import settings
import json


class ClaudeAPIAdapter(BaseLLMAdapter):
    """
    Adapter for Anthropic Claude API
    Suitable for: Development, Demo, Quick prototyping
    """
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_MODEL
        self.max_tokens = 2048
    
    async def _call_claude(self, system_prompt: str, user_message: str) -> str:
        """Internal method to call Claude API"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": user_message
            }]
        )
        return response.content[0].text
    
    async def summarize(self, text: str, max_length: int = 300) -> str:
        system_prompt = f"""You are a professional summarization assistant.
Provide a clear and accurate summary in Traditional Chinese, not exceeding {max_length} characters.
The summary should preserve the most important information and key details."""
        
        user_message = f"Please summarize the following content:\n\n{text}"
        
        return await self._call_claude(system_prompt, user_message)
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        system_prompt = """You are a sentiment analysis expert.
Analyze the sentiment of the text and respond in JSON format:
{
  "sentiment": "positive" | "negative" | "neutral",
  "confidence": 0.0-1.0,
  "reasoning": "Brief explanation of why this sentiment"
}

Respond with only JSON, no other text."""
        
        user_message = f"Please analyze the sentiment of the following text:\n\n{text}"
        
        response = await self._call_claude(system_prompt, user_message)
        
        # Parse JSON response
        try:
            # Remove possible markdown markers
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            return json.loads(response.strip())
        except json.JSONDecodeError:
            # Return default structure if parsing fails
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "reasoning": "Failed to parse response"
            }
    
    async def extract_key_points(self, text: str, num_points: int = 5) -> List[str]:
        system_prompt = f"""You are a content analysis expert.
Extract {num_points} most important key points from the text.
Express each point in one sentence, in Traditional Chinese.
Respond in list format, each line starting with "- "."""
        
        user_message = f"Please extract key points from the following content:\n\n{text}"
        
        response = await self._call_claude(system_prompt, user_message)
        
        # Parse list
        points = [
            line.strip("- ").strip() 
            for line in response.split("\n") 
            if line.strip().startswith("-")
        ]
        
        return points[:num_points]
    
    async def generate_report(
        self, 
        data: Dict[str, Any], 
        template: str,
        language: str = "zh-TW"
    ) -> str:
        # Select system prompt based on template
        if template == "academic":
            system_prompt = """You are an academic paper analysis expert.
Generate a professional academic literature summary report, including:
1. Overall trends summary
2. Key papers list (title, authors, core contributions)
3. Key findings
4. Recommended reading

Use Traditional Chinese and maintain an academic professional tone."""
        
        elif template == "financial":
            system_prompt = """You are a financial analyst.
Generate an investment analysis report, including:
1. Market dynamics summary
2. Key news and impacts
3. Sentiment analysis (bullish/bearish)
4. Related company movements
5. Points to watch

Use Traditional Chinese and maintain a professional objective tone."""
        
        else:
            system_prompt = "You are a professional analyst. Generate a comprehensive report based on the provided data. Use Traditional Chinese."
        
        # Convert data to JSON string
        data_str = json.dumps(data, ensure_ascii=False, indent=2)
        user_message = f"Please generate a report based on the following data:\n\n{data_str}"
        
        return await self._call_claude(system_prompt, user_message)
    
    async def answer_question(self, question: str, context: str) -> str:
        system_prompt = """You are a professional Q&A assistant.
Answer questions based on the provided context, maintaining objectivity and accuracy.
If there is insufficient information in the context, clearly state so.
Answer in Traditional Chinese."""
        
        user_message = f"""Context:
{context}

Question: {question}"""
        
        return await self._call_claude(system_prompt, user_message)
    
    def get_provider_name(self) -> str:
        """Return the provider name"""
        return "ClaudeAPI"