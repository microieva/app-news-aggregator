from typing import List, Dict
from .base_aggregator import BaseAggregator
from .reddit_service import reddit_service
from app.core.config import setup_colored_logging

logger = setup_colored_logging()

class RedditAggregator(BaseAggregator):
    """Reddit-specific implementation of BaseAggregator"""
    
    async def fetch_articles(self, topic: str, limit: int = 10) -> List[Dict]:
        """
        Fetch articles from Reddit for a given topic
        
        Args:
            topic: Search topic
            limit: Number of articles to fetch
            
        Returns:
            List of article dictionaries
        """
        try:
            posts = await reddit_service.fetch_posts(topic, limit)
            
            articles = []
            for post in posts:
                article = {
                    "title": post["title"],
                    "url": post["url"],
                    "content": post["content"],
                    "summary": "",  # Will be filled by AI summarization
                    "source": self.get_source_name(),
                    "author": post["author"],
                    "published_at": post["published_at"],
                    "image_url": None,  
                    "source_metadata": {
                        "subreddit": post["subreddit"],
                        "score": post["score"],
                        "num_comments": post["num_comments"],
                        "source_id": post["source_id"]
                    }
                }
                articles.append(article)
                
            return articles
            
        except Exception as e:
            logger.error(f"Error in RedditAggregator for topic '{topic}': {e}")
            return []
    
    def get_source_name(self) -> str:
        return "reddit"
    

reddit_aggregator = RedditAggregator()