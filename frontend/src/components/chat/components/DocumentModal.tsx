import type { Document } from '../types'
import { getDocumentIcon, formatDate, getFilteredAndSortedDocuments } from '../utils/documentUtils'
import { useTheme } from '../contexts/ThemeContext'
import { useState } from 'react'

// Configuration
const MAX_DOCUMENT_SELECTION_LIMIT = 20

interface DocumentModalProps {
  showModal: boolean
  onClose: () => void
  documents: Document[]
  selectedDocuments: string[]
  documentFilter: string
  setDocumentFilter: (filter: string) => void
  documentSearch: string
  setDocumentSearch: (search: string) => void
  sortDate: string
  setSortDate: (sort: string) => void
  sortSize: string
  setSortSize: (sort: string) => void
  onToggleDocumentSelection: (docId: string) => void
  onClearAllDocuments: () => void
  isLoading?: boolean
  error?: string | null
}

// Preview modal styles
const previewModalStyles = {
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
    zIndex: 10000,
    padding: '20px'
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
    overflow: 'hidden'
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '20px 24px',
    borderBottom: '1px solid #e5e7eb',
    background: 'linear-gradient(135deg, #f8fafc, #e2e8f0)'
  },
  body: {
    flex: 1,
    padding: 0,
    overflow: 'hidden',
    background: '#f7fafc'
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
  unsupported: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    textAlign: 'center' as const,
    padding: '40px',
    color: '#718096'
  }
}

export function DocumentModal({
  showModal,
  onClose,
  documents,
  selectedDocuments,
  documentFilter,
  setDocumentFilter,
  documentSearch,
  setDocumentSearch,
  sortDate,
  setSortDate,
  sortSize,
  setSortSize,
  onToggleDocumentSelection,
  onClearAllDocuments,
  isLoading = false,
  error = null
}: DocumentModalProps) {
  const { isDarkMode } = useTheme()
  
  // Preview states
  const [showPreview, setShowPreview] = useState(false)
  const [previewDocument, setPreviewDocument] = useState<Document | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [loadingPreview, setLoadingPreview] = useState(false)
  
  // Toast notification state
  const [showToast, setShowToast] = useState(false)
  const [toastMessage, setToastMessage] = useState('')
  
  if (!showModal) return null

  const filteredDocuments = getFilteredAndSortedDocuments(
    documents,
    documentFilter,
    documentSearch,
    sortDate,
    sortSize
  )

  // JWT token handling
  const getToken = () => {
    return localStorage.getItem("token")
  }

  // Document preview handler
  const previewDocumentHandler = async (doc: Document) => {
    setLoadingPreview(true)
    setPreviewDocument(doc)
    setShowPreview(true)

    try {
      const token = getToken()
      if (!token) {
        alert('Authentication required')
        return
      }

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

  // Show toast notification
  const showToastNotification = (message: string) => {
    setToastMessage(message)
    setShowToast(true)
    setTimeout(() => {
      setShowToast(false)
    }, 3000) // Hide after 3 seconds
  }

  // Handle document selection with limit check
  const handleDocumentSelection = (docId: string) => {
    const isCurrentlySelected = selectedDocuments.includes(docId)
    
    if (!isCurrentlySelected && selectedDocuments.length >= MAX_DOCUMENT_SELECTION_LIMIT) {
      showToastNotification(`Maximum ${MAX_DOCUMENT_SELECTION_LIMIT} documents can be selected for Document Scope`)
      return
    }
    
    onToggleDocumentSelection(docId)
  }

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      zIndex: 1000,
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center'
    }}>
      <div style={{
        backgroundColor: isDarkMode ? '#2d3748' : 'white',
        borderRadius: '8px',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        width: '95%',
        maxWidth: '1000px',
        maxHeight: '85vh',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {/* Modal Header */}
        <div style={{
          padding: '16px 24px',
          borderBottom: `1px solid ${isDarkMode ? '#4a5568' : '#e2e8f0'}`,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <h3 style={{ fontSize: '18px', fontWeight: '600', color: isDarkMode ? '#f7fafc' : '#1f2937', margin: 0 }}>Set Document Scope</h3>
          <button 
            onClick={onClose}
            style={{
              backgroundColor: 'transparent',
              border: 'none',
              color: isDarkMode ? '#9ca3af' : '#6b7280',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            <i className="fas fa-times"></i>
          </button>
        </div>
        
        {/* Modal Body */}
        <div style={{
          padding: '24px',
          overflowY: 'auto',
          flex: 1
        }}>
          {/* Filter Section */}
          <div style={{
            borderBottom: `1px solid ${isDarkMode ? '#4a5568' : '#e2e8f0'}`,
            paddingBottom: '16px',
            marginBottom: '16px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <h4 style={{ fontWeight: '600', margin: 0, color: isDarkMode ? '#e2e8f0' : '#334155' }}>Filter by Type</h4>
              <div style={{ 
                fontSize: '12px', 
                color: selectedDocuments.length >= MAX_DOCUMENT_SELECTION_LIMIT ? '#ef4444' : (isDarkMode ? '#9ca3af' : '#6b7280'),
                fontWeight: '500',
                padding: '4px 8px',
                borderRadius: '12px',
                backgroundColor: selectedDocuments.length >= MAX_DOCUMENT_SELECTION_LIMIT ? '#fef2f2' : (isDarkMode ? '#374151' : '#f1f5f9'),
                border: `1px solid ${selectedDocuments.length >= MAX_DOCUMENT_SELECTION_LIMIT ? '#fecaca' : (isDarkMode ? '#4a5568' : '#e2e8f0')}`
              }}>
                {selectedDocuments.length}/{MAX_DOCUMENT_SELECTION_LIMIT} selected
              </div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <select 
                  value={sortDate}
                  onChange={(e) => setSortDate(e.target.value)}
                  style={{
                    padding: '4px 8px',
                    borderRadius: '6px',
                    border: `1px solid ${isDarkMode ? '#4a5568' : '#cbd5e1'}`,
                    backgroundColor: isDarkMode ? '#374151' : 'white',
                    color: isDarkMode ? '#f7fafc' : '#1f2937',
                    fontSize: '14px',
                    cursor: 'pointer'
                  }}
                >
                  <option value="none">None</option>
                  <option value="date-desc">Date (Newest First)</option>
                  <option value="date-asc">Date (Oldest First)</option>
                </select>
                <select 
                  value={sortSize}
                  onChange={(e) => setSortSize(e.target.value)}
                  style={{
                    padding: '4px 8px',
                    borderRadius: '6px',
                    border: `1px solid ${isDarkMode ? '#4a5568' : '#cbd5e1'}`,
                    backgroundColor: isDarkMode ? '#374151' : 'white',
                    color: isDarkMode ? '#f7fafc' : '#1f2937',
                    fontSize: '14px',
                    cursor: 'pointer'
                  }}
                >
                  <option value="none">None</option>
                  <option value="size-desc">Size (Largest First)</option>
                  <option value="size-asc">Size (Smallest First)</option>
                </select>
                <button 
                  onClick={onClearAllDocuments}
                  style={{
                    fontSize: '14px',
                    color: isDarkMode ? '#9ca3af' : '#6b7280',
                    backgroundColor: 'transparent',
                    border: 'none',
                    cursor: 'pointer'
                  }}
                >
                  <i className="fas fa-times-circle" style={{ marginRight: '4px' }}></i> Deselect All
                </button>
              </div>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {['all', 'pdf', 'img', 'txt'].map(type => (
                <div 
                  key={type}
                  onClick={() => setDocumentFilter(type)}
                  style={{
                    padding: '4px 12px',
                    borderRadius: '16px',
                    fontSize: '14px',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    backgroundColor: documentFilter === type ? '#3b82f6' : (isDarkMode ? '#4a5568' : '#f1f5f9'),
                    color: documentFilter === type ? 'white' : (isDarkMode ? '#f7fafc' : '#334155'),
                    border: `1px solid ${documentFilter === type ? '#3b82f6' : (isDarkMode ? '#718096' : '#cbd5e1')}`
                  }}
                >
                  {type === 'all' ? 'All' : type.toUpperCase()}
                </div>
              ))}
            </div>
          </div>
          
          {/* Search */}
          <div style={{ marginBottom: '16px' }}>
            <input 
              type="text" 
              placeholder="Search documents..."
              value={documentSearch}
              onChange={(e) => setDocumentSearch(e.target.value)}
              style={{
                width: '100%',
                padding: '8px 12px',
                border: `1px solid ${isDarkMode ? '#4a5568' : '#d1d5db'}`,
                borderRadius: '8px',
                fontSize: '14px',
                backgroundColor: isDarkMode ? '#374151' : 'white',
                color: isDarkMode ? '#f7fafc' : '#1f2937',
                outline: 'none'
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#3b82f6'
                e.target.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)'
              }}
              onBlur={(e) => {
                e.target.style.borderColor = isDarkMode ? '#4a5568' : '#d1d5db'
                e.target.style.boxShadow = 'none'
              }}
            />
          </div>
          
          {/* Documents Grid */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
            gap: '20px'
          }}>
            {isLoading ? (
              <div style={{ 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center', 
                justifyContent: 'center', 
                gridColumn: '1 / -1', 
                padding: '40px',
                color: isDarkMode ? '#9ca3af' : '#6b7280'
              }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  border: '3px solid #e5e7eb',
                  borderTop: '3px solid #3b82f6',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite',
                  marginBottom: '16px'
                }}></div>
                <p style={{ margin: 0, fontSize: '14px' }}>Loading documents...</p>
                <style jsx>{`
                  @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                  }
                `}</style>
              </div>
            ) : error ? (
              <div style={{ 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center', 
                justifyContent: 'center', 
                gridColumn: '1 / -1', 
                padding: '40px',
                color: '#ef4444',
                textAlign: 'center'
              }}>
                <i className="fas fa-exclamation-triangle" style={{ fontSize: '24px', marginBottom: '12px' }}></i>
                <p style={{ margin: '0 0 8px 0', fontSize: '14px', fontWeight: '500' }}>Failed to load documents</p>
                <p style={{ margin: 0, fontSize: '12px', color: '#6b7280' }}>{error}</p>
              </div>
            ) : filteredDocuments.length === 0 ? (
              <p style={{ color: isDarkMode ? '#9ca3af' : '#6b7280', textAlign: 'center', gridColumn: '1 / -1', padding: '16px' }}>No documents found</p>
            ) : (
              filteredDocuments.map(doc => {
                const iconInfo = getDocumentIcon(doc.type)
                const isSelected = selectedDocuments.includes(doc.id)
                return (
                  <div 
                    key={doc.id}
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      padding: '16px',
                      borderRadius: '8px',
                      transition: 'all 0.2s',
                      border: `1px solid ${isSelected ? '#93c5fd' : (isDarkMode ? '#4a5568' : '#e2e8f0')}`,
                      backgroundColor: isSelected ? '#dbeafe' : (isDarkMode ? '#374151' : 'white'),
                      minHeight: '110px',
                      position: 'relative'
                    }}
                  >
                    {/* Selection indicator */}
                    <div style={{
                      position: 'absolute',
                      top: '8px',
                      right: '8px',
                      cursor: 'pointer',
                      padding: '4px'
                    }}
                    onClick={() => handleDocumentSelection(doc.id)}
                    >
                      {isSelected ? (
                        <i className="fas fa-check-circle" style={{ color: '#3b82f6', fontSize: '20px' }}></i>
                      ) : (
                        <i className="far fa-circle" style={{ color: isDarkMode ? '#9ca3af' : '#6b7280', fontSize: '20px' }}></i>
                      )}
                    </div>

                    {/* Document icon and main content */}
                    <div 
                      style={{ cursor: 'pointer', flex: 1 }}
                      onClick={() => handleDocumentSelection(doc.id)}
                    >
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        marginBottom: '12px',
                        paddingRight: '8px'
                      }}>
                        <div style={{
                          marginRight: '12px',
                          width: '48px',
                          height: '48px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          borderRadius: '8px',
                          flexShrink: 0,
                          backgroundColor: iconInfo.bg,
                          color: iconInfo.color
                        }}>
                          <i className={`fas ${iconInfo.icon}`} style={{ fontSize: '24px' }}></i>
                        </div>
                        <div style={{ flex: 1, minWidth: 0, paddingRight: '32px' }}>
                          <p style={{ 
                            fontWeight: '600', 
                            fontSize: '16px', 
                            margin: 0, 
                            color: isDarkMode ? '#f7fafc' : '#1f2937',
                            lineHeight: '1.2',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                          }}>
                            {doc.name}
                          </p>
                          <p style={{ 
                            fontSize: '13px', 
                            color: isDarkMode ? '#9ca3af' : '#6b7280', 
                            margin: '4px 0 0 0' 
                          }}>
                            {doc.size}
                          </p>
                        </div>
                      </div>
                      
                      {/* Date and Preview button row */}
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        marginTop: 'auto'
                      }}>
                        <p style={{ 
                          fontSize: '12px', 
                          color: isDarkMode ? '#9ca3af' : '#94a3b8', 
                          margin: 0
                        }}>
                          {formatDate(doc.date)}
                        </p>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            previewDocumentHandler(doc)
                          }}
                          style={{
                            backgroundColor: '#3b82f6',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            padding: '6px 10px',
                            fontSize: '12px',
                            fontWeight: '500',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px',
                            transition: 'background-color 0.2s'
                          }}
                          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#2563eb'}
                          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#3b82f6'}
                          title="Preview document"
                        >
                          <i className="fas fa-eye" style={{ fontSize: '10px' }}></i>
                          Preview
                        </button>
                      </div>
                    </div>
                  </div>
                )
              })
            )}
          </div>
        </div>
        
        {/* Modal Footer */}
        <div style={{
          padding: '16px 24px',
          borderTop: `1px solid ${isDarkMode ? '#4a5568' : '#e2e8f0'}`,
          display: 'flex',
          justifyContent: 'flex-end',
          gap: '8px'
        }}>
          <button 
            onClick={onClose}
            style={{
              padding: '8px 16px',
              color: isDarkMode ? '#9ca3af' : '#374151',
              backgroundColor: 'transparent',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'background-color 0.2s'
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = isDarkMode ? '#4a5568' : '#f3f4f6'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
          >
            Cancel
          </button>
          <button 
            onClick={onClose}
            style={{
              padding: '8px 16px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'background-color 0.2s'
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#2563eb'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#3b82f6'}
          >
            Done
          </button>
        </div>
      </div>
      
      {/* Document Preview Modal */}
      {showPreview && (
        <div style={previewModalStyles.overlay}>
          <div style={previewModalStyles.container}>
            <div style={previewModalStyles.header}>
              <div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#1a202c', margin: '0 0 4px 0' }}>
                  {previewDocument?.name}
                </h3>
                <p style={{ fontSize: '0.875rem', color: '#718096', margin: 0 }}>
                  {previewDocument?.type} • {previewDocument && formatDate(previewDocument.date)}
                </p>
              </div>
              <button
                onClick={closePreview}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '24px',
                  color: '#718096',
                  cursor: 'pointer',
                  padding: '8px',
                  borderRadius: '8px',
                  transition: 'all 0.2s ease'
                }}
              >
                ✕
              </button>
            </div>

            <div style={previewModalStyles.body}>
              {loadingPreview ? (
                <div style={previewModalStyles.loading}>
                  <div style={previewModalStyles.loadingSpinner}></div>
                  <p>Loading document preview...</p>
                  <style jsx>{`
                    @keyframes spin {
                      0% { transform: rotate(0deg); }
                      100% { transform: rotate(360deg); }
                    }
                  `}</style>
                </div>
              ) : previewUrl ? (
                <div style={{ width: '100%', height: '100%' }}>
                  {previewDocument?.type === 'PDF' || previewDocument?.name?.toLowerCase().endsWith('.pdf') ? (
                    <iframe
                      src={previewUrl}
                      style={previewModalStyles.iframe}
                      title="Document Preview"
                    />
                  ) : previewDocument?.type?.startsWith('image/') ||
                       ['JPG', 'JPEG', 'PNG', 'GIF'].includes(previewDocument?.type || '') ||
                       previewDocument?.name?.match(/\.(jpg|jpeg|png|gif)$/i) ? (
                    <div style={previewModalStyles.imageViewer}>
                      <img
                        src={previewUrl}
                        alt="Document Preview"
                        style={previewModalStyles.image}
                      />
                    </div>
                  ) : (
                    <div style={previewModalStyles.unsupported}>
                      <div style={{ fontSize: '4rem', marginBottom: '16px', color: '#a0aec0' }}>
                        <i className="fas fa-file"></i>
                      </div>
                      <h4 style={{ fontSize: '1.25rem', color: '#2d3748', marginBottom: '8px' }}>
                        Preview not available
                      </h4>
                      <p style={{ color: '#718096', marginBottom: '24px' }}>
                        Preview not available for this file type
                      </p>
                      <a
                        href={previewUrl}
                        download={previewDocument?.name}
                        style={{
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
                          gap: '8px',
                          textDecoration: 'none'
                        }}
                      >
                        <i className="fas fa-download"></i>
                        Download File
                      </a>
                    </div>
                  )}
                </div>
              ) : (
                <div style={previewModalStyles.error}>
                  <div style={{ fontSize: '4rem', marginBottom: '16px', color: '#e53e3e' }}>
                    <i className="fas fa-exclamation-triangle"></i>
                  </div>
                  <h4 style={{ fontSize: '1.25rem', color: '#2d3748', marginBottom: '8px' }}>
                    Failed to load document preview
                  </h4>
                  <p style={{ color: '#718096' }}>
                    Unable to load the document preview
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      
      {/* Toast Notification */}
      {showToast && (
        <div style={{
          position: 'fixed',
          top: '20px',
          left: '50%',
          transform: 'translateX(-50%)',
          backgroundColor: '#ef4444',
          color: 'white',
          padding: '12px 24px',
          borderRadius: '8px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          zIndex: 10001,
          fontSize: '14px',
          fontWeight: '500',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          animation: 'slideDown 0.3s ease-out'
        }}>
          <i className="fas fa-exclamation-circle"></i>
          {toastMessage}
          <style jsx>{`
            @keyframes slideDown {
              from {
                opacity: 0;
                transform: translateX(-50%) translateY(-10px);
              }
              to {
                opacity: 1;
                transform: translateX(-50%) translateY(0);
              }
            }
          `}</style>
        </div>
      )}
    </div>
  )
}
