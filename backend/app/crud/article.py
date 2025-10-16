from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from sqlalchemy import desc
from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleUpdate

def get_article(db: Session, article_id: int) -> Optional[Article]:
    """Get an article by ID"""
    return db.query(Article).filter(Article.id == article_id).first()

def get_articles_by_topic(
    db: Session, 
    topic_id: int, 
    skip: int = 0, 
    limit: int = 50,
    sort_by: str = "published_at",
    sort_order: str = "desc"
) -> List[Article]:
    """Get articles by topic ID with sorting"""
    query = db.query(Article).filter(Article.topic_id == topic_id)
    
    # Apply sorting
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
    
    return query.offset(skip).limit(limit).all()

def get_articles_by_source(
    db: Session, 
    source: str, 
    skip: int = 0, 
    limit: int = 50
) -> List[Article]:
    """Get articles by source"""
    return db.query(Article).filter(Article.source == source).offset(skip).limit(limit).all()

def create_article(db: Session, article: ArticleCreate) -> Article:
    """Create a new article"""
    db_article = Article(
        title=article.title,
        url=article.url,
        content=article.content,
        summary=article.summary,
        source=article.source,
        author=article.author,
        published_at=article.published_at,
        image_url=article.image_url,
        topic_id=article.topic_id,
        source_metadata=article.source_metadata
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def create_articles_bulk(db: Session, articles: List[ArticleCreate]) -> List[Article]:
    """Create multiple articles in bulk"""
    db_articles = []
    for article_data in articles:
        # Check if article already exists by URL
        existing = db.query(Article).filter(Article.url == article_data.url).first()
        if not existing:
            db_article = Article(
                title=article_data.title,
                url=article_data.url,
                content=article_data.content,
                summary=article_data.summary,
                source=article_data.source,
                author=article_data.author,
                published_at=article_data.published_at,
                image_url=article_data.image_url,
                topic_id=article_data.topic_id,
                source_metadata=article_data.source_metadata
            )
            db_articles.append(db_article)
            db.add(db_article)
    
    db.commit()
    
    # Refresh all created articles
    for article in db_articles:
        db.refresh(article)
    
    return db_articles

def update_article(db: Session, article_id: int, article_update: ArticleUpdate) -> Optional[Article]:
    """Update an article"""
    db_article = db.query(Article).filter(Article.id == article_id).first()
    if db_article:
        update_data = article_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_article, field, value)
        db.commit()
        db.refresh(db_article)
    return db_article

def delete_article(db: Session, article_id: int) -> bool:
    """Delete an article"""
    db_article = db.query(Article).filter(Article.id == article_id).first()
    if db_article:
        db.delete(db_article)
        db.commit()
        return True
    return False

def get_articles_count(db: Session, topic_id: Optional[int] = None) -> int:
    """Get total number of articles, optionally filtered by topic"""
    query = db.query(Article)
    if topic_id:
        query = query.filter(Article.topic_id == topic_id)
    return query.count()