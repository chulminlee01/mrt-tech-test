# 🔧 Railway Deployment Fix

## ✅ Issues Fixed

### Issue: "Deploy crashed" - Worker exiting

**Root Causes & Fixes:**

### 1. ✅ Port Configuration
**Problem:** App was hardcoded to port 8080  
**Fix:** Now uses `$PORT` environment variable (Railway requirement)

```python
# Before
app.run(debug=True, host="0.0.0.0", port=8080)

# After  
port = int(os.getenv("PORT", 8080))
app.run(debug=False, host="0.0.0.0", port=port)
```

### 2. ✅ Python Version
**Problem:** No Python version specified  
**Fix:** Created `runtime.txt` with Python 3.11.9

```
python-3.11.9
```

### 3. ✅ Gunicorn Configuration
**Problem:** Too many workers, not enough logging  
**Fix:** Updated Procfile with better settings

```
Before: gunicorn -w 4 ...
After:  gunicorn -w 2 ... --log-level debug --access-logfile - --error-logfile -
```

### 4. ✅ Debug Mode
**Problem:** Debug mode enabled in production  
**Fix:** Changed to `debug=False` for production

---

## 🚀 Deploy Again

### Step 1: Commit Changes

```bash
cd /Users/chulmin.lee/Desktop/github/mrt-tech-test

# Check what changed
git status

# Add files
git add app.py Procfile runtime.txt

# Commit
git commit -m "Fix Railway deployment: port config, Python version, gunicorn settings"
```

### Step 2: Redeploy to Railway

```bash
railway up
```

Or if you've connected GitHub:
```bash
git push origin main
# Railway auto-deploys
```

### Step 3: Check Logs

```bash
railway logs
```

**Look for:**
```
✅ "Starting gunicorn"
✅ "Booting worker"
✅ "Server: http://0.0.0.0:[PORT]"
✅ "🚀 Tech Test Generator Web App"
```

---

## 🔍 If Still Crashing

### Check Environment Variables

```bash
# List all variables
railway variables

# Make sure these are set:
railway variables set OPENROUTER_API_KEY=sk-or-v1-...
railway variables set GOOGLE_API_KEY=AIza...
railway variables set GOOGLE_CSE_ID=c2df9...
```

### Check Logs for Errors

```bash
railway logs --follow
```

**Common errors:**

| Error Message | Solution |
|---------------|----------|
| `ModuleNotFoundError: No module named 'crewai'` | Dependencies not installed - check requirements.txt |
| `OPENROUTER_API_KEY not found` | Set environment variable |
| `Address already in use` | Port conflict - should be fixed now |
| `ImportError: ...` | Missing dependency in requirements.txt |

### Verify requirements.txt

```bash
cat requirements.txt
```

**Should include:**
```
flask>=3.0.0
crewai>=0.11.0
crewai-tools>=0.8.0
langchain>=0.2.14
langchain-openai>=0.1.22
langchain-community>=0.2.11
langhub>=0.1.21
google-api-python-client>=2.143.0
requests>=2.31.0
pandas>=2.2.2
Faker>=25.3.0
python-dotenv>=1.0.1
gunicorn>=21.0.0
```

---

## 🧪 Test Locally with Gunicorn

Before deploying, test with gunicorn locally:

```bash
cd /Users/chulmin.lee/Desktop/github/mrt-tech-test
source .venv/bin/activate

# Test gunicorn (like Railway will use)
PORT=8080 gunicorn -w 2 -b 0.0.0.0:8080 app:app --timeout 600
```

**Should see:**
```
[INFO] Starting gunicorn 21.x.x
[INFO] Listening at: http://0.0.0.0:8080
[INFO] Using worker: sync
[INFO] Booting worker with pid: ...
```

**Then test:**
```
http://localhost:8080
```

If this works locally with gunicorn, it should work on Railway!

---

## 🔧 Alternative: Simplified Startup

If gunicorn still has issues, use simpler startup:

**Create `start.sh`:**
```bash
#!/bin/bash
python app.py
```

**Update `Procfile`:**
```
web: python app.py
```

**Redeploy:**
```bash
railway up
```

---

## 📊 Checklist

Before deploying to Railway:

```
☐ Port uses $PORT environment variable (✅ Fixed!)
☐ Debug mode is False (✅ Fixed!)
☐ runtime.txt specifies Python version (✅ Created!)
☐ Procfile has correct gunicorn command (✅ Updated!)
☐ requirements.txt includes all deps (✅ Check it!)
☐ Environment variables set on Railway
   ☐ OPENROUTER_API_KEY
   ☐ GOOGLE_API_KEY
   ☐ GOOGLE_CSE_ID
☐ Test locally with gunicorn first
☐ Commit and push changes
☐ Deploy to Railway
☐ Check logs: railway logs
```

---

## 🚀 Deploy Steps (After Fixes)

```bash
# 1. Test locally with gunicorn
source .venv/bin/activate
PORT=8080 gunicorn -w 2 -b 0.0.0.0:8080 app:app --timeout 600

# 2. If works, commit changes
git add app.py Procfile runtime.txt
git commit -m "Fix Railway deployment"

# 3. Deploy
railway up

# 4. Watch logs
railway logs --follow

# 5. If successful, get URL
railway domain
```

---

## ✅ Fixes Applied

1. ✅ **app.py** - Uses $PORT env var, debug=False
2. ✅ **Procfile** - Reduced workers (2), added logging
3. ✅ **runtime.txt** - Specifies Python 3.11.9
4. ✅ **requirements.txt** - Includes gunicorn

**Try deploying again now!** 🚀

---

## 🆘 Still Not Working?

### Get Detailed Logs

```bash
# Real-time logs
railway logs --follow

# Last 100 lines
railway logs --tail 100

# Show timestamps
railway logs --timestamps
```

### Check Railway Dashboard

Visit: https://railway.app/project/[your-project]

**Look for:**
- Build logs (did dependencies install?)
- Deploy logs (did app start?)
- Runtime logs (what error occurred?)

### Common Fixes

**Error: "No module named 'X'"**
```bash
# Add to requirements.txt
echo "missing-module>=1.0.0" >> requirements.txt
railway up
```

**Error: "API key missing"**
```bash
railway variables set YOUR_API_KEY=...
railway restart
```

**Error: "Port already in use"**  
→ Should be fixed now with $PORT variable

---

**With these fixes, Railway deployment should work!** 🎉

