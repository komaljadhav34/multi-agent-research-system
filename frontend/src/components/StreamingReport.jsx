import React from "react"
import { Sparkles, Terminal, AlertCircle, Bookmark } from "lucide-react"

export default function StreamingReport({ report, isStreaming }) {
  
  // Custom inline formatter to handle bold and inline citations
  const formatInlineText = (text) => {
    if (!text) return ""
    
    // 1. Format bold text: **text**
    let formatted = text
    const boldRegex = /\*\*(.*?)\*\*/g
    const boldMatches = [...formatted.matchAll(boldRegex)]
    
    // We'll compile nodes dynamically
    const elements = []
    let lastIndex = 0
    
    // Regex for inline citations: [1], [2], etc.
    const citationRegex = /\[(\d+)\]/g
    const allMatches = []
    
    // Collate all bold and citation matches to parse sequentially
    let match
    while ((match = citationRegex.exec(text)) !== null) {
      allMatches.push({
        type: "citation",
        index: match.index,
        length: match[0].length,
        value: match[1],
        raw: match[0]
      })
    }
    
    while ((match = boldRegex.exec(text)) !== null) {
      allMatches.push({
        type: "bold",
        index: match.index,
        length: match[0].length,
        value: match[1],
        raw: match[0]
      })
    }
    
    // Sort matches chronologically by occurrence index
    allMatches.sort((a, b) => a.index - b.index)
    
    // Reconstruct string into JSX nodes
    allMatches.forEach((item, i) => {
      // Add preceding plain text
      if (item.index > lastIndex) {
        elements.push(text.substring(lastIndex, item.index))
      }
      
      if (item.type === "citation") {
        elements.push(
          <span 
            key={`cite_${i}`} 
            title="Sourced Citations"
            className="inline-flex items-center justify-center bg-indigo-950/70 text-indigo-400 border border-indigo-500/30 text-[10px] w-4.5 h-4.5 rounded-full mx-0.5 font-bold cursor-help hover:bg-indigo-900 transition-colors select-none"
          >
            {item.value}
          </span>
        )
      } else if (item.type === "bold") {
        elements.push(
          <strong key={`bold_${i}`} className="font-bold text-white font-semibold">
            {item.value}
          </strong>
        )
      }
      
      lastIndex = item.index + item.length
    })
    
    if (lastIndex < text.length) {
      elements.push(text.substring(lastIndex))
    }
    
    return elements.length > 0 ? elements : text
  }

  // Parses blocks (H1, H2, lists, tables, callouts)
  const renderMarkdownBlocks = (markdownText) => {
    if (!markdownText) return null
    
    const lines = markdownText.split("\n")
    const blocks = []
    
    let currentTable = null
    let currentList = null
    let listType = null // 'ul' or 'ol'
    let currentCallout = null
    
    const flushTable = (key) => {
      if (currentTable) {
        blocks.push(
          <div key={`table_${key}`} className="overflow-x-auto w-full my-6 rounded-xl border border-gray-800/40">
            <table className="min-w-full divide-y divide-gray-800/60 bg-gray-950/20 text-sm">
              <thead className="bg-gray-900/40">
                <tr>
                  {currentTable.headers.map((h, i) => (
                    <th key={i} className="px-4 py-3 text-left font-bold text-gray-300 tracking-wider font-semibold uppercase text-xs">
                      {h.trim()}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-850">
                {currentTable.rows.map((row, rowIdx) => (
                  <tr key={rowIdx} className="hover:bg-gray-900/10">
                    {row.map((cell, cellIdx) => (
                      <td key={cellIdx} className="px-4 py-3 text-gray-300">
                        {formatInlineText(cell.trim())}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
        currentTable = null
      }
    }
    
    const flushList = (key) => {
      if (currentList) {
        if (listType === "ul") {
          blocks.push(
            <ul key={`list_${key}`} className="list-disc list-inside pl-5 my-4 space-y-2 text-gray-300">
              {currentList.map((li, i) => (
                <li key={i} className="leading-relaxed">
                  {formatInlineText(li)}
                </li>
              ))}
            </ul>
          )
        } else {
          blocks.push(
            <ol key={`list_${key}`} className="list-decimal list-inside pl-5 my-4 space-y-2 text-gray-300">
              {currentList.map((li, i) => (
                <li key={i} className="leading-relaxed">
                  {formatInlineText(li)}
                </li>
              ))}
            </ol>
          )
        }
        currentList = null
        listType = null
      }
    }
    
    const flushCallout = (key) => {
      if (currentCallout) {
        let borderClass = "border-indigo-500/30 text-indigo-300 bg-indigo-950/5"
        let titleColor = "text-indigo-400"
        let icon = Sparkles
        
        if (currentCallout.type === "TIP") {
          borderClass = "border-emerald-500/30 text-emerald-300 bg-emerald-950/5"
          titleColor = "text-emerald-400"
          icon = Sparkles
        } else if (currentCallout.type === "IMPORTANT") {
          borderClass = "border-violet-500/30 text-violet-300 bg-violet-950/5"
          titleColor = "text-violet-400"
          icon = Bookmark
        } else if (currentCallout.type === "NOTE") {
          borderClass = "border-cyan-500/30 text-cyan-300 bg-cyan-950/5"
          titleColor = "text-cyan-400"
          icon = AlertCircle
        }
        
        const IconComponent = icon
        
        blocks.push(
          <div key={`callout_${key}`} className={`border-l-4 rounded-r-xl p-4 my-6 glass-card ${borderClass}`}>
            <div className="flex items-center gap-2 mb-1.5">
              <IconComponent className={`w-4 h-4 ${titleColor}`} />
              <span className={`text-xs font-bold uppercase tracking-wider ${titleColor}`}>
                {currentCallout.type}
              </span>
            </div>
            <p className="text-sm leading-relaxed">
              {formatInlineText(currentCallout.content.join(" "))}
            </p>
          </div>
        )
        currentCallout = null
      }
    }
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]
      const trimmed = line.trim()
      
      // 1. Process table line
      if (trimmed.startsWith("|")) {
        flushList(i)
        flushCallout(i)
        
        const cells = line.split("|").slice(1, -1)
        if (!currentTable) {
          currentTable = { headers: cells, rows: [] }
        } else {
          // Skip divider rows (e.g. |:---|:---|)
          if (trimmed.includes("---")) continue
          currentTable.rows.push(cells)
        }
        continue
      } else {
        flushTable(i)
      }
      
      // 2. Process callout line
      if (trimmed.startsWith(">")) {
        flushList(i)
        
        const content = trimmed.substring(1).trim()
        if (content.startsWith("[!TIP]")) {
          flushCallout(i)
          currentCallout = { type: "TIP", content: [] }
        } else if (content.startsWith("[!IMPORTANT]")) {
          flushCallout(i)
          currentCallout = { type: "IMPORTANT", content: [] }
        } else if (content.startsWith("[!NOTE]")) {
          flushCallout(i)
          currentCallout = { type: "NOTE", content: [] }
        } else if (currentCallout) {
          currentCallout.content.push(content)
        } else {
          // Standard blockquote
          blocks.push(
            <blockquote key={i} className="border-l-4 border-gray-700 pl-4 py-1 my-4 italic text-gray-400 text-sm">
              {formatInlineText(content)}
            </blockquote>
          )
        }
        continue
      } else {
        flushCallout(i)
      }
      
      // 3. Process bullet list line
      if (trimmed.startsWith("- ") || trimmed.startsWith("* ") || trimmed.startsWith("• ")) {
        const itemContent = trimmed.substring(2).trim()
        if (!currentList || listType !== "ul") {
          flushList(i)
          currentList = [itemContent]
          listType = "ul"
        } else {
          currentList.push(itemContent)
        }
        continue
      }
      
      // 4. Process numbered list line
      if (/^\d+\.\s/.test(trimmed)) {
        const idxOfDot = trimmed.indexOf(".")
        const itemContent = trimmed.substring(idxOfDot + 1).trim()
        if (!currentList || listType !== "ol") {
          flushList(i)
          currentList = [itemContent]
          listType = "ol"
        } else {
          currentList.push(itemContent)
        }
        continue
      }
      
      // If we reach a standard paragraph, flush active list accumulator
      flushList(i)
      
      // 5. Empty lines
      if (!trimmed) {
        continue
      }
      
      // 6. Header 1: # Header
      if (trimmed.startsWith("# ")) {
        blocks.push(
          <h1 key={i} className="text-3xl md:text-4xl font-extrabold text-white tracking-tight leading-tight border-b border-indigo-500/20 pb-4 mb-8 glow-text-indigo">
            {trimmed.substring(2)}
          </h1>
        )
        continue
      }
      
      // 7. Header 2: ## Header
      if (trimmed.startsWith("## ")) {
        const title = trimmed.substring(3)
        // Highlight references title
        const isRef = title.toLowerCase().includes("references")
        blocks.push(
          <h2 key={i} className={`text-xl font-bold mt-10 mb-5 border-b border-gray-800/40 pb-2 flex items-center gap-2 ${
            isRef ? "text-indigo-400" : "text-indigo-300"
          }`}>
            {title}
          </h2>
        )
        continue
      }
      
      // 8. Header 3: ### Header
      if (trimmed.startsWith("### ")) {
        blocks.push(
          <h3 key={i} className="text-md font-bold text-white mt-6 mb-3 tracking-wide">
            {trimmed.substring(4)}
          </h3>
        )
        continue
      }
      
      // 9. Standard paragraphs
      blocks.push(
        <p key={i} className="text-sm md:text-base leading-relaxed text-gray-300 my-4 text-justify font-normal">
          {formatInlineText(trimmed)}
        </p>
      )
    }
    
    // Flush remaining accumulators after line iteration
    flushTable("final")
    flushList("final")
    flushCallout("final")
    
    return blocks
  }

  return (
    <div className="w-full glass-panel rounded-2xl p-6 md:p-8 border-gray-800/50 shadow-2xl relative overflow-hidden">
      {/* Decorative gradient overlay */}
      <div className="absolute top-0 right-0 w-80 h-80 bg-indigo-500/5 rounded-full filter blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-80 h-80 bg-cyan-500/5 rounded-full filter blur-3xl pointer-events-none" />
      
      {/* Streaming state overlay banner */}
      {isStreaming && (
        <div className="flex items-center gap-2 mb-4 px-3 py-1 bg-indigo-950/40 border border-indigo-500/20 text-indigo-400 rounded-full w-max text-xs select-none">
          <span className="w-2 h-2 rounded-full bg-indigo-400 animate-ping" />
          <span className="font-semibold tracking-wide uppercase text-[10px]">Streaming document contents live...</span>
        </div>
      )}

      {/* Markdown Compiled Content */}
      <div className="prose prose-invert max-w-none space-y-4">
        {report ? (
          renderMarkdownBlocks(report)
        ) : (
          <div className="py-20 text-center flex flex-col items-center justify-center text-gray-500">
            <Bookmark className="w-12 h-12 text-gray-700 mb-3 stroke-[1.5]" />
            <p className="text-sm">Your formatted research report will stream here word-by-word.</p>
          </div>
        )}
      </div>
      
      {/* Blinking cursor typing indicator */}
      {isStreaming && report && (
        <span className="inline-block w-2.5 h-4 bg-indigo-400 animate-pulse ml-1 align-middle" />
      )}
    </div>
  )
}
