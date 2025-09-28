import { useState, useEffect } from 'react'

export function TypingIndicator() {
  const [currentText, setCurrentText] = useState('')
  const [currentIndex, setCurrentIndex] = useState(0)
  
  const thinkingStates = [
    'Searching documents...',
    'Analyzing content...',
    'Generating response...',
    'Finalizing answer...'
  ]
  
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % thinkingStates.length)
    }, 1500) // Change text every 1.5 seconds
    
    return () => clearInterval(interval)
  }, [])
  
  useEffect(() => {
    setCurrentText(thinkingStates[currentIndex])
  }, [currentIndex])

  return (
    <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start', marginBottom: '16px' }}>
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
      <div style={{ 
        backgroundColor: '#f3f4f6', 
        padding: '12px 16px', 
        borderRadius: '12px',
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
      }}>
        {/* Thinking spinner */}
        <div style={{
          width: '16px',
          height: '16px',
          border: '2px solid #e5e7eb',
          borderTop: '2px solid #3b82f6',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }}></div>
        
        {/* Dynamic thinking text */}
        <span style={{ 
          color: '#6b7280', 
          fontSize: '14px',
          fontStyle: 'italic'
        }}>
          {currentText}
        </span>
        
        {/* CSS for spinner animation */}
        <style jsx>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    </div>
  )
}
