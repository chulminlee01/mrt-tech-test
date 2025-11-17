#!/usr/bin/env python3
"""
Verify that the LLM setup is working correctly.
Run this to test your API keys before deploying.
"""

import os
import sys
from dotenv import load_dotenv

def main():
    print("=" * 70)
    print("🔍 Verifying MRT Tech Test Generator Setup")
    print("=" * 70)
    print()
    
    # Load environment variables
    load_dotenv()
    
    # Check for LLM API keys
    nvidia_key = os.getenv("NVIDIA_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    print("📋 Checking LLM API Keys:")
    print("-" * 70)
    
    has_llm = False
    
    if nvidia_key:
        print("✅ NVIDIA_API_KEY found (Primary)")
        has_llm = True
    else:
        print("❌ NVIDIA_API_KEY not set")
    
    if openai_key:
        print("✅ OPENAI_API_KEY found (Fallback)")
        has_llm = True
    else:
        print("⚪ OPENAI_API_KEY not set (optional)")
    
    if openrouter_key:
        print("✅ OPENROUTER_API_KEY found (Fallback)")
        has_llm = True
    else:
        print("⚪ OPENROUTER_API_KEY not set (optional)")
    
    print()
    
    if not has_llm:
        print("❌ ERROR: No LLM API key found!")
        print()
        print("Please set at least ONE of these in your .env file:")
        print("  - NVIDIA_API_KEY (recommended)")
        print("  - OPENAI_API_KEY")
        print("  - OPENROUTER_API_KEY")
        print()
        print("Get API keys:")
        print("  - NVIDIA: https://build.nvidia.com/")
        print("  - OpenAI: https://platform.openai.com/api-keys")
        print("  - OpenRouter: https://openrouter.ai/")
        print()
        return False
    
    # Test LLM client creation
    print("🧪 Testing LLM Client Creation:")
    print("-" * 70)
    
    try:
        from llm_client import create_llm_client
        
        llm = create_llm_client(temperature=0.7)
        print("✅ LLM client created successfully!")
        print()
        
    except Exception as e:
        print(f"❌ ERROR creating LLM client: {e}")
        print()
        return False
    
    # Check optional features
    print("📋 Checking Optional Features:")
    print("-" * 70)
    
    google_key = os.getenv("GOOGLE_API_KEY")
    google_cse = os.getenv("GOOGLE_CSE_ID")
    
    if google_key and google_cse:
        print("✅ Google Search API configured (Research agent will work)")
    else:
        print("⚪ Google Search API not configured (Research agent disabled)")
        if not google_key:
            print("   Missing: GOOGLE_API_KEY")
        if not google_cse:
            print("   Missing: GOOGLE_CSE_ID")
    
    print()
    print("=" * 70)
    print("✅ Setup verification complete!")
    print("=" * 70)
    print()
    print("🚀 You can now run the application:")
    print("   python app.py")
    print()
    print("   Or deploy to:")
    print("   - Render.com: https://render.com/")
    print("   - Railway: https://railway.app/")
    print()
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

