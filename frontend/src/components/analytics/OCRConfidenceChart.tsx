import React, { useState, useEffect } from 'react';
import { Icons } from './icons';

interface OCRConfidenceChartProps {
  // You can pass props later if needed
}

const OCRConfidenceChart: React.FC<OCRConfidenceChartProps> = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    fetchOCRData();
  }, []);

  const fetchOCRData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/analytics/ocr-confidence-distribution', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        setData(result);
      }
    } catch (error) {
      console.error('Error fetching OCR confidence data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="chart-container" style={{ width: '50%' }}>
        <div className="chart-header">
          <h2><Icons.Eye /> OCR Confidence Score Distribution</h2>
        </div>
        <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>
          Loading...
        </div>
      </div>
    );
  }

  const distribution = data?.distribution || {};
  const statistics = data?.statistics || {};
  
  // Check if no data available
  const hasData = statistics.total > 0;
  
  // Define categories with labels and colors
  const categories = [
    { key: 'low', label: 'Low (<50%)', color: '#ef4444', range: '0-50%' },
    { key: 'medium', label: 'Medium (50-70%)', color: '#f97316', range: '50-70%' },
    { key: 'good', label: 'Good (70-85%)', color: '#eab308', range: '70-85%' },
    { key: 'very_good', label: 'Very Good (85-95%)', color: '#22c55e', range: '85-95%' },
    { key: 'excellent', label: 'Excellent (≥95%)', color: '#3b82f6', range: '95-100%' }
  ];

  const maxCount = Math.max(...categories.map(cat => distribution[cat.key] || 0), 1);

  return (
    <div className="chart-container" style={{ width: '50%' }}>
      <div className="chart-header">
        <h2><Icons.Eye /> OCR Confidence Score Distribution</h2>
      </div>

      {!hasData ? (
        <div style={{ 
          padding: '60px 40px', 
          textAlign: 'center', 
          color: '#94a3b8',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '12px'
        }}>
          <div style={{ fontSize: '3rem', opacity: 0.3 }}>📊</div>
          <div style={{ fontSize: '1.1rem', fontWeight: 600, color: '#cbd5e1' }}>No OCR Data Available</div>
          <div style={{ fontSize: '0.9rem', maxWidth: '500px', lineHeight: '1.5' }}>
            Documents with OCR confidence scores will appear here. Upload documents with OCR processing to see the quality distribution.
          </div>
        </div>
      ) : (
        <div style={{ padding: '16px', display: 'flex', gap: '24px', alignItems: 'flex-end' }}>
        {/* Bar Chart */}
        <div style={{ flex: 1, paddingTop: '0' }}>
          <div style={{ 
            display: 'flex', 
            alignItems: 'flex-end', 
            gap: '16px',
            height: '180px',
            padding: '0 20px'
          }}>
            {categories.map((cat, index) => {
              const count = distribution[cat.key] || 0;
              const barHeight = maxCount > 0 ? (count / maxCount) * 180 : 0;
              const percentage = statistics.total > 0 ? ((count / statistics.total) * 100).toFixed(1) : 0;

              return (
                <div
                  key={cat.key}
                  style={{
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
                  {/* Bar */}
                  <div style={{ 
                    width: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'flex-end',
                    height: '180px'
                  }}>
                    {count > 0 && (
                      <div style={{
                        fontSize: '0.75rem',
                        color: '#fff',
                        fontWeight: 600,
                        marginBottom: '4px'
                      }}>
                        {count}
                      </div>
                    )}
                    <div
                      title={`${cat.label}: ${count} documents (${percentage}%)`}
                      style={{
                        width: '100%',
                        height: `${barHeight}px`,
                        background: cat.color,
                        borderRadius: '6px 6px 0 0',
                        transition: 'all 0.3s ease',
                        cursor: 'pointer',
                        border: `1px solid ${cat.color}`,
                        boxShadow: `0 0 10px ${cat.color}40`
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.filter = 'brightness(1.2)';
                        e.currentTarget.style.transform = 'scaleY(1.05)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.filter = 'brightness(1)';
                        e.currentTarget.style.transform = 'scaleY(1)';
                      }}
                    />
                  </div>

                  {/* Label */}
                  <div style={{ 
                    textAlign: 'center',
                    fontSize: '0.7rem',
                    color: '#9ca3af',
                    fontWeight: 500,
                    lineHeight: '1.2'
                  }}>
                    <div style={{ color: cat.color, fontWeight: 600 }}>{cat.range}</div>
                    <div style={{ fontSize: '0.65rem', marginTop: '2px' }}>{percentage}%</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Statistics Panel */}
        <div style={{
          width: '180px',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
          padding: '12px',
          background: '#1e293b',
          borderRadius: '8px',
          border: '2px solid #3b82f6',
          flexShrink: 0
        }}>
          <div style={{ 
            fontSize: '0.65rem', 
            color: '#94a3b8', 
            fontWeight: 500, 
            textTransform: 'uppercase',
            paddingBottom: '4px'
          }}>
            Overall Statistics
          </div>

          <div>
            <div style={{ fontSize: '0.6rem', color: '#94a3b8', marginBottom: '2px', textTransform: 'uppercase', fontWeight: 600 }}>Total Documents</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 600, color: '#ffffff' }}>
              {statistics.total || 0}
            </div>
          </div>

          <div style={{ width: '100%', height: '1px', background: '#334155' }}></div>

          <div>
            <div style={{ fontSize: '0.6rem', color: '#94a3b8', marginBottom: '2px', textTransform: 'uppercase', fontWeight: 600 }}>Average Score</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 600, color: '#3b82f6' }}>
              {statistics.average ? `${(statistics.average * 100).toFixed(1)}%` : 'N/A'}
            </div>
          </div>

          <div style={{ width: '100%', height: '1px', background: '#334155' }}></div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: '0.55rem', color: '#94a3b8', marginBottom: '2px', textTransform: 'uppercase', fontWeight: 600 }}>Min</div>
              <div style={{ fontSize: '1rem', fontWeight: 600, color: '#ef4444' }}>
                {statistics.min ? `${(statistics.min * 100).toFixed(1)}%` : 'N/A'}
              </div>
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: '0.55rem', color: '#94a3b8', marginBottom: '2px', textTransform: 'uppercase', fontWeight: 600 }}>Max</div>
              <div style={{ fontSize: '1rem', fontWeight: 600, color: '#22c55e' }}>
                {statistics.max ? `${(statistics.max * 100).toFixed(1)}%` : 'N/A'}
              </div>
            </div>
          </div>
        </div>
      </div>
      )}
    </div>
  );
};

export default OCRConfidenceChart;
