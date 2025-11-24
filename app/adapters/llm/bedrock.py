"""
AWS Bedrock LLM Adapter - Week 2 Implementation
Enterprise-grade LLM service with data privacy guarantees
"""
import json
import logging
from typing import List, Dict, Any
from app.adapters.llm.base import BaseLLMAdapter
from app.config import settings

# Import boto3 only if needed (will be installed in Week 2)
try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    logging.warning("boto3 not installed. Install with: pip install boto3")

logger = logging.getLogger(__name__)


class AWSBedrockAdapter(BaseLLMAdapter):
    """
    AWS Bedrock adapter for Claude models
    
    Advantages:
    - Enterprise-grade security and compliance
    - Data doesn't leave your AWS account
    - No rate limits (pay per use)
    - Audit logging with CloudTrail
    - VPC deployment option
    
    Suitable for:
    - Enterprise deployments
    - Regulated industries (finance, healthcare)
    - High-volume production use
    
    Setup:
    1. Enable Bedrock in AWS Console
    2. Request model access (Claude 3)
    3. Configure IAM permissions
    4. Set AWS credentials in environment
    """
    
    def __init__(self):
        """Initialize AWS Bedrock client"""
        if not BOTO3_AVAILABLE:
            raise ImportError(
                "boto3 is required for Bedrock adapter. "
                "Install with: pip install boto3"
            )
        
        # Initialize boto3 client
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None
        )
        
        # Model configuration
        self.model_id = settings.BEDROCK_MODEL_ID
        self.max_tokens = 2048
        
        logger.info(f"Bedrock adapter initialized with model: {self.model_id}")
    
    async def _invoke_model(
        self, 
        system_prompt: str, 
        user_message: str,
        max_tokens: int = None
    ) -> str:
        """
        Internal method to invoke Bedrock model
        
        Bedrock uses different API format than Claude API
        """
        # Prepare request body (Bedrock format)
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens or self.max_tokens,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            # Optional parameters
            "temperature": 1.0,
            "top_p": 0.999,
        }
        
        try:
            # Invoke model
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Extract text from response
            # Bedrock response format: {"content": [{"text": "..."}], ...}
            content = response_body.get('content', [])
            if content and len(content) > 0:
                return content[0].get('text', '')
            else:
                logger.error("No content in Bedrock response")
                return ""
                
        except Exception as e:
            logger.error(f"Bedrock invocation error: {e}", exc_info=True)
            raise
    
    async def summarize(self, text: str, max_length: int = 300) -> str:
        """Generate a summary of the given text"""
        system_prompt = f"""You are a professional summarization assistant.
Provide a clear and accurate summary in Traditional Chinese, not exceeding {max_length} characters.
The summary should preserve the most important information and key details."""
        
        user_message = f"Please summarize the following content:\n\n{text}"
        
        return await self._invoke_model(system_prompt, user_message)
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of the text"""
        system_prompt = """You are a sentiment analysis expert.
Analyze the sentiment of the text and respond in JSON format:
{
  "sentiment": "positive" | "negative" | "neutral",
  "confidence": 0.0-1.0,
  "reasoning": "Brief explanation"
}

Respond with only JSON, no other text."""
        
        user_message = f"Please analyze the sentiment of the following text:\n\n{text}"
        
        response = await self._invoke_model(system_prompt, user_message)
        
        # Parse JSON response
        try:
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            return json.loads(response.strip())
        except json.JSONDecodeError:
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "reasoning": "Failed to parse response"
            }
    
    async def extract_key_points(self, text: str, num_points: int = 5) -> List[str]:
        """Extract key points from text"""
        system_prompt = f"""You are a content analysis expert.
Extract {num_points} most important key points from the text.
Express each point in one sentence, in Traditional Chinese.
Respond in list format, each line starting with "- "."""
        
        user_message = f"Please extract key points from the following content:\n\n{text}"
        
        response = await self._invoke_model(system_prompt, user_message)
        
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
        """Generate a comprehensive report from structured data"""
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
        
        return await self._invoke_model(
            system_prompt, 
            user_message, 
            max_tokens=4096  # Longer reports may need more tokens
        )
    
    async def answer_question(self, question: str, context: str) -> str:
        """Answer a question based on given context"""
        system_prompt = """You are a professional Q&A assistant.
Answer questions based on the provided context, maintaining objectivity and accuracy.
If there is insufficient information in the context, clearly state so.
Answer in Traditional Chinese."""
        
        user_message = f"""Context:
{context}

Question: {question}"""
        
        return await self._invoke_model(system_prompt, user_message)
    
    def get_provider_name(self) -> str:
        """Return the provider name"""
        return "AWS Bedrock"


# Helper functions for Bedrock setup and testing

def test_bedrock_connection() -> bool:
    """
    Test if Bedrock is properly configured
    
    Returns:
        True if connection successful
    """
    try:
        client = boto3.client(
            service_name='bedrock',
            region_name=settings.AWS_REGION
        )
        
        # List available models
        response = client.list_foundation_models()
        logger.info(f"Bedrock connection successful. Found {len(response['modelSummaries'])} models")
        return True
        
    except Exception as e:
        logger.error(f"Bedrock connection failed: {e}")
        return False


def list_available_models() -> List[str]:
    """
    List all Claude models available in Bedrock
    
    Returns:
        List of model IDs
    """
    try:
        client = boto3.client(
            service_name='bedrock',
            region_name=settings.AWS_REGION
        )
        
        response = client.list_foundation_models(
            byProvider='Anthropic'
        )
        
        models = [
            model['modelId'] 
            for model in response['modelSummaries']
        ]
        
        logger.info(f"Available Claude models: {models}")
        return models
        
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        return []