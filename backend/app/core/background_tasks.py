import asyncio
from enum import Enum
from typing import Dict, Optional
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db, setup_colored_logging
from app.services import summary_pipeline, aggregation_service
from app.models import Summary
from app.crud import article as article_crud
from app.crud import summary as summary_crud

logger = setup_colored_logging()

class TaskType(Enum):
    AGGREGATION = "aggregation"
    SUMMARIZATION = "summarization"

class BackgroundTaskManager:
    """
    Background task manager for article summarization
    """
    
    def __init__(self):
        self.is_running = False
        self.aggregation_queue = asyncio.Queue()
        self.summarization_queue = asyncio.Queue()
        self.task_status: Dict[str, Dict] = {}
        self.active_tasks: Dict[str, asyncio.Task] = {}
        
        self.max_concurrent_aggregations = 1  
        self.max_concurrent_summarizations = 3 


    # async def process_tasks(self):
    #     """
    #     Background worker that processes summarization tasks
    #     """
    #     logger.info("🔄 Background task processor started")
        
    #     while self.is_running:
    #         try:
    #             try:
    #                 task_data = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
    #             except asyncio.TimeoutError:
    #                 continue
                
    #             task = asyncio.create_task(self._process_single_task(task_data))
    #             self.active_tasks[task_data['task_id']] = task
                
    #             await self._cleanup_completed_tasks()
                
    #         except Exception as e:
    #             logger.error(f"❌ Error in background task processor: {e}")
  
    async def start_processing(self):
        """Start processing both aggregation and summarization tasks"""
        if self.is_running:
            logger.warning("⚠️ Background task processor already running")
            return
            
        self.is_running = True
        logger.info("🔄 Starting background task processors...")
        
        # Start aggregation processor
        asyncio.create_task(self._process_aggregation_tasks())
        logger.info("✅ Aggregation task processor started")
        
        # Start multiple summarization workers (for parallel processing)
        for i in range(self.max_concurrent_summarizations):
            asyncio.create_task(self._process_summarization_tasks(i))
            logger.info(f"✅ Summarization worker {i+1} started")
        
        logger.info("🎯 All background task processors started")

    async def stop_processing(self):
        """Stop all background processing"""
        self.is_running = False
        logger.info("🛑 Stopping background task processors...")
        
        for task_id, task in self.active_tasks.items():
            if not task.done():
                task.cancel()
                logger.info(f"🛑 Cancelled task: {task_id}")
        
        if self.active_tasks:
            await asyncio.gather(*self.active_tasks.values(), return_exceptions=True)
        
        logger.info("✅ All background task processors stopped")

    # AGGREGATION METHODS

    async def _process_aggregation_tasks(self):
        """Process aggregation tasks from the queue"""
        logger.info("🔄 Aggregation task processor started")
        
        while self.is_running:
            try:
                if len([t for t in self.active_tasks.values() if t.get('type') == TaskType.AGGREGATION]) >= self.max_concurrent_aggregations:
                    await asyncio.sleep(1)
                    continue
                
                task_data = await asyncio.wait_for(self.aggregation_queue.get(), timeout=1.0)
                
                task = asyncio.create_task(self._execute_aggregation_task(task_data))
                self.active_tasks[task_data['task_id']] = task
                self.task_status[task_data['task_id']].update({
                    'started_at': datetime.now(),
                    'status': 'processing'
                })
                
                task.add_done_callback(lambda t, tid=task_data['task_id']: self._handle_task_completion(tid))
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"❌ Error in aggregation task processor: {e}")

    async def _execute_aggregation_task(self, task_data: Dict) -> Dict:
        """Execute an aggregation task"""
        task_id = task_data['task_id']
        
        try:
            logger.info(f"🔄 Starting aggregation task: {task_id}")
            
            result = await aggregation_service.run_aggregation(task_data['topics'])
            
            self.task_status[task_id].update({
                'completed_at': datetime.now(),
                'status': 'completed',
                'result': result,
                'articles_processed': result
            })
            
            logger.info(f"✅ Aggregation task completed: {task_id} - {result} articles")
            return {'success': True, 'articles_processed': result}
            
        except Exception as e:
            logger.error(f"❌ Aggregation task failed: {task_id} - {e}")
            self.task_status[task_id].update({
                'completed_at': datetime.now(),
                'status': 'failed',
                'error': str(e)
            })
            return {'success': False, 'error': str(e)}

    # SUMMARIZATION METHODS

    async def _process_summarization_tasks(self, worker_id: int):
        """Process summarization tasks from the queue (multiple workers)"""
        logger.info(f"🔄 Summarization worker {worker_id} started")
        
        while self.is_running:
            try:
                task_data = await asyncio.wait_for(self.summarization_queue.get(), timeout=1.0)
                
                task = asyncio.create_task(self._execute_summarization_task(task_data, worker_id))
                self.active_tasks[task_data['task_id']] = task
                self.task_status[task_data['task_id']].update({
                    'started_at': datetime.now(),
                    'status': 'processing',
                    'worker_id': worker_id
                })
                
                # Remove from active tasks when done
                task.add_done_callback(lambda t, tid=task_data['task_id']: self._handle_task_completion(tid))
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"❌ Error in summarization worker {worker_id}: {e}")

    async def _execute_summarization_task(self, task_data: Dict, worker_id: int) -> Dict:
        """Execute a summarization task"""
        task_id = task_data['task_id']
        article_id = task_data['article_id']
        
        try:
            logger.info(f"🔄 Worker {worker_id} starting summarization: {task_id} for article {article_id}")
            
            # Get database session for this task
            async with get_db() as db_session:
                # Get the article
                article = await article_crud.get_article(db_session, article_id)
                if not article:
                    raise ValueError(f"Article {article_id} not found")
                
                # Process through summary pipeline
                summary = await summary_pipeline.process_article(
                    db=db_session,
                    article=article,
                    preferred_provider=task_data.get('preferred_provider'),
                    quality_level=task_data.get('quality_level', 'standard')
                )
                
                if summary:
                    # Update task status
                    self.task_status[task_id].update({
                        'completed_at': datetime.now(),
                        'status': 'completed',
                        'summary_id': summary.id,
                        'provider_used': summary.provider,
                        'processing_time_ms': summary.processing_time_ms
                    })
                    
                    logger.info(f"✅ Worker {worker_id} completed summarization: {task_id} for article {article_id}")
                    return {'success': True, 'summary_id': summary.id}
                else:
                    raise ValueError("Summary pipeline returned None")
                    
        except Exception as e:
            logger.error(f"❌ Worker {worker_id} failed summarization: {task_id} - {e}")
            self.task_status[task_id].update({
                'completed_at': datetime.now(),
                'status': 'failed',
                'error': str(e)
            })
            
            try:
                async with get_db() as db_session:
                    await summary_crud.mark_summary_failed(db_session, task_data['summary_id'], str(e))
            except Exception as db_error:
                logger.error(f"❌ Failed to update summary status: {db_error}")
            
            return {'success': False, 'error': str(e)}
    
    async def submit_article_for_summarization(
        self, 
        db: AsyncSession,
        article_id: int,
        article_content: str,
        article_title: str,
        preferred_provider: Optional[str] = None,
        quality_level: str = "standard"
    ) -> str:
        """Submit article for background summarization"""
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
            
            task_data = {
                'task_id': task_id,
                'type': TaskType.SUMMARIZATION,
                'article_id': article_id,
                'article_content': article_content,
                'article_title': article_title,
                'preferred_provider': preferred_provider,
                'quality_level': quality_level,
                'summary_id': summary.id,
                'submitted_at': datetime.now(),
                'status': 'pending'
            }
            
            await self.summarization_queue.put(task_data)
            self.task_status[task_id] = task_data
            
            logger.info(f"📥 Submitted article {article_id} for summarization. Task: {task_id}")
            return task_id
            
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Failed to submit article {article_id} for summarization: {e}")
            raise
    
    # COMMON METHODS

    def _handle_task_completion(self, task_id: str):
        """Handle task completion - remove from active tasks"""
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]
    
    async def recover_pending_tasks(self, db_session: AsyncSession):
        """Recover pending tasks from database"""
        logger.info("🔄 Recovering pending tasks...")
        
        try:
            pending_summaries = await summary_crud.get_pending_summaries(db_session)
            for summary in pending_summaries:

                article = await article_crud.get_article_by_id(db_session, summary.article_id)

                if article and article.content:
                    await self.submit_article_for_summarization(
                        db=db_session,
                        article_id=article.id,
                        article_content=article.content,
                        article_title=article.title,
                        quality_level=summary.quality_level
                    )
                    logger.info(f"🔄 Recovered pending summary task for article {article.id}")
            
            logger.info(f"✅ Recovered {len(pending_summaries)} pending summarization tasks")
            
        except Exception as e:
            logger.error(f"❌ Error recovering pending tasks: {e}")
    
    # YET UNUSED METHODS
    async def get_active_tasks_count(self) -> int:
        """Get number of actively processing tasks"""
        return len(self.active_tasks)
    
    def get_all_task_statuses(self) -> Dict[str, Dict]:
        """Get status of all tasks"""
        return self.task_status.copy()
    
    def get_queue_sizes(self) -> Dict[str, int]:
        """Get current queue sizes"""
        return {
            'aggregation': self.aggregation_queue.qsize(),
            'summarization': self.summarization_queue.qsize()
        }
    
    
    #------------------------------------------------------------------
    # async def submit_article_for_summarization(
    #     self, 
    #     db: AsyncSession,
    #     article_id: int,
    #     article_content: str,
    #     article_title: str,
    #     preferred_provider: Optional[str] = None,
    #     quality_level: str = "standard"
    # ) -> str:
    #     """
    #     Submit article for background summarization
    #     Returns task_id for status tracking
    #     """
    #     task_id = str(uuid.uuid4())
        
    #     try:
    #         summary = Summary(
    #             article_id=article_id,
    #             task_id=task_id,
    #             status='pending',
    #             content='',  
    #             provider='', 
    #             model_name='',
    #             quality_level=quality_level,
    #             word_count=0,
    #             char_count=0,
    #             processing_time_ms=0,
    #             is_successful=False
    #         )
    #         summary_create = SummaryCreate(**summary.__dict__)
    #         summary_created = await summary_crud.create_summary(db, summary_create)
            
    #         self.task_status[task_id] = {
    #             'task_id': task_id,
    #             'article_id': article_id,
    #             'article_title': article_title,
    #             'status': 'pending',
    #             'submitted_at': datetime.now(),
    #             'started_at': None,
    #             'completed_at': None,
    #             'preferred_provider': preferred_provider,
    #             'quality_level': quality_level,
    #             'error': None,
    #             'summary_id': summary_created.id
    #         }
            
    #         task_data = {
    #             'task_id': task_id,
    #             'db': db,
    #             'article_id': article_id,
    #             'article_content': article_content,
    #             'article_title': article_title,
    #             'preferred_provider': preferred_provider,
    #             'quality_level': quality_level
    #         }
            
    #         await self.task_queue.put(task_data)
    #         logger.info(f"📥 Submitted article {article_id} for background summarization. Task: {task_id}")
            
    #         return task_id
            
    #     except Exception as e:
    #         await db.rollback()
    #         logger.error(f"❌ Failed to submit article {article_id} for summarization: {e}")
    #         raise
    
    
    # async def _process_single_task(self, task_data: dict):
    #     """
    #     Process a single summarization task
    #     """
    #     task_id = task_data['task_id']
    #     db = task_data['db']
        
    #     try:
    #         self.task_status[task_id].update({
    #             'status': 'processing',
    #             'started_at': datetime.now()
    #         })
            
    #         await self._update_summary_status(db, task_id, 'processing', started_at=datetime.now())
            
    #         logger.info(f"🔄 Processing task {task_id} for article {task_data['article_id']}")
            
    #         summary = await self._process_with_pipeline(db, task_data)
            
    #         if summary and summary.is_successful:
    #             self.task_status[task_id].update({
    #                 'status': 'completed',
    #                 'completed_at': datetime.now(),
    #                 'summary_id': summary.id
    #             })
    #             logger.info(f"✅ Task {task_id} completed successfully. Summary ID: {summary.id}")
    #         else:
    #             error_msg = "Summarization failed"
    #             if summary and summary.error_message:
    #                 error_msg = summary.error_message
                    
    #             self.task_status[task_id].update({
    #                 'status': 'failed',
    #                 'completed_at': datetime.now(),
    #                 'error': error_msg
    #             })
    #             await self._update_summary_status(db, task_id, 'failed', error_message=error_msg)
                
    #     except Exception as e:
    #         error_msg = str(e)
    #         self.task_status[task_id].update({
    #             'status': 'error',
    #             'completed_at': datetime.now(),
    #             'error': error_msg
    #         })
    #         await self._update_summary_status(db, task_id, 'error', error_message=error_msg)
    #         logger.error(f"💥 Task {task_id} error: {e}")
        
    #     finally:
    #         self.active_tasks.pop(task_id, None)
    
    # async def _process_with_pipeline(self, db: AsyncSession, task_data: dict) -> Optional[Summary]:
    #     try:
    #         article = await article_crud.get_article_by_id(db, task_data['article_id'])
            
    #         if article is None:
    #             raise ValueError(f"Article {task_data['article_id']} not found")
            
    #         summary = await summary_pipeline.process_article(
    #             db=db,
    #             article=article,
    #             preferred_provider=task_data['preferred_provider'],
    #             quality_level=task_data['quality_level']
    #         )
            
    #         return summary
        
    #     except Exception as e:
    #         logger.error(f"❌ Pipeline processing error for article {task_data['article_id']}: {e}")
    #         return None
    

    # async def _update_summary_status(
    #     self, 
    #     db: AsyncSession, 
    #     task_id: str, 
    #     status: str, 
    #     started_at: datetime = None,
    #     error_message: str = None
    # ):
    #     """Update summary status in database"""
    #     from sqlalchemy import update
        
    #     try:
    #         update_data = {'status': status}
    #         if started_at:
    #             update_data['started_at'] = started_at
    #         if error_message:
    #             update_data['error_message'] = error_message
    #         if status in ['completed', 'failed', 'error']:
    #             update_data['completed_at'] = datetime.now()
            
    #         await db.execute(
    #             update(Summary)
    #             .where(Summary.task_id == task_id)
    #             .values(update_data)
    #         )
    #         await db.commit()
            
    #     except Exception as e:
    #         await db.rollback()
    #         logger.error(f"❌ Failed to update summary status for task {task_id}: {e}")
    #         raise
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get status of a specific task"""
        return self.task_status.get(task_id)
    
    # async def _get_task_status_from_db(self, task_id: str) -> Optional[dict]:
    #     """Get task status from database"""
        
    #     async with AsyncSessionLocal() as db:
    #         try:
    #             result = await db.execute(
    #                 select(Summary).where(Summary.task_id == task_id)
    #             )
    #             summary = result.scalar_one_or_none()
                
    #             if not summary:
    #                 return None
                
    #             task_status = {
    #                 'task_id': task_id,
    #                 'article_id': summary.article_id,
    #                 'article_title': self._get_article_title_from_db(db, summary.article_id),
    #                 'status': summary.status,
    #                 'submitted_at': summary.created_at,
    #                 'started_at': summary.started_at,
    #                 'completed_at': summary.completed_at,
    #                 'preferred_provider': None,  
    #                 'quality_level': summary.quality_level,
    #                 'error': summary.error_message,
    #                 'summary_id': summary.id
    #             }
                
    #             self.task_status[task_id] = task_status
                
    #             return task_status
                
    #         except Exception as e:
    #             logger.error(f"Error retrieving task status from database for {task_id}: {e}")
    #             return None

    # async def _get_article_title_from_db(self, db, article_id: int) -> str:
    #     """Get article title from database"""
        
    #     try:
    #         result = await db.execute(
    #             select(Article.title).where(Article.id == article_id)
    #         )
    #         title = result.scalar_one_or_none()
    #         return title or "Unknown Article"
    #     except Exception:
    #         return "Unknown Article"
    
    async def get_article_tasks(self, article_id: int) -> list:
        """Get all tasks for a specific article"""
        return [
            status for status in self.task_status.values() 
            if status['article_id'] == article_id
        ]
    
    async def get_pending_tasks_count(self) -> int:
        """Get number of pending tasks in queue"""
        return self.task_queue.qsize()
    
    # async def recover_pending_tasks(self, db) -> None:
    #     """Recover pending tasks from database on startup"""

    #     try:
    #         result = await db.execute(
    #             select(Summary).where(Summary.status.in_(['pending', 'processing']))
    #         )
    #         pending_summaries = result.scalars().all()
            
    #         for summary in pending_summaries:
    #             task_id = summary.task_id
    #             article_id = summary.article_id
                
    #             article_result = await db.execute(
    #                 select(Article).where(Article.id == article_id)
    #             )
    #             article = article_result.scalar_one_or_none()
                
    #             if not article:
    #                 continue
                
    #             task_data = {
    #                 'task_id': task_id,
    #                 'db': db,
    #                 'article_id': article_id,
    #                 'article_content': article.content,
    #                 'article_title': article.title,
    #                 'preferred_provider': None,
    #                 'quality_level': summary.quality_level
    #             }
                
    #             await self.task_queue.put(task_data)
                
    #             self.task_status[task_id] = {
    #                 'task_id': task_id,
    #                 'article_id': article_id,
    #                 'article_title': article.title,
    #                 'status': summary.status,
    #                 'submitted_at': summary.created_at,
    #                 'started_at': summary.started_at,
    #                 'completed_at': summary.completed_at,
    #                 'preferred_provider': None,
    #                 'quality_level': summary.quality_level,
    #                 'error': summary.error_message,
    #                 'summary_id': summary.id
    #             }
                
    #         logger.info(f"♻️ Recovered {len(pending_summaries)} pending tasks from database")
            
    #     except Exception as e:
    #         logger.error(f"❌ Failed to recover pending tasks: {e}")    
    
    # async def _cleanup_completed_tasks(self):
    #     """Clean up old completed tasks to prevent memory leaks"""
    #     current_time = datetime.now()
    #     tasks_to_remove = []
        
    #     for task_id, status in self.task_status.items():
    #         if status['status'] in ['completed', 'failed', 'error']:
    #             # Remove tasks older than 1 hour from memory
    #             if status['completed_at'] and (current_time - status['completed_at']).total_seconds() > 3600:
    #                 tasks_to_remove.append(task_id)
        
    #     for task_id in tasks_to_remove:
    #         self.task_status.pop(task_id, None)
    
    # async def shutdown(self):
    #     """Gracefully shutdown the task manager"""
    #     logger.info("🛑 Shutting down background task manager...")
    #     self.is_running = False
        
    #     # Wait for current tasks to complete (with timeout)
    #     if self.active_tasks:
    #         logger.info(f"Waiting for {len(self.active_tasks)} active tasks to complete...")
    #         try:
    #             await asyncio.wait_for(
    #                 asyncio.gather(*self.active_tasks.values(), return_exceptions=True),
    #                 timeout=30.0
    #             )
    #         except asyncio.TimeoutError:
    #             logger.warning("Timeout waiting for active tasks to complete")
        
    #     logger.info("✅ Background task manager shutdown complete")

task_manager = BackgroundTaskManager()

