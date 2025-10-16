from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.article import Article, ArticleList, ArticleUpdate
from app.schemas.topic import Topic
from app.crud import article as article_crud
from app.crud import topic as topic_crud

router = APIRouter()

@router.get("/by-topic/{topic_id}", response_model=ArticleList)
def read_articles_by_topic(
    topic_id: int,
    skip: int = Query(0, ge=0, description="Number of articles to skip"),
    limit: int = Query(50, ge=1, le=200, description="Number of articles to return"),
    sort_by: str = Query("published_at", description="Sort by field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    db: Session = Depends(get_db)
):
    """Get articles by topic ID with sorting and pagination"""
    # Verify topic exists
    topic = topic_crud.get_topic(db, topic_id=topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Validate sort parameters
    valid_sort_fields = ["published_at", "created_at", "title"]
    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid sort field. Must be one of: {valid_sort_fields}"
        )
    
    if sort_order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400, 
            detail="Invalid sort order. Must be 'asc' or 'desc'"
        )
    
    articles = article_crud.get_articles_by_topic(
        db, 
        topic_id=topic_id, 
        skip=skip, 
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    total = article_crud.get_articles_count(db, topic_id=topic_id)
    
    return ArticleList(
        articles=articles, 
        total=total,
        topic_name=topic.name
    )

@router.get("/{article_id}", response_model=Article)
def read_article(article_id: int, db: Session = Depends(get_db)):
    """Get a specific article by ID"""
    db_article = article_crud.get_article(db, article_id=article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return db_article

@router.put("/{article_id}", response_model=Article)
def update_article(
    article_id: int, 
    article_update: ArticleUpdate, 
    db: Session = Depends(get_db)
):
    """Update an article (e.g., mark as processed, add summary)"""
    db_article = article_crud.update_article(db, article_id=article_id, article_update=article_update)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return db_article

@router.delete("/{article_id}")
def delete_article(article_id: int, db: Session = Depends(get_db)):
    """Delete an article"""
    success = article_crud.delete_article(db, article_id=article_id)
    if not success:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"message": "Article deleted successfully"}