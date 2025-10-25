from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import setup_colored_logging
from typing import List
from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.services.aggregation_orchestrator import aggregation_orchestrator
from app.crud import article as article_crud
from app.crud import topic as topic_crud
from app.schemas.article import ArticleCreate
from app.services import topic_matcher

logger = setup_colored_logging()

class AggregationService:
    """Service to manage news aggregation on a schedule"""
    
    def __init__(self):
        self.is_running = False
        self.last_run = None
        self.async_session_factory = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

    async def run_aggregation(self, topics: List[str] = None):
        """Run aggregation for specified topics"""

        async with self.async_session_factory() as db_session:
            if topics is None:
                db_topics = await topic_crud.get_all(db_session)
                topics = [topic.name for topic in db_topics]
        
        logger.info("\n\n\n🔄 Starting news aggregation cycle\n\n\n")
        self.last_run = datetime.now()
        
        total_articles = 0
        for topic in topics:
            try:
                articles = await aggregation_orchestrator.aggregate_articles(topic)
                
                enhanced_articles = []
                for article in articles:
                    enhanced_article = await self._enhance_article_with_topic(article, topic)
                    enhanced_articles.append(enhanced_article)
                
                total_articles += len(enhanced_articles)
                
                saved_count = await self._save_articles_to_db(enhanced_articles)
                
                logger.info(f"✅ Topic '{topic}': {len(enhanced_articles)} articles processed, {saved_count} saved")
                
            except Exception as e:
                logger.error(f"❌ Error aggregating topic '{topic}': {e}")
        
        logger.info(f"\n\n\n📊 Aggregation complete: {total_articles} total articles across {len(topics)} topics\n\n\n")
        return total_articles

    async def _enhance_article_with_topic(self, article: dict, search_topic: str) -> dict:
        """Enhance article with better topic detection using topic_matcher"""
        try:
            title = article.get('title')
            content = article.get('content')

            detected_topic = await topic_matcher.get_primary_topic(title, content)
            async with self.async_session_factory() as db_session:
                try:
                    if detected_topic and detected_topic != search_topic:
                        logger.debug(f"🎯 Topic refined: '{search_topic}' → '{detected_topic}' for: {title[:50]}...")
                        article['primary_topic'] = detected_topic
                        article['original_search_topic'] = search_topic 
                        article['topic_id'] = await topic_crud.get_topic_id_by_name(detected_topic, db_session)
                    else:
                        article['primary_topic'] = search_topic
                        article['original_search_topic'] = search_topic
                        article['topic_id'] = await topic_crud.get_topic_id_by_name(search_topic, db_session)

                except Exception as e:
                    logger.error(f"Error fetching topic ID: {e}")

            return article
            
        except Exception as e:
            logger.warning(f"⚠️ Error enhancing article topic: {e}")
            article['primary_topic'] = search_topic
            return article
    
    async def _save_articles_to_db(self, articles: List[dict]) -> int:
        """Save aggregated articles to the database"""
        saved_count = 0
        async with self.async_session_factory() as db_session:
            try:
                for article_data in articles:
                    article_create = ArticleCreate(**article_data)
                    existing_article = await article_crud.get_by_url(db_session, article_create.url)
                    
                    if not existing_article:
                        await article_crud.create_article(db_session, article_create)
                        saved_count += 1
                    else:
                        logger.debug(f"📝 Article already exists: {article_create.title}")
                
                await db_session.commit()
                logger.info(f"💾 Saved {saved_count} new articles to database")
                
            except Exception as e:
                await db_session.rollback()
                logger.error(f"❌ Error saving articles to database: {e}")
                raise
        
        return saved_count      

aggregation_service = AggregationService()