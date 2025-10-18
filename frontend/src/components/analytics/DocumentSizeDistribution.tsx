import React from 'react';
import { Icons } from './icons';

interface DocumentSizeDistributionProps {
  // We'll use mock data for now, but you can pass real data later
}

const DocumentSizeDistribution: React.FC<DocumentSizeDistributionProps> = () => {
  // Individual document sizes in KB (continuous data for histogram)
  const documentSizesKB = [
    45, 67, 89, 123, 156, 234, 289, 345, 456, 567, 678, 789, 890, 
    1023, 1234, 1456, 1678, 1890, 2345, 2678, 3456, 4567, 5678, 
    6789, 7890, 8901, 9012, 10234, 11456, 12678, 13890, 15234,
    234, 345, 456, 567, 678, 789, 890, 1023, 1234
  ];

  // Convert to MB for display
  const documentSizes = documentSizesKB.map(kb => kb / 1024);

  // Create histogram bins (automatic binning)
  const numBins = 20;
  const minSize = Math.min(...documentSizes);
  const maxSize = Math.max(...documentSizes);
  const binWidth = (maxSize - minSize) / numBins;

  // Calculate frequency for each bin
  const bins = Array.from({ length: numBins }, (_, i) => {
    const binStart = minSize + i * binWidth;
    const binEnd = binStart + binWidth;
    const count = documentSizes.filter(size => size >= binStart && size < binEnd).length;
    return { binStart, binEnd, count };
  });

  const maxCount = Math.max(...bins.map(b => b.count));

  return (
    <div className="chart-container" style={{ width: '50%' }}>
      <div className="chart-header">
        <h2><Icons.BarChart /> Document Size Distribution</h2>
      </div>

      <div style={{ padding: '24px 16px', paddingBottom: '16px' }}>
        {/* Histogram */}
        <div style={{ 
          display: 'flex', 
          alignItems: 'flex-end', 
          gap: '0',
          height: '130px',
          position: 'relative',
          paddingLeft: '40px'
        }}>
          {/* Y-axis label */}
          <div style={{
            position: 'absolute',
            left: '-8px',
            top: '50%',
            transform: 'translateY(-50%) rotate(-90deg)',
            transformOrigin: 'center',
            fontSize: '0.75rem',
            color: '#9ca3af',
            fontWeight: 600,
            whiteSpace: 'nowrap'
          }}>
            Frequency
          </div>

          {/* Y-axis ticks */}
          <div style={{ position: 'absolute', left: '8px', top: '0', fontSize: '0.65rem', color: '#9ca3af', fontWeight: 500 }}>{maxCount}</div>
          <div style={{ position: 'absolute', left: '8px', top: '50%', transform: 'translateY(-50%)', fontSize: '0.65rem', color: '#9ca3af', fontWeight: 500 }}>{Math.round(maxCount / 2)}</div>
          <div style={{ position: 'absolute', left: '8px', bottom: '0', fontSize: '0.65rem', color: '#9ca3af', fontWeight: 500 }}>0</div>

          {/* Grid lines */}
          <div style={{ position: 'absolute', left: '40px', right: '0', top: '0', height: '1px', borderTop: '1px dashed #374151' }}></div>
          <div style={{ position: 'absolute', left: '40px', right: '0', top: '50%', height: '1px', borderTop: '1px dashed #374151' }}></div>
          <div style={{ position: 'absolute', left: '40px', right: '0', bottom: '0', height: '1px', borderTop: '1px dashed #374151' }}></div>

          {/* Histogram bars */}
          {bins.map((bin, index) => {
            const barHeight = maxCount > 0 ? (bin.count / maxCount) * 130 : 0;
            // Blue gradient from light to dark
            const lightness = 70 - (index / bins.length) * 30; // 70% to 40%
            const color = `hsl(210, 80%, ${lightness}%)`;
            
            return (
              <div
                key={index}
                style={{
                  flex: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'flex-end',
                  height: '100%'
                }}
              >
                {/* Bar */}
                <div
                  title={`${bin.binStart.toFixed(2)} - ${bin.binEnd.toFixed(2)} MB: ${bin.count} documents`}
                  style={{
                    width: '100%',
                    height: `${barHeight}px`,
                    background: color,
                    borderRadius: '0',
                    transition: 'all 0.3s ease',
                    cursor: 'pointer',
                    position: 'relative',
                    border: '1px solid #1e293b',
                    borderBottom: 'none',
                    margin: '0',
                    boxSizing: 'border-box'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.filter = 'brightness(1.2)';
                    e.currentTarget.style.transform = 'scaleY(1.02)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.filter = 'brightness(1)';
                    e.currentTarget.style.transform = 'scaleY(1)';
                  }}
                >
                  {/* Count label on top of bar */}
                  {bin.count > 0 && barHeight > 20 && (
                    <div style={{
                      position: 'absolute',
                      top: '-20px',
                      left: '50%',
                      transform: 'translateX(-50%)',
                      fontSize: '0.65rem',
                      fontWeight: 600,
                      color: '#ffffff',
                      whiteSpace: 'nowrap'
                    }}>
                      {bin.count}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* X-axis labels - show only first, middle, and last */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginTop: '16px',
          paddingLeft: '40px',
          position: 'relative'
        }}>
          <div style={{ fontSize: '0.7rem', color: '#9ca3af', fontWeight: 500 }}>
            {minSize.toFixed(2)} MB
          </div>
          <div style={{ fontSize: '0.7rem', color: '#9ca3af', fontWeight: 500 }}>
            {((minSize + maxSize) / 2).toFixed(2)} MB
          </div>
          <div style={{ fontSize: '0.7rem', color: '#9ca3af', fontWeight: 500 }}>
            {maxSize.toFixed(2)} MB
          </div>
        </div>

        {/* X-axis label */}
        <div style={{
          textAlign: 'center',
          marginTop: '8px',
          fontSize: '0.75rem',
          color: '#9ca3af',
          fontWeight: 600
        }}>
          Document Size (MB)
        </div>
      </div>
    </div>
  );
};

export default DocumentSizeDistribution;
