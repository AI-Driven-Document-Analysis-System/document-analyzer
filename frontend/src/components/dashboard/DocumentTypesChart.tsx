// DocumentTypesChart.tsx
import React from 'react';

interface DocumentTypeData {
  type: string;
  count: number;
  avgSize: number;
}

interface Props {
  documentTypes: DocumentTypeData[];
  formatFileSize: (bytes: number) => string;
}

const DocumentTypesChart: React.FC<Props> = ({ documentTypes, formatFileSize }) => {
  const maxTypeCount = documentTypes.length > 0 
    ? Math.max(...documentTypes.map(d => d.count)) 
    : 1;

  // Icon component
  const FileTypeIcon = () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z" />
      <path d="M14 2v6h6" />
    </svg>
  );

  return (
    <div className="doc-types-container">
      <div className="doc-types-header">
        <h2><FileTypeIcon /> Document Types</h2>
        <p>Breakdown by file type</p>
      </div>
      
      {documentTypes.length === 0 ? (
        <div style={{ height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <p style={{ color: '#6b7280' }}>No document types data available</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {documentTypes.slice(0, 8).map((item, index) => {
            const width = maxTypeCount > 0 ? (item.count / maxTypeCount) * 100 : 0;
            const blueShades = ['#3b82f6', '#2563eb', '#1d4ed8', '#1e40af', '#1e3a8a', '#172554'];
            return (
              <div key={index} className="doc-type-item">
                <div className="doc-type-label">{item.type}</div>
                <div className="type-bar-container">
                  <div 
                    style={{
                      width: `${width}%`,
                      backgroundColor: blueShades[index % blueShades.length]
                    }}
                    className="type-bar"
                    title={`${item.type}: ${item.count} files (avg: ${formatFileSize(item.avgSize)})`}
                  >
                    <span>{item.count}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default DocumentTypesChart;