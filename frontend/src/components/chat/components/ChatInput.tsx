import type React from "react"

interface ChatInputProps {
  inputValue: string
  setInputValue: (value: string) => void
  onSendMessage: () => void
  isTyping: boolean
  onKeyPress: (e: React.KeyboardEvent) => void
}

export function ChatInput({ inputValue, setInputValue, onSendMessage, isTyping, onKeyPress }: ChatInputProps) {
  return (
    <div style={{ 
      position: 'absolute', 
      bottom: '0', 
      left: '0', 
      right: '0', 
      backgroundColor: 'white', 
      borderTop: '1px solid #e5e7eb', 
      padding: '12px 16px',
      display: 'flex',
      alignItems: 'center',
      gap: '12px'
    }}>
      <input
        type="text"
        placeholder="Ask a question about your documents..."
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyPress={onKeyPress}
        style={{
          flex: 1,
          padding: '12px 16px',
          border: '1px solid #d1d5db',
          borderRadius: '24px',
          fontSize: '14px',
          backgroundColor: '#f9fafb',
          outline: 'none',
          transition: 'all 0.2s ease'
        }}
        onFocus={(e) => {
          e.target.style.borderColor = '#3b82f6'
          e.target.style.backgroundColor = 'white'
          e.target.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)'
        }}
        onBlur={(e) => {
          e.target.style.borderColor = '#d1d5db'
          e.target.style.backgroundColor = '#f9fafb'
          e.target.style.boxShadow = 'none'
        }}
      />
      <button 
        onClick={onSendMessage} 
        disabled={!inputValue.trim() || isTyping}
        style={{
          width: '44px',
          height: '44px',
          borderRadius: '50%',
          backgroundColor: inputValue.trim() && !isTyping ? '#3b82f6' : '#d1d5db',
          border: 'none',
          color: 'white',
          cursor: inputValue.trim() && !isTyping ? 'pointer' : 'not-allowed',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'all 0.2s ease',
          flexShrink: 0
        }}
        onMouseEnter={(e) => {
          if (inputValue.trim() && !isTyping) {
            e.currentTarget.style.backgroundColor = '#2563eb'
          }
        }}
        onMouseLeave={(e) => {
          if (inputValue.trim() && !isTyping) {
            e.currentTarget.style.backgroundColor = '#3b82f6'
          }
        }}
      >
        <i className="fas fa-paper-plane" style={{ fontSize: '16px' }}></i>
      </button>
    </div>
  )
}
