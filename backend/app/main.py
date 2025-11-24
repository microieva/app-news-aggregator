from fastapi import FastAPI
import uvicorn
from app.api.routes import api_router
from app.core import favicon_router, settings, setup_exception_handlers, app_lifespan, setup_cors
from app.services.llm import register_providers


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.PROJECT_VERSION,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOC_URL,
        lifespan=app_lifespan
    )
    
    setup_cors(application)
    
    application.include_router(favicon_router)
    application.include_router(api_router)
    
    return application

register_providers()
app = create_application()
setup_exception_handlers(app)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )