"""
Test the new database schema with Article-Topic-Summary relationships - FIXED ASYNC VERSION
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import AsyncSessionLocal, engine
from app.models.article import Article
from app.models.topic import Topic
from app.models.summary import Summary
from sqlalchemy import select, text
from sqlalchemy.orm import selectinload
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_database_schema():
    """Test the complete database schema - FIXED ASYNC VERSION"""
    print("🧪 Testing Database Schema")
    print("=" * 40)
    
    print("1. Checking table existence...")
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            AND name IN ('topics', 'articles', 'summaries')
        """))
        tables = sorted([row[0] for row in result.fetchall()])
        expected_tables = ['articles', 'summaries', 'topics']
        
        if tables == expected_tables:
            print("   ✅ All tables exist")
        else:
            print(f"   ❌ Missing tables: {set(expected_tables) - set(tables)}")
            return False
    
    print("2. Testing relationships...")
    db = AsyncSessionLocal()
    try:
        await db.execute(text("DELETE FROM summaries"))
        await db.execute(text("DELETE FROM articles")) 
        await db.execute(text("DELETE FROM topics"))
        await db.commit()
        
        topic = Topic(name="Technology", description="Tech news")
        db.add(topic)
        await db.commit()
        await db.refresh(topic)
        
        article = Article(
            title="Test Article",
            url="https://example.com/test-schema",
            content="Test content for schema validation",
            source="Test Source",
            topic_id=topic.id,
            is_processed=False
        )
        db.add(article)
        await db.commit()
        await db.refresh(article)
        
        summary = Summary(
            article_id=article.id,
            content="Test summary content",
            provider="test-provider",
            model_name="test-model",
            quality_level="standard",
            word_count=10,
            char_count=50,
            processing_time_ms=1000,
            is_successful=True
        )
        db.add(summary)
        await db.commit()
        await db.refresh(summary)

        print("   Testing Article-Summary relationship...")
        
        result = await db.execute(
            select(Article)
            .options(selectinload(Article.summary))
            .where(Article.id == article.id)
        )
        article_with_summary = result.scalar_one()

        result = await db.execute(
            select(Summary)
            .options(selectinload(Summary.article))
            .where(Summary.id == summary.id)
        )
        summary_with_article = result.scalar_one()
        
        if article_with_summary.summary and article_with_summary.summary.id == summary.id:
            print("   ✅ Article-Summary relationship works")
        else:
            print("   ❌ Article-Summary relationship broken")
            return False
            
        if summary_with_article.article and summary_with_article.article.id == article.id:
            print("   ✅ Summary-Article relationship works") 
        else:
            print("   ❌ Summary-Article relationship broken")
            return False
            
        print("   Testing cascade delete...")
        await db.delete(topic)
        await db.commit()
        
        result = await db.execute(select(Article).where(Article.id == article.id))
        remaining_articles = result.scalar_one_or_none()
        
        result = await db.execute(select(Summary).where(Summary.id == summary.id))
        remaining_summaries = result.scalar_one_or_none()
        
        if not remaining_articles and not remaining_summaries:
            print("   ✅ Cascade delete works")
        else:
            print("   ❌ Cascade delete failed")
            if remaining_articles:
                print(f"      Article still exists: {remaining_articles.id}")
            if remaining_summaries:
                print(f"      Summary still exists: {remaining_summaries.id}")
            return False
            
        return True
        
    except Exception as e:
        await db.rollback()
        print(f"   ❌ Relationship test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await db.close()

async def test_relationships_with_queries():
    """Additional test for relationship queries - FIXED ASYNC"""
    print("\n3. Testing relationship queries...")
    
    db = AsyncSessionLocal()
    try:
        await db.execute(text("DELETE FROM summaries"))
        await db.execute(text("DELETE FROM articles")) 
        await db.execute(text("DELETE FROM topics"))
        await db.commit()
        
        topic = Topic(name="Science", description="Science news")
        db.add(topic)
        await db.commit()
        await db.refresh(topic)
        
        article = Article(
            title="Science Test Article",
            url="https://example.com/science-test",
            content="Science test content",
            source="Science Source",
            topic_id=topic.id,
            is_processed=False
        )
        db.add(article)
        await db.commit()
        await db.refresh(article)
        
        summary = Summary(
            article_id=article.id,
            content="Science test summary",
            provider="test-provider",
            model_name="test-model",
            quality_level="standard",
            word_count=5,
            char_count=30,
            processing_time_ms=500,
            is_successful=True
        )
        db.add(summary)
        await db.commit()
        await db.refresh(summary)
        
        result = await db.execute(
            select(Article, Summary, Topic)
            .join(Summary, Article.id == Summary.article_id)
            .join(Topic, Article.topic_id == Topic.id)
            .where(Article.id == article.id)
        )
        joined_result = result.first()
        
        if joined_result:
            article_joined, summary_joined, topic_joined = joined_result
            if (article_joined.id == article.id and 
                summary_joined.id == summary.id and 
                topic_joined.id == topic.id):
                print("   ✅ Join queries work correctly")
            else:
                print("   ❌ Join queries failed")
                return False
        else:
            print("   ❌ No results from join query")
            return False
            
        result = await db.execute(
            select(Article)
            .options(selectinload(Article.summary))
            .where(Article.id == article.id)
        )
        article_with_eager_summary = result.scalar_one()
        
        if article_with_eager_summary.summary and article_with_eager_summary.summary.id == summary.id:
            print("   ✅ Eager loading works with selectinload")
        else:
            print("   ❌ Eager loading failed")
            return False
            
        return True
        
    except Exception as e:
        await db.rollback()
        print(f"   ❌ Relationship query test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await db.close()

async def test_foreign_key_constraints():
    """Test foreign key constraints work properly"""
    print("\n4. Testing foreign key constraints...")
    
    db = AsyncSessionLocal()
    try:
        await db.execute(text("DELETE FROM summaries"))
        await db.execute(text("DELETE FROM articles")) 
        await db.execute(text("DELETE FROM topics"))
        await db.commit()
        
        print("   Testing invalid foreign key...")
        try:
            invalid_summary = Summary(
                article_id=99999,  # Non-existent article
                content="Invalid summary",
                provider="test",
                model_name="test",
                quality_level="standard",
                word_count=5,
                char_count=25,
                processing_time_ms=100,
                is_successful=True
            )
            db.add(invalid_summary)
            await db.commit()
            print("   ❌ Should have failed with invalid foreign key")
            return False
        except Exception:
            await db.rollback()
            print("   ✅ Foreign key constraint works (prevents invalid references)")
        
        topic = Topic(name="Constraint Test", description="Testing constraints")
        db.add(topic)
        await db.commit()
        await db.refresh(topic)
        
        article = Article(
            title="Constraint Test Article",
            url="https://example.com/constraint-test",
            content="Test content",
            source="Test Source",
            topic_id=topic.id,
            is_processed=False
        )
        db.add(article)
        await db.commit()
        await db.refresh(article)
        
        valid_summary = Summary(
            article_id=article.id,  # Valid article
            content="Valid summary",
            provider="test",
            model_name="test",
            quality_level="standard",
            word_count=5,
            char_count=25,
            processing_time_ms=100,
            is_successful=True
        )
        db.add(valid_summary)
        await db.commit()
        print("   ✅ Valid foreign key works")
        
        return True
        
    except Exception as e:
        await db.rollback()
        print(f"   ❌ Foreign key test failed: {e}")
        return False
    finally:
        await db.close()

async def main():
    """Run all database schema tests"""
    try:
        tests = [
            ("Database Schema", test_database_schema),
            ("Relationship Queries", test_relationships_with_queries),
            ("Foreign Key Constraints", test_foreign_key_constraints),
        ]
        
        results = {}
        for test_name, test_func in tests:
            print(f"\n🎯 Running: {test_name}")
            print("-" * 30)
            try:
                success = await test_func()
                results[test_name] = success
                status = "✅ PASS" if success else "❌ FAIL"
                print(f"   {status}")
            except Exception as e:
                print(f"   ❌ CRASH: {e}")
                results[test_name] = False
        
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        all_passed = True
        for test_name, success in results.items():
            status_icon = "✅" if success else "❌"
            print(f"{status_icon} {test_name}: {'PASS' if success else 'FAIL'}")
            if not success:
                all_passed = False
        
        print(f"\n{'🎉 All schema tests passed!' if all_passed else '❌ Some schema tests failed!'}")
        return all_passed
        
    except Exception as e:
        print(f"💥 Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)