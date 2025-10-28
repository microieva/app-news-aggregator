from pydantic import BaseModel
from typing import Optional, List

class TopicBase(BaseModel):
    id: Optional[int] = None 
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class TopicCreate(TopicBase):
    pass

class TopicUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# class Topic(TopicBase):
#     id: int
#     created_at: datetime
#     updated_at: Optional[datetime] = None
    
#     class Config:
#         from_attributes = True

class TopicWithArticles(TopicBase):
    articles: List['ArticleBase'] = []

class TopicList(BaseModel):
    topics: List[TopicBase]
    total: int