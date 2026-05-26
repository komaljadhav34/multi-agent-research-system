import React, { useState } from "react"
import { ExternalLink, ChevronDown, ChevronUp, Link2, Layers } from "lucide-react"

export default function SourceCards({ findings }) {
  const [expandedCard, setExpandedCard] = useState(null)

  const toggleExpand = (id) => {
    if (expandedCard === id) {
      setExpandedCard(null)
    } else {
      setExpandedCard(id)
    }
  }

  if (!findings || findings.length === 0) {
    return (
      <div className="glass-panel rounded-2xl p-6 text-center text-gray-500 text-sm">
        No source bibliography compiled yet. Run a research query above.
      </div>
    )
  }

  return (
    <div className="w-full space-y-6">
      <div className="flex items-center gap-2 mb-1">
        <Layers className="w-5 h-5 text-indigo-400" />
        <h3 className="font-bold text-lg text-white">Sourced Database Bibliography</h3>
      </div>
      
      {findings.map((item, idx) => {
        const subtopic = item.subtopic
        const sources = item.sources || []
        const snippets = item.scraped_snippets || []
        
        return (
          <div key={idx} className="glass-panel rounded-xl p-5 border-gray-800/40">
            {/* Subtopic Header */}
            <div className="flex items-center justify-between mb-4 border-b border-gray-800/40 pb-2">
              <span className="font-bold text-sm tracking-wide text-indigo-300 uppercase">
                {subtopic}
              </span>
              <span className="text-xs bg-indigo-950/50 text-indigo-400 px-2 py-0.5 rounded-full border border-indigo-500/20 font-medium">
                {sources.length} sources indexed
              </span>
            </div>

            {sources.length === 0 ? (
              <p className="text-xs text-gray-500">No external sources cited.</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {sources.map((src, srcIdx) => {
                  const cardId = `${idx}_${srcIdx}`
                  const isExpanded = expandedCard === cardId
                  const url = src.url || ""
                  const domain = url ? new URL(url).hostname : "web"
                  
                  // Filter snippets belonging to this source URL
                  const matchingSnippets = snippets.filter((s) => s.url === url)
                  
                  return (
                    <div 
                      key={srcIdx} 
                      className={`glass-card rounded-lg overflow-hidden border transition-all ${
                        isExpanded ? "border-indigo-500/30 ring-1 ring-indigo-500/20 bg-indigo-950/5" : "border-gray-800/20"
                      }`}
                    >
                      {/* Card Content Summary */}
                      <div 
                        className="p-4 cursor-pointer flex flex-col justify-between h-full"
                        onClick={() => toggleExpand(cardId)}
                      >
                        <div>
                          {/* Title */}
                          <h4 className="font-medium text-sm text-gray-200 line-clamp-2 leading-snug group-hover:text-indigo-400">
                            {src.title || "Untitled Search Result"}
                          </h4>
                          
                          {/* Domain details */}
                          <div className="flex items-center gap-1.5 mt-2 text-xs text-gray-400">
                            <img 
                              src={`https://www.google.com/s2/favicons?domain=${domain}&sz=16`} 
                              alt="favicon" 
                              className="w-3.5 h-3.5 shrink-0 rounded"
                              onError={(e) => {
                                e.target.src = "data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🌐</text></svg>"
                              }}
                            />
                            <span className="truncate text-gray-400">{domain}</span>
                          </div>
                        </div>

                        {/* Card Controls Footer */}
                        <div className="flex items-center justify-between mt-4 pt-2 border-t border-gray-800/10">
                          <a 
                            href={url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium select-none"
                            onClick={(e) => e.stopPropagation()} // Prevent card expand trigger
                          >
                            Visit Article <ExternalLink className="w-3 h-3" />
                          </a>
                          
                          <button 
                            className="text-gray-400 hover:text-white flex items-center gap-0.5 text-xs font-semibold shrink-0"
                            onClick={(e) => {
                              e.stopPropagation()
                              toggleExpand(cardId)
                            }}
                          >
                            {isExpanded ? (
                              <>Collapse <ChevronUp className="w-3.5 h-3.5" /></>
                            ) : (
                              <>Vector Chunks <ChevronDown className="w-3.5 h-3.5" /></>
                            )}
                          </button>
                        </div>
                      </div>

                      {/* Expandable Chunks Pane */}
                      {isExpanded && (
                        <div className="bg-gray-950/45 border-t border-gray-800/40 p-4 space-y-3">
                          <div className="flex items-center gap-1 text-[10px] uppercase font-bold tracking-wider text-indigo-400">
                            <Link2 className="w-3 h-3" /> ChromaDB Scraped Excerpts
                          </div>
                          
                          {matchingSnippets.length === 0 ? (
                            <p className="text-xs text-gray-500 italic">No corresponding vector fragments found.</p>
                          ) : (
                            matchingSnippets.map((snip, snipIdx) => (
                              <div key={snipIdx} className="bg-gray-950/80 rounded border border-gray-850 p-2.5 space-y-1.5">
                                <div className="flex justify-between items-center text-[10px] text-indigo-300">
                                  <span className="font-mono">Chunk #{snipIdx + 1}</span>
                                  <span className="bg-indigo-950/60 px-1.5 py-0.5 rounded font-mono border border-indigo-900/30 text-indigo-400">
                                    Sim Score: {(snip.relevance_score * 100).toFixed(1)}%
                                  </span>
                                </div>
                                <p className="text-xs leading-relaxed text-gray-300 font-mono line-clamp-4">
                                  "{snip.snippet}"
                                </p>
                              </div>
                            ))
                          )}
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
