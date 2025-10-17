import logging
from typing import Optional
import time

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.services.llm.provider_manager import provider_manager
from app.models.article import Article
from app.models.summary import Summary

logger = logging.getLogger(__name__)

class SummaryPipeline:
    """
    Async summary pipeline for article processing
    """
    
    def __init__(self):
        self.provider_manager = provider_manager
        self.stats = {
            "total_processed": 0,
            "successful_summaries": 0,
            "failed_summaries": 0,
            "provider_usage": {},
            "average_processing_time": 0,
            "processing_times": []
        }
    
    async def process_article(
        self,
        db: AsyncSession,  
        article: Article,
        preferred_provider: Optional[str] = None,
        quality_level: str = "standard"
    ) -> Optional[Summary]:
        """
        Process an article through the summarization pipeline
        """
        start_time = time.time()
        
        self.stats["total_processed"] += 1
        
        logger.info(f"📝 Processing article: {article.title[:50]}... (ID: {article.id})")
        
        try:
            # Step 1: Check if summary already exists
            existing_summary = await self._get_existing_summary(db, article.id)
            if existing_summary:
                logger.info(f"✅ Summary already exists for article {article.id}")
                return existing_summary
            
            # Step 2: Generate summary using provider manager
            summary_text = await self.provider_manager.summarize_with_fallback(
                text=article.content,
                preferred_provider=preferred_provider,
                quality_level=quality_level 
            )
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            if not summary_text:
                logger.error(f"❌ Failed to generate summary for article: {article.id}")
                await self._mark_article_failed(db, article.id, "All providers failed")
                self.stats["failed_summaries"] += 1
                return None
            
            # Step 3: Create and save Summary object
            summary = await self._create_and_save_summary(
                db=db,
                article_id=article.id,
                summary_text=summary_text,
                provider_used=self.provider_manager.get_last_used_provider(),
                model_used=self.provider_manager.get_last_used_model(),
                quality_level=quality_level,
                processing_time_ms=processing_time_ms
            )
            
            # Step 4: Mark article as processed
            await self._mark_article_processed(db, article.id)
            
            # Update statistics
            self.stats["successful_summaries"] += 1
            self.stats["processing_times"].append(processing_time_ms / 1000)
            self.stats["average_processing_time"] = sum(self.stats["processing_times"]) / len(self.stats["processing_times"])
            
            # Track provider usage
            provider_name = self.provider_manager.get_last_used_provider()
            self.stats["provider_usage"][provider_name] = self.stats["provider_usage"].get(provider_name, 0) + 1
            
            logger.info(f"✅ Successfully processed article {article.id} in {processing_time_ms}ms using {provider_name}")
            return summary
            
        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            self.stats["failed_summaries"] += 1
            logger.error(f"❌ Pipeline error processing article {article.id}: {e}")
            
            # Mark article as failed
            await self._mark_article_failed(db, article.id, str(e))
            return None
    
    async def _get_existing_summary(self, db: AsyncSession, article_id: int) -> Optional[Summary]:
        """Check if summary already exists for article"""
        result = await db.execute(
            select(Summary).where(Summary.article_id == article_id)
        )
        return result.scalar_one_or_none()
    
    async def _create_and_save_summary(
        self,
        db: AsyncSession,
        article_id: int,
        summary_text: str,
        provider_used: str,
        model_used: str,
        quality_level: str,
        processing_time_ms: int
    ) -> Summary:
        """Create and save a Summary object to database"""
        summary = Summary(
            article_id=article_id,
            content=summary_text,
            provider=provider_used,
            model_name=model_used,
            quality_level=quality_level,
            word_count=len(summary_text.split()),
            char_count=len(summary_text),
            processing_time_ms=processing_time_ms,
            is_successful=True
        )
        
        db.add(summary)
        await db.commit()
        await db.refresh(summary)
        
        return summary
    
    async def _mark_article_processed(self, db: AsyncSession, article_id: int):
        """Mark article as successfully processed"""
        await db.execute(
            update(Article)
            .where(Article.id == article_id)
            .values(is_processed=True, processing_error=None)
        )
        await db.commit()
    
    async def _mark_article_failed(self, db: AsyncSession, article_id: int, error_message: str):
        """Mark article as failed processing"""
        await db.execute(
            update(Article)
            .where(Article.id == article_id)
            .values(is_processed=False, processing_error=error_message)
        )
        await db.commit()

summary_pipeline = SummaryPipeline()

