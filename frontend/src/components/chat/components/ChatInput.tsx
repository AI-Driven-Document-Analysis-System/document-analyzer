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
  selectedModel: { provider: string; model: string; name: string }
  setSelectedModel: (model: { provider: string; model: string; name: string }) => void
  isDarkMode?: boolean
}

export function ChatInput({ inputValue, setInputValue, onSendMessage, isTyping, onKeyPress, searchMode, setSearchMode, selectedModel, setSelectedModel, isDarkMode = false }: ChatInputProps) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const [isModelDropdownOpen, setIsModelDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const modelDropdownRef = useRef<HTMLDivElement>(null)

  // Available models
  const availableModels = [
    { provider: 'groq', model: 'llama-3.1-8b-instant', name: 'Groq Llama 3.1 8B' },
    { provider: 'deepseek', model: 'deepseek-chat', name: 'DeepSeek Chat' }
  ]

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleGlobalClick = (event: MouseEvent) => {
      if (isDropdownOpen && dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false)
      }
      if (isModelDropdownOpen && modelDropdownRef.current && !modelDropdownRef.current.contains(event.target as Node)) {
        setIsModelDropdownOpen(false)
      }
    }

    document.addEventListener('mousedown', handleGlobalClick)
    
    return () => {
      document.removeEventListener('mousedown', handleGlobalClick)
    }
  }, [isDropdownOpen, isModelDropdownOpen])
  return (
    <div style={{ 
      position: 'absolute', 
      bottom: '0', 
      left: '0', 
      right: '0', 
      backgroundColor: isDarkMode ? '#2d3748' : 'white', 
      borderTop: `1px solid ${isDarkMode ? '#4a5568' : '#e5e7eb'}`, 
      padding: '12px 16px'
    }}>
      {/* Top Row: Search Mode and Model Selector */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        marginBottom: '8px',
        fontSize: '12px',
        color: isDarkMode ? '#9ca3af' : '#6b7280',
        position: 'relative'
      }}>
        {/* Search Mode Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontWeight: '500', color: isDarkMode ? '#f9fafb' : '#374151' }}>Search mode:</span>
        <div ref={dropdownRef} style={{ position: 'relative' }}>
          <button
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            style={{
              padding: '4px 8px 4px 8px',
              paddingRight: '24px',
              border: `1px solid ${isDarkMode ? '#4b5563' : '#d1d5db'}`,
              borderRadius: '6px',
              fontSize: '12px',
              backgroundColor: isDarkMode ? '#374151' : 'white',
              color: isDarkMode ? '#f9fafb' : '#374151',
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
              backgroundColor: isDarkMode ? '#374151' : 'white',
              border: `1px solid ${isDarkMode ? '#4b5563' : '#d1d5db'}`,
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
                  color: isDarkMode ? '#f9fafb' : '#374151',
                  backgroundColor: searchMode === 'standard' ? (isDarkMode ? '#4b5563' : '#f3f4f6') : 'transparent'
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = isDarkMode ? '#4b5563' : '#f9fafb'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = searchMode === 'standard' ? (isDarkMode ? '#4b5563' : '#f3f4f6') : 'transparent'}
              >
                <div style={{ fontWeight: '500', marginBottom: '2px' }}>Standard search</div>
                <div style={{ fontSize: '10px', color: isDarkMode ? '#9ca3af' : '#6b7280', lineHeight: '1.2' }}>
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
                  color: isDarkMode ? '#f9fafb' : '#374151',
                  backgroundColor: searchMode === 'rephrase' ? (isDarkMode ? '#4b5563' : '#f3f4f6') : 'transparent',
                  borderTop: `1px solid ${isDarkMode ? '#4b5563' : '#e5e7eb'}`
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = isDarkMode ? '#4b5563' : '#f9fafb'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = searchMode === 'rephrase' ? (isDarkMode ? '#4b5563' : '#f3f4f6') : 'transparent'}
              >
                <div style={{ fontWeight: '500', marginBottom: '2px' }}>Enhanced search - Rephrase</div>
                <div style={{ fontSize: '10px', color: isDarkMode ? '#9ca3af' : '#6b7280', lineHeight: '1.2' }}>
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
                  color: isDarkMode ? '#f9fafb' : '#374151',
                  backgroundColor: searchMode === 'multiple_queries' ? (isDarkMode ? '#4b5563' : '#f3f4f6') : 'transparent',
                  borderTop: `1px solid ${isDarkMode ? '#4b5563' : '#e5e7eb'}`
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = isDarkMode ? '#4b5563' : '#f9fafb'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = searchMode === 'multiple_queries' ? (isDarkMode ? '#4b5563' : '#f3f4f6') : 'transparent'}
              >
                <div style={{ fontWeight: '500', marginBottom: '2px' }}>Enhanced search - Multiple queries</div>
                <div style={{ fontSize: '10px', color: isDarkMode ? '#9ca3af' : '#6b7280', lineHeight: '1.2' }}>
                  Comprehensive answers for complex topics (adds ~3-8 seconds)
                </div>
              </div>
            </div>
          )}
          </div>
        </div>
        
        {/* Model Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontWeight: '500', color: isDarkMode ? '#e2e8f0' : '#374151' }}>Model:</span>
          <div style={{ position: 'relative' }} ref={modelDropdownRef}>
            <button
              onClick={() => setIsModelDropdownOpen(!isModelDropdownOpen)}
              style={{
                padding: '4px 8px',
                paddingRight: '24px',
                border: `1px solid ${isDarkMode ? '#4b5563' : '#d1d5db'}`,
                borderRadius: '6px',
                fontSize: '12px',
                backgroundColor: isDarkMode ? '#475569' : 'white',
                color: isDarkMode ? '#f1f5f9' : '#374151',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                minWidth: '120px',
                textAlign: 'left'
              }}
            >
              <span style={{ 
                width: '6px', 
                height: '6px', 
                borderRadius: '50%', 
                backgroundColor: selectedModel.provider === 'groq' ? '#10b981' : '#3b82f6',
                flexShrink: 0
              }}></span>
              <span style={{ 
                overflow: 'hidden', 
                textOverflow: 'ellipsis', 
                whiteSpace: 'nowrap',
                flex: 1
              }}>
                {selectedModel.provider === 'groq' ? 'Groq' : 'DeepSeek'}
              </span>
            </button>

            {/* Model Dropdown */}
            {isModelDropdownOpen && (
              <div style={{
                position: 'absolute',
                bottom: '100%',
                right: '0',
                marginBottom: '4px',
                backgroundColor: isDarkMode ? '#374151' : 'white',
                border: `1px solid ${isDarkMode ? '#4b5563' : '#d1d5db'}`,
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                zIndex: 1000,
                minWidth: '200px'
              }}>
                {availableModels.map((model, index) => (
                  <div
                    key={`${model.provider}-${model.model}`}
                    onClick={() => {
                      setSelectedModel(model)
                      setIsModelDropdownOpen(false)
                    }}
                    style={{
                      padding: '8px 12px',
                      cursor: 'pointer',
                      fontSize: '12px',
                      color: isDarkMode ? '#f9fafb' : '#374151',
                      backgroundColor: selectedModel.provider === model.provider ? (isDarkMode ? '#4b5563' : '#f3f4f6') : 'transparent',
                      borderTop: index > 0 ? `1px solid ${isDarkMode ? '#4b5563' : '#e5e7eb'}` : 'none',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = isDarkMode ? '#4b5563' : '#f9fafb'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = selectedModel.provider === model.provider ? (isDarkMode ? '#4b5563' : '#f3f4f6') : 'transparent'}
                  >
                    <span style={{ 
                      width: '8px', 
                      height: '8px', 
                      borderRadius: '50%', 
                      backgroundColor: model.provider === 'groq' ? '#10b981' : '#3b82f6',
                      flexShrink: 0
                    }}></span>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: '500', marginBottom: '2px' }}>{model.provider === 'groq' ? 'Groq' : 'DeepSeek'}</div>
                      <div style={{ fontSize: '10px', color: isDarkMode ? '#9ca3af' : '#6b7280', lineHeight: '1.2' }}>
                        {model.provider === 'groq' ? 'Fast responses, free tier' : 'High quality, reliable'}
                      </div>
                    </div>
                    {selectedModel.provider === model.provider && (
                      <i className="fas fa-check" style={{ fontSize: '10px', color: '#10b981' }}></i>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
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
          border: `1px solid ${isDarkMode ? '#4a5568' : '#d1d5db'}`,
          borderRadius: '8px',
          fontSize: '14px',
          backgroundColor: isDarkMode ? '#374151' : '#f9fafb',
          color: isDarkMode ? '#e2e8f0' : '#374151',
          outline: 'none',
          transition: 'all 0.2s ease'
        }}
        onFocus={(e) => {
          e.target.style.borderColor = '#3b82f6'
          e.target.style.backgroundColor = isDarkMode ? '#4a5568' : 'white'
          e.target.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)'
        }}
        onBlur={(e) => {
          e.target.style.borderColor = isDarkMode ? '#4a5568' : '#d1d5db'
          e.target.style.backgroundColor = isDarkMode ? '#374151' : '#f9fafb'
          e.target.style.boxShadow = 'none'
        }}
        />
        
        <button 
        onClick={onSendMessage} 
        disabled={!inputValue.trim() || isTyping}
        style={{
          width: '44px',
          height: '44px',
          borderRadius: '8px',
          backgroundColor: inputValue.trim() && !isTyping ? '#3b82f6' : '#93c5fd',
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
