export function TypingIndicator() {
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
      <div style={{ backgroundColor: '#f3f4f6', padding: '16px', borderRadius: '12px' }}>
        <div style={{ display: 'flex', gap: '4px' }}>
          <div style={{ width: '8px', height: '8px', backgroundColor: '#9ca3af', borderRadius: '50%', animation: 'bounce 1.4s infinite ease-in-out' }}></div>
          <div style={{ width: '8px', height: '8px', backgroundColor: '#9ca3af', borderRadius: '50%', animation: 'bounce 1.4s infinite ease-in-out', animationDelay: '0.16s' }}></div>
          <div style={{ width: '8px', height: '8px', backgroundColor: '#9ca3af', borderRadius: '50%', animation: 'bounce 1.4s infinite ease-in-out', animationDelay: '0.32s' }}></div>
        </div>
      </div>
    </div>
  )
}
