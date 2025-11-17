"""
LLM Client with multi-provider fallback support.

Tries providers in order:
1. NVIDIA (DeepSeek v3.1 with thinking)
2. OpenAI
3. OpenRouter
"""

import os
from typing import Dict, Optional, Any
from langchain_openai import ChatOpenAI


class LLMClientError(Exception):
    """Custom exception for LLM client errors."""
    pass


def create_nvidia_llm_direct(temperature: float = 0.7) -> ChatOpenAI:
    """
    Create NVIDIA LLM directly without going through any wrapper.
    This bypasses LiteLLM completely to avoid provider parsing errors.
    
    Uses: deepseek-ai/deepseek-v3.1-terminus with thinking enabled
    """
    nvidia_key = os.getenv("NVIDIA_API_KEY")
    if not nvidia_key:
        raise LLMClientError("NVIDIA_API_KEY not found")
    
    # Force DeepSeek model regardless of DEFAULT_MODEL setting
    nvidia_model = "deepseek-ai/deepseek-v3.1-terminus"
    nvidia_base = "https://integrate.api.nvidia.com/v1"
    
    print(f"🚀 Creating NVIDIA LLM directly (bypassing LiteLLM)")
    print(f"   Model: {nvidia_model}")
    print(f"   Base URL: {nvidia_base}")
    print(f"   Thinking: ENABLED ✓")
    
    # Set environment for OpenAI client library
    os.environ["OPENAI_API_KEY"] = nvidia_key
    os.environ["OPENAI_API_BASE"] = nvidia_base
    
    # Create with thinking enabled (extra_body must be passed directly, not in model_kwargs)
    return ChatOpenAI(
        model=nvidia_model,
        temperature=temperature,
        extra_body={
            "chat_template_kwargs": {"thinking": True}
        }
    )


def _get_nvidia_headers() -> Dict[str, str]:
    """Get NVIDIA API headers."""
    return {}


def _get_openrouter_headers() -> Dict[str, str]:
    """Get OpenRouter attribution headers."""
    headers: Dict[str, str] = {}
    site = os.getenv("OPENROUTER_SITE_URL")
    app = os.getenv("OPENROUTER_APP_NAME")
    if site:
        headers["HTTP-Referer"] = site
    if app:
        headers["X-Title"] = app
    return headers


def create_llm_client(
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    **kwargs: Any
) -> ChatOpenAI:
    """
    Create LLM client with automatic fallback.
    
    Fallback order:
    1. NVIDIA minimax-m2 (if NVIDIA_API_KEY is set)
    2. OpenAI GPT (if OPENAI_API_KEY is set)
    3. DeepSeek v3.1-terminus via OpenRouter (with thinking)
    4. OpenRouter fallback model
    
    Args:
        model: Optional model override
        temperature: Optional temperature override
        **kwargs: Additional ChatOpenAI parameters
        
    Returns:
        ChatOpenAI: Configured LLM client
        
    Raises:
        LLMClientError: If no valid API keys are found
    """
    temp_val = temperature if temperature is not None else float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    # If user explicitly provides a model, use it with best-guess provider
    if model:
        return _create_with_explicit_model(model, temp_val, **kwargs)
    
    # Try NVIDIA first (primary)
    nvidia_key = os.getenv("NVIDIA_API_KEY")
    if nvidia_key:
        try:
            return _create_nvidia_client(temp_val, **kwargs)
        except Exception as e:
            print(f"⚠️  NVIDIA client failed: {e}")
            print(f"   Error type: {type(e).__name__}")
            
            # If NVIDIA model not accessible, try known good models
            fallback_models = [
                "deepseek-ai/deepseek-v3.1-terminus",
                "meta/llama-3.1-8b-instruct",
                "google/gemma-2-9b-it",
                "mistralai/mistral-7b-instruct-v0.3"
            ]
            
            current_model = os.getenv("DEFAULT_MODEL", "")
            for fallback_model in fallback_models:
                if fallback_model != current_model:
                    print(f"   Trying fallback NVIDIA model: {fallback_model}")
                    try:
                        os.environ["DEFAULT_MODEL"] = fallback_model
                        return _create_nvidia_client(temp_val, **kwargs)
                    except Exception as fallback_err:
                        print(f"   Fallback {fallback_model} also failed: {fallback_err}")
                        continue
            
            print("   All NVIDIA models failed, falling back to OpenAI...")
    
    # Try OpenAI (fallback #1)
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            return _create_openai_client(temp_val, **kwargs)
        except Exception as e:
            print(f"⚠️  OpenAI client failed: {e}")
            print("   Falling back to OpenRouter...")
    
    # Try DeepSeek with thinking (fallback #2)
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_key:
        try:
            return _create_deepseek_client(temp_val, **kwargs)
        except Exception as e:
            print(f"⚠️  DeepSeek client failed: {e}")
            print("   Falling back to OpenRouter...")
        
        # Try OpenRouter fallback model (fallback #3)
        try:
            return _create_openrouter_fallback_client(temp_val, **kwargs)
        except Exception as e:
            print(f"⚠️  OpenRouter fallback failed: {e}")
    
    # No valid keys found
    raise LLMClientError(
        "No valid API keys found. Please set one of: OPENAI_API_KEY, NVIDIA_API_KEY, or OPENROUTER_API_KEY"
    )


def _create_nvidia_client(temperature: float, **kwargs: Any) -> ChatOpenAI:
    """Create NVIDIA client with DeepSeek v3.1 terminus (thinking enabled)."""
    # NVIDIA uses OpenAI-compatible API
    nvidia_model = os.getenv("DEFAULT_MODEL", "deepseek-ai/deepseek-v3.1-terminus")
    base_url = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
    api_key = os.getenv("NVIDIA_API_KEY")
    
    if not api_key:
        raise LLMClientError("NVIDIA_API_KEY not found")
    
    print(f"✨ Using NVIDIA API")
    print(f"   Model: {nvidia_model}")
    print(f"   Base URL: {base_url}")
    print(f"   API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 10 else 'xxx'}")
    
    # Enable thinking for DeepSeek models
    model_kwargs = kwargs.pop("model_kwargs", {})
    if "deepseek" in nvidia_model.lower():
        model_kwargs["extra_body"] = {
            "chat_template_kwargs": {"thinking": True}
        }
        print(f"   DeepSeek Thinking: ENABLED ✓")
    
    # Create ChatOpenAI client directly with base_url
    # The OpenAI client will make requests to NVIDIA's OpenAI-compatible endpoint
    return ChatOpenAI(
        model=nvidia_model,
        temperature=temperature,
        base_url=base_url,
        api_key=api_key,
        model_kwargs=model_kwargs,
        **kwargs
    )


def _create_openai_client(temperature: float, **kwargs: Any) -> ChatOpenAI:
    """Create standard OpenAI client."""
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise LLMClientError("OPENAI_API_KEY not found")
    
    print(f"✨ Using OpenAI {model}")
    
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=api_key,
        **kwargs
    )


def _create_deepseek_client(temperature: float, **kwargs: Any) -> ChatOpenAI:
    """Create DeepSeek client with thinking enabled."""
    model = os.getenv("FALLBACK_MODEL", "deepseek-ai/deepseek-v3.1-terminus")
    base_url = os.getenv("FALLBACK_BASE_URL", "https://openrouter.ai/api/v1")
    api_key = os.getenv("OPENROUTER_API_KEY")
    thinking_enabled = os.getenv("DEEPSEEK_THINKING", "True").lower() == "true"
    
    if not api_key:
        raise LLMClientError("OPENROUTER_API_KEY not found")
    
    print(f"✨ Using DeepSeek {model} (thinking={'on' if thinking_enabled else 'off'})")
    
    # Build model_kwargs with thinking option
    model_kwargs = kwargs.pop("model_kwargs", {})
    if thinking_enabled:
        model_kwargs["extra_body"] = {
            "chat_template_kwargs": {"thinking": True}
        }
    
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        base_url=base_url,
        api_key=api_key,
        default_headers=_get_openrouter_headers(),
        model_kwargs=model_kwargs,
        **kwargs
    )


def _create_openrouter_fallback_client(temperature: float, **kwargs: Any) -> ChatOpenAI:
    """Create OpenRouter fallback client."""
    model = os.getenv("OPENROUTER_FALLBACK_MODEL", "z-ai/glm-4.5-air:free")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        raise LLMClientError("OPENROUTER_API_KEY not found")
    
    print(f"✨ Using OpenRouter {model}")
    
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        base_url=base_url,
        api_key=api_key,
        default_headers=_get_openrouter_headers(),
        **kwargs
    )


def _create_with_explicit_model(model: str, temperature: float, **kwargs: Any) -> ChatOpenAI:
    """Create client when user explicitly provides a model name."""
    print(f"✨ Using explicit model: {model}")
    
    # Detect provider from model name
    if "minimax" in model.lower():
        # Use NVIDIA
        base_url = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
        api_key = os.getenv("NVIDIA_API_KEY")
        headers = _get_nvidia_headers()
    elif "gpt" in model.lower() or "o1" in model.lower():
        # Use OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise LLMClientError(f"OPENAI_API_KEY required for model: {model}")
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key,
            **kwargs
        )
    elif "deepseek" in model.lower():
        # Use OpenRouter with thinking
        base_url = os.getenv("FALLBACK_BASE_URL", "https://openrouter.ai/api/v1")
        api_key = os.getenv("OPENROUTER_API_KEY")
        headers = _get_openrouter_headers()
        
        # Add thinking if it's DeepSeek
        thinking_enabled = os.getenv("DEEPSEEK_THINKING", "True").lower() == "true"
        if thinking_enabled:
            model_kwargs = kwargs.pop("model_kwargs", {})
            model_kwargs["extra_body"] = {
                "chat_template_kwargs": {"thinking": True}
            }
            kwargs["model_kwargs"] = model_kwargs
    else:
        # Use OpenRouter for everything else
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        api_key = os.getenv("OPENROUTER_API_KEY")
        headers = _get_openrouter_headers()
    
    if not api_key:
        raise LLMClientError(f"No API key found for model: {model}")
    
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        base_url=base_url,
        api_key=api_key,
        default_headers=headers if headers else None,
        **kwargs
    )


# Backward compatibility function
def create_llm(
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    **kwargs: Any
) -> ChatOpenAI:
    """Alias for create_llm_client for backward compatibility."""
    return create_llm_client(model, temperature, **kwargs)

