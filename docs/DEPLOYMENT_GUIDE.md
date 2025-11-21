# Deployment Guide - NVIDIA API

This guide shows how to deploy the Tech Test Generator using **NVIDIA API** (recommended).

## 🚀 Quick Deploy with NVIDIA

### Prerequisites

Get your NVIDIA API key:
1. Visit: https://build.nvidia.com/
2. Sign up for a free account
3. Navigate to API Keys section
4. Generate a new API key
5. Copy your key (starts with `nvapi-...`)

---

## Option 1: Deploy to Render.com (Recommended)

1. **Go to Render.com**
   - Visit: https://render.com/
   - Sign up/Login with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Select repository: `chulminlee01/mrt-tech-test`
   - Render will auto-detect `render.yaml`

3. **Set Environment Variable**
   - Add only this one variable:
   ```
   NVIDIA_API_KEY=nvapi-your-key-here
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait 2-3 minutes for deployment
   - Done! ✅

---

## Option 2: Deploy to Railway

1. **Go to Railway**
   - Visit: https://railway.app/
   - Login with GitHub

2. **Deploy from GitHub**
   - Click "New Project" → "Deploy from GitHub repo"
   - Select: `chulminlee01/mrt-tech-test`

3. **Add Environment Variables**
   - Go to "Variables" tab
   - Add:
   ```
   NVIDIA_API_KEY=nvapi-your-key-here
   DEFAULT_MODEL=minimaxai/minimax-m2
   ```

4. **Deploy**
   - Railway will automatically deploy
   - Wait 2-3 minutes
   - Done! ✅

---

## Environment Variables Reference

### Required (Choose One)

```bash
# Primary: NVIDIA (Recommended)
NVIDIA_API_KEY=nvapi-your-key-here
DEFAULT_MODEL=minimaxai/minimax-m2
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
```

### Optional Fallback Providers

```bash
# Fallback Option 1: OpenAI
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4o-mini

# Fallback Option 2: OpenRouter
OPENROUTER_API_KEY=sk-or-your-key
```

### Optional Features

```bash
# Google Search API (for research agent)
GOOGLE_API_KEY=your-google-api-key
GOOGLE_CSE_ID=your-google-cse-id

# Temperature setting
OPENAI_TEMPERATURE=0.7
```

---

## Supported Models

### NVIDIA Models (Primary)
- `minimaxai/minimax-m2` (Default - Recommended)
- Fast, reliable, high-quality output
- Free tier available

### OpenAI Models (Fallback)
- `gpt-4o-mini` (Fast & Affordable)
- `gpt-4o` (High Performance)
- `gpt-3.5-turbo` (Budget Option)

---

## Troubleshooting

### "NVIDIA_API_KEY required" Error
- Make sure you added the environment variable in your deployment platform
- Check the key starts with `nvapi-`
- Verify the key is active at https://build.nvidia.com/

### Slow Deployment
- First deployment takes 2-3 minutes (installing dependencies)
- Subsequent deployments are faster (cached)
- If using Docker, switch to Nixpacks/Buildpacks (faster)

### Build Failures
- Check your `requirements.txt` has correct versions
- Ensure Python version is 3.11 or higher
- Check deployment logs for specific errors

---

## Get Your NVIDIA API Key

1. Visit: https://build.nvidia.com/
2. Sign up (free)
3. Go to API Keys → Generate New Key
4. Copy and use in deployment

**Note:** NVIDIA offers generous free tier for testing and development!

---

## Support

For issues, check:
- Deployment platform logs
- GitHub repository issues
- NVIDIA API documentation: https://docs.api.nvidia.com/

Happy deploying! 🚀

