
//****************************CSS */
import { useState, useEffect, useMemo } from "react"
import './Dashboard.css' // Import the CSS file

// TypeScript interfaces
interface Document {
  id: string
  original_filename: string
  content_type: string
  processing_status: 'completed' | 'processing' | 'failed'
  upload_date: string
  user_id: string
}

interface Summary {
  id: number | string
  summary_text: string
  summary_type: string
  word_count: number
  model_used: string
  created_at: string
  from_cache: boolean
  key_points?: string[] | null
  document_type?: string | null
}

interface FormattedDocument {
  id: string
  name: string
  type: string
  status: string
  uploadedAt: string
  confidence: number | null
}

interface SummaryOption {
  id: string
  name: string
  description: string
  model: string
  icon: string
}

interface DocumentWithSummary extends FormattedDocument {
  showSummaryOptions: boolean
  selectedModel: string | null
  currentSummary: Summary | null
  loadingSummary: boolean
  generatingNew: boolean
  summaryError: string | null
}

// Main Dashboard Component
function Dashboard() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [documentsWithSummary, setDocumentsWithSummary] = useState<DocumentWithSummary[]>([])

  // Summary options configuration
  const summaryOptions: SummaryOption[] = [
    {
      id: 'brief',
      name: 'Brief Summary',
      description: 'Quick overview with key points (50-150 words)',
      model: 'BART',
      icon: 'fas fa-file-text'
    },
    {
      id: 'detailed',
      name: 'Detailed Summary',
      description: 'Comprehensive analysis with full context (80-250 words)',
      model: 'PEGASUS',
      icon: 'fas fa-file-alt'
    },
    {
      id: 'domain_specific',
      name: 'Domain-Specific',
      description: 'Specialized summary based on document type (70-200 words)',
      model: 'Auto-Selected',
      icon: 'fas fa-bullseye'
    }
  ]

  // Mock token for demo - in real app this would come from auth context
  const getToken = () => {
    const token = localStorage.getItem("token")
    if (!token) {
      setError("No authentication token found. Please log in again.")
      return null
    }
    return token
  }

  // Fetch user documents
  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const token = getToken()
        if (!token) return

        const response = await fetch("http://localhost:8000/api/documents/", {
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        })

        if (response.status === 401) {
          localStorage.removeItem("token")
          localStorage.removeItem("user")
          setError("Session expired. Please log in again.")
          return
        }

        if (!response.ok) {
          throw new Error("Failed to fetch documents")
        }

        const data = await response.json()
        setDocuments(data.documents || [])
      } catch (err) {
        console.error("Error fetching documents:", err)
        setError(err instanceof Error ? err.message : "Failed to load documents")
      } finally {
        setLoading(false)
      }
    }

    fetchDocuments()
  }, [])

  // Format date to relative time
  const formatRelativeTime = (isoString: string): string => {
    const past = new Date(isoString)
    const now = new Date()
    const diffInMs = now.getTime() - past.getTime()
    const diffInHours = diffInMs / (1000 * 60 * 60)
    const diffInDays = diffInHours / 24

    if (diffInHours < 1) return "Less than an hour ago"
    if (diffInHours < 24) return `${Math.floor(diffInHours)} hours ago`
    if (diffInDays < 7) return `${Math.floor(diffInDays)} days ago`
    return past.toLocaleDateString()
  }

  // Compute stats from real documents
  const stats = useMemo(() => {
    const total = documents.length
    const today = new Date().setHours(0, 0, 0, 0)
    const processedToday = documents.filter(
      (doc) =>
        doc.processing_status === "completed" &&
        new Date(doc.upload_date).getTime() >= today
    ).length
    const inQueue = documents.filter(doc => doc.processing_status === "processing").length
    const successRate = total > 0 ? ((documents.filter(doc => doc.processing_status === "completed").length / total) * 100).toFixed(1) : "0"

    return [
      {
        title: "Total Documents",
        value: total.toLocaleString(),
        change: "+12%",
        icon: "fas fa-file-alt",
        positive: true
      },
      {
        title: "Processed Today",
        value: processedToday.toString(),
        change: "+23%",
        icon: "fas fa-check-circle",
        positive: true
      },
      {
        title: "Processing Queue",
        value: inQueue.toString(),
        change: inQueue > 0 ? "-5%" : "0%",
        icon: "fas fa-clock",
        positive: inQueue === 0
      },
      {
        title: "Success Rate",
        value: `${successRate}%`,
        change: "+0.5%",
        icon: "fas fa-chart-line",
        positive: true
      },
    ]
  }, [documents])

  // Format recent documents with summary state
  const recentDocuments = useMemo((): DocumentWithSummary[] => {
    const formatted = documents
      .sort((a, b) => new Date(b.upload_date).getTime() - new Date(a.upload_date).getTime())
      .slice(0, 5) // Show more documents
      .map((doc): DocumentWithSummary => ({
        id: doc.id,
        name: doc.original_filename,
        type: doc.content_type?.split("/")[1]?.toUpperCase() || "FILE",
        status: doc.processing_status === "completed" ? "Completed" : 
                doc.processing_status === "processing" ? "Processing" : "Failed",
        uploadedAt: formatRelativeTime(doc.upload_date),
        confidence: doc.processing_status === "completed" ? 95 : null,
        showSummaryOptions: false,
        selectedModel: null,
        currentSummary: null,
        loadingSummary: false,
        generatingNew: false,
        summaryError: null
      }))
    
    setDocumentsWithSummary(formatted)
    return formatted
  }, [documents])

  // Toggle summary options for a document
  const toggleSummaryOptions = (docId: string) => {
    setDocumentsWithSummary(prev => prev.map(doc => {
      if (doc.id === docId) {
        const newShowState = !doc.showSummaryOptions
        return { 
          ...doc, 
          showSummaryOptions: newShowState,
          selectedModel: newShowState ? doc.selectedModel : null,
          currentSummary: newShowState ? doc.currentSummary : null,
          summaryError: null
        }
      }
      return { ...doc, showSummaryOptions: false }
    }))
  }

  // Select a model and fetch summary for that model
  const selectModel = async (docId: string, modelId: string) => {
    setDocumentsWithSummary(prev => prev.map(doc => 
      doc.id === docId 
        ? { 
            ...doc, 
            selectedModel: modelId, 
            loadingSummary: true, 
            summaryError: null,
            currentSummary: null 
          } 
        : doc
    ))

    try {
      const token = getToken()
      if (!token) return

      const response = await fetch(`http://localhost:8000/api/summarize/document/${docId}`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      })

      if (response.status === 401) {
        localStorage.removeItem("token")
        localStorage.removeItem("user")
        setError("Session expired. Please log in again.")
        return
      }

      if (response.ok) {
        const data = await response.json()
        if (data.success && data.summaries) {
          const matchingSummaries = data.summaries.filter((summary: Summary) => 
            summary.summary_type === modelId || 
            summary.summary_type.toLowerCase() === modelId.toLowerCase() ||
            summary.summary_type.replace(/[\s_-]/g, '').toLowerCase() === modelId.replace(/[\s_-]/g, '').toLowerCase()
          )

          if (matchingSummaries.length > 0) {
            const latestSummary = matchingSummaries.sort((a: Summary, b: Summary) => 
              new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
            )[0]

            setDocumentsWithSummary(prev => prev.map(doc => 
              doc.id === docId 
                ? { 
                    ...doc, 
                    currentSummary: latestSummary,
                    loadingSummary: false
                  }
                : doc
            ))
          } else {
            setDocumentsWithSummary(prev => prev.map(doc => 
              doc.id === docId 
                ? { 
                    ...doc, 
                    currentSummary: null,
                    loadingSummary: false
                  }
                : doc
            ))
          }
        } else {
          setDocumentsWithSummary(prev => prev.map(doc => 
            doc.id === docId 
              ? { 
                  ...doc, 
                  currentSummary: null,
                  loadingSummary: false
                }
              : doc
          ))
        }
      } else {
        console.error("Failed to fetch summaries")
        setDocumentsWithSummary(prev => prev.map(doc => 
          doc.id === docId 
            ? { 
                ...doc, 
                loadingSummary: false,
                summaryError: "Failed to load summary"
              }
            : doc
        ))
      }
    } catch (err) {
      console.error("Error fetching summaries:", err)
      setDocumentsWithSummary(prev => prev.map(doc => 
        doc.id === docId 
          ? { 
              ...doc, 
              loadingSummary: false, 
              summaryError: "Failed to load summary" 
            }
          : doc
      ))
    }
  }

  // Generate new summary
  const generateSummary = async (docId: string, summaryType: string) => {
    setDocumentsWithSummary(prev => prev.map(doc => 
      doc.id === docId ? { ...doc, generatingNew: true, summaryError: null } : doc
    ))

    try {
      const token = getToken()
      if (!token) return

      const response = await fetch("http://localhost:8000/api/summarize/", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          document_id: docId,
          summary_type: summaryType
        })
      })

      if (response.status === 401) {
        localStorage.removeItem("token")
        localStorage.removeItem("user")
        setError("Session expired. Please log in again.")
        return
      }

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Failed to generate summary")
      }

      const data = await response.json()
      
      if (data.success) {
        const newSummary: Summary = {
          id: Date.now(),
          summary_type: data.summary_type,
          summary_text: data.summary_text,
          word_count: data.word_count,
          model_used: data.model_used,
          created_at: data.created_at,
          from_cache: data.from_cache,
          document_type: data.document_type,
          key_points: data.key_points
        }

        setDocumentsWithSummary(prev => prev.map(doc => 
          doc.id === docId 
            ? { 
                ...doc, 
                currentSummary: newSummary,
                generatingNew: false
              }
            : doc
        ))
      } else {
        throw new Error("Summary generation failed")
      }
    } catch (err: any) {
      console.error("Error generating summary:", err)
      setDocumentsWithSummary(prev => prev.map(doc => 
        doc.id === docId 
          ? { 
              ...doc, 
              generatingNew: false, 
              summaryError: `Failed to generate summary: ${err.message}` 
            }
          : doc
      ))
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const getSummaryTypeColor = (type: string) => {
    const colors: { [key: string]: string } = {
      "Brief Summary": "status-badge status-completed",
      "brief": "status-badge status-completed",
      "Detailed Summary": "status-badge status-processing", 
      "detailed": "status-badge status-processing",
      "Domain Specific Summary": "status-badge",
      "Domain-Specific": "status-badge",
      "domain_specific": "status-badge"
    }
    return colors[type] || "status-badge"
  }

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      alert("Summary copied to clipboard!")
    } catch (err) {
      console.error("Failed to copy:", err)
      alert("Failed to copy summary")
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="error-message max-w-md w-full">
          <div className="flex items-center gap-3">
            <i className="fas fa-exclamation-triangle text-2xl text-yellow-500"></i>
            <p>{error}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="main-container">
      <div className="max-w-7xl mx-auto space-y-6">

        {/* Stats Grid - Single Compact Row */}
        <div className="grid grid-cols-4 gap-4">
          {stats.map((stat) => (
            <div key={stat.title} className="stats-card fade-in">
              <div className="stats-header">
                <i className={`stats-icon ${stat.icon}`}></i>
                <span className={`stats-change ${stat.positive ? 'positive' : 'negative'}`}>
                  {stat.change}
                </span>
              </div>
              <div className="stats-content">
                <div className="stats-value">{stat.value}</div>
                <div className="stats-title">{stat.title}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Recent Documents */}
        <div className="document-card">
          <div className="section-header">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <i className="fas fa-file-alt"></i> Recent Documents
            </h2>
            <p className="text-gray-600 text-sm mt-1">Your latest document processing activities</p>
          </div>
          <div className="p-6">
            {documentsWithSummary.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon"><i className="fas fa-file-alt"></i></div>
                <p>No documents uploaded yet.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {documentsWithSummary.map((doc) => (
                  <div key={doc.id} className="document-card">
                    {/* Document Card */}
                    <div className="document-card-header">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900">{doc.name}</h4>
                          <div className="flex items-center gap-4 mt-1">
                            <span className="status-badge">{doc.type}</span>
                            <span className="text-xs text-gray-500">{doc.uploadedAt}</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          {doc.confidence !== null && (
                            <div className="text-right">
                              <div className="text-sm font-medium">{doc.confidence}%</div>
                              <div className="progress-bar w-16">
                                <div 
                                  className="progress-fill" 
                                  style={{ width: `${doc.confidence}%` }}
                                ></div>
                              </div>
                            </div>
                          )}
                          <span className={`${
                            doc.status === "Completed" ? "status-completed" : 
                            doc.status === "Processing" ? "status-processing" : "status-failed"
                          }`}>
                            {doc.status}
                          </span>
                        </div>
                      </div>
                      <div className="flex gap-3">
                        <button 
                          onClick={() => toggleSummaryOptions(doc.id)}
                          className="btn btn-primary flex-1"
                        >
                          <i className="fas fa-chart-bar"></i>
                          {doc.showSummaryOptions ? 'Hide Summary' : 'Summarize'}
                        </button>
                        <button className="btn btn-success flex-1">
                          <i className="fas fa-comments"></i>
                          Chat with Doc
                        </button>
                      </div>
                    </div>

                    {/* Summary Section */}
                    {doc.showSummaryOptions && (
                      <div className="summary-section">
                        <h5 className="font-medium text-gray-900 mb-4">Document Summary</h5>
                        
                        {doc.summaryError && (
                          <div className="error-message mb-4">
                            <p>{doc.summaryError}</p>
                          </div>
                        )}

                        {/* Model Selection */}
                        <div className="mb-4">
                          <h6 className="text-sm font-medium text-gray-700 mb-3">Select Summary Type</h6>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                            {summaryOptions.map((option) => (
                              <button
                                key={option.id}
                                onClick={() => selectModel(doc.id, option.id)}
                                className={`summary-option ${
                                  doc.selectedModel === option.id ? 'selected' : ''
                                }`}
                              >
                                <div className="flex items-center gap-3">
                                  <i className={`text-xl ${option.icon}`}></i>
                                  <div className="text-left">
                                    <div className="font-medium text-sm">{option.name}</div>
                                    <div className="text-xs text-gray-600">{option.description}</div>
                                    <div className="text-xs text-gray-500 mt-1">Model: {option.model}</div>
                                  </div>
                                </div>
                              </button>
                            ))}
                          </div>
                        </div>

                        {/* Summary Content or Generate Option */}
                        {doc.selectedModel && (
                          <div className="border-t pt-4">
                            {doc.loadingSummary ? (
                              <div className="text-center py-8">
                                <div className="loading-spinner mx-auto"></div>
                                <p className="mt-2 text-sm text-gray-600">Loading summary...</p>
                              </div>
                            ) : doc.currentSummary ? (
                              /* Show Existing Summary */
                              <div className="fade-in">
                                <div className="flex items-center justify-between mb-4">
                                  <h6 className="text-sm font-medium text-gray-700">Summary Content</h6>
                                  <div className="flex items-center gap-2">
                                    {doc.currentSummary.from_cache && (
                                      <span className="status-badge status-completed">
                                        <i className="fas fa-clipboard"></i> From Cache
                                      </span>
                                    )}
                                    <span className={getSummaryTypeColor(doc.currentSummary.summary_type)}>
                                      {doc.currentSummary.summary_type}
                                    </span>
                                  </div>
                                </div>

                                {/* Summary Details */}
                                <div className="mb-4 p-3 bg-gray-50 rounded-lg border">
                                  <div className="grid grid-cols-3 gap-4 text-xs">
                                    <div>
                                      <span className="text-gray-500">Words:</span> {doc.currentSummary.word_count}
                                    </div>
                                    <div>
                                      <span className="text-gray-500">Model:</span> {doc.currentSummary.model_used}
                                    </div>
                                    <div>
                                      <span className="text-gray-500">Generated:</span> {formatDate(doc.currentSummary.created_at)}
                                    </div>
                                  </div>
                                </div>

                                {/* Summary Text */}
                                <div className="summary-content mb-4">
                                  <p className="text-gray-800 text-sm leading-relaxed whitespace-pre-wrap">
                                    {doc.currentSummary.summary_text}
                                  </p>
                                </div>

                                {/* Key Points */}
                                {doc.currentSummary.key_points && doc.currentSummary.key_points.length > 0 && (
                                  <div className="key-points mb-4">
                                    <h6 className="text-xs font-medium text-gray-700 mb-2">Key Points</h6>
                                    <ul className="space-y-1">
                                      {doc.currentSummary.key_points.map((point, index) => (
                                        <li key={index} className="key-point flex items-start gap-2 text-sm">
                                          <span className="text-blue-500 mt-1">•</span>
                                          <span className="text-gray-700">{point}</span>
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                )}

                                {/* Action Buttons */}
                                <div className="action-buttons">
                                  <button 
                                    onClick={() => copyToClipboard(doc.currentSummary!.summary_text)}
                                    className="btn btn-copy"
                                  >
                                    <i className="fas fa-clipboard"></i>
                                    Copy
                                  </button>
                                  <button className="btn btn-export">
                                    <i className="fas fa-file-export"></i>
                                    Export
                                  </button>
                                  <button className="btn btn-email">
                                    <i className="fas fa-envelope"></i>
                                    Email
                                  </button>
                                  <button 
                                    onClick={() => generateSummary(doc.id, doc.selectedModel!)}
                                    disabled={doc.generatingNew}
                                    className="btn btn-regenerate"
                                  >
                                    {doc.generatingNew ? "Generating..." : (
                                      <>
                                        <i className="fas fa-sync-alt"></i>
                                        Regenerate
                                      </>
                                    )}
                                  </button>
                                </div>
                              </div>
                            ) : (
                              /* Show Generate Option */
                              <div className="text-center py-8">
                                <div className="text-3xl mb-3"><i className="fas fa-robot"></i></div>
                                <p className="text-gray-600 mb-2">No summary available for this model</p>
                                <p className="text-gray-500 text-sm mb-4">Generate a new summary with the selected model</p>
                                
                                <button
                                  onClick={() => generateSummary(doc.id, doc.selectedModel!)}
                                  disabled={doc.generatingNew}
                                  className="btn btn-generate"
                                >
                                  {doc.generatingNew ? (
                                    <>
                                      <div className="loading-spinner w-4 h-4 inline-block mr-2"></div>
                                      Generating...
                                    </>
                                  ) : (
                                    <>
                                      <i className="fas fa-magic"></i>
                                      Generate Summary
                                    </>
                                  )}
                                </button>

                                {doc.generatingNew && (
                                  <div className="mt-4 text-sm text-blue-600">
                                    This may take a few moments...
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard