import React, { useState, useEffect } from 'react';
import { Icons } from './icons';

interface ModelUsageChartProps {
  // You can pass period as prop later
}

const ModelUsageChart: React.FC<ModelUsageChartProps> = () => {
  const [loading, setLoading] = useState(true);
  const [modelData, setModelData] = useState<any>(null);

  // Model colors
  const modelColors: { [key: string]: string } = {
    'pegasus': '#3b82f6',  // blue
    'bart': '#8b5cf6',     // purple
    't5': '#ec4899',       // pink
  };

  useEffect(() => {
    fetchModelUsage();
  }, []);

  const fetchModelUsage = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/analytics/model-usage-over-time?period=30d', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setModelData(data);
      }
    } catch (error) {
      console.error('Error fetching model usage:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="chart-container" style={{ width: '50%' }}>
        <div className="chart-header">
          <h2><Icons.Activity /> Summarization Model Usage</h2>
        </div>
        <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>
          Loading...
        </div>
      </div>
    );
  }

  // Prepare data for visualization
  const models = modelData?.models || {};
  const allDates = new Set<string>();
  
  // Collect all unique dates
  Object.values(models).forEach((dataPoints: any) => {
    dataPoints.forEach((point: any) => {
      allDates.add(point.date);
    });
  });

  const sortedDates = Array.from(allDates).sort();
  
  // Create data structure with all dates for each model
  const chartData: { [key: string]: { [date: string]: number } } = {};
  Object.keys(models).forEach(model => {
    chartData[model] = {};
    sortedDates.forEach(date => {
      chartData[model][date] = 0;
    });
    models[model].forEach((point: any) => {
      chartData[model][point.date] = point.count;
    });
  });

  // Find max value for scaling
  const maxValue = Math.max(
    ...Object.values(chartData).flatMap(modelData => Object.values(modelData)),
    1
  );

  const chartHeight = 170;
  const chartWidth = 600;

  return (
    <div className="chart-container" style={{ width: '50%' }}>
      <div className="chart-header">
        <h2><Icons.Activity /> Summarization Model Usage</h2>
      </div>

      <div style={{ padding: '24px 16px', paddingBottom: '16px' }}>
        {/* Chart */}
        <div style={{ position: 'relative', height: `${chartHeight}px`, paddingLeft: '40px', paddingBottom: '30px' }}>
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
            Usage Count
          </div>

          {/* Y-axis ticks */}
          <div style={{ position: 'absolute', left: '8px', top: '0', fontSize: '0.65rem', color: '#9ca3af', fontWeight: 500 }}>{maxValue}</div>
          <div style={{ position: 'absolute', left: '8px', top: '50%', transform: 'translateY(-50%)', fontSize: '0.65rem', color: '#9ca3af', fontWeight: 500 }}>{Math.round(maxValue / 2)}</div>
          <div style={{ position: 'absolute', left: '8px', bottom: '30px', fontSize: '0.65rem', color: '#9ca3af', fontWeight: 500 }}>0</div>

          {/* Grid lines */}
          <div style={{ position: 'absolute', left: '40px', right: '0', top: '0', height: '1px', borderTop: '1px dashed #374151' }}></div>
          <div style={{ position: 'absolute', left: '40px', right: '0', top: '50%', height: '1px', borderTop: '1px dashed #374151' }}></div>
          <div style={{ position: 'absolute', left: '40px', right: '0', bottom: '30px', height: '1px', borderTop: '1px dashed #374151' }}></div>

          {/* SVG for lines */}
          <svg
            style={{
              position: 'absolute',
              left: '40px',
              top: '0',
              width: 'calc(100% - 40px)',
              height: `${chartHeight - 30}px`,
              overflow: 'hidden'
            }}
            viewBox={`0 0 ${chartWidth - 40} ${chartHeight - 30}`}
            preserveAspectRatio="none"
          >
            {Object.keys(chartData).map((model, modelIndex) => {
              const points = sortedDates.map((date, index) => {
                const value = chartData[model][date] || 0;
                const x = (index / (sortedDates.length - 1)) * (chartWidth - 40);
                const y = (chartHeight - 30) - (value / maxValue) * (chartHeight - 30);
                return { x, y, value };
              });

              // Create smooth curve path using cubic Bezier
              const pathData = points.map((point, index) => {
                if (index === 0) {
                  return `M ${point.x} ${point.y}`;
                }
                
                // Calculate control points for smooth curve
                const prevPoint = points[index - 1];
                const tension = 0.3; // Adjust this for more/less curve
                
                const dx = point.x - prevPoint.x;
                const cp1x = prevPoint.x + dx * tension;
                const cp1y = prevPoint.y;
                const cp2x = point.x - dx * tension;
                const cp2y = point.y;
                
                return `C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${point.x} ${point.y}`;
              }).join(' ');

              const color = modelColors[model] || '#64748b';

              return (
                <g key={model}>
                  {/* Line */}
                  <path
                    d={pathData}
                    fill="none"
                    stroke={color}
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  {/* Points */}
                  {points.map((point, index) => (
                    <circle
                      key={index}
                      cx={point.x}
                      cy={point.y}
                      r="4"
                      fill={color}
                      stroke="#0f172a"
                      strokeWidth="2"
                      style={{ cursor: 'pointer' }}
                    >
                      <title>{`${model}: ${point.value} on ${sortedDates[index]}`}</title>
                    </circle>
                  ))}
                </g>
              );
            })}
          </svg>

          {/* X-axis labels */}
          <div style={{
            position: 'absolute',
            left: '40px',
            bottom: '8px',
            right: '0',
            display: 'flex',
            justifyContent: 'space-between'
          }}>
            {sortedDates.length > 0 && (
              <>
                <div style={{ fontSize: '0.7rem', color: '#9ca3af', fontWeight: 500 }}>
                  {new Date(sortedDates[0]).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </div>
                {sortedDates.length > 2 && (
                  <div style={{ fontSize: '0.7rem', color: '#9ca3af', fontWeight: 500 }}>
                    {new Date(sortedDates[Math.floor(sortedDates.length / 2)]).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  </div>
                )}
                <div style={{ fontSize: '0.7rem', color: '#9ca3af', fontWeight: 500 }}>
                  {new Date(sortedDates[sortedDates.length - 1]).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </div>
              </>
            )}
          </div>
        </div>

        {/* Legend */}
        <div style={{
          display: 'flex',
          gap: '24px',
          justifyContent: 'center',
          marginTop: '8px',
          flexWrap: 'wrap'
        }}>
          {Object.keys(chartData).map(model => (
            <div key={model} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{
                width: '16px',
                height: '3px',
                background: modelColors[model] || '#64748b',
                borderRadius: '2px'
              }}></div>
              <span style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: 500, textTransform: 'capitalize' }}>
                {model}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ModelUsageChart;
