import type React from "react"
import { useState } from "react"
import type { Message } from '../types'

interface ChatMessageProps {
  message: Message
  onSourcesClick?: (sources: any[]) => void
}

export function ChatMessage({ message, onSourcesClick }: ChatMessageProps) {
  const [isCopied, setIsCopied] = useState(false)
  
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
          <div className="p-4 rounded-lg" style={{ backgroundColor: '#f3f4f6', color: '#111827' }}>
            <p className="text-sm leading-relaxed">{message.content}</p>
          </div>
          {message.sources && (
            <div style={{ marginTop: '12px' }}>
              <p style={{ fontSize: '12px', color: '#6b7280', fontWeight: '500', margin: '0 0 8px 0' }}>Sources:</p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {message.sources.map((source, index) => (
                  <div key={index} style={{ 
                    display: 'inline-flex',
                    alignItems: 'center',
                    backgroundColor: '#f1f5f9',
                    border: '1px solid #e2e8f0',
                    borderRadius: '16px',
                    padding: '4px 8px',
                    fontSize: '10px',
                    color: '#475569',
                    cursor: 'pointer'
                  }}>
                    <span style={{ fontWeight: '500' }}>{source.title}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '8px', marginTop: '12px' }}>
            <button style={{ 
              padding: '6px 8px', 
              border: '1px solid #e5e7eb', 
              borderRadius: '6px', 
              backgroundColor: 'transparent',
              color: '#6b7280',
              cursor: 'pointer',
              fontSize: '12px'
            }} onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'} onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
              <i className="far fa-thumbs-up"></i>
            </button>
            <button style={{ 
              padding: '6px 8px', 
              border: '1px solid #e5e7eb', 
              borderRadius: '6px', 
              backgroundColor: 'transparent',
              color: '#6b7280',
              cursor: 'pointer',
              fontSize: '12px'
            }} onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'} onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
              <i className="far fa-thumbs-down"></i>
            </button>
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
                border: `1px solid ${isCopied ? '#3b82f6' : '#e5e7eb'}`, 
                borderRadius: '6px', 
                backgroundColor: isCopied ? '#3b82f6' : 'transparent',
                color: isCopied ? 'white' : '#6b7280',
                cursor: 'pointer',
                fontSize: '12px',
                transition: 'all 0.3s ease'
              }} 
              onMouseEnter={(e) => {
                if (!isCopied) e.currentTarget.style.backgroundColor = '#f9fafb'
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
