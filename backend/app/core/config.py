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

    RSS_FEEDS: dict = {
        "abc_news": "https://www.abc.net.au/news/feed/2942460/rss.xml",
        "al_jazeera_english": "https://www.aljazeera.com/xml/rss/all.xml",
        "al_jazeera_latest": "https://www.aljazeera.com/xml/rss/all.xml",
        "al_jazeera_news": "https://www.aljazeera.com/xml/rss/all.xml",
        "al_jazeera_top_stories": "https://www.aljazeera.com/xml/rss/all.xml",
        "ars_technica": "https://feeds.arstechnica.com/arstechnica/index",
        "bbc_entertainment": "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
        "bbc_news": "http://feeds.bbci.co.uk/news/rss.xml",
        "bbc_science": "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
        "bbc_world": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "cnn_top_stories": "http://rss.cnn.com/rss/edition.rss",
        "cnn_world": "http://rss.cnn.com/rss/edition_world.rss",
        "dw_english": "https://rss.dw.com/rdf/rss-en-all",
        "financial_times": "https://www.ft.com/?format=rss",
        "france24_english": "https://www.france24.com/en/rss",
        "hacker_news": "https://news.ycombinator.com/rss",
        "nasa_news": "https://www.nasa.gov/rss/dyn/breaking_news.rss",
        "roya_news": "https://royanews.tv/rss",
        "science_daily": "https://www.sciencedaily.com/rss/all.xml",
        "tass_english": "https://tass.com/rss/v2.xml",
        "techcrunch": "https://techcrunch.com/feed/",
        "variety": "https://variety.com/feed/",
        "vox_news": "https://www.vox.com/rss/world-politics/index.xml",
        "wired": "https://www.wired.com/feed/rss",
        "xinhua_english": "http://www.xinhuanet.com/english/rss/worldrss.xml",
    }
    
    RSS_ARTICLE_LIMIT: int = 10

    GNEWS_API_KEY: str = ""
    GNEWS_API_URL: str = "https://gnews.io/api/v4"
    GNEWS_ARTICLE_LIMIT: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()