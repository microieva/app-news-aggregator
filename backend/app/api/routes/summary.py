from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.core.background_tasks import task_manager
from app.services.summary_pipeline import summary_pipeline
from app.services.llm import provider_manager
from app.schemas.summary import (
    BatchSummarizeRequest, 
    BatchSummarizeResponse, 
    SummarizeRequest, 
    SummarizeResponse,
    BackgroundSummarizeResponse
)

router = APIRouter()

@router.post("/summarize", response_model=BackgroundSummarizeResponse)
async def summarize_article(
    request: SummarizeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Submit article for background summarization."""
    try:
        from app.models.article import Article
        from sqlalchemy import select
        
        # Get the article
        result = await db.execute(
            select(Article).where(Article.id == request.article_id)
        )
        article = result.scalar_one_or_none()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        if not article.content:
            raise HTTPException(status_code=400, detail="Article has no content to summarize")
        
        if article.summary and article.summary.is_successful:
            return BackgroundSummarizeResponse(
                success=True,
                task_id=None,
                article_id=article.id,
                status="already_completed",
                message="Summary already exists for this article",
                summary_id=article.summary.id
            )
        
        # Check if there's already a pending/processing task for this article
        existing_tasks = await task_manager.get_article_tasks(article.id)
        pending_tasks = [t for t in existing_tasks if t['status'] in ['pending', 'processing']]
        
        if pending_tasks:
            latest_task = pending_tasks[-1]
            return BackgroundSummarizeResponse(
                success=True,
                task_id=latest_task['task_id'],
                article_id=article.id,
                status=latest_task['status'],
                message=f"Summarization already in progress (task: {latest_task['task_id']})"
            )
        
        task_id = await task_manager.submit_article_for_summarization(
            db=db,
            article_id=article.id,
            article_content=article.content,
            article_title=article.title,
            preferred_provider=request.preferred_provider,
            quality_level=request.quality_level
        )
        
        return BackgroundSummarizeResponse(
            success=True,
            task_id=task_id,
            article_id=article.id,
            status="pending",
            message="Article submitted for background summarization"
        )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit summarization: {str(e)}")

@router.post("/summarize/batch", response_model=BatchSummarizeResponse)
async def summarize_batch_articles(
    request: BatchSummarizeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Submit multiple unprocessed articles for background summarization."""
    try:
        from app.models.article import Article
        from sqlalchemy import select
        
        query = select(Article).where(Article.is_processed == False)
        
        if request.topic_id:
            query = query.where(Article.topic_id == request.topic_id)
        
        if request.batch_size and request.batch_size > 0:
            query = query.limit(request.batch_size)
        
        result = await db.execute(query)
        articles = result.scalars().all()
        
        if not articles:
            return BatchSummarizeResponse(
                total_articles=0,
                submitted_tasks=0,
                already_processing=0,
                task_ids=[],
                message="No unprocessed articles found"
            )
        
        submitted_tasks = 0
        task_ids = []
        already_processing = 0
        
        for article in articles:
            if not article.content:
                continue
            
            existing_tasks = await task_manager.get_article_tasks(article.id)
            pending_tasks = [t for t in existing_tasks if t['status'] in ['pending', 'processing']]
            
            if pending_tasks:
                already_processing += 1
                continue
            
            task_id = await task_manager.submit_article_for_summarization(
                db=db,
                article_id=article.id,
                article_content=article.content,
                article_title=article.title,
                preferred_provider=request.preferred_provider,
                quality_level=request.quality_level
            )
            
            task_ids.append(task_id)
            submitted_tasks += 1
        
        return BatchSummarizeResponse(
            total_articles=len(articles),
            submitted_tasks=submitted_tasks,
            already_processing=already_processing,
            task_ids=task_ids,
            message=f"Submitted {submitted_tasks} articles for background summarization"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch summarization failed: {str(e)}")

@router.get("/task/{task_id}")
async def get_summarization_task_status(task_id: str):
    """Get status of a specific summarization task."""
    status = await task_manager.get_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return status

@router.get("/article/{article_id}/tasks")
async def get_article_summarization_tasks(article_id: int, db: AsyncSession = Depends(get_db)):
    """Get all summarization tasks for an article."""
    from app.models.article import Article
    from sqlalchemy import select
    
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    tasks = await task_manager.get_article_tasks(article_id)
    return {
        "article_id": article_id,
        "article_title": article.title,
        "tasks": tasks,
        "total_tasks": len(tasks)
    }

@router.post("/article/{article_id}/retry")
async def retry_article_summarization(
    article_id: int,
    background_tasks: BackgroundTasks,
    preferred_provider: Optional[str] = Query(None),
    quality_level: str = Query("standard"),
    db: AsyncSession = Depends(get_db)
):
    """Retry summarization for an article that previously failed."""
    try:
        from app.models.article import Article
        from sqlalchemy import select
        
        result = await db.execute(select(Article).where(Article.id == article_id))
        article = result.scalar_one_or_none()
        
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
        
        return BackgroundSummarizeResponse(
            success=True,
            task_id=task_id,
            article_id=article.id,
            status="pending",
            message="Article submitted for re-summarization"
        )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit re-summarization: {str(e)}")

@router.get("/providers")
async def get_available_providers():
    """Get available LLM providers and their status."""
    providers = provider_manager.get_available_providers()
    
    provider_status = {}
    for name, provider in providers.items():
        provider_status[name] = {
            "available": await provider.is_available(),
            "models": getattr(provider, 'available_models', []),
            "default_model": getattr(provider, 'default_model', 'unknown')
        }
    
    return {
        "providers": provider_status,
        "fallback_order": provider_manager.fallback_order
    }

@router.get("/pipeline/stats")
async def get_pipeline_stats():
    """Get pipeline statistics."""

    pipeline_stats = summary_pipeline.get_pipeline_stats()
    background_stats = {
        "pending_tasks": await task_manager.get_pending_tasks_count(),
        "active_tasks": len(task_manager.active_tasks),
        "total_tracked_tasks": len(task_manager.task_status)
    }
    
    return {**pipeline_stats, "background_processing": background_stats}

@router.post("/pipeline/stats/reset")
async def reset_pipeline_stats():
    """Reset pipeline statistics."""
    summary_pipeline.reset_stats()
    return {"message": "Pipeline statistics reset"}