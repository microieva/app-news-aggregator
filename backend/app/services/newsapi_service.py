import httpx
from typing import List, Dict, Optional
from app.core.config import settings
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class NewsAPIService:
    def __init__(self):
        self.api_key = settings.NEWSAPI_KEY
        self.base_url = settings.NEWSAPI_BASE_URL
        
    async def fetch_articles(self, topic: str, limit: int = 10) -> List[Dict]:
        """
        Fetch articles from NewsAPI for a given topic
        
        Args:
            topic: Search topic
            limit: Number of articles to fetch
            
        Returns:
            List of article dictionaries
        """
        if not self.api_key:
            logger.warning("NewsAPI key not configured")
            return []
            
        try:
            async with httpx.AsyncClient() as client:
                # Calculate date from 1 week ago
                from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                
                response = await client.get(
                    f"{self.base_url}/everything",
                    params={
                        "q": topic,
                        "apiKey": self.api_key,
                        "pageSize": limit,
                        "sortBy": "publishedAt",
                        "from": from_date,
                        "language": "en"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get("articles", [])
                    
                    transformed_articles = []
                    for article in articles:
                        transformed = {
                            "title": article.get("title", ""),
                            "url": article.get("url", ""),
                            "content": article.get("content", "") or article.get("description", ""),
                            "summary": article.get("description", ""),
                            "source": "newsapi",
                            "author": article.get("author", "Unknown"),
                            "published_at": article.get("publishedAt", ""),
                            "image_url": article.get("urlToImage", ""),
                            "source_metadata": {
                                "source_name": article.get("source", {}).get("name", ""),
                                "api_source": "newsapi"
                            }
                        }

                        if transformed["title"] and transformed["url"]:
                            transformed_articles.append(transformed)
                    
                    logger.info(f"Fetched {len(transformed_articles)} articles from NewsAPI for topic: {topic}")
                    return transformed_articles
                else:
                    logger.error(f"NewsAPI error: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching from NewsAPI for topic '{topic}': {e}")
            return []

newsapi_service = NewsAPIService()