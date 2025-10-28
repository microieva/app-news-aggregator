import asyncio
from app.core.config import setup_colored_logging
from typing import List, Dict
from .gnews_aggregator import gnews_aggregator
from .newsapi_aggregator import newsapi_aggregator
from .reddit_aggregator import reddit_aggregator
from .rss_aggregator import rss_aggregator

logger = setup_colored_logging()

class AggregationOrchestrator:
    """Orchestrates multiple aggregators and manages the aggregation flow"""
    
    def __init__(self):
        self.aggregators = {
            "gnews": gnews_aggregator,
            "newsapi": newsapi_aggregator, 
            "reddit": reddit_aggregator,
            "rss": rss_aggregator
        }
    
    async def aggregate_articles(self, topic: str, limit_per_source: int = 10) -> List[Dict]:
        """
        Aggregate articles from all sources for a given topic
        
        Args:
            topic: Search topic
            limit_per_source: Number of articles per source
            
        Returns:
            Combined list of articles from all sources
        """

        tasks = []
        for source_name, aggregator in self.aggregators.items():
            task = self._fetch_from_aggregator(aggregator, topic, limit_per_source, source_name)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_articles = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Aggregator error: {result}")
            elif result:
                all_articles.extend(result)
        return all_articles
    
    async def _fetch_from_aggregator(self, aggregator, topic: str, limit: int, source_name: str):
        """Fetch articles from a single aggregator with error handling"""
        try:
            articles = await aggregator.fetch_articles(topic, limit)
            logger.info(f"✅ {source_name}: fetched {len(articles)} articles")
            return articles
        except Exception as e:
            logger.error(f"❌ {source_name}: failed to fetch articles - {e}")
            return []

aggregation_orchestrator = AggregationOrchestrator()