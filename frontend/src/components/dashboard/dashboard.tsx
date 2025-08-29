//****************************CSS */
import { useState, useEffect, useMemo } from "react"
import './Dashboard.css' // Import the CSS file
import '../../styles/components.css';
//import DocumentViewer from '../DocumentViewer/DocumentViewer';


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

// Inline styles for modal
const modalStyles = {
  overlay: {
    position: 'fixed' as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(0, 0, 0, 0.75)',
    backdropFilter: 'blur(8px)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 9999,
    padding: '20px',
    animation: 'fadeInModal 0.3s ease-out'
  },
  container: {
    background: 'white',
    borderRadius: '16px',
    width: '90vw',
    maxWidth: '1200px',
    height: '90vh',
    maxHeight: '900px',
    display: 'flex',
    flexDirection: 'column' as const,
    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
    overflow: 'hidden',
    position: 'relative' as const,
    animation: 'slideInModal 0.3s ease-out'
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '20px 24px',
    borderBottom: '1px solid #e5e7eb',
    background: 'linear-gradient(135deg, #f8fafc, #e2e8f0)',
    flexShrink: 0
  },
  title: {
    flex: 1
  },
  titleH3: {
    fontSize: '1.25rem',
    fontWeight: 600,
    color: '#1a202c',
    margin: '0 0 4px 0'
  },
  titleP: {
    fontSize: '0.875rem',
    color: '#718096',
    margin: 0
  },
  closeButton: {
    background: 'none',
    border: 'none',
    fontSize: '24px',
    color: '#718096',
    cursor: 'pointer',
    padding: '8px',
    borderRadius: '8px',
    transition: 'all 0.2s ease',
    lineHeight: 1,
    marginLeft: '16px'
  },
  body: {
    flex: 1,
    padding: 0,
    overflow: 'hidden',
    position: 'relative' as const,
    background: '#f7fafc'
  },
  viewer: {
    width: '100%',
    height: '100%',
    position: 'relative' as const
  },
  iframe: {
    width: '100%',
    height: '100%',
    border: 'none',
    background: 'white'
  },
  imageViewer: {
    width: '100%',
    height: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '20px',
    overflow: 'auto'
  },
  image: {
    maxWidth: '100%',
    maxHeight: '100%',
    objectFit: 'contain' as const,
    borderRadius: '8px',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)'
  },
  loading: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    color: '#718096'
  },
  loadingSpinner: {
    width: '48px',
    height: '48px',
    border: '4px solid #e2e8f0',
    borderTop: '4px solid #667eea',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    marginBottom: '16px'
  },
  error: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    textAlign: 'center' as const,
    color: '#718096',
    padding: '40px'
  },
  errorIcon: {
    fontSize: '4rem',
    marginBottom: '16px',
    color: '#e53e3e'
  },
  errorH4: {
    fontSize: '1.25rem',
    color: '#2d3748',
    marginBottom: '8px'
  },
  errorP: {
    color: '#718096',
    marginBottom: '24px'
  },
  unsupported: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    textAlign: 'center' as const,
    padding: '40px',
    color: '#718096'
  },
  fileIcon: {
    fontSize: '4rem',
    marginBottom: '16px',
    color: '#a0aec0'
  },
  downloadBtn: {
    background: 'linear-gradient(135deg, #667eea, #764ba2)',
    color: 'white',
    border: 'none',
    padding: '12px 24px',
    borderRadius: '8px',
    fontSize: '1rem',
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  }
};

// Main Dashboard Component
function Dashboard() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [documentsWithSummary, setDocumentsWithSummary] = useState<DocumentWithSummary[]>([])
  // Chat and modal states
  const [activeView, setActiveView] = useState<'documents' | 'chat'>('documents')
  const [selectedDocument, setSelectedDocument] = useState<any>(null)
  const [summaryModalOpen, setSummaryModalOpen] = useState(false)
  const [selectedDocumentForSummary, setSelectedDocumentForSummary] = useState<{id: string, name: string} | null>(null)
  
  // Document preview states
  const [previewDocument, setPreviewDocument] = useState<DocumentWithSummary | null>(null)
  const [showPreview, setShowPreview] = useState(false)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [loadingPreview, setLoadingPreview] = useState(false)

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

  // JWT token handling
  const getToken = () => {
    const token = localStorage.getItem("token")
    return token
  }

  // Document preview handler
  const previewDocumentHandler = async (doc: DocumentWithSummary) => {
    setLoadingPreview(true)
    setPreviewDocument(doc)
    setShowPreview(true)

    try {
      const token = getToken()
      if (!token) return

      const response = await fetch(`http://localhost:8000/api/documents/${doc.id}/download`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      })

      if (response.ok) {
        const data = await response.json()
        setPreviewUrl(data.download_url)
      } else {
        console.error("Failed to get preview URL")
        alert("Failed to load document preview")
      }
    } catch (err) {
      console.error("Error getting preview URL:", err)
      alert("Error loading document preview")
    } finally {
      setLoadingPreview(false)
    }
  }

  // Close preview
  const closePreview = () => {
    setShowPreview(false)
    setPreviewDocument(null)
    setPreviewUrl(null)
  }

  // Fetch user documents with JWT authentication and fallback
  useEffect(() => {
    const fetchDocuments = async () => {
      const tryFallback = async () => {
        try {
          const userStr = localStorage.getItem("user")
          if (!userStr) {
            throw new Error("No user info found for fallback fetch")
          }
          const user = JSON.parse(userStr)
          const userId = user?.id || user?.user?.id || user?.user_id
          if (!userId) {
            throw new Error("No user_id in local storage user")
          }
          const res = await fetch(`http://localhost:8000/api/documents/by-user?user_id=${encodeURIComponent(userId)}`)
          if (!res.ok) {
            throw new Error("Fallback fetch failed")
          }
          const data = await res.json()
          setDocuments(data.documents || [])
          setError(null)
        } catch (e) {
          console.error("Fallback documents fetch error:", e)
          setError("Failed to load documents")
        } finally {
          setLoading(false)
        }
      }

      try {
        const token = getToken()
        if (!token) {
          await tryFallback()
          return
        }

        const response = await fetch("http://localhost:8000/api/documents/", {
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        })

        if (response.status === 401) {
          localStorage.removeItem("token")
          await tryFallback()
          return
        }

        if (!response.ok) {
          await tryFallback()
          return
        }

        const data = await response.json()
        setDocuments(data.documents || [])
        setLoading(false)
      } catch (err) {
        console.error("Error fetching documents:", err)
        await tryFallback()
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

  // Other handler functions
  const handleChatWithDoc = (doc: DocumentWithSummary) => {
    setSelectedDocument(doc)
    setActiveView('chat')
  }

  const handleSummarizeDoc = (doc: DocumentWithSummary) => {
    setSelectedDocumentForSummary({
      id: doc.id,
      name: doc.name
    })
    setSummaryModalOpen(true)
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
        {/* Stats Grid */}
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

        {/* Search and Chat Feature */}
        <div className="feature-container">
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

          <div className="tab-content-container">
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
                                onClick={() => handleSummarizeDoc(doc)}
                              >
                                <i className="fas fa-file-contract me-1"></i>Summarize
                              </button>
                              <button
                                className="btn chat-doc-btn"
                                onClick={() => handleChatWithDoc(doc)}
                              >
                                <i className="fas fa-comments me-1"></i>Chat with Doc
                              </button>
                              <button
                                onClick={() => previewDocumentHandler(doc)}
                                className="btn btn-secondary"
                              >
                                <i className="fas fa-eye me-1"></i>Preview
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))
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

        {/* Document Preview Modal */}
        {showPreview && (
          <div style={modalStyles.overlay}>
            <div style={modalStyles.container}>
              <div style={modalStyles.header}>
                <div style={modalStyles.title}>
                  <h3 style={modalStyles.titleH3}>{previewDocument?.name}</h3>
                  <p style={modalStyles.titleP}>{previewDocument?.type} • {previewDocument?.uploadedAt}</p>
                </div>
                <button
                  onClick={closePreview}
                  style={modalStyles.closeButton}
                >
                  ✕
                </button>
              </div>

              <div style={modalStyles.body}>
                {loadingPreview ? (
                  <div style={modalStyles.loading}>
                    <div style={modalStyles.loadingSpinner}></div>
                    <p>Loading document preview...</p>
                  </div>
                ) : previewUrl ? (
                  <div style={modalStyles.viewer}>
                    {previewDocument?.type === 'PDF' ? (
                      <iframe
                        src={previewUrl}
                        style={modalStyles.iframe}
                        title="Document Preview"
                      />
                    ) : previewDocument?.type?.startsWith('image/') ||
                         ['JPG', 'JPEG', 'PNG', 'GIF'].includes(previewDocument?.type || '') ? (
                      <div style={modalStyles.imageViewer}>
                        <img
                          src={previewUrl}
                          alt="Document Preview"
                          style={modalStyles.image}
                        />
                      </div>
                    ) : (
                      <div style={modalStyles.unsupported}>
                        <div style={modalStyles.fileIcon}><i className="fas fa-file"></i></div>
                        <h4 style={modalStyles.titleH3}>Preview not available</h4>
                        <p style={modalStyles.titleP}>Preview not available for this file type</p>
                        <a
                          href={previewUrl}
                          download={previewDocument?.name}
                          style={modalStyles.downloadBtn}
                        >
                          <i className="fas fa-download"></i>
                          Download Document
                        </a>
                      </div>
                    )}
                  </div>
                ) : (
                  <div style={modalStyles.error}>
                    <div style={modalStyles.errorIcon}><i className="fas fa-exclamation-triangle"></i></div>
                    <h4 style={modalStyles.errorH4}>Failed to load document preview</h4>
                    <p style={modalStyles.errorP}>Unable to load the document preview</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes fadeInModal {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        @keyframes slideInModal {
          from {
            opacity: 0;
            transform: scale(0.95) translateY(-20px);
          }
          to {
            opacity: 1;
            transform: scale(1) translateY(0);
          }
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
          .modal-overlay { padding: 10px; }
          .modal-container { width: 95vw; height: 95vh; }
          .modal-header { padding: 16px 20px; }
          .modal-header h3 { font-size: 1.125rem; }
          .image-viewer { padding: 16px; }
        }

        ${showPreview ? 'body { overflow: hidden; }' : ''}
      `}</style>
    </div>
  )
}

export default Dashboard
