from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.schemas import ApiResponse, TopicList
from app.crud import topic as topic_crud

router = APIRouter()

@router.get("/used", response_model=ApiResponse)
async def read_used_topics(
    db:AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of topics to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of topics to return"),
    source: Optional[str] = None
):
    """Get used topics with pagination"""
    topics = await topic_crud.get_used_topics(db, source=source, skip=skip, limit=limit)
    total = await topic_crud.get_used_topics_count(db, source=source)

    if topics:
        api_response = TopicList(
            topics=topics,
            total=total
        )
        return ApiResponse(
            data=api_response
        )
    else:  
        raise HTTPException(status_code=404, detail="No topics found")

