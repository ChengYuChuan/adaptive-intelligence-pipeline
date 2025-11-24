"""
Tests for source adapters
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from app.adapters.source.arxiv import ArXivAdapter
from app.adapters.source import get_source_adapter


class TestArXivAdapter:
    """Test ArXivAdapter functionality"""
    
    @pytest.fixture
    def adapter(self):
        """Create an ArXivAdapter instance for testing"""
        return ArXivAdapter()
    
    @pytest.mark.asyncio
    async def test_fetch_basic(self, adapter):
        """Test basic fetch functionality"""
        # This test will make actual API calls to arXiv
        # You might want to mock this in CI/CD
        results = await adapter.fetch(
            query="machine learning",
            max_results=2,
            date_from=datetime.now() - timedelta(days=30),
            date_to=datetime.now()
        )
        
        # Basic assertions
        assert isinstance(results, list)
        # Results might be empty depending on date range
        if len(results) > 0:
            assert "id" in results[0]
            assert "title" in results[0]
            assert "content" in results[0]
            assert "authors" in results[0]
            assert "source" in results[0]
            assert results[0]["source"] == "arXiv"
    
    @pytest.mark.asyncio
    async def test_fetch_with_date_filter(self, adapter):
        """Test fetch with date filtering"""
        date_from = datetime.now() - timedelta(days=7)
        date_to = datetime.now()
        
        results = await adapter.fetch(
            query="cs.LG",
            max_results=5,
            date_from=date_from,
            date_to=date_to
        )
        
        assert isinstance(results, list)
        
        # Verify dates are within range
        for result in results:
            published = datetime.fromisoformat(result["published_date"])
            assert date_from <= published.replace(tzinfo=None) <= date_to
    
    def test_get_source_name(self, adapter):
        """Test source name retrieval"""
        assert adapter.get_source_name() == "arXiv"
    
    @pytest.mark.asyncio
    async def test_standardized_format(self, adapter):
        """Test that returned data follows standardized format"""
        results = await adapter.fetch(
            query="attention mechanism",
            max_results=1
        )
        
        if len(results) > 0:
            result = results[0]
            # Check all required fields are present
            required_fields = [
                "id", "title", "content", "summary", 
                "authors", "published_date", "url", 
                "source", "metadata"
            ]
            for field in required_fields:
                assert field in result, f"Missing field: {field}"
            
            # Check metadata structure
            assert isinstance(result["metadata"], dict)
            assert "categories" in result["metadata"]
            assert "pdf_url" in result["metadata"]


class TestSourceAdapterFactory:
    """Test source adapter factory function"""
    
    def test_get_arxiv_adapter(self):
        """Test getting arXiv adapter"""
        with patch('app.adapters.source.settings') as mock_settings:
            mock_settings.SOURCE_PROVIDER = "arxiv"
            adapter = get_source_adapter()
            assert isinstance(adapter, ArXivAdapter)
    
    def test_get_unsupported_adapter(self):
        """Test getting unsupported adapter raises error"""
        with patch('app.adapters.source.settings') as mock_settings:
            mock_settings.SOURCE_PROVIDER = "unsupported"
            with pytest.raises(ValueError):
                get_source_adapter()
    
    def test_get_newsapi_adapter_not_implemented(self):
        """Test that NewsAPI adapter raises NotImplementedError"""
        with patch('app.adapters.source.settings') as mock_settings:
            mock_settings.SOURCE_PROVIDER = "newsapi"
            with pytest.raises(NotImplementedError):
                get_source_adapter()


@pytest.mark.skip(reason="Slow integration test")
class TestArXivAdapterIntegration:
    """Integration tests for arXiv adapter"""
    
    @pytest.mark.asyncio
    async def test_large_result_set(self):
        """Test fetching larger result set"""
        adapter = ArXivAdapter()
        results = await adapter.fetch(
            query="transformer",
            max_results=20
        )
        
        assert isinstance(results, list)
        assert len(results) <= 20
    
    @pytest.mark.asyncio
    async def test_specific_category(self):
        """Test searching specific arXiv category"""
        adapter = ArXivAdapter()
        results = await adapter.fetch(
            query="cat:cs.LG",
            max_results=5
        )
        
        assert isinstance(results, list)
        for result in results:
            # Should contain cs.LG category
            categories = result["metadata"].get("categories", [])
            assert any("cs.LG" in cat for cat in categories)