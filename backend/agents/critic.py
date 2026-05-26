import json
import logging
from backend.graph.state import ResearchState
from backend.agents.llm_client import call_llm, clean_json_string

logger = logging.getLogger(__name__)

def run_critic(state: ResearchState) -> dict:
    """
    Critic Node: Analyzes researcher findings, evaluates them for relevance, accuracy,
    and coverage, assigns quality scores (1-5), identifies missing details, and
    flags subtopics requiring research retries.
    """
    query = state.get("query", "")
    findings = state.get("findings", [])
    iterations = state.get("iterations", 0)
    
    logger.info(f"Critic Agent starting. Current iteration: {iterations}")
    print(f"⚖️ Critic Agent: Reviewing {len(findings)} research findings. Loop iteration: {iterations}...")
    
    # Format researcher summaries to feed into the critic prompt
    findings_summary = ""
    for idx, f in enumerate(findings):
        findings_summary += f"[{idx}] Subtopic: \"{f['subtopic']}\"\n"
        findings_summary += f"Summary: {f['summary']}\n"
        findings_summary += f"Key Bullet Points: {', '.join(f['key_points'])}\n\n"

    system_prompt = (
        "You are an Elite Academic Critic and Fact Checker. Your task is to evaluate a set of research findings against the overall query.\n"
        "You must analyze each finding and return a strict JSON object containing:\n"
        "1. 'scores': A dictionary mapping each subtopic title to a relevance and depth score from 1 (poor/shallow) to 5 (excellent/deep).\n"
        "2. 'gaps': A list of string descriptions detailing specific information gaps or factual contradictions found in the material.\n"
        "3. 'retry_topics': A list of subtopic titles that score lower than 3 and require a deeper search retry. If all are sufficient, return an empty list.\n\n"
        "Important rules:\n"
        "- If it is the first loop (iteration = 0), be very rigorous! Flag at least one weak or shallow subtopic for retry to ensure comprehensive coverage, providing detailed feedback on what is missing.\n"
        "- If it is the second loop (iteration >= 1), be lenient. Accept findings unless there are severe failures.\n\n"
        "Output ONLY valid JSON. Do not include markdown headers or other text.\n\n"
        "Schema:\n"
        "{\n"
        "  \"scores\": {\n"
        "    \"Subtopic Title 1\": 5,\n"
        "    \"Subtopic Title 2\": 2\n"
        "  },\n"
        "  \"gaps\": [\"Explanation of missing context in Title 2\"],\n"
        "  \"retry_topics\": [\"Subtopic Title 2\"]\n"
        "}"
    )

    prompt = (
        f"Overall Query: \"{query}\"\n"
        f"Iteration Code: \"iteration: {iterations}\"\n\n"
        f"Researcher Compiled Findings:\n{findings_summary}"
    )

    try:
        response_text = call_llm(prompt, system_prompt=system_prompt, json_mode=True)
        response_text = clean_json_string(response_text)
        critique = json.loads(response_text)
        
        scores = critique.get("scores", {})
        retry_topics = critique.get("retry_topics", [])
        gaps = critique.get("gaps", [])
        
        # Enforce maximum of 2 iterations to prevent infinite search loops
        if iterations >= 2:
            logger.info("Maximum iterations (2) reached. Forcing transition to Writer.")
            print("⚖️ Critic Agent: Maximum feedback loops reached (2). Approving all research.")
            retry_topics = []
            critique["retry_topics"] = []
            
        new_iterations = iterations + 1
        
        # Determine next agent status update
        next_status = "researcher" if retry_topics else "writer"
        
        print(f"⚖️ Critic Agent completed:")
        print(f"  ➞ Scores: {scores}")
        if retry_topics:
            print(f"  ➞ ⚠️ Gaps found: {gaps}")
            print(f"  ➞ 🔄 Flagged for deeper search: {retry_topics}")
        else:
            print("  ➞ ✅ All subtopics approved! Ready for writing phase.")

        return {
            "critique": critique,
            "iterations": new_iterations,
            "status": next_status
        }
    except Exception as e:
        logger.error(f"Error in Critic Agent: {e}")
        # Default fallback approval to prevent stuck graph
        fallback_critique = {
            "scores": {f["subtopic"]: 5 for f in findings},
            "gaps": [],
            "retry_topics": []
        }
        return {
            "critique": fallback_critique,
            "iterations": iterations + 1,
            "status": "writer"
        }
