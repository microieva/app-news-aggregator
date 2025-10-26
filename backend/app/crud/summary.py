from sqlalchemy.orm import joinedload
from typing import List, Optional, Dict, Any
from sqlalchemy import desc, func, select
from app.models.summary import Summary
from app.models.article import Article
from app.models.topic import Topic
from app.schemas.summary import SummaryCreate, SummaryUpdate
from sqlalchemy.ext.asyncio import AsyncSession


async def create_summary(db: AsyncSession, summary: SummaryCreate) -> Summary:
    db_summary = Summary(
        article_id=summary.article_id,
        content=summary.content,
        provider=summary.provider,
        model_name=summary.model_name,
        quality_level=summary.quality_level,
        word_count=summary.word_count,
        char_count=summary.char_count,
        processing_time_ms=summary.processing_time_ms,
        is_successful=True,
        error_message=None,
        retry_count=0
    )
    db.add(db_summary)
    await db.commit()
    await db.refresh(db_summary)
    return db_summary

async def get_summary_by_article_id(db: AsyncSession, article_id: int) -> Optional[Summary]:
    result = await db.execute(
        select(Summary).where(Summary.article_id == article_id)
    )
    return result.scalar_one_or_none()

async def get_pending_summaries(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50
) -> List[Summary]:
    """
    Get summaries that are pending (not successful).
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of pending Summary objects
    """
    query = (
        select(Summary)
        .where(Summary.is_successful == False)
        .order_by(desc(Summary.id))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()

async def get_summary(db: AsyncSession, summary_id: int) -> Optional[Summary]:
    result = await db.execute(
        select(Summary).where(Summary.id == summary_id)
    )
    return result.scalar_one_or_none()

async def mark_summary_failed(db: AsyncSession, summary_id, str):
    failed_summary = get_summary(db, summary_id)
    if failed_summary:
        failed_summary['is_successful'] = False
        failed_summary['status'] = "failed"
        failed_summary['error_message'] = str
        summary_update = SummaryUpdate(**failed_summary)

        await update_summary(db, summary_id, summary_update)

async def get_summaries_by_provider(
    db: AsyncSession, 
    provider: str, 
    skip: int = 0, 
    limit: int = 50
) -> List[Summary]:
    """
    Get summaries by provider.
    
    Args:
        db: Database session
        provider: Provider name
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of Summary objects
    """
    query = (
        select(Summary)
        .where(Summary.provider == provider)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


async def get_summaries_with_articles(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    provider: Optional[str] = None,
    quality_level: Optional[str] = None
) -> List[Summary]:
    """
    Get summaries with their associated articles.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        provider: Filter by provider
        quality_level: Filter by quality level
        
    Returns:
        List of Summary objects with articles loaded
    """
    query = select(Summary).options(joinedload(Summary.article))
    
    if provider:
        query = query.where(Summary.provider == provider)
    
    if quality_level:
        query = query.where(Summary.quality_level == quality_level)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def update_summary(db: AsyncSession, summary_id: int, summary_update: SummaryUpdate) -> Optional[Summary]:
    """
    Update a summary.
    
    Args:
        db: Database session
        summary_id: Summary ID to update
        summary_update: Summary update data
        
    Returns:
        Updated Summary object or None if not found
    """
    result = await db.execute(
        select(Summary).where(Summary.id == summary_id)
    )
    db_summary = result.scalar_one_or_none()
    
    if db_summary:
        update_data = summary_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_summary, field, value)
        await db.commit()
        await db.refresh(db_summary)
    return db_summary


async def delete_summary(db: AsyncSession, summary_id: int) -> bool:
    """
    Delete a summary.
    
    Args:
        db: Database session
        summary_id: Summary ID to delete
        
    Returns:
        True if deleted, False if not found
    """
    result = await db.execute(
        select(Summary).where(Summary.id == summary_id)
    )
    db_summary = result.scalar_one_or_none()
    
    if db_summary:
        await db.delete(db_summary)
        await db.commit()
        return True
    return False


async def get_summary_stats(db: AsyncSession, provider: Optional[str] = None) -> Dict[str, Any]:
    """
    Get statistics about summaries.
    
    Args:
        db: Database session
        provider: Filter by provider
        
    Returns:
        Dictionary with summary statistics
    """

    conditions = []
    if provider:
        conditions.append(Summary.provider == provider)
    
    total_query = select(func.count(Summary.id))
    if conditions:
        total_query = total_query.where(*conditions)
    result = await db.execute(total_query)
    total = result.scalar_one()
    
    successful_conditions = conditions + [Summary.is_successful == True]
    successful_query = select(func.count(Summary.id)).where(*successful_conditions)
    result = await db.execute(successful_query)
    successful = result.scalar_one()
    
    failed_conditions = conditions + [Summary.is_successful == False]
    failed_query = select(func.count(Summary.id)).where(*failed_conditions)
    result = await db.execute(failed_query)
    failed = result.scalar_one()
    
    avg_query = select(func.avg(Summary.processing_time_ms))
    if conditions:
        avg_query = avg_query.where(*conditions)
    result = await db.execute(avg_query)
    avg_processing_time = result.scalar_one() or 0
    
    provider_query = select(Summary.provider, func.count(Summary.id))
    if conditions:
        provider_query = provider_query.where(*conditions)
    provider_query = provider_query.group_by(Summary.provider)
    result = await db.execute(provider_query)
    provider_distribution = {provider: count for provider, count in result.all()}
    
    quality_query = select(Summary.quality_level, func.count(Summary.id))
    if conditions:
        quality_query = quality_query.where(*conditions)
    quality_query = quality_query.group_by(Summary.quality_level)
    result = await db.execute(quality_query)
    quality_distribution = {quality: count for quality, count in result.all()}
    
    success_rate = (successful / total * 100) if total > 0 else 0
    
    return {
        "total_summaries": total,
        "successful_summaries": successful,
        "failed_summaries": failed,
        "success_rate": round(success_rate, 2),
        "average_processing_time_ms": round(avg_processing_time, 2),
        "provider_distribution": provider_distribution,
        "quality_distribution": quality_distribution
    }

async def get_summaries_by_topic(
    db: AsyncSession,
    topic_id: int,
    skip: int = 0,
    limit: int = 50
) -> List[Summary]:
    """
    Get summaries for articles in a specific topic.
    
    Args:
        db: Database session
        topic_id: Topic ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of Summary objects
    """
    query = (
        select(Summary)
        .join(Article, Summary.article_id == Article.id)
        .where(Article.topic_id == topic_id)
        .options(joinedload(Summary.article))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


async def get_summary_with_article_details(db: AsyncSession, summary_id: int) -> Optional[Dict[str, Any]]:
    """
    Get summary with detailed article and topic information.
    
    Args:
        db: Database session
        summary_id: Summary ID
        
    Returns:
        Dictionary with summary and related details or None if not found
    """
    result = await db.execute(
        select(Summary, Article, Topic)
        .join(Article, Summary.article_id == Article.id)
        .join(Topic, Article.topic_id == Topic.id)
        .where(Summary.id == summary_id)
    )
    row = result.first()
    
    if row:
        summary, article, topic = row
        return {
            "summary": summary,
            "article_title": article.title,
            "article_url": article.url,
            "topic_name": topic.name,
            "topic_description": topic.description
        }
    
    return None


async def bulk_create_summaries(db: AsyncSession, summaries: List[SummaryCreate]) -> List[Summary]:
    """
    Create multiple summaries in bulk.
    
    Args:
        db: Database session
        summaries: List of summary data to create
        
    Returns:
        List of created Summary objects
    """
    db_summaries = []
    for summary_data in summaries:

        existing = await get_summary_by_article_id(db, summary_data.article_id)
        if not existing:
            db_summary = Summary(
                article_id=summary_data.article_id,
                content=summary_data.content,
                provider=summary_data.provider,
                model_name=summary_data.model_name,
                quality_level=summary_data.quality_level,
                word_count=summary_data.word_count,
                char_count=summary_data.char_count,
                processing_time_ms=summary_data.processing_time_ms,
                is_successful=True,
                error_message=None,
                retry_count=0
            )
            db_summaries.append(db_summary)
            db.add(db_summary)
    
    await db.commit()
    
    for summary in db_summaries:
        await db.refresh(summary)
    
    return db_summaries