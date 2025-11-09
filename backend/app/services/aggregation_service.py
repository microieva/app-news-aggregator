from datetime import datetime
import traceback
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy.orm import sessionmaker

from app.core import engine, setup_colored_logging
from app.services import topic_matcher, aggregation_orchestrator
from app.crud import article as article_crud
from app.crud import topic as topic_crud
from app.schemas.article import ArticleCreate

logger = setup_colored_logging()

class AggregationService:
    """Service to manage news aggregation on a schedule"""
    
    def __init__(self):
        self.is_running = False
        self.last_run = None
        self.async_session_factory = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

    async def run_aggregation(self, topics: List[str] = None) -> int:
        """Run aggregation for specified topics"""

        async with self.async_session_factory() as db_session:
            if topics is None:
                db_topics = await topic_crud.get_all(db_session)
                topics = [topic.name for topic in db_topics]
        
        logger.info("\n\n\n🔄 Starting news aggregation cycle\n\n\n")
        self.last_run = datetime.now()
        
        total_articles = 0
        for topic in topics:
            if topic.lower() == "other":
                logger.info(f"⏭️ Skipping 'other' topic")
                continue

            try:
                articles = await aggregation_orchestrator.aggregate_articles(topic)
                from app.core import task_manager
                enhanced_articles = []


                for article in articles:
                    #if self._validate_article(article):
                    enhanced_article = await self._enhance_article_with_topic(article, topic)
                    enhanced_articles.append(enhanced_article)

                saved_ids = await self._save_articles_to_db(enhanced_articles)
                if saved_ids:  
                    total_articles = len(saved_ids)  
                    await task_manager.submit_articles_for_summarization(saved_ids)

                logger.info(f"✅ Topic '{topic}': {total_articles} articles processed, saved, and submitted for summarization")
                
            except Exception as e:
                logger.error(f"❌ Error aggregating topic '{topic}': {e}")
                logger.error(f"🔍 Stack trace: {traceback.format_exc()}")
                
        
        logger.info(f"📊 Aggregation complete: {total_articles} total articles across {len(topics)} topics")
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
        
    def _validate_article(self, article: dict) -> bool:
        
        validation_checks = [
            # (condition, field_name, failure_message)
            (
                article.get('author') and str(article.get('author')).strip(),
                'author',
                'missing or empty author'
            ),
            (
                article.get('image_url') and 
                str(article.get('image_url')).strip() and 
                article.get('image_url') != article.get('url'),
                'image_url',
                'missing, empty, or same as article URL'
            ),
            (
                article.get('title') and str(article.get('title')).strip(),
                'title',
                'missing or empty title'
            ),
            (
                article.get('content') and 
                len(str(article.get('content')).split()) >= 50,
                'content',
                f'missing or too short ({len(str(article.get("content") or "").split())} words, need 50+)'
            )
        ]
        
        failed_checks = []
        
        for condition, field, message in validation_checks:
            if not condition:
                failed_checks.append(field)
                logger.info(f"Article validation failed for {field}: {message}")
        
        if failed_checks:
            logger.info(f"Article validation failed. Total failed fields: {len(failed_checks)}")
            return False
        
        logger.info("Article validation passed all checks")
        return True
    
    async def _save_articles_to_db(self, articles: List[dict]) -> List[int]:
        """Save aggregated articles to the database, return new article IDs"""
        new_article_ids = []
        async with self.async_session_factory() as db_session:
            try:
                for article_data in articles:
                    article_create = ArticleCreate(**article_data)
                    existing_article = await article_crud.get_by_url(db_session, article_create.url)
                    
                    if not existing_article:
                        created_article = await article_crud.create_article(db_session, article_create)
                        new_article_ids.append(created_article.id)
                
                await db_session.commit()
                
            except Exception as e:
                await db_session.rollback()
                logger.error(f"❌ Error saving articles: {e}")
                raise
        
        return new_article_ids

aggregation_service = AggregationService()