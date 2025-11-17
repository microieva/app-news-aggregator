from datetime import date
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    data: T
    message: Optional[str] = None
    success: bool = True
    
    class Config:
        from_attributes = True

class SearchParams(BaseModel):
    content: Optional[str] = None
    title: Optional[str] = None
    published_after: Optional[date] = None
    published_before: Optional[date] = None
    source: Optional[str] = None
    topic_id: Optional[int] = None
    sort_by: str = "relevance"
    skip: int = 0
    limit: int = 50