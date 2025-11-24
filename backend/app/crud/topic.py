from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from app.models import Topic, Article
from app.schemas import TopicCreate, TopicUpdate


async def get_used_topics(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    source: Optional[str] = None,
    min_articles: int = 3 
) -> List[Topic]:
    """
    Get topics that have at least min_articles articles, optionally filtered by source.
    Also update articles with unpopular topics (less than min_articles) to 'other' topic.
    Returns empty list if no topics found.
    """

    try:
        # Step 1: Find the "other" topic (create if it doesn't exist)
        other_topic_result = await db.execute(
            select(Topic).where(Topic.name == "other")
        )
        other_topic = other_topic_result.scalar_one_or_none()
        
        if not other_topic:
            try:
                other_topic = Topic(name="other", description="Non exisiting category")
                db.add(other_topic)
                await db.flush() 
                await db.refresh(other_topic)
            except SQLAlchemyError as e:
                raise
        
        # Step 2: Find topics with less than min_articles (unpopular topics)
        unpopular_topics_query = (
            select(
                Article.topic_id,
                func.count(Article.id).label('article_count')
            )
            .where(Article.topic_id.is_not(None))
            .group_by(Article.topic_id)
            .having(func.count(Article.id) < min_articles)
        )
        
        if source:
            unpopular_topics_query = unpopular_topics_query.where(Article.source == source)
        
        unpopular_topics_result = await db.execute(unpopular_topics_query)
        unpopular_topic_ids = [row[0] for row in unpopular_topics_result.all()]
        
        # Step 3: Update articles with unpopular topics to "other" topic
        if unpopular_topic_ids:
            # Don't include the "other" topic itself in the update
            unpopular_topic_ids_to_update = [tid for tid in unpopular_topic_ids if tid != other_topic.id]
            
            if unpopular_topic_ids_to_update:
                try:
                    update_stmt = (
                        update(Article)
                        .where(Article.topic_id.in_(unpopular_topic_ids_to_update))
                        .values(topic_id=other_topic.id)
                    )
                    await db.execute(update_stmt)
                    await db.commit()
                except SQLAlchemyError as e:
                    await db.rollback()

        
        # Step 4: Get popular topics (original logic)
        topic_counts_query = (
            select(
                Article.topic_id,
                func.count(Article.id).label('article_count')
            )
            .where(Article.topic_id.is_not(None))
            .group_by(Article.topic_id)
            .having(func.count(Article.id) >= min_articles) 
        )
        
        if source:
            topic_counts_query = topic_counts_query.where(Article.source == source)
        
        topic_counts_query = topic_counts_query.subquery()
        
        topics_query = (
            select(Topic)
            .join(topic_counts_query, Topic.id == topic_counts_query.c.topic_id)
            .order_by(Topic.name)
            .offset(skip)
            .limit(limit)
        )
        
        topics_result = await db.execute(topics_query)
        topics = topics_result.scalars().all()
        
        return topics
        
    except SQLAlchemyError as e:
        try:
            await db.rollback()
        except Exception:
            pass
        raise
        
    except Exception as e:
        try:
            await db.rollback()
        except Exception:
            pass
        raise

async def get_used_topics_count(db: AsyncSession, source: Optional[str] = None) -> int:
    """
    Get count of distinct topics that have articles, optionally filtered by source.
    Returns 0 if no topics found.
    """

    try:
        query = select(func.count(Topic.id.distinct()))
        
        if source:
            query = (
                query
                .select_from(Topic)
                .join(Article, Topic.id == Article.topic_id)
                .where(Article.source == source)
                .where(Article.topic_id.is_not(None))
            )
        else:
            query = (
                query
                .select_from(Topic)
                .join(Article, Topic.id == Article.topic_id)
                .where(Article.topic_id.is_not(None))
            )
        
        result = await db.execute(query)
        count = result.scalar()
        
        return count or 0
        
    except SQLAlchemyError as e:
        raise
    except Exception as e:
        raise


# --------------------------------------------------------------------------------------------------------

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

# async def get_used_topics(
#     db: AsyncSession, 
#     skip: int = 0, 
#     limit: int = 100,
#     source: Optional[str] = None,
#     min_articles: int = 3 
# ) -> List[Topic]:
#     """
#     Get topics that have at least min_articles articles, optionally filtered by source.
#     Also update articles with unpopular topics (less than min_articles) to 'other' topic.
#     """
#     from sqlalchemy import update
    
#     # Step 1: Find the "other" topic (create if it doesn't exist)
#     other_topic_result = await db.execute(
#         select(Topic).where(Topic.name == "other")
#     )
#     other_topic = other_topic_result.scalar_one_or_none()
    
#     if not other_topic:
#         # Create "other" topic if it doesn't exist
#         other_topic = Topic(name="other", description="Miscellaneous topics")
#         db.add(other_topic)
#         await db.flush()  # Flush to get the ID
#         await db.refresh(other_topic)
    
#     # Step 2: Find topics with less than min_articles (unpopular topics)
#     unpopular_topics_query = (
#         select(
#             Article.topic_id,
#             func.count(Article.id).label('article_count')
#         )
#         .where(Article.topic_id.is_not(None))
#         .group_by(Article.topic_id)
#         .having(func.count(Article.id) < min_articles)
#     )
    
#     if source:
#         unpopular_topics_query = unpopular_topics_query.where(Article.source == source)
    
#     unpopular_topics_result = await db.execute(unpopular_topics_query)
#     unpopular_topic_ids = [row[0] for row in unpopular_topics_result.all()]
    
#     # Step 3: Update articles with unpopular topics to "other" topic
#     if unpopular_topic_ids:
#         # Don't include the "other" topic itself in the update
#         unpopular_topic_ids_to_update = [tid for tid in unpopular_topic_ids if tid != other_topic.id]
        
#         if unpopular_topic_ids_to_update:
#             update_stmt = (
#                 update(Article)
#                 .where(Article.topic_id.in_(unpopular_topic_ids_to_update))
#                 .values(topic_id=other_topic.id)
#             )
#             await db.execute(update_stmt)
#             await db.commit()
    
#     # Step 4: Get popular topics (original logic)
#     topic_counts_query = (
#         select(
#             Article.topic_id,
#             func.count(Article.id).label('article_count')
#         )
#         .where(Article.topic_id.is_not(None))
#         .group_by(Article.topic_id)
#         .having(func.count(Article.id) >= min_articles) 
#     )
    
#     if source:
#         topic_counts_query = topic_counts_query.where(Article.source == source)
    
#     topic_counts_query = topic_counts_query.subquery()
    
#     topics_query = (
#         select(Topic)
#         .join(topic_counts_query, Topic.id == topic_counts_query.c.topic_id)
#         .order_by(Topic.name)
#         .offset(skip)
#         .limit(limit)
#     )
    
#     topics_result = await db.execute(topics_query)
#     topics = topics_result.scalars().all()
    
#     return topics



# async def get_used_topics_count(db: AsyncSession, source: Optional[str] = None) -> int:
#     query = select(func.count(Topic.id))

#     if source:
#         query.where(Article.source == source)
    
#     query.where(Article.topic_id.is_not(None))
    
#     result = await db.execute(query)
#     return result.scalar_one()

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