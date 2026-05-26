import logging
from langgraph.graph import StateGraph, END
from backend.graph.state import ResearchState
from backend.agents.planner import run_planner
from backend.agents.researcher import run_researcher
from backend.agents.critic import run_critic
from backend.agents.writer import run_writer

logger = logging.getLogger(__name__)

def route_after_critic(state: ResearchState) -> str:
    """
    State router function: Evaluates the Critique output. If any topics are
    flagged for deep retries and we have not exceeded our maximum loop budget
    (2 iterations), routes back to the Researcher agent. Otherwise, forwards
    to the Writer agent.
    """
    critique = state.get("critique", {}) or {}
    retry_topics = critique.get("retry_topics", [])
    iterations = state.get("iterations", 0)
    
    if retry_topics and iterations < 2:
        logger.info(f"LangGraph routing: Loop back to RESEARCHER. Retry topics: {retry_topics}")
        return "researcher"
        
    logger.info("LangGraph routing: Forward to WRITER.")
    return "writer"

def create_research_graph():
    """
    Compiles and constructs the cyclical Multi-Agent State Graph.
    """
    # 1. Initialize workflow with global State Typings
    workflow = StateGraph(ResearchState)
    
    # 2. Add our specialized agent nodes
    workflow.add_node("planner", run_planner)
    workflow.add_node("researcher", run_researcher)
    workflow.add_node("critic", run_critic)
    workflow.add_node("writer", run_writer)
    
    # 3. Establish Entrypoint node
    workflow.set_entry_point("planner")
    
    # 4. Set static paths
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "critic")
    
    # 5. Define cyclical conditional path from Critic
    workflow.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "researcher": "researcher",
            "writer": "writer"
        }
    )
    
    # 6. Terminal edge to END execution
    workflow.add_edge("writer", END)
    
    # Compile
    return workflow.compile()

# Global Compiled Pipeline
research_graph = create_research_graph()
