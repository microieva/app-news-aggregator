from fastapi import APIRouter
from app.api.routes import health, root, test, topics, articles

api_router = APIRouter()

api_router.include_router(root.router, tags=["root"])
api_router.include_router(health.router, tags=["health"])
api_router.include_router(test.router, prefix="/api", tags=["test"])
api_router.include_router(topics.router, prefix="/api/topics", tags=["topics"])
api_router.include_router(articles.router, prefix="/api/articles", tags=["articles"])