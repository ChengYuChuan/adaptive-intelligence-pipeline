import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.adapters.llm.claude_api import ClaudeAPIAdapter


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client"""
    with patch('app.adapters.llm.claude_api.anthropic.Anthropic') as mock:
        client = Mock()
        mock.return_value = client
        
        # Mock response
        response = Mock()
        response.content = [Mock(text="這是測試回應")]
        client.messages.create.return_value = response
        
        yield client


@pytest.mark.asyncio
async def test_claude_adapter_summarize(mock_anthropic_client):
    """測試 Claude API 摘要功能"""
    adapter = ClaudeAPIAdapter()
    
    result = await adapter.summarize("這是一篇很長的文章...")
    
    assert isinstance(result, str)
    assert len(result) > 0
    mock_anthropic_client.messages.create.assert_called_once()


@pytest.mark.asyncio
async def test_claude_adapter_sentiment(mock_anthropic_client):
    """測試 Claude API 情緒分析"""
    # Mock JSON 回應
    mock_anthropic_client.messages.create.return_value.content[0].text = '''
    {
        "sentiment": "positive",
        "confidence": 0.85,
        "reasoning": "文本表達積極情緒"
    }
    '''
    
    adapter = ClaudeAPIAdapter()
    result = await adapter.analyze_sentiment("這是一個很棒的產品！")
    
    assert result["sentiment"] in ["positive", "negative", "neutral"]
    assert 0 <= result["confidence"] <= 1


@pytest.mark.asyncio
async def test_claude_adapter_key_points(mock_anthropic_client):
    """測試 Claude API 關鍵要點提取"""
    mock_anthropic_client.messages.create.return_value.content[0].text = '''
    - 要點一
    - 要點二
    - 要點三
    '''
    
    adapter = ClaudeAPIAdapter()
    result = await adapter.extract_key_points("文章內容...", num_points=3)
    
    assert isinstance(result, list)
    assert len(result) <= 3


def test_get_provider_name():
    """測試取得 provider 名稱"""
    adapter = ClaudeAPIAdapter()
    assert adapter.get_provider_name() == "ClaudeAPI"
