import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import topic as topic_crud
from app.schemas import TopicCreate
from app.core.config import settings
from sqlalchemy.orm import sessionmaker
from app.core.database import engine

logger = logging.getLogger(__name__)

class TopicInitializer:
    def __init__(self):
        self.default_topics = settings.DEFAULT_TOPICS
        self.async_session_factory = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def initialize_default_topics(self, db: AsyncSession):
        """Initialize default topics in database"""
        created_count = 0
        for topic_data in self.default_topics:
            existing_topic = await topic_crud.get_topic_by_name(db, topic_data["name"])
            if not existing_topic:
                    topic_create = TopicCreate(**topic_data)
                    await topic_crud.create_topic(db, obj_in=topic_create)
                    created_count += 1
                
                    logger.info(f"✅ Created topic: {topic_data['name']}")
            else:
                logger.info(f"ℹ️ Topic already exists: {topic_data['name']}")
        
        logger.info(f"\n\n\n📚 Topic initialization complete: {created_count} new topics created\n\n\n")
        return created_count

topic_initializer = TopicInitializer()