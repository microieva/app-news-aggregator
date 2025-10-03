from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_endpoint():
    return {
        "message": "Backend is working!",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "test": "/api/test"
        }
    }