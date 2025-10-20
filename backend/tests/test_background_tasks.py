import pytest
from unittest.mock import patch
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.background_tasks import BackgroundTaskManager, task_manager
from app.models.article import Article
from app.models.summary import Summary
from app.models.topic import Topic


class TestBackgroundTaskManager:
    """Test the BackgroundTaskManager with proper async handling"""
    
    @pytest.fixture(autouse=True)
    def setup_manager(self):
        """Reset task manager before each test"""
        self.manager = BackgroundTaskManager()
        yield
        # Cleanup after test
        self.manager.task_status.clear()
        self.manager.active_tasks.clear()
    
    @pytest.mark.asyncio
    async def test_submit_article_for_summarization_success(self, db_session, sample_article):
        """Test successful article submission for summarization"""
        article = sample_article
        
        print(f"📝 Testing with article: {article.title} (ID: {article.id})")
        
        task_id = await self.manager.submit_article_for_summarization(
            db=db_session,
            article_id=article.id,
            article_content=article.content,
            article_title=article.title
        )
        
        # Verify task was created
        assert task_id is not None
        assert len(task_id) == 36 
        
        # Verify task status was stored in memory
        status = await self.manager.get_task_status(task_id)
        assert status is not None
        assert status['status'] == 'pending'
        assert status['article_id'] == article.id
        assert status['article_title'] == article.title

        from sqlalchemy import select
        result = await db_session.execute(
            select(Summary).where(Summary.task_id == task_id)
        )
        summary = result.scalar_one_or_none()
        assert summary is not None
        assert summary.article_id == article.id
        assert summary.status == 'pending'
        assert summary.task_id == task_id
        
        print(f"✅ Successfully created task {task_id} and summary record")

    @pytest.mark.asyncio
    async def test_submit_article_database_failure(self, db_session, sample_article):
        """Test handling of database failures during submission"""
        article = sample_article
        
        print("🧪 Testing database failure handling")
        
        class MockFailingSession:
            def __init__(self):
                self.add_called = False
                self.commit_called = False
                self.refresh_called = False
            
            async def __aenter__(self):
                return self
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass
            
            async def commit(self):
                self.commit_called = True
                raise Exception("Simulated database error")
            
            def add(self, obj):
                self.add_called = True
            
            async def refresh(self, obj):
                self.refresh_called = True
            
            async def rollback(self):
                pass 
            
            async def close(self):
                pass 
        
        failing_session = MockFailingSession()
        
        with pytest.raises(Exception) as exc_info:
            await self.manager.submit_article_for_summarization(
                db=failing_session,
                article_id=article.id,
                article_content=article.content,
                article_title=article.title
            )
        
        assert "Simulated database error" in str(exc_info.value)
        
        assert failing_session.add_called, "add() should have been called"
        assert failing_session.commit_called, "commit() should have been called"
        
        print("✅ Database failure handled correctly")
        
    @pytest.mark.asyncio
    async def test_task_processing_success(self, db_session, sample_article):
        """Test successful task processing"""
        article = sample_article
        
        print("🧪 Testing successful task processing")
        
        task_id = await self.manager.submit_article_for_summarization(
            db=db_session,
            article_id=article.id,
            article_content=article.content,
            article_title=article.title
        )
        
        mock_summary = Summary(
            id=999,
            article_id=article.id,
            content="Test summary content",
            provider="test-provider",
            model_name="test-model",
            quality_level="standard",
            word_count=10,
            char_count=100,
            processing_time_ms=500,
            is_successful=True,
            task_id=task_id,
            status="completed"
        )
        
        with patch('app.core.background_tasks.summary_pipeline.process_article') as mock_pipeline:
            mock_pipeline.return_value = mock_summary
            
            task_data = {
                'task_id': task_id,
                'db': db_session,
                'article_id': article.id,
                'article_content': article.content,
                'article_title': article.title,
                'preferred_provider': None, 
                'quality_level': 'standard' 
            }
            
            await self.manager._process_single_task(task_data)
            
            status = await self.manager.get_task_status(task_id)
            assert status['status'] == 'completed'
            assert status['started_at'] is not None
            assert status['completed_at'] is not None
            
            print("✅ Task processing success handled correctly")


class TestGlobalTaskManager:
    """Test the global task manager instance"""
    
    @pytest.mark.asyncio
    async def test_global_instance(self):
        """Test global instance properties"""
        print("🧪 Testing global task manager instance")
        
        assert task_manager is not None
        assert isinstance(task_manager, BackgroundTaskManager)
        assert task_manager.is_running == True
        
        print("✅ Global instance is properly initialized")


class TestBackgroundTaskIntegration:
    """Integration tests for background tasks"""
    
    @pytest.mark.asyncio
    async def test_multiple_article_submission(self, db_session, sample_topic):
        """Test submitting multiple articles"""
        print("🧪 Testing multiple article submission")
        
        topic = sample_topic
        
        articles = []
        for i in range(2):
            article = Article(
                title=f"Integration Test Article {i}",
                url=f"https://example.com/integration-test-{i}",
                content=f"This is integration test article content {i}",
                source="test",
                topic_id=topic.id
            )
            db_session.add(article)
            articles.append(article)
        
        await db_session.commit()
        
        for article in articles:
            await db_session.refresh(article)
        
        task_ids = []
        for article in articles:
            task_id = await task_manager.submit_article_for_summarization(
                db=db_session,
                article_id=article.id,
                article_content=article.content,
                article_title=article.title
            )
            task_ids.append(task_id)
        
        assert len(task_ids) == 2
        assert len(set(task_ids)) == 2
        
        for task_id in task_ids:
            status = await task_manager.get_task_status(task_id)
            assert status['status'] == 'pending'
        
        print(f"✅ Successfully submitted {len(task_ids)} articles")