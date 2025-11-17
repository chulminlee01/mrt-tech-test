"""
Flask Web Application for Tech Test Generator
Provides a web interface to generate tech assignments using CrewAI orchestrator.
"""

import os
import sys
import io
import json
import threading
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory, Response

from crewai_working import generate_with_crewai
from agent_starter_code import run_starter_code_generator
from agent_web_designer import run_web_designer

app = Flask(__name__)

# Store generation status
generation_status = {}

# Agent definitions for UI (7 agents: 4 CrewAI + 3 post-processing)
AGENTS = [
    {"id": "pm", "name": "Product Manager", "icon": "👔", "role": "Team Leader & Coordinator"},
    {"id": "researcher", "name": "Research Analyst", "icon": "🔍", "role": "Industry Research"},
    {"id": "designer", "name": "Assignment Designer", "icon": "✏️", "role": "Question Creation"},
    {"id": "reviewer", "name": "QA Reviewer", "icon": "🔎", "role": "Quality Assurance"},
    {"id": "data", "name": "Data Provider", "icon": "📊", "role": "Dataset Generation"},
    {"id": "builder", "name": "Web Builder", "icon": "🌐", "role": "Portal Creation"},
    {"id": "styler", "name": "Web Designer", "icon": "🎨", "role": "Styling & Design"},
]


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
        
        # Detect which phase we're in based on logs
        if 'task 1' in text_lower or 'pm initialization' in text_lower:
            generation_status[self.job_id]['progress'] = '👔 PM initializing project...'
            generation_status[self.job_id]['active_agent'] = 'pm'
        elif 'task 2' in text_lower or 'research' in text_lower and 'analyst' in text_lower:
            generation_status[self.job_id]['progress'] = '🔍 Research Analyst investigating...'
            generation_status[self.job_id]['active_agent'] = 'researcher'
        elif 'task 3' in text_lower or 'discussion' in text_lower or 'consensus' in text_lower:
            generation_status[self.job_id]['progress'] = '💬 Team discussion in progress...'
            generation_status[self.job_id]['active_agent'] = 'pm'
        elif 'task 4' in text_lower or 'assignment designer' in text_lower:
            generation_status[self.job_id]['progress'] = '✏️ Designer creating assignments...'
            generation_status[self.job_id]['active_agent'] = 'designer'
        elif 'task 5' in text_lower or 'qa reviewer' in text_lower or 'reviewing' in text_lower:
            generation_status[self.job_id]['progress'] = '🔎 QA reviewing assignments...'
            generation_status[self.job_id]['active_agent'] = 'reviewer'
        elif 'task 6' in text_lower or 'final decision' in text_lower or 'approved' in text_lower:
            generation_status[self.job_id]['progress'] = '👔 PM final approval...'
            generation_status[self.job_id]['active_agent'] = 'pm'
        elif 'generating structured assignments' in text_lower:
            generation_status[self.job_id]['progress'] = '📝 Generating detailed assignments...'
        elif 'generating datasets' in text_lower:
            generation_status[self.job_id]['progress'] = '📊 Creating datasets...'
            generation_status[self.job_id]['active_agent'] = 'data'
        elif 'building web portal' in text_lower:
            generation_status[self.job_id]['progress'] = '🌐 Building web portal...'
            generation_status[self.job_id]['active_agent'] = 'builder'
        elif 'applying custom styling' in text_lower or 'web designer' in text_lower:
            generation_status[self.job_id]['progress'] = '🎨 Applying custom styling...'
            generation_status[self.job_id]['active_agent'] = 'styler'
    
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


def run_generation(job_id, job_role, job_level, language):
    """Run the orchestrator in a background thread."""
    global generation_status
    
    print(f"[GENERATION] Thread started for job_id={job_id}", flush=True)
    print(f"[GENERATION] Current generation_status keys: {list(generation_status.keys())}", flush=True)
    
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
        
        # Run CrewAI team collaboration
        generation_status[job_id]["progress"] = "CrewAI team collaborating..."
        result = generate_with_crewai(
            job_role=job_role,
            job_level=job_level,
            language=language,
            output_root=str(job_dir)
        )
        
        # Post-processing: Generate starter code and styling
        assignments_path = Path(job_dir) / "assignments.json"
        html_path = Path(job_dir) / "index.html"
        
        if assignments_path.exists():
            generation_status[job_id]["progress"] = "Generating starter code..."
            try:
                run_starter_code_generator(
                    assignments_path=str(assignments_path),
                    output_dir=str(Path(job_dir) / "starter_code")
                )
            except Exception as e:
                print(f"⚠️  Starter code error: {e}", flush=True)
        
        if html_path.exists():
            generation_status[job_id]["progress"] = "Applying custom styling..."
            try:
                run_web_designer(
                    html_path=str(html_path),
                    css_output=str(Path(job_dir) / "styles.css"),
                    notes_output=str(Path(job_dir) / "design_notes.md"),
                    language=language
                )
            except Exception as e:
                print(f"⚠️  Web designer error: {e}", flush=True)
        
        # Success
        generation_status[job_id].update({
            "status": "completed",
            "progress": "Generation complete!",
            "output_dir": str(job_dir),
            "completed_at": datetime.now().isoformat(),
            "index_url": f"/output/{job_dir.name}/index.html"
        })
        
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
            "failed_at": datetime.now().isoformat()
        })
    finally:
        # Restore stdout/stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr


@app.route("/")
def index():
    """Serve the main page."""
    try:
        return render_template("index.html", agents=AGENTS)
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
            "started_at": datetime.now().isoformat()
        }
        
        print(f"[API] After initialization - generation_status keys: {list(generation_status.keys())}", flush=True)
        print(f"[API] Status for {job_id}: {generation_status[job_id]}", flush=True)
        
        # Start generation in background thread
        thread = threading.Thread(
            target=run_generation,
            args=(job_id, job_role, job_level, language),
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


@app.route("/output/<path:filename>")
def output_files(filename):
    """Serve generated output files."""
    return send_from_directory("output", filename)


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

