import type { Document } from '../types'
import { getDocumentIcon, formatDate, getFilteredAndSortedDocuments } from '../utils/documentUtils'
import { useTheme } from '../contexts/ThemeContext'

interface DocumentModalProps {
  showModal: boolean
  onClose: () => void
  documents: Document[]
  selectedDocuments: number[]
  documentFilter: string
  setDocumentFilter: (filter: string) => void
  documentSearch: string
  setDocumentSearch: (search: string) => void
  sortDate: string
  setSortDate: (sort: string) => void
  sortSize: string
  setSortSize: (sort: string) => void
  onToggleDocumentSelection: (docId: number) => void
  onClearAllDocuments: () => void
  isLoading?: boolean
  error?: string | null
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
  if (!showModal) return null

  const filteredDocuments = getFilteredAndSortedDocuments(
    documents,
    documentFilter,
    documentSearch,
    sortDate,
    sortSize
  )

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
          <h3 style={{ fontSize: '18px', fontWeight: '600', color: isDarkMode ? '#f7fafc' : '#1f2937', margin: 0 }}>Select Documents</h3>
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
            gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
            gap: '16px'
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
                    onClick={() => onToggleDocumentSelection(doc.id)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      padding: '12px',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      border: `1px solid ${isSelected ? '#93c5fd' : (isDarkMode ? '#4a5568' : '#e2e8f0')}`,
                      backgroundColor: isSelected ? '#dbeafe' : (isDarkMode ? '#374151' : 'white'),
                      minHeight: '40px',
                      overflow: 'hidden'
                    }}
                    onMouseEnter={(e) => {
                      if (!isSelected) {
                        e.currentTarget.style.backgroundColor = isDarkMode ? '#4a5568' : '#f1f5f9'
                        e.currentTarget.style.borderColor = isDarkMode ? '#718096' : '#cbd5e1'
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!isSelected) {
                        e.currentTarget.style.backgroundColor = isDarkMode ? '#374151' : 'white'
                        e.currentTarget.style.borderColor = isDarkMode ? '#4a5568' : '#e2e8f0'
                      }
                    }}
                  >
                    <div style={{
                      marginRight: '12px',
                      width: '40px',
                      height: '40px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      borderRadius: '4px',
                      flexShrink: 0,
                      backgroundColor: iconInfo.bg,
                      color: iconInfo.color
                    }}>
                      <i className={`fas ${iconInfo.icon}`} style={{ fontSize: '18px' }}></i>
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <p style={{ fontWeight: '500', fontSize: '14px', margin: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: isDarkMode ? '#f7fafc' : '#1f2937' }}>{doc.name}</p>
                      <p style={{ fontSize: '12px', color: isDarkMode ? '#9ca3af' : '#6b7280', margin: '4px 0 0 0' }}>{doc.size}</p>
                      <p style={{ fontSize: '12px', color: isDarkMode ? '#9ca3af' : '#94a3b8', margin: '2px 0 0 0' }}>{formatDate(doc.date)}</p>
                    </div>
                    <div>
                      {isSelected && <i className="fas fa-check" style={{ color: '#3b82f6', fontSize: '18px' }}></i>}
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
    </div>
  )
}
