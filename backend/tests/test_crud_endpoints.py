import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal, engine
from app.models.topic import Topic
from app.models.article import Article

client = TestClient(app)

def setup_module():
    """Set up test database"""

    from app.core.database import Base
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:

        test_topic = Topic(name="Test Technology", description="Test topic for CRUD operations")
        db.add(test_topic)
        db.commit()
        db.refresh(test_topic)
        
        test_articles = [
            Article(
                title="Test Article 1",
                url="https://example.com/test1",
                content="Test content 1",
                summary="Test summary 1",
                source="test",
                author="Test Author",
                topic_id=test_topic.id
            ),
            Article(
                title="Test Article 2", 
                url="https://example.com/test2",
                content="Test content 2",
                summary="Test summary 2", 
                source="test",
                author="Test Author",
                topic_id=test_topic.id
            )
        ]
        
        for article in test_articles:
            db.add(article)
        
        db.commit()
        
    finally:
        db.close()

def teardown_module():
    """Clean up test database"""
    db = SessionLocal()
    try:
        db.query(Article).delete()
        db.query(Topic).delete()
        db.commit()
    finally:
        db.close()

def test_create_topic():
    """Test creating a topic"""
    response = client.post("/api/topics/", json={
        "name": "Artificial Intelligence",
        "description": "AI and machine learning topics"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Artificial Intelligence"
    assert data["description"] == "AI and machine learning topics"
    assert "id" in data

def test_get_topics():
    """Test getting all topics"""
    response = client.get("/api/topics/")
    
    assert response.status_code == 200
    data = response.json()
    assert "topics" in data
    assert "total" in data
    assert len(data["topics"]) > 0

def test_get_topic():
    """Test getting a specific topic"""

    topics_response = client.get("/api/topics/")
    topic_id = topics_response.json()["topics"][0]["id"]
    
    response = client.get(f"/api/topics/{topic_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == topic_id
    assert "name" in data

def test_get_articles_by_topic():
    """Test getting articles by topic"""

    topics_response = client.get("/api/topics/")
    topic_id = topics_response.json()["topics"][0]["id"]
    
    response = client.get(f"/api/articles/by-topic/{topic_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert "articles" in data
    assert "total" in data
    assert "topic_name" in data
    assert len(data["articles"]) > 0

def test_get_articles_with_sorting():
    """Test getting articles with sorting"""
    topics_response = client.get("/api/topics/")
    topic_id = topics_response.json()["topics"][0]["id"]
    
    response = client.get(
        f"/api/articles/by-topic/{topic_id}",
        params={"sort_by": "title", "sort_order": "asc"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["articles"]) > 0

def test_update_article():
    """Test updating an article"""

    topics_response = client.get("/api/topics/")
    topic_id = topics_response.json()["topics"][0]["id"]
    
    articles_response = client.get(f"/api/articles/by-topic/{topic_id}")
    article_id = articles_response.json()["articles"][0]["id"]
    
    response = client.put(
        f"/api/articles/{article_id}",
        json={"summary": "Updated test summary", "is_processed": True}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == "Updated test summary"
    assert data["is_processed"] == True

def test_topic_not_found():
    """Test getting non-existent topic"""
    response = client.get("/api/topics/9999")
    assert response.status_code == 404

def test_article_not_found():
    """Test getting non-existent article"""
    response = client.get("/api/articles/9999")
    assert response.status_code == 404

if __name__ == "__main__":
    setup_module()
    
    try:
        test_create_topic()
        test_get_topics()
        test_get_topic()
        test_get_articles_by_topic() 
        test_get_articles_with_sorting()
        test_update_article()
        test_topic_not_found()
        test_article_not_found()
        
        print("All CRUD endpoint tests passed")
        
    finally:
        teardown_module()