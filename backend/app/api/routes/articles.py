from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.schemas import ArticleBase, ArticleList, ArticleUpdate, ArticleCreate, TaskStatusResponse, ApiResponse
from app.crud import article as article_crud
from app.crud import topic as topic_crud
from app.core.background_tasks import task_manager

router = APIRouter()

@router.get("/with-summaries", response_model=ApiResponse)
async def read_articles_with_summaries(
    db:AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    topic_name: Optional[str] = None,
    source: Optional[str] = None
):
    articles = await article_crud.get_articles_with_summaries(db = db, skip=skip, limit=limit, topic_name=topic_name, source=source)
    total = await article_crud.get_articles_with_summaries_count(db, topic_name=topic_name, source=source)

    if articles:
        api_response = ArticleList(
            articles=articles,
            total=total,
            topic_name=topic_name 
        )
        return ApiResponse(
            data=api_response
        )
    else:  
        raise HTTPException(status_code=404, detail="No articles with summaries found")
    

@router.get("/topic-name/{topic_name}", response_model=ApiResponse)
async def read_articles_by_topic(
    topic_name: str,
    skip: int = Query(0, ge=0, description="Number of articles to skip"),
    limit: int = Query(50, ge=1, le=200, description="Number of articles to return"),
    sort_by: str = Query("published_at", description="Sort by field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    include_summary: bool = Query(False, description="Include summary status for each article"),
    db: AsyncSession = Depends(get_db),
    source: Optional[str] = None
):
    """Get articles by topic name with sorting and pagination"""

    name = topic_name.replace('-', ' ')
    valid_sort_fields = ["published_at", "created_at", "title"]
    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid sort field. Must be one of: {valid_sort_fields}"
        )
    
    if sort_order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400, 
            detail="Invalid sort order. Must be 'asc' or 'desc'"
        )
    
    articles = await article_crud.get_articles_by_topic_name(
        db=db, 
        topic_name=name, 
        skip=skip, 
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
        source=source
    )
    
    total = await article_crud.get_articles_with_summaries_count(db, topic_name=name, source=source)
    
    # enhanced_articles = []
    # for article in articles:
    #     article_dict = article.to_dict() if hasattr(article, 'to_dict') else dict(article)
        
    #     if include_summary_status:
    #         tasks = await task_manager.get_article_tasks(article.id)
    #         latest_task = tasks[-1] if tasks else None
            
    #         article_dict["summary_status"] = {
    #             "is_processed": article.is_processed,
    #             "has_summary": hasattr(article, 'summary') and article.summary is not None,
    #             "latest_task": latest_task
    #         }
        
    #     enhanced_articles.append(article_dict)
    
    if articles:
        api_response = ArticleList(
            articles=articles,
            total=total,
            topic_name=name 
        )
        return ApiResponse(
            data=api_response
        )
    else:  
        raise HTTPException(status_code=404, detail="No articles found for topic {name}")
    
@router.get("/sources", response_model=ApiResponse)
async def read_used_topics(
    db:AsyncSession = Depends(get_db)
):
    """Get used topics with pagination"""
    sources = await article_crud.get_used_sources(db)

    if sources:
        api_response = sources
        return ApiResponse(
            data=api_response
        )
    else:  
        raise HTTPException(status_code=404, detail="No sources found")


@router.get("/topic/{topic_id}", response_model=ApiResponse)
async def read_articles_by_topic(
    topic_id: int,
    skip: int = Query(0, ge=0, description="Number of articles to skip"),
    limit: int = Query(50, ge=1, le=200, description="Number of articles to return"),
    sort_by: str = Query("published_at", description="Sort by field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    include_summary_status: bool = Query(False, description="Include summary status for each article"),
    db: AsyncSession = Depends(get_db)
):
    """Get articles by topic ID with sorting and pagination"""

    topic = await topic_crud.get_topic(db, topic_id=topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    valid_sort_fields = ["published_at", "created_at", "title"]
    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid sort field. Must be one of: {valid_sort_fields}"
        )
    
    if sort_order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400, 
            detail="Invalid sort order. Must be 'asc' or 'desc'"
        )
    
    articles = await article_crud.get_articles_by_topic(
        db, 
        topic_id=topic_id, 
        skip=skip, 
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    total = await article_crud.get_articles_count(db, topic_id=topic_id)
    
    enhanced_articles = []
    for article in articles:
        article_dict = article.to_dict() if hasattr(article, 'to_dict') else dict(article)
        
        if include_summary_status:
            tasks = await task_manager.get_article_tasks(article.id)
            latest_task = tasks[-1] if tasks else None
            
            article_dict["summary_status"] = {
                "is_processed": article.is_processed,
                "has_summary": hasattr(article, 'summary') and article.summary is not None,
                "latest_task": latest_task
            }
        
        enhanced_articles.append(article_dict)
    
    return ArticleList(
        articles=enhanced_articles, 
        total=total,
        topic_name=topic.name
    )

@router.post("/", response_model=TaskStatusResponse)
async def create_article(
    article: ArticleCreate,
    background_tasks: BackgroundTasks,
    preferred_provider: Optional[str] = Query(None, description="Preferred LLM provider"),
    quality_level: str = Query("standard", description="Summary quality level"),
    db: AsyncSession = Depends(get_db)
):
    """Create article and start background summarization"""
    try:
        existing_article = await article_crud.get_article_by_url(db, url=article.url)
        if existing_article:
            tasks = await task_manager.get_article_tasks(existing_article.id)
            latest_task = tasks[-1] if tasks else None
            
            return TaskStatusResponse(
                task_id=latest_task["task_id"] if latest_task else None,
                article_id=existing_article.id,
                status=latest_task["status"] if latest_task else "exists",
                message="Article already exists" + (" with pending summarization" if latest_task else "")
            )
        
        db_article = await article_crud.create_article(db, article=article)
        
        if not db_article.content:
            raise HTTPException(
                status_code=400, 
                detail="Article content is required for summarization"
            )
        
        task_id = await task_manager.submit_article_for_summarization(
            db=db,
            article_id=db_article.id,
            article_content=db_article.content,
            article_title=db_article.title,
            preferred_provider=preferred_provider,
            quality_level=quality_level
        )
        
        return TaskStatusResponse(
            task_id=task_id,
            article_id=db_article.id,
            status="pending",
            message="Article submitted for background summarization"
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create article: {str(e)}")

@router.get("/{article_id}", response_model=ArticleBase)
async def read_article(
    article_id: int, 
    include_task_status: bool = Query(False, description="Include background task status"),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific article by ID"""
    db_article = await article_crud.get_article_by_id(db, article_id=article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Convert to dict for potential enhancement
    article_data = db_article.to_dict() if hasattr(db_article, 'to_dict') else dict(db_article)
    
    if include_task_status:
        tasks = await task_manager.get_article_tasks(article_id)
        article_data["background_tasks"] = tasks
    
    return article_data

@router.put("/{article_id}", response_model=ArticleBase)
async def update_article(
    article_id: int, 
    article_update: ArticleUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """Update an article"""
    db_article = await article_crud.update_article(db, article_id=article_id, article_update=article_update)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return db_article

@router.delete("/{article_id}")
async def delete_article(article_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an article and any associated background tasks"""

    article = await article_crud.get_article(db, article_id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    tasks = await task_manager.get_article_tasks(article_id)
    for task in tasks:
        # Note: Active tasks will continue but fail gracefully when they can't find the article
        pass  
    
    success = await article_crud.delete_article(db, article_id=article_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete article")
    
    return {"message": "Article deleted successfully"}

# New endpoints for background task management
@router.get("/{article_id}/tasks")
async def get_article_tasks(article_id: int, db: AsyncSession = Depends(get_db)):
    """Get all background tasks for an article"""

    article = await article_crud.get_article(db, article_id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    tasks = await task_manager.get_article_tasks(article_id)
    return {
        "article_id": article_id,
        "article_title": article.title,
        "tasks": tasks,
        "total_tasks": len(tasks)
    }

@router.post("/{article_id}/retry-summarization", response_model=TaskStatusResponse)
async def retry_article_summarization(
    article_id: int,
    background_tasks: BackgroundTasks,
    preferred_provider: Optional[str] = Query(None, description="Preferred LLM provider"),
    quality_level: str = Query("standard", description="Summary quality level"),
    db: AsyncSession = Depends(get_db)
):
    """Retry summarization for an existing article"""
    article = await article_crud.get_article(db, article_id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    if not article.content:
        raise HTTPException(status_code=400, detail="Article has no content to summarize")
    
    task_id = await task_manager.submit_article_for_summarization(
        db=db,
        article_id=article.id,
        article_content=article.content,
        article_title=article.title,
        preferred_provider=preferred_provider,
        quality_level=quality_level
    )
    
    return TaskStatusResponse(
        task_id=task_id,
        article_id=article.id,
        status="pending", 
        message="Article submitted for re-summarization"
    )