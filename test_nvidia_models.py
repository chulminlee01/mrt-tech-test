#!/usr/bin/env python3
"""Test which NVIDIA models are accessible on your account."""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("NVIDIA_API_KEY")
if not api_key:
    print("❌ NVIDIA_API_KEY not found in .env")
    exit(1)

print(f"Testing NVIDIA API (key: {api_key[:10]}...{api_key[-4:]})")
print(f"Base URL: https://integrate.api.nvidia.com/v1")
print("=" * 70)
print()

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

models_to_test = [
    "meta/llama-3.1-8b-instruct",
    "moonshotai/kimi-k2-instruct-0905",
    "google/gemma-2-9b-it",
    "mistralai/mistral-7b-instruct-v0.3",
    "microsoft/phi-3-mini-128k-instruct"
]

working_models = []

for model in models_to_test:
    try:
        print(f"Testing: {model}")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=20,
            temperature=0.3
        )
        result = response.choices[0].message.content
        print(f"  ✅ SUCCESS: {result[:50]}")
        working_models.append(model)
    except Exception as e:
        error_msg = str(e)[:100]
        print(f"  ❌ FAILED: {error_msg}")
    print()

print("=" * 70)
if working_models:
    print(f"✅ Found {len(working_models)} working model(s):")
    for m in working_models:
        print(f"   - {m}")
    print()
    print(f"Recommended: Use DEFAULT_MODEL={working_models[0]}")
else:
    print("❌ No working models found!")
    print("   Check your NVIDIA API key and account access.")
    print("   Visit: https://build.nvidia.com/ to verify models")

