import React, { useState, useEffect } from "react"
import { useSSE } from "./hooks/useSSE"
import AgentStatusPanel from "./components/AgentStatusPanel"
import StreamingReport from "./components/StreamingReport"
import SourceCards from "./components/SourceCards"
import { 
  Compass, 
  Search, 
  RotateCcw, 
  Layers, 
  History, 
  TrendingUp, 
  BookOpen, 
  FileCheck,
  ChevronRight,
  GitBranch,
  Settings
} from "lucide-react"

const BACKEND_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

export default function App() {
  const {
    status,
    plan,
    findings,
    critique,
    report,
    setReport,
    isStreaming,
    error,
    currentReportId,
    executeResearch,
    executeDigDeeper,
    abortActiveStream
  } = useSSE()

  const [query, setQuery] = useState("")
  const [history, setHistory] = useState([])
  const [selectedSubtopic, setSelectedSubtopic] = useState("")
  const [digInstructions, setDigInstructions] = useState("")

  // Fetch report history list on load
  const fetchHistory = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/history`)
      if (res.ok) {
        const data = await res.json()
        setHistory(data)
      }
    } catch (err) {
      console.error("Failed to fetch search history: ", err)
    }
  }

  useEffect(() => {
    fetchHistory()
  }, [currentReportId])

  // Trigger search execution
  const handleSearchSubmit = (e) => {
    e.preventDefault()
    if (!query.trim()) return
    executeResearch(query)
  }

  // Restore history item details
  const loadHistoricalReport = async (id) => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/reports/${id}`)
      if (res.ok) {
        const data = await res.json()
        
        // Populate states dynamically to mock a reinstantiated graph
        setReport(data.report_markdown)
        
        const restoredSources = data.sources || []
        
        // Reconstruct plan list based on sources H2 titles
        setPlan(restoredSources.map((item) => ({
          subtopic: item.subtopic,
          intent: `Explore detailed insights on ${item.subtopic}.`,
          depth: "Deep"
        })))
        
        // Reconstruct findings
        setFindings(restoredSources.map((item) => ({
          subtopic: item.subtopic,
          sources: item.sources || [],
          scraped_snippets: (item.sources || []).map((s) => ({
            title: s.title,
            url: s.url,
            snippet: "Restored from database records.",
            relevance_score: 0.95
          }))
        })))
        
        // Clear runtime critique and reset status
        abortActiveStream()
      }
    } catch (err) {
      console.error("Failed to restore history report: ", err)
    }
  }

  // Dig deeper targeted execution
  const handleDigDeeperSubmit = (e) => {
    e.preventDefault()
    if (!currentReportId || !selectedSubtopic || !digInstructions.trim()) return
    executeDigDeeper(currentReportId, selectedSubtopic, digInstructions)
    // Clear inputs
    setDigInstructions("")
  }

  return (
    <div className="flex h-screen bg-[#030712] text-gray-100 overflow-hidden font-sans">
      {/* 1. Left Sidebar History Panel */}
      <aside className="w-80 border-r border-gray-900 bg-gray-950/70 backdrop-blur-xl flex flex-col shrink-0 z-10">
        {/* Header Title */}
        <div className="p-6 border-b border-gray-900 flex items-center gap-2">
          <GitBranch className="w-5 h-5 text-indigo-400 stroke-[2]" />
          <span className="font-extrabold text-md tracking-wider bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-cyan-400 uppercase">
            CogniResearch Graph
          </span>
        </div>

        {/* Saved Research History */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          <div className="space-y-3">
            <div className="flex items-center gap-1.5 text-[10px] font-bold text-gray-500 uppercase tracking-widest px-2">
              <History className="w-3 h-3" /> Historical Sourcing logs
            </div>
            
            {history.length === 0 ? (
              <div className="text-center py-8 text-xs text-gray-600 italic">
                No past studies recorded.
              </div>
            ) : (
              <div className="space-y-1.5">
                {history.map((h) => (
                  <button
                    key={h.id}
                    onClick={() => loadHistoricalReport(h.id)}
                    className="w-full text-left p-3 rounded-xl transition-all duration-200 glass-card border border-gray-800/10 hover:border-indigo-500/20 group flex items-start gap-2.5"
                  >
                    <FileCheck className="w-4 h-4 text-indigo-400 mt-0.5 shrink-0 group-hover:text-indigo-300" />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-semibold text-gray-200 truncate group-hover:text-white leading-normal">
                        {h.query}
                      </p>
                      <span className="text-[9px] text-gray-500 font-medium block mt-1">
                        {new Date(h.created_at).toLocaleDateString(undefined, {
                          month: "short",
                          day: "numeric",
                          hour: "2-digit",
                          minute: "2-digit"
                        })}
                      </span>
                    </div>
                    <ChevronRight className="w-3.5 h-3.5 text-gray-600 shrink-0 self-center opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer Profile Details */}
        <div className="p-4 border-t border-gray-900 bg-gray-950/40 flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-indigo-500 to-cyan-400 flex items-center justify-center font-bold text-white text-[10px]">
              AI
            </div>
            <span className="font-semibold text-gray-400">Agent Mode active</span>
          </div>
          <button title="Settings" className="hover:text-white transition-colors">
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </aside>

      {/* 2. Main Workspace Dashboard */}
      <main className="flex-1 flex flex-col min-w-0 relative">
        {/* Glowing top backdrop blur gradients */}
        <div className="absolute top-0 inset-x-0 h-40 bg-gradient-to-b from-indigo-500/5 to-transparent pointer-events-none" />

        {/* Global Nav Header */}
        <header className="h-16 border-b border-gray-900 px-8 flex items-center justify-between z-10 bg-gray-950/15 backdrop-blur-md">
          <div className="flex items-center gap-2">
            <span className="text-xs bg-indigo-950/50 text-indigo-400 border border-indigo-500/30 px-2 py-0.5 rounded-full font-bold uppercase tracking-wider">
              System Live
            </span>
            <span className="text-xs text-gray-500">FastAPI Server at Port 8000</span>
          </div>
          
          {status !== "idle" && (
            <div className="flex items-center gap-3">
              <span className="text-xs text-indigo-400 font-semibold uppercase tracking-wider animate-pulse">
                Agent graph compiling...
              </span>
              <button 
                onClick={abortActiveStream}
                className="text-xs bg-red-950/40 hover:bg-red-900/60 border border-red-500/30 text-red-400 px-2.5 py-1 rounded-lg transition-colors font-semibold"
              >
                Abort Job
              </button>
            </div>
          )}
        </header>

        {/* Scrollable Dashboard Viewport */}
        <div className="flex-1 overflow-y-auto p-8 space-y-8 max-w-5xl mx-auto w-full relative">
          
          {/* Query Formulation Console */}
          <div className="text-center max-w-2xl mx-auto py-4">
            <h2 className="text-2xl font-extrabold tracking-tight text-white mb-2 sm:text-3xl glow-text-indigo">
              Autonomous Deep Sourcing Engine
            </h2>
            <p className="text-sm text-gray-400 leading-relaxed mb-6">
              Enter any query. Our multi-agent graph will draft research plans, scrape resources, 
              index vector clusters, reflect on gaps, and stream final formatted studies.
            </p>
            
            {/* Main Form Search Bar */}
            <form onSubmit={handleSearchSubmit} className="relative group max-w-xl mx-auto">
              {/* Pulsing neon highlight */}
              <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-cyan-500 rounded-2xl blur opacity-25 group-hover:opacity-40 transition duration-1000" />
              
              <div className="relative flex items-center bg-gray-950/90 rounded-xl overflow-hidden border border-gray-800/80 p-1">
                <Search className="w-5 h-5 text-gray-500 ml-3.5 shrink-0" />
                <input
                  type="text"
                  placeholder="e.g. Impact of AI on clinical trial designs in 2026..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  disabled={isStreaming}
                  className="flex-1 bg-transparent px-3 py-2 text-sm border-0 focus:outline-none focus:ring-0 text-white placeholder-gray-500 disabled:text-gray-500"
                />
                <button
                  type="submit"
                  disabled={isStreaming || !query.trim()}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs px-4 py-2.5 rounded-lg transition-colors font-bold disabled:bg-gray-850 disabled:text-gray-500 shrink-0"
                >
                  Compile Study
                </button>
              </div>
            </form>
            
            {error && (
              <div className="mt-4 p-3 bg-red-950/20 border border-red-500/30 text-red-400 rounded-xl text-xs font-semibold text-center">
                ⚠️ Connection Error: {error}
              </div>
            )}
          </div>

          {/* Conditional Agent Workflow Progress */}
          {status !== "idle" && (
            <AgentStatusPanel status={status} critique={critique} plan={plan} />
          )}

          {/* Double Columns Grid (Plan Table & Critic Scores) */}
          {plan.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Structured plan card */}
              <div className="glass-panel rounded-2xl p-5 border-gray-800/40">
                <div className="flex items-center gap-2 mb-4 border-b border-gray-800/40 pb-2">
                  <Compass className="w-4.5 h-4.5 text-indigo-400" />
                  <span className="font-bold text-sm text-white uppercase tracking-wider">
                    Planner Agent Structure
                  </span>
                </div>
                <div className="space-y-3">
                  {plan.map((p, idx) => (
                    <div key={idx} className="bg-gray-900/20 rounded-xl p-3 border border-gray-850 flex items-start gap-3">
                      <span className="w-5 h-5 rounded-full bg-indigo-950/50 text-indigo-400 border border-indigo-500/20 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5 select-none">
                        {idx + 1}
                      </span>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between gap-2">
                          <h4 className="font-semibold text-xs text-gray-200 truncate leading-snug">
                            {p.subtopic}
                          </h4>
                          <span className={`text-[9px] px-1.5 py-0.5 rounded font-mono font-bold select-none ${
                            p.depth === "Deep" ? "bg-cyan-950 text-cyan-400 border border-cyan-500/25" : "bg-gray-850 text-gray-400 border border-gray-700/50"
                          }`}>
                            {p.depth}
                          </span>
                        </div>
                        <p className="text-[11px] text-gray-400 mt-1 leading-normal font-normal">
                          {p.intent}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Critic Evaluation Score Card */}
              <div className="glass-panel rounded-2xl p-5 border-gray-800/40 flex flex-col justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-4 border-b border-gray-800/40 pb-2">
                    <FileCheck className="w-4.5 h-4.5 text-indigo-400" />
                    <span className="font-bold text-sm text-white uppercase tracking-wider">
                      Critic Quality Reflection
                    </span>
                  </div>
                  
                  {!critique ? (
                    <div className="py-12 text-center text-xs text-gray-500 italic flex-1 flex flex-col justify-center items-center">
                      <Bookmark className="w-8 h-8 text-gray-800 mb-2 stroke-[1.5]" />
                      Peer review scores will display once Researcher agent finishes extraction.
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {/* Metric bars */}
                      <div className="space-y-3.5">
                        {Object.entries(critique.scores || {}).map(([topicKey, score]) => {
                          // Try to map topicKey e.g. 'topic_0' or direct title back to plan titles
                          let displayTitle = topicKey
                          if (topicKey.startsWith("topic_") && plan[parseInt(topicKey.split("_")[1])]) {
                            displayTitle = plan[parseInt(topicKey.split("_")[1])].subtopic
                          }
                          
                          return (
                            <div key={topicKey} className="space-y-1">
                              <div className="flex justify-between text-xs">
                                <span className="font-medium text-gray-300 truncate max-w-[200px]">{displayTitle}</span>
                                <span className="font-bold font-mono text-indigo-400">{score} / 5</span>
                              </div>
                              <div className="h-1.5 w-full bg-gray-900 rounded-full overflow-hidden border border-gray-850">
                                <div 
                                  className={`h-full rounded-full transition-all duration-1000 ${
                                    score >= 4 ? "bg-gradient-to-r from-emerald-500 to-teal-400" : score >= 3 ? "bg-indigo-500" : "bg-red-500 animate-pulse"
                                  }`} 
                                  style={{ width: `${(score / 5) * 100}%` }}
                                />
                              </div>
                            </div>
                          )
                        })}
                      </div>

                      {/* Flagged Contradictions or Gaps */}
                      {critique.gaps && critique.gaps.length > 0 && (
                        <div className="mt-4 p-3 bg-red-950/15 border border-red-500/20 text-red-400 rounded-xl space-y-1">
                          <span className="text-[10px] font-bold uppercase tracking-widest block">Detected Information Gaps:</span>
                          <ul className="list-disc pl-3.5 text-xs text-gray-300 space-y-0.5">
                            {critique.gaps.map((gap, i) => (
                              <li key={i}>{gap}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Score Summary Footer */}
                {critique && (
                  <div className="text-[10px] font-semibold text-gray-500 text-center border-t border-gray-850 pt-2 mt-4 font-mono select-none">
                    * Scores below 3 trigger a deeper loop (max iterations: 2)
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Central Streaming Document Report */}
          {(report || isStreaming) && (
            <div className="space-y-8">
              {/* Report Display */}
              <StreamingReport report={report} isStreaming={isStreaming} />

              {/* Source Cards display */}
              <SourceCards findings={findings} />

              {/* 3. Deepen Section Controller ("Dig Deeper") */}
              {currentReportId && !isStreaming && (
                <div className="glass-panel rounded-2xl p-6 border-gray-800/40 max-w-2xl mx-auto">
                  <div className="flex items-center gap-2 mb-3 border-b border-gray-800/40 pb-2">
                    <RotateCcw className="w-5 h-5 text-indigo-400 shrink-0" />
                    <h3 className="font-bold text-sm text-white uppercase tracking-wider">
                      Targeted Section Deepening
                    </h3>
                  </div>
                  
                  <p className="text-xs text-gray-400 leading-normal mb-4">
                    Is a section missing vital details or specific statistics? Choose the subtopic, 
                    enter your focus instructions, and let our agents scrape and expand this report section.
                  </p>

                  <form onSubmit={handleDigDeeperSubmit} className="space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {/* Subtopic selector */}
                      <div className="space-y-1">
                        <label className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">
                          Select Section to Expand
                        </label>
                        <select
                          value={selectedSubtopic}
                          onChange={(e) => setSelectedSubtopic(e.target.value)}
                          required
                          className="w-full bg-gray-950 text-gray-300 text-xs rounded-lg border border-gray-850 px-3 py-2.5 focus:outline-none focus:border-indigo-500/60"
                        >
                          <option value="">-- Choose Subtopic --</option>
                          {plan.map((p, i) => (
                            <option key={i} value={p.subtopic}>{p.subtopic}</option>
                          ))}
                        </select>
                      </div>

                      {/* Instruction Focus Input */}
                      <div className="space-y-1">
                        <label className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">
                          Focus Instructions & Requirements
                        </label>
                        <input
                          type="text"
                          placeholder="e.g. Add 2026 statistics about claim denials..."
                          value={digInstructions}
                          onChange={(e) => setDigInstructions(e.target.value)}
                          required
                          className="w-full bg-gray-950 text-white text-xs rounded-lg border border-gray-850 px-3 py-2.5 focus:outline-none focus:border-indigo-500/60"
                        />
                      </div>
                    </div>

                    <button
                      type="submit"
                      disabled={!selectedSubtopic || !digInstructions.trim() || isStreaming}
                      className="w-full bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 text-white text-xs py-2.5 rounded-lg transition-colors font-bold disabled:from-gray-850 disabled:to-gray-850 disabled:text-gray-500"
                    >
                      🔄 Dig Deeper & Expand Section
                    </button>
                  </form>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
