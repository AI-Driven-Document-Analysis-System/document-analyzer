import React, { useState, useEffect } from "react"
import { authService } from "../../services/authService"
import "./document_view.css"

// Keep interfaces unchanged
interface Document {
  id: string
  original_filename: string
  content_type: string
  file_size: number
  processing_status: 'completed' | 'processing' | 'failed'
  upload_date: string
  user_id: string
  thumbnail_url?: string
  document_type?: string
  created_at: string
  updated_at: string
}

interface DocumentViewProps {
  authToken?: string
  onAuthError?: () => void
}

// Helper functions unchanged
const getFileIcon = (contentType: string) => {
  if (contentType.includes("pdf")) return { icon: "📄", colorClass: "docview-color-red", bgClass: "docview-bg-red", accentClass: "docview-accent-red" }
  if (contentType.includes("image")) return { icon: "🖼️", colorClass: "docview-color-blue", bgClass: "docview-bg-blue", accentClass: "docview-accent-blue" }
  if (contentType.includes("spreadsheet") || contentType.includes("excel")) return { icon: "📊", colorClass: "docview-color-green", bgClass: "docview-bg-green", accentClass: "docview-accent-green" }
  if (contentType.includes("word") || contentType.includes("document")) return { icon: "📝", colorClass: "docview-color-blue-dark", bgClass: "docview-bg-blue", accentClass: "docview-accent-blue-dark" }
  if (contentType.includes("text")) return { icon: "📄", colorClass: "docview-color-gray", bgClass: "docview-bg-gray", accentClass: "docview-accent-gray" }
  return { icon: "📁", colorClass: "docview-color-gray-light", bgClass: "docview-bg-gray", accentClass: "docview-accent-gray-light" }
}

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'completed': return "docview-badge-success"
    case 'processing': return "docview-badge-warning"
    case 'failed': return "docview-badge-error"
    default: return "docview-badge-default"
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export function DocumentView({ authToken: propAuthToken, onAuthError }: DocumentViewProps = {}) {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [filterStatus, setFilterStatus] = useState<string>("all")
  const [sortBy, setSortBy] = useState<string>("newest")
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null)
  const [authToken, setAuthToken] = useState<string | null>(null)

  // Get auth token
  React.useEffect(() => {
    const token = propAuthToken || authService.getToken()
    setAuthToken(token)
  }, [propAuthToken])

  // Fetch documents
  const fetchDocuments = async () => {
    try {
      setLoading(true)
      setError(null)

      if (!authToken) {
        throw new Error('No authentication token provided')
      }

      const response = await fetch('http://localhost:8000/api/documents/', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        if (response.status === 401) {
          onAuthError?.()
          throw new Error('Authentication failed. Please log in again.')
        }
        throw new Error(`Failed to fetch documents: ${response.statusText}`)
      }

      const data = await response.json()
      console.log('API Response:', data)
      
      if (Array.isArray(data)) {
        setDocuments(data)
      } else if (data && Array.isArray(data.documents)) {
        setDocuments(data.documents)
      } else if (data && Array.isArray(data.data)) {
        setDocuments(data.data)
      } else {
        console.warn('API response is not an array:', data)
        setDocuments([])
      }
    } catch (error) {
      console.error('Error fetching documents:', error)
      setError(error instanceof Error ? error.message : 'Failed to fetch documents')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (authToken) {
      fetchDocuments()
    }
  }, [authToken])

  // Filter and sort documents
  const filteredDocuments = (Array.isArray(documents) ? documents : [])
    .filter(doc => {
      const matchesSearch = doc.original_filename.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesStatus = filterStatus === "all" || doc.processing_status === filterStatus
      return matchesSearch && matchesStatus
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return new Date(b.upload_date).getTime() - new Date(a.upload_date).getTime()
        case 'oldest':
          return new Date(a.upload_date).getTime() - new Date(b.upload_date).getTime()
        case 'name':
          return a.original_filename.localeCompare(b.original_filename)
        case 'size':
          return b.file_size - a.file_size
        default:
          return 0
      }
    })

  // Get recent files (last 3 uploaded)
  const recentFiles = (Array.isArray(documents) ? documents : [])
    .sort((a, b) => new Date(b.upload_date).getTime() - new Date(a.upload_date).getTime())
    .slice(0, 3)

  const handleDocumentClick = (document: Document) => {
    // setSelectedDocument(document) // Disabled to fix preview errors
  }

  const handleDownload = async (document: Document) => {
    try {
      const response = await fetch(`http://localhost:8000/api/documents/${document.id}/download`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to download document')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = window.document.createElement('a')
      a.href = url
      a.download = document.original_filename
      window.document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      window.document.body.removeChild(a)
    } catch (error) {
      console.error('Error downloading document:', error)
      alert('Failed to download document')
    }
  }

  const handleDelete = async (document: Document) => {
    if (!confirm(`Are you sure you want to delete "${document.original_filename}"?`)) {
      return
    }

    try {
      const response = await fetch(`http://localhost:8000/api/documents/${document.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to delete document')
      }

      setDocuments(prev => prev.filter(doc => doc.id !== document.id))
      if (selectedDocument?.id === document.id) {
        setSelectedDocument(null)
      }
    } catch (error) {
      console.error('Error deleting document:', error)
      alert('Failed to delete document')
    }
  }

  // LOADING STATE
  if (loading) {
    return (
      <div className="docview-container docview-loading">
        <div className="docview-loading-card">
          <div className="docview-spinner"></div>
          <p className="docview-loading-text">Loading your documents...</p>
          <div className="docview-progress-bar">
            <div className="docview-progress-fill"></div>
          </div>
        </div>
      </div>
    )
  }

  // ERROR STATE
  if (error) {
    return (
      <div className="docview-container docview-error">
        <div className="docview-error-card">
          <div className="docview-error-icon">
            <i className="fas fa-exclamation-triangle"></i>
          </div>
          <h2 className="docview-error-title">Oops! Something went wrong</h2>
          <p className="docview-error-message">{error}</p>
          <button
            onClick={fetchDocuments}
            className="docview-cta-button docview-cta-primary"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <>
      

      <div className="docview-min-h-screen docview-bg-gray-50">
        {/* Header with Search */}
        <div className="docview-header">
          <div className="docview-header-container docview-flex docview-items-center docview-justify-between docview-gap-6">
            {/* Left Side - Search Bar */}
            <div className="docview-flex-1 docview-max-w-2xl docview-relative">
              <div className="docview-relative">
                <div className="docview-search-icon">
                  <i className="fas fa-search docview-icon"></i>
                </div>
                <input
                  type="text"
                  placeholder="Search documents by name..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="docview-search-input docview-w-full docview-text-gray-700 docview-placeholder-gray-400"
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery("")}
                    className="docview-search-clear"
                  >
                    <i className="fas fa-times docview-icon-sm"></i>
                  </button>
                )}
              </div>
            </div>

            {/* Right Side - Controls */}
            <div className="docview-flex docview-items-center docview-gap-4">
              {/* View Options */}
              <div className="docview-view-toggle">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`docview-view-button ${viewMode === 'grid' ? 'docview-active' : ''}`}
                  title="Grid View"
                >
                  <i className="fas fa-th docview-icon"></i>
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`docview-view-button ${viewMode === 'list' ? 'docview-active' : ''}`}
                  title="List View"
                >
                  <i className="fas fa-list docview-icon"></i>
                </button>
              </div>

              {/* Filters */}
              <div className="docview-flex docview-items-center docview-gap-3">
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="docview-select"
                >
                  <option value="all">All Status</option>
                  <option value="completed">Completed</option>
                  <option value="processing">Processing</option>
                  <option value="failed">Failed</option>
                </select>
                
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="docview-select"
                >
                  <option value="newest">Newest First</option>
                  <option value="oldest">Oldest First</option>
                  <option value="name">Name A-Z</option>
                  <option value="size">Size (Largest)</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="docview-max-w-7xl docview-mx-auto docview-px-6 docview-py-8">
          {/* Recent Files Section */}
          {recentFiles.length > 0 && (
            <div className="docview-mb-12">
              <div className="docview-flex docview-items-center docview-justify-between docview-mb-6">
                <div>
                  <h2 className="docview-text-2xl docview-font-bold docview-text-gray-800">Recent Files</h2>
                  <p className="docview-text-gray-500 docview-mt-1 docview-text-sm">Your most recently uploaded documents</p>
                </div>
                <button className="docview-text-blue-600 hover:docview-text-blue-700 docview-font-medium docview-flex docview-items-center docview-gap-2 docview-transition-colors docview-duration-300 group">
                  View All
                  <i className="fas fa-arrow-right docview-text-xs group-hover:docview-translate-x-1 docview-transition-transform docview-duration-300"></i>
                </button>
              </div>
              <div className="docview-flex docview-gap-6 docview-overflow-x-auto docview-pb-4 docview-scrollbar-hide">
                {recentFiles.map((document) => {
                  const fileIcon = getFileIcon(document.content_type)
                  return (
                    <div
                      key={`recent-${document.id}`}
                      className="docview-recent-file docview-cursor-pointer docview-group docview-relative docview-overflow-hidden"
                      onClick={() => handleDocumentClick(document)}
                    >
                      {/* Decorative accent bar */}
                      <div className={`docview-absolute docview-top-0 docview-left-0 docview-w-full docview-h-1 ${fileIcon.accentClass} docview-accent-bar`}></div>
                      
                      <div className="docview-flex docview-flex-col docview-h-full">
                        <div className="docview-flex docview-items-center docview-gap-4 docview-mb-4">
                          <div className={`docview-w-14 docview-h-14 ${fileIcon.bgClass} docview-rounded-2xl docview-flex docview-items-center docview-justify-center docview-text-2xl docview-shadow-sm`}>
                            {fileIcon.icon}
                          </div>
                          <div className="docview-flex-1 docview-min-w-0">
                            <p className="docview-text-base docview-font-semibold docview-text-gray-900 docview-line-clamp-2 docview-leading-tight group-hover:docview-text-blue-600 docview-transition-colors docview-duration-300">
                              {document.original_filename}
                            </p>
                          </div>
                        </div>
                        
                        <div className="docview-mt-auto">
                          <div className="docview-flex docview-items-center docview-justify-between">
                            <span className="docview-text-xs docview-text-gray-500">
                              {formatDate(document.upload_date)}
                            </span>
                            <span className={`docview-badge ${getStatusBadgeClass(document.processing_status)}`}>
                              {document.processing_status}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Files Section */}
          <div>
            <div className="docview-flex docview-items-center docview-justify-between docview-mb-8">
              <div>
                <h2 className="docview-text-2xl docview-font-bold docview-text-gray-800">All Files</h2>
                <p className="docview-text-gray-500 docview-mt-1 docview-text-sm">
                  {filteredDocuments.length} {filteredDocuments.length === 1 ? 'document' : 'documents'} found
                </p>
              </div>
            </div>

            {/* Documents Grid/List */}
            {filteredDocuments.length === 0 ? (
              <div className="docview-empty-state">
                <div className="docview-empty-icon">
                  <i className="fas fa-folder-open"></i>
                </div>
                <h3 className="docview-empty-title">No documents found</h3>
                <p className="docview-empty-message">
                  {searchQuery || filterStatus !== "all" 
                    ? "Try adjusting your search terms or filters to find what you're looking for"
                    : "Upload your first document to get started. Your files will appear here."
                  }
                </p>
                <button className="docview-cta-primary">
                  Upload Document
                </button>
              </div>
            ) : viewMode === 'grid' ? (
              <div className="grid docview-grid-cols-1 docview-grid-cols-2 docview-grid-cols-3 docview-grid-cols-4 docview-grid-cols-5 docview-gap-6">
                {filteredDocuments.map((document, index) => {
                  const fileIcon = getFileIcon(document.content_type)
                  return (
                    <div
                      key={document.id}
                      className="docview-grid-item docview-cursor-pointer docview-group docview-relative docview-overflow-hidden"
                      onClick={() => handleDocumentClick(document)}
                    >
                      {/* Decorative accent bar */}
                      <div className={`docview-absolute docview-top-0 docview-left-0 docview-w-full docview-h-1 ${fileIcon.accentClass} docview-accent-bar`}></div>
                      
                      {/* Document Preview/Icon */}
                      <div className={`docview-file-preview ${fileIcon.bgClass} docview-rounded-t-2xl docview-flex docview-flex-col docview-items-center docview-justify-center docview-relative docview-overflow-hidden`}>
                        {document.thumbnail_url ? (
                          <img
                            src={document.thumbnail_url}
                            alt={document.original_filename}
                            className="docview-w-full docview-h-full docview-object-cover group-hover:docview-scale-110 docview-transition-transform docview-duration-500"
                          />
                        ) : (
                          <div className="docview-flex docview-flex-col docview-items-center docview-justify-center docview-h-full docview-p-6">
                            <div className="docview-file-icon-container docview-group-hover:docview-scale-110 docview-transition-transform docview-duration-300">
                              {fileIcon.icon}
                            </div>
                            <div className="docview-file-type">
                              {document.content_type.split('/')[1]?.toUpperCase() || 'FILE'}
                            </div>
                          </div>
                        )}
                        
                        {/* Action Buttons */}
                        <div className="docview-action-buttons">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDownload(document)
                            }}
                            className="docview-action-button docview-download"
                            title="Download"
                          >
                            <i className="fas fa-download docview-icon-sm"></i>
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDelete(document)
                            }}
                            className="docview-action-button docview-delete"
                            title="Delete"
                          >
                            <i className="fas fa-trash docview-icon-sm"></i>
                          </button>
                        </div>
                      </div>

                      {/* Document Info */}
                      <div className="docview-p-5">
                        <div className="docview-flex docview-items-start docview-justify-between docview-mb-3">
                          <h3 className="docview-font-semibold docview-text-gray-900 docview-text-base docview-mb-1 docview-line-clamp-2 docview-leading-tight group-hover:docview-text-blue-600 docview-transition-colors docview-duration-300" title={document.original_filename}>
                            {document.original_filename}
                          </h3>
                          <span className={`docview-badge ${getStatusBadgeClass(document.processing_status)}`}>
                            {document.processing_status}
                          </span>
                        </div>
                        
                        <div className="docview-flex docview-items-center docview-justify-between docview-text-sm">
                          <span className="docview-text-gray-500">{formatFileSize(document.file_size)}</span>
                          <span className="docview-text-gray-400">{formatDate(document.upload_date)}</span>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              /* List View */
              <div className="docview-bg-white docview-rounded-2xl docview-border docview-border-gray-100 docview-overflow-hidden docview-shadow-lg">
                <div className="docview-divide-y docview-divide-gray-100">
                  {filteredDocuments.map((document, index) => {
                    const fileIcon = getFileIcon(document.content_type)
                    return (
                      <div
                        key={document.id}
                        className="docview-list-item docview-cursor-pointer docview-group docview-transition-all docview-duration-300"
                        onClick={() => handleDocumentClick(document)}
                      >
                        <div className={`docview-w-14 docview-h-14 ${fileIcon.bgClass} docview-rounded-2xl docview-flex docview-items-center docview-justify-center docview-text-2xl docview-flex-shrink-0 docview-shadow-sm docview-list-icon`}>
                          {fileIcon.icon}
                        </div>
                        
                        <div className="docview-flex-1 docview-min-w-0">
                          <div className="docview-flex docview-items-center docview-gap-3 docview-mb-1">
                            <h3 className="docview-text-base docview-font-semibold docview-text-gray-900 docview-truncate group-hover:docview-text-blue-600 docview-transition-colors docview-duration-300">
                              {document.original_filename}
                            </h3>
                            <span className={`docview-badge ${getStatusBadgeClass(document.processing_status)}`}>
                              {document.processing_status}
                            </span>
                          </div>
                          <div className="docview-flex docview-items-center docview-gap-4 docview-text-sm docview-text-gray-500">
                            <span>{formatFileSize(document.file_size)}</span>
                            <span>•</span>
                            <span>{formatDate(document.upload_date)}</span>
                            {document.document_type && (
                              <>
                                <span>•</span>
                                <span className="docview-capitalize">{document.document_type}</span>
                              </>
                            )}
                          </div>
                        </div>

                        <div className="docview-flex docview-items-center docview-gap-3 docview-opacity-0 group-hover:docview-opacity-100 docview-transition-opacity docview-duration-300">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDownload(document)
                            }}
                            className="docview-p-3 docview-text-gray-400 hover:docview-text-blue-600 hover:docview-bg-blue-50 docview-rounded-xl docview-transition-all docview-duration-300"
                            title="Download"
                          >
                            <i className="fas fa-download docview-icon"></i>
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDelete(document)
                            }}
                            className="docview-p-3 docview-text-gray-400 hover:docview-text-red-600 hover:docview-bg-red-50 docview-rounded-xl docview-transition-all docview-duration-300"
                            title="Delete"
                          >
                            <i className="fas fa-trash docview-icon"></i>
                          </button>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Document Detail Modal */}
        {selectedDocument && (
          <div 
            className="docview-modal-overlay"
            onClick={() => setSelectedDocument(null)}
          >
            <div 
              className="docview-modal-content"
              onClick={e => e.stopPropagation()}
            >
              <div className="docview-p-8">
                <div className="docview-modal-header">
                  <h2 className="docview-text-2xl docview-font-bold docview-text-gray-900">Document Details</h2>
                  <button
                    onClick={() => setSelectedDocument(null)}
                    className="docview-modal-close"
                  >
                    <i className="fas fa-times docview-icon-lg"></i>
                  </button>
                </div>

                <div className="docview-space-y-8">
                  <div className="docview-flex docview-items-center docview-gap-6">
                    <div className={`docview-w-20 docview-h-20 ${getFileIcon(selectedDocument.content_type).bgClass} docview-rounded-2xl docview-flex docview-items-center docview-justify-center docview-text-4xl docview-shadow-lg docview-detail-icon`}>
                      {getFileIcon(selectedDocument.content_type).icon}
                    </div>
                    <div className="docview-flex-1">
                      <h3 className="docview-font-bold docview-text-xl docview-text-gray-900 docview-mb-2">{selectedDocument.original_filename}</h3>
                      <div className="docview-flex docview-items-center docview-gap-3">
                        <span className={`docview-badge ${getStatusBadgeClass(selectedDocument.processing_status)}`}>
                          {selectedDocument.processing_status}
                        </span>
                        <span className="docview-text-sm docview-text-gray-500">{formatFileSize(selectedDocument.file_size)}</span>
                      </div>
                    </div>
                  </div>

                  <div className="docview-detail-grid">
                    <div>
                      <span className="docview-detail-label">File Size</span>
                      <p className="docview-detail-value">{formatFileSize(selectedDocument.file_size)}</p>
                    </div>
                    <div>
                      <span className="docview-detail-label">Content Type</span>
                      <p className="docview-detail-value">{selectedDocument.content_type}</p>
                    </div>
                    <div>
                      <span className="docview-detail-label">Upload Date</span>
                      <p className="docview-detail-value">{formatDate(selectedDocument.upload_date)}</p>
                    </div>
                    <div>
                      <span className="docview-detail-label">Document ID</span>
                      <p className="docview-detail-value docview-detail-id">{selectedDocument.id}</p>
                    </div>
                    {selectedDocument.document_type && (
                      <div>
                        <span className="docview-detail-label">Document Type</span>
                        <p className="docview-detail-value">{selectedDocument.document_type}</p>
                      </div>
                    )}
                    <div>
                      <span className="docview-detail-label">Uploaded By</span>
                      <p className="docview-detail-value">User {selectedDocument.user_id.slice(0, 8)}...</p>
                    </div>
                  </div>

                  <div className="docview-modal-actions docview-flex docview-gap-4 docview-pt-2">
                    <button
                      onClick={() => handleDownload(selectedDocument)}
                      className="docview-flex-1 docview-cta-primary"
                    >
                      <i className="fas fa-download"></i>
                      Download Document
                    </button>
                    <button
                      onClick={() => handleDelete(selectedDocument)}
                      className="docview-flex-1 docview-cta-danger"
                    >
                      <i className="fas fa-trash"></i>
                      Delete Document
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  )
}