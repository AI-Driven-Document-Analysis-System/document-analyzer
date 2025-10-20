



// //**************Real Data */
// // import React from 'react';
// "use client"

// import type React from "react"
// import { useState, useEffect } from "react"

// interface Summary {
//   id: string
//   summary_text: string
//   model_used: string
//   word_count: number
//   created_at: string
//   document_id: string
//   document_name: string
//   document_created_at: string
//   summary_type: string
//   from_cache: boolean
// }

// const PinnedSummaries: React.FC = () => {
//   const [summaries, setSummaries] = useState<Summary[]>([])
//   const [loading, setLoading] = useState(true)
//   const [error, setError] = useState<string | null>(null)
//   const [selectedSummary, setSelectedSummary] = useState<Summary | null>(null)
//   const [showModal, setShowModal] = useState(false)

//   useEffect(() => {
//     const fetchUserSummaries = async () => {
//       setLoading(true)
//       setError(null)
//       try {
//         const token = localStorage.getItem("token")
//         const response = await fetch("http://localhost:8000/api/summarize/user/recent?limit=3", {
//           headers: {
//             Authorization: `Bearer ${token}`,
//             "Content-Type": "application/json",
//           },
//         })

//         if (!response.ok) {
//           throw new Error(`Failed to fetch summaries: ${response.statusText}`)
//         }

//         const data = await response.json()
//         console.log("[v0] Fetched user summaries:", data)

//         if (data.success && data.summaries) {
//           setSummaries(data.summaries)
//         }
//       } catch (err) {
//         console.error("[v0] Error fetching user summaries:", err)
//         setError(err instanceof Error ? err.message : "Failed to fetch summaries")
//       } finally {
//         setLoading(false)
//       }
//     }

//     fetchUserSummaries()
//   }, [])

//   const formatDate = (dateString: string) => {
//     const date = new Date(dateString)
//     const now = new Date()
//     const diffMs = now.getTime() - date.getTime()
//     const diffHours = Math.floor(diffMs / (1000 * 60 * 60))

//     if (diffHours < 1) return "Just now"
//     if (diffHours < 24) return `${diffHours}h ago`
//     const diffDays = Math.floor(diffHours / 24)
//     if (diffDays < 7) return `${diffDays}d ago`
//     return date.toLocaleDateString()
//   }

//   const handleViewSummary = (summary: Summary) => {
//     setSelectedSummary(summary)
//     setShowModal(true)
//   }

//   const handleCloseModal = () => {
//     setShowModal(false)
//     setSelectedSummary(null)
//   }

//   if (loading) {
//     return (
//       <div className="feature-container" style={{ flex: "1", marginTop: "1.5rem" }}>
//         <div className="tab-content-container">
//           <h5 className="mb-4">
//             <i className="fas fa-bookmark me-2"></i>Recent Summaries
//           </h5>
//           <div style={{ textAlign: "center", padding: "2rem", color: "#666" }}>Loading summaries...</div>
//         </div>
//       </div>
//     )
//   }

//   if (error) {
//     return (
//       <div className="feature-container" style={{ flex: "1", marginTop: "1.5rem" }}>
//         <div className="tab-content-container">
//           <h5 className="mb-4">
//             <i className="fas fa-bookmark me-2"></i>Recent Summaries
//           </h5>
//           <div style={{ textAlign: "center", padding: "2rem", color: "#d32f2f" }}>Error: {error}</div>
//         </div>
//       </div>
//     )
//   }

//   if (summaries.length === 0) {
//     return (
//       <div className="feature-container" style={{ flex: "1", marginTop: "1.5rem" }}>
//         <div className="tab-content-container">
//           <h5 className="mb-4">
//             <i className="fas fa-bookmark me-2"></i>Recent Summaries
//           </h5>
//           <div style={{ textAlign: "center", padding: "2rem", color: "#999" }}>
//             No summaries available yet. Create a summary to get started!
//           </div>
//         </div>
//       </div>
//     )
//   }

//   return (
//     <>
//       <div className="feature-container" style={{ flex: "1", marginTop: "1.5rem" }}>
//         <div className="tab-content-container">
//           <h5 className="mb-4">
//             <i className="fas fa-bookmark me-2"></i>Recent Summaries
//           </h5>

//           <div>
//             {summaries.map((summary) => (
//               <div key={summary.id} className="result-item">
//                 <div
//                   style={{
//                     display: "flex",
//                     justifyContent: "space-between",
//                     alignItems: "flex-start",
//                     width: "100%",
//                     gap: "1rem",
//                   }}
//                 >
//                   <div className="flex-grow-1">
//                     <div className="result-title" style={{ marginBottom: "0.5rem" }}>
//                       {summary.document_name}
//                     </div>
//                     <div className="result-meta" style={{ marginBottom: "0.5rem" }}>
//                       <span style={{ fontWeight: 500, color: "#555" }}>Summary:</span> {summary.word_count} words •{" "}
//                       {summary.model_used}
//                     </div>
//                     <div className="result-meta">Created {formatDate(summary.created_at)}</div>
//                   </div>
//                   <button
//                     onClick={() => handleViewSummary(summary)}
//                     style={{
//                       padding: "6px 12px",
//                       fontSize: "0.75rem",
//                       fontWeight: 500,
//                       backgroundColor: "#10b981",
//                       color: "white",
//                       border: "none",
//                       borderRadius: "6px",
//                       cursor: "pointer",
//                       transition: "all 0.2s ease",
//                       whiteSpace: "nowrap",
//                       flexShrink: 0,
//                     }}
//                     onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#059669")}
//                     onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "#10b981")}
//                   >
//                     View Summary
//                   </button>
//                 </div>
//               </div>
//             ))}
//           </div>
//         </div>
//       </div>

//       {showModal && selectedSummary && (
//         <div
//           style={{
//             position: "fixed",
//             top: 0,
//             left: 0,
//             right: 0,
//             bottom: 0,
//             backgroundColor: "rgba(0, 0, 0, 0.5)",
//             display: "flex",
//             alignItems: "center",
//             justifyContent: "center",
//             zIndex: 1000,
//           }}
//           onClick={handleCloseModal}
//         >
//           <div
//             style={{
//               backgroundColor: "white",
//               borderRadius: "8px",
//               padding: "2rem",
//               maxWidth: "600px",
//               maxHeight: "80vh",
//               overflow: "auto",
//               boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
//             }}
//             onClick={(e) => e.stopPropagation()}
//           >
//             <div
//               style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}
//             >
//               <h3 style={{ margin: 0 }}>{selectedSummary.document_name}</h3>
//               <button
//                 onClick={handleCloseModal}
//                 style={{
//                   background: "none",
//                   border: "none",
//                   fontSize: "1.5rem",
//                   cursor: "pointer",
//                   color: "#666",
//                 }}
//               >
//                 ×
//               </button>
//             </div>

//             <div
//               style={{
//                 marginBottom: "1rem",
//                 padding: "0.75rem",
//                 backgroundColor: "white",
//                 borderRadius: "6px",
//                 fontSize: "0.875rem",
//                 color: "#666",
//               }}
//             >
//               <div style={{ marginBottom: "0.5rem" , color: "#FFFFFF"}}>
//                 <strong >Document:</strong> {selectedSummary.document_name}
//               </div>
//               <div style={{  color: "#FFFFFF"}}>
//                 <strong>Summary Details:</strong> {selectedSummary.word_count} words • {selectedSummary.model_used} •{" "}
//                 {formatDate(selectedSummary.created_at)}
//               </div>
//             </div>

//             <div style={{
//                 lineHeight: "1.6",
//                 color: "#000000",
//                 backgroundColor: "#FFFFFF",
//                 padding: "1rem",
//                 borderRadius: "6px",
//               }}>{selectedSummary.summary_text}</div>
//           </div>
//         </div>
//       )}
//     </>
//   )
// }

// export default PinnedSummaries


//***********************Optimised */
"use client"

import type React from "react"
import { useState, useEffect, useRef } from "react"

interface Summary {
  id: string
  summary_text: string
  model_used: string
  word_count: number
  created_at: string
  document_id: string
  document_name: string
  document_created_at: string
  summary_type: string
  from_cache: boolean
}

// Cache with TTL
const SUMMARIES_CACHE_KEY = 'recent_summaries_cache'
const SUMMARIES_CACHE_TTL = 5 * 60 * 1000 // 5 minutes

const PinnedSummaries: React.FC = () => {
  const [summaries, setSummaries] = useState<Summary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedSummary, setSelectedSummary] = useState<Summary | null>(null)
  const [showModal, setShowModal] = useState(false)
  const fetchAbortRef = useRef<AbortController | null>(null)

  // Check cache validity
  const getCachedData = (key: string, ttl: number) => {
    try {
      const cached = sessionStorage.getItem(key)
      if (!cached) return null
      
      const { data, timestamp } = JSON.parse(cached)
      if (Date.now() - timestamp > ttl) {
        sessionStorage.removeItem(key)
        return null
      }
      return data
    } catch {
      return null
    }
  }

  // Set cache
  const setCacheData = (key: string, data: any) => {
    try {
      sessionStorage.setItem(key, JSON.stringify({ data, timestamp: Date.now() }))
    } catch {
      // Silently fail if storage unavailable
    }
  }

  useEffect(() => {
    const fetchUserSummaries = async () => {
      setLoading(true)
      setError(null)
      
      try {
        // Check cache first - instant load
        const cached = getCachedData(SUMMARIES_CACHE_KEY, SUMMARIES_CACHE_TTL)
        if (cached) {
          setSummaries(cached)
          setLoading(false)
          return
        }

        const token = localStorage.getItem("token")
        if (!token) {
          setLoading(false)
          return
        }

        // Create abort controller for this request
        fetchAbortRef.current = new AbortController()

        const response = await fetch("http://localhost:8000/api/summarize/user/recent?limit=3", {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          signal: fetchAbortRef.current.signal,
        })

        if (!response.ok) {
          throw new Error(`Failed to fetch summaries: ${response.statusText}`)
        }

        const data = await response.json()

        if (data.success && data.summaries) {
          // Cache the data
          setCacheData(SUMMARIES_CACHE_KEY, data.summaries)
          setSummaries(data.summaries)
        }
      } catch (err) {
        // Ignore abort errors (component unmounted)
        if (err instanceof Error && err.name === 'AbortError') {
          return
        }
        console.error("[v0] Error fetching user summaries:", err)
        setError(err instanceof Error ? err.message : "Failed to fetch summaries")
      } finally {
        setLoading(false)
      }
    }

    fetchUserSummaries()

    // Cleanup: abort fetch if component unmounts
    return () => {
      if (fetchAbortRef.current) {
        fetchAbortRef.current.abort()
      }
    }
  }, [])

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))

    if (diffHours < 1) return "Just now"
    if (diffHours < 24) return `${diffHours}h ago`
    const diffDays = Math.floor(diffHours / 24)
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  const handleViewSummary = (summary: Summary) => {
    setSelectedSummary(summary)
    setShowModal(true)
  }

  const handleCloseModal = () => {
    setShowModal(false)
    setSelectedSummary(null)
  }

  if (loading) {
    return (
      <div className="feature-container" style={{ flex: "1", marginTop: "1.5rem" }}>
        <div className="tab-content-container">
          <h5 className="mb-4">
            <i className="fas fa-bookmark me-2"></i>Recent Summaries
          </h5>
          <div style={{ textAlign: "center", padding: "2rem", color: "#666" }}>Loading summaries...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="feature-container" style={{ flex: "1", marginTop: "1.5rem" }}>
        <div className="tab-content-container">
          <h5 className="mb-4">
            <i className="fas fa-bookmark me-2"></i>Recent Summaries
          </h5>
          <div style={{ textAlign: "center", padding: "2rem", color: "#d32f2f" }}>Error: {error}</div>
        </div>
      </div>
    )
  }

  if (summaries.length === 0) {
    return (
      <div className="feature-container" style={{ flex: "1", marginTop: "1.5rem" }}>
        <div className="tab-content-container">
          <h5 className="mb-4">
            <i className="fas fa-bookmark me-2"></i>Recent Summaries
          </h5>
          <div style={{ textAlign: "center", padding: "2rem", color: "#999" }}>
            No summaries available yet. Create a summary to get started!
          </div>
        </div>
      </div>
    )
  }

  return (
    <>
      <div className="feature-container" style={{ flex: "1", marginTop: "1.5rem" }}>
        <div className="tab-content-container">
          <h5 className="mb-4">
            <i className="fas fa-bookmark me-2"></i>Recent Summaries
          </h5>

          <div>
            {summaries.map((summary) => (
              <div key={summary.id} className="result-item">
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    width: "100%",
                    gap: "1rem",
                  }}
                >
                  <div className="flex-grow-1">
                    <div className="result-title" style={{ marginBottom: "0.5rem" }}>
                      {summary.document_name}
                    </div>
                    <div className="result-meta" style={{ marginBottom: "0.5rem" }}>
                      <span style={{ fontWeight: 500, color: "#555" }}>Summary:</span> {summary.word_count} words •{" "}
                      {summary.model_used}
                    </div>
                    <div className="result-meta">Created {formatDate(summary.created_at)}</div>
                  </div>
                  <button
                    onClick={() => handleViewSummary(summary)}
                    style={{
                      padding: "6px 12px",
                      fontSize: "0.75rem",
                      fontWeight: 500,
                      backgroundColor: "#10b981",
                      color: "white",
                      border: "none",
                      borderRadius: "6px",
                      cursor: "pointer",
                      transition: "all 0.2s ease",
                      whiteSpace: "nowrap",
                      flexShrink: 0,
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#059669")}
                    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "#10b981")}
                  >
                    View Summary
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {showModal && selectedSummary && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0, 0, 0, 0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
          }}
          onClick={handleCloseModal}
        >
          <div
            style={{
              backgroundColor: "#FFFFFF",
              color: "#000000",
              borderRadius: "8px",
              padding: "2rem",
              maxWidth: "600px",
              maxHeight: "80vh",
              overflow: "auto",
              boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
              border: "1px solid #e5e7eb",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div
              style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}
            >
              <h3 style={{ margin: 0, color: "#000000" }}>{selectedSummary.document_name}</h3>
              <button
                onClick={handleCloseModal}
                style={{
                  background: "none",
                  border: "none",
                  fontSize: "1.5rem",
                  cursor: "pointer",
                  color: "#666",
                }}
              >
                ×
              </button>
            </div>

            <div
              style={{
                marginBottom: "1rem",
                padding: "0.75rem",
                backgroundColor: "#FFFFFF",
                borderRadius: "6px",
                fontSize: "0.875rem",
                color: "#000000",
                border: "1px solid #e5e7eb",
              }}
            >
              <div style={{ marginBottom: "0.5rem", color: "#000000" }}>
                <strong style={{ color: "#000000" }}>Document:</strong> {selectedSummary.document_name}
              </div>
              <div style={{ color: "#000000" }}>
                <strong style={{ color: "#000000" }}>Summary Details:</strong> {selectedSummary.word_count} words • {selectedSummary.model_used} •{" "}
                {formatDate(selectedSummary.created_at)}
              </div>
            </div>

            <div
              style={{
                lineHeight: "1.6",
                color: "#000000",
                backgroundColor: "#ffffff",
                padding: "1rem",
                borderRadius: "6px",
                border: "1px solid #e5e7eb",
              }}
            >
              {selectedSummary.summary_text}
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default PinnedSummaries
