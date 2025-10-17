"""
Test CRUD operations with new database structure - FIXED ASYNC VERSION
"""

import sys
import os
from datetime import datetime
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import AsyncSessionLocal
from app.crud.article import (
    create_article, get_article, get_articles_by_topic, 
    get_unprocessed_articles, mark_article_processed,
    get_processing_stats
)
from app.crud.summary import create_summary, get_summary_by_article_id
from app.schemas.article import ArticleCreate
from app.schemas.summary import SummaryCreate
from app.models.topic import Topic
from sqlalchemy import text

async def test_crud_operations():
    """Test CRUD operations with new schema - FIXED ASYNC VERSION"""
    print("🧪 Testing CRUD Operations")
    print("=" * 40)
    
    db = AsyncSessionLocal()
    try:
        await db.execute(text("DELETE FROM summaries"))
        await db.execute(text("DELETE FROM articles"))
        await db.execute(text("DELETE FROM topics"))
        await db.commit()
        
        topic = Topic(name="CRUD Test", description="Testing CRUD operations")
        db.add(topic)
        await db.commit()
        await db.refresh(topic)
        
        print("1. Testing article creation...")
        article_data = ArticleCreate(
            title="CRUD Test Article",
            url="https://example.com/crud-test",
            content="This is test content for CRUD operations",
            source="Test Source",
            topic_id=topic.id
        )
        article = await create_article(db, article_data)
        
        if article and article.id:
            print("   ✅ Article creation works")
        else:
            print("   ❌ Article creation failed")
            return False
        
        print("2. Testing article retrieval...")
        retrieved_article = await get_article(db, article.id)
        if retrieved_article and retrieved_article.id == article.id:
            print("   ✅ Article retrieval works")
        else:
            print("   ❌ Article retrieval failed")
            return False
        
        print("3. Testing unprocessed articles...")
        unprocessed = await get_unprocessed_articles(db)
        if len(unprocessed) == 1 and unprocessed[0].id == article.id:
            print("   ✅ Unprocessed articles retrieval works")
        else:
            print(f"   ❌ Unprocessed articles retrieval failed. Found: {len(unprocessed)}")
            return False
        
        print("4. Testing summary creation...")
        summary_data = SummaryCreate(
            article_id=article.id,
            content="This is a test summary",
            provider="test-provider",
            model_name="test-model",
            quality_level="standard",
            word_count=5,
            char_count=25,
            processing_time_ms=500
        )
        summary = await create_summary(db, summary_data)
        
        if summary and summary.id:
            print("   ✅ Summary creation works")
        else:
            print("   ❌ Summary creation failed")
            return False
        
        print("5. Testing article processing...")
        await mark_article_processed(db, article.id)
        processed_article = await get_article(db, article.id)
        
        if processed_article and processed_article.is_processed:
            print("   ✅ Article processing works")
        else:
            print("   ❌ Article processing failed")
            return False
        
        print("6. Testing processing stats...")
        stats = await get_processing_stats(db, topic.id)
        if (stats["total_articles"] == 1 and 
            stats["processed_articles"] == 1 and 
            stats["success_rate"] == 100.0):
            print("   ✅ Processing stats work")
        else:
            print(f"   ❌ Processing stats failed. Got: {stats}")
            return False
        
        print("7. Testing articles with summaries...")
        articles_with_summaries = await get_articles_by_topic(
            db, topic.id, include_summaries=True
        )
        if (len(articles_with_summaries) == 1 and 
            articles_with_summaries[0].summary and 
            articles_with_summaries[0].summary.id == summary.id):
            print("   ✅ Articles with summaries work")
        else:
            print(f"   ❌ Articles with summaries failed. Found: {len(articles_with_summaries)}")
            if articles_with_summaries:
                print(f"      Article has summary: {hasattr(articles_with_summaries[0], 'summary')}")
                if hasattr(articles_with_summaries[0], 'summary'):
                    print(f"      Summary object: {articles_with_summaries[0].summary}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ CRUD test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await db.close()

if __name__ == "__main__":
    success = asyncio.run(test_crud_operations())
    print(f"\n{'🎉 CRUD test passed!' if success else '❌ CRUD test failed!'}")
    exit(0 if success else 1)