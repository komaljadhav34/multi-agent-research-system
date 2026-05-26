import logging
from backend.graph.state import ResearchState
from backend.agents.llm_client import call_llm

logger = logging.getLogger(__name__)

def generate_writer_prompt(query: str, plan: list, findings: list) -> tuple[str, str]:
    """Generates the prompt and system prompt for the report Writer."""
    
    # Compile a detailed presentation of all research gathered
    findings_compiled = ""
    for idx, f in enumerate(findings):
        findings_compiled += f"### Subtopic: {f['subtopic']}\n"
        findings_compiled += f"Factual Summary: {f['summary']}\n"
        findings_compiled += "Key Verified Points:\n"
        for pt in f.get("key_points", []):
            findings_compiled += f"- {pt}\n"
        
        findings_compiled += "Available Source Citations:\n"
        for src in f.get("sources", []):
            findings_compiled += f"  - Title: {src.get('title')}, URL: {src.get('url')}\n"
        findings_compiled += "\n"

    system_prompt = (
        "You are the Lead Technical Science Writer and Research Synthesizer. Your task is to write a highly premium, "
        "comprehensive Executive Research Report based on the compiled findings and the original plan.\n\n"
        "Your report MUST strictly adhere to the following formatting guidelines:\n"
        "1. Write a clear, engaging main Title (H1) based on the overall query.\n"
        "2. Break down the report into logical numbered H2 sections corresponding to the subtopics.\n"
        "3. Include a professional HTML/Markdown Table comparing key attributes, statistics, or metrics mentioned in the findings.\n"
        "4. Synthesize and expand on the factual summaries and bullet points. Never just copy and paste them; weave them into a premium narrative.\n"
        "5. Use GitHub Markdown Alert Callouts strategically (e.g. `> [!TIP]`, `> [!NOTE]`, or `> [!IMPORTANT]`) to highlight key action points.\n"
        "6. STRICT REQUIREMENT: Integrate inline citations using brackets e.g. [1], [2], [3] that directly map to the urls.\n"
        "7. End the report with a dedicated '## References' section listing each unique URL used, formatted exactly as: \n"
        "   - [1] Title of Source: URL\n\n"
        "Do not include any conversational meta-text before or after the report. Start immediately with the Markdown Title H1."
    )

    prompt = (
        f"Original Research Query: \"{query}\"\n\n"
        f"Original Plan Structure:\n{plan}\n\n"
        f"Verified Researcher Findings:\n{findings_compiled}"
    )
    
    return prompt, system_prompt

def run_writer(state: ResearchState) -> dict:
    """
    Writer Node: Takes all accumulated approved findings, formats the compilation prompt,
    generates the complete Markdown report, and returns it to finalize the state.
    """
    query = state.get("query", "")
    plan = state.get("plan", [])
    findings = state.get("findings", [])
    
    logger.info(f"Writer Agent starting for query: '{query}'")
    print(f"✍️ Writer Agent: Synthesizing final comprehensive report for: '{query}'...")
    
    prompt, system_prompt = generate_writer_prompt(query, plan, findings)
    
    try:
        report = call_llm(prompt, system_prompt=system_prompt)
        logger.info("Writer generated final report successfully.")
        print("✍️ Writer Agent: Report generated successfully.")
        return {
            "report": report,
            "status": "idle"
        }
    except Exception as e:
        logger.error(f"Error in Writer Agent: {e}")
        fallback_report = f"# Executive Report: {query}\n\nFailed to compile the final report. Findings are preserved in history."
        return {
            "report": fallback_report,
            "status": "idle"
        }
