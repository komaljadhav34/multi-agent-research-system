import json
import logging
from backend.graph.state import ResearchState
from backend.agents.llm_client import call_llm, clean_json_string

logger = logging.getLogger(__name__)

def run_planner(state: ResearchState) -> dict:
    """
    Planner Node: Takes the raw user query, analyzes it, and generates a structured
    research plan containing 4-6 subtopics, search intents, and target depths.
    """
    query = state.get("query", "")
    logger.info(f"Planner Agent starting for query: '{query}'")
    print(f"🧩 Planner Agent: Analyzing and breaking down topic: '{query}'...")
    
    # Prompt instructing chain-of-thought and strict JSON array output
    system_prompt = (
        "You are an expert Strategic Research Planner. Your job is to take a raw user query "
        "and break it down into 4 to 6 distinct, structured subtopics to build a comprehensive report.\n"
        "You must return ONLY a JSON array matching the schema below. Do not include markdown wraps or other text.\n\n"
        "Schema:\n"
        "[\n"
        "  {\n"
        "    \"subtopic\": \"Subtopic Title\",\n"
        "    \"intent\": \"Specific search intent and goals for this subtopic\",\n"
        "    \"depth\": \"Deep\" or \"Medium\"\n"
        "  }\n"
        "]"
    )
    
    prompt = f"Create a structured research plan for the query: \"{query}\". Ensure subtopics cover foundational concepts, implementation details, real-world case studies, and compliance/safety issues."
    
    try:
        response_text = call_llm(prompt, system_prompt=system_prompt, json_mode=True)
        response_text = clean_json_string(response_text)
        plan = json.loads(response_text)
        
        # Ensure it's a list
        if not isinstance(plan, list):
            plan = [plan]
            
        logger.info(f"Planner generated {len(plan)} subtopics.")
        print(f"🧩 Planner Agent completed. Structured plan with {len(plan)} subtopics created.")
        
        # Return state update dictionary
        return {
            "plan": plan,
            "status": "researcher"
        }
    except Exception as e:
        logger.error(f"Error in Planner Agent: {e}")
        # Fallback basic plan in case of json parse issues
        fallback_plan = [
            {"subtopic": f"Overview of {query}", "intent": "Initial foundation search", "depth": "Deep"},
            {"subtopic": f"Core mechanics and technologies in {query}", "intent": "Analyze structural details", "depth": "Deep"},
            {"subtopic": f"Challenges and hurdles in {query}", "intent": "Analyze key pain-points", "depth": "Medium"},
            {"subtopic": f"Future outlook and regulations in {query}", "intent": "Review policy and tomorrow's trends", "depth": "Medium"}
        ]
        return {
            "plan": fallback_plan,
            "status": "researcher"
        }
