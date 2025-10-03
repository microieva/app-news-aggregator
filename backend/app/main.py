from fastapi import FastAPI
import uvicorn
from app.core.config import settings
from app.core.middleware import setup_cors
from app.api.routes import api_router
from app.core.favicon import favicon_router

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.PROJECT_VERSION,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOC_URL,
    )
    
    setup_cors(application)
    
    application.include_router(favicon_router)
    application.include_router(api_router)
    
    return application

app = create_application()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )