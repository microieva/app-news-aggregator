import httpx
import logging
from typing import Dict, Any

from .base_provider import LLMProvider, SummaryQuality, LLMError, LLMTimeoutError, LLMRateLimitError
from .retry import llm_retry
from app.core.config import settings

logger = logging.getLogger(__name__)

class HuggingFaceProvider(LLMProvider):
    """
    Hugging Face Inference API provider for text summarization.
    Free tier with generous rate limits - perfect for development.
    """
    
    def __init__(self):
        self.api_key = settings.HUGGINGFACE_API_KEY
        self.base_url = settings.HUGGINGFACE_BASE_URL 
        self.default_model = settings.HUGGINGFACE_DEFAULT_MODEL 
        self.fallback_models = settings.HUGGINGFACE_FALLBACK_MODELS
        
        # Track usage metrics
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "model_usage": {}
        }
        
        self.client = httpx.AsyncClient(
            timeout=60.0,
            headers=self._get_headers()
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for Hugging Face API"""
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    @llm_retry(max_attempts=3, min_wait=2.0, max_wait=10.0)
    async def summarize(
        self, 
        text: str, 
        quality: SummaryQuality = SummaryQuality.STANDARD,
        max_retries: int = 3
    ) -> str:
        """
        Generate summary using Hugging Face Inference API.
        
        Args:
            text: Text to summarize
            quality: Desired summary quality level
            max_retries: Maximum number of retry attempts
            
        Returns:
            Generated summary text
        """
        self.metrics["total_requests"] += 1
        
        try:
            self._validate_input_text(text)
            
            prompt = self._create_summary_prompt(text, quality)
            
            # Try models 
            for model in [self.default_model] + self.fallback_models:
                try:
                    summary = await self._call_huggingface_api(prompt, model)
                    if summary and self._is_valid_summary(summary):
                        self.metrics["successful_requests"] += 1
                        self.metrics["model_usage"][model] = self.metrics["model_usage"].get(model, 0) + 1
                        return self._clean_summary_output(summary)
                        
                except LLMError as e:
                    logger.warning(f"Model {model} failed: {e}")
                    continue
            
            raise LLMError("All Hugging Face models failed to generate a summary")
            
        except Exception as e:
            self.metrics["failed_requests"] += 1
            if isinstance(e, LLMError):
                raise e
            else:
                raise LLMError(f"Hugging Face API error: {str(e)}")
    
    async def _call_huggingface_api(self, text: str, model: str) -> str:
        """
        Call Hugging Face Inference API.
        
        Args:
            text: Text to summarize
            model: Model to use for summarization
            
        Returns:
            Generated summary text
        """
        payload = {
            "inputs": text,
            "parameters": {
                "max_length": self._get_max_length_for_model(model),
                "min_length": 30,
                "do_sample": False,  # For more deterministic results
                "temperature": 0.7,  # Balance between creativity and consistency
            },
            "options": {
                "wait_for_model": True,  
                "use_cache": True
            }
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/models/{model}",
                json=payload
            )
            
            return await self._handle_api_response(response, model)
            
        except httpx.TimeoutException:
            raise LLMTimeoutError(f"Hugging Face API timeout for model {model}")
        except httpx.RequestError as e:
            raise LLMError(f"HTTP error calling Hugging Face API: {str(e)}")
    
    async def _handle_api_response(self, response: httpx.Response, model: str) -> str:
        """Handle API response and extract summary"""
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                summary = data[0].get('summary_text', '')
                if summary:
                    return summary
            
            if isinstance(data, dict) and 'generated_text' in data:
                return data['generated_text']
            elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                if 'generated_text' in data[0]:
                    return data[0]['generated_text']
            
            raise LLMError(f"Unexpected response format from model {model}")
            
        elif response.status_code == 503:
            raise LLMError(f"Model {model} is currently loading, please try again in a few moments")
            
        elif response.status_code == 429:
            raise LLMRateLimitError("Hugging Face API rate limit exceeded")
            
        elif response.status_code == 401:
            raise LLMError("Invalid Hugging Face API key")
            
        elif response.status_code == 400:
            error_msg = response.json().get('error', 'Bad request')
            raise LLMError(f"Hugging Face API error: {error_msg}")
            
        else:
            error_msg = f"HTTP {response.status_code}"
            try:
                error_data = response.json()
                error_msg = error_data.get('error', error_msg)
            except:
                pass
            raise LLMError(f"Hugging Face API error: {error_msg}")
    
    def _get_max_length_for_model(self, model: str) -> int:
        """Get appropriate max length for different models"""
        model_lengths = {
            "facebook/bart-large-cnn": 142,  # Standard max
            "google/pegasus-xsum": 64,   
            "mrm8488/bert-small2bert-small-finetuned-cnn_daily_mail-summarization": 128
        }
        return model_lengths.get(model, 142) 
    
    def _is_valid_summary(self, summary: str) -> bool:
        """Validate that the generated summary is reasonable"""
        if not summary or not summary.strip():
            return False
        
        # Check if summary is too short (likely error)
        if len(summary.strip()) < 10:
            return False
        
        # Check for common error patterns
        error_indicators = [
            "error",
            "exception",
            "model is currently loading",
            "rate limit",
            "unauthorized"
        ]
        
        summary_lower = summary.lower()
        return not any(indicator in summary_lower for indicator in error_indicators)
    
    async def is_available(self) -> bool:
        """
        Check if Hugging Face API is available.
        We'll consider it available if we have an API key.
        """
        if not self.api_key:
            logger.warning("Hugging Face API key not configured")
            return False
        
        try:
            # Quick test if API is responsive
            test_response = await self.client.get(
                f"{self.base_url}/models/{self.default_model}",
                timeout=5.0
            )
            return test_response.status_code in [200, 401, 403]  # Even auth errors mean API is up
        except:
            return False
    
    def get_provider_name(self) -> str:
        return "huggingface"
    
    def get_usage_metrics(self) -> Dict[str, Any]:
        """Get detailed usage metrics"""
        success_rate = (
            (self.metrics["successful_requests"] / self.metrics["total_requests"] * 100)
            if self.metrics["total_requests"] > 0 else 0
        )
        
        return {
            **self.metrics,
            "success_rate": round(success_rate, 2),
            "default_model": self.default_model,
            "available_models": self.fallback_models
        }
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def __del__(self):
        # Ensure client is closed when provider is garbage collected
        try:
            import asyncio
            if hasattr(self, 'client') and not self.client.is_closed:
                asyncio.create_task(self.client.aclose())
        except:
            pass

# Factory function to create and register the provider
async def create_huggingface_provider():
    """Create and initialize Hugging Face provider"""
    provider = HuggingFaceProvider()

    is_available = await provider.is_available()
    if is_available:
        logger.info("Hugging Face provider initialized and available")
    else:
        logger.warning("Hugging Face provider initialized but not available (check API key)")
    
    return provider