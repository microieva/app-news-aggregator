from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core import engine, Base, task_manager, cron_manager, setup_colored_logging
from app.services import topic_initializer, aggregation_service

logger = setup_colored_logging()

@asynccontextmanager
async def app_lifespan(app:FastAPI):
    await startup()    
    yield
    await shutdown()

async def startup():
    logger.info("\n\n\n 🚀 Starting News Aggregator Application...\n\n\n")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async with async_session_factory() as db_session:
        await topic_initializer.initialize_default_topics(db_session)
    
    await task_manager.start_processing()
    logger.info("✅ Background task processor started")

    await task_manager.recover_pending_tasks(db_session)
    logger.info("✅ Pending tasks recovered")
    # FOR PRODUCTION:

    # cron_manager.add_aggregation_job(
    #     func=aggregation_service.run_aggregation,
    #     name="Aggregation"
    # )
    # for dev 
    # cron_manager.add_one_time_job(
    #     func=aggregation_service.run_aggregation,
    #     name="Aggregation"
    # )

    #cron_manager.start()
    logger.info("✅ Cron manager started")

async def shutdown():
    logger.info("🛑 Shutting down News Aggregator Application...")
    
    cron_manager.stop()
    logger.info("✅ Cron manager stopped")
    
    await task_manager.stop_processing()
    logger.info("✅ Background task manager stopped")