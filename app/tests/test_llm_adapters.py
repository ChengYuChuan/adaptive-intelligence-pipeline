"""
Tests for LLM adapters
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.adapters.llm.claude_api import ClaudeAPIAdapter
from app.adapters.llm import get_llm_adapter


class TestClaudeAPIAdapter:
    """Test ClaudeAPIAdapter functionality"""
    
    @pytest.fixture
    def adapter(self):
        """Create a ClaudeAPIAdapter instance for testing"""
        return ClaudeAPIAdapter()
    
    @pytest.mark.asyncio
    async def test_summarize(self, adapter):
        """Test summarization functionality"""
        # Mock the Anthropic client
        with patch.object(adapter.client.messages, 'create') as mock_create:
            # Setup mock response
            mock_response = Mock()
            mock_response.content = [Mock(text="這是一個測試摘要")]
            mock_create.return_value = mock_response
            
            # Call summarize
            result = await adapter.summarize("This is a test text to summarize")
            
            # Assertions
            assert isinstance(result, str)
            assert len(result) > 0
            mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment(self, adapter):
        """Test sentiment analysis functionality"""
        with patch.object(adapter.client.messages, 'create') as mock_create:
            # Setup mock response with JSON
            mock_response = Mock()
            mock_response.content = [Mock(text='{"sentiment": "positive", "confidence": 0.85, "reasoning": "Test reasoning"}')]
            mock_create.return_value = mock_response
            
            # Call analyze_sentiment
            result = await adapter.analyze_sentiment("This is great news!")
            
            # Assertions
            assert isinstance(result, dict)
            assert "sentiment" in result
            assert "confidence" in result
            assert result["sentiment"] in ["positive", "negative", "neutral"]
    
    @pytest.mark.asyncio
    async def test_extract_key_points(self, adapter):
        """Test key points extraction"""
        with patch.object(adapter.client.messages, 'create') as mock_create:
            # Setup mock response
            mock_response = Mock()
            mock_response.content = [Mock(text="- Point 1\n- Point 2\n- Point 3")]
            mock_create.return_value = mock_response
            
            # Call extract_key_points
            result = await adapter.extract_key_points("Long text to extract points from", num_points=3)
            
            # Assertions
            assert isinstance(result, list)
            assert len(result) <= 3
    
    @pytest.mark.asyncio
    async def test_generate_report_academic(self, adapter):
        """Test academic report generation"""
        with patch.object(adapter.client.messages, 'create') as mock_create:
            # Setup mock response
            mock_response = Mock()
            mock_response.content = [Mock(text="# Academic Report\n\nThis is a test report")]
            mock_create.return_value = mock_response
            
            # Call generate_report
            data = {
                "query": "machine learning",
                "items": [{"title": "Test Paper", "content": "Abstract"}],
                "count": 1
            }
            result = await adapter.generate_report(data, template="academic")
            
            # Assertions
            assert isinstance(result, str)
            assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_generate_report_financial(self, adapter):
        """Test financial report generation"""
        with patch.object(adapter.client.messages, 'create') as mock_create:
            # Setup mock response
            mock_response = Mock()
            mock_response.content = [Mock(text="# Financial Report\n\nMarket analysis")]
            mock_create.return_value = mock_response
            
            # Call generate_report
            data = {
                "query": "TSMC",
                "items": [{"title": "News Article", "content": "Company news"}],
                "count": 1
            }
            result = await adapter.generate_report(data, template="financial")
            
            # Assertions
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_get_provider_name(self, adapter):
        """Test provider name retrieval"""
        assert adapter.get_provider_name() == "ClaudeAPI"


class TestLLMAdapterFactory:
    """Test LLM adapter factory function"""
    
    def test_get_claude_adapter(self):
        """Test getting Claude adapter"""
        with patch('app.adapters.llm.settings') as mock_settings:
            mock_settings.LLM_PROVIDER = "claude"
            adapter = get_llm_adapter()
            assert isinstance(adapter, ClaudeAPIAdapter)
    
    def test_get_unsupported_adapter(self):
        """Test getting unsupported adapter raises error"""
        with patch('app.adapters.llm.settings') as mock_settings:
            mock_settings.LLM_PROVIDER = "unsupported"
            with pytest.raises(ValueError):
                get_llm_adapter()
    
    def test_get_bedrock_adapter_not_implemented(self):
        """Test that Bedrock adapter raises NotImplementedError"""
        with patch('app.adapters.llm.settings') as mock_settings:
            mock_settings.LLM_PROVIDER = "bedrock"
            with pytest.raises(NotImplementedError):
                get_llm_adapter()


@pytest.mark.skip(reason="Requires actual API key")
class TestClaudeAPIAdapterIntegration:
    """Integration tests for Claude API (requires API key)"""
    
    @pytest.mark.asyncio
    async def test_real_summarize(self):
        """Test real summarization with API"""
        adapter = ClaudeAPIAdapter()
        result = await adapter.summarize(
            "Artificial intelligence is transforming the world. "
            "Machine learning models are becoming more sophisticated every day.",
            max_length=100
        )
        assert isinstance(result, str)
        assert len(result) > 0