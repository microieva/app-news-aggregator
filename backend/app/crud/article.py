from datetime import datetime
from typing import List, Optional
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import selectinload

from app.models import Topic, Article
from app.schemas import ArticleCreate, SearchParams, TopicBase
from app.core.exceptions import DatabaseException


# async def create_article(db: AsyncSession, article: ArticleCreate) -> Article:
#     """Create a new article - async version"""

#     db_article = Article(
#         title=article.title,
#         url=article.url,
#         content=article.content,
#         source=article.source,
#         author=article.author,
#         published_at=article.published_at,
#         image_url=article.image_url,
#         topic_id=article.topic_id,
#         is_processed=False
#     )
    
#     db.add(db_article)
#     await db.commit()
#     await db.refresh(db_article)
#     return db_article

async def create_article(db: AsyncSession, article: ArticleCreate) -> Article:

    try:
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
        
    except IntegrityError as e:
        await db.rollback()
        raise DatabaseException(
            detail="Article creation failed due to data integrity violation (possibly duplicate URL)",
            context={
                "article_title": article.title,
                "article_url": article.url
            }
        )
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseException(
            detail="Failed to create article due to database error",
            context={
                "article_title": article.title,
                "article_url": article.url
            }
        )
    except Exception as e:
        await db.rollback()
        raise DatabaseException(
            detail="Failed to create article",
            context={
                "article_title": article.title,
                "article_url": article.url
            }
        )

async def get_article_by_url(db: AsyncSession, url: str) -> Optional[Article]:
    try:
        result = await db.execute(select(Article).where(Article.url == url))
        return result.scalar_one_or_none()
        
    except SQLAlchemyError as e:
        raise
        
    except Exception as e:
        raise

async def get_articles_by_ids(db: AsyncSession, article_ids: List[int], include_summary: bool = True) -> List[Article]:
    """Get articles by IDs, optionally including summary"""
    try:
        query = select(Article).options(
            selectinload(Article.topic)
            ).where(Article.id.in_(article_ids)).order_by(Article.created_at.desc())
        
        if include_summary:
            query = query.options(selectinload(Article.summary))
        
        result = await db.execute(query)    
        articles = result.scalars().all()
        
        return articles
        
    except SQLAlchemyError as e:
        raise
        
    except Exception as e:
        raise


async def mark_article_processed(db: AsyncSession, article_id: int) -> Optional[Article]:
    """Mark an article as successfully processed"""
    try:
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
        
    except SQLAlchemyError as e:
        await db.rollback()
        raise
        
    except Exception as e:
        await db.rollback()
        raise

async def mark_article_failed(db: AsyncSession, article_id: int, error_message: str) -> Optional[Article]:
    try:
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
        
    except SQLAlchemyError as e:
        await db.rollback()
        raise
        
    except Exception as e:
        await db.rollback()
        raise


async def get_used_sources(db: AsyncSession) -> List[str]:
    try:
        query = select(Article.source).distinct().where(Article.source.isnot(None))
        result = await db.execute(query)
        sources = result.scalars().all()
        return sources
        
    except SQLAlchemyError as e:
        raise
    except Exception as e:
        raise


async def search_articles(
    db: AsyncSession,
    search_params: SearchParams
) -> List[Article]:
    """
    Search articles with filters.
    Returns empty list if no articles found (no exception thrown).
    """
    try:
        params = search_params.model_dump()
        
        query = select(Article).options(
            selectinload(Article.summary), 
            selectinload(Article.topic)   
        )
        
        if params.get('title'):
            query = query.filter(Article.title.ilike(f"%{params['title']}%"))
        
        if params.get('source'):
            query = query.filter(Article.source == params['source'])
        
        if params.get('content'):
            content_filter = or_(
                Article.content.ilike(f"%{params['content']}%")
            )
            query = query.filter(content_filter)
        
        if params.get('published_after'):
            published_after_dt = datetime.combine(params['published_after'], datetime.min.time())
            query = query.filter(Article.published_at >= published_after_dt)
        
        if params.get('published_before'):
            published_before_dt = datetime.combine(params['published_before'], datetime.max.time())
            query = query.filter(Article.published_at <= published_before_dt)
        
        if params.get('topic_id'):
            query = query.filter(Article.topic_id == params['topic_id'])
            
        sort_by = params.get('sort_by', 'relevance')
        if sort_by == "newest":
            query = query.order_by(Article.published_at.desc())
        elif sort_by == "oldest":
            query = query.order_by(Article.published_at.asc())
        elif sort_by == "title_asc":
            query = query.order_by(Article.title.asc())
        elif sort_by == "title_desc":
            query = query.order_by(Article.title.desc())
        else:
            query = query.order_by(Article.published_at.desc())
       
        result = await db.execute(query)
        articles = result.scalars().all()
        return articles
        
    except SQLAlchemyError as e:
        raise
    except Exception as e:
        raise


async def get_articles(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    topic: Optional[TopicBase] = None,
    source: Optional[str] = None
) -> List[Article]:
    """
    Get articles with their summaries and topics, optionally filtered by topic and source.
    Returns empty list if no articles found.
    """

    try:
        query = (
            select(Article)
            .options(
                selectinload(Article.summary), 
                selectinload(Article.topic)   
            )
            .where(Article.is_processed == True)  
            .offset(skip)
            .limit(limit)
            .order_by(Article.created_at.desc())
        )
        
        if topic:
            query = query.join(Topic).where(Topic.id == topic.id)

        if source:
            query = query.where(Article.source == source)
        
        result = await db.execute(query)
        articles = result.scalars().all()
        
        return articles
        
    except SQLAlchemyError as e:
        raise
        
    except Exception as e:
        raise

async def count_articles(
    db: AsyncSession, 
    topic: Optional[TopicBase] = None, 
    source: Optional[str] = None
) -> int:
    """
    Get count of articles with summaries, optionally filtered by topic and source.
    Returns 0 if no articles found.
    """
    try:
        query = select(func.count(Article.id)).where(Article.is_processed == True)
        
        if topic:
            query = query.join(Topic).where(Topic.id == topic.id)

        if source:
            query = query.where(Article.source == source)
        
        result = await db.execute(query)
        count = result.scalar()

        return count or 0  
        
    except SQLAlchemyError as e:
        raise
        
    except Exception as e:
        raise

async def get_article_by_id(db: AsyncSession, article_id: int) -> Optional[Article]:
    """Get an article by ID, optionally including its summary and topic"""
    try:
        query = select(Article).options(
            selectinload(Article.summary), 
            selectinload(Article.topic)   
        ).where(Article.id == article_id)
        
        result = await db.execute(query)    
        article = result.scalar_one_or_none()
        
        return article
        
    except SQLAlchemyError as e:
        raise
    except Exception as e:
        raise

async def get_articles_by_topic_id(
    db: AsyncSession, 
    topic_id: str,
    skip: int = 0, 
    limit: int = 100,
    source: Optional[str] = None
) -> List[Article]:
    """
    Get articles by topic ID with pagination and optional source filtering.
    Returns empty list if no articles found.
    """
    try:
        query = (
            select(Article)
            .options(
                selectinload(Article.summary), 
                selectinload(Article.topic)   
            )
            .where(Article.topic_id == topic_id)
            .offset(skip)
            .limit(limit)
            .order_by(Article.published_at.desc())
        )
        
        if source:
            query = query.where(Article.source == source)
        
        result = await db.execute(query)
        articles = result.scalars().all()
        
        return articles
        
    except SQLAlchemyError as e:
        raise
        
    except Exception as e:
        raise

async def count_articles_by_topic_id(
    db: AsyncSession,
    topic_id: str,
    source: Optional[str] = None
) -> int:
    """
    Count articles by topic ID with optional source filtering.
    Returns 0 if no articles found.
    """
    try:
        query = select(func.count(Article.id)).where(Article.topic_id == topic_id)
        
        if source:
            query = query.where(Article.source == source)
        
        result = await db.execute(query)
        count = result.scalar()
        
        return count or 0
        
    except SQLAlchemyError as e:
        raise
        
    except Exception as e:
        raise