from app.core.config import setup_colored_logging
from typing import Optional
import time
import traceback
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.services.llm.provider_manager import provider_manager
from app.models import Article, Summary
from app.schemas.summary import SummaryCreate
from app.crud import summary as summary_crud

logger = setup_colored_logging()

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
        
        logger.info(f"📝 Starting processing for article: {article.title[:50]}... (ID: {article.id})")
        logger.info(f"🔍 Article content length: {len(article.content or '')} chars")
        
        try:
            # Step 1: Check if summary already exists
            logger.info(f"🔍 Checking for existing summary...")
            existing_summary = await self._get_existing_summary(db, article.id)

            if existing_summary:
                logger.warning(f"⚠️ Summary already exists for article {article.id}")
                return existing_summary
            else:
                logger.info(f"📝 No existing summary found, proceeding with generation...")
            
            # Step 2: Check if article has content
            if not article.content or len(article.content.strip()) < 50:
                logger.warning(f"⚠️ Article {article.id} has insufficient content: '{article.content}'")
                await self._mark_article_failed(db, article.id, "Insufficient content for summarization")
                self.stats["failed_summaries"] += 1
                return None
            
            # Step 3: Generate summary using provider manager
            logger.info(f"🤖 Generating summary with provider manager...")
            summary_text = await self.provider_manager.summarize_with_fallback(
                text=article.content,
                preferred_provider=preferred_provider,
                quality_level=quality_level 
            )
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            if not summary_text:
                logger.error(f"❌ All providers failed to generate summary for article: {article.id}")
                await self._mark_article_failed(db, article.id, "All providers failed")
                self.stats["failed_summaries"] += 1
                return None
            
            logger.info(f"✅ Summary generated successfully. Length: {len(summary_text)} chars")
            
            # Step 4: Create and save Summary object
            logger.info(f"💾 Saving summary to database...")
            summary = await self._create_and_save_summary(
                db=db,
                article_id=article.id,
                summary_text=summary_text,
                provider_used=self.provider_manager.get_last_used_provider(),
                model_used=self.provider_manager.get_last_used_model(),
                quality_level=quality_level,
                processing_time_ms=processing_time_ms
            )
            
            # Step 5: Mark article as processed
            logger.info(f"🏷️ Marking article as processed...")
            await self._mark_article_processed(db, article.id)
            
            self.stats["successful_summaries"] += 1
            self.stats["processing_times"].append(processing_time_ms / 1000)
            self.stats["average_processing_time"] = sum(self.stats["processing_times"]) / len(self.stats["processing_times"])
            
            provider_name = self.provider_manager.get_last_used_provider()
            self.stats["provider_usage"][provider_name] = self.stats["provider_usage"].get(provider_name, 0) + 1
            
            logger.info(f"✅ Successfully processed article {article.id} in {processing_time_ms}ms using {provider_name}")
            return summary
            
        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            self.stats["failed_summaries"] += 1
            logger.error(f"❌ Pipeline error processing article {article.id}: {e}")
            logger.error(f"🔍 Stack trace: {traceback.format_exc()}")
            
            await self._mark_article_failed(db, article.id, str(e))
            return None
    
    async def _get_existing_summary(self, db: AsyncSession, article_id: int) -> Optional[Summary]:
        """Check if summary already exists for article"""
        try:
            result = await db.execute(
                select(Summary).where(Summary.article_id == article_id)
            )
            summary = result.scalar_one_or_none()
            logger.info(f"🔍 Existing summary check: {'found' if summary else 'not found'}")
            return summary
        except Exception as e:
            logger.error(f"❌ Error checking existing summary: {e}")
            return None
    
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
        logger.info(f"💾 Creating summary for article {article_id}...")
        
        try:
            summary_create = SummaryCreate(
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
            
            logger.info(f"🔍 Checking if summary already exists...")
            existing_summary = await summary_crud.get_summary_by_article_id(db, article_id)

            if existing_summary is None:
                logger.info(f"📝 Creating new summary...")
                summary = await summary_crud.create_summary(db, summary_create)
                logger.info(f"✅ Summary created successfully with ID: {summary.id}")
                return summary
            else:
                logger.warning(f"⚠️ Summary already exists for article {article_id}")
                return existing_summary
            
        except Exception as e:
            logger.error(f"❌ Error in _create_and_save_summary: {e}")
            logger.error(f"🔍 Stack trace: {traceback.format_exc()}")
            await db.rollback()
            raise e
    
    async def _mark_article_processed(self, db: AsyncSession, article_id: int):
        """Mark article as successfully processed"""
        try:
            logger.info(f"🏷️ Marking article {article_id} as processed...")
            await db.execute(
                update(Article)
                .where(Article.id == article_id)
                .values(is_processed=True, processing_error=None)
            )
            await db.commit()
            logger.info(f"✅ Article {article_id} marked as processed")
        except Exception as e:
            logger.error(f"❌ Error marking article as processed: {e}")
            await db.rollback()
            raise
    
    async def _mark_article_failed(self, db: AsyncSession, article_id: int, error_message: str):
        """Mark article as failed processing"""
        try:
            logger.info(f"🏷️ Marking article {article_id} as failed: {error_message}")
            await db.execute(
                update(Article)
                .where(Article.id == article_id)
                .values(is_processed=False, processing_error=error_message)
            )
            await db.commit()
            logger.info(f"✅ Article {article_id} marked as failed")
        except Exception as e:
            logger.error(f"❌ Error marking article as failed: {e}")
            await db.rollback()
            raise

    def get_stats(self) -> dict:
        """Get pipeline statistics"""
        return self.stats.copy()

summary_pipeline = SummaryPipeline()