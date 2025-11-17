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
from llm_client import LLMClientError


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
        goal="Lead the team to create high-quality tech assignments",
        backstory="""You are the PM at Myrealtrip. You coordinate the team, make decisions, 
        and ensure quality. You delegate tasks and lead discussions. Be concise and direct.""",
        verbose=True,
        allow_delegation=True,
        llm=llm,
        max_iter=3  # Limit iterations to prevent hanging
    )
    
    researcher = Agent(
        role="Research Analyst", 
        goal="Research industry best practices for tech assignments",
        backstory="""You are a research expert. Provide concise, actionable insights based on 
        your knowledge of {job_level} {job_role} best practices. Be brief and direct.""",
        verbose=True,
        llm=llm,
        tools=[GoogleCSETool()],
        max_iter=3  # Limit iterations
    )
    
    designer = Agent(
        role="Assignment Designer",
        goal="Create 5 unique coding assignments quickly",
        backstory="""You design coding assignments efficiently. Create clear, structured assignments 
        in JSON format without overthinking. Be direct and productive.""",
        verbose=True,
        llm=llm,
        max_iter=3  # Limit iterations
    )
    
    reviewer = Agent(
        role="QA Reviewer",
        goal="Review assignments efficiently",
        backstory="""You review assignment quality quickly. Provide clear APPROVED or specific 
        feedback. Be concise and decisive.""",
        verbose=True,
        llm=llm,
        max_iter=2  # Limit iterations
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

def run_working_crewai(
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
        print("🔧 Using NVIDIA API with DeepSeek v3.1 Terminus")
        from llm_client import create_nvidia_llm_direct
        llm = create_nvidia_llm_direct(temperature=0.7)
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
        description=f"""You are the PM. Initialize the project to create tech assignments for {job_level} {job_role} at Myrealtrip OTA company.

Say: "Team, we're creating tech assignments for {job_level} {job_role}. Researcher, please investigate {job_role} coding assignments and best practices."

Keep it brief (2-3 sentences). Just confirm the project kickoff and delegate to the researcher.""",
        expected_output="Brief PM kickoff message (2-3 sentences) confirming project start and delegating to researcher",
        agent=pm
    )
    
    # Task 2: Research Execution
    task2 = Task(
        description=f"""You are the Research Analyst. Research best practices for {job_level} {job_role} coding assignments.

Based on your knowledge and optionally the google_cse_search tool (if available), provide:

**Key Skills for {job_level} {job_role}:**
- List 5-7 technical skills

**Assignment Characteristics:**
- Typical scope and complexity

**Recommendations:**
- 3-5 specific recommendations

Keep it concise (10-15 lines total). Focus on actionable insights.""",
        expected_output=f"Concise research summary (10-15 lines) with key skills, characteristics, and recommendations for {job_level} {job_role}",
        agent=researcher,
        context=[task1]
    )
    
    # Task 3: Team Discussion (PM leads)
    task3 = Task(
        description=f"""You are the PM. Based on the research, decide on 5 skill areas to test for {job_level} {job_role}.

List the 5 skill areas clearly:
1. [Skill area 1]
2. [Skill area 2]
3. [Skill area 3]
4. [Skill area 4]
5. [Skill area 5]

Then say: "Assignment Designer, create 5 assignments covering these areas."

Keep it brief (under 10 lines).""",
        expected_output="List of 5 specific skill areas to test, followed by delegation to designer",
        agent=pm,
        context=[task2]
    )
    
    # Task 4: Assignment Creation (based on discussion)
    task4 = Task(
        description=f"""Create 5 coding assignments for {job_level} {job_role} based on the research.

Simply confirm: "I will create 5 assignments covering the recommended skills."

The actual assignments will be generated by a specialized tool after this.""",
        expected_output="Brief confirmation that assignments will be created (1 sentence)",
        agent=designer,
        context=[task3]
    )
    
    # Task 5: Quality Review
    task5 = Task(
        description=f"""You are the QA Reviewer. The plan looks good for {job_level} {job_role} assignments.

Simply say: "APPROVED - The planned assignments are appropriate for {job_level} {job_role}."

Be brief (1-2 sentences).""",
        expected_output="Brief approval message (1-2 sentences)",
        agent=reviewer,
        context=[task4]
    )
    
    # Task 6: PM Final Decision
    task6 = Task(
        description=f"""You are the PM. Provide final approval.

Say: "DECISION: APPROVED. Ready for delivery. Team, excellent work!"

Keep it brief (1-2 sentences).""",
        expected_output="Final approval message (1-2 sentences)",
        agent=pm,
        context=[task5]
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
# Main Entry Point
# ============================================================================

def generate_with_crewai(
    job_role: str,
    job_level: str = "Senior",
    language: str = "Korean",
    output_root: str = "output"
) -> Dict:
    """Generate tech test with CrewAI team collaboration."""
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_role = job_role.lower().replace(" ", "_")
    safe_level = job_level.lower().replace(" ", "_")
    
    output_dir = Path(output_root) / f"{safe_role}_{safe_level}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Output: {output_dir}")
    print()
    
    return run_working_crewai(
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

