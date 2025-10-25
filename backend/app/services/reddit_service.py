import asyncpraw
from typing import List, Dict, Optional
from app.core.config import settings
from app.core.config import setup_colored_logging

logger = setup_colored_logging()

class RedditService:
    def __init__(self):
        self.client_id = settings.REDDIT_CLIENT_ID
        self.client_secret = settings.REDDIT_CLIENT_SECRET
        self.user_agent = "SmartContentAggregator/1.0"
        self.reddit = None
        
    async def initialize(self):
        """Initialize Reddit client"""
        if not self.client_id or not self.client_secret:
            logger.warning("Reddit API credentials not configured")
            return False
            
        try:
            self.reddit = asyncpraw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            )
            logger.info("Reddit client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Reddit client: {e}")
            return False
    
    async def fetch_posts(self, topic: str, limit: int = 10, subreddit: str = "all") -> List[Dict]:
        """
        Fetch posts from Reddit for a given topic
        
        Args:
            topic: Search topic
            limit: Number of posts to fetch
            subreddit: Subreddit to search (default: "all")
            
        Returns:
            List of post dictionaries
        """
        if not self.reddit:
            if not await self.initialize():
                return []
        
        try:
            posts = []
            subreddit_obj = await self.reddit.subreddit(subreddit)
            
            async for submission in subreddit_obj.search(
                query=topic, 
                limit=limit, 
                sort="relevance"
            ):
                post_data = {
                    "title": submission.title,
                    "url": submission.url,
                    "content": self._extract_content(submission),
                    "author": str(submission.author) if submission.author else "Unknown",
                    "published_at": submission.created_utc,
                    "source": "reddit",
                    "source_id": submission.id,
                    "score": submission.score,
                    "num_comments": submission.num_comments,
                    "subreddit": str(submission.subreddit)
                }
                posts.append(post_data)
                
            logger.info(f"Fetched {len(posts)} posts for topic: {topic}")
            return posts
            
        except Exception as e:
            logger.error(f"Error fetching Reddit posts for topic '{topic}': {e}")
            return []
    
    def _extract_content(self, submission) -> str:
        """Extract content from Reddit submission"""
        if submission.is_self:  # Text post
            return submission.selftext[:2000] if submission.selftext else ""  # Limit content length
        else:  # Link post
            return submission.title  # Use title as content for link posts
    
    async def close(self):
        """Close Reddit client"""
        if self.reddit:
            await self.reddit.close()

reddit_service = RedditService()