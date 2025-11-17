# 🤖 Myrealtrip Tech Test Generator

> **AI-powered collaborative team system for generating comprehensive, role-specific coding assignments with real-time visualization.**

Automatically creates complete assignment packages through **CrewAI team collaboration** with PM leadership, research, team discussions, quality reviews, and beautiful interactive UI.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/CrewAI-0.11+-green.svg)](https://www.crewai.com/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-orange.svg)](https://flask.palletsprojects.com/)

---

## ✨ Key Features

### 🤖 CrewAI Collaborative Team
- **👔 PM Leader** - Initializes, delegates, leads discussions, approves delivery
- **🔍 Research Analyst** - Google Custom Search (4+ searches per generation)
- **✏️ Assignment Designer** - Creates 5 unique assignments
- **🔎 QA Reviewer** - Quality assurance and feedback
- **📊 Data Provider** - Generates synthetic datasets
- **🌐 Web Builder** - Creates candidate portals
- **🎨 Web Designer** - Custom styling

### 🎨 Interactive Web UI
- **Real-time agent visualization** - Watch agents work with live status updates
- **Fixed-grid layout** - 7 agent activity boxes with summaries
- **Click to expand** - Full conversation details in modals
- **Color-coded messages** - Each agent has distinct colors
- **Task separators** - Clear visual task progression
- **Clean display** - ANSI codes automatically removed

### 🔍 True Collaboration
- **PM initialization** - Sets direction and delegates
- **Team discussions** - Agents discuss findings and reach consensus
- **Quality reviews** - Built-in peer review process
- **Iterative revisions** - Agents update based on feedback
- **Final sign-off** - PM approves delivery

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (3.11 recommended)
- **OpenRouter API Key** (for CrewAI - required)
- **Google Custom Search API** (API Key + Search Engine ID)
- **NVIDIA API Key** (optional, for other agents)

### Installation

```bash
# 1. Clone and enter directory
cd mrt-tech-test

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API keys
cp .env.example .env
# Edit .env and add your keys:
#   NVIDIA_API_KEY (recommended - primary LLM)
#   GOOGLE_API_KEY (optional - for research agent)
#   GOOGLE_CSE_ID (optional - for research agent)
#
# Alternative LLM options (if not using NVIDIA):
#   OPENAI_API_KEY (fallback option)
#   OPENROUTER_API_KEY (fallback option)
```

### Get API Keys

- **NVIDIA** (Recommended): https://build.nvidia.com/ - Free tier available
- **OpenAI** (Alternative): https://platform.openai.com/api-keys
- **OpenRouter** (Alternative): https://openrouter.ai/
- **Google CSE** (Optional): https://programmablesearchengine.google.com/

### Launch Web UI

```bash
./start_webapp.sh
```

**Then open:** http://localhost:8080

---

## 🎬 How It Works

### Collaborative Workflow

```
1. 👔 PM Initialization
   └─→ Kickoff project, set direction

2. 🔍 Research Phase (Google CSE)
   └─→ 4 targeted searches
   └─→ Analyze findings
   └─→ Synthesize report

3. 💬 Team Discussion
   └─→ PM leads discussion
   └─→ Designer proposes approach
   └─→ Reviewer adds concerns
   └─→ Team reaches consensus

4. ✏️ Assignment Creation
   └─→ Designer creates 5 assignments
   └─→ Based on team consensus

5. 🔎 Quality Review
   └─→ Reviewer examines outputs
   └─→ Provides specific feedback
   └─→ Requests revisions if needed

6. 👔 PM Final Decision
   └─→ Reviews feedback
   └─→ Approves or requests changes
   └─→ Provides final sign-off

7. 📊🌐🎨 Asset Generation
   └─→ Datasets (CSV/JSON)
   └─→ Starter code (Swift/Kotlin/etc)
   └─→ Candidate portal (HTML/CSS)
```

**Total Time:** 4-6 minutes per tech test

---

## 🎨 Interactive UI Features

### Fixed-Grid Agent Activity Boxes

```
💬 Agent Activity & Thinking

┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  👔 PM       │  │ 🔍 Research  │  │ ✏️ Designer  │  │ 🔎 Reviewer  │
│ [ACTIVE NOW] │  │ [Completed ✅]│  │ [Waiting]    │  │ [Waiting]    │
├──────────────┤  ├──────────────┤  ├──────────────┤  ├──────────────┤
│ Team, we're  │  │ Research     │  │ Not started  │  │ Not started  │
│ creating...  │  │ complete with│  │ yet...       │  │ yet...       │
│              │  │ findings     │  │              │  │              │
│ Click to     │  │ Click to     │  │ Click to     │  │ Click to     │
│ expand →     │  │ expand →     │  │ expand →     │  │ expand →     │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
  Green pulsing    Green solid      Gray             Gray

[Click any box → Modal with full conversation]
```

**Features:**
- ✅ Fixed-size boxes (220px height)
- ✅ Responsive grid (3-4 per row)
- ✅ Summaries (last 2-3 lines, ~200 chars)
- ✅ Scrollable content inside boxes
- ✅ Click to expand full details
- ✅ Color-coded agent messages
- ✅ Task separators
- ✅ Real-time updates

---

## 📂 Complete Output

Each generation creates a complete package:

```
output/ios_developer_senior_20241113_123456/
├── research_report.txt          # Google CSE research findings
├── assignments.json              # 5 structured assignments
├── assignments.md                # Human-readable preview
├── datasets/                     # Synthetic test data
│   ├── OTA-IOS-001.csv
│   ├── OTA-IOS-002.json
│   ├── OTA-IOS-003.csv
│   ├── OTA-IOS-004.json
│   └── OTA-IOS-005.csv
├── starter_code/                 # Language-specific templates
│   ├── OTA-IOS-001_starter.swift
│   ├── OTA-IOS-002_starter.swift
│   ├── OTA-IOS-003_starter.swift
│   ├── OTA-IOS-004_starter.swift
│   └── OTA-IOS-005_starter.swift
├── index.html                    # Beautiful candidate portal
├── styles.css                    # Custom Myrealtrip styling
└── design_notes.md               # Design documentation
```

---

## 💬 Real Collaboration Examples

### Team Discussion

```
👔 PM: "Based on research, key findings:
       - SwiftUI is industry standard
       - Senior expects architecture decisions
       Team, what should we test?"

✏️ Designer: "I recommend testing:
             - SwiftUI (research shows it's standard)
             - Async/await (modern pattern)
             - Data modeling (essential for OTA)"

🔎 Reviewer: "We should also assess:
             - Architectural pattern choices
             - Error handling strategies"

👔 PM: "CONSENSUS REACHED:
       We will test these 5 areas:
       1. SwiftUI fundamentals
       2. Networking with async/await
       3. Data modeling
       4. OTA booking flows
       5. Architecture & testing"
```

### Quality Review

```
🔎 Reviewer: "Assignment #3 timeline too tight for Senior level"

👔 PM: "I agree. Designer, please extend to 5 days"

✏️ Designer: "Updated to 5 days with 12-15 hour estimate"

🔎 Reviewer: "Re-reviewed - now approved ✅"
```

---

## 🌐 Deployment Options

### Option 1: Railway (Recommended - Full App)

**Perfect for:** On-demand generation with web UI

```bash
npm install -g @railway/cli
./deploy_railway.sh
```

**Result:** https://your-app.up.railway.app

**Features:**
- ✅ Full web UI
- ✅ No timeout limits
- ✅ Free tier (500 hrs/month)
- ✅ All features work

### Option 2: Netlify (Static Portals Only)

**Perfect for:** Serving pre-generated tests to candidates

```bash
# Generate tests locally first
./start_webapp.sh

# Deploy static files
cd output
netlify deploy --prod --dir=.
```

**Result:** https://mrt-tests.netlify.app

**Features:**
- ✅ Fast CDN delivery
- ✅ Free forever
- ❌ No live generation

### Option 3: Local Only

```bash
./start_webapp.sh
```

**Visit:** http://localhost:8080

---

## 🎯 Usage Examples

### Web UI (Easiest!)

1. Start server: `./start_webapp.sh`
2. Open: http://localhost:8080
3. Select role, level, language
4. Click "Generate Tech Test"
5. Watch agents collaborate in real-time!
6. Click any agent box to see full details
7. Download complete package when done

### Command Line

```bash
# Single role
python crewai_working.py \
  --job-role "iOS Developer" \
  --job-level "Senior" \
  --language Korean

# Bulk generation from Google Sheets
python sheet_bulk_runner.py \
  --sheet-url "https://docs.google.com/spreadsheets/d/YOUR_ID/edit" \
  --output-root bulk_output
```

---

## ⚙️ Configuration

### Environment Variables

```env
# Required for CrewAI
OPENROUTER_API_KEY=sk-or-v1-...           # CrewAI LLM (required)
OPENROUTER_FALLBACK_MODEL=deepseek/deepseek-chat

# Required for Research
GOOGLE_API_KEY=AIza...                    # Google CSE
GOOGLE_CSE_ID=your_search_engine_id

# Optional for Better Quality
NVIDIA_API_KEY=nvapi-...                  # For NVIDIA API
DEFAULT_MODEL=deepseek-ai/deepseek-v3.1-terminus

# Optional Attribution
OPENROUTER_SITE_URL=https://myrealtrip.com
OPENROUTER_APP_NAME=MRT Tech Test Generator
```

### Multi-Provider Setup

- **All agents** → NVIDIA DeepSeek v3.1 with thinking (primary)
- **Automatic fallback** → Moonshot Kimi → Llama → Gemma → Mistral
- **Also supports** → OpenAI, OpenRouter

---

## 🤖 Agent Team

| Agent | Icon | Role | Uses |
|-------|------|------|------|
| **PM Leader** | 👔 | Coordinates team, approves delivery | OpenRouter |
| **Research Analyst** | 🔍 | Google CSE searches (4+) | OpenRouter |
| **Assignment Designer** | ✏️ | Creates 5 assignments | OpenRouter |
| **QA Reviewer** | 🔎 | Quality assurance | OpenRouter |
| **Data Provider** | 📊 | Synthetic datasets | (No LLM) |
| **Web Builder** | 🌐 | Candidate portal | (No LLM) |
| **Web Designer** | 🎨 | Custom styling | NVIDIA/OpenRouter |

---

## 📊 Performance

### Generation Time

| Phase | Time | Agent |
|-------|------|-------|
| PM Init | 10-30 sec | PM |
| Research | 1-2 min | Research (Google CSE) |
| Discussion | 30-60 sec | PM, Designer, Reviewer |
| Assignment Creation | 30-60 sec | Designer + Generator |
| Quality Review | 30-60 sec | Reviewer |
| Asset Generation | 1-2 min | Data, Builder, Designer |
| **Total** | **4-6 min** | All |

### Cost Estimate

**OpenRouter (CrewAI):**
- Free models: $0.00
- Paid models: ~$0.02-0.05 per generation

**NVIDIA (Other agents):**
- ~$0.02-0.05 per generation

**Google CSE:**
- Free: 100 queries/day
- Paid: $5 per 1,000 queries
- Usage: ~4-6 queries per generation

**Total:** ~$0.00-0.10 per tech test

---

## 🐛 Troubleshooting

### Generate Button Not Working?

1. **Check server is running:**
   ```bash
   lsof -i :8080
   ```

2. **Open diagnostic page:**
   ```
   http://localhost:8080/test_server.html
   ```

3. **Hard refresh browser:**
   - Mac: `Cmd + Shift + R`
   - Windows: `Ctrl + Shift + F5`

4. **Check browser console:**
   - Press `F12`
   - Look for errors (red text)

See **TROUBLESHOOTING.md** for complete guide.

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| **START_HERE.md** | Quick start guide - Read this first! |
| **README.md** | This file - Project overview |
| **ARCHITECTURE.md** | Complete system architecture (43K) |
| **RAILWAY_DEPLOY.md** | Deploy to Railway (recommended) |
| **TROUBLESHOOTING.md** | Debug guide & common issues |
| **PROJECT_STRUCTURE.md** | File organization |

---

## 🎯 Project Structure

```
mrt-tech-test/
├── 📚 Documentation (6 files)
│   ├── README.md              ← Project overview
│   ├── START_HERE.md          ← Quick start
│   ├── ARCHITECTURE.md        ← Technical details
│   ├── RAILWAY_DEPLOY.md      ← Deployment
│   ├── TROUBLESHOOTING.md     ← Debug help
│   └── PROJECT_STRUCTURE.md   ← File organization
│
├── 🤖 Agents (6 files)
│   ├── agent_researcher.py
│   ├── agent_question_generator.py
│   ├── agent_data_provider.py
│   ├── agent_starter_code.py
│   ├── agent_web_builder.py
│   └── agent_web_designer.py
│
├── 🎯 Orchestration (3 files)
│   ├── crewai_working.py      ← CrewAI collaboration
│   ├── main_orchestrator.py   ← Sequential pipeline
│   └── sheet_bulk_runner.py   ← Bulk generation
│
├── 🌐 Web Application (3 files)
│   ├── app.py                 ← Flask server
│   ├── templates/index.html   ← Interactive UI
│   └── llm_client.py          ← Multi-provider LLM
│
└── ⚙️ Configuration & Scripts
    ├── requirements.txt       ← Dependencies
    ├── .env / .env.example    ← API keys
    ├── .gitignore             ← Git rules
    ├── Procfile               ← Production config
    ├── railway.json           ← Railway settings
    ├── netlify.toml           ← Netlify config
    ├── start_webapp.sh        ← Local startup
    ├── deploy_railway.sh      ← Railway deploy
    └── test_server.html       ← API diagnostics
```

---

## 🎨 UI Screenshots

### Main Interface
- Myrealtrip logo and branding
- Job role/level/language selectors
- Generate button with loading state
- Real-time progress tracking

### Agent Collaboration View
- 7 fixed-size activity boxes in grid
- Color-coded agent messages
- Live status updates (ACTIVE NOW / Completed ✅)
- Click any box for full conversation

### Formatted Conversations
- PM messages: Purple border
- Research: Blue border
- Designer: Orange border
- Reviewer: Red border
- Task separators with labels

---

## 💡 CrewAI Best Practices Used

✅ **Sequential Process** - Tasks execute in order  
✅ **Agent Memory** - Context preserved across tasks  
✅ **Delegation** - Agents can ask each other  
✅ **Shared Tools** - Google CSE for research  
✅ **Verbose Mode** - Full transparency  
✅ **Quality Reviews** - Built-in peer review  

---

## 🔧 Advanced Usage

### Bulk Generation

Generate for multiple roles using Google Sheets:

```bash
python sheet_bulk_runner.py \
  --sheet-url "https://docs.google.com/spreadsheets/d/YOUR_ID/edit" \
  --output-root bulk_output \
  --max-workers 4
```

### Custom Models

```bash
# Use specific model for CrewAI
OPENROUTER_FALLBACK_MODEL=deepseek/deepseek-chat python crewai_working.py

# Use NVIDIA for all agents
NVIDIA_API_KEY=nvapi-... python main_orchestrator.py --job-role "Backend Engineer"
```

### Environment Profiles

```bash
# Development
python agent_researcher.py --profile dev

# Production
python agent_researcher.py --profile prod
```

---

## 🌍 Deployment

### Deploy to Railway (Recommended)

Full Flask app with CrewAI online in 5 minutes:

```bash
npm install -g @railway/cli
./deploy_railway.sh
```

**Result:** https://your-app.up.railway.app

**Why Railway:**
- ✅ No timeout limits (CrewAI needs 4-6 minutes)
- ✅ Free tier (500 hours/month)
- ✅ All features work
- ✅ Easy deployment

See **RAILWAY_DEPLOY.md** for complete guide.

### Deploy to Netlify (Static Portals)

Serve pre-generated test portals:

```bash
cd output
netlify deploy --prod --dir=.
```

**Result:** https://mrt-tests.netlify.app

**Best for:** Candidate-facing portals (fast CDN delivery)

---

## 🎯 Use Cases

### Use Case 1: Single Tech Test
```bash
./start_webapp.sh
# Visit http://localhost:8080
# Fill form → Generate → Download
```

### Use Case 2: Multiple Roles
```bash
# Create Google Sheet with: team, level, language columns
python sheet_bulk_runner.py --sheet-url "YOUR_SHEET_URL"
```

### Use Case 3: Production Deployment
```bash
./deploy_railway.sh
# Share URL with team
# Anyone can generate tests online
```

---

## 🔍 Features in Detail

### Research with Google CSE
- ✅ Direct API integration (not scraping)
- ✅ Date-restricted searches (recent sources)
- ✅ 4+ targeted queries per generation
- ✅ Source URLs preserved
- ✅ Consensus identification

### Team Collaboration
- ✅ PM leads discussions
- ✅ Agents provide input
- ✅ Consensus building
- ✅ Quality reviews
- ✅ Iterative revisions

### Interactive Visualization
- ✅ 7 agent activity boxes
- ✅ Real-time status updates
- ✅ Pulsing animations for active agents
- ✅ Color-coded messages
- ✅ Expandable detail views
- ✅ Clean ANSI-free display

### Quality Assurance
- ✅ Peer review by QA agent
- ✅ Revision requests
- ✅ Re-review cycle
- ✅ Final PM approval

---

## 📖 Technology Stack

### AI & Orchestration
- **CrewAI 0.11+** - Multi-agent collaboration
- **LangChain 0.2+** - Agent framework
- **LiteLLM** - Multi-provider LLM access
- **OpenRouter** - LLM gateway (CrewAI compatible)
- **NVIDIA** - High-quality LLM (optional)

### Web Framework
- **Flask 3.0+** - Web server
- **Jinja2** - Templates
- **JavaScript (Vanilla)** - Interactive UI

### Data & Tools
- **Google Custom Search API** - Research tool
- **Faker** - Synthetic data generation
- **Pandas** - CSV processing

### Deployment
- **Gunicorn** - Production WSGI server
- **Railway** - Recommended hosting
- **Netlify** - Static site hosting

---

## 🔒 Security

### API Key Management

```bash
# Never commit .env to git
# Use environment variables in production
railway variables set OPENROUTER_API_KEY=...
```

### Data Privacy

- ✅ All datasets are synthetic (Faker-generated)
- ✅ No real user data
- ✅ Safe for public sharing

---

## 🤝 Contributing

This is a Myrealtrip internal tool. For questions or improvements, contact the Myrealtrip Engineering Team.

---

## 📄 License

Proprietary - Myrealtrip OTA Company

---

## 🙏 Acknowledgments

- **CrewAI** - Multi-agent orchestration
- **OpenRouter** - Multi-model LLM access
- **NVIDIA** - High-quality LLM inference
- **Google** - Custom Search API
- **LangChain** - Agent framework

---

## 📞 Support

### Quick Links

- **Quick Start:** See START_HERE.md
- **Deploy Online:** See RAILWAY_DEPLOY.md
- **Having Issues:** See TROUBLESHOOTING.md
- **Architecture:** See ARCHITECTURE.md

### Common Issues

| Issue | Solution |
|-------|----------|
| Generate button not working | Hard refresh (Cmd+Shift+R) |
| No agents showing | Check server console for errors |
| API key errors | Verify .env file has all keys |
| Timeout issues | Use Railway (not Netlify Functions) |

### Test Server

Open http://localhost:8080/test_server.html for automatic diagnostics.

---

## 🎊 Ready to Start?

```bash
# Local development
./start_webapp.sh

# Deploy to Railway
./deploy_railway.sh
```

**Watch your AI team create amazing tech tests with real-time collaboration!** 🚀🤖👥✨

---

**Version:** 2.0  
**Last Updated:** November 13, 2025  
**Status:** Production Ready ✅
