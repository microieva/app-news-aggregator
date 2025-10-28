from pydantic_settings import BaseSettings
import logging
import sys
from datetime import datetime

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
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]
    
    DATABASE_URL: str = "sqlite:///./content_aggregator.db"
    
    HUGGINGFACE_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    NEWSAPI_KEY: str = ""
    NEWSAPI_BASE_URL: str = "https://newsapi.org/v2"
    
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

    HUGGINGFACE_BASE_URL: str = "https://api-inference.huggingface.co"
    HUGGINGFACE_DEFAULT_MODEL: str = "facebook/bart-large-cnn"
    HUGGINGFACE_FALLBACK_MODELS: list = [
        "facebook/bart-large-cnn",
        "google/pegasus-xsum",
        "mrm8488/bert-small2bert-small-finetuned-cnn_daily_mail-summarization"
    ]

    GROQ_API_URL: str = "https://api.groq.com/openai/v1"
    GROQ_MODELS: list = [
            "llama-3.3-70b-versatile",   
            "llama-3.1-8b-instant",        
            "mixtral-8x7b-32768",          
            "gemma2-9b-it"         
        ]
    GROQ_API_KEY: str = ""

    DEFAULT_TOPICS: list = [
            {"name": "technology", "description": "Technology news and innovations"},
            {"name": "artificial intelligence", "description": "AI and machine learning"},
            {"name": "programming", "description": "Software development and coding"},
            {"name": "science", "description": "Scientific discoveries and research"},
            {"name": "business", "description": "Business and finance news"},
            {"name": "cybersecurity", "description": "Cybersecurity and privacy"},
            {"name": "palestine", "description": "News related to the occupation"},
            {"name": "politics", "description": "Political news and analysis"},
            {"name": "environment", "description": "Environmental issues and climate change"},
            {"name": "health", "description": "Health and wellness topics"},
            {"name": "other", "description": "Uncategorized topics"}
        ]

    TOPIC_KEYWORDS: dict = {
            "technology": {
                "technology", "tech", "software", "hardware", "digital", "innovation", 
                "gadget", "device", "computer", "internet", "web", "mobile", "app", 
                "application", "software", "hardware", "electronics", "digital", 
                "innovation", "startup", "silicon valley", "tech news", "IT", 
                "information technology", "cloud", "saas", "paas", "iaas"
            },
            "artificial intelligence": {
                "ai", "artificial intelligence", "machine learning", "ml", "neural network", 
                "deep learning", "llm", "gpt", "openai", "chatgpt", "claude", "gemini",
                "transformer", "natural language processing", "nlp", "computer vision",
                "generative ai", "agi", "artificial general intelligence", "robotics",
                "automation", "neural", "algorithm", "training", "inference", "model",
                "prompt", "fine-tuning", "hallucination", "alignment"
            },
            "programming": {
                "programming", "coding", "developer", "software", "code", "algorithm", 
                "framework", "library", "api", "python", "javascript", "java", "c++",
                "rust", "go", "golang", "typescript", "react", "vue", "angular",
                "node.js", "docker", "kubernetes", "git", "github", "debugging",
                "syntax", "compiler", "interpreter", "backend", "frontend", "fullstack",
                "devops", "agile", "scrum", "version control", "pull request", "merge",
                "deployment", "container", "microservices", "rest", "graphql"
            },
            "science": {
                "science", "scientific", "research", "study", "discovery", "experiment", 
                "scientist", "physics", "chemistry", "biology", "astronomy", "space",
                "nasa", "research", "peer review", "journal", "publication", "hypothesis",
                "theory", "scientific method", "laboratory", "data", "analysis",
                "scientific discovery", "breakthrough", "innovation", "academic",
                "university", "institute", "nobel prize", "quantum", "genetics",
                "evolution", "climate science", "environmental science"
            },
            "business": {
                "business", "company", "enterprise", "market", "industry", "corporate", 
                "startup", "venture", "finance", "investment", "economy", "stock",
                "market", "trading", "investment", "venture capital", "vc", "angel investor",
                "ipo", "merger", "acquisition", "revenue", "profit", "loss", "quarterly",
                "earnings", "ceo", "cfo", "cto", "board", "shareholder", "dividend",
                "wall street", "nasdaq", "nyse", "entrepreneur", "entrepreneurship",
                "small business", "corporation", "multinational", "fortune 500"
            },
            "cybersecurity": {
                "cybersecurity", "security", "hack", "breach", "malware", "ransomware", 
                "firewall", "encryption", "privacy", "data breach", "phishing", "vulnerability",
                "exploit", "zero-day", "patch", "update", "antivirus", "antimalware",
                "intrusion", "detection", "prevention", "siem", "soc", "incident response",
                "penetration testing", "pentest", "ethical hacking", "black hat",
                "white hat", "gray hat", "ddos", "botnet", "trojan", "virus", "worm",
                "spyware", "adware", "two-factor authentication", "2fa", "mfa",
                "vpn", "proxy", "tor", "dark web", "data protection", "gdpr", "compliance"
            },
            "palestine": {
                "palestine", "palestinian", "gaza", "west bank", "israel", "occupation",
                "settlement", "nakba", "resistance", "zionism", "zionist", "hamas",
                "fatah", "plo", "idf", "checkpoint", "blockade", "siege", "refugee",
                "right of return", "al-aqsa", "jerusalem", "al-quds", "hebron",
                "ramallah", "jenin", "nablus", "rafah", "khan younis", "deir al-balah",
                "humanitarian", "ceasefire", "unrwa", "bds", "boycott", "divestment",
                "sanctions", "apartheid", "colonial", "settler", "resistance",
                "intifada", "martyr", "solidarity", "free palestine", "liberation"
            },
            "politics": {
                "politics", "political", "government", "election", "vote", "democracy",
                "republic", "congress", "parliament", "senate", "house", "president",
                "prime minister", "minister", "policy", "legislation", "bill", "law",
                "regulation", "executive", "legislative", "judicial", "supreme court",
                "diplomacy", "foreign policy", "domestic policy", "left", "right",
                "liberal", "conservative", "progressive", "socialist", "capitalist",
                "national", "international", "geopolitics", "summit", "treaty",
                "alliance", "united nations", "un", "eu", "nato", "sanction", "embargo"
            },
            "environment": {
                "environment", "environmental", "climate", "climate change", "global warming",
                "sustainability", "renewable", "solar", "wind", "hydro", "geothermal",
                "fossil fuel", "coal", "oil", "gas", "carbon", "emission", "pollution",
                "air quality", "water quality", "conservation", "biodiversity",
                "ecosystem", "wildlife", "deforestation", "reforestation", "ocean",
                "plastic", "recycling", "circular economy", "green", "eco-friendly",
                "carbon footprint", "net zero", "paris agreement", "ipcc", "cop",
                "extinction", "endangered", "habitat", "conservation", "natural resource"
            },
            "health": {
                "health", "healthcare", "medical", "medicine", "doctor", "hospital",
                "patient", "treatment", "therapy", "vaccine", "vaccination", "immune",
                "disease", "illness", "condition", "diagnosis", "prognosis", "recovery",
                "wellness", "fitness", "nutrition", "diet", "exercise", "mental health",
                "psychology", "therapy", "counseling", "public health", "epidemic",
                "pandemic", "virus", "bacteria", "infection", "symptom", "prevention",
                "screening", "checkup", "pharmacy", "prescription", "insurance",
                "telemedicine", "digital health", "wearable", "fitness tracker"
            }
        }
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()


class ColoredFormatter(logging.Formatter):
    """Custom formatter adding colors to log levels"""
    
    GREY = "\x1b[38;20m"
    GREEN = "\x1b[32;20m"
    ORANGE = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"
    
    LEVEL_COLORS = {
        logging.DEBUG: GREY,
        logging.INFO: GREEN,
        logging.WARNING: ORANGE,
        logging.ERROR: RED,
        logging.CRITICAL: BOLD_RED
    }
    
    def format(self, record):
        original_levelname = record.levelname
        
        color = self.LEVEL_COLORS.get(record.levelno, self.RESET)
        record.asctime = self.formatTime(record, self.datefmt)
        record.levelname = f"{color}{record.levelname} - {record.asctime}{self.RESET}"
        result = super().format(record)
        
        if record.levelno >= logging.ERROR:
            result += "\n\n\n"
        
        record.levelname = original_levelname    
        return result
    
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created)
        return dt.strftime('%H:%M:%S')

def setup_colored_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    formatter = ColoredFormatter(
        '%(levelname)s: %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(console_handler)
    
    return logger