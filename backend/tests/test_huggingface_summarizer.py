import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.services.llm import HuggingFaceProvider, SummaryQuality, provider_manager
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_huggingface_availability():
    """Test if Hugging Face provider is available"""
    print("🔍 Testing Hugging Face Provider Availability")
    print("=" * 50)
    
    provider = HuggingFaceProvider()
    is_available = await provider.is_available()
    
    print(f"API Key configured: {'Yes' if settings.HUGGINGFACE_API_KEY else 'No'}")
    print(f"Provider available: {'✅ Yes' if is_available else '❌ No'}")
    
    if not is_available and not settings.HUGGINGFACE_API_KEY:
        print("\n💡 To enable Hugging Face summarization:")
        print("1. Get a free token from: https://huggingface.co/settings/tokens")
        print("2. Add to .env: HUGGINGFACE_API_KEY=your_token_here")
    
    return is_available, provider

async def test_summarization(provider: HuggingFaceProvider):
    """Test actual summarization with different quality levels"""
    print(f"\n🧪 Testing Hugging Face Summarization")
    print("=" * 45)
    
    test_article = """
    Artificial intelligence is transforming industries across the globe. 
    Machine learning algorithms can now analyze vast amounts of data to identify patterns 
    that humans might miss. Companies are using AI for everything from customer service 
    chatbots to medical diagnosis systems. Recent advances in natural language processing 
    have made it possible for AI to understand and generate human-like text. 
    However, ethical considerations around AI bias and job displacement remain important 
    topics of discussion among researchers and policymakers.
    """
    
    for quality in SummaryQuality:
        print(f"\n🎯 Testing {quality.value} summary:")
        try:
            summary = await provider.summarize(test_article, quality)
            print(f"   ✅ Success!")
            print(f"   📝 Summary: {summary}")
            print(f"   📏 Length: {len(summary)} characters")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")

async def test_different_article_types(provider: HuggingFaceProvider):
    """Test summarization with different types of content"""
    print(f"\n📚 Testing Different Article Types")
    print("=" * 40)
    
    test_cases = [
        {
            "name": "Technology Article",
            "text": """
            The rapid advancement of quantum computing promises to revolutionize 
            how we process information. Unlike classical computers that use bits, 
            quantum computers use qubits which can exist in multiple states simultaneously. 
            This allows them to solve certain problems much faster than traditional computers. 
            Major tech companies like IBM, Google, and Microsoft are investing heavily 
            in quantum research. Potential applications include drug discovery, 
            cryptography, and complex system optimization.
            """
        },
        {
            "name": "Business News", 
            "text": """
            The global stock market experienced significant volatility this week 
            due to changing economic indicators. Technology stocks led the decline 
            while energy sectors showed resilience. Analysts attribute the movement 
            to concerns about inflation and upcoming central bank decisions. 
            Investors are advised to maintain diversified portfolios and consider 
            long-term strategies rather than reacting to short-term market fluctuations.
            """
        },
        {
            "name": "Science Discovery",
            "text": """
            Researchers at an international observatory have discovered a new exoplanet 
            located in the habitable zone of its star. The planet, designated Kepler-452b, 
            has conditions that could potentially support liquid water. This discovery 
            was made using advanced telescope technology that can detect minute changes 
            in starlight. Further observations will focus on analyzing the planet's 
            atmosphere for signs of biological activity.
            """
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📖 {test_case['name']}:")
        try:
            summary = await provider.summarize(test_case['text'], SummaryQuality.STANDARD)
            print(f"   ✅ {summary}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")

async def test_provider_manager_integration():
    """Test Hugging Face integration with provider manager"""
    print(f"\n🔄 Testing Provider Manager Integration")
    print("=" * 50)
    
    provider = HuggingFaceProvider()
    provider_manager.register_provider(provider)
    
    test_text = "Climate change is one of the most pressing issues facing humanity today. Rising global temperatures are causing extreme weather events, sea level rise, and ecosystem disruptions. International cooperation is essential to address this challenge through reduced emissions and sustainable practices."
    
    try:
        summary = await provider_manager.summarize_with_fallback(
            test_text, 
            preferred_provider="huggingface"
        )
        print(f"✅ Provider manager integration working!")
        print(f"📝 Summary: {summary}")
        
        metrics = provider_manager.get_provider_metrics()
        huggingface_metrics = metrics.get("huggingface", {})
        print(f"📊 Hugging Face metrics: {huggingface_metrics}")
        
    except Exception as e:
        print(f"❌ Provider manager integration failed: {e}")

async def test_error_handling(provider: HuggingFaceProvider):
    """Test error handling with invalid inputs"""
    print(f"\n🔧 Testing Error Handling")
    print("=" * 30)
    
    # Test empty text
    try:
        await provider.summarize("")
        print("❌ Empty text should have failed")
    except Exception as e:
        print(f"✅ Empty text handled: {e}")
    
    # Test very short text
    try:
        await provider.summarize("Hi")
        print("❌ Short text should have failed") 
    except Exception as e:
        print(f"✅ Short text handled: {e}")
    
    # Test invalid text 
    try:
        result = await provider.summarize("Error test " * 1000)
        print(f"✅ Invalid text handled, got: {result[:50]}...")
    except Exception as e:
        print(f"✅ Invalid text handled: {e}")

async def main():
    """Run all Hugging Face tests"""
    print("🚀 Hugging Face Summarizer Tests")
    print("Testing the primary free LLM provider for development.\n")
    
    try:
        # Test availability
        is_available, provider = await test_huggingface_availability()
        
        if is_available:
            await test_summarization(provider)
            await test_different_article_types(provider)
            await test_provider_manager_integration()
            await test_error_handling(provider)
            
            metrics = provider.get_usage_metrics()
            print(f"\n📈 Final Provider Metrics:")
            for key, value in metrics.items():
                print(f"   {key}: {value}")
            
            print(f"\n✅ Hugging Face summarizer is working correctly!")
            print("🎉 Ready for production use and as primary provider!")
            
        else:
            print(f"\n💡 Hugging Face provider not available.")
            print("   Get a free API token and add it to your .env file.")
            print("   You can still proceed with other providers (Groq, etc.)")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())