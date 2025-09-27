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
}

export function ChatInput({ inputValue, setInputValue, onSendMessage, isTyping, onKeyPress, searchMode, setSearchMode, selectedModel, setSelectedModel }: ChatInputProps) {
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
      
      {/* Model Selector */}
      <div style={{ position: 'relative' }} ref={modelDropdownRef}>
        <button
          onClick={() => setIsModelDropdownOpen(!isModelDropdownOpen)}
          style={{
            padding: '8px 12px',
            border: '1px solid #d1d5db',
            borderRadius: '20px',
            backgroundColor: 'white',
            cursor: 'pointer',
            fontSize: '12px',
            color: '#374151',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            transition: 'all 0.2s ease',
            flexShrink: 0,
            maxWidth: '140px'
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
          <span style={{ 
            width: '8px', 
            height: '8px', 
            borderRadius: '50%', 
            backgroundColor: selectedModel.provider === 'groq' ? '#10b981' : selectedModel.provider === 'deepseek' ? '#3b82f6' : selectedModel.provider === 'openai' ? '#f59e0b' : '#8b5cf6',
            flexShrink: 0
          }}></span>
          <span style={{ 
            overflow: 'hidden', 
            textOverflow: 'ellipsis', 
            whiteSpace: 'nowrap' 
          }}>
            {selectedModel.name}
          </span>
          <i className="fas fa-chevron-down" style={{ fontSize: '10px', marginLeft: 'auto' }}></i>
        </button>

        {/* Model Dropdown */}
        {isModelDropdownOpen && (
          <div style={{
            position: 'absolute',
            bottom: '100%',
            right: '0',
            marginBottom: '8px',
            backgroundColor: 'white',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
            zIndex: 1000,
            minWidth: '250px',
            maxHeight: '300px',
            overflowY: 'auto'
          }}>
            {availableModels.map((model, index) => (
              <div
                key={`${model.provider}-${model.model}`}
                onClick={() => {
                  setSelectedModel(model)
                  setIsModelDropdownOpen(false)
                }}
                style={{
                  padding: '12px 16px',
                  cursor: 'pointer',
                  fontSize: '13px',
                  color: '#374151',
                  backgroundColor: selectedModel.provider === model.provider && selectedModel.model === model.model ? '#f3f4f6' : 'transparent',
                  borderTop: index > 0 ? '1px solid #f3f4f6' : 'none',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px'
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = selectedModel.provider === model.provider && selectedModel.model === model.model ? '#f3f4f6' : 'transparent'}
              >
                <span style={{ 
                  width: '10px', 
                  height: '10px', 
                  borderRadius: '50%', 
                  backgroundColor: model.provider === 'groq' ? '#10b981' : model.provider === 'deepseek' ? '#3b82f6' : model.provider === 'openai' ? '#f59e0b' : '#8b5cf6',
                  flexShrink: 0
                }}></span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: '500', marginBottom: '2px' }}>{model.name}</div>
                  <div style={{ fontSize: '11px', color: '#6b7280' }}>
                    {model.provider.toUpperCase()} • {model.model}
                  </div>
                </div>
                {selectedModel.provider === model.provider && selectedModel.model === model.model && (
                  <i className="fas fa-check" style={{ fontSize: '12px', color: '#10b981' }}></i>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

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
