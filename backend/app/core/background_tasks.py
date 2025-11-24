import asyncio
from enum import Enum
from typing import Dict, List, Optional
import uuid
import traceback
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core import setup_colored_logging, engine
from app.services import summary_pipeline, aggregation_service
from app.crud import article as article_crud
from app.crud import summary as summary_crud
from app.schemas import SummaryCreate

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

        self.async_session_factory = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
  
    async def start_processing(self):
        """Start processing both aggregation and summarization tasks"""
        if self.is_running:
            logger.warning("⚠️ Background task processor already running")
            return
            
        self.is_running = True
        logger.info("🔄 Starting background task processors...")
        asyncio.create_task(self._process_aggregation_tasks())
        logger.info("✅ Aggregation task processor started")
        
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


    async def _process_aggregation_tasks(self):
        """Process aggregation tasks from the queue"""
        logger.info("🔄 Aggregation task processor started")
        
        while self.is_running:
            try:
                active_aggregation_count = len([
                    task_id for task_id, status in self.task_status.items()
                    if status.get('type') == TaskType.AGGREGATION and status.get('status') == 'processing'
                ])
                
                if active_aggregation_count >= self.max_concurrent_aggregations:
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
                logger.error(f"🔍 Stack trace: {traceback.format_exc()}")

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
                
                task.add_done_callback(lambda t, tid=task_data['task_id']: self._handle_task_completion(tid))
                
            except asyncio.TimeoutError:
                continue  # No tasks in queue, continue waiting
            except Exception as e:
                logger.error(f"❌ Error in summarization worker {worker_id}: {e}")

    async def _execute_summarization_task(self, task_data: Dict, worker_id: int) -> Dict:
        """Execute a summarization task"""
        task_id = task_data['task_id']
        article_id = task_data['article_id']
        
        try:
            logger.info(f"🔄 Worker {worker_id} starting summarization: {task_id} for article {article_id}")
            
            async with self.async_session_factory() as db_session:
                article = await article_crud.get_article_by_id(db_session, article_id)
                if article:
                    summary = await summary_pipeline.process_article(
                        db=db_session,
                        article=article,
                        preferred_provider=task_data.get('preferred_provider'),
                        quality_level=task_data.get('quality_level', 'standard')
                    )
                
                    if summary:
                        self.task_status[task_id].update({
                            'completed_at': datetime.now(),
                            'status': 'completed',
                            'summary_id': summary.id,
                            'provider_used': summary.provider,
                            'processing_time_ms': summary.processing_time_ms
                        })
                        
                        return {'success': True, 'summary_id': summary.id}
                    
        except Exception as e:
            logger.error(f"❌ Summarization failed (article id): ({task_id}) - {e}")

            self.task_status[task_id].update({
                'completed_at': datetime.now(),
                'status': 'failed',
                'error': str(e)
            })
            
            try:
                async with self.async_session_factory() as db_session:
                    summary_record = await summary_crud.get_summary_by_task_id(db_session, task_id)
                    if summary_record:
                        await summary_crud.mark_summary_failed(db_session, summary_record.id, str(e))
            except Exception as db_error:
                logger.error(f"❌ Failed to update summary status in database: {db_error}")
            
            return {'success': False, 'error': str(e)}
    
    async def submit_articles_for_summarization(self, article_ids:List[int]):
        async with self.async_session_factory() as db_session:
            submit_articles = await article_crud.get_articles_by_ids(db_session, article_ids=article_ids, include_summary=False)

            task_ids = []
            for article in submit_articles:
                task_id = await self._submit_article_for_summarization(
                    db=db_session,
                    article_id=article.id,
                    article_content=article.content,
                    article_title=article.title,
                    quality_level="standard"
                )
                if task_id:
                    task_ids.append(task_id)
            
            return task_ids
    
    async def _submit_article_for_summarization(
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
            summary_create = SummaryCreate(
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
            summary_created = await summary_crud.create_summary(db, summary_create)

            if summary_created: 
                task_data = {
                    'task_id': task_id,
                    'type': TaskType.SUMMARIZATION,
                    'article_id': article_id,
                    'article_content': article_content,
                    'article_title': article_title,
                    'preferred_provider': preferred_provider,
                    'quality_level': quality_level,
                    'summary_id': summary_created.id,
                    'submitted_at': datetime.now(),
                    'status': 'pending'
                }
        
                await self.summarization_queue.put(task_data)
                self.task_status[task_id] = task_data
                return task_id
        
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to submit article {article_id} for summarization: {e}")
            raise
    

    def _handle_task_completion(self, task_id: str):
        """Handle task completion - remove from active tasks"""
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]
    
    # async def recover_pending_tasks(self, db_session: AsyncSession):
    #     """Recover pending tasks by creating new summaries and deleting old ones"""
    #     logger.info("🔄 Recovering pending tasks...")
        
    #     try:
    #         pending_summaries = await summary_crud.get_pending_summaries(db_session)
    #         recovered_count = 0
            
    #         for summary in pending_summaries:
    #             try:
    #                 article = await article_crud.get_article_by_id(db_session, summary.article_id)
                    
    #                 if not article or not article.content or len(article.content.strip()) < 50:
    #                     logger.warning(f"⚠️ Article {summary.article_id} not found or has insufficient content")
    #                     await summary_crud.mark_summary_failed(
    #                         db_session, 
    #                         summary.id, 
    #                         "Article not found or insufficient content"
    #                     )
    #                     continue
                    

    #                 await summary_crud.delete_summary(db_session, summary.id)
                    
    #                 task_id = await self._submit_article_for_summarization(
    #                     db=db_session,
    #                     article_id=article.id,
    #                     article_content=article.content,
    #                     article_title=article.title,
    #                     preferred_provider=summary.provider if summary.provider else None,
    #                     quality_level=summary.quality_level
    #                 )
                    
    #                 if task_id:
    #                     logger.info(f"🔄 Replaced pending summary {summary.id} with new task {task_id}")
    #                     recovered_count += 1
                        
    #             except Exception as e:
    #                 logger.error(f"❌ Error recovering summary {summary.id}: {e}")
    #                 await summary_crud.mark_summary_failed(db_session, summary.id, f"Recovery error: {str(e)}")
            
    #         await db_session.commit()
    #         logger.info(f"✅ Recovered {recovered_count} pending summarization tasks")
            
    #     except Exception as e:
    #         await db_session.rollback()
    #         logger.error(f"❌ Error in recover_pending_tasks: {e}")

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
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get status of a specific task"""
        return self.task_status.get(task_id)
    
    async def get_article_tasks(self, article_id: int) -> list:
        """Get all tasks for a specific article"""
        return [
            status for status in self.task_status.values() 
            if status['article_id'] == article_id
        ]
    
    async def get_pending_tasks_count(self) -> int:
        """Get number of pending tasks in queue"""
        return self.task_queue.qsize()
    
    async def recover_pending_tasks(self, db_session: AsyncSession):
        """Recover pending tasks by creating new summaries and deleting old ones"""
        logger.info("🔄 Recovering pending tasks...")
        
        try:
            pending_summaries_result = await summary_crud.get_pending_summaries(db_session)
            # Extract the actual Summary objects from the result
            pending_summaries = pending_summaries_result.scalars().all() if hasattr(pending_summaries_result, 'scalars') else pending_summaries_result
            
            recovered_count = 0
            
            for summary in pending_summaries:
                try:
                    article = await article_crud.get_article_by_id(db_session, summary.article_id)
                    
                    if not article or not article.content or len(article.content.strip()) < 50:
                        logger.warning(f"⚠️ Article {summary.article_id} not found or has insufficient content")
                        await summary_crud.mark_summary_failed(
                            db_session, 
                            summary.id, 
                            "Article not found or insufficient content"
                        )
                        continue
                    
                    # Delete the old pending summary
                    await summary_crud.delete_summary(db_session, summary.id)
                    
                    # Create a new summarization task
                    task_id = await self._submit_article_for_summarization(
                        db=db_session,
                        article_id=article.id,
                        article_content=article.content,
                        article_title=article.title,
                        preferred_provider=summary.provider if summary.provider else None,
                        quality_level=summary.quality_level
                    )
                    
                    if task_id:
                        logger.info(f"🔄 Replaced pending summary {summary.id} with new task {task_id}")
                        recovered_count += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error recovering summary {summary.id}: {e}")
                    await summary_crud.mark_summary_failed(db_session, summary.id, f"Recovery error: {str(e)}")
            
            await db_session.commit()
            logger.info(f"✅ Recovered {recovered_count} pending summarization tasks")
            
        except Exception as e:
            await db_session.rollback()
            logger.error(f"❌ Error in recover_pending_tasks: {e}")


task_manager = BackgroundTaskManager()

