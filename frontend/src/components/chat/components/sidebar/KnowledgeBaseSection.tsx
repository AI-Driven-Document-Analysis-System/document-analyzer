import type { ExpandedSections, Document } from '../../types'
import { getDocumentIcon } from '../../utils/documentUtils'

interface KnowledgeBaseSectionProps {
  expandedSections: ExpandedSections
  toggleSection: (section: keyof ExpandedSections) => void
  selectedDocuments: number[]
  documents: Document[]
  onShowDocumentModal: () => void
  onRemoveDocument: (docId: number) => void
  documentsLoading?: boolean
  documentsError?: string | null
}

export function KnowledgeBaseSection({ 
  expandedSections, 
  toggleSection, 
  selectedDocuments, 
  documents, 
  onShowDocumentModal, 
  onRemoveDocument,
  documentsLoading = false,
  documentsError = null
}: KnowledgeBaseSectionProps) {
  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
      <div 
        style={{ padding: '16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', transition: 'background-color 0.2s' }}
        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#374151'}
        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
        onClick={() => toggleSection('knowledge')}
      >
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <i className="fas fa-database" style={{ color: '#60a5fa', marginRight: '8px' }}></i>
          <div>
            <h3 style={{ fontWeight: '500', color: 'white', margin: 0 }}>Knowledge Base</h3>
            <p style={{ fontSize: '12px', color: '#d1d5db', margin: '2px 0 0 0' }}>Manage document sources</p>
          </div>
        </div>
        <i className={`fas ${expandedSections.knowledge ? 'fa-chevron-up' : 'fa-chevron-down'}`} style={{ color: '#d1d5db' }}></i>
      </div>
      {expandedSections.knowledge && (
        <div style={{ padding: '0 16px 100px 16px', flex: 1 }}>
          <div style={{ textAlign: 'center', padding: '16px 0' }}>
            <button 
              onClick={onShowDocumentModal}
              style={{ 
                backgroundColor: '#3b82f6', 
                color: 'white', 
                padding: '8px 16px', 
                borderRadius: '8px', 
                border: 'none', 
                fontSize: '14px', 
                cursor: 'pointer',
                transition: 'background-color 0.2s'
              }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#2563eb'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#3b82f6'}
            >
              <i className="fas fa-plus" style={{ marginRight: '4px' }}></i> Select Documents
            </button>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: '8px' }}>
            {documentsLoading ? (
              <div style={{ 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center', 
                padding: '20px',
                color: '#9ca3af'
              }}>
                <div style={{
                  width: '20px',
                  height: '20px',
                  border: '2px solid #4b5563',
                  borderTop: '2px solid #60a5fa',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite',
                  marginBottom: '8px'
                }}></div>
                <p style={{ fontSize: '12px', margin: 0 }}>Loading documents...</p>
                <style jsx>{`
                  @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                  }
                `}</style>
              </div>
            ) : documentsError ? (
              <div style={{ 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center', 
                padding: '20px',
                color: '#ef4444',
                textAlign: 'center'
              }}>
                <i className="fas fa-exclamation-triangle" style={{ fontSize: '16px', marginBottom: '8px' }}></i>
                <p style={{ fontSize: '12px', margin: '0 0 4px 0', fontWeight: '500' }}>Failed to load</p>
                <p style={{ fontSize: '10px', margin: 0, color: '#9ca3af' }}>{documentsError}</p>
              </div>
            ) : selectedDocuments.length === 0 ? (
              <p style={{ fontSize: '12px', color: '#9ca3af', width: '100%', textAlign: 'center' }}>No documents selected</p>
            ) : (
              selectedDocuments.map(docId => {
                const doc = documents.find(d => d.id === docId)
                if (!doc) return null
                const iconInfo = getDocumentIcon(doc.type)
                return (
                  <div key={docId} style={{
                    display: 'flex',
                    alignItems: 'center',
                    backgroundColor: '#374151',
                    border: '1px solid #4b5563',
                    borderRadius: '8px',
                    padding: '8px 12px',
                    fontSize: '12px',
                    color: 'white'
                  }}>
                    <i className={`fas ${iconInfo.icon}`} style={{ 
                      color: iconInfo.color, 
                      marginRight: '8px',
                      fontSize: '14px'
                    }}></i>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <p style={{ fontWeight: '500', fontSize: '12px', margin: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{doc.name}</p>
                      <p style={{ fontSize: '10px', color: '#d1d5db', margin: '2px 0 0 0' }}>{doc.size}</p>
                    </div>
                    <button 
                      onClick={(e) => {
                        e.stopPropagation()
                        onRemoveDocument(docId)
                      }}
                      style={{ 
                        marginLeft: '8px', 
                        backgroundColor: 'transparent', 
                        border: 'none', 
                        color: '#9ca3af', 
                        cursor: 'pointer',
                        fontSize: '12px',
                        padding: '4px'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.color = '#ef4444'}
                      onMouseLeave={(e) => e.currentTarget.style.color = '#9ca3af'}
                    >
                      <i className="fas fa-times"></i>
                    </button>
                  </div>
                )
              })
            )}
          </div>
        </div>
      )}
    </div>
  )
}
