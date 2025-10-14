from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

# router for favicon and static assets
favicon_router = APIRouter()

@favicon_router.get("/favicon.ico", include_in_schema=False)
async def get_favicon() -> Response:
    """Handle favicon requests to prevent 404 errors."""
    return JSONResponse(status_code=204)  # No Content