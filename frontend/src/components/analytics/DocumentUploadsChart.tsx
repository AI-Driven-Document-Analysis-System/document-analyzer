import React from 'react';
import { Icons } from './icons';

const VIBRANT_COLORS = [
  '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', 
  '#10b981', '#06b6d4', '#6366f1', '#f97316'
];

interface ChartDataItem {
  date: string;
  uploads: number;
  totalSize: number;
}

interface DocumentUploadsChartProps {
  chartData: ChartDataItem[];
  maxUploads: number;
  formatDate: (date: string) => string;
  formatFileSize: (bytes: number) => string;
}

const DocumentUploadsChart: React.FC<DocumentUploadsChartProps> = ({
  chartData,
  maxUploads,
  formatDate,
  formatFileSize
}) => {
  return (
    <div className="chart-container">
      <div className="chart-header">
        <h2><Icons.LineChart /> Document Uploads Over Time</h2>
        <p>Track your document upload activity over the selected period</p>
      </div>
      
      {chartData.length === 0 ? (
        <div className="no-data-container">
          <div className="no-data-content">
            <div className="no-data-icon"><Icons.LineChart /></div>
            <h3 className="no-data-title">No Data Available</h3>
            <p className="no-data-text">No document uploads found for the selected period</p>
          </div>
        </div>
      ) : (
        <div>
          <div className="bar-chart-container">
            {chartData.slice(-14).map((item, index) => {
              const height = maxUploads > 0 ? (item.uploads / maxUploads) * 250 : 0;
              return (
                <div key={index} className="bar-item">
                  <div
                    title={`${formatDate(item.date)}: ${item.uploads} uploads (${formatFileSize(item.totalSize)})`}
                    className={item.uploads > 0 ? "bar active" : "bar inactive"}
                    style={{ 
                      height: `${height}px`,
                      backgroundColor: item.uploads > 0 ? VIBRANT_COLORS[index % VIBRANT_COLORS.length] : '#e5e7eb',
                      animation: `barRiseUp 0.6s ease-out ${index * 0.08}s both`,
                      transformOrigin: 'bottom'
                    }}
                    onMouseEnter={(e) => {
                      if (item.uploads > 0) {
                        e.currentTarget.style.transform = 'scale(1.05)';
                        e.currentTarget.style.filter = 'brightness(1.1)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (item.uploads > 0) {
                        e.currentTarget.style.transform = 'scale(1)';
                        e.currentTarget.style.filter = 'brightness(1)';
                      }
                    }}
                  />
                  <div className="date-label">
                    {formatDate(item.date)}
                  </div>
                </div>
              );
            })}
          </div>
          
          <div className="chart-summary">
            <div className="summary-item">
              <p className="summary-item-label">Total Uploads</p>
              <div className="summary-item-value">
                {chartData.reduce((sum, item) => sum + item.uploads, 0)}
              </div>
            </div>
            <div className="summary-item">
              <p className="summary-item-label">Total Size</p>
              <div className="summary-item-value">
                {formatFileSize(chartData.reduce((sum, item) => sum + item.totalSize, 0))}
              </div>
            </div>
          </div>
        </div>
      )}
      <style>{`
        @keyframes barRiseUp {
          from {
            transform: scaleY(0);
            opacity: 0.8;
          }
          to {
            transform: scaleY(1);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
};

export default DocumentUploadsChart;
