# Verify Your Deployment is Running the Latest Version

After pushing the code to GitHub, follow these steps to ensure your deployment is running the **correct version** without the OpenRouter error.

---

## ✅ Step 1: Check Your Deployment Version

Visit this URL on your deployed app:

```
https://your-app-url.com/api/version
```

**Expected Response:**
```json
{
  "success": true,
  "version": "2.0.0-nvidia-support",
  "supports": ["NVIDIA", "OpenAI", "OpenRouter"],
  "primary": "NVIDIA",
  "message": "OpenRouter is optional, not required"
}
```

### If you see the above response:
✅ **Your deployment is up to date!** The OpenRouter error is fixed.

### If you see an error or different version:
❌ **Your deployment is running old code.** Continue to Step 2.

---

## 🔄 Step 2: Force Fresh Deployment

### **For Render.com:**

1. **Login** to Render: https://dashboard.render.com/
2. **Find your service** (mrt-tech-test)
3. Click **"Manual Deploy"** dropdown
4. Select **"Clear build cache & deploy"** (IMPORTANT!)
5. Wait 2-3 minutes for rebuild
6. Check `/api/version` endpoint again

### **For Railway:**

1. **Login** to Railway: https://railway.app/
2. **Find your project** (mrt-tech-test)
3. Go to **Settings** → **Service**
4. Click **"Redeploy"** or **"Restart"**
5. If still showing old code:
   - Go to **Settings** → **"Delete Service"**
   - Create a new service from GitHub repo
   - Add `NVIDIA_API_KEY` environment variable
6. Wait 2-3 minutes for rebuild
7. Check `/api/version` endpoint again

### **For Vercel/Other Platforms:**

1. Go to your dashboard
2. Find "Clear Cache" or "Redeploy" option
3. Force a fresh deployment
4. Check `/api/version` endpoint

---

## 🧪 Step 3: Test with NVIDIA API Key

### Set Environment Variable:

**On Render.com:**
1. Go to your service
2. Click "Environment"
3. Add: `NVIDIA_API_KEY` = `nvapi-your-key-here`
4. Save (auto-redeploys)

**On Railway:**
1. Go to your service
2. Click "Variables" tab
3. Add: `NVIDIA_API_KEY` = `nvapi-your-key-here`
4. Redeploy if needed

### Test the Application:

1. Visit your app homepage
2. Fill in the form:
   - Job Role: `iOS Developer`
   - Job Level: `Senior`
   - Language: `Korean`
3. Click "Generate"
4. Watch the logs

**Expected behavior:**
- ✅ You should see: "✨ Using NVIDIA minimaxai/minimax-m2"
- ✅ Agents start working
- ✅ No OpenRouter error

**If you still see:**
- ❌ "OPENROUTER_API_KEY required for CrewAI"
- ❌ "OpenrouterException - User not found"

Then the deployment is **STILL running old cached code**. Go back to Step 2 and clear the build cache more aggressively.

---

## 🔑 Get Your NVIDIA API Key

If you don't have an NVIDIA API key yet:

1. Visit: **https://build.nvidia.com/**
2. **Sign up** (free account)
3. Go to **"API Keys"**
4. Click **"Generate API Key"**
5. Copy the key (starts with `nvapi-...`)
6. Add to your deployment environment variables

---

## 📊 Verify Logs on Startup

When your app starts, you should see in the logs:

```
======================================================================
🚀 Tech Test Generator Web App
📦 Version: 2.0.0-nvidia-support
======================================================================
📍 Server: http://0.0.0.0:8080
🎨 Using Myrealtrip branding
🤖 Powered by NVIDIA & CrewAI
💡 Primary: NVIDIA | Fallback: OpenAI, OpenRouter
======================================================================
```

If you see **Version: 2.0.0-nvidia-support**, the deployment is correct!

---

## 🆘 Still Having Issues?

### Option A: Nuclear Option - Delete and Redeploy

**Render.com:**
1. Delete the entire service
2. Create a new web service
3. Connect to GitHub: `chulminlee01/mrt-tech-test`
4. Set branch: `main`
5. Add environment variable: `NVIDIA_API_KEY`
6. Deploy

**Railway:**
1. Delete the project
2. Create new project from GitHub repo
3. Add environment variable: `NVIDIA_API_KEY`
4. Deploy

### Option B: Local Test First

Test locally to confirm the code works:

```bash
cd /Users/chulmin.lee/Desktop/github/mrt-tech-test
git pull origin main
python verify_setup.py
python app.py
```

Visit: http://localhost:8080/api/version

If local works but deployment doesn't, the issue is **definitely cache** on the deployment platform.

---

## ✅ Success Checklist

- [ ] `/api/version` shows `"version": "2.0.0-nvidia-support"`
- [ ] `/api/version` shows `"message": "OpenRouter is optional, not required"`
- [ ] Startup logs show `Version: 2.0.0-nvidia-support`
- [ ] `NVIDIA_API_KEY` environment variable is set
- [ ] App starts without OpenRouter error
- [ ] Can generate assignments with NVIDIA API

If all checkboxes are ✅, you're all set! 🎉

---

## 📞 Contact

If you've followed all steps and still see the OpenRouter error, the deployment platform might have aggressive caching. Consider switching to a different platform or contact their support to clear all caches.

