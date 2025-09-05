interface SidebarHeaderProps {
  onNewChat: () => void
}

export function SidebarHeader({ onNewChat }: SidebarHeaderProps) {
  return (
    <div style={{ borderBottom: '1px solid #4b5563', padding: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: '600', color: 'white', margin: 0 }}>Assistant Panel</h2>
        <button
          onClick={onNewChat}
          style={{
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            padding: '6px 12px',
            fontSize: '12px',
            fontWeight: '500',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            display: 'flex',
            alignItems: 'center',
            gap: '4px'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#2563eb'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = '#3b82f6'
          }}
        >
          <i className="fas fa-plus" style={{ fontSize: '10px' }}></i>
          New Chat
        </button>
      </div>
      <p style={{ fontSize: '12px', color: '#d1d5db', margin: 0 }}>Document insights and controls</p>
    </div>
  )
}
