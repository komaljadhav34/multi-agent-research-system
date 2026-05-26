import json
import logging
import asyncio
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.db.models import get_db, ResearchReport
from backend.memory.redis_store import redis_store
from backend.graph.pipeline import research_graph, route_after_critic
from backend.agents.planner import run_planner
from backend.agents.researcher import run_researcher
from backend.agents.critic import run_critic
from backend.agents.llm_client import call_llm_stream
from backend.tools.tavily_search import search_tavily
from backend.tools.web_scraper import store_and_query_vectors
from backend.agents.researcher import synthesize_subtopic_findings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")

class ResearchRequest(BaseModel):
    topic: str
    session_id: str

class DigDeeperRequest(BaseModel):
    subtopic: str
    instructions: str
    session_id: str

async def run_graph_and_stream(query: str, session_id: str, db: Session):
    """
    Executes each LangGraph node sequentially, maintaining state updates in Redis,
    and yielding Server-Sent Events (SSE) progress details to the client, including
    token-by-token markdown streaming.
    """
    try:
        # Initialize default state
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
        
        # 1. Start Planner Agent
        yield f"data: {json.dumps({'type': 'status', 'status': 'planner'})}\n\n"
        await asyncio.sleep(0.1) # Brief yield pause
        
        # Run node synchronously in threadpool to avoid blocking event loop
        planner_res = await asyncio.to_thread(run_planner, state)
        state.update(planner_res)
        redis_store.save_state(session_id, state)
        
        yield f"data: {json.dumps({'type': 'plan', 'plan': state['plan']})}\n\n"
        await asyncio.sleep(0.1)

        # 2. Researcher & Critic Loop (Max 2 iterations)
        max_loops = 2
        for loop_idx in range(max_loops):
            # Run Researcher Node
            yield f"data: {json.dumps({'type': 'status', 'status': 'researcher', 'iteration': loop_idx})}\n\n"
            await asyncio.sleep(0.1)
            
            researcher_res = await asyncio.to_thread(run_researcher, state)
            state.update(researcher_res)
            redis_store.save_state(session_id, state)
            
            yield f"data: {json.dumps({'type': 'findings', 'findings': state['findings']})}\n\n"
            await asyncio.sleep(0.1)
            
            # Run Critic Node
            yield f"data: {json.dumps({'type': 'status', 'status': 'critic', 'iteration': loop_idx})}\n\n"
            await asyncio.sleep(0.1)
            
            critic_res = await asyncio.to_thread(run_critic, state)
            state.update(critic_res)
            redis_store.save_state(session_id, state)
            
            yield f"data: {json.dumps({'type': 'critique', 'critique': state['critique'], 'iterations': state['iterations']})}\n\n"
            await asyncio.sleep(0.1)
            
            # Use compiled LangGraph routing logic
            next_node = route_after_critic(state)
            if next_node == "writer":
                break
                
            # If routing back to researcher, clear retry lists to avoid state leakage
            state["status"] = "researcher"

        # 3. Writer Node (Generates Streaming Tokens)
        yield f"data: {json.dumps({'type': 'status', 'status': 'writer'})}\n\n"
        await asyncio.sleep(0.1)
        
        # Compile prompts for writing phase
        from backend.agents.writer import generate_writer_prompt
        prompt, system_prompt = generate_writer_prompt(state["query"], state["plan"], state["findings"])
        
        full_report = ""
        # We call the Groq/Mock stream client to yield text tokens instantly
        for chunk in call_llm_stream(prompt, system_prompt=system_prompt):
            full_report += chunk
            yield f"data: {json.dumps({'type': 'report_chunk', 'content': chunk})}\n\n"
            
        state["report"] = full_report
        state["status"] = "idle"
        redis_store.save_state(session_id, state)
        
        # Save the finalized report into database for persistence
        db_report = ResearchReport(
            query=query,
            report_markdown=full_report,
            sources=[{
                "subtopic": f["subtopic"],
                "sources": f["sources"]
            } for f in state["findings"]]
        )
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        
        # Save report history mapping in session store
        redis_store.add_user_report("default_user", db_report.id)
        
        # Stream completion event
        yield f"data: {json.dumps({'type': 'done', 'report_id': db_report.id})}\n\n"
        
    except Exception as e:
        logger.error(f"Error in SSE research stream: {e}", exc_info=True)
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

@router.post("/research/stream")
async def stream_research(query: ResearchRequest, db: Session = Depends(get_db)):
    """
    Exposes a Server-Sent Events (SSE) streaming API to stream full-blueprint
    research logs, plans, scores, and real-time word-by-word content reports.
    """
    return StreamingResponse(
        run_graph_and_stream(query.topic, query.session_id, db),
        media_type="text/event-stream"
    )

@router.get("/history")
def get_research_history(db: Session = Depends(get_db)):
    """
    Fetches the history of saved research reports from SQLite/PostgreSQL database.
    """
    reports = db.query(ResearchReport).order_by(ResearchReport.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "query": r.query,
            "created_at": r.created_at.isoformat()
        }
        for r in reports
    ]

@router.get("/reports/{report_id}")
def get_report_details(report_id: str, db: Session = Depends(get_db)):
    """
    Retrieves full details (markdown text, references list) of a specific research report.
    """
    report = db.query(ResearchReport).filter(ResearchReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    return {
        "id": report.id,
        "query": report.query,
        "report_markdown": report.report_markdown,
        "sources": report.sources,
        "created_at": report.created_at.isoformat()
    }

async def run_dig_deeper_stream(report_id: str, subtopic: str, instructions: str, session_id: str, db: Session):
    """
    Asynchronous executor that runs targeted research on an existing section,
    re-synthesis, rewrites that report section, and streams progress chunks back.
    """
    try:
        # Load original report
        report = db.query(ResearchReport).filter(ResearchReport.id == report_id).first()
        if not report:
            yield f"data: {json.dumps({'type': 'error', 'message': 'Report not found'})}\n\n"
            return
            
        yield f"data: {json.dumps({'type': 'status', 'status': 'researcher'})}\n\n"
        await asyncio.sleep(0.1)
        
        # 1. Run targeted search
        print(f"🔄 Targeted Deep Research: Sourcing additional info for '{subtopic}' with details '{instructions}'")
        search_results = await asyncio.to_thread(search_tavily, f"{report.query} {subtopic} {instructions}", max_results=3)
        
        # 2. Vector indexing
        vector_contexts = await asyncio.to_thread(store_and_query_vectors, subtopic, search_results, top_k=3)
        
        # 3. Synthesize deeper findings
        synthesis = await asyncio.to_thread(synthesize_subtopic_findings, subtopic, instructions, vector_contexts)
        
        # 4. Stream updated Writer tokens
        yield f"data: {json.dumps({'type': 'status', 'status': 'writer'})}\n\n"
        await asyncio.sleep(0.1)
        
        system_prompt = (
            "You are a Senior Editor. You are updating a section of an existing research report.\n"
            "Integrate the deep-dive research instructions and new findings into the existing text.\n"
            "Return only the REVISED section text, including updated inline citation markdown links. Make it highly professional."
        )
        prompt = (
            f"Original Query: \"{report.query}\"\n"
            f"Section Subtopic: \"{subtopic}\"\n"
            f"User Deepen Instructions: \"{instructions}\"\n"
            f"New Sourced Findings: {synthesis['summary']}\n"
            f"Key Verified Points: {synthesis['key_points']}"
        )
        
        revised_section = ""
        for chunk in call_llm_stream(prompt, system_prompt=system_prompt):
            revised_section += chunk
            yield f"data: {json.dumps({'type': 'report_chunk', 'content': chunk})}\n\n"
            
        # Update original report text locally
        # Look for the H2 subtopic block and replace it, or append the revised section
        # For simplicity and robustness, we can append a H2 'Deep-Dive: [Subtopic]' section to the original markdown report
        depth_block = f"\n\n## Deep-Dive Focus: {subtopic}\n\n**Deepen Context:** *{instructions}*\n\n{revised_section}\n"
        
        updated_markdown = report.report_markdown + depth_block
        report.report_markdown = updated_markdown
        db.commit()
        
        yield f"data: {json.dumps({'type': 'done', 'report_id': report.id})}\n\n"
        
    except Exception as e:
        logger.error(f"Error in dig-deeper stream: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

@router.post("/reports/{report_id}/dig-deeper")
async def dig_deeper(report_id: str, request: DigDeeperRequest, db: Session = Depends(get_db)):
    """
    Executes a targeted search and rewrite to deepen a specific section
    of an existing report, streaming updates back in real-time.
    """
    return StreamingResponse(
        run_dig_deeper_stream(report_id, request.subtopic, request.instructions, request.session_id, db),
        media_type="text/event-stream"
    )
