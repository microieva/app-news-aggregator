from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.schemas import ApiResponse, TopicCreate, TopicUpdate, TopicList
from app.crud import topic as topic_crud

router = APIRouter()

@router.get("/used", response_model=ApiResponse)
async def read_used_topics(
    db:AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of topics to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of topics to return"),
):
    """Get used topics with pagination"""
    topics = await topic_crud.get_used_topics(db, skip=skip, limit=limit)
    total = await topic_crud.get_used_topics_count(db)

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



# @router.get("/{topic_id}", response_model=TopicBase)
# def read_topic(topic_id: int, db: Session = Depends(get_db)):
#     """Get a specific topic by ID"""
#     db_topic = topic_crud.get_topic(db, topic_id=topic_id)
#     if db_topic is None:
#         raise HTTPException(status_code=404, detail="TopicBase not found")
#     return db_topic

# @router.post("/", response_model=TopicBase)
# def create_topic(topic: TopicCreate, db: Session = Depends(get_db)):
#     """Create a new topic"""
#     # Check if topic with same name already exists
#     db_topic = topic_crud.get_topic_by_name(db, name=topic.name)
#     if db_topic:
#         raise HTTPException(
#             status_code=400, 
#             detail="TopicBase with this name already exists"
#         )
#     return topic_crud.create_topic(db=db, topic=topic)

# @router.put("/{topic_id}", response_model=TopicBase)
# def update_topic(
#     topic_id: int, 
#     topic_update: TopicUpdate, 
#     db: Session = Depends(get_db)
# ):
#     """Update a topic"""
#     db_topic = topic_crud.update_topic(db, topic_id=topic_id, topic_update=topic_update)
#     if db_topic is None:
#         raise HTTPException(status_code=404, detail="TopicBase not found")
#     return db_topic

# @router.delete("/{topic_id}")
# def delete_topic(topic_id: int, db: Session = Depends(get_db)):
#     """Delete a topic"""
#     success = topic_crud.delete_topic(db, topic_id=topic_id)
#     if not success:
#         raise HTTPException(status_code=404, detail="TopicBase not found")
#     return {"message": "TopicBase deleted successfully"}