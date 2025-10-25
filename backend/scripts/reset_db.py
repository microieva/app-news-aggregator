import asyncio
import sys
import os
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.config import setup_colored_logging
from app.core.database import engine


logger = setup_colored_logging()

async def reset_database():
    """Remove all rows from all tables"""
    logger.info("🔄 Starting database reset...")
    
    try:
        async with engine.begin() as conn:
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            )
            tables = [row[0] for row in result.fetchall()]
            
            if not tables:
                logger.warning("No tables found in database")
                return
            
            logger.info(f"Found {len(tables)} tables: {', '.join(tables)}")
            
            total_deleted = 0
            for table in tables:
                result = await conn.execute(text(f"DELETE FROM {table}"))
                deleted_count = result.rowcount
                total_deleted += deleted_count
                logger.info(f"Cleared {deleted_count} rows from {table}")
            
            logger.info(f"✅ Database reset complete! Deleted {total_deleted} total rows")
            
    except Exception as e:
        logger.error(f"❌ Database reset failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(reset_database())