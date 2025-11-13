# 🔧 Troubleshooting Guide

## Issue: Generate Button Not Working

### Quick Checks

1. **Is the server running?**
   ```bash
   # Check if process is running
   lsof -i :8080
   
   # Should show: python (running on port 8080)
   ```

2. **Open test page**
   ```
   http://localhost:8080/test_server.html
   ```
   This will test all API endpoints and show exactly what's working/broken

3. **Check browser console**
   - Open browser
   - Press `F12` or `Cmd+Option+I`
   - Click `Console` tab
   - Click "Generate" button
   - Look for errors (red text)

4. **Check server console**
   - Look at the terminal where Flask is running
   - When you click "Generate", you should see:
     ```
     [API] Received request: role=iOS Developer, level=Senior...
     [API] Starting generation for job_id=...
     [API] Thread started successfully...
     ```

---

## Common Issues & Solutions

### Issue 1: Server Not Running

**Symptoms:**
- Page doesn't load
- "Cannot connect" error

**Solution:**
```bash
cd /Users/chulmin.lee/Desktop/github/mrt-tech-test
./start_webapp.sh
```

---

### Issue 2: Port 8080 Already in Use

**Symptoms:**
- Server won't start
- "Address already in use" error

**Solution:**
```bash
# Find and kill process
lsof -i :8080
kill -9 [PID]

# Or use different port (edit app.py line 291)
app.run(debug=True, host="0.0.0.0", port=9000)
```

---

### Issue 3: JavaScript Error

**Symptoms:**
- Button doesn't respond
- No console logs

**Solution:**
1. Open browser console (F12)
2. Look for red errors
3. If you see `Uncaught ReferenceError` or `Uncaught TypeError`:
   - Hard refresh: `Cmd+Shift+R` or `Ctrl+Shift+F5`
   - Clear cache and reload

---

### Issue 4: API Call Fails

**Symptoms:**
- Button spins but nothing happens
- Console shows fetch error

**Check:**
```javascript
// In browser console, manually test:
fetch('/api/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    job_role: 'iOS Developer',
    job_level: 'Senior',
    language: 'Korean'
  })
}).then(r => r.json()).then(d => console.log(d))
```

---

### Issue 5: Form Validation Error

**Symptoms:**
- Alert says "Please fill in all required fields"

**Solution:**
- Make sure you selected options from ALL dropdowns:
  - Job Role (not "Select a role...")
  - Job Level (not "Select a level...")
  - Language (should have default "Korean")

---

### Issue 6: CORS Error

**Symptoms:**
- Console shows CORS policy error

**Solution:**
- This shouldn't happen if accessing from same domain
- If using different domain, add to app.py:
  ```python
  from flask_cors import CORS
  CORS(app)
  ```

---

### Issue 7: API Keys Missing

**Symptoms:**
- Server console shows: "No API keys found"

**Solution:**
```bash
# Check .env file exists
cat .env | grep API_KEY

# Should show:
# OPENROUTER_API_KEY=sk-or-...
# GOOGLE_API_KEY=AIza...
```

---

## 🧪 Debug Mode

### Step 1: Run Test Server
```bash
cd /Users/chulmin.lee/Desktop/github/mrt-tech-test

# Start server
./start_webapp.sh
```

### Step 2: Open Test Page
```
http://localhost:8080/test_server.html
```

**This will show:**
- ✅ Server status
- ✅ API endpoints status
- ✅ Test generate call
- ✅ Exact error messages if any fail

### Step 3: Check Main Page
```
http://localhost:8080
```

**Open browser console (F12) and watch for:**
- `🚀 Form submitted` - Button was clicked
- `📋 Form data:` - Data being sent
- `📡 Calling /api/generate...` - API call starting
- `📡 Response status: 200` - Server responded
- `✅ Generation started successfully` - All good!

If you see any ❌ errors, that's where the problem is!

---

## 🔍 Manual API Test

If nothing else works, test the API directly:

```bash
# Test with curl
curl -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{"job_role":"iOS Developer","job_level":"Senior","language":"Korean"}'

# Should return:
# {"success":true,"job_id":"20241113...","message":"Generation started"}
```

---

## 📊 Checklist

Run through this checklist:

```
□ Server is running (./start_webapp.sh)
□ Can access http://localhost:8080
□ Main page loads (shows form)
□ Dropdowns populated with options
□ Can select role, level, language
□ Browser console open (F12)
□ No red errors in console
□ Click "Generate" button
□ See console logs starting with 🚀
□ Button shows loading spinner
□ Status card appears
□ Agent boxes show up
□ Logs start appearing

If ANY step fails, that's where the problem is!
```

---

## 🆘 Still Not Working?

### Get Full Debug Info

1. **Start server with verbose output:**
   ```bash
   cd /Users/chulmin.lee/Desktop/github/mrt-tech-test
   source .venv/bin/activate
   FLASK_ENV=development python app.py
   ```

2. **Open test page:**
   ```
   http://localhost:8080/test_server.html
   ```

3. **Take screenshot of:**
   - Test page results
   - Browser console (F12)
   - Server console output

4. **Check these files exist:**
   ```bash
   ls -la app.py
   ls -la templates/index.html
   ls -la crewai_working.py
   ```

---

## ✅ Expected Behavior

### When Everything Works:

**Server Console:**
```
======================================================================
🚀 Tech Test Generator Web App
======================================================================
📍 Server: http://localhost:8080
...
 * Running on http://0.0.0.0:8080

[API] Received request: role=iOS Developer, level=Senior, lang=Korean
[API] Starting generation for job_id=20241113123456_1234
[API] Thread started successfully for job_id=20241113123456_1234
```

**Browser Console:**
```
🚀 Form submitted
📋 Form data: {job_role: "iOS Developer", job_level: "Senior", language: "Korean"}
🔄 Button disabled, making API call...
📡 Calling /api/generate...
📡 Response status: 200
📡 Response data: {success: true, job_id: "20241113123456_1234", message: "Generation started"}
✅ Generation started successfully
🆔 Job ID: 20241113123456_1234
```

**Browser UI:**
- Form disappears
- Status card appears
- 7 agent boxes appear
- Progress bar animates
- Logs start streaming

---

## 🚀 Quick Fix

If still not working, try this reset:

```bash
# Stop server (Ctrl+C)

# Reinstall dependencies
pip install -r requirements.txt

# Restart server
./start_webapp.sh
```

Then visit test page first:
```
http://localhost:8080/test_server.html
```

---

**Need more help?** Check the console outputs (both browser and server) - they now have detailed logging!

