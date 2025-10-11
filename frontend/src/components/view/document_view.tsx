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
  download_url?: string
}

interface DocumentViewProps {
  authToken?: string
  onAuthError?: () => void
}

// Helper functions with PNG icons
const getFileIcon = (contentType: string) => {
  if (contentType.includes("pdf")) return { 
    icon: <img src="/icons/pdf-icon.png" alt="PDF" style={{ width: '2rem', height: '2rem' }} />,
    colorClass: "text-red-600", bgClass: "bg-red-50", accentClass: "bg-red-500" 
  }
  if (contentType.includes("image")) return { 
    icon: <img src="/icons/image-icon.png" alt="Image" style={{ width: '2rem', height: '2rem' }} />,
    colorClass: "text-blue-600", bgClass: "bg-blue-50", accentClass: "bg--500" 
  }
  if (contentType.includes("spreadsheet") || contentType.includes("excel")) return { 
    icon: <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H9v-2h5v2zm0-4H9v-2h5v2zm0-4H9V7h5v2zm5 8h-3V7h3v10z"/></svg>,
    colorClass: "text-green-600", bgClass: "bg-green-50", accentClass: "bg-green-500" 
  }
  if (contentType.includes("word") || contentType.includes("document") || contentType.includes("docx")) return { 
    icon: <img src="/icons/docx-icon.png" alt="DOCX" style={{ width: '2rem', height: '2rem' }} />,
    colorClass: "text-indigo-600", bgClass: "bg-indigo-50", accentClass: "bg-indigo-500" 
  }
  if (contentType.includes("text") || contentType.includes("txt")) return { 
    icon: <img src="/icons/txt-icon.png" alt="TXT" style={{ width: '2rem', height: '2rem' }} />,
    colorClass: "text-gray-600", bgClass: "bg-gray-50", accentClass: "bg-gray-500" 
  }
  return { 
    icon: <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24"><path d="M10 4H4c-1.11 0-2 .89-2 2v12c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2h-8l-2-2z"/></svg>,
    colorClass: "text-gray-500", bgClass: "bg-gray-50", accentClass: "bg-gray-400" 
  }
}
const getDocumentTypeBadgeStyle = (docType: string | undefined): React.CSSProperties => {
  const baseStyle = {
    padding: '0.25rem 0.75rem',
    fontSize: '0.75rem',
    borderRadius: '9999px',
    fontWeight: '500',
    display: 'inline-flex',
    alignItems: 'center',
    gap: '0.25rem',
    borderWidth: '1px',
    borderStyle: 'solid'
  }

  if (!docType) {
    return {
      ...baseStyle,
      backgroundColor: '#f8fafc',
      color: '#64748b',
      borderColor: '#e2e8f0'
    }
  }

  const normalized = docType.toLowerCase().trim()
  const typeColors: Record<string, { bg: string; text: string; border: string }> = {
    'medical record': { bg: '#f0fdf4', text: '#166534', border: '#bbf7d0' },
    'invoice and receipt': { bg: '#fffbeb', text: '#78350f', border: '#fcd34d' },
    'legal document': { bg: '#ede9fe', text: '#5b21b6', border: '#c4b5fd' },
    'research paper': { bg: '#dbeafe', text: '#1e40af', border: '#93c5fd' },
    'financial report': { bg: '#f0f9ff', text: '#0891b2', border: '#a5f3fc' },
  }

  const colors = typeColors[normalized] || {
    bg: '#f1f5f9',
    text: '#475569',
    border: '#cbd5e1'
  }

  return {
    ...baseStyle,
    backgroundColor: colors.bg,
    color: colors.text,
    borderColor: colors.border
  }
}

const getStatusBadgeStyle = (status: string) => {
  const baseStyle = {
    padding: '0.25rem 0.75rem',
    fontSize: '0.75rem',
    borderRadius: '9999px',
    fontWeight: '500',
    display: 'inline-flex',
    alignItems: 'center',
    gap: '0.25rem',
    borderWidth: '1px',
    borderStyle: 'solid'
  }
  switch (status) {
    case 'completed': 
      return {
        ...baseStyle,
        backgroundColor: '#dbeafe',
        color: '#1e40af',
        borderColor: '#93c5fd'
      }
    case 'processing': 
      return {
        ...baseStyle,
        backgroundColor: '#e0f2fe',
        color: '#0369a1',
        borderColor: '#7dd3fc'
      }
    case 'failed': 
      return {
        ...baseStyle,
        backgroundColor: '#fee2e2',
        color: '#b91c1c',
        borderColor: '#fecaca'
      }
    default: 
      return {
        ...baseStyle,
        backgroundColor: '#f8fafc',
        color: '#64748b',
        borderColor: '#e2e8f0'
      }
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

export function DocumentView({ authToken: propAuthToken, onAuthError }: DocumentViewProps) {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [filterStatus, setFilterStatus] = useState<string>("all")
  const [sortBy, setSortBy] = useState<string>("newest")
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null)
  const [authToken, setAuthToken] = useState<string | null>(null)

  React.useEffect(() => {
    const token = propAuthToken || authService.getToken()
    setAuthToken(token)
  }, [propAuthToken])

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

  const recentFiles = (Array.isArray(documents) ? documents : [])
    .sort((a, b) => new Date(b.upload_date).getTime() - new Date(a.upload_date).getTime())
    .slice(0, 3)

  const handleDocumentClick = async (document: Document) => {
    const downloadResponse = await fetch(
          `http://localhost:8000/api/documents/${document.id}/download`,
          {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${authToken}`,
              'Content-Type': 'application/json',
            },
          }
        );

        if (!downloadResponse.ok) {
          throw new Error(`Failed to fetch download URL: ${downloadResponse.status}`);
        }

        const downloadData = await downloadResponse.json();
        document.download_url = downloadData.download_url;

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
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #f8fafc 0%, #e0f2fe 50%, #e8eaf6 100%)',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
      }}>
        {/* Modern Header with Glass Effect */}
        <div style={{
          position: 'sticky',
          top: 0,
          zIndex: 40,
          background: 'rgba(255, 255, 255, 0.85)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{
            maxWidth: '80rem',
            margin: '0 auto',
            padding: '1rem 1.5rem'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '1.5rem'
            }}>
              {/* Left Side - Search Bar */}
              <div style={{
                flex: '1 1 0%',
                maxWidth: '32rem'
              }}>
                <div style={{ position: 'relative' }}>
                  <div style={{
                    position: 'absolute',
                    top: '50%',
                    left: '1rem',
                    transform: 'translateY(-50%)',
                    pointerEvents: 'none'
                  }}>
                    <svg style={{
                      width: '1.25rem',
                      height: '1.25rem',
                      color: '#9ca3af'
                    }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                  <input
                    type="text"
                    placeholder="Search documents by name..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    style={{
                      width: '100%',
                      paddingLeft: '3rem',
                      paddingRight: '3rem',
                      paddingTop: '0.875rem',
                      paddingBottom: '0.875rem',
                      background: 'rgba(255, 255, 255, 0.7)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid rgba(229, 231, 235, 0.6)',
                      borderRadius: '1rem',
                      color: '#111827',
                      fontSize: '0.875rem',
                      transition: 'all 0.3s ease',
                      boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)'
                    }}
                    onFocus={(e) => {
                      e.target.style.outline = 'none'
                      e.target.style.boxShadow = '0 0 0 4px rgba(59, 130, 246, 0.1)'
                      e.target.style.borderColor = '#3b82f6'
                    }}
                    onBlur={(e) => {
                      e.target.style.boxShadow = '0 1px 2px rgba(0, 0, 0, 0.05)'
                      e.target.style.borderColor = 'rgba(229, 231, 235, 0.6)'
                    }}
                  />
                  {searchQuery && (
                    <button
                      onClick={() => setSearchQuery("")}
                      style={{
                        position: 'absolute',
                        top: '50%',
                        right: '1rem',
                        transform: 'translateY(-50%)',
                        color: '#9ca3af',
                        cursor: 'pointer',
                        transition: 'color 0.2s ease'
                      }}
                      onMouseEnter={(e) => (e.target as HTMLButtonElement).style.color = '#6b7280'}
                      onMouseLeave={(e) => (e.target as HTMLButtonElement).style.color = '#9ca3af'}
                    >
                      <svg style={{
                        width: '1.25rem',
                        height: '1.25rem'
                      }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  )}
                </div>
              </div>
              {/* Right Side - Modern Controls */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '1rem'
              }}>
                {/* View Toggle with Modern Design */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  background: 'rgba(255, 255, 255, 0.7)',
                  backdropFilter: 'blur(10px)',
                  borderRadius: '0.75rem',
                  padding: '0.25rem',
                  border: '1px solid rgba(229, 231, 235, 0.6)',
                  boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)'
                }}>
                  <button
                    onClick={() => setViewMode('grid')}
                    style={{
                      padding: '0.625rem',
                      borderRadius: '0.5rem',
                      transition: 'all 0.3s ease',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      background: viewMode === 'grid' ? '#3b82f6' : 'transparent',
                      color: viewMode === 'grid' ? 'white' : '#6b7280',
                      boxShadow: viewMode === 'grid' ? '0 4px 14px rgba(59, 130, 246, 0.25)' : 'none',
                      transform: viewMode === 'grid' ? 'scale(1.05)' : 'scale(1)',
                      cursor: 'pointer',
                      border: 'none'
                    }}
                    title="Grid View"
                    onMouseEnter={(e) => (e.target as HTMLButtonElement).style.color = '#3b82f6'}
                    onMouseLeave={(e) => (e.target as HTMLButtonElement).style.color = '#6b7280'}
                  >
                    <svg style={{
                      width: '1.25rem',
                      height: '1.25rem'
                    }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => setViewMode('list')}
                    style={{
                      padding: '0.625rem',
                      borderRadius: '0.5rem',
                      transition: 'all 0.3s ease',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      background: viewMode === 'list' ? '#3b82f6' : 'transparent',
                      color: viewMode === 'list' ? 'white' : '#6b7280',
                      boxShadow: viewMode === 'list' ? '0 4px 14px rgba(59, 130, 246, 0.25)' : 'none',
                      transform: viewMode === 'list' ? 'scale(1.05)' : 'scale(1)',
                      cursor: 'pointer',
                      border: 'none'
                    }}
                    title="List View"
                    onMouseEnter={(e) => (e.target as HTMLButtonElement).style.color = '#3b82f6'}
                    onMouseLeave={(e) => (e.target as HTMLButtonElement).style.color = '#6b7280'}
                  >
                    <svg style={{
                      width: '1.25rem',
                      height: '1.25rem'
                    }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                    </svg>
                  </button>
                </div>
                {/* Modern Filter Dropdowns */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem'
                }}>
                  <select
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value)}
                    style={{
                      padding: '0.625rem 1rem',
                      background: 'rgba(255, 255, 255, 0.7)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid rgba(229, 231, 235, 0.6)',
                      borderRadius: '0.75rem',
                      fontSize: '0.875rem',
                      fontWeight: '500',
                      color: '#374151',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
                      appearance: 'none',
                      backgroundImage: 'url("data:image/svg+xml,%3csvg xmlns=\'http://www.w3.org/2000/svg\' fill=\'none\' viewBox=\'0 0 20 20\'%3e%3cpath stroke=\'%236b7280\' stroke-linecap=\'round\' stroke-linejoin=\'round\' stroke-width=\'1.5\' d=\'M6 8l4 4 4-4\'/%3e%3c/svg%3e")',
                      backgroundRepeat: 'no-repeat',
                      backgroundPosition: 'right 0.75rem center',
                      backgroundSize: '1em 1em',
                      paddingRight: '2.5rem'
                    }}
                    onFocus={(e) => {
                      e.target.style.outline = 'none'
                      e.target.style.boxShadow = '0 0 0 4px rgba(59, 130, 246, 0.1)'
                      e.target.style.borderColor = '#3b82f6'
                    }}
                    onBlur={(e) => {
                      e.target.style.boxShadow = '0 1px 2px rgba(0, 0, 0, 0.05)'
                      e.target.style.borderColor = 'rgba(229, 231, 235, 0.6)'
                    }}
                  >
                    <option value="all">All Status</option>
                    <option value="completed">Completed</option>
                    <option value="processing">Processing</option>
                    <option value="failed">Failed</option>
                  </select>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    style={{
                      padding: '0.625rem 1rem',
                      background: 'rgba(255, 255, 255, 0.7)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid rgba(229, 231, 235, 0.6)',
                      borderRadius: '0.75rem',
                      fontSize: '0.875rem',
                      fontWeight: '500',
                      color: '#374151',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
                      appearance: 'none',
                      backgroundImage: 'url("data:image/svg+xml,%3csvg xmlns=\'http://www.w3.org/2000/svg\' fill=\'none\' viewBox=\'0 0 20 20\'%3e%3cpath stroke=\'%236b7280\' stroke-linecap=\'round\' stroke-linejoin=\'round\' stroke-width=\'1.5\' d=\'M6 8l4 4 4-4\'/%3e%3c/svg%3e")',
                      backgroundRepeat: 'no-repeat',
                      backgroundPosition: 'right 0.75rem center',
                      backgroundSize: '1em 1em',
                      paddingRight: '2.5rem'
                    }}
                    onFocus={(e) => {
                      e.target.style.outline = 'none'
                      e.target.style.boxShadow = '0 0 0 4px rgba(59, 130, 246, 0.1)'
                      e.target.style.borderColor = '#3b82f6'
                    }}
                    onBlur={(e) => {
                      e.target.style.boxShadow = '0 1px 2px rgba(0, 0, 0, 0.05)'
                      e.target.style.borderColor = 'rgba(229, 231, 235, 0.6)'
                    }}
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
        </div>

        {/* Main Content with Better Spacing */}
        <div style={{
          maxWidth: '80rem',
          margin: '0 auto',
          padding: '2rem 1.5rem'
        }}>
          {/* Enhanced Recent Files Section */}
          {recentFiles.length > 0 && (
            <div style={{ marginBottom: '3rem' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '2rem'
              }}>
                <div>
                  <h2 style={{
                    fontSize: '1.875rem',
                    fontWeight: '700',
                    color: '#111827',
                    marginBottom: '0.5rem'
                  }}>Recent Files</h2>
                  <p style={{
                    color: '#6b7280',
                    fontSize: '1rem'
                  }}>Your most recently uploaded documents</p>
                </div>
                <button style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.5rem 1rem',
                  color: '#2563eb',
                  fontWeight: '500',
                  transition: 'all 0.3s ease',
                  borderRadius: '0.75rem',
                  cursor: 'pointer',
                  border: 'none',
                  background: 'transparent'
                }}
                onMouseEnter={(e) => {
                  const target = e.target as HTMLSelectElement
                  target.style.color = '#1d4ed8'
                  target.style.background = 'rgba(59, 130, 246, 0.1)'
                }}
                onMouseLeave={(e) => {
                  const target = e.target as HTMLSelectElement
                  target.style.color = '#2563eb'
                  target.style.background = 'transparent'
                }}>
                  View All
                  <svg style={{
                    width: '1rem',
                    height: '1rem',
                    transition: 'transform 0.3s ease'
                  }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
              <div style={{
                display: 'flex',
                gap: '1.5rem',
                overflowX: 'auto',
                paddingBottom: '1rem',
                scrollbarWidth: 'none',
                msOverflowStyle: 'none'
              }}>
                {recentFiles.map((document) => {
                  const fileIcon = getFileIcon(document.content_type)
                  return (
                    <div
                      key={`recent-${document.id}`}
                      style={{
                        cursor: 'pointer',
                        position: 'relative',
                        overflow: 'hidden',
                        flexShrink: 0,
                        width: '20rem',
                        background: 'rgba(255, 255, 255, 0.8)',
                        backdropFilter: 'blur(20px)',
                        borderRadius: '1rem',
                        padding: '1.5rem',
                        border: '1px solid rgba(255, 255, 255, 0.5)',
                        boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
                        transition: 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)'
                      }}
                      onClick={() => handleDocumentClick(document)}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.transform = 'translateY(-8px) scale(1.02)'
                        e.currentTarget.style.boxShadow = '0 25px 50px rgba(0, 0, 0, 0.15)'
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.transform = 'translateY(0) scale(1)'
                        e.currentTarget.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.1)'
                      }}
                    >
                      {/* Decorative accent bar */}
                      <div style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: '4px',
                        background: fileIcon.accentClass === 'bg-red-500' ? '#ef4444' :
                                   fileIcon.accentClass === 'bg-blue-500' ? '#3b82f6' :
                                   fileIcon.accentClass === 'bg-green-500' ? '#10b981' :
                                   fileIcon.accentClass === 'bg-indigo-500' ? '#6366f1' : '#6b7280',
                        borderRadius: '1rem 1rem 0 0'
                      }}></div>
                      <div style={{
                        display: 'flex',
                        flexDirection: 'column',
                        height: '100%'
                      }}>
                        <div style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '1rem',
                          marginBottom: '1rem'
                        }}>
                          <div style={{
                            width: '4rem',
                            height: '4rem',
                            background: fileIcon.bgClass === 'bg-red-50' ? '#fef2f2' :
                                       fileIcon.bgClass === 'bg-blue-50' ? '#eff6ff' :
                                       fileIcon.bgClass === 'bg-green-50' ? '#ecfdf5' :
                                       fileIcon.bgClass === 'bg-indigo-50' ? '#eef2ff' : '#f9fafb',
                            color: fileIcon.colorClass === 'text-red-600' ? '#dc2626' :
                                   fileIcon.colorClass === 'text-blue-600' ? '#2563eb' :
                                   fileIcon.colorClass === 'text-green-600' ? '#16a34a' :
                                   fileIcon.colorClass === 'text-indigo-600' ? '#4f46e5' : '#6b7280',
                            borderRadius: '1rem',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
                            transition: 'transform 0.3s ease'
                          }}>
                            {fileIcon.icon}
                          </div>
                          <div style={{
                            flex: '1 1 0%',
                            minWidth: 0
                          }}>
                            <p style={{
                              fontSize: '1.125rem',
                              fontWeight: '600',
                              color: '#111827',
                              lineHeight: '1.4',
                              marginBottom: '0.25rem',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              display: '-webkit-box',
                              WebkitLineClamp: 2,
                              WebkitBoxOrient: 'vertical',
                              transition: 'color 0.3s ease'
                            }}>
                              {document.original_filename}
                            </p>
                            <p style={{
                              fontSize: '0.875rem',
                              color: '#6b7280',
                              fontWeight: '500'
                            }}>
                              {formatFileSize(document.file_size)}
                            </p>
                          </div>
                        </div>
                        
                        <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                          {/* <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between'
                          }}> */}
                            <span style={{
                              fontSize: '0.875rem',
                              color: '#6b7280'
                            }}>
                              {formatDate(document.upload_date)}
                            </span>
                            <div style={{ display: 'flex', justifyContent: 'flex-start', gap: '0.5rem' }}>
                            <span style={{
                              padding: '0.25rem 0.75rem',
                              borderRadius: '9999px',
                              fontSize: '0.75rem',
                              fontWeight: '500',
                              background: document.processing_status === 'completed' ? '#dbeafe' :
                                         document.processing_status === 'processing' ? '#e0f2fe' : '#dbeafe',
                              color: document.processing_status === 'completed' ? '#1e40af' :
                                     document.processing_status === 'processing' ? '#0369a1' : '#1e40af'
                            }}>
                              {document.processing_status}
                            </span>
                            {document.document_type && (
                              <span style={getDocumentTypeBadgeStyle(document.document_type)}>
                                {document.document_type}
                              </span>
                            )}
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
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '2rem'
            }}>
              <div>
                <h2 style={{
                  fontSize: '1.875rem',
                  fontWeight: '700',
                  color: '#111827',
                  marginBottom: '0.5rem'
                }}>All Files</h2>
                <p style={{
                  color: '#6b7280',
                  fontSize: '1rem'
                }}>
                  {filteredDocuments.length} {filteredDocuments.length === 1 ? 'document' : 'documents'} found
                </p>
              </div>
            </div>

            {filteredDocuments.length === 0 ? (
              <div style={{
                textAlign: 'center',
                padding: '5rem 2rem',
                background: 'rgba(255, 255, 255, 0.7)',
                backdropFilter: 'blur(20px)',
                borderRadius: '1.5rem',
                border: '1px solid rgba(255, 255, 255, 0.5)',
                boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)'
              }}>
                <div style={{
                  width: '6rem',
                  height: '6rem',
                  background: '#f3f4f6',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 1.5rem'
                }}>
                  <svg style={{
                    width: '3rem',
                    height: '3rem',
                    color: '#9ca3af'
                  }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 5a2 2 0 012-2h4a2 2 0 012 2v2H8V5z" />
                  </svg>
                </div>
                <h3 style={{
                  fontSize: '1.5rem',
                  fontWeight: '700',
                  color: '#111827',
                  marginBottom: '0.75rem'
                }}>No documents found</h3>
                <p style={{
                  color: '#6b7280',
                  fontSize: '1.125rem',
                  maxWidth: '28rem',
                  margin: '0 auto 2rem',
                  lineHeight: '1.6'
                }}>
                  {searchQuery || filterStatus !== "all" 
                    ? "Try adjusting your search terms or filters to find what you're looking for"
                    : "Upload your first document to get started. Your files will appear here."
                  }
                </p>
                <button style={{
                  padding: '1rem 2rem',
                  background: 'linear-gradient(135deg, #3b82f6 0%, #6366f1 100%)',
                  color: 'white',
                  fontWeight: '600',
                  borderRadius: '1rem',
                  boxShadow: '0 10px 25px rgba(59, 130, 246, 0.3)',
                  transition: 'all 0.3s ease',
                  cursor: 'pointer',
                  border: 'none',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}
                onMouseEnter={(e) => {
                  const target = e.target as HTMLButtonElement
                  target.style.transform = 'translateY(-2px) scale(1.05)'
                  target.style.boxShadow = '0 20px 40px rgba(59, 130, 246, 0.4)'
                }}
                onMouseLeave={(e) => {
                  const target = e.target as HTMLButtonElement
                  target.style.transform = 'translateY(0) scale(1)'
                  target.style.boxShadow = '0 10px 25px rgba(59, 130, 246, 0.3)'
                }}>
                  <svg style={{
                    width: '1.25rem',
                    height: '1.25rem'
                  }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  Upload Document
                </button>
              </div>
            ) : viewMode === 'grid' ? (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                gap: '1.5rem'
              }}>
                {filteredDocuments.map((document) => {
                  const fileIcon = getFileIcon(document.content_type)
                  return (
                    <div
                      key={document.id}
                      style={{
                        cursor: 'pointer',
                        position: 'relative',
                        overflow: 'hidden',
                        background: 'rgba(255, 255, 255, 0.8)',
                        backdropFilter: 'blur(20px)',
                        borderRadius: '1rem',
                        border: '1px solid rgba(255, 255, 255, 0.5)',
                        boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
                        transition: 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
                        display: 'flex',
                        flexDirection: 'column'
                      }}
                      onClick={() => handleDocumentClick(document)}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.transform = 'translateY(-4px) scale(1.02)'
                        e.currentTarget.style.boxShadow = '0 25px 50px rgba(0, 0, 0, 0.15)'
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.transform = 'translateY(0) scale(1)'
                        e.currentTarget.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.1)'
                      }}
                    >
                      {/* Decorative accent bar */}
                      <div style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: '4px',
                        background: fileIcon.accentClass === 'bg-red-500' ? '#ef4444' :
                                   fileIcon.accentClass === 'bg-blue-500' ? '#3b82f6' :
                                   fileIcon.accentClass === 'bg-green-500' ? '#10b981' :
                                   fileIcon.accentClass === 'bg-indigo-500' ? '#6366f1' : '#6b7280',
                        borderRadius: '1rem 1rem 0 0'
                      }}></div>
                      {/* Document Preview/Icon */}
                      <div style={{
                        height: '10rem',
                        background: fileIcon.bgClass === 'bg-red-50' ? '#fef2f2' :
                                   fileIcon.bgClass === 'bg-blue-50' ? '#eff6ff' :
                                   fileIcon.bgClass === 'bg-green-50' ? '#ecfdf5' :
                                   fileIcon.bgClass === 'bg-indigo-50' ? '#eef2ff' : '#f9fafb',
                        borderRadius: '1rem 1rem 0 0',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        position: 'relative',
                        overflow: 'hidden'
                      }}>
                        {document.thumbnail_url ? (
                          <img
                            src={document.thumbnail_url}
                            alt={document.original_filename}
                            style={{
                              width: '100%',
                              height: 'auto',
                              objectFit: 'cover',
                              transition: 'transform 0.5s ease'
                            }}
                          />
                        ) : (
                          <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            height: '100%',
                            background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
                            color: '#9ca3af',
                            fontSize: '0.875rem',
                            fontWeight: '500',
                            textTransform: 'uppercase',
                            letterSpacing: '0.1em'
                          }}>
                            No Preview Available
                          </div>
                        )}
                        {/* Action Buttons */}
                        <div style={{
                          position: 'absolute',
                          top: '0.75rem',
                          right: '0.75rem',
                          // opacity: 0,
                          transition: 'opacity 0.3s ease',
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '0.5rem'
                        }}
                        className="group-hover:opacity-100">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDownload(document)
                            }}
                            style={{
                              width: '2rem',
                              height: '2rem',
                              background: 'rgba(255, 255, 255, 0.9)',
                              backdropFilter: 'blur(10px)',
                              borderRadius: '0.75rem',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              color: '#6b7280',
                              boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
                              transition: 'all 0.3s ease',
                              cursor: 'pointer',
                              border: 'none'
                            }}
                            onMouseEnter={(e) => {
                              const target = e.target as HTMLButtonElement
                              target.style.color = '#2563eb'
                              target.style.background = '#ffffff'
                              target.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.15)'
                            }}
                            onMouseLeave={(e) => {
                              const target = e.target as HTMLButtonElement
                              target.style.color = '#6b7280'
                              target.style.background = 'rgba(255, 255, 255, 0.9)'
                              target.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.1)'
                            }}
                            title="Download"
                          >
                            <svg style={{ width: '1.25rem', height: '1.25rem' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDelete(document)
                            }}
                            style={{
                              width: '2rem',
                              height: '2rem',
                              background: 'rgba(255, 255, 255, 0.9)',
                              backdropFilter: 'blur(10px)',
                              borderRadius: '0.75rem',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              color: '#6b7280',
                              boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
                              transition: 'all 0.3s ease',
                              cursor: 'pointer',
                              border: 'none'
                            }}
                            onMouseEnter={(e) => {
                              const target = e.target as HTMLButtonElement
                              target.style.color = '#dc2626'
                              target.style.background = '#ffffff'
                              target.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.15)'
                            }}
                            onMouseLeave={(e) => {
                              const target = e.target as HTMLButtonElement
                              target.style.color = '#6b7280'
                              target.style.background = 'rgba(255, 255, 255, 0.9)'
                              target.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.1)'
                            }}
                            title="Delete"
                          >
                            <svg style={{ width: '1.25rem', height: '1.25rem' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        </div>
                      </div>
                      {/* Document Info */}
                      <div style={{ 
                        padding: '1.5rem',
                        display: 'flex',
                        flexDirection: 'column',
                        flex: 1
                      }}>
                        <div style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '1rem',
                          marginBottom: '1rem'
                        }}>
                          <div style={{
                            width: '3.5rem',
                            height: '3.5rem',
                            background: fileIcon.bgClass === 'bg-red-50' ? '#fef2f2' :
                                       fileIcon.bgClass === 'bg-blue-50' ? '#eff6ff' :
                                       fileIcon.bgClass === 'bg-green-50' ? '#ecfdf5' :
                                       fileIcon.bgClass === 'bg-indigo-50' ? '#eef2ff' : '#f9fafb',
                            color: fileIcon.colorClass === 'text-red-600' ? '#dc2626' :
                                   fileIcon.colorClass === 'text-blue-600' ? '#2563eb' :
                                   fileIcon.colorClass === 'text-green-600' ? '#16a34a' :
                                   fileIcon.colorClass === 'text-indigo-600' ? '#4f46e5' : '#6b7280',
                            borderRadius: '0.75rem',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
                            transition: 'transform 0.3s ease'
                          }}>
                            {fileIcon.icon}
                          </div>
                          <div style={{
                            flex: '1 1 0%',
                            minWidth: 0
                          }}>
                            <p style={{
                              fontSize: '1.125rem',
                              fontWeight: '600',
                              color: '#111827',
                              lineHeight: '1.4',
                              marginBottom: '0.25rem',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              display: '-webkit-box',
                              WebkitLineClamp: 2,
                              WebkitBoxOrient: 'vertical',
                              transition: 'color 0.3s ease'
                            }}>
                              {document.original_filename}
                            </p>
                            <p style={{
                              fontSize: '0.875rem',
                              color: '#6b7280',
                              fontWeight: '500'
                            }}>
                              {formatFileSize(document.file_size)}
                            </p>
                          </div>
                        </div>

                        <div style={ { marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                          <span style={{
                            fontSize: '0.875rem',
                            color: '#6b7280',
                            textAlign: 'left'
                          }}>
                            {formatDate(document.upload_date)}
                          </span>
                          <div style={{ display: 'flex', justifyContent: 'flex-start', gap: '0.5rem' }}>
                          <span style={{
                            padding: '0.25rem 0.75rem',
                            borderRadius: '9999px',
                            fontSize: '0.75rem',
                            fontWeight: '500',
                            background: document.processing_status === 'completed' ? '#dbeafe' :
                                       document.processing_status === 'processing' ? '#e0f2fe' : '#dbeafe',
                            color: document.processing_status === 'completed' ? '#1e40af' :
                                   document.processing_status === 'processing' ? '#0369a1' : '#1e40af'
                          }}>
                            {document.processing_status}
                          </span>
                          {document.document_type && (
                              <span style={getDocumentTypeBadgeStyle(document.document_type)}>
                                {document.document_type}
                              </span>
                            )}
                        </div>
                        </div>
                        
                        {/* <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-500 font-medium">{formatFileSize(document.file_size)}</span>
                          <span className="text-gray-400">{formatDate(document.upload_date)}</span>
                        </div> */}
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              /* Enhanced List View */
              <div className="bg-white/70 backdrop-blur-sm rounded-2xl border border-white/40 overflow-hidden shadow-lg">
                <div className="divide-y divide-gray-100/60">
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
                            <span style={{
                              ...getStatusBadgeStyle(document.processing_status),
                              backgroundColor: document.processing_status === 'failed' ? '#dbeafe' : getStatusBadgeStyle(document.processing_status).backgroundColor,
                              color: document.processing_status === 'failed' ? '#1e40af' : getStatusBadgeStyle(document.processing_status).color,
                              borderColor: document.processing_status === 'failed' ? '#93c5fd' : getStatusBadgeStyle(document.processing_status).borderColor
                            }}>
                              {document.processing_status}
                            </span>
                            {document.document_type && (
                              <span style={getDocumentTypeBadgeStyle(document.document_type)}>
                                {document.document_type}
                              </span>
                            )}
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
              style={{ maxWidth: 900, width: '95vw', minHeight: 500, display: 'flex', flexDirection: 'column' }}
            >
              <div className="docview-modal-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1.5rem 2rem 0rem 2rem' }}>
              <h2 className="docview-text-2xl docview-font-bold docview-text-gray-900">Document Details</h2>
              <button
                onClick={() => setSelectedDocument(null)}
                className="docview-modal-close"
              >
                <i className="fas fa-times docview-icon-lg"></i>
              </button>
              </div>
              <div style={{ flex: 1, display: 'flex', gap: 25, padding: '0 2rem 2rem 2rem', minHeight: 0 }}>
              {/* Left: Preview */}
              <div style={{ flex: 2, minWidth: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f8fafc', borderRadius: 16, minHeight: 650, overflow: 'auto', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
                {selectedDocument.content_type.includes('pdf') ? (
                <iframe
                  src={selectedDocument.download_url}
                  title="PDF Preview"
                  style={{ width: '100%', height: '100%', border: 'none', minHeight: 400 }}
                />
                ) : selectedDocument.content_type.startsWith('image/') ? (
                <img
                  src={selectedDocument.download_url || selectedDocument.thumbnail_url}
                  alt={selectedDocument.original_filename}
                  style={{ maxWidth: '100%', maxHeight: 480, borderRadius: 12, objectFit: 'contain', background: '#fff' }}
                />
                ) : selectedDocument.content_type.includes('text') ? (
                <iframe
                  src={selectedDocument.download_url}
                  title="Text Preview"
                  style={{ width: '100%', height: 480, border: 'none', background: '#fff', borderRadius: 12 }}
                />
                ) : (
                <div style={{ textAlign: 'center', color: '#64748b', fontSize: 18, width: '100%' }}>
                  <div style={{ marginBottom: 16 }}>
                  {getFileIcon(selectedDocument.content_type).icon}
                  </div>
                  <div>No preview available for this file type.</div>
                </div>
                )}
              </div>
              {/* Right: Details */}
              <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: 24 }}>
                <div className="docview-flex docview-items-center docview-gap-4" style={{ marginBottom: 16 }}>
                <div className={`docview-w-16 docview-h-16 ${getFileIcon(selectedDocument.content_type).bgClass} docview-rounded-xl docview-flex docview-items-center docview-justify-center docview-text-3xl docview-shadow`}>
                  {getFileIcon(selectedDocument.content_type).icon}
                </div>
                <div style={{ flex: 1 }}>
                  <h3 className="docview-font-bold docview-text-lg docview-text-gray-900 docview-mb-1" style={{ marginBottom: 4 }}>{selectedDocument.original_filename}</h3>
                  <div className="docview-flex docview-items-center docview-gap-2">
                  <span style={{
                    ...getStatusBadgeStyle(selectedDocument.processing_status),
                    backgroundColor: selectedDocument.processing_status === 'failed' ? '#dbeafe' : getStatusBadgeStyle(selectedDocument.processing_status).backgroundColor,
                    color: selectedDocument.processing_status === 'failed' ? '#1e40af' : getStatusBadgeStyle(selectedDocument.processing_status).color,
                    borderColor: selectedDocument.processing_status === 'failed' ? '#93c5fd' : getStatusBadgeStyle(selectedDocument.processing_status).borderColor
                  }}>
                    {selectedDocument.processing_status}
                  </span>
                  {selectedDocument.document_type && (
                    <span style={getDocumentTypeBadgeStyle(selectedDocument.document_type)}>
                      {selectedDocument.document_type}
                    </span>
                  )}
                  {/* <span className="docview-text-xs docview-text-gray-500">{formatFileSize(selectedDocument.file_size)}</span> */}
                  </div>
                </div>
                </div>
                <div className="docview-detail-grid" style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 12 }}>
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
                {/* <div>
                  <span className="docview-detail-label">Document ID</span>
                  <p className="docview-detail-value docview-detail-id">{selectedDocument.id}</p>
                </div> */}
                {selectedDocument.document_type && (
                  <div>
                  <span className="docview-detail-label">Document Type</span>
                  <p className="docview-detail-value">{selectedDocument.document_type}</p>
                  </div>
                )}
                {/* <div>
                  <span className="docview-detail-label">Uploaded By</span>
                  <p className="docview-detail-value">User {selectedDocument.user_id.slice(0, 8)}...</p>
                </div> */}
                </div>
                <div className="docview-modal-actions docview-flex docview-gap-3 docview-pt-2" style={{ marginTop: 16 }}>
                <button
                  onClick={() => handleDownload(selectedDocument)}
                  className="docview-flex-1 docview-cta-primary"
                >
                  <i className="fas fa-download"></i>
                  Download
                </button>
                <button
                  onClick={() => handleDelete(selectedDocument)}
                  className="docview-flex-1 docview-cta-danger"
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
    </>
  )
}