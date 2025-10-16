from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class ArticleBase(BaseModel):
    title: str
    url: str
    content: Optional[str] = None
    summary: Optional[str] = None
    source: str
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    image_url: Optional[str] = None
    topic_id: int

class ArticleCreate(ArticleBase):
    source_metadata: Optional[Dict[str, Any]] = None

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    is_processed: Optional[bool] = None
    processing_error: Optional[str] = None

class Article(ArticleBase):
    id: int
    is_processed: bool
    processing_error: Optional[str] = None
    source_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ArticleList(BaseModel):
    articles: List[Article]
    total: int
    topic_name: Optional[str] = None