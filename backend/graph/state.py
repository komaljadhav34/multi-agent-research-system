from typing import TypedDict, List, Dict, Any

class ResearchState(TypedDict):
    """
    Defines the global state shared across all nodes in the multi-agent graph.
    """
    query: str
    plan: List[Dict[str, Any]]         # [{subtopic: str, intent: str, depth: str}]
    findings: List[Dict[str, Any]]     # [{subtopic: str, summaries: List[Dict], sources: List[Dict]}]
    critique: Dict[str, Any]           # {scores: Dict[str, int], gaps: List[str], retry_topics: List[str]}
    report: str                        # Final generated markdown report
    iterations: int                    # Critic feedback iteration count (max 2)
    session_id: str                    # Redis session ID for real-time memory
    status: str                        # Current running agent (planner, researcher, critic, writer, idle)
