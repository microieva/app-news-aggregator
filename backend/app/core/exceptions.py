from fastapi import HTTPException, status
from typing import Optional, Dict, Any

class BaseAPIException(HTTPException):
  """Base exception for all API errors"""
  def __init__(
    self,
    status_code: int,
    detail: str,
    code: str,
    context: Optional[Dict[str, Any]] = None
  ):
    super().__init__(status_code=status_code, detail=detail)
    self.code = code
    self.context = context or {}

class NotFoundException(BaseAPIException):
  def __init__(self, detail: str = "Resource not found", context: Optional[Dict[str, Any]] = None):
    super().__init__(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=detail,
      code="not_found",
      context=context
    )

class ValidationException(BaseAPIException):
  def __init__(self, detail: str = "Validation error", context: Optional[Dict[str, Any]] = None):
    super().__init__(
      status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
      detail=detail,
      code="validation_error",
      context=context
    )

class DatabaseException(BaseAPIException):
  def __init__(self, detail: str = "Database error", context: Optional[Dict[str, Any]] = None):
    super().__init__(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=detail,
      code="database_error",
      context=context
    )

class ExternalServiceException(BaseAPIException):
  def __init__(self, detail: str = "External service error", context: Optional[Dict[str, Any]] = None):
    super().__init__(
      status_code=status.HTTP_502_BAD_GATEWAY,
      detail=detail,
      code="external_service_error",
      context=context
    )

class RateLimitException(BaseAPIException):
  def __init__(self, detail: str = "Rate limit exceeded", context: Optional[Dict[str, Any]] = None):
    super().__init__(
      status_code=status.HTTP_429_TOO_MANY_REQUESTS,
      detail=detail,
      code="rate_limit_exceeded",
      context=context
    )