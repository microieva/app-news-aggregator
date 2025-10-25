import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.services.llm import LLMProvider, SummaryQuality, LLMError, provider_manager
from app.core.config import setup_colored_logging

logging.basicConfig(level=logging.INFO)
logger = setup_colored_logging()

class MockLLMProvider(LLMProvider):
    """Mock provider for testing the abstraction layer"""
    
    def __init__(self, name: str, should_fail: bool = False):
        self.name = name
        self.should_fail = should_fail
        self.call_count = 0
        
    async def summarize(self, text: str, quality: SummaryQuality = SummaryQuality.STANDARD, max_retries: int = 3) -> str:
        self.call_count += 1
        
        if self.should_fail:
            raise LLMError(f"Mock provider {self.name} is configured to fail")
        
        # Mock summary based on quality
        quality_lengths = {
            SummaryQuality.CONCISE: "This is a very short summary.",
            SummaryQuality.STANDARD: "This is a standard length summary that covers the main points of the text.",
            SummaryQuality.DETAILED: "This is a detailed summary that provides comprehensive coverage of all key points and important details from the original text."
        }
        
        return quality_lengths[quality]
    
    def get_provider_name(self) -> str:
        return self.name
    
    async def is_available(self) -> bool:
        return True
    
    def get_usage_metrics(self) -> dict:
        return {"call_count": self.call_count}

async def test_provider_abstraction():
    """Test the LLM provider abstraction"""
    print("Testing LLM Provider Abstraction")
    print("=" * 40)
    
    mock_provider = MockLLMProvider("test_provider")
    
    # Test different quality levels
    test_text = "This is a long article about artificial intelligence and machine learning. It covers various topics including neural networks, deep learning, and natural language processing."
    
    for quality in SummaryQuality:
        print(f"\nTesting {quality.value} summary:")
        summary = await mock_provider.summarize(test_text, quality)
        print(f"   Provider: {mock_provider.get_provider_name()}")
        print(f"   Summary: {summary}")
        print(f"   Length: {len(summary)} characters")
    
    # Test provider metrics
    metrics = mock_provider.get_usage_metrics()
    print(f"\n Provider metrics: {metrics}")
    
    return mock_provider

async def test_provider_manager():
    """Test the provider manager with fallback logic"""
    print(f"\n Testing Provider Manager with Fallback")
    print("=" * 50)
    
    # Create multiple mock providers
    primary_provider = MockLLMProvider("primary")
    backup_provider = MockLLMProvider("backup")
    failing_provider = MockLLMProvider("failing", should_fail=True)
    
    # Register providers
    provider_manager.register_provider(primary_provider)
    provider_manager.register_provider(backup_provider)
    provider_manager.register_provider(failing_provider)
    
    # Test successful summarization
    test_text = "Artificial intelligence is transforming various industries."
    
    print(f"\nTesting successful summarization:")
    summary = await provider_manager.summarize_with_fallback(test_text)
    print(f"   Result: {summary}")
    print(f"   Available providers: {provider_manager.get_available_providers()}")
    
    # Test metrics
    metrics = provider_manager.get_provider_metrics()
    print(f"\n Provider metrics: {metrics}")
    
    overall_metrics = provider_manager.get_overall_metrics()
    print(f" Overall metrics: {overall_metrics}")
    
    # Test with preferred provider
    print(f"\n Testing preferred provider:")
    summary = await provider_manager.summarize_with_fallback(
        test_text, 
        preferred_provider="primary"
    )
    print(f"   Result: {summary}")

async def test_error_handling():
    """Test error handling and retry logic"""
    print(f"\n Testing Error Handling")
    print("=" * 30)
    
    # Test with only failing providers
    failing_manager = provider_manager.__class__()
    failing_provider = MockLLMProvider("always_fails", should_fail=True)
    failing_manager.register_provider(failing_provider)
    
    try:
        await failing_manager.summarize_with_fallback("test text")
        print("❌ Expected error was not raised")
    except LLMError as e:
        print(f"Error handling working: {e}")

async def main():
    """Run all abstraction layer tests"""
    print("LLM Provider Abstraction Layer Tests")
    print("This tests the foundation for all AI summarization features.\n")
    
    try:
        # Test basic provider abstraction
        await test_provider_abstraction()
        
        # Test provider manager
        await test_provider_manager()
        
        # Test error handling
        await test_error_handling()
        
        print(f"\n LLM Provider Abstraction layer is working correctly!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())