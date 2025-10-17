from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.models.topic import Topic
from app.schemas.topic import TopicCreate, TopicUpdate

async def get_topic(db: AsyncSession, topic_id: int) -> Optional[Topic]:
    """Get a topic by ID"""
    result = await db.execute(
        select(Topic).where(Topic.id == topic_id)
    )
    return result.scalar_one_or_none()

async def get_topic_by_name(db: AsyncSession, name: str) -> Optional[Topic]:
    """Get a topic by name"""
    result = await db.execute(
        select(Topic).where(Topic.name == name)
    )
    return result.scalar_one_or_none()

async def get_topics(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Topic]:
    """Get all topics with pagination"""
    query = select(Topic).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def create_topic(db: AsyncSession, topic: TopicCreate) -> Topic:
    """Create a new topic"""
    db_topic = Topic(
        name=topic.name,
        description=topic.description
    )
    db.add(db_topic)
    await db.commit()
    await db.refresh(db_topic)
    return db_topic

async def update_topic(db: AsyncSession, topic_id: int, topic_update: TopicUpdate) -> Optional[Topic]:
    """Update a topic"""
    result = await db.execute(
        select(Topic).where(Topic.id == topic_id)
    )
    db_topic = result.scalar_one_or_none()
    
    if db_topic:
        update_data = topic_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_topic, field, value)
        await db.commit()
        await db.refresh(db_topic)
    return db_topic

async def delete_topic(db: AsyncSession, topic_id: int) -> bool:
    """Delete a topic"""
    result = await db.execute(
        select(Topic).where(Topic.id == topic_id)
    )
    db_topic = result.scalar_one_or_none()
    
    if db_topic:
        await db.delete(db_topic)
        await db.commit()
        return True
    return False

async def get_topics_count(db: AsyncSession) -> int:
    """Get total number of topics"""
    result = await db.execute(select(func.count(Topic.id)))
    return result.scalar_one()