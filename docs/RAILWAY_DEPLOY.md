# 🚂 Railway Deployment Guide (Recommended!)

## ✅ Why Railway?

✅ **No timeout limits** - Full 4-6 minute generation works  
✅ **Free tier** - 500 hours/month included  
✅ **Easy deployment** - Git push to deploy  
✅ **Full Flask support** - Works out of the box  
✅ **Environment variables** - Easy configuration  
✅ **Custom domains** - Can use your own domain  

---

## 🚀 Deploy in 5 Minutes

### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

Or visit: https://railway.app

### Step 2: Login to Railway

```bash
railway login
```

Opens browser for authentication.

### Step 3: Initialize Project

```bash
cd /Users/chulmin.lee/Desktop/github/mrt-tech-test
railway init
```

Follow prompts:
- Project name: `mrt-tech-test-generator`
- Create new project: Yes

### Step 4: Add Environment Variables

```bash
# Add your API keys
railway variables set NVIDIA_API_KEY=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
railway variables set OPENROUTER_API_KEY=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
railway variables set GOOGLE_API_KEY=AIzaSyCiSivvk-WNz33lntQRp8XVFas_acP2n8U
railway variables set GOOGLE_CSE_ID=c2df9ceeedce6477d
railway variables set OPENROUTER_SITE_URL=https://myrealtrip.com
railway variables set OPENROUTER_APP_NAME="MRT Tech Test Generator"
```

### Step 5: Deploy

```bash
railway up
```

**That's it!** Railway will:
- Detect Python project
- Install dependencies from requirements.txt
- Run with gunicorn (from Procfile)
- Assign a public URL

### Step 6: Get Your URL

```bash
railway domain
```

Or visit Railway dashboard: https://railway.app/project/[your-project]

**Your app is now live!** 🎉

Example: `https://mrt-tech-test-generator.up.railway.app`

---

## 🔧 Configuration Files (Already Created!)

### ✅ requirements.txt
```
flask>=3.0.0
crewai>=0.11.0
crewai-tools>=0.8.0
langchain>=0.2.14
langchain-openai>=0.1.22
...
gunicorn>=21.0.0  ← Added for production
```

### ✅ Procfile
```
web: gunicorn -w 4 -b 0.0.0.0:$PORT app:app --timeout 600
```

### ✅ railway.json
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn -w 4 -b 0.0.0.0:$PORT app:app --timeout 600"
  }
}
```

---

## 🌐 After Deployment

### Your Live URLs

```
Main App: https://your-app.up.railway.app
API: https://your-app.up.railway.app/api/generate
Test Page: https://your-app.up.railway.app/test_server.html
```

### Usage

1. **Share the URL** with your team
2. **Anyone can access** the web UI
3. **Generate tech tests** on demand
4. **Download outputs** directly
5. **View portals** in browser

---

## 💰 Cost

### Railway Free Tier

**Included:**
- 500 execution hours/month
- $5 credit/month
- 1 GB RAM
- Shared CPU

**Your App Usage:**
- ~0.5 hours per 10 generations
- ~100 generations/month on free tier
- After that: ~$5-10/month

**Sufficient for:**
- Small team usage
- Testing and development
- 50-100 tech tests/month

---

## 🔒 Security

### Environment Variables

All API keys are securely stored in Railway:

```bash
# Set variables (only once)
railway variables set NVIDIA_API_KEY=...
railway variables set OPENROUTER_API_KEY=...
railway variables set GOOGLE_API_KEY=...

# View variables
railway variables
```

### Access Control

**Option 1: Public (anyone can use)**
- Default setup
- Anyone with URL can generate

**Option 2: Add authentication**
```python
# Add to app.py
from functools import wraps

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if auth != f"Bearer {os.getenv('API_SECRET')}":
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route("/api/generate", methods=["POST"])
@require_auth  # Add authentication
def generate():
    ...
```

---

## 📊 Deployment Comparison

| Platform | Timeout | Free Tier | Ease | Best For |
|----------|---------|-----------|------|----------|
| **Railway** | ∞ (unlimited) | 500 hrs/mo | ⭐⭐⭐⭐⭐ | **Recommended!** |
| **Render** | ∞ (unlimited) | 750 hrs/mo | ⭐⭐⭐⭐ | Good alternative |
| **Heroku** | ∞ (unlimited) | None (paid) | ⭐⭐⭐ | Established, but not free |
| **AWS Lambda** | 15 min | 1M requests/mo | ⭐⭐ | Enterprise, complex |
| **Netlify** | 10-26 sec | Unlimited | ⭐⭐⭐⭐⭐ | **Static only** |

---

## 🎯 My Recommendation

### Deploy to Railway (Best Option!)

**Why:**
1. ✅ Full Flask app works unchanged
2. ✅ No timeout issues (4-6 min generation OK)
3. ✅ Free tier sufficient for your needs
4. ✅ Easy deployment (5 minutes)
5. ✅ Environment variables secure
6. ✅ Auto-deploys on git push
7. ✅ Free SSL certificate
8. ✅ Custom domain support

**Steps:**
```bash
npm install -g @railway/cli
railway login
cd /Users/chulmin.lee/Desktop/github/mrt-tech-test
railway init
railway up
```

**Done!** Your app is live in ~5 minutes! 🚀

---

## 🆚 Netlify vs Railway

### Use Netlify For:
- ✅ Static tech test portals (already generated)
- ✅ Fast CDN delivery
- ✅ Simple candidate-facing pages

### Use Railway For:
- ✅ Dynamic tech test generation
- ✅ Web UI for creating tests
- ✅ API endpoints
- ✅ Background processing

### Best of Both Worlds:
```
Railway: https://mrt-generator.railway.app
└── Generate tech tests (internal tool)
    ↓
    Creates output files
    ↓
Netlify: https://mrt-tech-tests.netlify.app
└── Serves portals to candidates (public)
```

---

## 🚀 Quick Start Commands

### Deploy to Railway (Full App)

```bash
npm install -g @railway/cli
railway login
cd /Users/chulmin.lee/Desktop/github/mrt-tech-test
railway init
railway variables set OPENROUTER_API_KEY=sk-or-v1-...
railway variables set GOOGLE_API_KEY=AIza...
railway variables set GOOGLE_CSE_ID=c2df9...
railway up
railway open
```

### Deploy to Netlify (Static Portals)

```bash
cd /Users/chulmin.lee/Desktop/github/mrt-tech-test/output
netlify deploy --prod --dir=.
```

---

**Ready to deploy?** I recommend **Railway** for the full working system! 🚂✨

