from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core import BaseAPIException
from app.schemas import ApiError, ValidationErrorResponse, ValidationErrorDetail


async def base_api_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """Handle custom BaseAPIException"""
    error = ApiError(
        detail=exc.detail,
        code=exc.code,
        status_code=exc.status_code,
        context=exc.context
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error.model_dump()
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors"""
    errors = []
    for error in exc.errors():
        errors.append(
            ValidationErrorDetail(
                loc=error["loc"],
                msg=error["msg"],
                type=error["type"]
            )
        )
    
    error_response = ValidationErrorResponse(
        detail="Request validation failed",
        code="validation_error",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        errors=errors
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump()
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle SQLAlchemy database errors"""
    
    error = ApiError(
        detail="An internal database error occurred",
        code="database_error",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error.model_dump()
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other exceptions"""
    
    error = ApiError(
        detail="An internal server error occurred",
        code="internal_error",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error.model_dump()
    )

def setup_exception_handlers(app: FastAPI):
    """Register all exception handlers with the FastAPI app"""
    app.add_exception_handler(BaseAPIException, base_api_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)