import React from "react"
import { Compass, Search, ShieldCheck, FileText, CheckCircle2, RotateCcw } from "lucide-react"

export default function AgentStatusPanel({ status, critique, plan }) {
  // Define agent stages
  const agents = [
    {
      id: "planner",
      name: "Planner Agent",
      icon: Compass,
      color: "indigo",
      activeBorder: "neon-border-indigo",
      activeGlow: "pulse-glow-indigo",
      bgClass: "bg-indigo-950/40 text-indigo-400 border-indigo-500/30",
      description: "Formulates JSON subtopics and strategic search intents."
    },
    {
      id: "researcher",
      name: "Researcher Agent",
      icon: Search,
      color: "cyan",
      activeBorder: "neon-border-cyan",
      activeGlow: "pulse-glow-cyan",
      bgClass: "bg-cyan-950/40 text-cyan-400 border-cyan-500/30",
      description: "Searches Tavily, parses HTML, and vectors ChromaDB chunks."
    },
    {
      id: "critic",
      name: "Critic Agent",
      icon: ShieldCheck,
      color: "violet",
      activeBorder: "neon-border-violet",
      activeGlow: "pulse-glow-violet",
      bgClass: "bg-violet-950/40 text-violet-400 border-violet-500/30",
      description: "Scores data (1-5), flags contradictions, and triggers retries."
    },
    {
      id: "writer",
      name: "Writer Agent",
      icon: FileText,
      color: "emerald",
      activeBorder: "neon-border-emerald",
      activeGlow: "pulse-glow-emerald",
      bgClass: "bg-emerald-950/40 text-emerald-400 border-emerald-500/30",
      description: "Compiles styled markdown reports with inline citation tags."
    }
  ]

  // Get current active index
  const activeIndex = agents.findIndex((a) => a.id === status)

  // Status message details
  const getSubtext = (id) => {
    if (status === id) {
      switch (id) {
        case "planner":
          return "Analyzing macro query parameters..."
        case "researcher":
          return "Querying APIs and indexing in vector DB..."
        case "critic":
          return "Scoring findings and checking factual gaps..."
        case "writer":
          return "Streaming final document blocks..."
        default:
          return "Computing..."
      }
    }
    return null
  }

  const retryTopics = critique?.retry_topics || []
  const hasLoopback = retryTopics.length > 0 && status === "researcher"

  return (
    <div className="w-full glass-panel rounded-2xl p-6 mb-6">
      <div className="flex flex-col md:flex-row items-center justify-between gap-6 relative">
        {agents.map((agent, index) => {
          const Icon = agent.icon
          const isActive = status === agent.id
          const isCompleted = activeIndex > index && status !== "idle"
          
          return (
            <React.Fragment key={agent.id}>
              {/* Agent Node Card */}
              <div 
                className={`flex-1 flex items-center gap-4 p-4 rounded-xl border transition-all duration-300 w-full ${
                  isActive 
                    ? `glass-panel ${agent.activeBorder} ${agent.activeGlow}` 
                    : isCompleted
                      ? "bg-emerald-950/10 border-emerald-500/20 text-emerald-400"
                      : "bg-gray-900/30 border-gray-800/40 text-gray-400"
                }`}
              >
                {/* Visual Icon Node */}
                <div 
                  className={`p-3 rounded-lg border ${
                    isActive 
                      ? `${agent.bgClass}`
                      : isCompleted
                        ? "bg-emerald-950/40 border-emerald-500/40 text-emerald-400"
                        : "bg-gray-950/50 border-gray-900 text-gray-500"
                  }`}
                >
                  <Icon className="w-6 h-6" />
                </div>
                
                {/* Node Details */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-sm tracking-wide text-white">
                      {agent.name}
                    </span>
                    {isCompleted && (
                      <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    )}
                  </div>
                  <p className="text-xs text-gray-400 mt-1 truncate">
                    {getSubtext(agent.id) || agent.description}
                  </p>
                </div>
              </div>

              {/* Connector Arrow */}
              {index < agents.length - 1 && (
                <div className="hidden md:block w-6 h-[2px] bg-gray-800 relative">
                  <div 
                    className={`absolute inset-0 transition-all duration-500 ${
                      isCompleted ? "bg-emerald-500" : isActive ? "bg-indigo-500" : "bg-gray-800"
                    }`} 
                  />
                </div>
              )}
            </React.Fragment>
          )
        })}
      </div>

      {/* Cyclic Loopback Alert Card */}
      {hasLoopback && (
        <div className="mt-5 p-4 bg-amber-950/20 border border-amber-500/30 text-amber-300 rounded-xl flex items-center gap-3 animate-pulse">
          <RotateCcw className="w-5 h-5 shrink-0" />
          <div className="text-xs">
            <span className="font-bold uppercase tracking-wider block mb-1">
              🔄 Critic Back-Routing Triggered
            </span>
            The Critic Agent detected information gaps in your research. Sourcing deeper evidence for:{" "}
            <span className="font-semibold text-white">
              {retryTopics.join(", ")}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
