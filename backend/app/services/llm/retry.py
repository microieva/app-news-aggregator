from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import Type, Tuple
from .base_provider import LLMTimeoutError, LLMRateLimitError

def llm_retry(
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 10.0,
    retry_exceptions: Tuple[Type[Exception], ...] = (LLMTimeoutError, LLMRateLimitError)
):
    """
    Decorator for retrying LLM operations with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time between retries (seconds)
        max_wait: Maximum wait time between retries (seconds)
        retry_exceptions: Exception types that should trigger retries
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type(retry_exceptions)
    )