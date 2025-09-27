import type React from "react"
import { useState, useEffect, useRef } from "react"
import type { Message } from '../types'
import { MarkdownRenderer } from './MarkdownRenderer'

interface ChatMessageProps {
  message: Message
  onSourcesClick: (sources: any[]) => void
  onFeedback: (messageId: string, feedback: 'thumbs_up' | 'thumbs_down', reason?: string) => void
  onRephrasedQueryClick?: (query: string) => void
  onRegenerateAnswer?: (messageId: string, method: 'rephrase' | 'multiple_queries') => void
  isDarkMode?: boolean
}

export function ChatMessage({ message, onSourcesClick, onFeedback, onRephrasedQueryClick, onRegenerateAnswer, isDarkMode = false }: ChatMessageProps) {
  const [isCopied, setIsCopied] = useState(false)
  const [showFeedbackDropdown, setShowFeedbackDropdown] = useState(false)
  const feedbackDropdownRef = useRef<HTMLDivElement>(null)

  // Close feedback dropdown when clicking outside
  useEffect(() => {
    const handleGlobalClick = (event: MouseEvent) => {
      if (showFeedbackDropdown && feedbackDropdownRef.current && !feedbackDropdownRef.current.contains(event.target as Node)) {
        setShowFeedbackDropdown(false)
      }
    }

    document.addEventListener('mousedown', handleGlobalClick)
    
    return () => {
      document.removeEventListener('mousedown', handleGlobalClick)
    }
  }, [showFeedbackDropdown])
  
  if (message.type === "assistant") {
    return (
      <div 
        style={{ display: 'flex', gap: '12px', alignItems: 'flex-start', marginBottom: '16px', cursor: 'pointer' }}
        onDoubleClick={() => {
          if (message.sources && onSourcesClick) {
            onSourcesClick(message.sources);
          }
        }}
      >
        <div style={{ 
          width: '40px', 
          height: '40px', 
          borderRadius: '50%', 
          backgroundColor: '#3b82f6', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          flexShrink: 0,
          color: 'white'
        }}>
          <i className="fas fa-robot" style={{ fontSize: '16px' }}></i>
        </div>
        <div className="max-w-[80%]">
          <div className="p-4 rounded-lg" style={{ backgroundColor: isDarkMode ? '#4a5568' : '#f3f4f6', color: isDarkMode ? '#f7fafc' : '#111827', border: isDarkMode ? '1px solid #718096' : 'none' }}>
            <div className="text-sm leading-relaxed">
              <MarkdownRenderer content={message.content} isDarkMode={isDarkMode} />
            </div>
          </div>
          {message.sources && message.sources.length > 0 && (
            <div style={{ marginTop: '12px' }}>
              <p style={{ fontSize: '12px', color: isDarkMode ? '#9ca3af' : '#6b7280', fontWeight: '500', margin: '0 0 8px 0' }}>Sources:</p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {message.sources.map((source, index) => (
                  <div key={index} style={{ 
                    display: 'inline-flex',
                    alignItems: 'center',
                    backgroundColor: isDarkMode ? '#4a5568' : '#f1f5f9',
                    border: `1px solid ${isDarkMode ? '#718096' : '#e2e8f0'}`,
                    borderRadius: '16px',
                    padding: '4px 8px',
                    fontSize: '10px',
                    color: isDarkMode ? '#f7fafc' : '#475569',
                    cursor: 'pointer'
                  }}>
                    <span style={{ fontWeight: '500' }}>{source.title}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '8px', marginTop: '12px', position: 'relative' }}>
            <button 
              onClick={() => onFeedback?.(message.id || '', 'thumbs_up')}
              style={{ 
                padding: '6px 8px', 
                border: `1px solid ${isDarkMode ? '#718096' : '#e5e7eb'}`, 
                borderRadius: '6px', 
                backgroundColor: 'transparent',
                color: isDarkMode ? '#9ca3af' : '#6b7280',
                cursor: 'pointer',
                fontSize: '12px'
              }} 
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = isDarkMode ? '#4a5568' : '#f9fafb'} 
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
            >
              <i className="far fa-thumbs-up"></i>
            </button>
            <div ref={feedbackDropdownRef} style={{ position: 'relative' }}>
              <button 
                onClick={() => setShowFeedbackDropdown(!showFeedbackDropdown)}
                style={{ 
                  padding: '6px 8px', 
                  border: `1px solid ${isDarkMode ? '#718096' : '#e5e7eb'}`, 
                  borderRadius: '6px', 
                  backgroundColor: showFeedbackDropdown ? (isDarkMode ? '#4a5568' : '#f3f4f6') : 'transparent',
                  color: isDarkMode ? '#9ca3af' : '#6b7280',
                  cursor: 'pointer',
                  fontSize: '12px'
                }} 
                onMouseEnter={(e) => {
                  if (!showFeedbackDropdown) e.currentTarget.style.backgroundColor = isDarkMode ? '#4a5568' : '#f9fafb'
                }} 
                onMouseLeave={(e) => {
                  if (!showFeedbackDropdown) e.currentTarget.style.backgroundColor = 'transparent'
                }}
              >
                <i className="far fa-thumbs-down"></i>
              </button>
              {showFeedbackDropdown && (
                <div style={{
                  position: 'absolute',
                  bottom: '100%',
                  right: '0',
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
                      onFeedback?.(message.id || '', 'thumbs_down', 'not_relevant')
                      onRegenerateAnswer?.(message.id || '', 'rephrase')
                      setShowFeedbackDropdown(false)
                    }}
                    style={{
                      padding: '8px 12px',
                      cursor: 'pointer',
                      fontSize: '12px',
                      color: '#374151',
                      backgroundColor: 'transparent'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                  >
                    <div style={{ fontWeight: '500', marginBottom: '2px' }}>Answer wasn't relevant</div>
                    <div style={{ fontSize: '10px', color: '#6b7280', lineHeight: '1.2' }}>
                      Try Rephrase for better relevance
                    </div>
                  </div>
                  <div
                    onClick={() => {
                      onFeedback?.(message.id || '', 'thumbs_down', 'not_factually_correct')
                      onRegenerateAnswer?.(message.id || '', 'multiple_queries')
                      setShowFeedbackDropdown(false)
                    }}
                    style={{
                      padding: '8px 12px',
                      cursor: 'pointer',
                      fontSize: '12px',
                      color: '#374151',
                      backgroundColor: 'transparent',
                      borderTop: '1px solid #e5e7eb'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                  >
                    <div style={{ fontWeight: '500', marginBottom: '2px' }}>Not factually correct</div>
                    <div style={{ fontSize: '10px', color: '#6b7280', lineHeight: '1.2' }}>
                      Try Multiple queries for verified facts
                    </div>
                  </div>
                  <div
                    onClick={() => {
                      onFeedback?.(message.id || '', 'thumbs_down', 'incomplete_response')
                      onRegenerateAnswer?.(message.id || '', 'multiple_queries')
                      setShowFeedbackDropdown(false)
                    }}
                    style={{
                      padding: '8px 12px',
                      cursor: 'pointer',
                      fontSize: '12px',
                      color: '#374151',
                      backgroundColor: 'transparent',
                      borderTop: '1px solid #e5e7eb'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                  >
                    <div style={{ fontWeight: '500', marginBottom: '2px' }}>Incomplete response</div>
                    <div style={{ fontSize: '10px', color: '#6b7280', lineHeight: '1.2' }}>
                      Try Multiple queries for comprehensive coverage
                    </div>
                  </div>
                  <div
                    onClick={() => {
                      onFeedback?.(message.id || '', 'thumbs_down', 'missing_info')
                      onRegenerateAnswer?.(message.id || '', 'multiple_queries')
                      setShowFeedbackDropdown(false)
                    }}
                    style={{
                      padding: '8px 12px',
                      cursor: 'pointer',
                      fontSize: '12px',
                      color: '#374151',
                      backgroundColor: 'transparent',
                      borderTop: '1px solid #e5e7eb'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                  >
                    <div style={{ fontWeight: '500', marginBottom: '2px' }}>Missing important information</div>
                    <div style={{ fontSize: '10px', color: '#6b7280', lineHeight: '1.2' }}>
                      Try Multiple queries for complete details
                    </div>
                  </div>
                  <div
                    onClick={() => {
                      onFeedback?.(message.id || '', 'thumbs_down', 'too_general')
                      onRegenerateAnswer?.(message.id || '', 'multiple_queries')
                      setShowFeedbackDropdown(false)
                    }}
                    style={{
                      padding: '8px 12px',
                      cursor: 'pointer',
                      fontSize: '12px',
                      color: '#374151',
                      backgroundColor: 'transparent',
                      borderTop: '1px solid #e5e7eb'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                  >
                    <div style={{ fontWeight: '500', marginBottom: '2px' }}>Answer was too general</div>
                    <div style={{ fontSize: '10px', color: '#6b7280', lineHeight: '1.2' }}>
                      Try Multiple queries for specific details
                    </div>
                  </div>
                  <div
                    onClick={() => {
                      onFeedback?.(message.id || '', 'thumbs_down', 'complex_topic')
                      onRegenerateAnswer?.(message.id || '', 'multiple_queries')
                      setShowFeedbackDropdown(false)
                    }}
                    style={{
                      padding: '8px 12px',
                      cursor: 'pointer',
                      fontSize: '12px',
                      color: '#374151',
                      backgroundColor: 'transparent',
                      borderTop: '1px solid #e5e7eb'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                  >
                    <div style={{ fontWeight: '500', marginBottom: '2px' }}>Topic needs deeper analysis</div>
                    <div style={{ fontSize: '10px', color: '#6b7280', lineHeight: '1.2' }}>
                      Try Multiple queries for comprehensive analysis
                    </div>
                  </div>
                  <div
                    onClick={() => {
                      onFeedback?.(message.id || '', 'thumbs_down', 'technical_issue')
                      setShowFeedbackDropdown(false)
                    }}
                    style={{
                      padding: '8px 12px',
                      cursor: 'pointer',
                      fontSize: '12px',
                      color: '#374151',
                      backgroundColor: 'transparent',
                      borderTop: '1px solid #e5e7eb'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                  >
                    <div style={{ fontWeight: '500', marginBottom: '2px' }}>Technical issue</div>
                    <div style={{ fontSize: '10px', color: '#6b7280', lineHeight: '1.2' }}>
                      System or performance problem
                    </div>
                  </div>
                </div>
              )}
            </div>
            <button 
              onClick={() => {
                navigator.clipboard.writeText(message.content).then(() => {
                  setIsCopied(true);
                  setTimeout(() => setIsCopied(false), 1000);
                }).catch(err => {
                  console.error('Failed to copy text: ', err);
                });
              }}
              style={{ 
                padding: '6px 8px', 
                border: `1px solid ${isCopied ? '#3b82f6' : (isDarkMode ? '#718096' : '#e5e7eb')}`, 
                borderRadius: '6px', 
                backgroundColor: isCopied ? '#3b82f6' : 'transparent',
                color: isCopied ? 'white' : (isDarkMode ? '#9ca3af' : '#6b7280'),
                cursor: 'pointer',
                fontSize: '12px',
                transition: 'all 0.3s ease'
              }} 
              onMouseEnter={(e) => {
                if (!isCopied) e.currentTarget.style.backgroundColor = isDarkMode ? '#4a5568' : '#f9fafb'
              }} 
              onMouseLeave={(e) => {
                if (!isCopied) e.currentTarget.style.backgroundColor = 'transparent'
              }}
              title="Copy message"
            >
              <i className={isCopied ? "fas fa-check" : "far fa-copy"}></i>
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div style={{ width: '100%', display: 'flex', justifyContent: 'flex-end', marginBottom: '16px' }}>
      <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-end', maxWidth: '70%' }}>
        <div style={{ 
          backgroundColor: '#3b82f6', 
          color: 'white', 
          padding: '12px 16px', 
          borderRadius: '18px',
          maxWidth: '100%',
          wordWrap: 'break-word'
        }}>
          <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.5' }}>{message.content}</p>
        </div>
        <div style={{ 
          width: '40px', 
          height: '40px', 
          borderRadius: '50%', 
          backgroundColor: '#6b7280', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          flexShrink: 0,
          color: 'white'
        }}>
          <i className="fas fa-user" style={{ fontSize: '16px' }}></i>
        </div>
      </div>
    </div>
  )
}
