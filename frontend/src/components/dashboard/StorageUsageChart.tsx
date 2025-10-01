import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faDatabase, faExclamationTriangle } from '@fortawesome/free-solid-svg-icons';
import './StorageUsageChart.css';

interface StorageUsageChartProps {
  used: number; // in MB
  total: number; // in MB (default 2GB = 2048MB)
  loading?: boolean;
  error?: string | null;
  isMockData?: boolean;
}

const StorageUsageChart: React.FC<StorageUsageChartProps> = ({ 
  used, 
  total = 2048,
  loading = false,
  error = null,
  isMockData = false
}) => {
  const remaining = Math.max(0, total - used);
  const usedPercentage = total > 0 ? Math.round((used / total) * 100) : 0;
  
  const data = [
    { name: 'Used', value: used, color: '#4f46e5' },
    { name: 'Remaining', value: remaining, color: '#e2e8f0' },
  ];

  const formatBytes = (bytes: number, decimals = 2) => {
    if (bytes === 0) return '0 MB';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
  };

  // Loading state
  if (loading) {
    return (
      <div style={{
        flex: 1,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '250px',
        backgroundColor: '#fff',
        borderRadius: '8px',
        padding: '20px'
      }}>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          color: '#4f46e5',
          textAlign: 'center'
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            border: '4px solid #e2e8f0',
            borderTop: '4px solid #4f46e5',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            marginBottom: '12px'
          }}></div>
          <p style={{ margin: 0, color: '#4b5563' }}>Loading storage data...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '250px',
        backgroundColor: '#fff',
        borderRadius: '8px',
        padding: '20px',
        textAlign: 'center',
        color: '#ef4444'
      }}>
        <FontAwesomeIcon 
          icon={faExclamationTriangle} 
          style={{ fontSize: '2rem', marginBottom: '12px' }} 
        />
        <p style={{ margin: '0 0 8px', fontWeight: 500 }}>Error loading storage data</p>
        <small style={{ color: '#6b7280', marginBottom: '12px' }}>{error}</small>
        {isMockData && (
          <div style={{
            marginTop: '8px',
            padding: '4px 8px',
            backgroundColor: '#f3f4f6',
            borderRadius: '4px',
            fontSize: '0.8rem'
          }}>
            <small style={{ color: '#6b7280' }}>Showing sample data</small>
          </div>
        )}
      </div>
    );
  }

  return (
    <div style={{
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      padding: '16px',
      boxSizing: 'border-box',
      borderRadius: '8px',
      backgroundColor: '#fff',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
    }}>
      <h3 style={{
        fontSize: '16px',
        fontWeight: 600,
        color: '#1a202c',
        margin: '0 0 16px 0',
        paddingBottom: '12px',
        borderBottom: '1px solid #edf2f7',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <span>Storage Usage</span>
        <span style={{
          fontSize: '14px',
          fontWeight: 500,
          color: '#4b5563'
        }}>
          {formatBytes(used * 1024 * 1024)} / {formatBytes(total * 1024 * 1024)}
        </span>
      </h3>
      
      <div style={{ 
        flex: 1,
        minHeight: '250px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        padding: '16px 0'
      }}>
        {total === 0 ? (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            color: '#9ca3af',
            textAlign: 'center',
            padding: '20px 0'
          }}>
            <FontAwesomeIcon 
              icon={faDatabase} 
              style={{ fontSize: '2rem', marginBottom: '8px', opacity: 0.5 }} 
            />
            <p style={{ margin: 0, fontSize: '14px' }}>No storage data available</p>
          </div>
        ) : (
          <div style={{ 
            width: '100%', 
            height: '100%', 
            maxWidth: '220px',
            margin: '0 auto',
            position: 'relative'
          }}>
            <ResponsiveContainer width="100%" height="100%" minHeight="220px">
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  innerRadius={70}
                  outerRadius={90}
                  paddingAngle={2}
                  dataKey="value"
                  labelLine={false}
                >
                  {data.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.color}
                      stroke="#fff"
                      strokeWidth={2}
                    />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: number) => {
                    const isUsed = data[0]?.value === value;
                    return [
                      `${isUsed ? 'Used' : 'Free'}: ${formatBytes(Number(value) * 1024 * 1024)}`,
                      ''
                    ];
                  }}
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e2e8f0',
                    borderRadius: '6px',
                    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
                    padding: '8px 12px',
                    fontSize: '12px',
                    fontWeight: 500
                  }}
                />
                <text 
                  x="50%" 
                  y="50%" 
                  textAnchor="middle"
                  dominantBaseline="middle"
                  style={{
                    fontSize: '24px',
                    fontWeight: 700,
                    fill: '#4f46e5'
                  }}
                >
                  {usedPercentage}%
                </text>
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Legend */}
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        gap: '24px',
        marginTop: 'auto',
        paddingTop: '16px',
        borderTop: '1px solid #edf2f7'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          fontSize: '13px',
          color: '#4b5563',
          fontWeight: 500
        }}>
          <span style={{
            display: 'inline-block',
            width: '12px',
            height: '12px',
            backgroundColor: '#4f46e5',
            borderRadius: '2px',
            marginRight: '6px',
            flexShrink: 0
          }}></span>
          <span>Used</span>
        </div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          fontSize: '13px',
          color: '#4b5563',
          fontWeight: 500
        }}>
          <span style={{
            display: 'inline-block',
            width: '12px',
            height: '12px',
            backgroundColor: '#e2e8f0',
            borderRadius: '2px',
            marginRight: '6px',
            flexShrink: 0
          }}></span>
          <span>Free</span>
        </div>
      </div>
    </div>
  );
};

export default StorageUsageChart;
