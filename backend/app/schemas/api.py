from datetime import date
from pydantic import BaseModel
from typing import Optional, Any, Dict, List, Generic, TypeVar
from enum import Enum

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

class ErrorCode(str, Enum):
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    INTERNAL_ERROR = "internal_error"
    EXTERNAL_SERVICE_ERROR = "external_service_error"
    DATABASE_ERROR = "database_error"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"

class ApiError(BaseModel):
    detail: str 
    code: ErrorCode 
    status_code: int 
    context: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "detail": "Article not found",
                "code": "not_found",
                "status_code": 404,
                "context": {"article_id": "123"}
            }
        }

class ValidationErrorDetail(BaseModel):
    loc: List[str] 
    msg: str 
    type: str 

class ValidationErrorResponse(ApiError):
    errors: List[ValidationErrorDetail] 