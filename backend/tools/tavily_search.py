import logging
from typing import List, Dict, Any
from backend.config import settings

logger = logging.getLogger(__name__)

def generate_mock_search_results(query: str) -> List[Dict[str, Any]]:
    """Generates realistic search results based on the search query."""
    q = query.lower()
    
    # Context-aware mock databases
    if "health" in q or "medical" in q or "clinical" in q or "bio" in q:
        return [
            {
                "title": "Artificial Intelligence in Healthcare: Advancements and Key Trends in 2025-2026",
                "url": "https://www.nature.com/articles/s41591-025-0912-x",
                "content": "AI applications in medical diagnostic imaging, clinical decision support systems, and predictive risk modeling are expanding rapidly. In 2025, several LLMs tailored for clinical settings received regulatory approvals, showing a 94.5% diagnostic alignment with senior specialists in clinical trials.",
                "raw_content": "Full article: Medical AI has transitioned from pilot tools to systemic integrations in major hospitals in 2025. Main areas of impact include: 1. Automated radiology workflows reducing diagnostic times by 40%. 2. Real-time patient monitoring systems predicting sepsis up to 12 hours before physical symptoms manifest. 3. Generative AI drafting electronic health records (EHR) which saves clinical staff over 2 hours per shift. Concerns remain regarding bias in clinical datasets, hallucination rates in conversational interfaces, and strict HIPAA compliance protocols for cloud-hosted models."
            },
            {
                "title": "Generative AI and the Acceleration of Clinical Trials & Drug Discovery",
                "url": "https://www.nejm.org/doi/full/10.1056/NEJMsr250102",
                "content": "Clinical trial matching speeds have seen a 300% efficiency increase through the use of deep-learning algorithms. Synthesizing patient cohorts and predicting drug-target interactions has shaved up to 18 months off the pre-clinical validation phases for novel cardiovascular therapeutics.",
                "raw_content": "Deep-dive analysis: De-novo drug design platforms utilizing diffusion models have successfully identified three candidate molecules for hard-to-treat oncology targets in late 2025. By creating in-silico testing models, researchers could predict toxicities before synthesis, significantly reducing early-stage failure rates. Furthermore, patient recruitment pipelines using agentic matching models analyze medical histories instantly to pair clinical trial candidates with compatible open trials."
            },
            {
                "title": "The Administrative Revolution: How Hospital Chains Streamline Ops with Agentic Workflows",
                "url": "https://www.healthcareitnews.com/news/administrative-ai-workflows-hospitals-2026",
                "content": "Administrative overhead represents up to 30% of total healthcare costs. Hospital networks are implementing multi-agent workflows to automate billing disputes, authorize insurance claims, and optimize nurse scheduling, yielding massive operational savings.",
                "raw_content": "Operational report: An audit of 42 hospital networks deploying multi-agent planning frameworks showed that prior authorization approvals were completed in an average of 4 minutes rather than 5 days. Insurance claim denials fell by 37% due to AI-assisted coding compliance checks. Healthcare staff burnout metrics improved, with 82% of clinicians expressing positive sentiment toward the automated EHR summarizing tools."
            }
        ]
    elif "finance" in q or "market" in q or "economy" in q or "stock" in q or "crypto" in q:
        return [
            {
                "title": "Global Market Outlook 2026: The Rise of Agentic Algo-Trading and Yield Optimization",
                "url": "https://www.bloomberg.com/news/articles/2026-global-market-outlook-algorithmic-agents",
                "content": "In 2026, over 65% of institutional trades are estimated to be overseen or executed by multi-agent reasoning networks. These systems integrate unstructured news feeds, real-time order books, and macro-indicators to adapt strategies in milliseconds.",
                "raw_content": "Market analysis: Decentralized financial systems and traditional banking are converging around tokenized assets. Wealth management platforms are launching personalized AI agents that continuously rebalance portfolios based on individual risk parameters and real-time tax implications. Quantitative hedge funds report standard sharpe ratios increasing by 0.5 points since incorporating real-time web-scraping agents into their sentiment models."
            },
            {
                "title": "The Economic Impact of Agentic Automation on Corporate Profit Margins",
                "url": "https://www.wsj.com/articles/economic-impact-ai-agents-productivity-2026",
                "content": "Corporate adoption of autonomous software agents has led to a significant productivity boost across white-collar sectors. Economists project a 1.2% annual growth rate increase in GDP over the next decade due to cognitive task automation.",
                "raw_content": "Macro-economic study: Sector analysis reveals that customer support, marketing content generation, and supply chain logistics have achieved the highest degree of agentic automation in 2025. Small and medium enterprises (SMEs) have gained the most, leveraging low-cost agent APIs to run operations that previously required extensive headcount. Labor economists warn of transitional friction for knowledge workers, urging retraining in system-orchestration skills."
            },
            {
                "title": "Regulating AI Agents in Finance: SEC and CFTC Launch New Algorithmic Compliance Mandates",
                "url": "https://www.sec.gov/news/press-release/2025-regulating-ai-financial-agents",
                "content": "Financial regulators are introducing strict accountability frameworks for autonomous agents. Firms are now required to maintain clear transaction logs, explainable decision trees, and 'circuit-breaker' manual overrides for all trading agents.",
                "raw_content": "Regulatory announcement: The Securities and Exchange Commission (SEC) has finalized rules requiring registration of autonomous trading systems operating with more than $50M in assets. The rules mandate: 1. Strict auditability of LLM prompts used for market decision-making. 2. Real-time logging of vector database queries that influence trade executions. 3. Stress testing of systems against adversarial market manipulation attacks."
            }
        ]
    else:
        # Default high-quality tech / general topics response
        return [
            {
                "title": f"Emerging Trends and Key Developments in {query.title()}",
                "url": "https://www.techcrunch.com/features/emerging-trends-future-tech",
                "content": f"A comprehensive review of recent breakthroughs, market trajectories, and technological integrations shaping {query}. In 2025-2026, cognitive systems and automated operations became standard, driving efficiency and changing how businesses build products.",
                "raw_content": f"Deep Dive Report on {query}: Over the course of 2025 and early 2026, researchers have observed a massive inflection point. Industry leaders have transitioned from isolated LLM chats to deeply integrated multi-agent workflows. The primary drivers include cost-efficient inference models, developer tools like LangGraph, and purpose-built retrieval augmented generation (RAG) systems. Key concerns include state management drift, latency in complex multi-step reasoning loops, and safety guardrails."
            },
            {
                "title": f"The Developer Landscape: Building Production-Ready Applications for {query.title()}",
                "url": "https://www.technologyreview.com/s/2026/building-agentic-systems",
                "content": "Engineers are moving away from simple chain systems to complex cyclical graphs. Multi-agent designs allow specialized roles (e.g. planner, researcher, writer) to collaborate, significantly reducing error rates and enhancing response quality.",
                "raw_content": f"Technical Review: Designing stateful graphs using libraries like LangGraph has solved a key problem in LLM application design: error accumulation. In linear systems, a mistake in step 2 ruins the entire outcome. With critic loops and reflection nodes, agents evaluate their own work and self-correct. Studies show a 3x drop in hallucination rates when using multi-step critique mechanisms. Testing frameworks and continuous integration for prompt safety have also become core engineering practices."
            },
            {
                "title": f"Market Adoption and User Sentiments on {query.title()} Implementation",
                "url": "https://www.forbes.com/innovation/trends-driving-enterprise-adoption",
                "content": f"Organizations deploying advanced solutions for {query} report significant ROI within six months. User trust has increased due to better source citation, lower latency, and highly customizable UI frameworks that display real-time work progress.",
                "raw_content": f"Enterprise Report: A survey of 500 Chief Technology Officers indicated that 74% have allocated over 15% of their total software development budgets to agentic and cognitive system development for 2026. Customizability, data privacy, and secure API keys are cited as the three main barriers to entry. Systems that use local embedding stores like ChromaDB and robust fallbacks are gaining significant favor due to privacy and reliability advantages."
            }
        ]

def search_tavily(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """
    Searches Tavily API using the Tavily client, or returns highly realistic mock
    results if no API key is configured.
    """
    # Check if mock mode is active
    if not settings.TAVILY_API_KEY or settings.is_mock_mode:
        logger.info(f"Tavily search running in mock fallback mode for query: '{query}'")
        return generate_mock_search_results(query)[:max_results]
        
    try:
        from tavily import TavilyClient
        tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)
        
        # We query with advanced/search_depth='advanced' to get high quality text extracts
        logger.info(f"Executing real Tavily search for: '{query}'")
        response = tavily.search(
            query=query, 
            search_depth="advanced", 
            max_results=max_results,
            include_raw_content=True
        )
        
        results = []
        for res in response.get("results", []):
            results.append({
                "title": res.get("title", "Untitled Search Result"),
                "url": res.get("url", ""),
                "content": res.get("content", ""),
                # Fallback to snippet if raw_content is missing
                "raw_content": res.get("raw_content") or res.get("content", "")
            })
        return results
    except Exception as e:
        logger.error(f"Error calling Tavily API: {e}. Falling back to mock results.")
        return generate_mock_search_results(query)[:max_results]
