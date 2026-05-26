import { useState, useCallback, useRef } from "react"

const BACKEND_URL = "http://localhost:8000"

export function useSSE() {
  const [status, setStatus] = useState("idle") // idle, planner, researcher, critic, writer
  const [plan, setPlan] = useState([])
  const [findings, setFindings] = useState([])
  const [critique, setCritique] = useState(null)
  const [report, setReport] = useState("")
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState(null)
  const [currentReportId, setCurrentReportId] = useState(null)
  
  const activeReaderRef = useRef(null)

  const abortActiveStream = useCallback(() => {
    if (activeReaderRef.current) {
      try {
        activeReaderRef.current.cancel()
      } catch (e) {
        console.warn("Error cancelling stream: ", e)
      }
      activeReaderRef.current = null
    }
  }, [])

  const executeResearch = useCallback(async (topic) => {
    // Abort any active streams first
    abortActiveStream()
    
    // Reset state variables
    setStatus("planner")
    setPlan([])
    setFindings([])
    setCritique(null)
    setReport("")
    setError(null)
    setCurrentReportId(null)
    setIsStreaming(true)

    // Generate a unique session ID for this request
    const session_id = "session_" + Math.random().toString(36).substring(2, 11)

    try {
      const response = await fetch(`${BACKEND_URL}/api/research/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ topic, session_id }),
      })

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}: ${response.statusText}`)
      }

      const reader = response.body.getReader()
      activeReaderRef.current = reader
      const decoder = new TextDecoder()
      
      let buffer = ""
      
      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        
        // Decode chunk and append to buffer
        buffer += decoder.decode(value, { stream: true })
        
        // Process SSE events separated by double newlines
        const events = buffer.split("\n\n")
        // Keep the last partial event in the buffer
        buffer = events.pop() || ""
        
        for (const rawEvent of events) {
          const line = rawEvent.trim()
          if (!line || !line.startsWith("data: ")) continue
          
          try {
            const dataText = line.substring(6)
            const eventData = JSON.parse(dataText)
            
            // Handle different event types
            switch (eventData.type) {
              case "status":
                setStatus(eventData.status)
                break
              case "plan":
                setPlan(eventData.plan)
                break
              case "findings":
                setFindings(eventData.findings)
                break
              case "critique":
                setCritique(eventData.critique)
                break
              case "report_chunk":
                // Smoothly append characters to the markdown report
                setReport((prev) => prev + eventData.content)
                break
              case "done":
                setIsStreaming(false)
                setStatus("idle")
                setCurrentReportId(eventData.report_id)
                break
              case "error":
                setError(eventData.message)
                setIsStreaming(false)
                setStatus("idle")
                break
              default:
                break
            }
          } catch (err) {
            console.error("Failed to parse SSE JSON payload: ", rawEvent, err)
          }
        }
      }
    } catch (err) {
      console.error("SSE stream error: ", err)
      setError(err.message || "Failed to establish stream connection.")
      setIsStreaming(false)
      setStatus("idle")
    } finally {
      activeReaderRef.current = null
    }
  }, [abortActiveStream])

  const executeDigDeeper = useCallback(async (reportId, subtopic, instructions) => {
    abortActiveStream()
    
    setStatus("researcher")
    setError(null)
    setIsStreaming(true)
    
    // Clear out report but store previous report text so we can append,
    // actually, let's keep the existing report text and append the streamed additions live!
    const session_id = "session_" + Math.random().toString(36).substring(2, 11)
    
    // Add title in report state to show it is deepening
    setReport((prev) => prev + `\n\n## Deep-Dive Focus: ${subtopic}\n\n**Deepen Context:** *${instructions}*\n\n`)

    try {
      const response = await fetch(`${BACKEND_URL}/api/reports/${reportId}/dig-deeper`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ subtopic, instructions, session_id }),
      })

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`)
      }

      const reader = response.body.getReader()
      activeReaderRef.current = reader
      const decoder = new TextDecoder()
      
      let buffer = ""
      
      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        
        buffer += decoder.decode(value, { stream: true })
        const events = buffer.split("\n\n")
        buffer = events.pop() || ""
        
        for (const rawEvent of events) {
          const line = rawEvent.trim()
          if (!line || !line.startsWith("data: ")) continue
          
          try {
            const dataText = line.substring(6)
            const eventData = JSON.parse(dataText)
            
            switch (eventData.type) {
              case "status":
                setStatus(eventData.status)
                break
              case "report_chunk":
                // Append the deep-dive tokens live to the end of the report
                setReport((prev) => prev + eventData.content)
                break
              case "done":
                setIsStreaming(false)
                setStatus("idle")
                break
              case "error":
                setError(eventData.message)
                setIsStreaming(false)
                setStatus("idle")
                break
              default:
                break
            }
          } catch (err) {
            console.error("Failed to parse dig-deeper payload: ", err)
          }
        }
      }
    } catch (err) {
      console.error("Dig deeper stream error: ", err)
      setError(err.message || "Failed to deepen report section.")
      setIsStreaming(false)
      setStatus("idle")
    } finally {
      activeReaderRef.current = null
    }
  }, [abortActiveStream])

  return {
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
  }
}
