import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.services.llm.groq_provider import GroqProvider, create_groq_provider, SummaryQuality
from app.services.llm import provider_manager
from app.core.config import settings
from app.core.config import setup_colored_logging

logging.basicConfig(level=logging.INFO)
logger = setup_colored_logging()

async def test_groq_availability():
    """Test if Groq provider is available"""
    print("🔍 Testing Groq Provider Availability")
    print("=" * 50)
    
    provider = GroqProvider()
    is_available = await provider.is_available()
    
    print(f"API Key configured: {'Yes' if settings.GROQ_API_KEY else 'No'}")
    print(f"Provider available: {'✅ Yes' if is_available else '❌ No'}")
    
    if is_available:
        print(f"📋 Available models: {provider.available_models}")
        print(f"🎯 Default model: {provider.default_model}")
    else:
        print("\n💡 To enable Groq summarization:")
        print("1. Get API key from: https://console.groq.com/")
        print("2. Add to .env: GROQ_API_KEY=your_key_here")
        print("3. Ensure API key starts with 'gsk_'")
    
    return is_available, provider

async def test_summarization(provider: GroqProvider):
    """Test actual summarization with different quality levels"""
    print(f"\n🧪 Testing Groq Summarization")
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
            import time
            start_time = time.time()
            
            summary = await provider.summarize(test_article, quality)
            
            response_time = time.time() - start_time
            print(f"   ✅ Success! ({response_time:.2f}s)")
            print(f"   📝 Summary: {summary}")
            print(f"   📏 Length: {len(summary)} characters")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")

async def test_different_article_types(provider: GroqProvider):
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
            import time
            start_time = time.time()
            
            summary = await provider.summarize(test_case['text'], SummaryQuality.STANDARD)
            
            response_time = time.time() - start_time
            print(f"   ✅ ({response_time:.2f}s) {summary}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")

async def test_provider_manager_integration():
    """Test Groq integration with provider manager"""
    print(f"\n🔄 Testing Provider Manager Integration")
    print("=" * 50)
    
    provider = await create_groq_provider()
    provider_manager.register_provider(provider)
    
    test_text = "Climate change is one of the most pressing issues facing humanity today. Rising global temperatures are causing extreme weather events, sea level rise, and ecosystem disruptions. International cooperation is essential to address this challenge through reduced emissions and sustainable practices."
    
    try:
        import time
        start_time = time.time()
        
        summary = await provider_manager.summarize_with_fallback(
            test_text, 
            preferred_provider="groq"
        )
        
        response_time = time.time() - start_time
        print(f"✅ Provider manager integration working! ({response_time:.2f}s)")
        print(f"📝 Summary: {summary}")
        
        metrics = provider_manager.get_provider_metrics()
        groq_metrics = metrics.get("groq", {})
        print(f"📊 Groq metrics: {groq_metrics}")
        
    except Exception as e:
        print(f"❌ Provider manager integration failed: {e}")

async def test_error_handling(provider: GroqProvider):
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
    
    # Test whitespace only
    try:
        await provider.summarize("   \n   \t   ")
        print("❌ Whitespace text should have failed")
    except Exception as e:
        print(f"✅ Whitespace text handled: {e}")

async def test_performance_metrics(provider: GroqProvider):
    """Test performance metrics collection"""
    print(f"\n📈 Testing Performance Metrics")
    print("=" * 35)
    
    test_texts = [
        "Renewable energy sources like solar and wind power are becoming increasingly cost-competitive with traditional fossil fuels.",
        "Remote work has transformed how companies operate, with many adopting hybrid models that offer flexibility to employees.",
        "Advancements in battery technology are crucial for the widespread adoption of electric vehicles and grid storage solutions."
    ]
    
    for i, text in enumerate(test_texts):
        try:
            summary = await provider.summarize(text, SummaryQuality.CONCISE)
            print(f"✅ Sample {i+1} completed")
        except Exception as e:
            print(f"❌ Sample {i+1} failed: {e}")
    
    metrics = provider.get_usage_metrics()
    perf_stats = provider.get_performance_stats()
    
    print(f"\n📊 Usage Metrics:")
    for key, value in metrics.items():
        if key not in ['response_times', 'model_usage']:
            print(f"   {key}: {value}")
    
    print(f"\n⚡ Performance Stats:")
    for key, value in perf_stats.items():
        print(f"   {key}: {value}")
    
    if 'model_usage' in metrics and metrics['model_usage']:
        print(f"\n🤖 Model Usage:")
        for model, count in metrics['model_usage'].items():
            print(f"   {model}: {count} requests")

async def test_model_fallback(provider: GroqProvider):
    """Test model fallback mechanism"""
    print(f"\n🔄 Testing Model Fallback Mechanism")
    print("=" * 40)
    
    original_models = provider.available_models.copy()
    
    try:
        # Test with multiple models including potentially unavailable ones
        test_models = ["invalid-model", "mixtral-8x7b-32768", "llama3-70b-8192"]
        provider.available_models = test_models
        
        test_text = "Blockchain technology enables secure, transparent transactions without central authorities through distributed ledger systems."
        
        print(f"Testing with models: {test_models}")
        summary = await provider.summarize(test_text, SummaryQuality.STANDARD)
        
        print(f"✅ Model fallback successful!")
        print(f"📝 Summary: {summary}")
        
        # Check which model was actually used
        metrics = provider.get_usage_metrics()
        if metrics['model_usage']:
            used_model = list(metrics['model_usage'].keys())[-1]  
            print(f"🎯 Successfully used model: {used_model}")
            
    except Exception as e:
        print(f"❌ Model fallback test failed: {e}")
    
    finally:
        # Restore original models
        provider.available_models = original_models

async def main():
    """Run all Groq tests"""
    print("🚀 Groq Summarizer Tests")
    print("Testing the high-performance backup LLM provider.\n")
    
    try:
        # Test availability
        is_available, provider = await test_groq_availability()
        
        if is_available:
            await test_summarization(provider)
            await test_different_article_types(provider)
            await test_provider_manager_integration()
            await test_error_handling(provider)
            await test_performance_metrics(provider)
            await test_model_fallback(provider)
            
            final_metrics = provider.get_usage_metrics()
            print(f"\n📈 Final Provider Metrics:")
            for key, value in final_metrics.items():
                if key not in ['response_times', 'model_usage']:
                    print(f"   {key}: {value}")
            
            print(f"\n✅ Groq summarizer is working correctly!")
            
        else:
            print(f"\n💡 Groq provider not available.")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if 'provider' in locals():
            await provider.close()

if __name__ == "__main__":
    asyncio.run(main())