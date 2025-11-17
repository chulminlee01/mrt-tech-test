#!/usr/bin/env python3
"""
Check your Railway deployment configuration remotely.
This helps verify environment variables are set correctly.
"""

import requests
import sys

def check_deployment(base_url):
    """Check deployment health and configuration."""
    
    print("=" * 70)
    print("🔍 Checking Railway Deployment Configuration")
    print("=" * 70)
    print(f"Target: {base_url}")
    print()
    
    # Check health
    print("1️⃣ Checking Health...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ App is running")
            print(f"   Version: {data.get('version')}")
            print(f"   Agents: {data.get('agents_count')}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot reach app: {e}")
        return False
    
    print()
    
    # Check LLM configuration
    print("2️⃣ Testing LLM Configuration...")
    try:
        response = requests.get(f"{base_url}/api/test-llm", timeout=30)
        data = response.json()
        
        if data.get("success"):
            print("   ✅ LLM is working!")
            config = data.get("config", {})
            print(f"   NVIDIA configured: {config.get('nvidia_configured')}")
            print(f"   OpenAI configured: {config.get('openai_configured')}")
            print(f"   Default model: {config.get('default_model')}")
            print(f"   OpenAI base: {config.get('openai_api_base')}")
            print(f"   Test response: {data.get('test_response', '')[:50]}...")
        else:
            print("   ❌ LLM test failed")
            print(f"   Error: {data.get('error')}")
            print(f"   Message: {data.get('message')}")
            
            config = data.get("config", {})
            print()
            print("   Current Configuration:")
            print(f"     NVIDIA_API_KEY: {'✅ Set' if config.get('nvidia_configured') else '❌ Missing'}")
            print(f"     DEFAULT_MODEL: {config.get('default_model', 'Not set')}")
            print(f"     OPENAI_API_BASE: {config.get('openai_api_base', 'Not set')}")
            
            if config.get('default_model') == 'minimaxai/minimax-m2':
                print()
                print("   ⚠️  WARNING: You're still using minimaxai/minimax-m2")
                print("   👉 Update Railway variable to: deepseek-ai/deepseek-v3.1-terminus")
                print("   Or delete the DEFAULT_MODEL variable to use code default")
            
            return False
    except Exception as e:
        print(f"   ❌ Cannot test LLM: {e}")
        return False
    
    print()
    print("=" * 70)
    print("✅ Deployment Check Complete!")
    print("=" * 70)
    return True


if __name__ == "__main__":
    # Default to Railway URL
    url = "https://mrt-tech-test-production.up.railway.app"
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    success = check_deployment(url)
    
    if success:
        print()
        print("🎉 Your deployment is working correctly!")
        print("   You can now generate tech tests.")
    else:
        print()
        print("❌ Deployment has issues. See errors above.")
        print()
        print("Common fixes:")
        print("  1. Update DEFAULT_MODEL in Railway to: deepseek-ai/deepseek-v3.1-terminus")
        print("  2. Ensure NVIDIA_API_KEY is set")
        print("  3. Wait 2-3 minutes after changing variables for redeploy")
        print("  4. Check Railway logs for detailed errors")
    
    sys.exit(0 if success else 1)

