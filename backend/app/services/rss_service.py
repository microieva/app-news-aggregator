import feedparser
import asyncio
from typing import List, Dict
import logging
from datetime import datetime
import aiohttp
from app.core.config import settings

logger = logging.getLogger(__name__)

class RSSService:
    def __init__(self):
        self.feeds = settings.RSS_FEEDS
    
    async def fetch_articles(self, topic: str, limit: int = 10) -> List[Dict]:
        """
        Fetch articles from RSS feeds matching a topic
        
        Args:
            topic: Search topic
            limit: Number of articles to fetch
            
        Returns:
            List of article dictionaries
        """
        try:
            all_articles = []
            
            tasks = []
            for feed_name, feed_url in self.feeds.items():
                task = self._fetch_feed_articles(feed_name, feed_url, topic, limit)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    all_articles.extend(result)
            
            all_articles.sort(key=lambda x: x.get("published_at", ""), reverse=True)
            return all_articles[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching RSS articles for topic '{topic}': {e}")
            return []
    
    async def _fetch_feed_articles(self, feed_name: str, feed_url: str, topic: str, limit: int) -> List[Dict]:
        """Fetch articles from a single RSS feed"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(feed_url) as response:
                    content = await response.text()
                    
            feed = feedparser.parse(content)
            articles = []
            
            for entry in feed.entries[:limit]:
                if topic.lower() in entry.title.lower() or (hasattr(entry, 'summary') and topic.lower() in entry.summary.lower()):
                    article = {
                        "title": entry.title,
                        "url": entry.link,
                        "content": getattr(entry, 'summary', entry.title),
                        "summary": getattr(entry, 'summary', ""),
                        "source": "rss",
                        "author": getattr(entry, 'author', feed.feed.get('title', feed_name)),
                        "published_at": self._parse_date(getattr(entry, 'published_parsed', None)),
                        "image_url": self._extract_image(entry),
                        "source_metadata": {
                            "feed_name": feed_name,
                            "feed_url": feed_url,
                            "rss_source": feed.feed.get('title', feed_name)
                        }
                    }
                    articles.append(article)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching from RSS feed '{feed_name}': {e}")
            return []
    
    def _parse_date(self, date_tuple) -> str:
        """Parse date tuple to ISO format string"""
        if date_tuple:
            try:
                dt = datetime(*date_tuple[:6])
                return dt.isoformat()
            except:
                pass
        return datetime.now().isoformat()
    
    def _extract_image(self, entry) -> str:
        """Extract image URL from RSS entry"""

        image_fields = ['media_thumbnail', 'media_content', 'links']
        for field in image_fields:
            if hasattr(entry, field):
                media = getattr(entry, field)
                if media and len(media) > 0 and hasattr(media[0], 'url'):
                    return media[0].url
        return ""

rss_service = RSSService()