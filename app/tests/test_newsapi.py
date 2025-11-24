#!/usr/bin/env python3
"""
Manual test for NewsAPI adapter
"""
import asyncio
import sys
from datetime import datetime, timedelta

sys.path.insert(0, '.')

from app.adapters.source.newsapi import NewsAPIAdapter

async def test_newsapi():
    print("="*60)
    print("Testing NewsAPI Adapter")
    print("="*60)
    
    # Initialize adapter
    print("\n1. Initializing NewsAPI adapter...")
    try:
        adapter = NewsAPIAdapter()
        print("   ✓ Adapter initialized")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test fetch
    print("\n2. Fetching news articles...")
    try:
        articles = await adapter.fetch(
            query="TSMC OR NVIDIA",
            max_results=5,
            date_from=datetime.now() - timedelta(days=7),
            date_to=datetime.now()
        )
        print(f"   ✓ Fetched {len(articles)} articles")
        
        # Display sample
        if articles:
            print("\n3. Sample article:")
            article = articles[0]
            print(f"   Title: {article['title'][:60]}...")
            print(f"   Source: {article['metadata']['source_name']}")
            print(f"   Published: {article['published_date']}")
            print(f"   URL: {article['url']}")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_newsapi())
    sys.exit(0 if success else 1)