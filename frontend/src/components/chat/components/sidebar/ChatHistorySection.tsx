import type { ExpandedSections, ChatHistory } from '../../types'

interface ChatHistorySectionProps {
  expandedSections: ExpandedSections
  toggleSection: (section: keyof ExpandedSections) => void
  chatHistory: ChatHistory[]
  onChatHistoryClick: (chatId: string) => void
  onDeleteChat: (chatId: string) => void
  selectedChatId?: string
}

export function ChatHistorySection({ expandedSections, toggleSection, chatHistory, onChatHistoryClick, onDeleteChat, selectedChatId }: ChatHistorySectionProps) {
  return (
    <div style={{ borderBottom: '1px solid #4b5563', flexShrink: 0 }}>
      <div 
        style={{ padding: '16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', transition: 'background-color 0.2s' }}
        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#374151'}
        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
        onClick={() => toggleSection('history')}
      >
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <i className="fas fa-history" style={{ color: '#60a5fa', marginRight: '8px' }}></i>
          <div>
            <h3 style={{ fontWeight: '500', color: 'white', margin: 0 }}>Chat History</h3>
            <p style={{ fontSize: '12px', color: '#d1d5db', margin: '2px 0 0 0' }}>Previous conversations</p>
          </div>
        </div>
        <i className={`fas ${expandedSections.history ? 'fa-chevron-up' : 'fa-chevron-down'}`} style={{ color: '#d1d5db' }}></i>
      </div>
      {expandedSections.history && (
        <div style={{ 
          padding: '0 16px 16px 16px',
          maxHeight: '250px',
          overflowY: 'auto',
          overflowX: 'hidden'
        }}>
          {chatHistory
            .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
            .map((chat) => (
            <div key={chat.id} style={{ 
                   padding: '8px 12px', 
                   backgroundColor: selectedChatId === chat.id ? '#1e40af' : '#374151', 
                   borderRadius: '8px', 
                   border: selectedChatId === chat.id ? '1px solid #3b82f6' : '1px solid #4b5563', 
                   marginBottom: '6px', 
                   cursor: 'pointer', 
                   transition: 'all 0.2s',
                   boxShadow: selectedChatId === chat.id ? '0 0 0 1px rgba(59, 130, 246, 0.3)' : 'none'
                 }}
                 onMouseEnter={(e) => {
                   if (selectedChatId !== chat.id) {
                     e.currentTarget.style.backgroundColor = '#4b5563'
                   }
                 }}
                 onMouseLeave={(e) => {
                   if (selectedChatId !== chat.id) {
                     e.currentTarget.style.backgroundColor = '#374151'
                   }
                 }}
                 onClick={(e) => {
                   // Only trigger chat selection if not clicking on delete button
                   if (!(e.target as HTMLElement).closest('.delete-btn')) {
                     onChatHistoryClick(chat.id);
                   }
                 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <i className="fas fa-comment" style={{ color: '#d1d5db', fontSize: '14px' }}></i>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <p style={{ fontWeight: '500', fontSize: '12px', color: 'white', margin: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{chat.title}</p>
                  <p style={{ fontSize: '10px', color: '#d1d5db', margin: '2px 0 0 0' }}>{chat.timestamp}</p>
                </div>
                <button
                  className="delete-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteChat(chat.id);
                  }}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#ef4444',
                    cursor: 'pointer',
                    padding: '4px',
                    borderRadius: '4px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    opacity: 0.7,
                    transition: 'all 0.2s ease',
                    fontSize: '12px',
                    width: '24px',
                    height: '24px'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.opacity = '1';
                    e.currentTarget.style.backgroundColor = 'rgba(239, 68, 68, 0.1)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.opacity = '0.7';
                    e.currentTarget.style.backgroundColor = 'transparent';
                  }}
                  title="Delete conversation"
                >
                  <i className="fas fa-trash" style={{ fontSize: '10px' }}></i>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
