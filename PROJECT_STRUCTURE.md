# 📁 Project Structure

## Clean Repository - Essential Files Only

### 📚 Documentation (5 files)

| File | Size | Purpose |
|------|------|---------|
| **README.md** | 18K | Project overview & setup guide |
| **START_HERE.md** | 16K | Quick start & usage guide |
| **ARCHITECTURE.md** | 43K | Complete system architecture |
| **RAILWAY_DEPLOY.md** | 6K | Railway deployment guide |
| **TROUBLESHOOTING.md** | 6K | Debug & troubleshooting |

### 🤖 Core Agents (6 files)

| File | Size | Purpose |
|------|------|---------|
| **agent_researcher.py** | 10K | Research with Google CSE |
| **agent_question_generator.py** | 15K | Assignment generation |
| **agent_data_provider.py** | 5.6K | Dataset generation |
| **agent_starter_code.py** | 9K | Starter code generation |
| **agent_web_builder.py** | 24K | HTML portal generation |
| **agent_web_designer.py** | 7.6K | CSS styling generation |

### 🎯 Orchestration (3 files)

| File | Size | Purpose |
|------|------|---------|
| **crewai_working.py** | 18K | CrewAI team collaboration |
| **main_orchestrator.py** | 9.5K | Sequential pipeline |
| **sheet_bulk_runner.py** | 16K | Bulk generation from sheets |

### 🌐 Web Application (2 files)

| File | Size | Purpose |
|------|------|---------|
| **app.py** | 12K | Flask web server |
| **templates/index.html** | 54K | Web UI with agent visualization |

### 🔧 Utilities (1 file)

| File | Size | Purpose |
|------|------|---------|
| **llm_client.py** | 7K | Multi-provider LLM client |

### ⚙️ Configuration (7 files)

| File | Size | Purpose |
|------|------|---------|
| **requirements.txt** | ~1K | Python dependencies |
| **.env** | ~1K | API keys (not in git) |
| **.env.example** | ~1K | Environment template |
| **.gitignore** | ~1K | Git ignore rules |
| **Procfile** | <1K | Production server config |
| **railway.json** | <1K | Railway settings |
| **netlify.toml** | <1K | Netlify config |

### 🚀 Deployment Scripts (2 files)

| File | Size | Purpose |
|------|------|---------|
| **start_webapp.sh** | 2K | Local server startup |
| **deploy_railway.sh** | 3K | Railway deployment |

### 🧪 Testing (1 file)

| File | Size | Purpose |
|------|------|---------|
| **test_server.html** | 4K | API diagnostics page |

---

## 📊 Total Files

- **Documentation:** 5 files (essential guides)
- **Python Code:** 11 files (agents + orchestration + web)
- **Configuration:** 7 files (env, deployment configs)
- **Scripts:** 2 files (startup + deployment)
- **Testing:** 1 file (diagnostic page)
- **Templates:** 1 file (web UI)

**Total:** ~27 essential files (was ~40+ with duplicates)

---

## 🗑️ Removed Files

- ❌ 16 redundant documentation files (interim guides, duplicates)
- ❌ crewai_orchestrator.py (non-working version)
- ❌ assignments.json (generated output)
- ❌ Other generated outputs

---

## 📁 Directory Structure

```
mrt-tech-test/
├── 📚 Documentation
│   ├── README.md
│   ├── START_HERE.md
│   ├── ARCHITECTURE.md
│   ├── RAILWAY_DEPLOY.md
│   └── TROUBLESHOOTING.md
│
├── 🤖 Agents
│   ├── agent_researcher.py
│   ├── agent_question_generator.py
│   ├── agent_data_provider.py
│   ├── agent_starter_code.py
│   ├── agent_web_builder.py
│   └── agent_web_designer.py
│
├── 🎯 Orchestration
│   ├── crewai_working.py
│   ├── main_orchestrator.py
│   └── sheet_bulk_runner.py
│
├── 🌐 Web Application
│   ├── app.py
│   ├── templates/
│   │   └── index.html
│   └── llm_client.py
│
├── ⚙️ Configuration
│   ├── .env (API keys - not in git)
│   ├── .env.example
│   ├── .gitignore
│   ├── requirements.txt
│   ├── Procfile
│   ├── railway.json
│   └── netlify.toml
│
└── 🚀 Scripts
    ├── start_webapp.sh
    ├── deploy_railway.sh
    └── test_server.html
```

---

## 🎯 Quick Reference

### Local Development
```bash
./start_webapp.sh
```

### Railway Deployment
```bash
./deploy_railway.sh
```

### Documentation to Read
1. **START_HERE.md** - Begin here
2. **README.md** - Project overview
3. **RAILWAY_DEPLOY.md** - Deploy online
4. **TROUBLESHOOTING.md** - If issues

---

**Clean, organized, production-ready!** ✅
