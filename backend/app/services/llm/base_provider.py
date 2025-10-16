from abc import ABC, abstractmethod
from typing import Dict, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class SummaryQuality(Enum):
    """Quality levels for summary generation"""
    CONCISE = "concise"      # Very short summary (50-100 chars)
    STANDARD = "standard"    # Normal summary (100-200 chars) 
    DETAILED = "detailed"    # Detailed summary (200-300 chars)

class LLMError(Exception):
    """Base exception for LLM provider errors"""
    pass

class LLMTimeoutError(LLMError):
    """Raised when LLM request times out"""
    pass

class LLMRateLimitError(LLMError):
    """Raised when rate limit is exceeded"""
    pass

class LLMProvider(ABC):
    """
    Abstract base class for all LLM providers.
    All summarization providers must implement this interface.
    """
    
    @abstractmethod
    async def summarize(
        self, 
        text: str, 
        quality: SummaryQuality = SummaryQuality.STANDARD,
        max_retries: int = 3
    ) -> str:
        """
        Generate a summary for the given text.
        
        Args:
            text: The text to summarize
            quality: Desired summary quality level
            max_retries: Maximum number of retry attempts
            
        Returns:
            Generated summary text
            
        Raises:
            LLMError: If summarization fails after all retries
            LLMTimeoutError: If request times out
            LLMRateLimitError: If rate limit is exceeded
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of this LLM provider.
        
        Returns:
            Provider name (e.g., "huggingface", "groq", "openai")
        """
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if the provider is currently available.
        
        Returns:
            True if provider is available, False otherwise
        """
        pass
    
    @abstractmethod
    def get_usage_metrics(self) -> Dict[str, Any]:
        """
        Get usage metrics for this provider.
        
        Returns:
            Dictionary with metrics like request count, error count, etc.
        """
        pass
    
    def _get_summary_length_range(self, quality: SummaryQuality) -> tuple[int, int]:
        """
        Get the target length range for summaries based on quality level.
        
        Args:
            quality: Desired summary quality level
            
        Returns:
            Tuple of (min_length, max_length) in characters
        """
        length_ranges = {
            SummaryQuality.CONCISE: (50, 100),
            SummaryQuality.STANDARD: (100, 200),
            SummaryQuality.DETAILED: (200, 300)
        }
        return length_ranges[quality]
    
    def _create_summary_prompt(self, text: str, quality: SummaryQuality) -> str:
        """
        Create a standardized prompt for summarization.
        
        Args:
            text: Text to summarize
            quality: Desired summary quality level
            
        Returns:
            Formatted prompt string
        """
        min_len, max_len = self._get_summary_length_range(quality)
        
        prompt_templates = {
            SummaryQuality.CONCISE: (
                f"Summarize the following text in {min_len}-{max_len} characters. "
                f"Be very concise and focus on the main point:\n\n{text}"
            ),
            SummaryQuality.STANDARD: (
                f"Summarize the following text in {min_len}-{max_len} characters. "
                f"Capture the key points and main ideas:\n\n{text}"
            ),
            SummaryQuality.DETAILED: (
                f"Create a detailed summary of the following text in {min_len}-{max_len} characters. "
                f"Include important details and context:\n\n{text}"
            )
        }
        
        return prompt_templates[quality]
    
    def _validate_input_text(self, text: str) -> None:
        """
        Validate input text before processing.
        
        Args:
            text: Text to validate
            
        Raises:
            ValueError: If text is invalid
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        if len(text.strip()) < 10:
            raise ValueError("Text is too short to summarize")
        
        if len(text) > 100000:  
            # ~100KB limit
            raise ValueError("Text is too long for summarization")
    
    def _clean_summary_output(self, summary: str) -> str:
        """
        Clean and normalize the summary output.
        
        Args:
            summary: Raw summary text
            
        Returns:
            Cleaned summary text
        """
        # Remove extra whitespace
        summary = ' '.join(summary.split())
        
        # Ensure proper sentence casing
        if summary and not summary[0].isupper():
            summary = summary[0].upper() + summary[1:]
        
        # Ensure it ends with proper punctuation
        if summary and summary[-1] not in ['.', '!', '?']:
            summary += '.'
        
        return summary.strip()