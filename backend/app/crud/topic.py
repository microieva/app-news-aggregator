from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import distinct, select, func
from typing import List, Optional
from app.models import Topic, Article
from app.schemas.topic import TopicCreate, TopicUpdate

async def create_topic(db: AsyncSession, *, obj_in: TopicCreate) -> Topic:
    db_obj = Topic(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_topic_by_name(db: AsyncSession, name: str) -> Optional[Topic]:
    """Get a topic by name"""
    result = await db.execute(
        select(Topic).where(Topic.name == name)
    )
    return result.scalar_one_or_none()

async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Topic]:
    """Get all topics with pagination"""
    query = select(Topic).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_topic_id_by_name(name: str, db: AsyncSession) -> Optional[int]:
    """Get topic ID by name"""
    result = await db.execute(
        select(Topic.id).where(Topic.name == name)
    )
    topic_id = result.scalar_one_or_none()
    return topic_id

async def get_used_topics(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Topic]:
    topic_ids_query = (
        select(distinct(Article.topic_id))
        .where(Article.topic_id.is_not(None))
        .offset(skip)
        .limit(limit)
    )
    
    topic_ids_result = await db.execute(topic_ids_query)
    topic_ids = topic_ids_result.scalars().all()
    
    if not topic_ids:
        return []
    
    topics_query = (
        select(Topic)
        .where(Topic.id.in_(topic_ids))
        .order_by(Topic.name) 
    )
    
    topics_result = await db.execute(topics_query)
    topics = topics_result.scalars().all()
    
    return topics

async def get_used_topics_count(db: AsyncSession) -> int:
    query = select(func.count(Topic.id)).where(Article.topic_id.is_not(None))
    result = await db.execute(query)
    return result.scalar_one()

# ------- not confirmed if used anywhere -------

async def get_topic(db: AsyncSession, topic_id: int) -> Optional[Topic]:
    """Get a topic by ID"""
    result = await db.execute(
        select(Topic).where(Topic.id == topic_id)
    )
    return result.scalar_one_or_none()

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