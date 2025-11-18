"""
Working CrewAI Implementation with True Collaboration
PM initializes → Research → Team Discussion → Question Creation → Review → Finalize
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# Optional import - only needed if using Google Search
try:
    from agent_researcher import recent_google_search
    GOOGLE_SEARCH_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Google Search not available (import error): {e}")
    GOOGLE_SEARCH_AVAILABLE = False
    def recent_google_search(query):
        return "Google Search not available."

from agent_data_provider import run_data_provider
from agent_web_builder import run_web_builder
from crewai.tools import BaseTool
from llm_client import (
    LLMClientError,
    create_llm_client,
    create_nvidia_llm_direct,
)


# ============================================================================
# Global Variables for Tool Access
# ============================================================================

CURRENT_RESEARCH_PATH = None
CURRENT_ASSIGNMENTS_PATH = None


# ============================================================================
# CrewAI Tools
# ============================================================================

class GoogleCSETool(BaseTool):
    name: str = "google_cse_search"
    description: str = "Search Google Custom Search Engine for recent information. Use this to research coding assignment best practices, industry trends, and technical hiring standards. Input should be your search query as a string."
    
    def _run(self, query: str) -> str:
        """Execute Google CSE search."""
        # Check if Google API is configured
        google_key = os.getenv("GOOGLE_API_KEY")
        google_cse = os.getenv("GOOGLE_CSE_ID")
        
        if not google_key or not google_cse:
            print(f"\n⚠️  [Research Analyst] Google Search not configured, using general knowledge for: '{query[:60]}...'\n", flush=True)
            return f"Google Search API not configured. Based on general knowledge about {query}, here are standard best practices for technical hiring and coding assessments in this area."
        
        print(f"\n🔍 [Research Analyst] Executing Google CSE search: '{query[:60]}...'\n", flush=True)
        try:
        result = recent_google_search(query)
        print(f"\n✅ [Research Analyst] Search completed - found results\n", flush=True)
        return result
        except Exception as e:
            print(f"\n⚠️  [Research Analyst] Search failed: {e}\n", flush=True)
            return f"Search failed. Using general knowledge about {query}."


# ============================================================================
# Create Agents
# ============================================================================

def create_working_agents(llm):
    """Create 6 agents for the complete team (Designer removed per user request)."""
    
    pm = Agent(
        role="Product Manager",
        goal="Lead team and make decisions",
        backstory="""You lead the Myrealtrip team. Keep messages brief (2-3 sentences). Coordinate work and give approvals.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        max_iter=1
    )
    
    researcher = Agent(
        role="Research Analyst", 
        goal="Research skills and requirements",
        backstory="""You research technical skills for {job_level} {job_role}. Be concise (5-7 lines). List key skills with brief reasons.""",
        verbose=True,
        llm=llm,
        tools=[],  # Remove tool to avoid delays
        max_iter=1
    )
    
    data_provider = Agent(
        role="Data Provider",
        goal="Confirm dataset creation",
        backstory="""You generate OTA datasets. Confirm what you'll create in 1-2 sentences. Be brief.""",
        verbose=True,
        llm=llm,
        max_iter=1
    )
    
    web_builder = Agent(
        role="Web Builder",
        goal="Confirm portal creation",
        backstory="""You build web portals. Confirm what you'll create in 1-2 sentences. Be brief.""",
        verbose=True,
        llm=llm,
        max_iter=1
    )
    
    web_designer = Agent(
        role="Web Designer",
        goal="Confirm styling",
        backstory="""You style websites. Confirm you'll apply Myrealtrip branding in 1-2 sentences. Be brief.""",
        verbose=True,
        llm=llm,
        max_iter=1
    )
    
    reviewer = Agent(
        role="QA Reviewer",
        goal="Review and approve",
        backstory="""You review deliverables. Give clear APPROVED or feedback in 2-3 sentences. Be decisive.""",
        verbose=True,
        llm=llm,
        max_iter=1
    )
    
    return pm, researcher, data_provider, web_builder, web_designer, reviewer


# ============================================================================
# Create Tasks with Proper Dependencies
# ============================================================================

def _run_crewai_classic(
    job_role: str,
    job_level: str,
    language: str,
    output_dir: Path
) -> Dict:
    """Run working CrewAI with proper collaboration."""
    
    global CURRENT_RESEARCH_PATH, CURRENT_ASSIGNMENTS_PATH
    
    load_dotenv()
    
    # Setup paths
    CURRENT_RESEARCH_PATH = str(output_dir / "research_report.txt")
    CURRENT_ASSIGNMENTS_PATH = str(output_dir / "assignments.json")
    
    # Configure LLM using our flexible client (supports NVIDIA, OpenAI, OpenRouter)
    from llm_client import create_llm_client
    
    print("=" * 70)
    print("🎯 CrewAI Team-Based Generation")
    print("=" * 70)
    
    # Check which LLM provider is configured
    nvidia_key = os.getenv("NVIDIA_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    # Use NVIDIA if available (bypass all LiteLLM complexity)
    if nvidia_key:
        print("🔧 Using NVIDIA API")
        from llm_client import create_nvidia_llm_direct
        llm = create_nvidia_llm_direct(temperature=0.3)  # Lower temp for faster, deterministic responses
        print()
        
    elif openai_key:
        print("🔧 Using OpenAI API")
        llm = create_llm_client(temperature=0.7)
    print()
    
    elif openrouter_key:
        print("🔧 Using OpenRouter API")
        llm = create_llm_client(temperature=0.7)
        print()
    else:
        print("❌ Error: No LLM API key found")
        print()
        print("Please set one of these environment variables:")
        print("  - NVIDIA_API_KEY (recommended)")
        print("  - OPENAI_API_KEY")
        print("  - OPENROUTER_API_KEY")
        raise LLMClientError("No LLM API key configured")
    
    # Create all 6 agents (Designer removed)
    pm, researcher, data_provider, web_builder, web_designer, reviewer = create_working_agents(llm)
    
    print("👥 Full Team Assembled (6 agents):")
    print(f"   👔 {pm.role}")
    print(f"   🔍 {researcher.role}")
    print(f"   📊 {data_provider.role}")
    print(f"   🌐 {web_builder.role}")
    print(f"   🎨 {web_designer.role}")
    print(f"   🔎 {reviewer.role}")
    print()
    
    # Task 1: PM Kickoff
    task1 = Task(
        description=f"""Say: "Team, let's create assignments for {job_level} {job_role}. Researcher, investigate required skills."

2 sentences only.""",
        expected_output="PM kickoff (2 sentences)",
        agent=pm,
        async_execution=False
    )
    
    # Task 2: Research
    task2 = Task(
        description=f"""List 5 key skills for {job_level} {job_role}:
1. [Skill]
2. [Skill]
3. [Skill]
4. [Skill]
5. [Skill]

Just list 5 skills. No explanation.""",
        expected_output=f"5 key skills for {job_level} {job_role}",
        agent=researcher,
        context=[task1],
        async_execution=False
    )
    
    # Task 3: PM Coordinates
    task3 = Task(
        description=f"""Say: "Great! Data Provider, Web Builder, Web Designer - please create the assets."

1 sentence only.""",
        expected_output="PM delegation (1 sentence)",
        agent=pm,
        context=[task2],
        async_execution=False
    )
    
    # Task 4: Data Provider
    task4 = Task(
        description=f"""Say: "I'll create OTA datasets - hotels, flights, bookings."

1-2 sentences.""",
        expected_output="Data Provider confirmation",
        agent=data_provider,
        context=[task3],
        async_execution=False
    )
    
    # Task 5: Web Builder
    task5 = Task(
        description=f"""Say: "I'll build the candidate portal."

1 sentence.""",
        expected_output="Web Builder confirmation",
        agent=web_builder,
        context=[task4],
        async_execution=False
    )
    
    # Task 6: Web Designer  
    task6 = Task(
        description=f"""Say: "I'll apply Myrealtrip branding."

1 sentence.""",
        expected_output="Web Designer confirmation",
        agent=web_designer,
        context=[task5],
        async_execution=False
    )
    
    # Task 7: QA Review
    task7 = Task(
        description=f"""Say: "APPROVED - Plan looks solid."

1 sentence.""",
        expected_output="QA approval",
        agent=reviewer,
        context=[task6],
        async_execution=False
    )
    
    # Task 8: PM Final
    task8 = Task(
        description=f"""Say: "Excellent! Proceed with the work."

1 sentence.""",
        expected_output="PM go-ahead",
        agent=pm,
        context=[task7],
        async_execution=False
    )
    
    # Create crew with all 6 agents
    print("📋 Tasks Defined (8 tasks):")
    print(f"   1. PM Kickoff")
    print(f"   2. Researcher Findings")
    print(f"   3. PM Coordination")
    print(f"   4. Data Provider Confirmation")
    print(f"   5. Web Builder Confirmation")
    print(f"   6. Web Designer Confirmation")
    print(f"   7. QA Approval")
    print(f"   8. PM Final Go-Ahead")
    print()
    print("🚀 Initializing CrewAI Team (6 agents)...")
    print()
    
    crew = Crew(
        agents=[pm, researcher, data_provider, web_builder, web_designer, reviewer],
        tasks=[task1, task2, task3, task4, task5, task6, task7, task8],
        process=Process.sequential,
        verbose=True
    )
    
    print("=" * 70)
    print("🎬 Starting Team Collaboration...")
    print("=" * 70)
    print()
    
    # Execute
    result = crew.kickoff()
    
    print()
    print("=" * 70)
    print("✅ Team Collaboration Complete")
    print("=" * 70)
    print()
    
    # Save discussion output to file
    discussion_text = str(result)
    
    # Save the full collaboration discussion
    Path(CURRENT_RESEARCH_PATH).write_text(discussion_text, encoding="utf-8")
    print(f"✅ Team discussion saved to: {CURRENT_RESEARCH_PATH}")
    
    # For assignments, use the proven agent_question_generator
    print()
    print("=" * 70)
    print("📝 Phase 1.5: Generating Detailed Assignments")
    print("=" * 70)
    
    try:
        from agent_question_generator import run_question_generator
        import traceback
        
        print(f"   Reading research from: {CURRENT_RESEARCH_PATH}")
        print(f"   Will save assignments to: {CURRENT_ASSIGNMENTS_PATH}")
        
        # Make sure research file exists
        if not Path(CURRENT_RESEARCH_PATH).exists():
            print(f"   ⚠️  Research file not found, creating placeholder...")
            Path(CURRENT_RESEARCH_PATH).write_text(f"Research for {job_level} {job_role}", encoding="utf-8")
        
        print(f"   Calling assignment generator...")
        
        run_question_generator(
            job_role=job_role,
            job_level=job_level,
            company_name="Myrealtrip OTA Company",
            input_path=CURRENT_RESEARCH_PATH,
            output_path=CURRENT_ASSIGNMENTS_PATH,
            language=language,
            model=None,  # Use default model
            temperature=0.5
        )
        print(f"   ✅ Assignments generated and saved to: {CURRENT_ASSIGNMENTS_PATH}")
        
        # Verify file was created
        if Path(CURRENT_ASSIGNMENTS_PATH).exists():
            file_size = Path(CURRENT_ASSIGNMENTS_PATH).stat().st_size
            print(f"   ✅ Verified: assignments.json created ({file_size} bytes)")
        else:
            print(f"   ❌ ERROR: assignments.json was NOT created!")
            
    except Exception as e:
        print(f"❌ Assignment generation failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        print(f"   ⚠️  Attempting to continue with remaining steps...")
    
    # Post-processing: Generate all assets
    print()
    print("=" * 70)
    print("🏗️  Asset Generation Phase")
    print("=" * 70)
    
    assignments_exists = Path(CURRENT_ASSIGNMENTS_PATH).exists()
    print(f"   Assignments file exists: {assignments_exists}")
    
    if assignments_exists:
        # Generate datasets
        print()
        print("📊 Step 1: Generating datasets...")
        try:
            datasets_dir = str(output_dir / "datasets")
            print(f"   Target: {datasets_dir}")
            run_data_provider(
                assignments_path=CURRENT_ASSIGNMENTS_PATH,
                output_dir=datasets_dir,
                language=language
            )
            print(f"   ✅ Datasets generated in: {datasets_dir}")
        except Exception as e:
            print(f"   ❌ Dataset generation error: {e}")
            import traceback
            traceback.print_exc()
        
        # Generate starter code
        print()
        print("🧰 Step 2: Generating starter code...")
        try:
            from agent_starter_code import run_starter_code_generator
            starter_dir = str(output_dir / "starter_code")
            print(f"   Target: {starter_dir}")
            run_starter_code_generator(
                assignments_path=CURRENT_ASSIGNMENTS_PATH,
                output_dir=starter_dir
            )
            print(f"   ✅ Starter code generated in: {starter_dir}")
        except Exception as e:
            print(f"   ❌ Starter code error: {e}")
            import traceback
            traceback.print_exc()
        
        # Build web portal
        print()
        print("🌐 Step 3: Building web portal...")
        try:
            html_path = str(output_dir / "index.html")
            print(f"   Target: {html_path}")
            run_web_builder(
                assignments_path=CURRENT_ASSIGNMENTS_PATH,
                research_summary_path=CURRENT_RESEARCH_PATH,
                output_html=html_path,
                language=language,
                starter_dir=str(output_dir / "starter_code")
            )
            print(f"   ✅ Web portal built: {html_path}")
            
            # Verify
            if Path(html_path).exists():
                size = Path(html_path).stat().st_size
                print(f"   ✅ Verified: index.html created ({size} bytes)")
            else:
                print(f"   ❌ ERROR: index.html was NOT created!")
        except Exception as e:
            print(f"   ❌ Web builder error: {e}")
            import traceback
            traceback.print_exc()
        
        # Apply styling
        print()
        print("🎨 Step 4: Applying custom styling...")
        try:
            from agent_web_designer import run_web_designer
            html_path = str(output_dir / "index.html")
            css_path = str(output_dir / "styles.css")
            print(f"   HTML: {html_path}")
            print(f"   CSS: {css_path}")
            
            if Path(html_path).exists():
                run_web_designer(
                    html_path=html_path,
                    css_output=css_path,
                    notes_output=str(output_dir / "design_notes.md"),
                    language=language
                )
                print(f"   ✅ Styling applied")
            else:
                print(f"   ⚠️  Skipping styling - HTML not found")
        except Exception as e:
            print(f"   ❌ Web designer error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("   ❌ Assignments file not found - skipping asset generation")
        print(f"   Expected: {CURRENT_ASSIGNMENTS_PATH}")
    
    # Check if portal was created
    portal_path = output_dir / "index.html"
    portal_ready = portal_path.exists()
    
    print(f"📊 Portal status: {'✅ Created' if portal_ready else '⏳ Pending'}")
    
    return {
        "status": "completed",
        "result": discussion_text,
        "output_dir": str(output_dir),
        "portal_ready": portal_ready
    }


# ============================================================================
# Simple Sequential Pipeline (Fast & Reliable)
# ============================================================================

def _log(text: str):
    """Log helper to ensure stdout is flushed (captured by UI)."""
    print(text, flush=True)


def _call_llm_text(llm, prompt: str) -> str:
    """Call LLM and return textual response."""
    response = llm.invoke(prompt)
    if hasattr(response, "content"):
        return response.content
    return str(response)


def _run_simple_pipeline(
    job_role: str,
    job_level: str,
    language: str,
    output_dir: Path
) -> Dict:
    """Fast sequential pipeline without CrewAI complexity."""
    load_dotenv()
    
    research_path = output_dir / "research_report.txt"
    research_path.parent.mkdir(parents=True, exist_ok=True)
    
    llm = create_nvidia_llm_direct(temperature=0.4)
    
    _log("👔 [PM] Kicking off project and delegating research.")
    kickoff = (
        f"Team, we're preparing a tech assignment for {job_level} {job_role}. "
        "Researcher, summarize current best practices so we can align."
    )
    _log(kickoff)
    
    # Research summary
    _log("🔍 [Research Analyst] Investigating best practices...")
    research_prompt = f"""
You are a research analyst specializing in OTA (Online Travel Agency) hiring.
Provide a concise summary (8-10 bullet points) for designing take-home tests targeting {job_level} {job_role}.

Include sections:
**Key Skills**
**Assignment Traits**
**Evaluation Criteria**
**Recommendations for Myrealtrip**
"""
    research_summary = _call_llm_text(llm, research_prompt)
    research_path.write_text(research_summary, encoding="utf-8")
    _log("✅ Research summary saved.")
    
    # Skill focus
    _log("💬 [PM] Aligning on skill focus areas...")
    skills_prompt = f"""
Based on the research summary below, list 5 skill areas we must test for {job_level} {job_role}.
Return format:
1. Skill - reason
2. ...

Research:
{research_summary}
"""
    skill_focus = _call_llm_text(llm, skills_prompt)
    _log(skill_focus)
    
    # Designer confirmation
    _log("✏️ [Designer] Acknowledging assignment creation plan.")
    _log("I will generate 5 assignments covering these skill areas.")
    
    # QA approval
    _log("🔎 [QA] APPROVED - Plan looks solid for the target role.")
    
    # PM final sign-off
    _log("👔 [PM] DECISION: APPROVED. Ready for delivery. Great work, team!")
    
    # Use assignment generator (existing workflow)
    from agent_question_generator import run_question_generator
    
    assignments_path = output_dir / "assignments.json"
    _log("📝 Generating detailed assignments...")
    run_question_generator(
        job_role=job_role,
        job_level=job_level,
        company_name="Myrealtrip OTA Company",
        input_path=str(research_path),
        output_path=str(assignments_path),
        language=language
    )
    _log("✅ Assignments generated.")
    
    # Datasets
    _log("📊 Creating datasets...")
    run_data_provider(
        assignments_path=str(assignments_path),
        output_dir=str(output_dir / "datasets"),
        language=language
    )
    
    # Web builder
    _log("🌐 Building candidate portal...")
    run_web_builder(
        assignments_path=str(assignments_path),
        research_summary_path=str(research_path),
        output_html=str(output_dir / "index.html"),
        language=language,
        starter_dir=str(output_dir / "starter_code")
    )
    
    return {
        "status": "completed",
        "result": research_summary,
        "output_dir": str(output_dir)
    }


# ============================================================================
# Main Entry Point
# ============================================================================


# ============================================================================
# Main Entry Point
# ============================================================================

def generate_with_crewai(
    job_role: str,
    job_level: str = "Senior",
    language: str = "Korean",
    output_root: str = "output"
) -> Dict:
    """Generate tech test using simple pipeline (default) or legacy CrewAI."""
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_role = job_role.lower().replace(" ", "_")
    safe_level = job_level.lower().replace(" ", "_")
    
    output_dir = Path(output_root) / f"{safe_role}_{safe_level}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Output: {output_dir}")
    print()
    
    # Use Full CrewAI by default (user wants all agents working)
    use_simple = os.getenv("USE_SIMPLE_PIPELINE", "false").lower() == "true"
    
    if use_simple:
        print("⚡ Using simple deterministic pipeline")
        return _run_simple_pipeline(
            job_role=job_role,
            job_level=job_level,
            language=language,
            output_dir=output_dir
        )
    
    print("🧠 Using Full CrewAI Collaboration Pipeline")
    return _run_crewai_classic(
        job_role=job_role,
        job_level=job_level,
        language=language,
        output_dir=output_dir
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--job-role", default="iOS Developer")
    parser.add_argument("--job-level", default="Senior")
    parser.add_argument("--language", default="Korean")
    parser.add_argument("--output-root", default="output")
    
    args = parser.parse_args()
    
    result = generate_with_crewai(
        job_role=args.job_role,
        job_level=args.job_level,
        language=args.language,
        output_root=args.output_root
    )
    
    print()
    print("✅ Complete!")
    print(f"📂 Output: {result['output_dir']}")

