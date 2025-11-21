# Local Testing Setup - Quick Fix

## 🔧 Update Your .env File

Your local `.env` currently has `DEFAULT_MODEL=minimaxai/minimax-m2` which causes 404 errors.

**Update these lines in your `.env` file:**

```bash
# Change this line:
DEFAULT_MODEL=minimaxai/minimax-m2

# To this (Moonshot Kimi - fast, no timeouts):
DEFAULT_MODEL=moonshotai/kimi-k2-instruct-0905

# Also add/update:
DEEPSEEK_THINKING=false
OPENAI_TEMPERATURE=0.3
USE_SIMPLE_PIPELINE=false
```

---

## 🚀 Then Restart the App

```bash
# Stop current app
pkill -f "app.py"

# Start fresh
cd /Users/chulmin.lee/Desktop/github/mrt-tech-test
python3 app.py
```

Visit: **http://localhost:8080**

---

## 🧪 Or Test CrewAI Directly

```bash
cd /Users/chulmin.lee/Desktop/github/mrt-tech-test
python3 crewai_working.py --job-role "Android Developer" --job-level "Junior" --language "Korean"
```

Watch it generate:
- ✅ assignments.json
- ✅ datasets/ folder
- ✅ starter_code/ folder
- ✅ index.html
- ✅ styles.css

---

## 📊 What Will Be Generated:

```
output/android_developer_junior_YYYYMMDD_HHMMSS/
├── research_report.txt (team discussion)
├── assignments.json (5 detailed assignments)
├── assignments.md (markdown version)
├── datasets/
│   ├── hotels.json
│   ├── flights.json
│   ├── bookings.csv
│   └── ... (more datasets)
├── starter_code/
│   ├── BookingViewModel.kt
│   ├── HotelSearchActivity.kt
│   └── ... (more starter files)
├── index.html (candidate portal)
├── styles.css (Myrealtrip branding)
└── design_notes.md
```

Just like the 20251113 example!

---

## ✅ Expected Workflow:

1. **Phase 1**: Team discusses (9 tasks, ~3-4 min)
2. **Asset Generation**: Creates all files (~2 min)
3. **Phase 2**: QA reviews website (3 tasks, ~1 min)
4. **Total**: ~6-7 minutes
5. **Result**: Complete tech test with portal!

---

##  Summary of Changes:

1. ✅ Model: Moonshot Kimi (fast, no timeouts)
2. ✅ Thinking: Disabled (no delays)
3. ✅ All 7 agents working together
4. ✅ Natural interactive discussions
5. ✅ Complete asset generation
6. ✅ Website QA and final approval
7. ✅ Button appears after approval
8. ✅ All files generated like 20251113 example

---

**Update your .env and test!** 🚀

