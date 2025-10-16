import httpx
import logging
from typing import Dict, Any, List

from .base_provider import LLMProvider, SummaryQuality, LLMError, LLMTimeoutError, LLMRateLimitError
from .retry import llm_retry
from app.core.config import settings

logger = logging.getLogger(__name__)

class GroqProvider(LLMProvider):
    """
    Groq API provider for ultra-fast text summarization.
    High-performance fallback with very fast response times.
    """
    
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.base_url = settings.GROQ_API_URL.rstrip('/')
        
        # Set default models if not configured
        self.available_models: List[str] = settings.GROQ_MODELS or [
            "mixtral-8x7b-32768",
            "llama3-70b-8192", 
            "llama3-8b-8192"
        ]
        self.default_model = self.available_models[0]
        
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "model_usage": {},
            "response_times": [] 
        }
        
        self._client = None  # Lazy initialization
        
    @property
    async def client(self) -> httpx.AsyncClient:
        """Lazy initialization of HTTP client"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                headers=self._get_headers()
            )
        return self._client
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for Groq API"""
        if not self.api_key:
            raise LLMError("Groq API key not configured")
            
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    @llm_retry(max_attempts=2, min_wait=1.0, max_wait=5.0) 
    async def summarize(
        self, 
        text: str, 
        quality: SummaryQuality = SummaryQuality.STANDARD,
        max_retries: int = 2
    ) -> str:
        """
        Generate summary using Groq's ultra-fast API.
        
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
            prompt = self._create_groq_prompt(text, quality)
            
            for model in self.available_models:
                try:
                    import time
                    start_time = time.time()
                    
                    summary = await self._call_groq_api(prompt, model)
                    
                    response_time = time.time() - start_time
                    self.metrics["response_times"].append(response_time)
                    
                    if summary and self._is_valid_summary(summary):
                        self.metrics["successful_requests"] += 1
                        self.metrics["model_usage"][model] = self.metrics["model_usage"].get(model, 0) + 1
                        
                        # Estimate tokens (rough approximation)
                        estimated_tokens = len(summary.split()) * 1.3
                        self.metrics["total_tokens"] += int(estimated_tokens)
                        
                        logger.info(f"Groq summary generated in {response_time:.2f}s using {model}")
                        return self._clean_summary_output(summary)
                        
                except LLMError as e:
                    logger.warning(f"Groq model {model} failed: {e}")
                    continue
            
            raise LLMError("All Groq models failed to generate a summary")
            
        except Exception as e:
            self.metrics["failed_requests"] += 1
            if isinstance(e, LLMError):
                raise e
            else:
                raise LLMError(f"Groq API error: {str(e)}")
    
    def _create_groq_prompt(self, text: str, quality: SummaryQuality) -> str:
        """
        Create optimized prompt for Groq models.
        
        Args:
            text: Text to summarize
            quality: Desired summary quality level
            
        Returns:
            Formatted prompt string
        """
        min_len, max_len = self._get_summary_length_range(quality)
        
        quality_instructions = {
            SummaryQuality.CONCISE: f"Create a very concise summary in {min_len}-{max_len} characters. Focus only on the most essential point.",
            SummaryQuality.STANDARD: f"Create a clear summary in {min_len}-{max_len} characters. Capture the key points and main ideas.",
            SummaryQuality.DETAILED: f"Create a comprehensive summary in {min_len}-{max_len} characters. Include important details and context."
        }
        
        prompt = f"""
        {quality_instructions[quality]}
        
        Text to summarize:
        {text}
        
        Summary:
        """
        
        return prompt.strip()
    
    async def _call_groq_api(self, prompt: str, model: str) -> str:
        """
        Call Groq Chat Completions API.
        
        Args:
            prompt: Formatted prompt
            model: Model to use
            
        Returns:
            Generated summary text
        """
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,  # Lower temperature for more consistent summaries
            "max_tokens": self._get_max_tokens_for_quality(),
            "top_p": 0.9,
            "stream": False,
        }
        
        try:
            client = await self.client
            url = f"{self.base_url}/chat/completions"
            
            logger.debug(f"Calling Groq API with model: {model}")
            logger.debug(f"Prompt length: {len(prompt)} chars")
            
            response = await client.post(url, json=payload)
            
            logger.debug(f"Groq API response status: {response.status_code}")
            
            return await self._handle_api_response(response, model)
            
        except httpx.TimeoutException:
            raise LLMTimeoutError(f"Groq API timeout for model {model}")
        except httpx.RequestError as e:
            raise LLMError(f"HTTP error calling Groq API: {str(e)}")
    
    async def _handle_api_response(self, response: httpx.Response, model: str) -> str:
        """Handle API response and extract summary"""
        try:
            response_data = response.json()
        except Exception as e:
            raise LLMError(f"Failed to parse Groq API response: {str(e)}")
        
        if response.status_code == 200:
            if 'choices' in response_data and len(response_data['choices']) > 0:
                choice = response_data['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    summary = choice['message']['content'].strip()
                    
                    if 'usage' in response_data:
                        usage = response_data['usage']
                        logger.debug(f"Groq usage - Tokens: {usage.get('total_tokens', 'N/A')}")
                    
                    return summary
            
            raise LLMError(f"Unexpected response format from Groq model {model}")
            
        elif response.status_code == 429:
            retry_after = response.headers.get('retry-after', 'unknown')
            raise LLMRateLimitError(f"Groq rate limit exceeded. Retry after: {retry_after}s")
            
        elif response.status_code == 401:
            raise LLMError("Invalid Groq API key")
            
        elif response.status_code == 400:
            error_msg = response_data.get('error', {}).get('message', 'Bad request')
            logger.error(f"Groq API 400 error: {error_msg}")
            raise LLMError(f"Groq API error: {error_msg}")
            
        elif response.status_code == 403:
            raise LLMError("Groq API access forbidden. Check your API key permissions.")
            
        elif response.status_code == 422:
            error_msg = response_data.get('error', {}).get('message', 'Validation error')
            raise LLMError(f"Groq validation error: {error_msg}")
            
        elif response.status_code == 404:
            raise LLMError(f"Groq model not found: {model}. Check model name.")
            
        else:
            error_msg = f"HTTP {response.status_code}"
            if isinstance(response_data, dict):
                error_msg = response_data.get('error', {}).get('message', error_msg)
            raise LLMError(f"Groq API error: {error_msg}")
    
    def _get_max_tokens_for_quality(self) -> int:
        """Get appropriate max_tokens for different quality levels"""
        # Conservative token limits for summaries
        return 512  # Increased from 300 for better summaries
    
    def _is_valid_summary(self, summary: str) -> bool:
        """Validate that the generated summary is reasonable"""
        if not summary or not summary.strip():
            return False
        
        # Check if summary is too short (likely error)
        if len(summary.strip()) < 10:
            return False
        
        error_indicators = [
            "error",
            "exception", 
            "rate limit",
            "unauthorized",
            "sorry,",
            "i cannot",
            "i'm sorry",
            "as an ai",
            "api key"
        ]
        
        summary_lower = summary.lower()
        return not any(indicator in summary_lower for indicator in error_indicators)
    
    async def is_available(self) -> bool:
        """
        Check if Groq API is available with valid credentials.
        Only returns True for successful (200) or rate-limited (429) responses.
        """
        if not self.api_key:
            logger.warning("Groq API key not configured")
            return False
        
        # Validate API key format
        if not self.api_key.startswith('gsk_'):
            logger.warning("Groq API key format invalid (should start with 'gsk_')")
            return False
        
        try:
            test_payload = {
                "model": self.default_model,
                "messages": [{"role": "user", "content": "Say 'hello'"}],
                "max_tokens": 5,
                "temperature": 0.1
            }
            
            client = await self.client
            url = f"{self.base_url}/chat/completions"
            
            response = await client.post(
                url,
                json=test_payload,
                timeout=10.0
            )
            
            # Only return True for successful or rate-limited responses
            # 401 means invalid API key, so provider is not available
            available = response.status_code in [200, 429]
            
            if not available:
                logger.warning(f"Groq availability check failed with status: {response.status_code}")
                try:
                    error_data = response.json()
                    logger.debug(f"Groq error details: {error_data}")
                except:
                    pass
                    
            return available
            
        except httpx.TimeoutException:
            logger.warning("Groq availability check timed out")
            return False
        except Exception as e:
            logger.warning(f"Groq availability check failed: {e}")
            return False
    
    def get_provider_name(self) -> str:
        return "groq"
    
    def get_usage_metrics(self) -> Dict[str, Any]:
        """Get detailed usage metrics including performance data"""
        success_rate = (
            (self.metrics["successful_requests"] / self.metrics["total_requests"] * 100)
            if self.metrics["total_requests"] > 0 else 0
        )
        
        avg_response_time = (
            sum(self.metrics["response_times"]) / len(self.metrics["response_times"])
            if self.metrics["response_times"] else 0
        )
        
        return {
            **self.metrics,
            "success_rate": round(success_rate, 2),
            "average_response_time": round(avg_response_time, 2),
            "available_models": self.available_models,
            "default_model": self.default_model,
            "total_models_used": len(self.metrics["model_usage"])
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance-specific statistics"""
        if not self.metrics["response_times"]:
            return {"message": "No performance data available"}
        
        times = self.metrics["response_times"]
        return {
            "request_count": len(times),
            "average_time": round(sum(times) / len(times), 2),
            "min_time": round(min(times), 2),
            "max_time": round(max(times), 2),
            "p95_time": round(sorted(times)[int(len(times) * 0.95)], 2) if len(times) > 1 else 0
        }
    
    async def close(self):
        """Close the HTTP client explicitly"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

async def create_groq_provider():
    """Create and initialize Groq provider"""
    provider = GroqProvider()
    
    # Validate configuration
    if not provider.api_key:
        logger.error("Groq API key not found in settings")
        return provider
    
    if not provider.api_key.startswith('gsk_'):
        logger.error("Groq API key format invalid - should start with 'gsk_'")
        return provider
    
    is_available = await provider.is_available()
    if is_available:
        logger.info("✅ Groq provider initialized and available - ready for high-speed summarization!")
    else:
        logger.warning("❌ Groq provider initialized but not available (check API key and model configuration)")
    
    return provider