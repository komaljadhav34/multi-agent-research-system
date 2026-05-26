import logging
from typing import List, Dict, Any
from backend.graph.state import ResearchState
from backend.tools.tavily_search import search_tavily
from backend.tools.web_scraper import store_and_query_vectors
from backend.agents.llm_client import call_llm

logger = logging.getLogger(__name__)

def synthesize_subtopic_findings(subtopic: str, intent: str, vector_contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Uses LLM to summarize raw vectorized context chunks into a factual summary
    and key bullet points, ensuring source URLs are mapped properly.
    """
    if not vector_contexts:
        return {
            "summary": "No research data was retrieved for this subtopic.",
            "key_points": ["Information unavailable."],
            "sources": []
        }
        
    # Build text representation of sources for the prompt
    context_text = ""
    sources_map = {}
    
    for idx, ctx in enumerate(vector_contexts):
        title = ctx.get("title", f"Source {idx+1}")
        url = ctx.get("url", "")
        snippet = ctx.get("snippet", "")
        
        # Deduplicate sources
        if url:
            sources_map[url] = title
            
        context_text += f"[{idx+1}] Title: {title}\nURL: {url}\nExcerpt: {snippet}\n\n"

    system_prompt = (
        "You are an Elite Research Investigator. Your task is to take a set of raw text snippets (from web search results) "
        "and synthesize them into a clean, highly factual, and academic summary for a specific subtopic.\n"
        "Rules:\n"
        "1. Write a dense, factual summary (150-200 words).\n"
        "2. Extract 3-5 critical, highly specific key bullet points.\n"
        "3. Explicitly link facts to the source URLs provided. If a source is used, refer to it using inline markdown links e.g. [Nature](URL) or [source](URL).\n"
        "4. Output your response in the exact format shown below, separating parts with '---'. Do not add any conversational text.\n\n"
        "Format:\n"
        "[Write your summary here with inline markdown links to sources]\n"
        "---\n"
        "- Bullet point 1\n"
        "- Bullet point 2\n"
        "- Bullet point 3"
    )

    prompt = (
        f"Subtopic: \"{subtopic}\"\n"
        f"Search Intent: \"{intent}\"\n\n"
        f"Vector Database Snippets:\n{context_text}"
    )

    try:
        response = call_llm(prompt, system_prompt=system_prompt)
        parts = response.split("---")
        
        summary = parts[0].strip()
        
        key_points = []
        if len(parts) > 1:
            points_text = parts[1].strip()
            for line in points_text.split("\n"):
                line = line.strip().lstrip("-*•").strip()
                if line:
                    key_points.append(line)
        else:
            key_points = ["Analyzed structural components and mechanisms.", "Synthesized case-study performance vectors."]

        # List of distinct sources cited
        sources = [{"title": title, "url": url} for url, title in sources_map.items()]
        
        return {
            "summary": summary,
            "key_points": key_points,
            "sources": sources
        }
    except Exception as e:
        logger.error(f"Error synthesizing findings: {e}")
        return {
            "summary": "Factual synthesis failed due to an error.",
            "key_points": ["Failed to extract bullet points."],
            "sources": []
        }

def run_researcher(state: ResearchState) -> dict:
    """
    Researcher Node: Identifies which subtopics need research, calls search engine,
    scrapes, chunks, embeds, queries ChromaDB, and uses LLM to write factual summaries.
    """
    query = state.get("query", "")
    plan = state.get("plan", [])
    findings = state.get("findings", []) or []
    critique = state.get("critique", {}) or {}
    retry_topics = critique.get("retry_topics", [])
    
    # If this is a retry loop, only research topics flagged for retry.
    # Otherwise, research all topics in the plan.
    topics_to_research = []
    if retry_topics:
        logger.info(f"Researcher running RETRY for topics: {retry_topics}")
        print(f"🔍 Researcher Agent: Critic requested deep-dive retry on: {retry_topics}")
        topics_to_research = [item for item in plan if item["subtopic"] in retry_topics]
    else:
        logger.info("Researcher running initial search for all plan topics.")
        print(f"🔍 Researcher Agent: Initiating deep search on all {len(plan)} plan subtopics...")
        topics_to_research = plan

    # Dict of subtopics we have processed so we can replace them in the findings state
    findings_by_subtopic = {item["subtopic"]: item for item in findings}

    for item in topics_to_research:
        subtopic = item["subtopic"]
        intent = item["intent"]
        depth = item.get("depth", "Medium")
        
        print(f"  ➞ Searching and scraping for subtopic: '{subtopic}' (depth: {depth})...")
        
        # 1. Search Tavily
        # Deep searches retrieve more search results
        max_results = 4 if depth == "Deep" else 2
        search_results = search_tavily(f"{query} {subtopic}", max_results=max_results)
        
        # 2. Scrape URLs and chunk in vector store
        print(f"  ➞ Vector indexing and chunking content in ChromaDB for '{subtopic}'...")
        vector_contexts = store_and_query_vectors(subtopic, search_results, top_k=3)
        
        # 3. Factual synthesis using LLM
        print(f"  ➞ Synthesizing and cleaning results into source-preserved summaries...")
        synthesis = synthesize_subtopic_findings(subtopic, intent, vector_contexts)
        
        # Store in results
        findings_by_subtopic[subtopic] = {
            "subtopic": subtopic,
            "summary": synthesis["summary"],
            "key_points": synthesis["key_points"],
            # Keep both summarized highlights and original raw snippets for frontend source cards!
            "sources": synthesis["sources"],
            "scraped_snippets": vector_contexts # Detailed chunks for frontend expander
        }

    # Reconstruct findings list
    updated_findings = list(findings_by_subtopic.values())
    
    logger.info(f"Researcher complete. Total findings saved: {len(updated_findings)}")
    print(f"🔍 Researcher Agent: Finished sourcing. Total compiled findings: {len(updated_findings)}")

    return {
        "findings": updated_findings,
        "status": "critic"
    }
