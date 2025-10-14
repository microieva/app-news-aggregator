from typing import List, Dict
from .base_aggregator import BaseAggregator
from .rss_service import rss_service
import logging

logger = logging.getLogger(__name__)

class RSSAggregator(BaseAggregator):
    """RSS-specific implementation of BaseAggregator"""
    
    async def fetch_articles(self, topic: str, limit: int = 10) -> List[Dict]:
        """
        Fetch articles from RSS feeds for a given topic
        
        Args:
            topic: Search topic
            limit: Number of articles to fetch
            
        Returns:
            List of article dictionaries
        """
        try:
            articles = await rss_service.fetch_articles(topic, limit)
            
            transformed_articles = []
            for article in articles:
                transformed = {
                    "title": article["title"],
                    "url": article["url"],
                    "content": article["content"],
                    "summary": article["summary"],
                    "source": self.get_source_name(),
                    "author": article["author"],
                    "published_at": article["published_at"],
                    "image_url": article["image_url"],
                    "source_metadata": article["source_metadata"]
                }
                transformed_articles.append(transformed)
                
            logger.info(f"RSS aggregator returned {len(transformed_articles)} articles for topic: {topic}")
            return transformed_articles
            
        except Exception as e:
            logger.error(f"Error in RSSAggregator for topic '{topic}': {e}")
            return []
    
    def get_source_name(self) -> str:
        return "rss"

rss_aggregator = RSSAggregator()