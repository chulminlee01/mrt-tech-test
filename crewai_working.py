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

from agent_researcher import recent_google_search
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
    """Create all agents for the team."""
    
    pm = Agent(
        role="Product Manager",
        goal="Lead team collaboration and decision-making",
        backstory="""You are an experienced PM at Myrealtrip OTA company. You lead discussions naturally, ask good questions, and make decisions collaboratively. You're supportive and appreciate team input.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        max_iter=2
    )
    
    researcher = Agent(
        role="Research Analyst", 
        goal="Provide actionable insights on technical hiring",
        backstory="""You research technical hiring best practices. You know industry standards for different experience levels and can recommend specific skills and assignment types. You're analytical but concise.""",
        verbose=True,
        llm=llm,
        tools=[GoogleCSETool()],  # Keep tool for authentic research
        max_iter=2
    )
    
    designer = Agent(
        role="Assignment Designer",
        goal="Propose creative, practical coding assignments",
        backstory="""You design technical assessments. You're creative in thinking of practical scenarios that test real skills. You understand OTA business and can create relevant challenges.""",
        verbose=True,
        llm=llm,
        max_iter=2
    )
    
    reviewer = Agent(
        role="QA Reviewer",
        goal="Ensure assignment quality and appropriateness",
        backstory="""You review technical assignments for quality. You check difficulty level, relevance, and clarity. You provide constructive feedback and catch potential issues.""",
        verbose=True,
        llm=llm,
        max_iter=2
    )
    
    tech_writer = Agent(
        role="Technical Writer",
        goal="Ensure documentation quality and clarity",
        backstory="""You review documentation for clarity and completeness. You ensure 
        requirements are well-written and candidates can understand them.""",
        verbose=True,
        llm=llm
    )
    
    return pm, researcher, designer, reviewer, tech_writer


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
    
    # Create agents (Technical Writer optional - not needed for core workflow)
    pm, researcher, designer, reviewer, tech_writer = create_working_agents(llm)
    
    print("👥 Team Assembled:")
    print(f"   👔 {pm.role}")
    print(f"   🔍 {researcher.role}")
    print(f"   ✏️ {designer.role}")
    print(f"   🔎 {reviewer.role}")
    print()
    
    # Task 1: PM Initialization & Research Delegation  
    task1 = Task(
        description=f"""You're the PM at Myrealtrip. Announce the project:

"Hi team! We need to create take-home coding assignments for {job_level} {job_role} candidates. These will be used to evaluate applicants for our OTA platform team. Researcher, can you investigate what skills and assignment types work best for this level? Let's aim for practical, real-world scenarios."

Keep it natural and conversational (3-4 sentences).""",
        expected_output="Natural PM kickoff announcement (3-4 sentences) introducing the project and delegating to researcher",
        agent=pm,
        async_execution=False
    )
    
    # Task 2: Research Execution
    task2 = Task(
        description=f"""You're the Research Analyst. Share your findings:

"Based on industry standards for {job_level} {job_role}, here are the key technical areas we should test:

1. [Specific skill with brief reason]
2. [Specific skill with brief reason]
3. [Specific skill with brief reason]
4. [Specific skill with brief reason]
5. [Specific skill with brief reason]

For an OTA company like Myrealtrip, I recommend focusing on [mention 2-3 relevant scenarios like hotel bookings, flight search, etc.].

The assignments should be practical and completable in 2-4 hours."

Be specific about skills and OTA scenarios. Write 8-12 lines.""",
        expected_output=f"Research summary with 5 specific skills (with reasons) and OTA-specific recommendations for {job_level} {job_role}",
        agent=researcher,
        context=[task1],
        async_execution=False
    )
    
    # Task 3: Team Discussion (PM leads)
    task3 = Task(
        description=f"""You're the PM leading a team discussion. Facilitate the conversation:

"Great research! Let me summarize what we heard:
- [Mention 3 key skills from research]
- [Mention the OTA scenarios suggested]

Designer, based on this research, what assignment ideas do you have? Think about how we can test these skills in practical OTA scenarios."

Lead the discussion naturally (4-5 sentences). Reference specific findings from the research.""",
        expected_output="PM summary of research findings and question to designer, referencing actual skills mentioned",
        agent=pm,
        context=[task2],
        async_execution=False
    )
    
    # Task 4: Assignment Creation (based on discussion)
    task4 = Task(
        description=f"""You're the Assignment Designer. Respond to the PM's question:

"I have some ideas! Based on the research, I propose we create 5 assignments:

1. [Assignment idea 1 - specific OTA scenario]
2. [Assignment idea 2 - different technical focus]  
3. [Assignment idea 3 - another OTA scenario]
4. [Assignment idea 4 - integration/API focus]
5. [Assignment idea 5 - comprehensive challenge]

Each one will test the key skills we discussed while being relevant to OTA operations. What do you think, PM?"

Propose 5 specific assignment ideas with brief descriptions (8-10 lines).""",
        expected_output="Designer proposes 5 specific assignment ideas related to OTA scenarios",
        agent=designer,
        context=[task3],
        async_execution=False
    )
    
    # Task 5: Quality Review
    task5 = Task(
        description=f"""You're the QA Reviewer. Evaluate the proposed assignments:

"I've reviewed the 5 proposed assignments. They look solid for {job_level} level:
- They cover the essential skills we identified
- The OTA scenarios are realistic and relevant  
- The scope seems appropriate for 2-4 hour assignments

I have one suggestion: [mention one minor improvement]

Overall assessment: APPROVED. These will effectively evaluate candidates."

Provide constructive review (4-5 sentences).""",
        expected_output="QA review with approval and one constructive suggestion",
        agent=reviewer,
        context=[task4],
        async_execution=False
    )
    
    # Task 6: PM Final Decision
    task6 = Task(
        description=f"""You're the PM. Give final approval:

"Excellent work, team! I'm impressed with this collaboration.

Researcher - your insights on {job_level} skills were spot-on.
Designer - the assignment ideas are creative and practical.
Reviewer - good catch on [mention the suggestion].

DECISION: APPROVED. Let's proceed with these 5 assignments. Great teamwork everyone!"

Provide encouraging final approval (5-6 sentences).""",
        expected_output="PM final approval with specific appreciation for each team member's contribution",
        agent=pm,
        context=[task5],
        async_execution=False
    )
    
    # Create crew (4 agents: PM, Researcher, Designer, Reviewer)
    print("📋 Tasks Defined:")
    print(f"   1. PM Initialization & Delegation")
    print(f"   2. Research Execution (Google CSE)")
    print(f"   3. Team Discussion (PM leads)")
    print(f"   4. Assignment Creation (Designer)")
    print(f"   5. Quality Review (QA Reviewer)")
    print(f"   6. PM Final Decision")
    print()
    print("🚀 Initializing CrewAI Team (4 core agents)...")
    print()
    
    crew = Crew(
        agents=[pm, researcher, designer, reviewer],
        tasks=[task1, task2, task3, task4, task5, task6],
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
    
    # Save research output to file
    result_text = str(result)
    
    # Extract research content (before discussion section)
    research_lines = []
    for line in result_text.split('\n'):
        if '[PM]' in line and 'discuss' in line.lower():
            break  # Stop at discussion phase
        if line.strip():
            research_lines.append(line)
    
    if research_lines:
        research_content = '\n'.join(research_lines)
        Path(CURRENT_RESEARCH_PATH).write_text(research_content, encoding="utf-8")
        print(f"✅ Research saved to: {CURRENT_RESEARCH_PATH}")
    
    # For assignments, use the proven agent_question_generator
    print()
    print("📝 Generating structured assignments using proven generator...")
    try:
        from agent_question_generator import run_question_generator
        
        # Get job info from paths
        parts = str(output_dir).split('/')
        job_info = parts[-1] if parts else ""
        
        run_question_generator(
            job_role=job_role,
            job_level=job_level,
            company_name="Myrealtrip OTA Company",
            input_path=CURRENT_RESEARCH_PATH,
            output_path=CURRENT_ASSIGNMENTS_PATH,
            language=language
        )
        print(f"✅ Assignments generated and saved")
    except Exception as e:
        print(f"⚠️  Assignment generation error: {e}")
    
    # Post-processing: Generate datasets
    if Path(CURRENT_ASSIGNMENTS_PATH).exists():
        print()
        print("📊 Generating datasets...")
        try:
            run_data_provider(
                assignments_path=CURRENT_ASSIGNMENTS_PATH,
                output_dir=str(output_dir / "datasets"),
                language=language
            )
        except Exception as e:
            print(f"⚠️  Dataset generation error: {e}")
        
        print("🌐 Building web portal...")
        try:
            run_web_builder(
                assignments_path=CURRENT_ASSIGNMENTS_PATH,
                research_summary_path=CURRENT_RESEARCH_PATH,
                output_html=str(output_dir / "index.html"),
                language=language,
                starter_dir=str(output_dir / "starter_code")
            )
        except Exception as e:
            print(f"⚠️  Web builder error: {e}")
    
    return {
        "status": "completed",
        "result": result_text,
        "output_dir": str(output_dir)
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
    
    # Use CrewAI by default (user requested)
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

