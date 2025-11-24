"""
Tests for output adapters
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from app.adapters.output.console import ConsoleOutputAdapter
from app.adapters.output.notion import NotionAdapter
from app.adapters.output import get_output_adapter


class TestConsoleOutputAdapter:
    """Test ConsoleOutputAdapter functionality"""
    
    @pytest.fixture
    def adapter(self):
        """Create a ConsoleOutputAdapter instance for testing"""
        return ConsoleOutputAdapter()
    
    @pytest.mark.asyncio
    async def test_send_basic(self, adapter, capsys):
        """Test basic send functionality"""
        content = "Test report content"
        metadata = {"title": "Test Report", "tags": ["test"]}
        
        result = await adapter.send(content, metadata)
        
        # Check result structure
        assert result["status"] == "success"
        assert "message" in result
        assert "timestamp" in result
        assert result["url"] is None
        
        # Check console output
        captured = capsys.readouterr()
        assert "Test Report" in captured.out
        assert "Test report content" in captured.out
    
    @pytest.mark.asyncio
    async def test_send_without_metadata(self, adapter, capsys):
        """Test send without metadata"""
        content = "Simple content"
        
        result = await adapter.send(content)
        
        assert result["status"] == "success"
        
        captured = capsys.readouterr()
        assert "Simple content" in captured.out
    
    def test_get_output_name(self, adapter):
        """Test output name retrieval"""
        assert adapter.get_output_name() == "Console"


class TestNotionAdapter:
    """Test NotionAdapter functionality"""
    
    @pytest.fixture
    def adapter(self):
        """Create a NotionAdapter instance for testing"""
        return NotionAdapter()
    
    @pytest.mark.asyncio
    async def test_send_without_config(self, adapter):
        """Test send when API key is not configured"""
        with patch.object(adapter, 'api_key', ''):
            result = await adapter.send("Test content")
            
            assert result["status"] == "failed"
            assert "not configured" in result["message"].lower()
    
    @pytest.mark.asyncio
    async def test_send_success(self, adapter):
        """Test successful send to Notion"""
        with patch.object(adapter, 'api_key', 'test_key'), \
             patch.object(adapter, 'database_id', 'test_db_id'), \
             patch('httpx.AsyncClient') as mock_client:
            
            # Mock HTTP response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"url": "https://notion.so/page123"}
            
            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post
            
            # Call send
            content = "Test report"
            metadata = {"title": "Test Title", "tags": ["test", "example"]}
            result = await adapter.send(content, metadata)
            
            # Assertions
            assert result["status"] == "success"
            assert result["url"] == "https://notion.so/page123"
            mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_api_error(self, adapter):
        """Test handling of API errors"""
        with patch.object(adapter, 'api_key', 'test_key'), \
             patch.object(adapter, 'database_id', 'test_db_id'), \
             patch('httpx.AsyncClient') as mock_client:
            
            # Mock HTTP error response
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.text = "Bad Request"
            
            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post
            
            # Call send
            result = await adapter.send("Test content")
            
            # Assertions
            assert result["status"] == "failed"
            assert "400" in result["message"]
    
    @pytest.mark.asyncio
    async def test_send_exception(self, adapter):
        """Test handling of exceptions"""
        with patch.object(adapter, 'api_key', 'test_key'), \
             patch.object(adapter, 'database_id', 'test_db_id'), \
             patch('httpx.AsyncClient') as mock_client:
            
            # Mock exception
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=Exception("Network error")
            )
            
            # Call send
            result = await adapter.send("Test content")
            
            # Assertions
            assert result["status"] == "failed"
            assert "Network error" in result["message"]
    
    def test_get_output_name(self, adapter):
        """Test output name retrieval"""
        assert adapter.get_output_name() == "Notion"


class TestOutputAdapterFactory:
    """Test output adapter factory function"""
    
    def test_get_console_adapter(self):
        """Test getting console adapter"""
        with patch('app.adapters.output.settings') as mock_settings:
            mock_settings.OUTPUT_PROVIDER = "console"
            adapter = get_output_adapter()
            assert isinstance(adapter, ConsoleOutputAdapter)
    
    def test_get_notion_adapter(self):
        """Test getting Notion adapter"""
        with patch('app.adapters.output.settings') as mock_settings:
            mock_settings.OUTPUT_PROVIDER = "notion"
            adapter = get_output_adapter()
            assert isinstance(adapter, NotionAdapter)
    
    def test_get_unsupported_adapter(self):
        """Test getting unsupported adapter raises error"""
        with patch('app.adapters.output.settings') as mock_settings:
            mock_settings.OUTPUT_PROVIDER = "unsupported"
            with pytest.raises(ValueError):
                get_output_adapter()
    
    def test_get_email_adapter_not_implemented(self):
        """Test that Email adapter raises NotImplementedError"""
        with patch('app.adapters.output.settings') as mock_settings:
            mock_settings.OUTPUT_PROVIDER = "email"
            with pytest.raises(NotImplementedError):
                get_output_adapter()


@pytest.mark.skip(reason="Requires Notion API key")
class TestNotionAdapterIntegration:
    """Integration tests for Notion adapter (requires API key)"""
    
    @pytest.mark.asyncio
    async def test_real_notion_send(self):
        """Test real Notion API integration"""
        # This requires actual Notion credentials
        adapter = NotionAdapter()
        
        content = "Integration test report content"
        metadata = {
            "title": "Integration Test",
            "tags": ["test", "integration"]
        }
        
        result = await adapter.send(content, metadata)
        
        assert result["status"] == "success"
        assert result["url"] is not None