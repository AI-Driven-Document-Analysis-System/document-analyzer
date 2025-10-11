import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faExclamationTriangle } from '@fortawesome/free-solid-svg-icons';
import './DocumentActivityChart.css';

interface DocumentActivityChartProps {
  data: Array<{ date: string; count: number }>;
  loading?: boolean;
  error?: string | null;
}

const DocumentActivityChart: React.FC<DocumentActivityChartProps> = ({ 
  data = [], 
  loading = false, 
  error = null 
}) => {
  // Loading state
  if (loading) {
    return (
      <div className="chart-container">
        <div className="chart-loading">
          <div className="spinner"></div>
          <p>Loading document activity...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="chart-container">
        <div className="chart-error">
          <i className="fas fa-exclamation-triangle"></i>
          <p>Error loading activity data</p>
          <small>{error}</small>
        </div>
      </div>
    );
  }

  // No data state
  if (data.length === 0 && !loading && !error) {
    return (
      <div className="chart-container">
        <div className="chart-header">
          <h3>Document Upload Activity</h3>
        </div>
        <div className="chart-content">
          <div className="no-data">
            <FontAwesomeIcon icon="database" className="no-data-icon" />
            <p>No upload activity data available</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      padding: '16px',
      boxSizing: 'border-box'
    }}>
      <h3 style={{
        fontSize: '16px',
        fontWeight: 600,
        color: 'var(--text-primary)',
        margin: '0 0 16px 0',
        paddingBottom: '12px',
        borderBottom: '1px solid var(--border-color)'
      }}>
        Document Upload Activity (Last 30 Days)
      </h3>
      
      <div style={{ 
        flex: 1,
        minHeight: '250px',
        position: 'relative'
      }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={data}
            margin={{ top: 10, right: 15, left: -10, bottom: 5 }}
          >
            <defs>
              <linearGradient id="colorUv" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.1}/>
                <stop offset="95%" stopColor="#4f46e5" stopOpacity={0.02}/>
              </linearGradient>
            </defs>
            <CartesianGrid 
              strokeDasharray="3 3" 
              vertical={false} 
              stroke="var(--border-color)" 
            />
            <XAxis 
              dataKey="date" 
              tick={{ 
                fill: 'var(--text-secondary)', 
                fontSize: 11,
                fontWeight: 500
              }}
              axisLine={false}
              tickLine={false}
              tickMargin={10}
            />
            <YAxis 
              tick={{ 
                fill: 'var(--text-secondary)', 
                fontSize: 11,
                fontWeight: 500
              }}
              axisLine={false}
              tickLine={false}
              width={30}
              tickFormatter={(value) => Number.isInteger(value) ? value.toString() : ''}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: 'var(--bg-primary)',
                borderRadius: '6px',
                border: '1px solid var(--border-color)',
                boxShadow: 'var(--card-shadow)',
                padding: '8px 12px',
                fontSize: '12px',
                fontWeight: 500
              }}
              labelStyle={{
                color: 'var(--text-primary)',
                fontWeight: 600,
                marginBottom: '4px'
              }}
              formatter={(value: number) => [`${value} ${value === 1 ? 'Document' : 'Documents'}`]}
            />
            <Line 
              type="monotone" 
              dataKey="count" 
              stroke="var(--accent-color)" 
              strokeWidth={2}
              dot={false}
              activeDot={{
                r: 4,
                fill: 'var(--accent-color)',
                stroke: 'var(--bg-primary)',
                strokeWidth: 2
              }}
              strokeLinecap="round"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default DocumentActivityChart;
