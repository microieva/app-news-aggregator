from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# async SQLite for dev
if "sqlite" in settings.DATABASE_URL:
    async_database_url = settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
else:
    async_database_url = settings.DATABASE_URL

engine = create_async_engine(
    async_database_url,
    echo=False,
    future=True
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

