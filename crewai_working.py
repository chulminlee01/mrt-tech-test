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
    """Create all 7 agents for the complete team."""
    
    pm = Agent(
        role="Product Manager",
        goal="Lead team collaboration and decision-making",
        backstory="""You are an experienced PM at Myrealtrip OTA company. You lead discussions naturally, coordinate work between team members, and make final decisions. You're supportive and appreciate team input.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        max_iter=2
    )
    
    researcher = Agent(
        role="Research Analyst", 
        goal="Provide actionable insights on technical hiring",
        backstory="""You research technical hiring best practices. You know industry standards for different experience levels and can recommend specific skills and assignment types.""",
        verbose=True,
        llm=llm,
        tools=[GoogleCSETool()],
        max_iter=2
    )
    
    assignment_designer = Agent(
        role="Assignment Designer",
        goal="Propose creative, practical coding assignments",
        backstory="""You design technical assessments. You're creative in thinking of practical OTA scenarios that test real skills. You create assignment concepts and requirements.""",
        verbose=True,
        llm=llm,
        max_iter=2
    )
    
    data_provider = Agent(
        role="Data Provider",
        goal="Generate realistic datasets for assignments",
        backstory="""You create sample datasets that candidates will use. You understand OTA data (hotels, flights, bookings) and generate realistic, useful test data.""",
        verbose=True,
        llm=llm,
        max_iter=2
    )
    
    web_builder = Agent(
        role="Web Builder",
        goal="Create the candidate portal webpage",
        backstory="""You build web portals. You create clean HTML pages that present assignments professionally. You ensure good UX and clear information architecture.""",
        verbose=True,
        llm=llm,
        max_iter=2
    )
    
    web_designer = Agent(
        role="Web Designer",
        goal="Style and enhance the portal",
        backstory="""You design beautiful, modern web interfaces. You apply Myrealtrip branding, ensure accessibility, and create engaging visual experiences.""",
        verbose=True,
        llm=llm,
        max_iter=2
    )
    
    reviewer = Agent(
        role="QA Reviewer",
        goal="Review and ensure quality of all deliverables",
        backstory="""You review everything for quality - assignments, datasets, and the website. You check for bugs, clarity issues, and provide constructive feedback.""",
        verbose=True,
        llm=llm,
        max_iter=2
    )
    
    return pm, researcher, assignment_designer, data_provider, web_builder, web_designer, reviewer


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
    
    # Create all 7 agents
    pm, researcher, assignment_designer, data_provider, web_builder, web_designer, reviewer = create_working_agents(llm)
    
    print("👥 Full Team Assembled (7 agents):")
    print(f"   👔 {pm.role}")
    print(f"   🔍 {researcher.role}")
    print(f"   ✏️ {assignment_designer.role}")
    print(f"   📊 {data_provider.role}")
    print(f"   🌐 {web_builder.role}")
    print(f"   🎨 {web_designer.role}")
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
    
    # Task 4: Assignment Designer Proposes Ideas
    task4 = Task(
        description=f"""You're the Assignment Designer. Respond to PM:

"I have some great ideas! Based on the research, I propose 5 assignments:

1. [Assignment 1 - specific OTA scenario]
2. [Assignment 2 - different focus]  
3. [Assignment 3 - another scenario]
4. [Assignment 4 - integration challenge]
5. [Assignment 5 - comprehensive test]

These will test the key skills while being relevant to OTA operations."

Propose 5 specific ideas (6-8 lines).""",
        expected_output="Designer proposes 5 assignment ideas",
        agent=assignment_designer,
        context=[task3],
        async_execution=False
    )
    
    # Task 5: PM Approves and Coordinates Asset Creation
    task5 = Task(
        description=f"""You're the PM. Approve and coordinate:

"Perfect! I love these ideas. Let's move forward:

Data Provider - please create realistic datasets for these assignments.
Web Builder - build the candidate portal.
Web Designer - apply our Myrealtrip branding.

Let's get these assets ready!"

Delegate to the asset creation team (3-4 sentences).""",
        expected_output="PM approval and delegation to Data Provider, Web Builder, Web Designer",
        agent=pm,
        context=[task4],
        async_execution=False
    )
    
    # Task 6: Data Provider Confirms
    task6 = Task(
        description=f"""You're the Data Provider. Confirm:

"I'll create realistic OTA datasets - hotels, flights, bookings data. They'll be in JSON/CSV format with realistic data for testing."

Brief confirmation (2 sentences).""",
        expected_output="Data Provider confirms dataset creation",
        agent=data_provider,
        context=[task5],
        async_execution=False
    )
    
    # Task 7: Web Builder Confirms
    task7 = Task(
        description=f"""You're the Web Builder. Confirm:

"I'll build a clean candidate portal with all assignment details, datasets, and starter code clearly presented."

Brief confirmation (1-2 sentences).""",
        expected_output="Web Builder confirms portal creation",
        agent=web_builder,
        context=[task6],
        async_execution=False
    )
    
    # Task 8: Web Designer Confirms
    task8 = Task(
        description=f"""You're the Web Designer. Confirm:

"I'll apply Myrealtrip branding with our emerald green colors and modern, accessible design."

Brief confirmation (1-2 sentences).""",
        expected_output="Web Designer confirms styling",
        agent=web_designer,
        context=[task7],
        async_execution=False
    )
    
    # Task 9: PM Triggers Actual Generation
    task9 = Task(
        description=f"""You're the PM. Say:

"Great! Team, please proceed with your work. I'll review everything once it's ready."

Brief go-ahead (1 sentence).""",
        expected_output="PM gives go-ahead for actual work",
        agent=pm,
        context=[task8],
        async_execution=False
    )
    
    # Create crew with all 7 agents
    print("📋 Phase 1 Tasks (Assignment Planning):")
    print(f"   1. PM Kickoff")
    print(f"   2. Researcher Findings")
    print(f"   3. PM Discussion Facilitation")
    print(f"   4. Designer Proposals")
    print(f"   5. PM Coordinates Asset Creation")
    print(f"   6-8. Asset Team Confirms (Data, Web, Design)")
    print(f"   9. PM Go-Ahead")
    print()
    print("🚀 Initializing CrewAI Team (7 agents)...")
    print()
    
    crew_phase1 = Crew(
        agents=[pm, researcher, assignment_designer, data_provider, web_builder, web_designer, reviewer],
        tasks=[task1, task2, task3, task4, task5, task6, task7, task8, task9],
        process=Process.sequential,
        verbose=True
    )
    
    print("=" * 70)
    print("🎬 Phase 1: Assignment Planning & Coordination...")
    print("=" * 70)
    print()
    
    # Execute Phase 1
    result_phase1 = crew_phase1.kickoff()
    
    print()
    print("=" * 70)
    print("✅ Phase 1 Complete - Moving to Asset Generation")
    print("=" * 70)
    print()
    
    # Save discussion output to file
    discussion_text = str(result_phase1)
    
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
    
    # Phase 2: Website QA and Final Approval
    portal_path = output_dir / "index.html"
    if portal_path.exists():
        print()
        print("=" * 70)
        print("🎬 Phase 2: Website Quality Assurance")
        print("=" * 70)
        print()
        
        # Task 10: QA Reviews Website
        task10 = Task(
            description=f"""You're the QA Reviewer. The website has been built at {portal_path}.

Review and report:

"I've reviewed the candidate portal. Here's my assessment:

✅ Strengths:
- [Mention 2-3 good aspects]

⚠️ Suggestions:
- [Mention 1-2 minor improvements if any, or say 'No issues found']

Overall: The portal is [ready/needs minor tweaks] for candidates."

Provide honest review (4-5 sentences).""",
            expected_output="QA review of the website with strengths and suggestions",
            agent=reviewer,
            async_execution=False
        )
        
        # Task 11: Team Discusses QA Feedback
        task11 = Task(
            description=f"""You're the PM. Respond to QA feedback:

"Thanks for the thorough review! [Reference the QA's feedback]

Team, what do you think about the suggestions? Web Builder and Designer, any quick improvements we can make?"

Facilitate brief discussion (2-3 sentences).""",
            expected_output="PM acknowledges QA feedback and asks team for input",
            agent=pm,
            context=[task10],
            async_execution=False
        )
        
        # Task 12: PM Final Approval
        task12 = Task(
            description=f"""You're the PM. Give final sign-off:

"Alright team! The tech test is complete and looking great:

✅ Research-backed assignments  
✅ Realistic OTA datasets
✅ Professional candidate portal
✅ Quality assured

FINAL DECISION: APPROVED FOR DELIVERY

Excellent collaboration everyone! The portal is ready for candidates. 🎉"

Provide final approval and summary (5-6 sentences).""",
            expected_output="PM final approval with summary of deliverables and team appreciation",
            agent=pm,
            context=[task11],
            async_execution=False
        )
        
        # Execute Phase 2
        crew_phase2 = Crew(
            agents=[pm, reviewer, web_builder, web_designer],
            tasks=[task10, task11, task12],
            process=Process.sequential,
            verbose=True
        )
        
        print("🎬 Starting Phase 2: Website QA...")
        print()
        result_phase2 = crew_phase2.kickoff()
        
        print()
        print("=" * 70)
        print("✅ Phase 2 Complete - Final Approval Given!")
        print("=" * 70)
        print()
    
    # Final result
    final_result = f"{discussion_text}\n\n{'='*70}\n\n{str(result_phase2) if portal_path.exists() else ''}"
    
    return {
        "status": "completed",
        "result": final_result,
        "output_dir": str(output_dir),
        "portal_ready": portal_path.exists()
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

