"""
Test the summary pipeline integration - FIXED ASYNC version
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import AsyncSessionLocal
from app.services.summary_pipeline import summary_pipeline
from app.schemas.article import ArticleCreate
from app.models.topic import Topic
from app.models.article import Article
from app.models.summary import Summary
from sqlalchemy import select, text

async def test_summary_pipeline():
    """Test the summary pipeline integration"""
    print("🧪 Testing Summary Pipeline")
    print("=" * 35)
    
    db = AsyncSessionLocal()
    try:
        await db.execute(text("DELETE FROM summaries"))
        await db.execute(text("DELETE FROM articles"))
        await db.execute(text("DELETE FROM topics"))
        await db.commit()
        
        topic = Topic(name="Pipeline Test", description="Testing pipeline")
        db.add(topic)
        await db.commit()
        await db.refresh(topic)
        
        print(f"✅ Created topic: {topic.name} (ID: {topic.id})")
        
        print("📝 Creating test article...")
        article = Article(
            title="Pipeline Test Article",
            url="https://example.com/pipeline-test",
            content="""
            This is a comprehensive test article for the summary pipeline.
            It contains enough content to test the summarization functionality.
            The article discusses modern technology trends and their impact on society.
            Artificial intelligence and machine learning are transforming various industries.
            This content should be sufficient for generating a meaningful summary.
            """,
            source="Test Source",
            topic_id=topic.id, 
            is_processed=False
        )
        db.add(article)
        await db.commit()
        await db.refresh(article)
        
        print(f"✅ Created test article: {article.title} (ID: {article.id})")
        
        print("🔄 Testing pipeline processing...")
        summary = await summary_pipeline.process_article(db, article)
        
        if summary:
            print("✅ Pipeline processing successful")
            print(f"   Summary ID: {summary.id}")
            print(f"   Provider: {summary.provider}")
            print(f"   Model: {summary.model_name}")
            print(f"   Content: {summary.content}")
            print(f"   Processing time: {summary.processing_time_ms}ms")
            
            result = await db.execute(select(Article).where(Article.id == article.id))
            updated_article = result.scalar_one()
            
            if updated_article.is_processed:
                print("✅ Article correctly marked as processed")
            else:
                print("❌ Article not marked as processed")
                return False
                
            result = await db.execute(select(Summary).where(Summary.article_id == article.id))
            retrieved_summary = result.scalar_one_or_none()
            
            if retrieved_summary and retrieved_summary.id == summary.id:
                print("✅ Summary retrieval works")
            else:
                print("❌ Summary retrieval failed")
                return False
                
            return True
        else:
            print("❌ Pipeline processing failed - no summary returned")
            return False
            
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await db.close()

if __name__ == "__main__":
    success = asyncio.run(test_summary_pipeline())
    print(f"\n{'🎉 Pipeline test passed!' if success else '❌ Pipeline test failed!'}")
    exit(0 if success else 1)

