import asyncio
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.services.llm import HuggingFaceProvider, GroqProvider

async def compare_providers():
    """Compare performance between Hugging Face and Groq"""
    print("⚡ Provider Performance Comparison")
    print("=" * 45)
    
    test_text = """
    Blockchain technology is transforming how we think about digital trust 
    and transactions. Originally developed for cryptocurrencies like Bitcoin, 
    blockchain has found applications in supply chain management, digital 
    identity, and smart contracts. The decentralized nature of blockchain 
    provides transparency and security without relying on central authorities. 
    Major industries from finance to healthcare are exploring blockchain 
    solutions for various use cases.
    """
    
    providers = []
    
    # Initialize providers if available
    hf_provider = HuggingFaceProvider()
    if await hf_provider.is_available():
        providers.append(("Hugging Face", hf_provider))
    
    groq_provider = GroqProvider()
    if await groq_provider.is_available():
        providers.append(("Groq", groq_provider))
    
    if not providers:
        print("❌ No providers available for comparison")
        return
    
    print(f"Testing with {len(providers)} provider(s)\n")
    
    for provider_name, provider in providers:
        print(f"🔍 Testing {provider_name}:")
        
        # Warm-up call
        try:
            await provider.summarize("Warm up", max_retries=1)
        except:
            pass
        
        # Performance test
        start_time = time.time()
        try:
            summary = await provider.summarize(test_text)
            response_time = time.time() - start_time
            
            print(f"   ✅ {response_time:.2f}s - {summary}")
            
        except Exception as e:
            response_time = time.time() - start_time
            print(f"   ❌ {response_time:.2f}s - Failed: {e}")
    
    print(f"\n🎯 Summary:")
    print("Hugging Face: Good for development, free, slower")
    print("Groq: Excellent for production, very fast, generous free tier")

if __name__ == "__main__":
    asyncio.run(compare_providers())