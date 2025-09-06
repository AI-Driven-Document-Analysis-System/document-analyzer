import React, { useState, useEffect } from "react"
import { authService } from "../../services/authService"
import { Search, Grid3X3, List, MoreHorizontal, Download, Trash2, X, Filter, RefreshCw } from "lucide-react"

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

const getFileIcon = (contentType: string) => {
  if (contentType.includes("pdf")) return { icon: "📄", color: "text-red-500", bg: "bg-red-50" }
  if (contentType.includes("image")) return { icon: "🖼️", color: "text-blue-500", bg: "bg-blue-50" }
  if (contentType.includes("spreadsheet") || contentType.includes("excel")) return { icon: "📊", color: "text-green-500", bg: "bg-green-50" }
  if (contentType.includes("word") || contentType.includes("document")) return { icon: "📝", color: "text-blue-600", bg: "bg-blue-50" }
  if (contentType.includes("text")) return { icon: "📄", color: "text-gray-500", bg: "bg-gray-50" }
  return { icon: "📁", color: "text-gray-400", bg: "bg-gray-50" }
}

const getStatusBadge = (status: string) => {
  const baseClasses = "px-2 py-1 text-xs rounded-full font-medium"
  switch (status) {
    case 'completed':
      return `${baseClasses} bg-green-100 text-green-800`
    case 'processing':
      return `${baseClasses} bg-yellow-100 text-yellow-800`
    case 'failed':
      return `${baseClasses} bg-red-100 text-red-800`
    default:
      return `${baseClasses} bg-gray-100 text-gray-800`
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
      console.log('API Response:', data) // Debug log
      
      // Ensure data is an array
      if (Array.isArray(data)) {
        setDocuments(data)
      } else if (data && Array.isArray(data.documents)) {
        // Handle case where documents are nested in a documents property
        setDocuments(data.documents)
      } else if (data && Array.isArray(data.data)) {
        // Handle case where documents are nested in a data property
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
    setSelectedDocument(document)
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading documents...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 mb-4">
            <i className="fas fa-exclamation-triangle text-4xl"></i>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Documents</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchDocuments}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header with Search */}
      <div className="bg-white border-b border-gray-100">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center gap-6">
            {/* Search Bar */}
            <div className="flex-1 max-w-lg">
              <div className="relative">
                <i className="fas fa-search absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 text-sm"></i>
                <input
                  type="text"
                  placeholder="Search here"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-50 text-sm"
                />
              </div>
            </div>

            {/* View Options */}
            <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-md transition-all ${
                  viewMode === 'grid' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'
                }`}
                title="Grid View"
              >
                <i className="fas fa-th text-sm"></i>
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-md transition-all ${
                  viewMode === 'list' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'
                }`}
                title="List View"
              >
                <i className="fas fa-list text-sm"></i>
              </button>
            </div>

            {/* Filters */}
            <div className="flex items-center gap-3">
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm bg-white"
              >
                <option value="all">All Status</option>
                <option value="completed">Completed</option>
                <option value="processing">Processing</option>
                <option value="failed">Failed</option>
              </select>
              
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm bg-white"
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
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Recent Files Section */}
        {recentFiles.length > 0 && (
          <div className="mb-10">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-semibold text-gray-800">Recent Files</h2>
              <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">More</button>
            </div>
            <div className="flex gap-4 overflow-x-auto pb-2">
              {recentFiles.map((document) => {
                const fileIcon = getFileIcon(document.content_type)
                return (
                  <div
                    key={`recent-${document.id}`}
                    className="flex-shrink-0 w-48 bg-white rounded-lg p-4 border border-gray-100 hover:shadow-md transition-all cursor-pointer group"
                    onClick={() => handleDocumentClick(document)}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 ${fileIcon.bg} rounded-lg flex items-center justify-center text-lg`}>
                        {fileIcon.icon}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {document.original_filename}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {formatDate(document.upload_date)}
                        </p>
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
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-lg font-semibold text-gray-800">Files</h2>
            <div className="text-sm text-gray-500">
              {filteredDocuments.length} files
            </div>
          </div>

          {/* Documents Grid/List */}
          {filteredDocuments.length === 0 ? (
            <div className="text-center py-16 bg-white rounded-xl border border-gray-100">
              <div className="text-gray-300 mb-4">
                <i className="fas fa-folder-open text-6xl"></i>
              </div>
              <h3 className="text-lg font-medium text-gray-700 mb-2">No documents found</h3>
              <p className="text-gray-500">
                {searchQuery || filterStatus !== "all" 
                  ? "Try adjusting your search or filters"
                  : "Upload your first document to get started"
                }
              </p>
            </div>
          ) : viewMode === 'grid' ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-4">
              {filteredDocuments.map((document) => {
                const fileIcon = getFileIcon(document.content_type)
                return (
                  <div
                    key={document.id}
                    className="bg-white rounded-xl border border-gray-100 hover:shadow-lg transition-all cursor-pointer group relative"
                    onClick={() => handleDocumentClick(document)}
                  >
                    {/* Document Preview/Icon */}
                    <div className={`aspect-[4/5] ${fileIcon.bg} rounded-t-xl flex flex-col items-center justify-center relative overflow-hidden`}>
                      {document.thumbnail_url ? (
                        <img
                          src={document.thumbnail_url}
                          alt={document.original_filename}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="flex flex-col items-center">
                          <div className="w-16 h-16 bg-white/80 rounded-xl flex items-center justify-center text-3xl mb-3 shadow-sm">
                            {fileIcon.icon}
                          </div>
                          <div className="text-xs text-gray-600 font-medium uppercase tracking-wide">
                            {document.content_type.split('/')[1] || 'FILE'}
                          </div>
                        </div>
                      )}
                      
                      {/* Status Badge */}
                      <div className="absolute top-3 right-3">
                        <span className={getStatusBadge(document.processing_status)}>
                          {document.processing_status}
                        </span>
                      </div>

                      {/* Action Buttons */}
                      <div className="absolute top-3 left-3 opacity-0 group-hover:opacity-100 transition-opacity">
                        <div className="flex gap-1">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDownload(document)
                            }}
                            className="bg-white/90 hover:bg-white text-gray-600 hover:text-blue-600 p-2 rounded-lg shadow-sm transition-colors"
                            title="Download"
                          >
                            <i className="fas fa-download text-xs"></i>
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDelete(document)
                            }}
                            className="bg-white/90 hover:bg-white text-gray-600 hover:text-red-600 p-2 rounded-lg shadow-sm transition-colors"
                            title="Delete"
                          >
                            <i className="fas fa-trash text-xs"></i>
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Document Info */}
                    <div className="p-4">
                      <h3 className="font-medium text-gray-900 text-sm mb-1 line-clamp-2 leading-tight" title={document.original_filename}>
                        {document.original_filename}
                      </h3>
                      <p className="text-xs text-gray-500">{formatFileSize(document.file_size)}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            /* List View */
            <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
              <div className="divide-y divide-gray-100">
                {filteredDocuments.map((document) => {
                  const fileIcon = getFileIcon(document.content_type)
                  return (
                    <div
                      key={document.id}
                      className="flex items-center gap-4 p-4 hover:bg-gray-50 cursor-pointer group"
                      onClick={() => handleDocumentClick(document)}
                    >
                      <div className={`w-10 h-10 ${fileIcon.bg} rounded-lg flex items-center justify-center text-lg flex-shrink-0`}>
                        {fileIcon.icon}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {document.original_filename}
                        </p>
                        <p className="text-xs text-gray-500">
                          {formatFileSize(document.file_size)} • {formatDate(document.upload_date)}
                        </p>
                      </div>

                      <div className="flex items-center gap-3">
                        <span className={getStatusBadge(document.processing_status)}>
                          {document.processing_status}
                        </span>
                        
                        <div className="opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDownload(document)
                            }}
                            className="text-gray-400 hover:text-blue-600 p-2 transition-colors"
                            title="Download"
                          >
                            <i className="fas fa-download text-sm"></i>
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDelete(document)
                            }}
                            className="text-gray-400 hover:text-red-600 p-2 transition-colors"
                            title="Delete"
                          >
                            <i className="fas fa-trash text-sm"></i>
                          </button>
                        </div>
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
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">Document Details</h2>
                <button
                  onClick={() => setSelectedDocument(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <i className="fas fa-times text-xl"></i>
                </button>
              </div>

              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <div className={`w-16 h-16 ${getFileIcon(selectedDocument.content_type).bg} rounded-xl flex items-center justify-center text-3xl`}>
                    {getFileIcon(selectedDocument.content_type).icon}
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">{selectedDocument.original_filename}</h3>
                    <span className={getStatusBadge(selectedDocument.processing_status)}>
                      {selectedDocument.processing_status}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">File Size:</span>
                    <p className="text-gray-600">{formatFileSize(selectedDocument.file_size)}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Content Type:</span>
                    <p className="text-gray-600">{selectedDocument.content_type}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Upload Date:</span>
                    <p className="text-gray-600">{formatDate(selectedDocument.upload_date)}</p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Document ID:</span>
                    <p className="text-gray-600 font-mono text-xs">{selectedDocument.id}</p>
                  </div>
                  {selectedDocument.document_type && (
                    <div>
                      <span className="font-medium text-gray-700">Document Type:</span>
                      <p className="text-gray-600 capitalize">{selectedDocument.document_type}</p>
                    </div>
                  )}
                </div>

                <div className="flex gap-3 pt-4 border-t">
                  <button
                    onClick={() => handleDownload(selectedDocument)}
                    className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
                  >
                    <i className="fas fa-download"></i>
                    Download
                  </button>
                  <button
                    onClick={() => handleDelete(selectedDocument)}
                    className="flex-1 bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors flex items-center justify-center gap-2"
                  >
                    <i className="fas fa-trash"></i>
                    Delete
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
