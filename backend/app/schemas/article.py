from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime

class ArticleBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    title: str
    url: str
    content: Optional[str] = None
    source: str
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    image_url: Optional[str] = None
    topic_id: int

class ArticleCreate(ArticleBase):
    source_metadata: Optional[Dict[str, Any]] = None

class ArticleUpdate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    title: Optional[str] = None
    content: Optional[str] = None
    is_processed: Optional[bool] = None
    processing_error: Optional[str] = None
    source_metadata: Optional[Dict[str, Any]] = None

class Article(ArticleBase):
    id: int
    is_processed: bool = False
    processing_error: Optional[str] = None
    source_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class ArticleWithSummary(Article):
    summary: Optional['Summary'] = None 

class ArticleList(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    articles: List[Article]
    total: int
    topic_name: Optional[str] = None

class ArticleListWithSummaries(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    articles: List[ArticleWithSummary]
    total: int
    topic_name: Optional[str] = None

class ArticleProcessingStatus(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    article_id: int
    is_processed: bool
    processing_error: Optional[str] = None
    has_summary: bool

class BulkProcessingResult(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    total_articles: int
    processed_count: int
    failed_count: int
    success_rate: float
    failed_article_ids: List[int]

class TaskStatusResponse(BaseModel):
    task_id: str
    article_id: int
    status: str  # pending, processing, completed, failed, error, exists
    message: str

class ArticleWithSummaryStatus(Article):
    summary_status: Optional[dict] = None
    background_tasks: Optional[List[dict]] = None