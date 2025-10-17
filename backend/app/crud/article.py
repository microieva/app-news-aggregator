from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict, Any
from sqlalchemy import desc, func, or_
from app.models.article import Article
from app.models.summary import Summary
from app.schemas.article import ArticleCreate, ArticleUpdate

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload 


async def create_article(db: AsyncSession, article: ArticleCreate) -> Article:
    """Create a new article - async version"""
    db_article = Article(
        title=article.title,
        url=article.url,
        content=article.content,
        source=article.source,
        author=article.author,
        published_at=article.published_at,
        image_url=article.image_url,
        topic_id=article.topic_id,
        is_processed=False
    )
    db.add(db_article)
    await db.commit()
    await db.refresh(db_article)
    return db_article

async def get_article_async(db: AsyncSession, article_id: int) -> Article:
    """Get an article by ID - async version"""
    result = await db.execute(select(Article).where(Article.id == article_id))
    return result.scalar_one_or_none()

async def get_article(db: AsyncSession, article_id: int, include_summary: bool = True) -> Optional[Article]:
    """Get an article by ID, optionally including its summary"""
    query = select(Article).where(Article.id == article_id)
    
    if include_summary:
        query = query.options(selectinload(Article.summary))
    
    result = await db.execute(query)    
    return result.scalar_one_or_none()

async def get_articles_by_topic(
    db: AsyncSession, 
    topic_id: int, 
    skip: int = 0, 
    limit: int = 50,
    sort_by: str = "published_at",
    sort_order: str = "desc",
    include_summaries: bool = True,
    only_processed: bool = False,
    only_unprocessed: bool = False
) -> List[Article]:
    """Get articles by topic ID with sorting and filtering options"""
    query = select(Article).where(Article.topic_id == topic_id)
    
    if only_processed:
        query = query.where(Article.is_processed == True)
    elif only_unprocessed:
        query = query.where(Article.is_processed == False)
    
    if sort_by == "published_at":
        if sort_order == "desc":
            query = query.order_by(desc(Article.published_at))
        else:
            query = query.order_by(Article.published_at)
    elif sort_by == "created_at":
        if sort_order == "desc":
            query = query.order_by(desc(Article.created_at))
        else:
            query = query.order_by(Article.created_at)
    elif sort_by == "title":
        if sort_order == "desc":
            query = query.order_by(desc(Article.title))
        else:
            query = query.order_by(Article.title)
    elif sort_by == "processing_status":
        if sort_order == "desc":
            query = query.order_by(desc(Article.is_processed))
        else:
            query = query.order_by(Article.is_processed)
    
    query = query.offset(skip).limit(limit)
    
    if include_summaries:
        query = query.options(selectinload(Article.summary))
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_articles_by_source(
    db: AsyncSession, 
    source: str, 
    skip: int = 0, 
    limit: int = 50,
    include_summaries: bool = True
) -> List[Article]:
    """Get articles by source"""
    query = select(Article).where(Article.source == source)
    query = query.offset(skip).limit(limit)
    
    if include_summaries:
        query = query.options(selectinload(Article.summary))
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_unprocessed_articles(
    db: AsyncSession, 
    topic_id: Optional[int] = None,
    skip: int = 0, 
    limit: int = 50
) -> List[Article]:
    """Get articles that haven't been processed (no summaries)"""
    query = select(Article).where(Article.is_processed == False)
    
    if topic_id:
        query = query.where(Article.topic_id == topic_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_processed_articles(
    db: AsyncSession, 
    topic_id: Optional[int] = None,
    skip: int = 0, 
    limit: int = 50,
    include_summaries: bool = True
) -> List[Article]:
    """Get articles that have been processed (have summaries)"""
    query = select(Article).where(Article.is_processed == True)
    
    if topic_id:
        query = query.where(Article.topic_id == topic_id)
    
    if include_summaries:
        query = query.options(selectinload(Article.summary))
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def create_articles_bulk(db: AsyncSession, articles: List[ArticleCreate]) -> List[Article]:
    """Create multiple articles in bulk"""
    db_articles = []
    
    for article_data in articles:
        result = await db.execute(
            select(Article).where(Article.url == article_data.url)
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            db_article = Article(
                title=article_data.title,
                url=article_data.url,
                content=article_data.content,
                source=article_data.source,
                author=article_data.author,
                published_at=article_data.published_at,
                image_url=article_data.image_url,
                topic_id=article_data.topic_id,
                is_processed=False, 
                processing_error=None
            )
            db_articles.append(db_article)
            db.add(db_article)
    
    await db.commit()
    
    for article in db_articles:
        await db.refresh(article)
    
    return db_articles

async def update_article(db: AsyncSession, article_id: int, article_update: ArticleUpdate) -> Optional[Article]:
    """Update an article"""
    result = await db.execute(
        select(Article).where(Article.id == article_id)
    )
    db_article = result.scalar_one_or_none()
    
    if db_article:
        update_data = article_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_article, field, value)
        await db.commit()
        await db.refresh(db_article)
    return db_article

async def mark_article_processed(db: AsyncSession, article_id: int) -> Optional[Article]:
    """Mark an article as successfully processed"""
    result = await db.execute(
        select(Article).where(Article.id == article_id)
    )
    db_article = result.scalar_one_or_none()
    
    if db_article:
        db_article.is_processed = True
        db_article.processing_error = None
        await db.commit()
        await db.refresh(db_article)
    return db_article

async def mark_article_failed(db: AsyncSession, article_id: int, error_message: str) -> Optional[Article]:
    """Mark an article as failed processing"""
    result = await db.execute(
        select(Article).where(Article.id == article_id)
    )
    db_article = result.scalar_one_or_none()
    
    if db_article:
        db_article.is_processed = False
        db_article.processing_error = error_message
        await db.commit()
        await db.refresh(db_article)
    return db_article

async def delete_article(db: AsyncSession, article_id: int) -> bool:
    """Delete an article (will cascade delete summary due to relationship)"""
    result = await db.execute(
        select(Article).where(Article.id == article_id)
    )
    db_article = result.scalar_one_or_none()
    
    if db_article:
        await db.delete(db_article) 
        await db.commit()
        return True
    return False

async def get_articles_count(db: AsyncSession, topic_id: Optional[int] = None) -> int:
    """Get total number of articles, optionally filtered by topic"""
    query = select(func.count(Article.id))
    
    if topic_id:
        query = query.where(Article.topic_id == topic_id)
    
    result = await db.execute(query)
    return result.scalar_one()

async def get_processing_stats(db: AsyncSession, topic_id: Optional[int] = None) -> Dict[str, Any]:
    """Get statistics about article processing status"""
    conditions = []
    if topic_id:
        conditions.append(Article.topic_id == topic_id)
    
    total_query = select(func.count(Article.id))
    if conditions:
        total_query = total_query.where(*conditions)
    
    result = await db.execute(total_query)
    total = result.scalar_one()
    
    processed_conditions = conditions + [Article.is_processed == True]
    processed_query = select(func.count(Article.id)).where(*processed_conditions)
    result = await db.execute(processed_query)
    processed = result.scalar_one()
    
    unprocessed_conditions = conditions + [Article.is_processed == False]
    unprocessed_query = select(func.count(Article.id)).where(*unprocessed_conditions)
    result = await db.execute(unprocessed_query)
    unprocessed = result.scalar_one()
    
    success_rate = (processed / total * 100) if total > 0 else 0
    
    return {
        "total_articles": total,
        "processed_articles": processed,
        "unprocessed_articles": unprocessed,
        "success_rate": round(success_rate, 2)
    }

async def get_articles_with_summaries(
    db: AsyncSession,
    topic_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50
) -> List[Article]:
    """Get articles that have summaries (eager load the summaries)"""
    query = (
        select(Article)
        .join(Summary, Article.id == Summary.article_id)
        .where(Article.is_processed == True)
    )
    
    if topic_id:
        query = query.where(Article.topic_id == topic_id)
    
    query = query.options(selectinload(Article.summary))
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def search_articles(
    db: AsyncSession,
    query_text: str,
    topic_id: Optional[int] = None,
    include_summaries: bool = True,
    skip: int = 0,
    limit: int = 50
) -> List[Article]:
    """Search articles by title and content"""
    search_query = f"%{query_text}%"
    
    query = select(Article).where(
        or_(
            Article.title.ilike(search_query),
            Article.content.ilike(search_query)
        )
    )
    
    if topic_id:
        query = query.where(Article.topic_id == topic_id)
    
    if include_summaries:
        query = query.options(selectinload(Article.summary))
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()