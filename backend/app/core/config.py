from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Content Aggregator API"
    PROJECT_DESCRIPTION: str = "API for aggregating and summarizing content from multiple sources"
    PROJECT_VERSION: str = "1.0.0"
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    
    ALLOWED_HOSTS: list = [
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:8000"
    ]
    
    DATABASE_URL: str = "sqlite:///./content_aggregator.db"
    
    HUGGINGFACE_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    NEWSAPI_KEY: str = ""
    
    REDDIT_POST_LIMIT: int = 15
    REDDIT_SUBREDDITS: list = ["all", "programming", "technology", "news"]
    NEWSAPI_ARTICLE_LIMIT: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()