import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

async def debug_database():
    """Debug what's in the database"""
    from app.core.database import AsyncSessionLocal
    from sqlalchemy import select
    from app.models.topic import Topic
    from app.models.article import Article
    from app.models.summary import Summary
    
    print("🔍 DEBUGGING DATABASE CONTENTS")
    print("=" * 50)
    
    db = AsyncSessionLocal()
    
    try:
        print("\n📋 TOPICS:")
        result = await db.execute(select(Topic))
        topics = result.scalars().all()
        for topic in topics:
            print(f"  - ID: {topic.id}, Name: {topic.name}, Description: {topic.description}")
        
        print("\n📰 ARTICLES:")
        result = await db.execute(select(Article))
        articles = result.scalars().all()
        for article in articles:
            print(f"  - ID: {article.id}, Title: {article.title}, URL: {article.url}, Topic ID: {article.topic_id}")
        
        print("\n📝 SUMMARIES:")
        result = await db.execute(select(Summary))
        summaries = result.scalars().all()
        for summary in summaries:
            print(f"  - ID: {summary.id}, Article ID: {summary.article_id}, Status: {summary.status}, Task ID: {summary.task_id}")
        
        print(f"\n📊 COUNTS:")
        print(f"  - Topics: {len(topics)}")
        print(f"  - Articles: {len(articles)}")
        print(f"  - Summaries: {len(summaries)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(debug_database())