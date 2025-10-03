from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/health")
async def health_check():
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy", 
            "message": "API is running successfully",
            "version": "1.0.0"
        }
    )