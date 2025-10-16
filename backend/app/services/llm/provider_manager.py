from typing import List, Dict, Any, Optional
from .base_provider import LLMProvider, SummaryQuality, LLMError
import logging

logger = logging.getLogger(__name__)

class LLMProviderManager:
    """
    Manages multiple LLM providers with fallback logic.
    """
    
    def __init__(self):
        self.providers: List[LLMProvider] = []
        self._provider_metrics: Dict[str, Dict[str, Any]] = {}
    
    def register_provider(self, provider: LLMProvider) -> None:
        """
        Register a new LLM provider.
        
        Args:
            provider: LLM provider instance to register
        """
        provider_name = provider.get_provider_name()
        self.providers.append(provider)
        self._provider_metrics[provider_name] = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "last_used": None
        }
        logger.info(f"Registered LLM provider: {provider_name}")
    
    async def summarize_with_fallback(
        self, 
        text: str, 
        quality: SummaryQuality = SummaryQuality.STANDARD,
        preferred_provider: Optional[str] = None
    ) -> str:
        """
        Generate summary using available providers with fallback logic.
        
        Args:
            text: Text to summarize
            quality: Desired summary quality level
            preferred_provider: Name of preferred provider (if available)
            
        Returns:
            Generated summary text
            
        Raises:
            LLMError: If all providers fail
        """
        errors = []
        
        if preferred_provider:
            provider = self._get_provider_by_name(preferred_provider)
            if provider and await provider.is_available():
                try:
                    result = await self._summarize_with_provider(provider, text, quality)
                    return result
                except LLMError as e:
                    errors.append(f"{preferred_provider}: {e}")
                    logger.warning(f"Preferred provider {preferred_provider} failed: {e}")
        
        for provider in self.providers:
            if preferred_provider and provider.get_provider_name() == preferred_provider:
                continue 
                
            if await provider.is_available():
                try:
                    result = await self._summarize_with_provider(provider, text, quality)
                    return result
                except LLMError as e:
                    provider_name = provider.get_provider_name()
                    errors.append(f"{provider_name}: {e}")
                    logger.warning(f"Provider {provider_name} failed: {e}")
        
        error_msg = f"All LLM providers failed. Errors: {'; '.join(errors)}"
        logger.error(error_msg)
        raise LLMError(error_msg)
    
    async def _summarize_with_provider(
        self, 
        provider: LLMProvider, 
        text: str, 
        quality: SummaryQuality
    ) -> str:
        """
        Summarize text with a specific provider and track metrics.
        """
        provider_name = provider.get_provider_name()
        
        self._provider_metrics[provider_name]["total_requests"] += 1
        self._provider_metrics[provider_name]["last_used"] = None  # Would use datetime.now()
        
        try:
            summary = await provider.summarize(text, quality)
            self._provider_metrics[provider_name]["successful_requests"] += 1
            logger.info(f"Successfully generated summary using {provider_name}")
            return summary
            
        except Exception as e:
            self._provider_metrics[provider_name]["failed_requests"] += 1
            raise e
    
    def _get_provider_by_name(self, name: str) -> Optional[LLMProvider]:
        """
        Get provider by name.
        
        Args:
            name: Provider name
            
        Returns:
            Provider instance or None if not found
        """
        for provider in self.providers:
            if provider.get_provider_name() == name:
                return provider
        return None
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of available provider names.
        
        Returns:
            List of provider names that are currently available
        """
        available = []
        for provider in self.providers:
            # Note: This doesn't check actual availability, just registration
            available.append(provider.get_provider_name())
        return available
    
    def get_provider_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metrics for all providers.
        
        Returns:
            Dictionary of provider metrics
        """
        return self._provider_metrics.copy()
    
    def get_overall_metrics(self) -> Dict[str, Any]:
        """
        Get overall metrics across all providers.
        
        Returns:
            Dictionary with overall metrics
        """
        total_requests = 0
        successful_requests = 0
        failed_requests = 0
        
        for metrics in self._provider_metrics.values():
            total_requests += metrics["total_requests"]
            successful_requests += metrics["successful_requests"]
            failed_requests += metrics["failed_requests"]
        
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "total_providers": len(self.providers),
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": round(success_rate, 2)
        }

provider_manager = LLMProviderManager()