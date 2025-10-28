from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas import TopicBase, TopicCreate, TopicUpdate, TopicList
from app.crud import topic as crud

router = APIRouter()

@router.get("/", response_model=TopicList)
def read_topics(
    skip: int = Query(0, ge=0, description="Number of topics to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of topics to return"),
    db: Session = Depends(get_db)
):
    """Get all topics with pagination"""
    topics = crud.get_topics(db, skip=skip, limit=limit)
    total = crud.get_topics_count(db)
    return TopicList(topics=topics, total=total)

@router.get("/{topic_id}", response_model=TopicBase)
def read_topic(topic_id: int, db: Session = Depends(get_db)):
    """Get a specific topic by ID"""
    db_topic = crud.get_topic(db, topic_id=topic_id)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="TopicBase not found")
    return db_topic

@router.post("/", response_model=TopicBase)
def create_topic(topic: TopicCreate, db: Session = Depends(get_db)):
    """Create a new topic"""
    # Check if topic with same name already exists
    db_topic = crud.get_topic_by_name(db, name=topic.name)
    if db_topic:
        raise HTTPException(
            status_code=400, 
            detail="TopicBase with this name already exists"
        )
    return crud.create_topic(db=db, topic=topic)

@router.put("/{topic_id}", response_model=TopicBase)
def update_topic(
    topic_id: int, 
    topic_update: TopicUpdate, 
    db: Session = Depends(get_db)
):
    """Update a topic"""
    db_topic = crud.update_topic(db, topic_id=topic_id, topic_update=topic_update)
    if db_topic is None:
        raise HTTPException(status_code=404, detail="TopicBase not found")
    return db_topic

@router.delete("/{topic_id}")
def delete_topic(topic_id: int, db: Session = Depends(get_db)):
    """Delete a topic"""
    success = crud.delete_topic(db, topic_id=topic_id)
    if not success:
        raise HTTPException(status_code=404, detail="TopicBase not found")
    return {"message": "TopicBase deleted successfully"}