from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    provider = Column(String(50), nullable=False) 
    model_name = Column(String(100), nullable=False)  
    quality_level = Column(String(20), nullable=False, default="standard")  # "concise", "standard", "detailed"
    word_count = Column(Integer, nullable=False)
    char_count = Column(Integer, nullable=False)
    processing_time_ms = Column(Integer, nullable=False)  
    is_successful = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    task_id = Column(String(36), nullable=True, index=True)  
    status = Column(String(20), default='pending')  # pending, processing, completed, failed
    started_at = Column(DateTime(timezone=True), nullable=True) 
    completed_at = Column(DateTime(timezone=True), nullable=True)  
    
    article = relationship("Article", back_populates="summary")