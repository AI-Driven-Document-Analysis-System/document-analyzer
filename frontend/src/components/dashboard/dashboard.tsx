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
  const [activeView, setActiveView] = useState<'documents' | 'chat'>('documents')
  const [selectedDocument, setSelectedDocument] = useState<any>(null)
  const [summaryModalOpen, setSummaryModalOpen] = useState(false)
  const [selectedDocumentForSummary, setSelectedDocumentForSummary] = useState<{id: string, name: string} | null>(null)

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
      // You could add a toast notification here
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  const handleChatWithDoc = (doc: DocumentWithSummary) => {
    setSelectedDocument(doc)
    setActiveView('chat')
  }

  const handleSummarizeDoc = (doc: DocumentWithSummary) => {
    console.log('Summarize button clicked for doc:', doc.name)
    setSelectedDocumentForSummary({
      id: doc.id,
      name: doc.name
    })
    setSummaryModalOpen(true)
    console.log('Modal should be open now')
  }

  const closeSummaryModal = () => {
    setSummaryModalOpen(false)
    setSelectedDocumentForSummary(null)
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

        {/* Search and Chat Feature - Exact Qwen Structure */}
        <div className="feature-container">
          {/* Tabs */}
          <div className="tabs-container d-flex">
            <button 
              className={`tab-btn ${activeView === 'documents' ? 'active' : ''}`}
              onClick={() => setActiveView('documents')}
            >
              <i className="fas fa-search me-2"></i>Search Documents
            </button>
            <button 
              className={`tab-btn ${activeView === 'chat' ? 'active' : ''}`}
              onClick={() => setActiveView('chat')}
            >
              <i className="fas fa-robot me-2"></i>Ask DocuMind AI
            </button>
          </div>

          {/* Tab Content */}
          <div className="tab-content-container">
            {/* Search Tab */}
            {activeView === 'documents' && (
              <div id="search-tab" className="tab-content active">
                <div className="search-input-group">
                  <span className="search-icon"><i className="fas fa-search"></i></span>
                  <input 
                    type="text" 
                    className="form-control" 
                    placeholder="Search across all your documents..."
                  />
                </div>

                <div id="searchResults">
                  <h5 className="mb-4"><i className="fas fa-history me-2"></i>Recent Documents</h5>
                  
                  {documentsWithSummary.length === 0 ? (
                    <div className="text-center py-5">
                      <i className="fas fa-file-alt" style={{fontSize: '4rem', color: '#dee2e6'}}></i>
                      <p className="mt-3 text-muted">No documents uploaded yet.</p>
                    </div>
                  ) : (
                    documentsWithSummary.map((doc) => (
                      <div key={doc.id} className="result-item">
                        <div className="d-flex">
                          <div className="result-icon">
                            <i className="fas fa-file-invoice"></i>
                          </div>
                          <div className="flex-grow-1">
                            <div className="result-title">
                              {doc.name}
                              <span className="doc-type-tag tag-invoice">{doc.type}</span>
                            </div>
                            <div className="result-snippet">
                              Financial summary for Q4 2023 showing a 12% increase in revenue compared to previous year...
                            </div>
                            <div className="result-meta">
                              PDF • 2.4 MB • Last accessed: {doc.uploadedAt}
                            </div>
                            <div className="result-actions">
                              <button 
                                className="btn summarize-btn"
                                onClick={() => {
                                  setSelectedDocumentForSummary({
                                    id: doc.id,
                                    name: doc.name
                                  });
                                  setSummaryModalOpen(true);
                                }}
                              >
                                <i className="fas fa-file-contract me-1"></i>Summarize
                              </button>
                              <button 
                                className="btn chat-doc-btn"
                                onClick={() => handleChatWithDoc(doc)}
                              >
                                <i className="fas fa-comments me-1"></i>Chat with Doc
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}

            {/* Chat Tab */}
            {activeView === 'chat' && (
              <div className="tab-content active">
                {selectedDocument && (
                  <div className="selected-document-context">
                    <div className="context-header">
                      <i className="fas fa-file-alt"></i>
                      <span>Chatting about: {selectedDocument.filename}</span>
                      <button 
                        className="btn btn-sm btn-outline-secondary"
                        onClick={() => setSelectedDocument(null)}
                      >
                        <i className="fas fa-times"></i>
                      </button>
                    </div>
                  </div>
                )}
                <div className="chat-messages">
                  <div className="message bot">
                    <div className="message-content">
                      {selectedDocument 
                        ? `Hello! I'm ready to help you with "${selectedDocument.name}". What would you like to know about this document?`
                        : "Hello! I'm DocuMind AI. I can help you analyze and understand your documents. What would you like to know?"
                      }
                    </div>
                  </div>
                  {selectedDocument && (
                    <div className="message bot">
                      <div className="message-content">
                        I can see you've selected "{selectedDocument.name}". I can help you:
                        <ul>
                          <li>Summarize key points</li>
                          <li>Answer specific questions about the content</li>
                          <li>Extract important data or insights</li>
                          <li>Compare with other documents</li>
                        </ul>
                        What would you like to explore?
                      </div>
                    </div>
                  )}
                </div>
                <div className="chat-input-group">
                  <input 
                    type="text" 
                    className="form-control" 
                    placeholder={selectedDocument 
                      ? `Ask about ${selectedDocument.name}...` 
                      : "Ask DocuMind AI anything about your documents..."
                    } 
                  />
                  <button className="btn btn-primary">
                    <i className="fas fa-paper-plane"></i>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Content Area */}
        <div className="grid grid-cols-12 gap-6">
          {/* Right Side - Quick Actions */}
          <div className="col-span-12">
            <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
              <div className="section-header mb-4">
                <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <i className="fas fa-bolt"></i> Quick Actions
                </h2>
                <p className="text-gray-600 text-sm mt-1">Common tasks and shortcuts</p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <button className="flex items-center gap-3 p-4 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors text-left">
                  <i className="fas fa-cloud-upload-alt text-blue-600 text-xl"></i>
                  <div>
                    <div className="font-medium text-gray-900">Upload Document</div>
                    <div className="text-sm text-gray-600">Add new files for analysis</div>
                  </div>
                </button>
                <button className="flex items-center gap-3 p-4 bg-green-50 hover:bg-green-100 rounded-lg transition-colors text-left">
                  <i className="fas fa-brain text-green-600 text-xl"></i>
                  <div>
                    <div className="font-medium text-gray-900">Summarize</div>
                    <div className="text-sm text-gray-600">Generate AI summaries</div>
                  </div>
                </button>
                <button className="flex items-center gap-3 p-4 bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors text-left">
                  <i className="fas fa-search text-purple-600 text-xl"></i>
                  <div>
                    <div className="font-medium text-gray-900">Search</div>
                    <div className="text-sm text-gray-600">Find content in documents</div>
                  </div>
                </button>
                <button className="flex items-center gap-3 p-4 bg-orange-50 hover:bg-orange-100 rounded-lg transition-colors text-left">
                  <i className="fas fa-chart-bar text-orange-600 text-xl"></i>
                  <div>
                    <div className="font-medium text-gray-900">Analytics</div>
                    <div className="text-sm text-gray-600">View processing insights</div>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Working Modal */}
      {summaryModalOpen && selectedDocumentForSummary && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999
          }}
          onClick={() => setSummaryModalOpen(false)}
        >
          <div 
            style={{
              backgroundColor: 'white',
              borderRadius: '8px',
              maxWidth: '800px',
              width: '90%',
              maxHeight: '90vh',
              overflow: 'auto',
              boxShadow: '0 10px 25px rgba(0, 0, 0, 0.2)'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div style={{ padding: '1.5rem', borderBottom: '1px solid #dee2e6', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h5 style={{ margin: 0, fontSize: '1.25rem', fontWeight: '600' }}>Document Summary</h5>
              <button 
                onClick={() => setSummaryModalOpen(false)}
                style={{ 
                  background: 'none',
                  border: 'none', 
                  fontSize: '2.2rem', 
                  cursor: 'pointer',
                  color: '#6c757d',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 'bold',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => (e.target as HTMLButtonElement).style.color = '#495057'}
                onMouseLeave={(e) => (e.target as HTMLButtonElement).style.color = '#6c757d'}
              >
                ×
              </button>
            </div>

            {/* Modal Body */}
            <div style={{ padding: '1.5rem' }}>
              {/* Document Info */}
              <div style={{ marginBottom: '1rem' }}>
                <strong>Document:</strong> {selectedDocumentForSummary.name}
              </div>

              {/* Model Selection and Regenerate */}
              <div style={{ display: 'flex', alignItems: 'end', gap: '1rem', marginBottom: '1.5rem' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                    Summarization Model:
                  </label>
                  <select 
                    style={{ 
                      width: '100%', 
                      padding: '0.5rem', 
                      border: '1px solid #ced4da', 
                      borderRadius: '4px',
                      fontSize: '1rem'
                    }}
                  >
                    <option value="pegasus">Pegasus (Default - High Quality)</option>
                    <option value="bart">BART (Balanced)</option>
                    <option value="t5">T5 (Flexible for Technical Docs)</option>
                  </select>
                </div>
                <button 
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: '#007bff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}
                >
                  <i className="fas fa-sync-alt"></i>
                  Regenerate
                </button>
              </div>

              {/* Summary Metadata */}
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(4, 1fr)', 
                gap: '1rem', 
                marginBottom: '1rem',
                padding: '1rem',
                backgroundColor: '#f8f9fa',
                borderRadius: '4px'
              }}>
                <div>
                  <small style={{ color: '#6c757d' }}>Word Count:</small><br />
                  <span>245</span>
                </div>
                <div>
                  <small style={{ color: '#6c757d' }}>Model:</small><br />
                  <span>Pegasus</span>
                </div>
                <div>
                  <small style={{ color: '#6c757d' }}>Cache:</small><br />
                  <span style={{ 
                    backgroundColor: '#28a745', 
                    color: 'white', 
                    padding: '0.25rem 0.5rem', 
                    borderRadius: '4px', 
                    fontSize: '0.75rem' 
                  }}>
                    Cached
                  </span>
                </div>
                <div>
                  <small style={{ color: '#6c757d' }}>Generated:</small><br />
                  <span>Just now</span>
                </div>
              </div>

              {/* Summary Content */}
              <div style={{ 
                border: '1px solid #dee2e6', 
                borderRadius: '4px', 
                padding: '1rem', 
                backgroundColor: '#f8f9fa',
                marginBottom: '1rem'
              }}>
                This document provides a comprehensive overview of computer vision fundamentals and applications. Key growth drivers included expansion in international markets and successful launch of new product lines. Operating expenses increased by 8%, primarily due to R&D investments. Net profit margin improved to 18.5% from 17.2% last year.
              </div>

              {/* Key Points */}
              <div>
                <h6 style={{ marginBottom: '0.5rem' }}>Key Points:</h6>
                <ul style={{ paddingLeft: '1.5rem' }}>
                  <li>Computer vision fundamentals covered comprehensively</li>
                  <li>International market expansion drove growth</li>
                  <li>R&D investments increased operating expenses by 8%</li>
                  <li>Net profit margin improved from 17.2% to 18.5%</li>
                </ul>
              </div>

              {/* Close Button */}
              <div style={{ textAlign: 'right', marginTop: '2rem' }}>
                <button 
                  onClick={() => setSummaryModalOpen(false)}
                  style={{
                    padding: '0.75rem 2rem',
                    backgroundColor: '#6c757d',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '1rem'
                  }}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard