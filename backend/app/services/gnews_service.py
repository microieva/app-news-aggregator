import httpx
from typing import List, Dict
from app.core.config import settings
from app.core.config import setup_colored_logging

logger = setup_colored_logging()

class GNewsService:
    def __init__(self):
        self.api_key = settings.GNEWS_API_KEY
        self.base_url = settings.GNEWS_API_URL
        
    async def fetch_articles(self, topic: str, limit: int = 10) -> List[Dict]:
        """
        Fetch articles from GNews API for a given topic
        
        Args:
            topic: Search topic
            limit: Number of articles to fetch
            
        Returns:
            List of article dictionaries
        """
        if not self.api_key:
            logger.warning("GNews API key not configured")
            return []
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/search",
                    params={
                        "q": topic,
                        "token": self.api_key,
                        "lang": "en",
                        "max": limit,
                        "sortby": "relevance"
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
                            "source": "gnews",
                            "author": article.get("source", {}).get("name", "Unknown"),
                            "published_at": article.get("publishedAt", ""),
                            "image_url": article.get("image", ""),
                            "source_metadata": {
                                "source_name": article.get("source", {}).get("name", ""),
                                "api_source": "gnews"
                            }
                        }
                        if transformed["title"] and transformed["url"]:
                            transformed_articles.append(transformed)
                    
                    logger.info(f"Fetched {len(transformed_articles)} articles from GNews for topic: {topic}")
                    return transformed_articles
                else:
                    logger.error(f"GNews API error: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching from GNews for topic '{topic}': {e}")
            return []

gnews_service = GNewsService()