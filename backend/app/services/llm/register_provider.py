from .provider_manager import provider_manager
from .huggingface_provider import HuggingFaceProvider
from .groq_provider import GroqProvider
from app.core.config import setup_colored_logging

logger = setup_colored_logging()

def register_providers():
    """Register all LLM providers with the manager"""
    try:
        # Clear any existing providers (for testing)
        provider_manager.providers.clear()
        provider_manager._provider_metrics.clear()

        try:
            huggingface_provider = HuggingFaceProvider()
            provider_manager.register_provider(huggingface_provider)
            logger.info("✅ Registered HuggingFace provider")
        except Exception as e:
            logger.error(f"❌ Failed to register HuggingFace provider: {e}")
        
        try:
            groq_provider = GroqProvider()
            provider_manager.register_provider(groq_provider)
            logger.info("✅ Registered Groq provider")
        except Exception as e:
            logger.error(f"❌ Failed to register Groq provider: {e}")
        
        logger.info(f"Total providers registered: {len(provider_manager.providers)}")
        
    except Exception as e:
        logger.error(f"❌ Failed to register providers: {e}")

register_providers()