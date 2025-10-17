from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.summary_pipeline import summary_pipeline
from app.services.llm import provider_manager
from app.schemas.summary import BatchSummarizeRequest, BatchSummarizeResponse, SummarizeRequest, SummarizeResponse

router = APIRouter()

@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_article(
    request: SummarizeRequest,
    db: AsyncSession = Depends(get_db)
):
    """Summarize a specific article."""
    try:
        from app.models.article import Article
        from sqlalchemy import select
        
        result = await db.execute(
            select(Article).where(Article.id == request.article_id)
        )
        article = result.scalar_one_or_none()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        if not article.content:
            raise HTTPException(status_code=400, detail="Article has no content to summarize")
        
        summary = await summary_pipeline.process_article(
            db=db,
            article=article,
            preferred_provider=request.preferred_provider,
            quality_level=request.quality_level
        )
        
        if summary:
            return SummarizeResponse(
                success=True,
                summary_id=summary.id,
                summary_content=summary.content,
                provider_used=summary.provider,
                processing_time_ms=summary.processing_time_ms
            )
        else:
            return SummarizeResponse(
                success=False,
                error_message="Failed to generate summary"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


@router.post("/summarize/batch", response_model=BatchSummarizeResponse)
async def summarize_batch_articles(
    request: BatchSummarizeRequest,
    db: AsyncSession = Depends(get_db)
):
    """Summarize all unprocessed articles (optionally filtered by topic)."""
    try:
        result = await summary_pipeline.process_unprocessed_articles(
            db=db,
            topic_id=request.topic_id,
            preferred_provider=request.preferred_provider,
            quality_level=request.quality_level,
            batch_size=request.batch_size
        )
        
        return BatchSummarizeResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch summarization failed: {str(e)}")


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
    return summary_pipeline.get_pipeline_stats()


@router.post("/pipeline/stats/reset")
async def reset_pipeline_stats():
    """Reset pipeline statistics."""
    summary_pipeline.reset_stats()
    return {"message": "Pipeline statistics reset"}