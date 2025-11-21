# LiteLLM Provider Error - Complete Fix Guide

## The Error

```
litellm.BadRequestError: LLM Provider NOT provided.
You passed model=deepseek-ai/deepseek-v3.1-terminus
```

---

## Why This Happens

CrewAI uses LiteLLM internally to route model calls. LiteLLM tries to parse the model name to determine the provider (e.g., `openai/gpt-4`, `anthropic/claude`, etc.).

When you pass `deepseek-ai/deepseek-v3.1-terminus`, LiteLLM doesn't recognize `deepseek-ai` as a known provider.

---

## The Solution: Use `openai/` Prefix

The code now uses: `openai/deepseek-ai/deepseek-v3.1-terminus`

This tells LiteLLM:
1. Use the **OpenAI provider/client**
2. Read `OPENAI_API_BASE` from environment (points to NVIDIA)
3. Send the model name to that endpoint
4. NVIDIA API receives and processes the request

---

## Current Code Configuration

The latest code (version 2.1.0-deepseek-direct):

```python
# Sets these environment variables:
os.environ["OPENAI_API_KEY"] = nvidia_key
os.environ["OPENAI_API_BASE"] = "https://integrate.api.nvidia.com/v1"

# Creates ChatOpenAI with:
ChatOpenAI(
    model="openai/deepseek-ai/deepseek-v3.1-terminus",
    temperature=0.7,
    extra_body={"chat_template_kwargs": {"thinking": True}}
)
```

---

## Verify Railway Has Latest Code

### Check deployed version:

```bash
curl https://mrt-tech-test-production.up.railway.app/api/version
```

**Should show:**
```json
{
  "version": "2.1.0-deepseek-direct"
}
```

**If it shows** `2.0.0-nvidia-support`, Railway hasn't deployed the latest code yet.

---

## Force Fresh Railway Deployment

If Railway is stuck on old code:

### Option 1: Manual Redeploy

1. Go to Railway dashboard
2. Click your service
3. Click "Deployments" tab
4. Click "..." menu on latest deployment
5. Click "Redeploy"

### Option 2: Clear Build Cache

1. Go to Railway dashboard
2. Click your service
3. Click "Settings"
4. Scroll to "Danger Zone"
5. Click "Reset Build Cache"
6. Go back to "Deployments"
7. Click "Deploy"

### Option 3: Delete and Recreate

1. Delete the service
2. Create new service from GitHub
3. Connect to: `chulminlee01/mrt-tech-test`
4. Add environment variable: `NVIDIA_API_KEY=nvapi-xxx`
5. Deploy

---

## Alternative: Use Just OpenAI Model Name

If the `openai/` prefix still doesn't work, edit Railway environment variables:

**Instead of setting DEFAULT_MODEL, don't set it at all.**

The code will default to `deepseek-ai/deepseek-v3.1-terminus` with the `openai/` prefix automatically.

---

## Testing

After deployment:

1. **Check version:**
   ```
   /api/version
   ```
   Should show: `2.1.0-deepseek-direct`

2. **Test LLM:**
   ```
   /api/test-llm
   ```
   Should see model: `openai/deepseek-ai/deepseek-v3.1-terminus`

3. **Check logs:**
   Should see:
   ```
   🚀 Creating NVIDIA LLM directly
      Model: deepseek-ai/deepseek-v3.1-terminus
      LiteLLM model format: openai/deepseek-ai/deepseek-v3.1-terminus
      Thinking: ENABLED ✓
   ```

---

## If Still Failing

If you continue to get the LiteLLM error after all this:

1. **Check Railway logs** - Look for the exact error
2. **Verify code deployed** - Check /api/version shows 2.1.0
3. **Try different model** - Use meta/llama-3.1-8b-instruct (doesn't need openai/ prefix)
4. **Contact me with**:
   - Full error message
   - Railway logs
   - Response from /api/test-llm

---

## Summary

✅ Latest code uses `openai/` prefix for LiteLLM compatibility  
✅ DeepSeek thinking enabled
✅ NVIDIA API properly configured  
⏳ Wait for Railway to deploy latest code (2-3 minutes)

