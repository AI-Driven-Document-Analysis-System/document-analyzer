interface NewChatConfirmModalProps {
  showModal: boolean
  onClose: () => void
  onConfirm: () => void
}

export function NewChatConfirmModal({
  showModal,
  onClose,
  onConfirm
}: NewChatConfirmModalProps) {
  if (!showModal) return null

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '24px',
        maxWidth: '450px',
        width: '90%',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
      }}>
        <div style={{ marginBottom: '20px', textAlign: 'center' }}>
          <div style={{
            width: '48px',
            height: '48px',
            backgroundColor: '#dbeafe',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px auto'
          }}>
            <i className="fas fa-database" style={{ color: '#3b82f6', fontSize: '20px' }}></i>
          </div>
          <h3 style={{ 
            margin: '0 0 8px 0', 
            fontSize: '20px', 
            fontWeight: '600', 
            color: '#1f2937' 
          }}>
            Knowledge Base Requires New Chat
          </h3>
          <p style={{ 
            margin: 0, 
            fontSize: '14px', 
            color: '#6b7280',
            lineHeight: '1.5'
          }}>
            To use the Knowledge Base feature with selected documents, you need to start a new conversation. This ensures your questions are answered exclusively from your chosen documents.
          </p>
        </div>
        
        <div style={{
          backgroundColor: '#f8fafc',
          border: '1px solid #e2e8f0',
          borderRadius: '8px',
          padding: '12px',
          marginBottom: '20px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
            <i className="fas fa-info-circle" style={{ color: '#3b82f6', marginRight: '8px', fontSize: '14px' }}></i>
            <span style={{ fontSize: '13px', fontWeight: '500', color: '#374151' }}>What happens next:</span>
          </div>
          <ul style={{ 
            margin: 0, 
            paddingLeft: '20px', 
            fontSize: '13px', 
            color: '#6b7280',
            lineHeight: '1.4'
          }}>
            <li>Your current conversation will be saved</li>
            <li>A new chat will be created</li>
            <li>You can select documents for the Knowledge Base</li>
          </ul>
        </div>
        
        <div style={{ 
          display: 'flex', 
          gap: '12px', 
          justifyContent: 'flex-end' 
        }}>
          <button
            onClick={onClose}
            style={{
              padding: '10px 20px',
              border: '1px solid #d1d5db',
              borderRadius: '8px',
              backgroundColor: 'white',
              color: '#374151',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#f9fafb'
              e.currentTarget.style.borderColor = '#9ca3af'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'white'
              e.currentTarget.style.borderColor = '#d1d5db'
            }}
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            style={{
              padding: '10px 20px',
              border: 'none',
              borderRadius: '8px',
              backgroundColor: '#3b82f6',
              color: 'white',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#2563eb'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#3b82f6'
            }}
          >
            <i className="fas fa-plus" style={{ marginRight: '6px' }}></i>
            Create New Chat
          </button>
        </div>
      </div>
    </div>
  )
}
