"""
Flask Web Application for Tech Test Generator
Provides a web interface to generate tech assignments using CrewAI orchestrator.
"""

import os
import sys
import io
import json
import threading
import logging
import time
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory, Response, abort, send_file

# Suppress BrokenPipeError from CrewAI logging
logging.getLogger().addHandler(logging.NullHandler())
logging.captureWarnings(True)
logging.raiseExceptions = False

from crewai_working import generate_with_crewai
from agent_starter_code import run_starter_code_generator
from agent_web_designer import run_web_designer

app = Flask(__name__)

# Store generation status
generation_status = {}

# Agent definitions for UI (6 agents: Designer removed per user request)
AGENTS = [
    {"id": "pm", "name": "Product Manager", "icon": "👔", "role": "Team Leader & Coordinator"},
    {"id": "researcher", "name": "Research Analyst", "icon": "🔍", "role": "Industry Research"},
    {"id": "designer", "name": "Assignment Generator", "icon": "✏️", "role": "Challenge Creation"},
    {"id": "reviewer", "name": "QA Reviewer", "icon": "🔎", "role": "Quality Assurance"},
    {"id": "data", "name": "Data Provider", "icon": "📊", "role": "Dataset Generation"},
    {"id": "builder", "name": "Web Builder", "icon": "🌐", "role": "Portal Creation"},
    {"id": "styler", "name": "Web Designer", "icon": "🎨", "role": "Styling & Design"},
]


def _run_with_heartbeat(description, func, agent_label="Web Builder", emoji="🌐", interval=30):
    """Run a blocking function while emitting periodic heartbeat logs."""
    stop_event = threading.Event()
    start_time = time.time()

    def heartbeat():
        while not stop_event.wait(interval):
            elapsed = int(time.time() - start_time)
            minutes, seconds = divmod(elapsed, 60)
            print(
                f"{emoji} [{agent_label}] {description} (still working… {minutes:02d}:{seconds:02d} elapsed)",
                flush=True,
            )

    thread = threading.Thread(target=heartbeat, daemon=True)
    thread.start()
    try:
        return func()
    finally:
        stop_event.set()
        thread.join()


class LogCapture(io.StringIO):
    """Capture stdout/stderr and store in generation status."""
    
    def __init__(self, job_id):
        super().__init__()
        self.job_id = job_id
        self.buffer = []
        
    def write(self, text):
        if text and text.strip():
            # Clean the text before storing
            cleaned_text = self._clean_ansi(text)
            if cleaned_text.strip():
                self.buffer.append(cleaned_text)
                # Update generation status with cleaned log line
                if self.job_id in generation_status:
                    if 'logs' not in generation_status[self.job_id]:
                        generation_status[self.job_id]['logs'] = []
                    generation_status[self.job_id]['logs'].append(cleaned_text)
                    
                    # Update progress based on log content
                    self._update_progress_from_log(cleaned_text)
        return len(text)
    
    def _update_progress_from_log(self, text):
        """Update progress status based on log content."""
        if self.job_id not in generation_status:
            return
            
        text_lower = text.lower()
        
        # Update timestamp to show activity
        generation_status[self.job_id]['last_update'] = datetime.now().isoformat()
        
        # Detect which phase we're in based on logs and update agent status
        agent_status = generation_status[self.job_id].get('agent_status', {})

        def set_progress(label, agent_id=None):
            if agent_id:
                generation_status[self.job_id]['active_agent'] = agent_id
            if generation_status[self.job_id].get('progress') == label:
                return
            generation_status[self.job_id]['progress'] = label
        
        # PM phases
        if '[pm]' in text_lower and ('kick' in text_lower or 'project' in text_lower):
            set_progress('👔 PM initializing project...', 'pm')
            agent_status['pm'] = 'active'
        elif '[pm]' in text_lower and 'aligning' in text_lower:
            set_progress('💬 PM aligning on skills...', 'pm')
            agent_status['pm'] = 'active'
        elif '[pm]' in text_lower and 'final approval' in text_lower:
            set_progress('👔 PM giving final approval...', 'pm')
            agent_status['pm'] = 'completed'
        
        # Research Analyst
        elif '[research' in text_lower or 'google cse' in text_lower or 'launching google cse' in text_lower or 'investigating best practices' in text_lower:
            set_progress('🔍 Research Analyst investigating...', 'researcher')
            agent_status['researcher'] = 'active'
        elif 'research summary saved' in text_lower or 'research findings shared' in text_lower:
            set_progress('✅ Research summary shared with PM...', 'pm')
            agent_status['researcher'] = 'completed'
        
        # Assignment Generator / Designer
        elif '[designer' in text_lower or 'assignment generator' in text_lower or 'generating detailed assignments' in text_lower or 'crafting scenario' in text_lower:
            set_progress('📝 Assignment Generator crafting challenges...', 'designer')
            agent_status['designer'] = 'active'
        elif 'assignments generated' in text_lower or 'assignments ready' in text_lower:
            set_progress('✅ Assignments ready. Data Provider preparing datasets...')
            agent_status['designer'] = 'completed'
        
        # Data Provider  
        elif '[data provider]' in text_lower or 'creating datasets' in text_lower or 'reviewing data requirements' in text_lower:
            set_progress('📊 Data Provider creating datasets...', 'data')
            agent_status['data'] = 'active'
        elif 'datasets created' in text_lower or 'recommend generating these datasets' in text_lower:
            # Mark as active but not complete until "datasets created"
            if 'datasets created' in text_lower:
                set_progress('✅ Datasets ready. Web Builder preparing portal...', 'builder')
                agent_status['data'] = 'completed'
            else:
                agent_status['data'] = 'active'
        
        # Web Builder
        elif '[web builder]' in text_lower or 'building candidate portal' in text_lower:
            set_progress('🌐 Web Builder creating portal...', 'builder')
            agent_status['builder'] = 'active'
        elif 'portal built' in text_lower:
            set_progress('✅ Portal skeleton built. Web Designer styling...', 'styler')
            agent_status['builder'] = 'completed'
        
        # Web Designer
        elif '[web designer]' in text_lower or 'applying myrealtrip branding' in text_lower:
            set_progress('🎨 Web Designer styling portal...', 'styler')
            agent_status['styler'] = 'active'
        elif 'styling applied' in text_lower:
            set_progress('✅ Styling finalized. QA reviewing...', 'reviewer')
            agent_status['styler'] = 'completed'
        
        # QA Reviewer
        elif '[qa' in text_lower or 'final review' in text_lower or 'reviewing plan' in text_lower:
            set_progress('🔎 QA reviewing deliverables...', 'reviewer')
            agent_status['reviewer'] = 'active'
        elif 'approved' in text_lower and '[qa' in text_lower:
            # Stay active until final QA step
            if 'final review' in text_lower:
                 agent_status['reviewer'] = 'completed'
            else:
                 # Initial plan approval - still active in flow
                 pass
        
        # Update agent_status in generation_status
        if agent_status:
            generation_status[self.job_id]['agent_status'] = agent_status
    
    def flush(self):
        pass
    
    @staticmethod
    def _clean_ansi(text):
        """Remove ANSI color codes and box-drawing characters, keep only content."""
        import re
        
        # Remove ANSI escape sequences (color codes)
        text = re.sub(r'\x1b\[[0-9;]*m', '', text)
        text = re.sub(r'\[[\d;]+m', '', text)
        
        # Remove box-drawing characters
        box_chars = ['╭', '╮', '╯', '╰', '─', '│', '├', '┤', '┬', '┴', '┼', '═', '╠', '╣', '╦', '╩', '╬']
        for char in box_chars:
            text = text.replace(char, '')
        
        # Split into lines and filter
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                continue
            
            # Skip pure decoration lines
            if all(c in '─═│╭╮╯╰├┤┬┴┼ \t-_' for c in stripped):
                continue
            
            # Skip CrewAI box headers/footers
            if any(marker in stripped for marker in [
                'Crew Execution Started',
                'Crew Execution Completed',
                'Crew Failure',
                'Task Completion',
                'Task Failure',
                'Memory Retrieval',
                'Tool Args:',
                'ID:', 
                'Name:',
            ]) and len(stripped) < 50:
                continue
            
            # Extract actual content (remove leading/trailing decoration)
            content = stripped.strip('│├┤╭╮╰╯─═ \t')
            
            if content:
                cleaned_lines.append(content)
        
        result = '\n'.join(cleaned_lines)
        
        # Remove excessive blank lines
        result = re.sub(r'\n\n\n+', '\n\n', result)
        
        return result


def run_generation(job_id, job_role, job_level, language, model=None):
    """Run the orchestrator in a background thread."""
    global generation_status
    
    print(f"[GENERATION] Thread started for job_id={job_id}", flush=True)
    print(f"[GENERATION] Current generation_status keys: {list(generation_status.keys())}", flush=True)
    if model:
        print(f"[GENERATION] Requested model: {model}", flush=True)
    
    try:
        # Ensure status exists (defensive - should be initialized already)
        if job_id not in generation_status:
            print(f"[GENERATION] WARNING: job_id {job_id} not in status, initializing now", flush=True)
            generation_status[job_id] = {
                "status": "running",
                "progress": "Starting...",
                "output_dir": None,
                "error": None,
                "logs": [],
                "started_at": datetime.now().isoformat()
            }
        
        # Update status to running
        generation_status[job_id]["status"] = "running"
        generation_status[job_id]["progress"] = "Initializing agents..."
        print(f"[GENERATION] Status updated to running for job_id={job_id}", flush=True)
        
        # Capture stdout and stderr
        log_capture = LogCapture(job_id)
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        # Redirect stdout/stderr to capture logs
        sys.stdout = log_capture
        sys.stderr = log_capture
        
        # Create output directory
        output_root = Path("output")
        output_root.mkdir(exist_ok=True)
        
        # Create job-specific directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_role = job_role.lower().replace(" ", "_")
        safe_level = job_level.lower().replace(" ", "_").replace("-", "_")
        job_dir = output_root / f"{safe_role}_{safe_level}_{timestamp}"
        job_dir.mkdir(parents=True, exist_ok=True)
        
        generation_status[job_id]["progress"] = "PM initializing team..."
        generation_status[job_id]["active_agent"] = "pm"
        generation_status[job_id]["agent_status"] = {agent["id"]: "pending" for agent in AGENTS}
        generation_status[job_id]["agent_status"]["pm"] = "active"
        generation_status[job_id]["last_update"] = datetime.now().isoformat()
        
        # Run CrewAI team collaboration
        generation_status[job_id]["progress"] = "🎯 Starting CrewAI team collaboration..."
        generation_status[job_id]["last_update"] = datetime.now().isoformat()
        
        print(f"[GENERATION] Starting CrewAI for job_id={job_id}", flush=True)
        result = generate_with_crewai(
            job_role=job_role,
            job_level=job_level,
            language=language,
            output_root=str(job_dir),
            model=model
        )
        print(f"[GENERATION] CrewAI completed for job_id={job_id}", flush=True)
        
        # Post-processing: Generate starter code and styling
        assignments_path = Path(job_dir) / "assignments.json"
        html_path = Path(job_dir) / "index.html"
        
        if assignments_path.exists():
            generation_status[job_id]["progress"] = "Generating starter code..."
            print("🛠️ [System] Generating starter code bundle for the portal...", flush=True)
            try:
                _run_with_heartbeat(
                    "Packaging starter code bundle for the portal",
                    lambda: run_starter_code_generator(
                        assignments_path=str(assignments_path),
                        output_dir=str(Path(job_dir) / "starter_code"),
                        model=model
                    ),
                    agent_label="Web Builder",
                    emoji="🌐",
                    interval=25
                )
                print("✅ [System] Starter code package ready.", flush=True)
            except Exception as e:
                print(f"⚠️  Starter code error: {e}", flush=True)
        
        # Rebuild portal now that starter code metadata is updated
        if assignments_path.exists():
            generation_status[job_id]["progress"] = "Rebuilding portal with starter code..."
            print("🌐 [Web Builder] Building candidate portal with downloadable starter code...", flush=True)
            try:
                _run_with_heartbeat(
                    "Assembling candidate portal with updated assets",
                    lambda: run_web_builder(
                        assignments_path=str(assignments_path),
                        research_summary_path=str(Path(job_dir) / "research_report.txt"),
                        output_html=str(Path(job_dir) / "index.html"),
                        language=language,
                        starter_dir=str(Path(job_dir) / "starter_code")
                    ),
                    agent_label="Web Builder",
                    emoji="🌐",
                    interval=25
                )
                print("✅ [Web Builder] Portal built with starter code links.", flush=True)
            except Exception as e:
                print(f"⚠️ [Web Builder] Portal generation error: {e}", flush=True)
        
        if html_path.exists():
            generation_status[job_id]["progress"] = "Applying custom styling..."
            print("🎨 [Web Designer] Applying Myrealtrip branding and layout polish...", flush=True)
            try:
                _run_with_heartbeat(
                    "Applying custom portal styling and layout polish",
                    lambda: run_web_designer(
                        html_path=str(html_path),
                        css_output=str(Path(job_dir) / "styles.css"),
                        notes_output=str(Path(job_dir) / "design_notes.md"),
                        language=language
                    ),
                    agent_label="Web Designer",
                    emoji="🎨",
                    interval=25
                )
                print("✅ [Web Designer] Styling refinements applied.", flush=True)
            except Exception as e:
                print(f"⚠️  Web designer error: {e}", flush=True)
        
        # Success - Always check if portal exists after generation
        portal_path = Path(job_dir) / "index.html"
        portal_exists = portal_path.exists()
        
        if portal_exists:
            print("🕒 [System] Final assets ready. Publishing portal link...", flush=True)
            generation_status[job_id].update({
                "status": "completed",
                "progress": "✅ Tech test complete! Portal ready for candidates.",
                "output_dir": str(job_dir),
                "completed_at": datetime.now().isoformat(),
                "index_url": f"/output/{job_dir.name}/index.html",
                "portal_ready": True,
                "active_agent": None
            })
            print(f"🎉 Portal ready at: /output/{job_dir.name}/index.html")
        else:
            generation_status[job_id].update({
                "status": "completed",
                "progress": "Generation complete (assets created, portal pending)",
                "output_dir": str(job_dir),
                "completed_at": datetime.now().isoformat(),
                # Fallback to directory listing if index.html is missing
                "index_url": f"/output/{job_dir.name}/",
                "portal_ready": False,
                "active_agent": None
            })
            print(f"⚠️  Portal not found at: {portal_path}, falling back to directory listing.")
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Generation failed: {e}", flush=True)
        print(f"Traceback:\n{error_trace}", flush=True)
        
        generation_status[job_id].update({
            "status": "failed",
            "progress": f"Error: {str(e)}",
            "error": str(e),
            "error_trace": error_trace,
            "failed_at": datetime.now().isoformat(),
            "active_agent": None
        })
    finally:
        # Restore stdout/stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr


@app.route("/")
def index():
    """Serve the main page."""
    try:
        default_model = os.getenv("DEFAULT_MODEL", "x-ai/grok-4.1-fast")
        available_models = os.getenv("AVAILABLE_MODELS", "").split(",")
        available_models = [m.strip() for m in available_models if m.strip()]
        return render_template("index.html", agents=AGENTS, default_model=default_model, available_models=available_models)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR in index route: {e}", flush=True)
        print(f"Traceback: {error_details}", flush=True)
        return jsonify({
            "error": "Internal Server Error",
            "message": str(e),
            "details": error_details
        }), 500


def _serve_test_page():
    """Utility to serve the cached-bypass diagnostics page."""
    try:
        return send_from_directory(".", "test_page.html")
    except FileNotFoundError:
        return """<!DOCTYPE html>
<html><head><title>API Test</title>
<meta http-equiv="Cache-Control" content="no-cache">
<style>body{font-family:Arial;padding:20px;background:#f5f5f5}
.result{padding:10px;margin:10px 0;border-radius:5px}
.success{background:#d4edda;color:#155724}
.error{background:#f8d7da;color:#721c24}</style></head>
<body><h1>🧪 API Test</h1><div id="results">Testing...</div>
<script>
async function test(){const r=document.getElementById('results');
const tests=[{n:'Version',u:'/api/version'},{n:'Agents',u:'/api/agents'},{n:'LLM',u:'/api/test-llm'}];
let h='';for(const t of tests){try{const res=await fetch(t.u);const d=await res.json();
h+=`<div class="result success">✅ ${t.n}: Working</div>`;}catch(e){
h+=`<div class="result error">❌ ${t.n}: ${e.message}</div>`;}}
r.innerHTML=h+'<h2 style="color:green">🎉 APIs Working!</h2><a href="/" style="font-size:20px">Go to Main App →</a>';}
test();
</script></body></html>"""


@app.route("/test")
def test_page():
    """Shortlink for diagnostics page."""
    return _serve_test_page()


@app.route("/test_page.html")
def test_page_legacy():
    """Legacy path expected by previous instructions."""
    return _serve_test_page()


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "version": "2.0.0-nvidia-support",
        "agents_count": len(AGENTS)
    })


@app.route("/api/test-llm")
def test_llm():
    """Test LLM connection and configuration."""
    try:
        from llm_client import create_llm_client
        
        # Check environment variables
        nvidia_key = os.getenv("NVIDIA_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        
        llm_config = {
            "nvidia_configured": bool(nvidia_key),
            "openai_configured": bool(openai_key),
            "openrouter_configured": bool(openrouter_key),
            "openai_api_base": os.getenv("OPENAI_API_BASE", "Not set"),
            "default_model": os.getenv("DEFAULT_MODEL", "Not set")
        }
        
        # Try to create LLM client
        try:
            llm = create_llm_client(temperature=0.7)
            
            # Try a simple completion
            response = llm.invoke("Say 'Hello, NVIDIA works!'")
            
            return jsonify({
                "success": True,
                "message": "LLM is working!",
                "config": llm_config,
                "test_response": str(response.content) if hasattr(response, 'content') else str(response),
                "llm_model": getattr(llm, 'model_name', 'unknown')
            })
            
        except Exception as llm_error:
            import traceback
            return jsonify({
                "success": False,
                "message": "LLM creation or test failed",
                "config": llm_config,
                "error": str(llm_error),
                "traceback": traceback.format_exc()
            }), 500
            
    except Exception as e:
        import traceback
        return jsonify({
            "success": False,
            "message": "Test endpoint error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route("/api/version")
def version():
    """Get application version."""
    version_str = "2.0.0-nvidia-support"
    try:
        with open("VERSION", "r") as f:
            version_str = f.readline().strip()
    except:
        pass
    
    return jsonify({
        "success": True,
        "version": version_str,
        "supports": ["NVIDIA", "OpenAI", "OpenRouter"],
        "primary": "NVIDIA",
        "message": "OpenRouter is optional, not required"
    })


@app.route("/api/agents")
def get_agents():
    """Get list of agents."""
    return jsonify({
        "success": True,
        "agents": AGENTS
    })


@app.route("/api/generate", methods=["POST"])
def generate():
    """Start tech test generation."""
    try:
        data = request.json
        
        if not data:
            print("[API] ERROR: No JSON data received", flush=True)
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        job_role = data.get("job_role")
        job_level = data.get("job_level")
        language = data.get("language", "Korean")
        model = (data.get("model") or os.getenv("DEFAULT_MODEL", "x-ai/grok-4.1-fast")).strip()
        
        print(f"[API] Received request: role={job_role}, level={job_level}, lang={language}", flush=True)
        
        if not job_role or not job_level:
            print("[API] ERROR: Missing required fields", flush=True)
            return jsonify({
                "success": False,
                "error": "Job role and level are required"
            }), 400
        
        # Generate unique job ID
        job_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{abs(hash(job_role + job_level)) % 10000}"
        
        print(f"[API] Generated job_id={job_id}", flush=True)
        print(f"[API] Before initialization - generation_status keys: {list(generation_status.keys())}", flush=True)
        
        # Initialize status immediately (before thread starts)
        generation_status[job_id] = {
            "status": "initializing",
            "progress": "Starting background process...",
            "output_dir": None,
            "error": None,
            "logs": [],
            "agent_status": {},
            "active_agent": None,
            "started_at": datetime.now().isoformat(),
            "model": model
        }
        
        print(f"[API] After initialization - generation_status keys: {list(generation_status.keys())}", flush=True)
        print(f"[API] Status for {job_id}: {generation_status[job_id]}", flush=True)
        
        # Start generation in background thread
        thread = threading.Thread(
            target=run_generation,
            args=(job_id, job_role, job_level, language, model),
            name=f"Generation-{job_id}"
        )
        thread.daemon = True
        thread.start()
        
        print(f"[API] Thread started successfully for job_id={job_id}", flush=True)
        print(f"[API] Thread is alive: {thread.is_alive()}", flush=True)
        
        return jsonify({
            "success": True,
            "job_id": job_id,
            "message": "Generation started"
        })
        
    except Exception as e:
        print(f"[API] EXCEPTION in generate endpoint: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/status/<job_id>")
def status(job_id):
    """Get generation status."""
    print(f"[API] Status check for job_id: {job_id}", flush=True)
    print(f"[API] Current generation_status keys: {list(generation_status.keys())}", flush=True)
    
    if job_id not in generation_status:
        print(f"[API] Status check failed - job_id not found: {job_id}", flush=True)
        
        # Return a pending status instead of 404 to avoid frontend errors
        return jsonify({
            "success": True,
            "status": {
                "status": "initializing",
                "progress": "Starting background process...",
                "logs": [],
                "started_at": datetime.now().isoformat()
            }
        })
    
    status_data = generation_status[job_id]
    print(f"[API] Returning status: {status_data.get('status')} - {status_data.get('progress')}", flush=True)
    
    return jsonify({
        "success": True,
        "status": status_data
    })


@app.route("/api/logs/<job_id>")
def get_logs(job_id):
    """Get generation logs."""
    print(f"[API] Logs request for job_id: {job_id}", flush=True)
    
    if job_id not in generation_status:
        print(f"[API] Logs - job_id not found: {job_id}", flush=True)
        # Return empty logs instead of 404 to avoid frontend errors
        return jsonify({
            "success": True,
            "logs": [],
            "count": 0,
            "message": "Job initializing or not found"
        })
    
    logs = generation_status[job_id].get('logs', [])
    print(f"[API] Returning {len(logs)} log lines for job_id={job_id}", flush=True)
    
    return jsonify({
        "success": True,
        "logs": logs,
        "count": len(logs)
    })


@app.route("/output/", defaults={"path": ""})
@app.route("/output/<path:path>")
def output_files(path):
    """Serve generated output files with directory safeguards."""
    root = Path("output").resolve()
    try:
        requested = (root / path).resolve()
    except Exception as e:
        print(f"⚠️  Path resolution error for '{path}': {e}", flush=True)
        abort(404)

    print(f"🔍 Serving file request: path='{path}'", flush=True)
    print(f"   Root: {root}", flush=True)
    print(f"   Requested: {requested}", flush=True)

    # Prevent directory traversal
    if not str(requested).startswith(str(root)):
        print(f"⛔ Access denied: {requested} is outside {root}", flush=True)
        abort(404)

    if requested.is_dir():
        index_obj = requested / "index.html"
        if index_obj.exists():
            print(f"   Serving index: {index_obj}", flush=True)
            return send_file(index_obj)
        
        # Directory exists but no index.html -> Show file listing
        print(f"   Index missing, serving directory listing for: {requested}", flush=True)
        files = sorted([f.name for f in requested.iterdir() if not f.name.startswith('.')])
        listing_html = f"""
        <html>
        <head><title>Asset Listing</title><style>body{{font-family:sans-serif;padding:2rem;line-height:1.5}} a{{color:#2563eb;text-decoration:none}} a:hover{{text-decoration:underline}} ul{{list-style:none;padding:0}} li{{padding:0.5rem 0;border-bottom:1px solid #eee}}</style></head>
        <body>
            <h2>📂 Generated Assets</h2>
            <p>Directory: {path}</p>
            <ul>
        """
        for f in files:
            listing_html += f'<li>📄 <a href="{f}">{f}</a></li>'
        listing_html += "</ul></body></html>"
        return listing_html

    if not requested.exists():
        # If user requested index.html explicitly but it's missing, try to show parent dir listing
        if requested.name == "index.html" and requested.parent.exists() and requested.parent.is_dir():
             print(f"   Explicit index.html missing, falling back to directory listing of {requested.parent}", flush=True)
             # Recursive call to serve directory
             # But simpler to just redirect or inline the logic. 
             # Let's just reuse the listing logic by adjusting 'requested'? 
             # No, 'path' arg needs to be adjusted for links to work.
             # Let's just redirect to the directory (remove index.html)
             return redirect(url_for('output_files', path=str(Path(path).parent) + "/"))

        # Helpful log for debugging missing files on hosting platforms
        print(f"⚠️  Requested output file not found: {requested}", flush=True)
        abort(404)

    return send_file(requested)


@app.route("/api/jobs")
def list_jobs():
    """List all generation jobs."""
    jobs = []
    for job_id, status_info in generation_status.items():
        jobs.append({
            "job_id": job_id,
            **status_info
        })
    
    # Sort by started time (newest first)
    jobs.sort(key=lambda x: x.get("started_at", ""), reverse=True)
    
    return jsonify({
        "success": True,
        "jobs": jobs
    })


if __name__ == "__main__":
    # Use PORT environment variable for Railway/Heroku compatibility
    port = int(os.getenv("PORT", 8080))
    
    # Read version
    version = "2.0.0"
    try:
        with open("VERSION", "r") as f:
            version = f.readline().strip()
    except:
        pass
    
    print("=" * 70)
    print("🚀 Tech Test Generator Web App")
    print(f"📦 Version: {version}")
    print("=" * 70)
    print(f"📍 Server: http://0.0.0.0:{port}")
    print("🎨 Using Myrealtrip branding")
    print("🤖 Powered by NVIDIA & CrewAI")
    print("💡 Primary: NVIDIA | Fallback: OpenAI, OpenRouter")
    print("=" * 70)
    if port == 8080:
        print("⚠️  Note: Using port 8080 (port 5000 is used by macOS AirPlay)")
        print("=" * 70)
    print()
    
    app.run(debug=False, host="0.0.0.0", port=port)

