"use client"

import { useState, useEffect } from "react"
import { apiService } from "../../services/api"
import { checkAuthStatus } from "../../services/authHelper"

interface SearchResult {
  id: string
  title: string
  type: string
  excerpt: string
  uploadDate: string
  confidence: number
  pages: number
  file_size: number
  content_type: string
  processing_status: string
  file_path: string
}

interface SearchFilters {
  document_type: string
  date_range: string
  limit: number
  offset: number
}

interface PaginationInfo {
  total: number
  limit: number
  offset: number
  has_more: boolean
}

// Modal styles
const modalStyles = {
  overlay: {
    position: 'fixed' as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.75)',
    backdropFilter: 'blur(8px)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 9999,
    padding: '20px',
  },
  content: {
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
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '20px 24px',
    borderBottom: '1px solid #e5e7eb',
    background: 'linear-gradient(135deg, #f8fafc, #e2e8f0)',
    flexShrink: 0,
  },
  title: {
    flex: 1,
  },
  titleH3: {
    fontSize: '1.25rem',
    fontWeight: 600,
    color: '#1a202c',
    margin: '0 0 4px 0',
  },
  titleP: {
    fontSize: '0.875rem',
    color: '#718096',
    margin: 0,
  },
  close: {
    background: 'none',
    border: 'none',
    fontSize: '24px',
    color: '#718096',
    cursor: 'pointer',
    padding: '8px',
    borderRadius: '8px',
    transition: 'all 0.2s ease',
    lineHeight: 1,
    marginLeft: '16px',
  },
  body: {
    flex: 1,
    padding: 0,
    overflow: 'hidden',
    position: 'relative' as const,
    background: '#f7fafc',
  },
  viewer: {
    width: '100%',
    height: '100%',
    position: 'relative' as const,
  },
  iframe: {
    width: '100%',
    height: '100%',
    border: 'none',
    background: 'white',
  },
  imageViewer: {
    width: '100%',
    height: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '20px',
    overflow: 'auto',
  },
  image: {
    maxWidth: '100%',
    maxHeight: '100%',
    objectFit: 'contain' as const,
    borderRadius: '8px',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)',
  },
  loading: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    color: '#718096',
  },
  spinner: {
    width: '48px',
    height: '48px',
    border: '4px solid #e2e8f0',
    borderTop: '4px solid #667eea',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    marginBottom: '16px',
  },
  error: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    textAlign: 'center' as const,
    color: '#718096',
    padding: '40px',
  },
  errorIcon: {
    fontSize: '4rem',
    marginBottom: '16px',
    color: '#e53e3e',
  },
  errorH4: {
    fontSize: '1.25rem',
    color: '#2d3748',
    marginBottom: '8px',
  },
  errorP: {
    color: '#718096',
    marginBottom: '24px',
  },
}

export function SearchInterface() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedType, setSelectedType] = useState("All Types")
  const [dateRange, setDateRange] = useState("all")
  const [showFilters, setShowFilters] = useState(false)
  const [isSearching, setIsSearching] = useState(false)
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [documentTypes, setDocumentTypes] = useState<string[]>(["All Types"])
  const [totalResults, setTotalResults] = useState(0)
  const [searchTime, setSearchTime] = useState(0)
  const [showPreview, setShowPreview] = useState(false)
  const [previewDocument, setPreviewDocument] = useState<SearchResult | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [loadingPreview, setLoadingPreview] = useState(false)
  const [loadingTypes, setLoadingTypes] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [pagination, setPagination] = useState<PaginationInfo>({
    total: 0,
    limit: 50,
    offset: 0,
    has_more: false
  })

  // Load document types on component mount
  useEffect(() => {
    loadDocumentTypes()
  }, [])

  const loadDocumentTypes = async () => {
    setLoadingTypes(true)
    setError(null)
    
    // Check authentication status first
    const authStatus = checkAuthStatus()
    if (!authStatus.isAuthenticated) {
      setError("Please log in to access document types")
      setDocumentTypes(["All Types"])
      setLoadingTypes(false)
      return
    }
    
    try {
      const response = await apiService.getDocumentTypes()
      setDocumentTypes(response.document_types || ["All Types"])
    } catch (error) {
      console.error("Error loading document types:", error)
      // Check if it's an authentication error
      if (error.message && error.message.includes("Not authenticated")) {
        setError("Please log in to access document types")
        // Set default types for now
        setDocumentTypes(["All Types"])
      } else {
        setError("Failed to load document types. Please refresh the page.")
        // Set default types as fallback
        setDocumentTypes(["All Types"])
      }
    } finally {
      setLoadingTypes(false)
    }
  }

  const handleSearch = async (newOffset: number = 0) => {
    if (!searchQuery.trim() && selectedType === "All Types" && dateRange === "all") {
      setError("Please enter a search query or select filters")
      return
    }

    // Check authentication status
    const authStatus = checkAuthStatus()
    if (!authStatus.isAuthenticated) {
      setError("Please log in to search documents")
      return
    }

    setIsSearching(true)
    setError(null)
    const startTime = Date.now()
    
    try {
      const filters: SearchFilters = {
        document_type: selectedType,
        date_range: dateRange,
        limit: pagination.limit,
        offset: newOffset
      }
      
      const response = await apiService.searchDocuments(searchQuery, filters)
      setSearchResults(response.documents || [])
      setTotalResults(response.total_results || 0)
      setSearchTime((Date.now() - startTime) / 1000)
      
      if (response.pagination) {
        setPagination(response.pagination)
      }
    } catch (error) {
      console.error("Error searching documents:", error)
      if (error.message && error.message.includes("Not authenticated")) {
        setError("Please log in to search documents")
      } else {
        setError("Failed to search documents. Please try again.")
      }
      setSearchResults([])
      setTotalResults(0)
    } finally {
      setIsSearching(false)
    }
  }

  const handleNextPage = () => {
    if (pagination.has_more) {
      handleSearch(pagination.offset + pagination.limit)
    }
  }

  const handlePrevPage = () => {
    if (pagination.offset > 0) {
      handleSearch(Math.max(0, pagination.offset - pagination.limit))
    }
  }

  // Document preview handler
  const previewDocumentHandler = async (doc: SearchResult) => {
    setLoadingPreview(true)
    setPreviewDocument(doc)
    setShowPreview(true)
    setError(null)

    try {
      const response = await apiService.downloadDocument(doc.id)
      setPreviewUrl(response.download_url)
    } catch (err) {
      console.error("Error getting preview URL:", err)
      setError("Failed to load document preview. Please try again.")
    } finally {
      setLoadingPreview(false)
    }
  }

  // Download document handler
  const downloadDocumentHandler = async (doc: SearchResult) => {
    try {
      const response = await apiService.downloadDocument(doc.id)
      const link = document.createElement('a')
      link.href = response.download_url
      link.download = doc.title
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (err) {
      console.error("Error downloading document:", err)
      setError("Failed to download document. Please try again.")
    }
  }

  // Close preview
  const closePreview = () => {
    setShowPreview(false)
    setPreviewDocument(null)
    setPreviewUrl(null)
    setError(null)
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getFileIcon = (contentType: string) => {
    if (contentType?.includes('pdf')) return 'fas fa-file-pdf text-red-500'
    if (contentType?.includes('image')) return 'fas fa-file-image text-green-500'
    if (contentType?.includes('word') || contentType?.includes('document')) return 'fas fa-file-word text-blue-500'
    if (contentType?.includes('excel') || contentType?.includes('spreadsheet')) return 'fas fa-file-excel text-green-600'
    if (contentType?.includes('powerpoint') || contentType?.includes('presentation')) return 'fas fa-file-powerpoint text-orange-500'
    return 'fas fa-file text-gray-500'
  }

  return (
    <div className="p-6 space-y-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Document Search</h1>
        <p className="text-gray-600">Search through your documents using AI-powered semantic search</p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <div className="flex items-center">
            <i className="fas fa-exclamation-triangle text-red-500 mr-3"></i>
            <span className="text-red-700">{error}</span>
            <button 
              onClick={() => setError(null)}
              className="ml-auto text-red-500 hover:text-red-700"
            >
              <i className="fas fa-times"></i>
            </button>
          </div>
        </div>
      )}

      {/* Search Bar */}
      <div className="card">
        <div className="card-content">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <input
                type="text"
                placeholder="Search documents, content, or ask questions..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="form-input text-lg"
                style={{ paddingLeft: "2.5rem", height: "48px" }}
                onKeyPress={(e) => e.key === "Enter" && handleSearch()}
              />
              <i className="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-blue-500"></i>
            </div>
            <button
              onClick={() => handleSearch()}
              disabled={isSearching}
              className="btn btn-primary"
              style={{ height: "48px", padding: "0 2rem" }}
            >
              {isSearching ? (
                <>
                  <i className="fas fa-spinner fa-spin mr-2"></i>
                  Searching...
                </>
              ) : (
                "Search"
              )}
            </button>
            <button
              className="btn btn-outline"
              onClick={() => setShowFilters(!showFilters)}
              style={{ height: "48px", padding: "0 1rem" }}
            >
              <i className="fas fa-filter text-gray-600"></i>
            </button>
          </div>
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Search Filters</h2>
          </div>
          <div className="card-content">
            <div className="grid grid-cols-3 gap-4">
                              <div>
                  <label className="form-label">Document Type</label>
                  <select 
                    className="form-select" 
                    value={selectedType} 
                    onChange={(e) => setSelectedType(e.target.value)}
                    disabled={loadingTypes}
                  >
                    {loadingTypes ? (
                      <option>Loading types...</option>
                    ) : (
                      documentTypes.map((type) => (
                        <option key={type} value={type}>
                          {type}
                        </option>
                      ))
                    )}
                  </select>
                </div>

              <div>
                <label className="form-label">Date Range</label>
                <select className="form-select" value={dateRange} onChange={(e) => setDateRange(e.target.value)}>
                  <option value="all">All Time</option>
                  <option value="today">Today</option>
                  <option value="week">This Week</option>
                  <option value="month">This Month</option>
                  <option value="year">This Year</option>
                </select>
              </div>

                              <div>
                  <label className="form-label">Search Options</label>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <input type="checkbox" id="semantic" defaultChecked />
                    <label htmlFor="semantic" className="text-sm">
                      Semantic Search
                    </label>
                  </div>
                  <div className="flex items-center gap-2">
                    <input type="checkbox" id="exact" />
                    <label htmlFor="exact" className="text-sm">
                      Exact Match
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Search Stats */}
              {searchResults.length > 0 && (
          <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
            <span className="font-medium">
              Found {totalResults.toLocaleString()} documents in {searchTime.toFixed(2)} seconds
            </span>
          <div className="flex items-center gap-4">
            <span>Sort by:</span>
            <select className="form-select" style={{ width: "128px" }}>
              <option value="relevance">Relevance</option>
              <option value="date">Date</option>
              <option value="name">Name</option>
              <option value="type">Type</option>
            </select>
          </div>
        </div>
      )}

      {/* Search Results */}
      <div className="space-y-4">
        {searchResults.map((result) => (
          <div key={result.id} className="card hover:shadow-lg transition-shadow duration-200">
            <div className="card-content">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <i className={`${getFileIcon(result.content_type)} text-xl`}></i>
                    <h3 className="text-lg font-semibold text-gray-900 hover:text-blue-600 cursor-pointer">
                      {result.title}
                    </h3>
                    <span className="badge badge-secondary">{result.type}</span>
                    {result.confidence > 80 && (
                      <span className="badge badge-success text-xs">
                        <i className="fas fa-star text-yellow-400 mr-1"></i>High Match
                      </span>
                    )}
                  </div>

                  <p className="text-gray-600 mb-3">{result.excerpt}</p>

                  <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                    <div className="flex items-center gap-1">
                      <i className="fas fa-calendar text-blue-500"></i> 
                      {new Date(result.uploadDate).toLocaleDateString()}
                    </div>
                    <div className="flex items-center gap-1">
                      <i className="fas fa-file-alt text-gray-500"></i> 
                      {result.pages} pages
                    </div>
                    <div className="flex items-center gap-1">
                      <i className="fas fa-weight text-green-500"></i> 
                      {formatFileSize(result.file_size)}
                    </div>
                    <div className="flex items-center gap-1">
                      <i className="fas fa-star text-yellow-500"></i> 
                      {result.confidence.toFixed(1)}% match
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="badge badge-primary text-xs">
                      <i className="fas fa-tag text-blue-400 mr-1"></i>{result.type}
                    </span>
                    <span className={`badge text-xs ${
                      result.processing_status === 'completed' ? 'badge-success' : 
                      result.processing_status === 'processing' ? 'badge-warning' : 'badge-outline'
                    }`}>
                      <i className="fas fa-info-circle text-gray-400 mr-1"></i>{result.processing_status}
                    </span>
                  </div>
                </div>

                                  <div className="flex flex-col gap-2 ml-4">
                    <button 
                      className="btn btn-sm btn-outline hover:bg-blue-50"
                      onClick={() => previewDocumentHandler(result)}
                      title="Preview document"
                    >
                      <i className="fas fa-eye text-blue-500 mr-1"></i>View
                    </button>
                    <button 
                      className="btn btn-sm btn-outline hover:bg-green-50"
                      onClick={() => downloadDocumentHandler(result)}
                      title="Download document"
                    >
                      <i className="fas fa-download text-green-500 mr-1"></i>Download
                    </button>
                  </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {searchResults.length > 0 && (
        <div className="flex items-center justify-between mt-6">
          <div className="text-sm text-gray-500">
            Showing {pagination.offset + 1} to {Math.min(pagination.offset + pagination.limit, pagination.total)} of {pagination.total.toLocaleString()} results
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handlePrevPage}
              disabled={pagination.offset === 0}
              className="btn btn-outline btn-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <i className="fas fa-chevron-left mr-1"></i>Previous
            </button>
            <button
              onClick={handleNextPage}
              disabled={!pagination.has_more}
              className="btn btn-outline btn-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next<i className="fas fa-chevron-right ml-1"></i>
            </button>
          </div>
        </div>
      )}

      {/* No Results */}
              {!isSearching && searchResults.length === 0 && searchQuery && (
          <div className="text-center py-12">
            <i className="fas fa-search text-gray-400 text-4xl mb-4"></i>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No documents found</h3>
            <p className="text-gray-600 mb-4">Try adjusting your search terms or filters</p>
            <div className="flex justify-center gap-2">
              <button 
                onClick={() => setSearchQuery("")}
                className="btn btn-outline btn-sm"
              >
                Clear Search
              </button>
              <button 
                onClick={() => setShowFilters(true)}
                className="btn btn-primary btn-sm"
              >
                Adjust Filters
              </button>
            </div>
          </div>
        )}

      {/* Document Preview Modal */}
      {showPreview && (
        <div style={modalStyles.overlay} onClick={closePreview}>
          <div style={modalStyles.content} onClick={(e) => e.stopPropagation()}>
            <div style={modalStyles.header}>
              <div style={modalStyles.title}>
                <h3 style={modalStyles.titleH3}>{previewDocument?.title}</h3>
                <p style={modalStyles.titleP}>Document Preview</p>
              </div>
              <button style={modalStyles.close} onClick={closePreview}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            
            <div style={modalStyles.body}>
              {loadingPreview ? (
                <div style={modalStyles.loading}>
                  <div style={modalStyles.spinner}></div>
                  <p>Loading document preview...</p>
                </div>
              ) : previewUrl ? (
                <div style={modalStyles.viewer}>
                  {previewDocument?.content_type?.includes('pdf') ? (
                    <iframe src={previewUrl} title="Document Preview" style={modalStyles.iframe}></iframe>
                  ) : previewDocument?.content_type?.includes('image') ? (
                    <div style={modalStyles.imageViewer}>
                      <img src={previewUrl} alt="Document Preview" style={modalStyles.image} />
                    </div>
                  ) : (
                                          <div style={modalStyles.error}>
                        <div style={modalStyles.errorIcon}>
                          <i className="fas fa-file-alt"></i>
                        </div>
                        <h4 style={modalStyles.errorH4}>Preview Not Available</h4>
                        <p style={modalStyles.errorP}>This file type cannot be previewed. Please download the file to view it.</p>
                        <button 
                          onClick={() => previewDocument && downloadDocumentHandler(previewDocument)}
                          className="btn btn-primary"
                        >
                          <i className="fas fa-download mr-2"></i>Download Instead
                        </button>
                      </div>
                  )}
                </div>
              ) : (
                <div style={modalStyles.error}>
                  <div style={modalStyles.errorIcon}>
                    <i className="fas fa-exclamation-triangle"></i>
                  </div>
                  <h4 style={modalStyles.errorH4}>Preview Error</h4>
                  <p style={modalStyles.errorP}>Failed to load document preview. Please try again.</p>
                  <button 
                    onClick={closePreview}
                    className="btn btn-outline"
                  >
                    Close
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Add CSS for spinner animation */}
      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}
