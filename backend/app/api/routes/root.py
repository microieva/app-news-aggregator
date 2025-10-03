from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    return {
        "message": "Smart Content Aggregator API is running!",
        "docs": "/docs",
        "health": "/health"
    }