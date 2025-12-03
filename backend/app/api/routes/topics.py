from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError

from app.core import get_db, DatabaseException
from app.schemas import ApiResponse, TopicList
from app.crud import topic as topic_crud

router = APIRouter()

@router.get("/", response_model=ApiResponse)
async def read_used_topics(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    source: Optional[str] = None
) -> ApiResponse:
    """Get used topics with pagination"""
    try:
        topics = await topic_crud.get_used_topics(db, source=source, skip=skip, limit=limit)
        total = await topic_crud.get_used_topics_count(db, source=source)
        
        api_response = TopicList(
            topics=topics,
            total=total
        )
        return ApiResponse(data=api_response)
        
    except SQLAlchemyError as e:
        raise DatabaseException(
            detail="Failed to retrieve topics due to database error",
            context={
                "endpoint": "read_used_topics",
                "source": source,
                "skip": skip,
                "limit": limit
            }
        )
    except Exception as e:
        raise DatabaseException(
            detail="Failed to retrieve topics",
            context={
                "endpoint": "read_used_topics", 
                "source": source,
                "skip": skip,
                "limit": limit
            }
        )

