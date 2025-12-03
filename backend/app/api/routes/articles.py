from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError

from app.core import get_db, DatabaseException, ValidationException, NotFoundException
from app.schemas import ArticleBase, ArticleList, ApiResponse, SearchParams, TopicBase, HeadlineList
from app.crud import article as article_crud
from app.crud import topic as topic_crud


router = APIRouter()

@router.get("/search", response_model=ApiResponse)
async def search_articles_route(
    db: AsyncSession = Depends(get_db),
    search_params: SearchParams = Depends()
) -> ApiResponse:

    try:
        articles = await article_crud.search_articles(db, search_params)
        
        api_response = ArticleList(
            articles=articles,
            total=len(articles)
        )
        return ApiResponse(data=api_response)
        
    except SQLAlchemyError as e:
        raise DatabaseException(
            message=e,
            detail="Failed to search articles due to database error",
            context={"search_params": search_params.model_dump()}
        )
    except Exception as e:
        raise DatabaseException(
            message=e,
            detail="Failed to search articles",
            context={"search_params": search_params.model_dump()}
        )

@router.get("/sources", response_model=ApiResponse)
async def read_used_topics(
    db: AsyncSession = Depends(get_db)
) -> ApiResponse:
    try:
        sources = await article_crud.get_used_sources(db)
        return ApiResponse(data=sources)
        
    except SQLAlchemyError as e:
        raise DatabaseException(
            detail="Failed to retrieve sources due to database error",
            context={"endpoint": "read_used_topics"}
        )
    except Exception as e:
        raise DatabaseException(
            detail="Failed to retrieve sources",
            context={"endpoint": "read_used_topics"}
        )
    
@router.get("/frontpage", response_model=ApiResponse)
async def read_frontpage_articles(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    source: Optional[str] = None
) -> ApiResponse:
    """Get frontpage articles, optionally filtered by source"""
    try:
        articles = await article_crud.get_articles(
            db=db, 
            skip=skip, 
            limit=limit, 
            source=source
        )
        total = await article_crud.count_articles(
            db, 
            source=source
        )
        
        api_response = ArticleList(
            articles=articles,
            total=total
        )
        return ApiResponse(data=api_response)
        
    except SQLAlchemyError as e:
        raise DatabaseException(
            detail="Failed to retrieve articles due to database error"
        )
    except Exception as e:
        raise DatabaseException(
            detail="Failed to retrieve articles"
        )
    
@router.get("/", response_model=ApiResponse)
async def read_articles(
    topic: Optional[TopicBase] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    source: Optional[str] = None
) -> ApiResponse:
    """Get articles by topic name with sorting and pagination"""

    try:
        
        articles = await article_crud.get_articles(
            db=db, 
            topic=topic, 
            skip=skip, 
            limit=limit,
            source=source
        )
        
        total = await article_crud.count_articles(db, topic=topic, source=source)
        
        api_response = ArticleList(
            articles=articles,
            total=total
        )
        return ApiResponse(data=api_response)
        
    except ValidationException:
        # Re-raise validation exceptions as they're already properly formatted
        raise
        
    except SQLAlchemyError as e:
        raise DatabaseException(
            detail="Failed to retrieve articles due to database error"
        )
    except Exception as e:
        raise DatabaseException(
            detail="Failed to retrieve articles"
        )

@router.get("/topic/{topic_id}", response_model=ApiResponse)
async def read_articles_by_topic_id(
    topic_id: str,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 4,
    source: Optional[str] = None   
):
    topic = await topic_crud.get_topic(db, topic_id=topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    try:
        articles = await article_crud.get_articles_by_topic_id(
            db=db, 
            skip=skip, 
            limit=limit, 
            source=source,
            topic_id=topic_id
        )
        total = await article_crud.count_articles_by_topic_id(
            db, 
            source=source,
            topic_id=topic_id
        )
        
        api_response = ArticleList(
            articles=articles,
            total=total
        )
        return ApiResponse(data=api_response)
        
    except SQLAlchemyError as e:
        raise DatabaseException(
            detail="Failed to retrieve articles due to database error"
        )
    except Exception as e:
        raise DatabaseException(
            detail="Failed to retrieve articles"
        )

@router.get("/article/{article_id}", response_model=ApiResponse[ArticleBase])
async def read_article(
    article_id: int, 
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[ArticleBase]:
    """Get a specific article by ID"""
    try:
        db_article = await article_crud.get_article_by_id(db, article_id=article_id)
        if db_article is None:
            raise NotFoundException(
                detail="Article not found",
                context={"article_id": article_id}
            )

        return ApiResponse(data=db_article)
        
    except NotFoundException:
        raise
    except SQLAlchemyError as e:
        raise DatabaseException(
            detail="Failed to retrieve article due to database error",
            context={"article_id": article_id}
        )
    except Exception as e:
        raise DatabaseException(
            detail="Failed to retrieve article",
            context={"article_id": article_id}
        )

@router.get("/headlines", response_model=ApiResponse)
async def read_headlines(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 50
) -> ApiResponse:
    try:   
        headlines = await article_crud.get_headlines(
            db=db, 
            skip=skip, 
            limit=limit
        )
        
        total = await article_crud.count_articles(db)
        
        api_response = HeadlineList(
            headlines=headlines,
            total=total
        )
        return ApiResponse(data=api_response)
        
    except ValidationException:
        # Re-raise validation exceptions as they're already properly formatted
        raise
        
    except SQLAlchemyError as e:
        raise DatabaseException(
            detail="Failed to retrieve articles due to database error"
        )
    except Exception as e:
        raise DatabaseException(
            detail="Failed to retrieve articles"
        )
