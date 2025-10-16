from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from backend.app.models.article import Article

class TopicBase(BaseModel):
    name: str
    description: Optional[str] = None

class TopicCreate(TopicBase):
    pass

class TopicUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class Topic(TopicBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TopicWithArticles(Topic):
    articles: List[Article] = []

class TopicList(BaseModel):
    topics: List[Topic]
    total: int