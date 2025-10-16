from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.topic import Topic
from app.schemas.topic import TopicCreate, TopicUpdate

def get_topic(db: Session, topic_id: int) -> Optional[Topic]:
    """Get a topic by ID"""
    return db.query(Topic).filter(Topic.id == topic_id).first()

def get_topic_by_name(db: Session, name: str) -> Optional[Topic]:
    """Get a topic by name"""
    return db.query(Topic).filter(Topic.name == name).first()

def get_topics(db: Session, skip: int = 0, limit: int = 100) -> List[Topic]:
    """Get all topics with pagination"""
    return db.query(Topic).offset(skip).limit(limit).all()

def create_topic(db: Session, topic: TopicCreate) -> Topic:
    """Create a new topic"""
    db_topic = Topic(
        name=topic.name,
        description=topic.description
    )
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic

def update_topic(db: Session, topic_id: int, topic_update: TopicUpdate) -> Optional[Topic]:
    """Update a topic"""
    db_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if db_topic:
        update_data = topic_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_topic, field, value)
        db.commit()
        db.refresh(db_topic)
    return db_topic

def delete_topic(db: Session, topic_id: int) -> bool:
    """Delete a topic"""
    db_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if db_topic:
        db.delete(db_topic)
        db.commit()
        return True
    return False

def get_topics_count(db: Session) -> int:
    """Get total number of topics"""
    return db.query(Topic).count()