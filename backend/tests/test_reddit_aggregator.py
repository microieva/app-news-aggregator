import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.services.reddit_aggregator import RedditAggregator
from app.core.config import settings

async def test_reddit_aggregator():
    """Test the Reddit aggregator service"""
    print("🧪 Testing Reddit Aggregator...")
    
    aggregator = RedditAggregator()
    
    # Test with a simple topic
    test_topic = "python programming"
    articles = await aggregator.fetch_articles(test_topic, limit=5)
    
    print(f"📰 Found {len(articles)} articles for topic: '{test_topic}'")
    
    for i, article in enumerate(articles, 1):
        print(f"\n--- Article {i} ---")
        print(f"Title: {article['title']}")
        print(f"Source: {article['source']}")
        print(f"Author: {article['author']}")
        print(f"URL: {article['url']}")
        print(f"Content preview: {article['content'][:100]}...")
    
    print(f"\n✅ Reddit aggregator test completed!")

if __name__ == "__main__":
    asyncio.run(test_reddit_aggregator())