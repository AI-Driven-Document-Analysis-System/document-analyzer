import React, { useState, useEffect } from "react"
import { authService } from "../../services/authService"

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
  if (contentType.includes("pdf")) return "fas fa-file-pdf text-red-500"
  if (contentType.includes("image")) return "fas fa-image text-blue-500"
  if (contentType.includes("spreadsheet") || contentType.includes("excel")) return "fas fa-file-excel text-green-500"
  if (contentType.includes("word") || contentType.includes("document")) return "fas fa-file-word text-blue-600"
  if (contentType.includes("text")) return "fas fa-file-alt text-gray-500"
  return "fas fa-file text-gray-400"
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
      setDocuments(data)
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
  const filteredDocuments = documents
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
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                <i className="fas fa-file-alt text-blue-600"></i>
                My Documents
              </h1>
              <p className="mt-1 text-gray-600">
                View and manage your uploaded documents
              </p>
            </div>
            <div className="text-sm text-gray-500">
              {filteredDocuments.length} of {documents.length} documents
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <i className="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
                <input
                  type="text"
                  placeholder="Search documents..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Status Filter */}
            <div className="sm:w-48">
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Status</option>
                <option value="completed">Completed</option>
                <option value="processing">Processing</option>
                <option value="failed">Failed</option>
              </select>
            </div>

            {/* Sort */}
            <div className="sm:w-48">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
                <option value="name">Name A-Z</option>
                <option value="size">Size (Largest)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Documents Grid */}
        {filteredDocuments.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <i className="fas fa-folder-open text-6xl"></i>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No documents found</h3>
            <p className="text-gray-600">
              {searchQuery || filterStatus !== "all" 
                ? "Try adjusting your search or filters"
                : "Upload your first document to get started"
              }
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredDocuments.map((document) => (
              <div
                key={document.id}
                className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => handleDocumentClick(document)}
              >
                {/* Document Preview/Thumbnail */}
                <div className="aspect-[4/3] bg-gray-100 rounded-t-lg flex items-center justify-center border-b">
                  {document.thumbnail_url ? (
                    <img
                      src={document.thumbnail_url}
                      alt={document.original_filename}
                      className="w-full h-full object-cover rounded-t-lg"
                    />
                  ) : (
                    <i className={`${getFileIcon(document.content_type)} text-4xl`}></i>
                  )}
                </div>

                {/* Document Info */}
                <div className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className={getStatusBadge(document.processing_status)}>
                      {document.processing_status}
                    </span>
                    <div className="flex items-center gap-1">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDownload(document)
                        }}
                        className="text-gray-400 hover:text-blue-600 transition-colors"
                        title="Download"
                      >
                        <i className="fas fa-download"></i>
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDelete(document)
                        }}
                        className="text-gray-400 hover:text-red-600 transition-colors"
                        title="Delete"
                      >
                        <i className="fas fa-trash"></i>
                      </button>
                    </div>
                  </div>

                  <h3 className="font-medium text-gray-900 mb-2 line-clamp-2" title={document.original_filename}>
                    {document.original_filename}
                  </h3>

                  <div className="space-y-1 text-sm text-gray-600">
                    <div className="flex items-center justify-between">
                      <span>Size:</span>
                      <span>{formatFileSize(document.file_size)}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Uploaded:</span>
                      <span>{formatDate(document.upload_date)}</span>
                    </div>
                    {document.document_type && (
                      <div className="flex items-center justify-between">
                        <span>Type:</span>
                        <span className="capitalize">{document.document_type}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
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
                  <i className={`${getFileIcon(selectedDocument.content_type)} text-3xl`}></i>
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
