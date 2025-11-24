"""
Week 2 Comprehensive Test Suite
Tests for NewsAPI, Bedrock, and Email adapters
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock


# ==================== NewsAPI Adapter Tests ====================

class TestNewsAPIAdapter:
    """Test NewsAPI source adapter"""
    
    @pytest.fixture
    def adapter(self):
        """Create NewsAPI adapter for testing"""
        from app.adapters.source.newsapi import NewsAPIAdapter
        return NewsAPIAdapter()
    
    @pytest.mark.asyncio
    async def test_fetch_basic(self, adapter):
        """Test basic fetch functionality"""
        results = await adapter.fetch(
            query="Apple",
            max_results=5,
            date_from=datetime.now() - timedelta(days=7),
            date_to=datetime.now()
        )
        
        assert isinstance(results, list)
        assert len(results) <= 5
        
        if len(results) > 0:
            article = results[0]
            assert "id" in article
            assert "title" in article
            assert "content" in article
            assert "source" in article
            assert article["source"] == "NewsAPI"
    
    @pytest.mark.asyncio
    async def test_fetch_with_or_operator(self, adapter):
        """Test query with OR operator"""
        results = await adapter.fetch(
            query="TSMC OR NVIDIA",
            max_results=10
        )
        
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_standardized_format(self, adapter):
        """Test that returned data follows standardized format"""
        results = await adapter.fetch(
            query="technology",
            max_results=1
        )
        
        if len(results) > 0:
            article = results[0]
            
            # Check required fields
            required_fields = [
                "id", "title", "content", "summary",
                "authors", "published_date", "url",
                "source", "metadata"
            ]
            
            for field in required_fields:
                assert field in article, f"Missing field: {field}"
            
            # Check metadata structure
            metadata = article["metadata"]
            assert "source_name" in metadata
            assert "image_url" in metadata
    
    def test_get_source_name(self, adapter):
        """Test source name retrieval"""
        assert adapter.get_source_name() == "NewsAPI"


class TestNewsAPIHelpers:
    """Test NewsAPI helper functions"""
    
    def test_filter_by_companies(self):
        """Test company filtering"""
        from app.adapters.source.newsapi import filter_by_companies
        
        articles = [
            {"title": "TSMC announces new chip", "content": "..."},
            {"title": "Apple releases iPhone", "content": "..."},
            {"title": "Microsoft updates Windows", "content": "..."}
        ]
        
        filtered = filter_by_companies(articles, ["TSMC", "Apple"])
        assert len(filtered) == 2
    
    def test_categorize_by_sentiment(self):
        """Test sentiment categorization"""
        from app.adapters.source.newsapi import categorize_by_sentiment_keywords
        
        articles = [
            {"title": "Stock prices surge", "summary": "Market gains"},
            {"title": "Company faces crisis", "summary": "Prices fall"},
            {"title": "Regular update", "summary": "No change"}
        ]
        
        categorized = categorize_by_sentiment_keywords(articles)
        
        assert "positive" in categorized
        assert "negative" in categorized
        assert "neutral" in categorized
        assert len(categorized["positive"]) >= 1
        assert len(categorized["negative"]) >= 1


# ==================== Bedrock Adapter Tests ====================

class TestAWSBedrockAdapter:
    """Test AWS Bedrock LLM adapter"""
    
    @pytest.fixture
    def adapter(self):
        """Create Bedrock adapter for testing"""
        # Mock boto3 if not installed
        with patch('app.adapters.llm.bedrock.BOTO3_AVAILABLE', True):
            with patch('app.adapters.llm.bedrock.boto3') as mock_boto3:
                from app.adapters.llm.bedrock import AWSBedrockAdapter
                return AWSBedrockAdapter()
    
    @pytest.mark.asyncio
    async def test_summarize(self, adapter):
        """Test summarization"""
        with patch.object(adapter.client, 'invoke_model') as mock_invoke:
            # Mock response
            mock_response = {
                'body': Mock(read=lambda: b'{"content": [{"text": "Test summary"}]}')
            }
            mock_invoke.return_value = mock_response
            
            result = await adapter.summarize("Long text to summarize")
            
            assert isinstance(result, str)
            assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment(self, adapter):
        """Test sentiment analysis"""
        with patch.object(adapter.client, 'invoke_model') as mock_invoke:
            # Mock JSON response
            mock_response = {
                'body': Mock(read=lambda: b'{"content": [{"text": "{\\"sentiment\\": \\"positive\\", \\"confidence\\": 0.85, \\"reasoning\\": \\"Test\\"}"}]}')
            }
            mock_invoke.return_value = mock_response
            
            result = await adapter.analyze_sentiment("Great news!")
            
            assert isinstance(result, dict)
            assert "sentiment" in result
            assert "confidence" in result
    
    def test_get_provider_name(self, adapter):
        """Test provider name"""
        assert adapter.get_provider_name() == "AWS Bedrock"


class TestBedrockHelpers:
    """Test Bedrock helper functions"""
    
    def test_test_connection(self):
        """Test connection testing function"""
        from app.adapters.llm.bedrock import test_bedrock_connection
        
        with patch('app.adapters.llm.bedrock.boto3') as mock_boto3:
            mock_client = Mock()
            mock_client.list_foundation_models.return_value = {
                'modelSummaries': [{'modelId': 'test-model'}]
            }
            mock_boto3.client.return_value = mock_client
            
            result = test_bedrock_connection()
            # Will fail without real credentials, but tests the code path
            assert isinstance(result, bool)


# ==================== Email Adapter Tests ====================

class TestEmailAdapter:
    """Test Email output adapter"""
    
    @pytest.fixture
    def adapter(self):
        """Create Email adapter for testing"""
        with patch('app.adapters.output.email.SMTP_AVAILABLE', True):
            from app.adapters.output.email import EmailAdapter
            return EmailAdapter()
    
    @pytest.mark.asyncio
    async def test_send_basic(self, adapter):
        """Test basic email sending"""
        with patch('app.adapters.output.email.aiosmtplib.SMTP') as mock_smtp:
            # Mock SMTP client
            mock_client = AsyncMock()
            mock_smtp.return_value.__aenter__.return_value = mock_client
            
            result = await adapter.send(
                content="Test report content",
                metadata={"title": "Test Report"}
            )
            
            assert result["status"] == "success"
            assert "recipients" in result
    
    @pytest.mark.asyncio
    async def test_send_with_html(self, adapter):
        """Test HTML email"""
        with patch('app.adapters.output.email.aiosmtplib.SMTP') as mock_smtp:
            mock_client = AsyncMock()
            mock_smtp.return_value.__aenter__.return_value = mock_client
            
            result = await adapter.send(
                content="# Test Report\n\nThis is **bold**",
                metadata={
                    "title": "HTML Test",
                    "format": "html"
                }
            )
            
            assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_send_with_priority(self, adapter):
        """Test email with priority"""
        with patch('app.adapters.output.email.aiosmtplib.SMTP') as mock_smtp:
            mock_client = AsyncMock()
            mock_smtp.return_value.__aenter__.return_value = mock_client
            
            result = await adapter.send(
                content="Urgent report",
                metadata={
                    "title": "Urgent Report",
                    "priority": "high"
                }
            )
            
            assert result["status"] == "success"
    
    def test_get_output_name(self, adapter):
        """Test output name"""
        assert adapter.get_output_name() == "Email"
    
    def test_parse_recipients(self, adapter):
        """Test recipient parsing"""
        recipients = adapter._parse_recipients({
            "recipients": ["user1@example.com", "user2@example.com"]
        })
        
        assert len(recipients) >= 2
        assert all("@" in email for email in recipients)
    
    def test_markdown_to_html(self, adapter):
        """Test markdown conversion"""
        content = "# Header\n\nThis is **bold** text"
        html = adapter._markdown_to_html(content)
        
        assert "<h1>" in html
        assert "<strong>" in html
        assert "<body>" in html


# ==================== Integration Tests ====================

class TestWeek2Integration:
    """Integration tests for Week 2 adapters"""
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires real API keys")
    async def test_newsapi_to_console_pipeline(self):
        """Test NewsAPI -> Console pipeline"""
        from app.adapters.source.newsapi import NewsAPIAdapter
        from app.adapters.output.console import ConsoleOutputAdapter
        
        source = NewsAPIAdapter()
        output = ConsoleOutputAdapter()
        
        # Fetch news
        articles = await source.fetch(
            query="technology",
            max_results=3
        )
        
        assert len(articles) > 0
        
        # Format for output
        content = "\n\n".join([
            f"**{article['title']}**\n{article['summary']}"
            for article in articles
        ])
        
        # Output
        result = await output.send(
            content=content,
            metadata={"title": "Tech News"}
        )
        
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires AWS credentials")
    async def test_bedrock_summarization(self):
        """Test Bedrock summarization"""
        from app.adapters.llm.bedrock import AWSBedrockAdapter
        
        adapter = AWSBedrockAdapter()
        
        summary = await adapter.summarize(
            "This is a long article about AI and machine learning. "
            "It discusses various applications and future directions."
        )
        
        assert isinstance(summary, str)
        assert len(summary) > 0


# ==================== Performance Tests ====================

class TestWeek2Performance:
    """Performance tests for Week 2 features"""
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Performance test")
    async def test_newsapi_response_time(self):
        """Test NewsAPI response time"""
        import time
        from app.adapters.source.newsapi import NewsAPIAdapter
        
        adapter = NewsAPIAdapter()
        
        start = time.time()
        await adapter.fetch(query="test", max_results=5)
        elapsed = time.time() - start
        
        # Should complete within 5 seconds
        assert elapsed < 5.0
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Performance test")
    async def test_bedrock_response_time(self):
        """Test Bedrock response time"""
        import time
        from app.adapters.llm.bedrock import AWSBedrockAdapter
        
        adapter = AWSBedrockAdapter()
        
        start = time.time()
        await adapter.summarize("Short text")
        elapsed = time.time() - start
        
        # Should complete within 10 seconds
        assert elapsed < 10.0


# ==================== Error Handling Tests ====================

class TestWeek2ErrorHandling:
    """Error handling tests"""
    
    @pytest.mark.asyncio
    async def test_newsapi_invalid_api_key(self):
        """Test NewsAPI with invalid key"""
        with patch('app.config.settings.NEWSAPI_KEY', 'invalid_key'):
            from app.adapters.source.newsapi import NewsAPIAdapter
            
            adapter = NewsAPIAdapter()
            
            # Should handle error gracefully
            results = await adapter.fetch(query="test")
            assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_email_invalid_smtp(self):
        """Test Email with invalid SMTP settings"""
        with patch('app.config.settings.SMTP_HOST', 'invalid.smtp.server'):
            from app.adapters.output.email import EmailAdapter
            
            adapter = EmailAdapter()
            
            result = await adapter.send("Test")
            assert result["status"] == "failed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])