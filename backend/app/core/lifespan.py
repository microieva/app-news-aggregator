from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import engine, Base
from sqlalchemy.orm import sessionmaker
from app.core.background_tasks import task_manager
from app.core.cron_manager import cron_manager
from app.services.aggregation_service import aggregation_service
from app.core.config import setup_colored_logging
from app.services import topic_initializer

logger = setup_colored_logging()

@asynccontextmanager
async def app_lifespan(app:FastAPI):
    await startup()    
    yield
    await shutdown()

async def startup():
    logger.info("\n\n\n\n\n 🚀 Starting News Aggregator Application...\n\n\n\n\n")
    
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async with async_session_factory() as db_session:
        await topic_initializer.initialize_default_topics(db_session)
    
    asyncio.create_task(task_manager.process_tasks())
    logger.info("\n\n\n✅ Background task processor started\n\n\n")
    # FOR PRODUCTION:
    
    # cron_manager.add_interval_job(
    #     func=aggregation_service.run_aggregation,
    #     interval_minutes=30,
    #     name="News Aggregation"
    # )
    cron_manager.add_one_time_job(
        func=aggregation_service.run_aggregation,
        name="News Aggregation Startup"
    )
    cron_manager.start()
    logger.info("✅ Cron manager started")
    
    await task_manager.recover_pending_tasks(db_session)
    logger.info("✅ Pending tasks recovered\n\n\n\n\n")

async def shutdown():
    logger.info("🛑 Shutting down News Aggregator Application...")
    
    cron_manager.stop()
    logger.info("✅ Cron manager stopped")
    
    await task_manager.shutdown()
    logger.info("✅ Background task manager stopped")