import asyncio
from asyncio import Queue
from typing import Dict, Optional
import uuid
from datetime import datetime
import logging

from app.services.summary_pipeline import summary_pipeline
from app.models.summary import Summary
from app.models.article import Article
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = logging.getLogger(__name__)

class BackgroundTaskManager:
    """
    Background task manager for article summarization
    """
    
    def __init__(self):
        self.task_queue = Queue()
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.task_status: Dict[str, dict] = {}
        self.is_running = True
        
    async def submit_article_for_summarization(
        self, 
        db: AsyncSession,
        article_id: int,
        article_content: str,
        article_title: str,
        preferred_provider: Optional[str] = None,
        quality_level: str = "standard"
    ) -> str:
        """
        Submit article for background summarization
        Returns task_id for status tracking
        """
        task_id = str(uuid.uuid4())
        
        try:
            summary = Summary(
                article_id=article_id,
                task_id=task_id,
                status='pending',
                content='',  
                provider='', 
                model_name='',
                quality_level=quality_level,
                word_count=0,
                char_count=0,
                processing_time_ms=0,
                is_successful=False
            )
            
            db.add(summary)
            await db.commit()
            await db.refresh(summary)
            
            self.task_status[task_id] = {
                'task_id': task_id,
                'article_id': article_id,
                'article_title': article_title,
                'status': 'pending',
                'submitted_at': datetime.now(),
                'started_at': None,
                'completed_at': None,
                'preferred_provider': preferred_provider,
                'quality_level': quality_level,
                'error': None,
                'summary_id': summary.id
            }
            
            task_data = {
                'task_id': task_id,
                'db': db,
                'article_id': article_id,
                'article_content': article_content,
                'article_title': article_title,
                'preferred_provider': preferred_provider,
                'quality_level': quality_level
            }
            
            await self.task_queue.put(task_data)
            logger.info(f"📥 Submitted article {article_id} for background summarization. Task: {task_id}")
            
            return task_id
            
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Failed to submit article {article_id} for summarization: {e}")
            raise
    
    async def process_tasks(self):
        """
        Background worker that processes summarization tasks
        """
        logger.info("🔄 Background task processor started")
        
        while self.is_running:
            try:
                try:
                    task_data = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                task = asyncio.create_task(self._process_single_task(task_data))
                self.active_tasks[task_data['task_id']] = task
                
                await self._cleanup_completed_tasks()
                
            except Exception as e:
                logger.error(f"❌ Error in background task processor: {e}")
    
    async def _process_single_task(self, task_data: dict):
        """
        Process a single summarization task
        """
        task_id = task_data['task_id']
        db = task_data['db']
        
        try:
            self.task_status[task_id].update({
                'status': 'processing',
                'started_at': datetime.now()
            })
            
            await self._update_summary_status(db, task_id, 'processing', started_at=datetime.now())
            
            logger.info(f"🔄 Processing task {task_id} for article {task_data['article_id']}")
            
            summary = await self._process_with_pipeline(db, task_data)
            
            if summary and summary.is_successful:
                self.task_status[task_id].update({
                    'status': 'completed',
                    'completed_at': datetime.now(),
                    'summary_id': summary.id
                })
                logger.info(f"✅ Task {task_id} completed successfully. Summary ID: {summary.id}")
            else:
                error_msg = "Summarization failed"
                if summary and summary.error_message:
                    error_msg = summary.error_message
                    
                self.task_status[task_id].update({
                    'status': 'failed',
                    'completed_at': datetime.now(),
                    'error': error_msg
                })
                await self._update_summary_status(db, task_id, 'failed', error_message=error_msg)
                logger.error(f"❌ Task {task_id} failed for article {task_data['article_id']}")
                
        except Exception as e:
            error_msg = str(e)
            self.task_status[task_id].update({
                'status': 'error',
                'completed_at': datetime.now(),
                'error': error_msg
            })
            await self._update_summary_status(db, task_id, 'error', error_message=error_msg)
            logger.error(f"💥 Task {task_id} error: {e}")
        
        finally:
            self.active_tasks.pop(task_id, None)
    
    async def _process_with_pipeline(self, db: AsyncSession, task_data: dict) -> Optional[Summary]:
        """
        Use the existing SummaryPipeline with real database operations
        """
        result = await db.execute(
            select(Article).where(Article.id == task_data['article_id'])
        )
        article = result.scalar_one_or_none()
        
        if not article:
            raise ValueError(f"Article {task_data['article_id']} not found")
        
        summary = await summary_pipeline.process_article(
            db=db,
            article=article,
            preferred_provider=task_data['preferred_provider'],
            quality_level=task_data['quality_level']
        )
        
        return summary
    
    async def _update_summary_status(
        self, 
        db: AsyncSession, 
        task_id: str, 
        status: str, 
        started_at: datetime = None,
        error_message: str = None
    ):
        """Update summary status in database"""
        from sqlalchemy import update
        
        try:
            update_data = {'status': status}
            if started_at:
                update_data['started_at'] = started_at
            if error_message:
                update_data['error_message'] = error_message
            if status in ['completed', 'failed', 'error']:
                update_data['completed_at'] = datetime.now()
            
            await db.execute(
                update(Summary)
                .where(Summary.task_id == task_id)
                .values(update_data)
            )
            await db.commit()
            
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Failed to update summary status for task {task_id}: {e}")
            raise
    
    async def get_task_status(self, task_id: str) -> Optional[dict]:
        """Get current status of a task with database fallback"""
        memory_status = self.task_status.get(task_id)
        if memory_status:
            return memory_status
        
        return await self._get_task_status_from_db(task_id)
    
    async def _get_task_status_from_db(self, task_id: str) -> Optional[dict]:
        """Get task status from database"""
        from sqlalchemy import select
        from app.core.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            try:
                result = await db.execute(
                    select(Summary).where(Summary.task_id == task_id)
                )
                summary = result.scalar_one_or_none()
                
                if not summary:
                    return None
                
                task_status = {
                    'task_id': task_id,
                    'article_id': summary.article_id,
                    'article_title': self._get_article_title_from_db(db, summary.article_id),
                    'status': summary.status,
                    'submitted_at': summary.created_at,
                    'started_at': summary.started_at,
                    'completed_at': summary.completed_at,
                    'preferred_provider': None,  
                    'quality_level': summary.quality_level,
                    'error': summary.error_message,
                    'summary_id': summary.id
                }
                
                self.task_status[task_id] = task_status
                
                return task_status
                
            except Exception as e:
                logger.error(f"Error retrieving task status from database for {task_id}: {e}")
                return None

    async def _get_article_title_from_db(self, db, article_id: int) -> str:
        """Get article title from database"""
        from sqlalchemy import select
        from app.models.article import Article
        
        try:
            result = await db.execute(
                select(Article.title).where(Article.id == article_id)
            )
            title = result.scalar_one_or_none()
            return title or "Unknown Article"
        except Exception:
            return "Unknown Article"
    
    async def get_article_tasks(self, article_id: int) -> list:
        """Get all tasks for a specific article"""
        return [
            status for status in self.task_status.values() 
            if status['article_id'] == article_id
        ]
    
    async def get_pending_tasks_count(self) -> int:
        """Get number of pending tasks in queue"""
        return self.task_queue.qsize()
    
    async def get_active_tasks_count(self) -> int:
        """Get number of actively processing tasks"""
        return len(self.active_tasks)
    
    async def _cleanup_completed_tasks(self):
        """Clean up old completed tasks to prevent memory leaks"""
        current_time = datetime.now()
        tasks_to_remove = []
        
        for task_id, status in self.task_status.items():
            if status['status'] in ['completed', 'failed', 'error']:
                # Remove tasks older than 1 hour from memory
                if status['completed_at'] and (current_time - status['completed_at']).total_seconds() > 3600:
                    tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            self.task_status.pop(task_id, None)
    
    async def shutdown(self):
        """Gracefully shutdown the task manager"""
        logger.info("🛑 Shutting down background task manager...")
        self.is_running = False
        
        # Wait for current tasks to complete (with timeout)
        if self.active_tasks:
            logger.info(f"Waiting for {len(self.active_tasks)} active tasks to complete...")
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self.active_tasks.values(), return_exceptions=True),
                    timeout=30.0
                )
            except asyncio.TimeoutError:
                logger.warning("Timeout waiting for active tasks to complete")
        
        logger.info("✅ Background task manager shutdown complete")

task_manager = BackgroundTaskManager()