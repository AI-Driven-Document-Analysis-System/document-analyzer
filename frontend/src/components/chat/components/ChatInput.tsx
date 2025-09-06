import type React from "react"
import { useState, useEffect, useRef } from "react"

interface ChatInputProps {
  inputValue: string
  setInputValue: (value: string) => void
  onSendMessage: () => void
  isTyping: boolean
  onKeyPress: (e: React.KeyboardEvent) => void
  searchMode: 'standard' | 'rephrase' | 'multiple_queries'
  setSearchMode: (mode: 'standard' | 'rephrase' | 'multiple_queries') => void
}

export function ChatInput({ inputValue, setInputValue, onSendMessage, isTyping, onKeyPress, searchMode, setSearchMode }: ChatInputProps) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleGlobalClick = (event: MouseEvent) => {
      if (isDropdownOpen && dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false)
      }
    }

    document.addEventListener('mousedown', handleGlobalClick)
    
    return () => {
      document.removeEventListener('mousedown', handleGlobalClick)
    }
  }, [isDropdownOpen])
  return (
    <div style={{ 
      position: 'absolute', 
      bottom: '0', 
      left: '0', 
      right: '0', 
      backgroundColor: 'white', 
      borderTop: '1px solid #e5e7eb', 
      padding: '12px 16px'
    }}>
      {/* Search Mode Selector */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '8px', 
        marginBottom: '8px',
        fontSize: '12px',
        color: '#6b7280',
        position: 'relative'
      }}>
        <span style={{ fontWeight: '500', color: '#374151' }}>Search mode:</span>
        <div ref={dropdownRef} style={{ position: 'relative' }}>
          <button
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            style={{
              padding: '4px 8px 4px 8px',
              paddingRight: '24px',
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              fontSize: '12px',
              backgroundColor: 'white',
              color: '#374151',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              minWidth: '140px',
              textAlign: 'left'
            }}
          >
            {searchMode === 'standard' ? 'Standard search' : 
             searchMode === 'rephrase' ? 'Enhanced search - Rephrase' : 
             'Enhanced search - Multiple queries'}
          </button>
          
          {isDropdownOpen && (
            <div style={{
              position: 'absolute',
              bottom: '100%',
              left: '0',
              marginBottom: '4px',
              backgroundColor: 'white',
              border: '1px solid #d1d5db',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              zIndex: 1000,
              minWidth: '280px'
            }}>
              <div
                onClick={() => {
                  setSearchMode('standard')
                  setIsDropdownOpen(false)
                }}
                style={{
                  padding: '8px 12px',
                  cursor: 'pointer',
                  fontSize: '12px',
                  color: '#374151',
                  backgroundColor: searchMode === 'standard' ? '#f3f4f6' : 'transparent'
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = searchMode === 'standard' ? '#f3f4f6' : 'transparent'}
              >
                <div style={{ fontWeight: '500', marginBottom: '2px' }}>Standard search</div>
                <div style={{ fontSize: '10px', color: '#6b7280', lineHeight: '1.2' }}>
                  Faster response, suitable for most general tasks
                </div>
              </div>
              <div
                onClick={() => {
                  setSearchMode('rephrase')
                  setIsDropdownOpen(false)
                }}
                style={{
                  padding: '8px 12px',
                  cursor: 'pointer',
                  fontSize: '12px',
                  color: '#374151',
                  backgroundColor: searchMode === 'rephrase' ? '#f3f4f6' : 'transparent',
                  borderTop: '1px solid #e5e7eb'
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = searchMode === 'rephrase' ? '#f3f4f6' : 'transparent'}
              >
                <div style={{ fontWeight: '500', marginBottom: '2px' }}>Enhanced search - Rephrase</div>
                <div style={{ fontSize: '10px', color: '#6b7280', lineHeight: '1.2' }}>
                  Better clarity for unclear questions (adds ~1-3 seconds)
                </div>
              </div>
              <div
                onClick={() => {
                  setSearchMode('multiple_queries')
                  setIsDropdownOpen(false)
                }}
                style={{
                  padding: '8px 12px',
                  cursor: 'pointer',
                  fontSize: '12px',
                  color: '#374151',
                  backgroundColor: searchMode === 'multiple_queries' ? '#f3f4f6' : 'transparent',
                  borderTop: '1px solid #e5e7eb'
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = searchMode === 'multiple_queries' ? '#f3f4f6' : 'transparent'}
              >
                <div style={{ fontWeight: '500', marginBottom: '2px' }}>Enhanced search - Multiple queries</div>
                <div style={{ fontSize: '10px', color: '#6b7280', lineHeight: '1.2' }}>
                  Comprehensive answers for complex topics (adds ~3-8 seconds)
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Input Area */}
      <div style={{
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
          cursor: inputValue.trim() && !isTyping ? 'pointer' : 'default',
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
    </div>
  )
}
