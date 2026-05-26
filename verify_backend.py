import sys
import os
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass
import json

# Ensure parent directory is in path so we can import backend packages
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.db.models import init_db, SessionLocal
from backend.graph.pipeline import research_graph, route_after_critic
from backend.agents.planner import run_planner
from backend.agents.researcher import run_researcher
from backend.agents.critic import run_critic
from backend.agents.writer import run_writer
from backend.memory.redis_store import redis_store

def run_diagnostic():
    print("=================================================")
    print("[RUN] MULTI-AGENT RESEARCH BACKEND DIAGNOSTIC RUN")
    print("=================================================")
    
    # 1. Initialize DB
    print("\n[Step 1] Initializing SQLite database...")
    init_db()
    db = SessionLocal()
    print("[OK] Database initialized successfully.")
    
    # 2. Formulate Initial State
    query = "Impact of AI in clinical healthcare 2026"
    session_id = "diagnostic_session_999"
    state = {
        "query": query,
        "plan": [],
        "findings": [],
        "critique": {},
        "report": "",
        "iterations": 0,
        "session_id": session_id,
        "status": "planner"
    }
    print(f"\n[Step 2] Initializing ResearchState for topic: '{query}'")
    redis_store.save_state(session_id, state)
    
    # 3. Test Planner Node
    print("\n[Step 3] Executing Planner Node...")
    planner_res = run_planner(state)
    state.update(planner_res)
    redis_store.save_state(session_id, state)
    print(f"[OK] Planner finished. Subtopics generated:")
    for idx, p in enumerate(state["plan"]):
        print(f"  {idx+1}. {p['subtopic']} (Depth: {p['depth']})")
        
    # 4. Test Researcher Node (Iteration 0)
    print("\n[Step 4] Executing Researcher Node (First Pass)...")
    researcher_res = run_researcher(state)
    state.update(researcher_res)
    redis_store.save_state(session_id, state)
    print(f"[OK] Researcher finished. compiled {len(state['findings'])} subtopic finding structures.")
    
    # 5. Test Critic Node
    print("\n[Step 5] Executing Critic Node (Iteration 0)...")
    critic_res = run_critic(state)
    state.update(critic_res)
    redis_store.save_state(session_id, state)
    
    # 6. Check Routing Decisions
    print("\n[Step 6] Testing Graph Router Logic...")
    next_node = route_after_critic(state)
    print(f"[OK] Critic Evaluation Scores: {state['critique']['scores']}")
    print(f"[OK] Critic Flagged Gaps: {state['critique']['gaps']}")
    print(f"[OK] Critic Flagged Retries: {state['critique']['retry_topics']}")
    print(f"[NEXT] LangGraph Next Edge Target Selection: '{next_node}'")
    
    # 7. Simulate Loop Iteration if needed (Mock mode iteration 0 triggers a retry)
    if next_node == "researcher":
        print("\n[Loop Simulation] Re-running Researcher for flagged retries...")
        researcher_res = run_researcher(state)
        state.update(researcher_res)
        
        print("\n[Loop Simulation] Re-running Critic (Iteration 1)...")
        critic_res = run_critic(state)
        state.update(critic_res)
        next_node = route_after_critic(state)
        print(f"[OK] Iteration 1 Scores: {state['critique']['scores']}")
        print(f"[NEXT] Next Edge Target Selection after retry: '{next_node}'")
 
    # 8. Test Writer Node
    print("\n[Step 7] Executing Writer Node...")
    writer_res = run_writer(state)
    state.update(writer_res)
    print("[OK] Writer finished compiling final report.")
    
    # Showcase report snippet
    print("\n================ REPORT PREVIEW =================\n")
    report_lines = state["report"].split("\n")
    for line in report_lines[:15]:
        print(line)
    print("\n... [Report Truncated] ...")
    print("\n=================================================")
    print("[SUCCESS] BACKEND AGENT PIPELINE DIAGNOSTIC COMPLETED SUCCESSFULLY!")
    print("=================================================")
    
    db.close()

if __name__ == "__main__":
    run_diagnostic()
