from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class SummaryBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    content: str
    provider: str
    model_name: str  # Consistent naming
    quality_level: str = "standard"
    word_count: int
    char_count: int
    processing_time_ms: int


class SummaryCreate(SummaryBase):
    article_id: int


class SummaryUpdate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    content: Optional[str] = None
    provider: Optional[str] = None
    model_name: Optional[str] = None
    quality_level: Optional[str] = None
    word_count: Optional[int] = None
    char_count: Optional[int] = None
    processing_time_ms: Optional[int] = None
    is_successful: Optional[bool] = None
    error_message: Optional[str] = None
    retry_count: Optional[int] = None


class Summary(SummaryBase):
    id: int
    article_id: int
    is_successful: bool
    error_message: Optional[str]
    retry_count: int
    created_at: datetime
    updated_at: Optional[datetime]


class SummaryWithArticle(Summary):
    article_title: str
    article_url: str
    topic_name: str


class SummarizeRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    article_id: int
    preferred_provider: Optional[str] = None
    quality_level: str = "standard"


class SummarizeResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    success: bool
    summary_id: Optional[int] = None
    summary_content: Optional[str] = None
    provider_used: Optional[str] = None
    model_used: Optional[str] = None
    processing_time_ms: Optional[int] = None
    error_message: Optional[str] = None


class BatchSummarizeRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    topic_id: Optional[int] = None
    preferred_provider: Optional[str] = None
    quality_level: str = "standard"
    batch_size: int = 5


class BatchSummarizeResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    total_articles: int
    successful: int
    failed: int
    success_rate: float
    failed_article_ids: List[int]