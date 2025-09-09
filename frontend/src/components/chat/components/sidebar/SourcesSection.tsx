import type { ExpandedSections } from '../../types'

interface SourcesSectionProps {
  expandedSections: ExpandedSections
  toggleSection: (section: keyof ExpandedSections) => void
  selectedMessageSources: any[]
}

export function SourcesSection({ expandedSections, toggleSection, selectedMessageSources }: SourcesSectionProps) {
  return (
    <div style={{ borderBottom: '1px solid #4b5563', flexShrink: 0 }}>
      <div 
        style={{ padding: '16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', transition: 'background-color 0.2s' }}
        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#374151'}
        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
        onClick={() => toggleSection('sources')}
      >
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <i className="fas fa-book" style={{ color: '#60a5fa', marginRight: '8px' }}></i>
          <div>
            <h3 style={{ fontWeight: '500', color: 'white', margin: 0 }}>Sources</h3>
            <p style={{ fontSize: '12px', color: '#d1d5db', margin: '2px 0 0 0' }}>Documents used for responses</p>
          </div>
        </div>
        <i className={`fas ${expandedSections.sources ? 'fa-chevron-up' : 'fa-chevron-down'}`} style={{ color: '#d1d5db' }}></i>
      </div>
      {expandedSections.sources && (
        <div style={{ padding: '16px' }}>
          <p style={{ fontSize: '12px', color: '#d1d5db', margin: '0 0 12px 0' }}>Double-click on assistant chat responses to view sources</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {selectedMessageSources.length > 0 ? (
              selectedMessageSources.map((source, index) => (
                <div key={index} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', backgroundColor: '#374151', borderRadius: '6px' }}>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <i className={
                      source.title.toLowerCase().includes('.pdf') ? 'fas fa-file-pdf' : 
                      source.title.toLowerCase().includes('.xlsx') ? 'fas fa-file-excel' : 
                      'fas fa-file-alt'
                    } style={{ 
                      color: source.title.toLowerCase().includes('.pdf') ? '#ef4444' : 
                             source.title.toLowerCase().includes('.xlsx') ? '#10b981' : 
                             '#3b82f6', 
                      marginRight: '8px' 
                    }}></i>
                    <div>
                      <p style={{ fontSize: '12px', fontWeight: '500', color: 'white', margin: 0 }}>{source.title}</p>
                      <p style={{ fontSize: '10px', color: '#d1d5db', margin: 0 }}>{source.type}</p>
                    </div>
                  </div>
                  <span style={{ fontSize: '10px', backgroundColor: '#10b981', color: 'white', padding: '2px 6px', borderRadius: '10px' }}>{source.confidence}%</span>
                </div>
              ))
            ) : (
              <div style={{ textAlign: 'center', padding: '20px', color: '#9ca3af' }}>
                <i className="fas fa-info-circle" style={{ fontSize: '24px', marginBottom: '8px' }}></i>
                <p style={{ fontSize: '12px', margin: 0 }}>No sources for this response</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
