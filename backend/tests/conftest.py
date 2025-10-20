import asyncio
import pytest_asyncio
from sqlalchemy import text
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import AsyncSessionLocal, Base, engine
from app.models.article import Article
from app.models.topic import Topic
from app.models.summary import Summary

pytest_plugins = ('pytest_asyncio',)

@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def db_session():
    """Create a database session using your actual AsyncSessionLocal"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    session = AsyncSessionLocal()
    
    try:
        yield session
    finally:
        await session.close()

@pytest_asyncio.fixture
async def test_data(db_session):
    """Create test data and ensure it exists"""
    # Clean up first
    await db_session.execute(text("DELETE FROM summaries"))
    await db_session.execute(text("DELETE FROM articles"))
    await db_session.execute(text("DELETE FROM topics"))
    await db_session.commit()
    
    # Create test topic
    topic = Topic(name="Test Topic", description="Test Description")
    db_session.add(topic)
    await db_session.commit()
    await db_session.refresh(topic)
    
    # Create test article
    article = Article(
        title="Test Article",
        url="https://example.com/test-background-tasks",
        content="This is a test article content for background processing.",
        source="test",
        topic_id=topic.id
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)
    
    return {"topic": topic, "article": article}

@pytest_asyncio.fixture
async def sample_topic(test_data):
    """Get the sample topic"""
    return test_data["topic"]

@pytest_asyncio.fixture
async def sample_article(test_data):
    """Get the sample article"""
    return test_data["article"]