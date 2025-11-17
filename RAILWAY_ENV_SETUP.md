# Railway Environment Variables Setup

## Required Environment Variables for NVIDIA API

Go to your Railway dashboard → Your service → Variables tab

Add these **3 environment variables**:

### 1. NVIDIA_API_KEY (Required)
```
NVIDIA_API_KEY=nvapi-your-actual-key-here
```
Get your key from: https://build.nvidia.com/

### 2. NVIDIA_BASE_URL (Required)
```
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
```
This is NVIDIA's OpenAI-compatible endpoint.

### 3. DEFAULT_MODEL (Required)
```
DEFAULT_MODEL=meta/llama-3.1-8b-instruct
```

**Available NVIDIA Models:**
- `meta/llama-3.1-8b-instruct` (Recommended - Fast, reliable)
- `meta/llama-3.1-70b-instruct` (More powerful)
- `google/gemma-2-9b-it` (Alternative)
- `mistralai/mistral-7b-instruct-v0.3` (Alternative)

**Note:** Check your NVIDIA account at https://build.nvidia.com/ to see which models you have access to.
Some models like `minimaxai/minimax-m2` may require special access or may not be available in all regions.

---

## How to Add Variables in Railway

1. Go to: https://railway.app/
2. Find your project: `mrt-tech-test`
3. Click on your service
4. Click the **"Variables"** tab
5. Click **"New Variable"**
6. Add each variable:
   - **Name**: `NVIDIA_API_KEY`
   - **Value**: `nvapi-...` (your key)
7. Click **"Add"**
8. Repeat for `NVIDIA_BASE_URL` and `DEFAULT_MODEL`

---

## Verify Setup

After adding variables and redeploying:

1. Check logs for:
```
✨ Using NVIDIA minimaxai/minimax-m2 via OpenAI-compatible API
   Endpoint: https://integrate.api.nvidia.com/v1
🔧 Configured NVIDIA as OpenAI-compatible endpoint for CrewAI
```

2. Visit `/health` endpoint:
```
https://your-app.up.railway.app/health
```

Should show:
```json
{
  "status": "healthy",
  "version": "2.0.0-nvidia-support"
}
```

---

## Troubleshooting

### Error: "LLM Provider NOT provided"
- **Cause**: Environment variables not set
- **Fix**: Make sure all 3 variables are set in Railway

### Error: "NVIDIA_API_KEY not found"
- **Cause**: NVIDIA_API_KEY variable missing
- **Fix**: Add NVIDIA_API_KEY in Railway Variables tab

### Error: "API key is invalid"
- **Cause**: Invalid or expired NVIDIA API key
- **Fix**: Generate a new key at https://build.nvidia.com/

---

## Optional Variables

These are optional (for Google Search integration):

```
GOOGLE_API_KEY=your-google-api-key
GOOGLE_CSE_ID=your-google-cse-id
```

If not set, the research agent will skip Google searches (but still work).

---

## After Setting Variables

Railway will **automatically redeploy** when you save variables.

Wait 2-3 minutes, then test your app!

