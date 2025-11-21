# Coding Platform Architecture Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Core Components (Agents)](#core-components-agents)
4. [Orchestration Layer](#orchestration-layer)
5. [Data Flow](#data-flow)
6. [Technology Stack](#technology-stack)
7. [Configuration & Environment](#configuration--environment)
8. [Bulk Processing](#bulk-processing)
9. [Output Artifacts](#output-artifacts)
10. [Deployment](#deployment)
11. [Use Cases & Workflows](#use-cases--workflows)

---

## Overview

The **Myrealtrip Take-Home Assignment Generation Platform** is an AI-powered, multi-agent system designed to automatically generate comprehensive, role-specific coding assignments for technical recruitment. The platform creates end-to-end assignment packages including:

- Industry research reports
- Structured assignment specifications
- Synthetic datasets
- Starter code templates
- Interactive candidate portals (HTML/CSS)
- Design documentation

### Key Features

- **AI-Driven Generation**: Uses OpenAI/OpenRouter LLMs with LangChain for intelligent content creation
- **Multi-Agent Architecture**: Specialized agents for different generation tasks
- **Customizable**: Supports multiple job roles, levels, and languages
- **Scalable**: Bulk generation from Google Sheets configuration
- **Production-Ready**: Includes Netlify deployment configuration

---

## System Architecture

### High-Level Design

The platform follows a **pipeline-based multi-agent architecture** where each agent is responsible for a specific aspect of assignment generation:

```
┌────────────────────────────────────────────────────────────────┐
│                     Main Orchestrator                          │
│                  (main_orchestrator.py)                        │
└────────────────────────────────────────────────────────────────┘
                            │
                            ├─── Agent 1: Researcher
                            ├─── Agent 2: Question Generator
                            ├─── Agent 3: Data Provider
                            ├─── Agent 4: Starter Code Generator
                            ├─── Agent 5: Web Builder
                            └─── Agent 6: Web Designer (optional)
                                    │
                            ┌───────▼────────┐
                            │  Output Bundle │
                            │  (per role)    │
                            └────────────────┘
```

### Architecture Patterns

1. **Agent Pattern**: Each agent is an autonomous module with a single responsibility
2. **Pipeline Pattern**: Sequential execution with dependency management
3. **Producer-Consumer Pattern**: Each agent consumes outputs from previous agents
4. **Configuration-Driven**: Environment variables and command-line arguments for flexibility

---

## Core Components (Agents)

### Agent 1: Deep Researcher (`agent_researcher.py`)

**Purpose**: Conducts automated web research on industry best practices for take-home assignments.

**Technology**:
- LangChain ReAct agent with Google Custom Search API
- Recent-biased search (configurable time window, default: 6 months)
- Structured information synthesis

**Key Functions**:
```python
def run_researcher(
    topic: Optional[str] = None,
    output_path: str = "research_report.txt",
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    job_role: Optional[str] = None,
    job_level: Optional[str] = None,
) -> str
```

**Workflow**:
1. Accepts job role/level or explicit topic
2. Generates targeted search queries
3. Uses `recent_google_search` tool with date restrictions
4. Synthesizes findings into structured report
5. Saves to `research_report.txt`

**Output**: Text report with sources, best practices, and industry consensus

**Configuration**:
- `GOOGLE_API_KEY`: Google Custom Search API key
- `GOOGLE_CSE_ID`: Custom Search Engine ID
- `RECENT_MONTHS`: Default recency window (default: 6)
- `AGENT_MAX_ITERATIONS`: Maximum agent iterations (default: 8)

---

### Agent 2: Question Generator (`agent_question_generator.py`)

**Purpose**: Transforms research into 5 structured, role-specific take-home assignments.

**Technology**:
- LangChain with ChatOpenAI
- JSON Schema-based structured output
- Korean/English language support

**Key Functions**:
```python
def run_question_generator(
    job_role: str,
    job_level: str = "Senior",
    company_name: str = "Myrealtrip OTA Company",
    input_path: str = "research_report.txt",
    output_path: str = "assignments.json",
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    language: str = "Korean",
    markdown_preview_path: Optional[str] = None,
) -> str
```

**Workflow**:
1. Reads research report
2. Generates 5 unique assignments aligned with OTA business context
3. Each assignment includes:
   - Title, mission, summary
   - Technical requirements
   - Deliverables
   - AI usage guidelines
   - Evaluation criteria
   - Timeline
   - Discussion questions
   - **Dataset specifications** (columns, types, record count)
   - **Starter code metadata** (language, filename, description)
4. Validates against JSON schema
5. Sanitizes output (removes non-Korean/ASCII characters)
6. Saves as `assignments.json` and `assignments.md` (preview)

**Output Schema**:
```json
{
  "company": "string",
  "job_role": "string",
  "job_level": "string",
  "assignments": [
    {
      "id": "string",
      "title": "string",
      "mission": "string",
      "summary": "string",
      "requirements": ["string"],
      "deliverables": ["string"],
      "ai_guidelines": ["string"],
      "evaluation": ["string"],
      "timeline": "string",
      "discussion_questions": ["string"],
      "datasets": [
        {
          "name": "string",
          "description": "string",
          "format": "csv|json",
          "records": 10-2000,
          "filename": "string",
          "columns": [
            {
              "name": "string",
              "type": "string|integer|float|boolean|date|datetime|category",
              "description": "string",
              "choices": ["string"] // optional
            }
          ]
        }
      ],
      "starter_code": {
        "language": "string",
        "filename": "string",
        "description": "string"
      }
    }
  ]
}
```

---

### Agent 3: Data Provider (`agent_data_provider.py`)

**Purpose**: Generates synthetic datasets based on assignment specifications.

**Technology**:
- Faker library for realistic fake data
- Pandas for CSV generation
- JSON file generation

**Key Functions**:
```python
def run_data_provider(
    assignments_path: str = "assignments.json",
    output_dir: str = "datasets",
    language: str = "Korean",
) -> List[Path]
```

**Workflow**:
1. Parses `assignments.json`
2. For each assignment's dataset specifications:
   - Creates appropriate filename
   - Generates N records (10-5000) with Faker
   - Respects column types and choices
   - Outputs as CSV or JSON
3. Updates `assignments.json` with file paths and download links

**Data Generation Logic**:
- `string`: Random word
- `text`: Random sentence
- `integer`: Random int (0-1000)
- `float`: Random float (0-1000)
- `boolean`: Random True/False
- `date`: Random date this year
- `datetime`: Random datetime this year
- `category`/`choices`: Random selection from predefined list

**Output**: CSV/JSON files in `datasets/` directory

---

### Agent 4: Starter Code Generator (`agent_starter_code.py`)

**Purpose**: Creates minimal, role-appropriate starter code templates for each assignment.

**Technology**:
- LangChain with ChatOpenAI
- Multi-language support (Kotlin, Swift, Python, TypeScript, Java, Go, etc.)
- Korean comments with proper language syntax

**Key Functions**:
```python
def run_starter_code_generator(
    assignments_path: str = "assignments.json",
    assignment_id: Optional[str] = None,
    output_dir: str = "starter_code",
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    myrealtrip_url: str = "https://www.myrealtrip.com/",
) -> Dict[str, Path]
```

**Workflow**:
1. Reads assignment specifications
2. For each assignment:
   - Analyzes requirements and dataset structure
   - Generates language-appropriate boilerplate
   - Includes model/DTO definitions based on dataset preview
   - Adds Korean comments explaining structure
   - Handles API mocking (no real Myrealtrip API)
3. Saves to `starter_code/` directory
4. Updates `assignments.json` with file paths

**Language Extensions**:
```python
LANGUAGE_EXTENSION = {
    "kotlin": "kt",
    "swift": "swift",
    "python": "py",
    "typescript": "ts",
    "javascript": "js",
    "java": "java",
    "go": "go",
    "dart": "dart",
    # ...
}
```

**Output**: Language-specific starter files with Korean documentation

---

### Agent 5: Web Builder (`agent_web_builder.py`)

**Purpose**: Generates a professional, interactive candidate portal (HTML page).

**Technology**:
- Pure Python HTML generation (no templates)
- Embedded CSS (inline styles)
- Vanilla JavaScript for tab interactivity

**Key Functions**:
```python
def run_web_builder(
    assignments_path: str = "assignments.json",
    research_summary_path: Optional[str] = None,
    output_html: str = "index.html",
    language: str = "Korean",
    title: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    starter_dir: Optional[str] = None,
) -> Path
```

**Workflow**:
1. Loads `assignments.json`
2. Constructs HTML structure with:
   - **Sticky header** with Myrealtrip logo and navigation
   - **Hero section** with job role/level and CTA buttons
   - **Intro panels**: North Star vision, Product Engineer culture, AI usage guidelines
   - **Assignment tabs** (JavaScript-powered, accessible)
   - Each assignment card displays:
     - Title, summary, mission
     - Technical requirements
     - Deliverables
     - Dataset downloads with metadata
     - Starter code download
     - Discussion questions
   - **Apply section** with CTA
   - **Footer** with copyright
3. Includes inline CSS for modern design
4. Adds JavaScript for tab switching and keyboard navigation

**HTML Structure**:
```html
<!DOCTYPE html>
<html lang='ko'>
<head>
  <meta charset='UTF-8' />
  <title>Myrealtrip Take-Home Portal</title>
  <style>/* Embedded CSS */</style>
</head>
<body>
  <header class='page-header'>...</header>
  <main class='layout'>
    <section class='hero-section'>...</section>
    <section class='intro-panels'>...</section>
    <section class='assignments-section'>
      <div class='assignments-tabs' data-tabs>
        <div class='assignments-tabs__list' role='tablist'>...</div>
        <div class='assignments-tabs__panels'>...</div>
      </div>
    </section>
    <section class='apply-section'>...</section>
  </main>
  <footer class='page-footer'>...</footer>
  <script>/* Tab switching logic */</script>
</body>
</html>
```

**Design Features**:
- Responsive layout (max-width: 1200px)
- Myrealtrip brand colors (deep blue, teal, orange)
- Sticky header for navigation
- Accessible tab component (ARIA roles)
- Clean, professional aesthetics

**Output**: `index.html` (self-contained, no external dependencies)

---

### Agent 6: Web Designer (`agent_web_designer.py`)

**Purpose**: (Optional) Generates advanced CSS styling based on current web design trends.

**Technology**:
- LangChain with ChatOpenAI
- Google Custom Search for design research
- JSON-based output with CSS, design notes, and color palette

**Key Functions**:
```python
def run_web_designer(
    html_path: str = "index.html",
    css_output: str = "styles.css",
    notes_output: str = "design_notes.md",
    language: str = "Korean",
    model: Optional[str] = None,
    temperature: Optional[float] = None,
) -> Dict[str, str]
```

**Workflow**:
1. Reads generated HTML
2. Searches for latest design trends (last 3 months)
3. Analyzes HTML structure
4. Generates:
   - **CSS**: Complete stylesheet with:
     - Google Fonts import
     - CSS variables (colors, shadows, spacing)
     - Base styles & reset
     - Component styles (BEM methodology)
     - Responsive media queries
     - Dark mode (optional)
   - **Design summary**: Korean documentation of design decisions
   - **Accessibility notes**: WCAG 2.1 AA compliance checklist
   - **Color palette**: 7 hex codes for brand/neutral/state colors

**Output**:
- `styles.css`: External stylesheet (replaces inline CSS if used)
- `design_notes.md`: Design rationale and guidelines

**Note**: Currently, the Web Builder generates inline CSS, so this agent is optional.

---

## Orchestration Layer

### Main Orchestrator (`main_orchestrator.py`)

**Purpose**: Coordinates all agents in a single execution pipeline.

**Key Functions**:
```python
def orchestrate(args) -> None
```

**Workflow**:
1. **Planning Phase**: Displays execution plan with model assignments
2. **Step 1**: Research (unless `--skip-research`)
3. **Step 2**: Question generation (unless `--skip-questions`)
4. **Step 3**: Data provider (unless `--skip-datasets`)
5. **Step 4**: Starter code (unless `--skip-starter`)
6. **Step 5**: Web builder (unless `--skip-builder`)
7. **Step 6**: Web designer (if `--with-designer`)
8. **Completion**: Reports output locations

**Command-Line Interface**:
```bash
python main_orchestrator.py \
  --job-role "iOS Developer" \
  --job-level "Mid-level" \
  --language Korean \
  --model deepseek/deepseek-chat-v3.1 \
  --with-designer
```

**Key Arguments**:
- `--job-role`: Target role (e.g., "iOS Developer", "Backend Engineer")
- `--job-level`: Junior, Mid-level, Senior, Principal
- `--language`: Korean, English, etc.
- `--company-name`: Company name (default: "Myrealtrip OTA Company")
- `--topic`: Research topic override
- `--model`: Default model for all agents
- Per-agent model overrides: `--research-model`, `--question-model`, `--starter-model`, etc.
- Skip flags: `--skip-research`, `--skip-questions`, etc.
- `--with-designer`: Enable optional design agent
- `--output-root`: Base directory for all outputs

**Model Resolution**:
```
Step-specific model > Global --model > OPENAI_MODEL env var > default
```

**Error Handling**:
- Validates file dependencies before each step
- Provides clear error messages
- Non-blocking errors (agents can fail independently)

---

## Data Flow

### Sequential Pipeline Flow

```
┌─────────────────────┐
│  Input: Job Spec    │
│  - Role             │
│  - Level            │
│  - Language         │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────────────────────────────┐
│ Agent 1: Researcher                              │
│ - Searches web for best practices                │
│ - Generates research_report.txt                  │
└──────────┬───────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────┐
│ Agent 2: Question Generator                      │
│ - Reads research_report.txt                      │
│ - Generates 1 assignment                         │
│ - Defines dataset schemas & starter code specs   │
│ - Outputs assignments.json + assignments.md      │
└──────────┬───────────────────────────────────────┘
           │
           ├──────────────┬──────────────────┐
           │              │                  │
           ▼              ▼                  ▼
┌──────────────┐  ┌────────────────┐  ┌──────────────┐
│ Agent 3:     │  │ Agent 4:       │  │ Agent 5:     │
│ Data         │  │ Starter Code   │  │ Web Builder  │
│ Provider     │  │ Generator      │  │              │
└──────┬───────┘  └────────┬───────┘  └──────┬───────┘
       │                   │                  │
       │ datasets/*.csv    │ starter_code/*   │ index.html
       │                   │                  │
       └───────────────────┴──────────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │ Optional: Agent 6            │
            │ Web Designer                 │
            │ - styles.css                 │
            │ - design_notes.md            │
            └──────────────────────────────┘
```

### Data Dependencies

| Agent              | Reads                     | Writes                                  |
|--------------------|---------------------------|-----------------------------------------|
| Researcher         | (external APIs)           | `research_report.txt`                   |
| Question Generator | `research_report.txt`     | `assignments.json`, `assignments.md`    |
| Data Provider      | `assignments.json`        | `datasets/*.{csv,json}`, updates JSON   |
| Starter Code       | `assignments.json`, datasets | `starter_code/*`, updates JSON       |
| Web Builder        | `assignments.json`, research | `index.html`                         |
| Web Designer       | `index.html`              | `styles.css`, `design_notes.md`         |

---

## Technology Stack

### Core Dependencies

**Python Environment**:
- Python 3.10+ (3.11 recommended)

**LLM & AI Framework**:
```python
langchain>=0.2.14          # Agent framework
langchain-openai>=0.1.22   # OpenAI/OpenRouter integration
langchain-community>=0.2.11 # Community tools (Google Search)
langhub>=0.1.21           # Prompt templates
```

**Data Processing**:
```python
pandas>=2.2.2              # CSV generation and processing
Faker>=25.3.0              # Synthetic data generation
```

**External APIs**:
```python
google-api-python-client>=2.143.0  # Google Custom Search
requests>=2.31.0                    # HTTP requests
```

**Configuration**:
```python
python-dotenv>=1.0.1       # Environment variable management
```

### LLM Providers

**Supported Providers**:
1. **OpenAI** (default)
   - Models: `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`
   - Configuration: `OPENAI_API_KEY`

2. **OpenRouter** (multi-model gateway)
   - Access to 100+ models (DeepSeek, Qwen, Claude, etc.)
   - Configuration:
     ```env
     OPENAI_API_KEY=sk-or-v1-...
     OPENAI_BASE_URL=https://openrouter.ai/api/v1
     OPENROUTER_SITE_URL=https://your-site.com
     OPENROUTER_APP_NAME=MRT Take-Home Generator
     ```
   - Free models available (e.g., `deepseek/deepseek-chat-v3.1:free`)

### External Services

**Google Custom Search API**:
- Purpose: Web research for trends and best practices
- Setup:
  1. Create Custom Search Engine at https://programmablesearchengine.google.com/
  2. Enable Custom Search JSON API in Google Cloud Console
  3. Obtain API key and Search Engine ID (CX)
- Configuration: `GOOGLE_API_KEY`, `GOOGLE_CSE_ID`

---

## Configuration & Environment

### Environment Variables

**Required**:
```env
# OpenAI/OpenRouter
OPENAI_API_KEY=sk-...                  # Required for all LLM operations

# Google Custom Search (for research)
GOOGLE_API_KEY=AIza...                 # Required for Agent 1
GOOGLE_CSE_ID=abc123...                # Required for Agent 1
```

**Optional**:
```env
# LLM Configuration
OPENAI_MODEL=gpt-4o-mini               # Default model (default: gpt-4o-mini)
OPENAI_TEMPERATURE=0.7                 # Sampling temperature (default: varies by agent)
OPENAI_BASE_URL=https://...            # Custom API endpoint (for OpenRouter)
OPENAI_API_BASE=https://...            # Alternative base URL variable

# OpenRouter Specific
OPENROUTER_SITE_URL=https://...        # Attribution header
OPENROUTER_APP_NAME=...                # Attribution header

# Agent Configuration
RECENT_MONTHS=6                        # Google Search recency window (default: 6)
AGENT_MAX_ITERATIONS=8                 # ReAct agent max steps (default: 8)
```

### Environment Profiles

**Multiple Environments**:
```bash
# Development
python agent_researcher.py --profile dev

# Production
python agent_researcher.py --profile prod

# Custom
python agent_researcher.py --env-file .env.staging
```

**File Hierarchy** (later overrides earlier):
1. `.env` (base)
2. `--env-file` (if provided)
3. `--profile` → `.env.{profile}`
4. CLI arguments (highest priority)

---

## Bulk Processing

### Sheet Bulk Runner (`sheet_bulk_runner.py`)

**Purpose**: Generate assignments for multiple roles in parallel from Google Sheets configuration.

**Key Features**:
- Google Sheets integration (live URL or exported CSV)
- Concurrent execution with configurable worker pool
- Per-row configuration with global defaults
- External link detection (skip rows with existing assignments)
- Result summary export

**Google Sheet Format**:

| Column           | Required | Description                                    |
|------------------|----------|------------------------------------------------|
| `team`           | Yes      | Team name (e.g., "iOS Developer")             |
| `level`          | Yes      | Job level (e.g., "Mid-level")                 |
| `language`       | No       | Korean, English (default: Korean)             |
| `model`          | No       | Model override for this row                   |
| `research_model` | No       | Research agent model override                 |
| `question_model` | No       | Question generator model override             |
| `data_model`     | No       | Data provider model override                  |
| `starter_model`  | No       | Starter code model override                   |
| `builder_model`  | No       | Web builder model override                    |
| `designer_model` | No       | Web designer model override                   |
| `with_designer`  | No       | 1/true/yes to enable designer                 |
| `topic`          | No       | Research topic override                       |
| `external_link`  | No       | URL to existing assignment (skips generation) |
| `job_role`       | No       | Role override (inferred from team if omitted) |

**Command-Line Usage**:
```bash
# From Google Sheet URL
python sheet_bulk_runner.py \
  --sheet-url "https://docs.google.com/spreadsheets/d/ABC123/edit#gid=0" \
  --output-root bulk_output \
  --max-workers 4 \
  --default-model deepseek/deepseek-chat-v3.1 \
  --with-designer \
  --summary results.json

# From exported CSV
python sheet_bulk_runner.py \
  --sheet-csv config.csv \
  --output-root bulk_output
```

**Workflow**:
1. Fetches Google Sheet as CSV (or reads local CSV)
2. Normalizes column names
3. Iterates rows, skipping:
   - Empty rows
   - Rows with `external_link` set
4. For each valid row:
   - Generates output folder name (e.g., `ios_dev_mid_ko`)
   - Constructs CLI arguments for `main_orchestrator`
   - Submits to worker pool
5. Executes pipelines concurrently (default: min(8, CPU_COUNT*2))
6. Collects results (completed/failed)
7. Exports summary JSON (if `--summary` provided)

**Output Structure**:
```
bulk_output/
├── ios_dev_mid_ko/
│   ├── research_report.txt
│   ├── assignments.json
│   ├── assignments.md
│   ├── datasets/
│   │   ├── OTA-IOS-001_01.csv
│   │   └── ...
│   ├── starter_code/
│   │   ├── OTA-IOS-001_starter.swift
│   │   └── ...
│   ├── index.html
│   ├── styles.css (if --with-designer)
│   └── design_notes.md (if --with-designer)
├── backend_dev_sr_en/
│   └── ...
└── results.json (summary)
```

**Folder Naming Logic**:
- Tokenizes role, level, language
- Applies normalization maps (e.g., "developer" → "dev", "senior" → "sr")
- Joins with underscores
- Example: "iOS Developer" + "Mid-level" + "Korean" → `ios_dev_mid_ko`

**Error Handling**:
- Failed rows don't block others
- Errors logged with row index and message
- Summary JSON contains `status: "completed" | "failed"` and `error` field

---

## Output Artifacts

### Per-Job-Role Bundle

Each generated bundle contains:

**1. Research Report** (`research_report.txt`)
- Synthesized web research
- Source URLs
- Industry consensus and trends
- Best practices for the role/level

**2. Structured Assignments** (`assignments.json`)
- 5 unique assignments
- Complete with requirements, evaluation criteria, datasets, starter code
- Machine-readable format for automation

**3. Assignment Preview** (`assignments.md`)
- Human-readable Markdown version
- Organized by assignment with sections

**4. Datasets** (`datasets/`)
- CSV or JSON files
- Realistic synthetic data (Faker-generated)
- Seeded for reproducibility (seed=42)
- File names match assignment IDs

**5. Starter Code** (`starter_code/`)
- Language-specific templates
- Korean comments
- Model/DTO definitions from datasets
- Basic structure to kickstart candidates

**6. Candidate Portal** (`index.html`)
- Self-contained HTML page
- Embedded CSS and JavaScript
- Professional, accessible UI
- Downloadable datasets and starter code
- Call-to-action for applications

**7. Design Assets** (optional, if `--with-designer`)
- `styles.css`: External stylesheet with modern design system
- `design_notes.md`: Design rationale and accessibility checklist

### Example Output Structure

```
mrt-tech-test/
├── research_report.txt
├── assignments.json
├── assignments.md
├── datasets/
│   ├── OTA-IOS-001_01_hotel_search.csv
│   ├── OTA-IOS-002_01_booking_history.json
│   ├── OTA-IOS-003_01_reviews.csv
│   └── ...
├── starter_code/
│   ├── OTA-IOS-001_starter.swift
│   ├── OTA-IOS-002_starter.swift
│   └── ...
├── index.html
├── styles.css
└── design_notes.md
```

---

## Deployment

### Netlify Configuration

**File**: `netlify.toml`

```toml
[build]
  publish = "."
  command = ""

[context.production.environment]
  PYTHON_VERSION = "3.11"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
  force = false
```

**Deployment Steps**:

1. **Prerequisites**:
   - Netlify account
   - Netlify CLI installed (`npm install -g netlify-cli`)

2. **Initialize Site**:
   ```bash
   netlify init
   ```

3. **Deploy Preview**:
   ```bash
   netlify deploy
   ```

4. **Deploy Production**:
   ```bash
   netlify deploy --prod
   ```

**What Gets Deployed**:
- `index.html` (candidate portal)
- `styles.css` (if generated)
- `datasets/` directory (downloadable assets)
- `starter_code/` directory (downloadable templates)

**Access**:
- Netlify provides a public URL (e.g., `https://mrt-takehome.netlify.app`)
- Candidates can view assignments and download resources

**Note**: The platform itself (Python agents) is NOT deployed. Only the generated outputs (HTML portal and assets) are hosted.

---

## Use Cases & Workflows

### Workflow 1: Single Role Generation

**Scenario**: Generate assignments for a Mid-level iOS Developer position.

```bash
# Step 1: Set up environment
cp .env.example .env
# Edit .env with API keys

# Step 2: Run orchestrator
python main_orchestrator.py \
  --job-role "iOS Developer" \
  --job-level "Mid-level" \
  --language Korean \
  --model gpt-4o-mini \
  --with-designer

# Step 3: Review outputs
open index.html

# Step 4: Deploy to Netlify
netlify deploy --prod
```

**Outputs**:
- 5 iOS-specific assignments (SwiftUI, Combine, async/await, etc.)
- Sample data (hotels, bookings, reviews)
- Swift starter templates
- Professional portal

---

### Workflow 2: Bulk Generation from Google Sheets

**Scenario**: Generate assignments for 10 different roles (iOS, Android, Backend, Frontend, Data Engineer) at various levels.

**Step 1: Prepare Google Sheet**:

| team            | level       | language | model                        | with_designer |
|-----------------|-------------|----------|------------------------------|---------------|
| iOS Developer   | Mid-level   | Korean   | gpt-4o-mini                  | true          |
| iOS Developer   | Senior      | Korean   | gpt-4o                       | true          |
| Backend Engineer| Mid-level   | English  | deepseek/deepseek-chat-v3.1  | false         |
| Frontend Engineer| Senior     | Korean   | gpt-4o-mini                  | true          |
| Data Engineer   | Principal   | English  | gpt-4o                       | true          |

**Step 2: Run Bulk Generator**:
```bash
python sheet_bulk_runner.py \
  --sheet-url "https://docs.google.com/spreadsheets/d/YOUR_ID/edit#gid=0" \
  --output-root bulk_output \
  --max-workers 4 \
  --company-name "Myrealtrip" \
  --summary results.json
```

**Step 3: Review Results**:
```bash
cat results.json
# Check completed vs failed rows

ls bulk_output/
# ios_dev_mid_ko/
# ios_dev_sr_ko/
# backend_eng_mid_en/
# ...
```

**Step 4: Deploy Multiple Portals**:
```bash
# Option 1: Deploy each individually
cd bulk_output/ios_dev_mid_ko
netlify deploy --prod

# Option 2: Create index page linking to all
# (custom script to generate master index.html)
```

---

### Workflow 3: Incremental Generation (Step-by-Step)

**Scenario**: Generate components separately for review/editing.

```bash
# Step 1: Research
python agent_researcher.py \
  --job-role "Backend Engineer" \
  --job-level "Senior" \
  --output research_report.txt

# [Review/edit research_report.txt]

# Step 2: Generate Questions
python agent_question_generator.py "Backend Engineer" \
  --level Senior \
  --input research_report.txt \
  --output assignments.json

# [Review/edit assignments.json]

# Step 3: Generate Datasets
python agent_data_provider.py \
  --input assignments.json \
  --output-dir datasets

# Step 4: Generate Starter Code
python agent_starter_code.py \
  --input assignments.json \
  --output-dir starter_code

# Step 5: Build Web Page
python agent_web_builder.py \
  --assignments assignments.json \
  --research research_report.txt \
  --output index.html

# [Optional] Step 6: Apply Design
python agent_web_designer.py \
  --html index.html \
  --css styles.css \
  --notes design_notes.md
```

**Advantages**:
- Human review at each stage
- Manual adjustments possible
- Debug individual agents

---

### Workflow 4: Using OpenRouter (Free Models)

**Scenario**: Minimize costs by using free models from OpenRouter.

**Setup**:
```env
# .env
OPENAI_API_KEY=sk-or-v1-YOUR_OPENROUTER_KEY
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_SITE_URL=https://myrealtrip.com
OPENROUTER_APP_NAME=MRT Take-Home Generator
OPENAI_MODEL=deepseek/deepseek-chat-v3.1:free
```

**Run**:
```bash
python main_orchestrator.py \
  --job-role "Data Engineer" \
  --job-level "Principal" \
  --model deepseek/deepseek-chat-v3.1:free
```

**Alternative Free Models**:
- `qwen/qwen3-coder:free` (good for code)
- `x-ai/grok-4-fast:free` (fast responses)
- `deepseek/deepseek-r1-0528-qwen3-8b:free` (reasoning)

---

## Advanced Topics

### Model Selection Strategy

**By Agent**:

| Agent              | Recommended Model       | Temperature | Reasoning                          |
|--------------------|-------------------------|-----------|------------------------------------|
| Researcher         | gpt-4o-mini, deepseek   | 0.0       | Needs factual accuracy             |
| Question Generator | gpt-4o, deepseek        | 0.35      | Structured output, some creativity |
| Data Provider      | (no LLM)                | N/A       | Rule-based generation              |
| Starter Code       | gpt-4o-mini, qwen-coder | 0.2       | Code generation, low randomness    |
| Web Builder        | (no LLM)                | N/A       | Template-based HTML generation     |
| Web Designer       | gpt-4o, claude          | 0.1       | CSS precision, design knowledge    |

**Cost Optimization**:
- Use `gpt-4o-mini` for all except critical agents
- Use OpenRouter free models for testing
- Use `gpt-4o` only for Question Generator (most critical)

**Quality Optimization**:
- Use `gpt-4o` or `claude-3.5-sonnet` for all agents
- Higher temperature for Question Generator (0.5-0.7) for diversity
- Lower temperature for Starter Code (0.0-0.2) for determinism

---

### Customization Points

**1. Prompt Engineering**:
- Edit prompts in each agent file
- Adjust system messages for company-specific tone
- Add domain-specific requirements

**2. Dataset Schemas**:
- Modify JSON schema in `agent_question_generator.py`
- Add custom column types in `agent_data_provider.py`

**3. Starter Code Templates**:
- Add language support in `LANGUAGE_EXTENSION` dict
- Adjust code generation prompts for frameworks

**4. Web Design**:
- Edit `_build_html()` in `agent_web_builder.py`
- Modify CSS variables for branding
- Add custom sections or components

**5. Bulk Processing**:
- Extend Google Sheet columns for more metadata
- Customize folder naming in `_compose_output_folder()`

---

### Monitoring & Debugging

**Logging**:
- LangChain agents have `verbose=True` for detailed logs
- Each agent prints progress messages with timestamps

**Common Issues**:

1. **OpenAI Rate Limits**:
   - Symptom: `RateLimitError`
   - Solution: Use OpenRouter, add delays between agents, or upgrade OpenAI tier

2. **Google Search Quota**:
   - Symptom: 429 errors from Google CSE
   - Solution: Increase quota in Google Cloud Console, or skip research with `--skip-research`

3. **JSON Parsing Errors**:
   - Symptom: `ValueError: Failed to parse assignments JSON`
   - Solution: Check `assignments.raw.json` for malformed output, adjust temperature, or use more capable model

4. **Missing Files**:
   - Symptom: `FileNotFoundError`
   - Solution: Ensure previous agent completed successfully, or use `--skip-*` flags

**Debug Mode**:
```bash
# Enable verbose LangChain logs
export LANGCHAIN_VERBOSE=1

# Use OpenAI debug mode
export OPENAI_LOG=debug

# Run single agent with verbose output
python agent_question_generator.py "iOS Developer" --model gpt-4o
```

---

## Performance & Scalability

### Execution Times

**Single Role** (approximate):
- Researcher: 1-2 minutes (depends on Google Search)
- Question Generator: 30-60 seconds (depends on LLM)
- Data Provider: 5-10 seconds (local generation)
- Starter Code: 30-90 seconds (5 files, depends on LLM)
- Web Builder: 1-2 seconds (local generation)
- Web Designer: 20-40 seconds (depends on LLM)

**Total**: ~3-5 minutes per role

**Bulk Generation** (10 roles, 4 workers):
- Sequential: ~30-50 minutes
- Parallel (4 workers): ~10-15 minutes

### Cost Estimation

**OpenAI Pricing** (as of 2024):

| Model        | Input (per 1M tokens) | Output (per 1M tokens) | Est. Cost per Role |
|--------------|-----------------------|------------------------|--------------------|
| gpt-4o-mini  | $0.15                 | $0.60                  | $0.02-0.05         |
| gpt-4o       | $2.50                 | $10.00                 | $0.20-0.40         |

**Google Custom Search**:
- Free tier: 100 queries/day
- Paid: $5 per 1,000 queries
- Est. usage: 5-10 queries per role

**Total Cost per Role**:
- Economy (gpt-4o-mini): ~$0.02-0.05
- Premium (gpt-4o): ~$0.20-0.40

**Bulk Generation (100 roles)**:
- Economy: ~$2-5
- Premium: ~$20-40

---

## Security & Best Practices

### API Key Management

**Never commit to Git**:
```bash
# .gitignore
.env
.env.*
!.env.example
```

**Use environment-specific profiles**:
- `.env.dev` for development (free models, low quotas)
- `.env.prod` for production (paid models, high quality)

**Rotate keys regularly**:
- OpenAI: Regenerate every 90 days
- Google: Use service accounts for production

### Data Privacy

**Synthetic Data Only**:
- All datasets are generated with Faker (no real data)
- Safe for public sharing

**Prompt Safety**:
- Don't include PII or sensitive company info in prompts
- Review research reports before sharing externally

### Code Quality

**Type Safety**:
- Use type hints throughout codebase
- Run `mypy` for static type checking

**Testing**:
```bash
# Unit tests (add as needed)
pytest tests/

# Integration test
python main_orchestrator.py --job-role "Test Role" --skip-research
```

**Linting**:
```bash
ruff check .
black .
```

---

## Future Enhancements

### Roadmap

**Phase 1: Core Stability** (Current)
- ✅ Multi-agent pipeline
- ✅ OpenRouter support
- ✅ Bulk generation
- ✅ Netlify deployment

**Phase 2: Candidate Experience**
- [ ] Online code editor integration (CodeSandbox, StackBlitz)
- [ ] Submission portal (form + GitHub integration)
- [ ] Automated evaluation agent (code review)

**Phase 3: Recruiter Tools**
- [ ] Dashboard for tracking submissions
- [ ] Comparison matrix for candidates
- [ ] Interview question generator from submissions

**Phase 4: Advanced Generation**
- [ ] Video explainer scripts (AI voiceover)
- [ ] Figma/Sketch design files generation
- [ ] Multi-language support (translate assignments)
- [ ] Real-time collaboration (candidates + reviewers)

**Phase 5: AI Evaluation**
- [ ] Automated code quality scoring
- [ ] Plagiarism detection (AI-generated vs human)
- [ ] Technical interview question generation based on code

---

## Conclusion

The **Myrealtrip Take-Home Assignment Generation Platform** represents a sophisticated, production-ready application of modern AI/LLM technologies for technical recruitment. Key strengths:

1. **Modularity**: Each agent is independent and replaceable
2. **Flexibility**: Supports multiple LLM providers, roles, languages
3. **Scalability**: Bulk generation with parallel execution
4. **Quality**: Structured outputs with validation
5. **Accessibility**: Professional, WCAG-compliant candidate portals
6. **Cost-Effective**: OpenRouter integration for free/cheap models

The architecture demonstrates best practices in:
- AI agent orchestration
- Prompt engineering
- Data generation
- Web development
- DevOps (environment management, deployment)

This platform can be adapted for any company's technical hiring process and extended with additional agents for specialized domains (ML Engineering, DevOps, Security, etc.).

---

## Appendix

### A. Complete Command Reference

**Researcher**:
```bash
python agent_researcher.py "topic" \
  --output research_report.txt \
  --model gpt-4o-mini \
  --temperature 0 \
  --recent-months 6 \
  --job-role "iOS Developer" \
  --job-level "Senior" \
  --profile prod
```

**Question Generator**:
```bash
python agent_question_generator.py "iOS Developer" \
  --level Senior \
  --company "Myrealtrip" \
  --input research_report.txt \
  --output assignments.json \
  --markdown assignments.md \
  --model gpt-4o \
  --temperature 0.35 \
  --language Korean \
  --profile prod
```

**Data Provider**:
```bash
python agent_data_provider.py \
  --input assignments.json \
  --output-dir datasets \
  --language Korean \
  --profile prod
```

**Starter Code**:
```bash
python agent_starter_code.py \
  --input assignments.json \
  --assignment-id OTA-IOS-001 \
  --output-dir starter_code \
  --model gpt-4o-mini \
  --temperature 0.2 \
  --myrealtrip-url https://www.myrealtrip.com/ \
  --profile prod
```

**Web Builder**:
```bash
python agent_web_builder.py \
  --assignments assignments.json \
  --research research_report.txt \
  --output index.html \
  --title "iOS Take-Home Portal" \
  --language Korean \
  --starter-dir starter_code \
  --profile prod
```

**Web Designer**:
```bash
python agent_web_designer.py \
  --html index.html \
  --css styles.css \
  --notes design_notes.md \
  --language Korean \
  --model gpt-4o \
  --temperature 0.1 \
  --profile prod
```

**Orchestrator**:
```bash
python main_orchestrator.py \
  --job-role "iOS Developer" \
  --job-level "Senior" \
  --language Korean \
  --company-name "Myrealtrip" \
  --topic "iOS take-home best practices 2024" \
  --model gpt-4o-mini \
  --research-model gpt-4o \
  --question-model gpt-4o \
  --starter-model qwen/qwen3-coder \
  --with-designer \
  --output-root output/ios_senior
```

**Bulk Runner**:
```bash
python sheet_bulk_runner.py \
  --sheet-url "https://docs.google.com/spreadsheets/d/ID/edit#gid=0" \
  --output-root bulk_output \
  --max-workers 4 \
  --default-model gpt-4o-mini \
  --with-designer \
  --company-name "Myrealtrip" \
  --summary results.json
```

---

### B. Environment Variable Reference

```env
# === Required ===
OPENAI_API_KEY=sk-...                    # OpenAI or OpenRouter API key
GOOGLE_API_KEY=AIza...                   # Google Custom Search API key
GOOGLE_CSE_ID=abc123...                  # Google Custom Search Engine ID

# === Optional: LLM Configuration ===
OPENAI_MODEL=gpt-4o-mini                 # Default model name
OPENAI_TEMPERATURE=0.7                   # Default temperature (0-2)
OPENAI_BASE_URL=https://...              # Custom API endpoint (for OpenRouter)
OPENAI_API_BASE=https://...              # Alternative base URL variable

# === Optional: OpenRouter ===
OPENROUTER_SITE_URL=https://...          # Attribution: your site URL
OPENROUTER_APP_NAME=...                  # Attribution: your app name

# === Optional: Agent Behavior ===
RECENT_MONTHS=6                          # Google Search recency window (1-12)
AGENT_MAX_ITERATIONS=8                   # ReAct agent max iterations (3-20)

# === Optional: Debugging ===
LANGCHAIN_VERBOSE=1                      # Enable LangChain verbose logs
OPENAI_LOG=debug                         # Enable OpenAI debug logs
```

---

### C. JSON Schema for assignments.json

See Agent 2 section for complete schema.

---

### D. Troubleshooting Guide

| Issue                          | Likely Cause                          | Solution                                    |
|--------------------------------|---------------------------------------|---------------------------------------------|
| `Missing required environment variable` | API key not set                      | Set `OPENAI_API_KEY` in `.env`              |
| `Rate limit exceeded`          | Too many API calls                    | Wait 1 minute, or upgrade OpenAI tier       |
| `Google API quota exceeded`    | Daily CSE limit hit                   | Wait until next day, or increase quota      |
| `Failed to parse assignments JSON` | LLM returned invalid JSON             | Try `gpt-4o` model, lower temperature       |
| `FileNotFoundError`            | Previous agent didn't run             | Run previous agent, or use `--skip-*` flag  |
| `Empty dataset generated`      | Invalid column specification          | Check `assignments.json` dataset schema     |
| `Starter code file empty`      | LLM failed to generate code           | Retry with different model, check logs      |
| `HTML rendering broken`        | Invalid HTML characters               | File a bug with reproduction steps          |

---

**Document Version**: 1.0  
**Last Updated**: November 12, 2025  
**Maintained By**: Myrealtrip Engineering Team

