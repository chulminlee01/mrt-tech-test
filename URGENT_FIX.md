# URGENT: Update Railway Environment Variable

## The Problem

You're getting this error:
```
LLM Provider NOT provided. You passed model=minimaxai/minimax-m2
```

**Cause:** Railway still has the OLD environment variable set.

---

## SOLUTION: Update Railway Variable NOW

### Step-by-Step:

1. **Go to Railway:** https://railway.app/dashboard

2. **Find your service:** `mrt-tech-test-production`

3. **Click "Variables" tab**

4. **Find `DEFAULT_MODEL` variable**

5. **Click to edit it**

6. **Change the value:**

**From:**
```
minimaxai/minimax-m2
```

**To:**
```
deepseek-ai/deepseek-v3.1-terminus
```

7. **Click "Update"** or "Save"

8. **Railway will auto-redeploy** (takes 2-3 minutes)

---

## Why DeepSeek v3.1 Terminus?

- ✅ **Thinking Mode Enabled**: Provides step-by-step reasoning
- ✅ **High Quality Output**: Better analysis and decision making  
- ✅ **Widely Available**: Should work on most NVIDIA accounts
- ✅ **Great for Tech Assignments**: Excels at technical content

---

## Alternative Models (if DeepSeek doesn't work)

If you still get errors, try one of these models instead:

```
meta/llama-3.1-8b-instruct
google/gemma-2-9b-it
mistralai/mistral-7b-instruct-v0.3
meta/llama-3.1-70b-instruct
```

**To check which models you have access to:**
1. Visit: https://build.nvidia.com/
2. Log in with your account
3. Browse available models
4. Use the exact model name shown there

---

## After Updating:

1. Wait 2-3 minutes for redeploy
2. Test: `https://mrt-tech-test-production.up.railway.app/api/test-llm`
3. Should see: `"success": true`
4. Try generating a tech test!

---

## CRITICAL NOTE:

The code default is already changed to `meta/llama-3.1-8b-instruct`, 
but Railway's environment variable OVERRIDES the code default.

You MUST update the variable in Railway for the fix to take effect!

