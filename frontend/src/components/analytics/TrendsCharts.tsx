import React from 'react';
import { Icons } from './icons';

const VIBRANT_COLORS = [
  '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', 
  '#10b981', '#06b6d4', '#6366f1', '#f97316'
];

interface TrendItem {
  day?: string;
  hour?: string;
  count: number;
}

interface TrendsChartsProps {
  byDayOfWeek: TrendItem[];
  byHourOfDay: TrendItem[];
  maxDayCount: number;
  maxHourCount: number;
}

const TrendsCharts: React.FC<TrendsChartsProps> = ({
  byDayOfWeek,
  byHourOfDay,
  maxDayCount,
  maxHourCount
}) => {
  return (
    <div className="two-column-grid">
      {/* Day of Week */}
      <div className="day-chart-container">
        <div className="day-chart-header">
          <h2><Icons.BarChart /> Uploads by Day</h2>
          <p>Weekly upload patterns</p>
        </div>
        
        {byDayOfWeek.length === 0 ? (
          <div style={{ height: '250px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <p style={{ color: '#6b7280' }}>No day-wise trends data available</p>
          </div>
        ) : (
          <div className="day-bars-container">
            {byDayOfWeek.map((item, index) => {
              const height = maxDayCount > 0 ? (item.count / maxDayCount) * 200 : 0;
              return (
                <div key={index} className="day-bar-item">
                  <div
                    title={`${item.day}: ${item.count} uploads`}
                    className={item.count > 0 ? "day-bar active" : "day-bar inactive"}
                    style={{ 
                      height: `${height}px`,
                      backgroundColor: item.count > 0 ? VIBRANT_COLORS[index % VIBRANT_COLORS.length] : '#e5e7eb'
                    }}
                    onMouseEnter={(e) => {
                      if (item.count > 0) {
                        e.currentTarget.style.transform = 'scale(1.05)';
                        e.currentTarget.style.filter = 'brightness(1.1)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (item.count > 0) {
                        e.currentTarget.style.transform = 'scale(1)';
                        e.currentTarget.style.filter = 'brightness(1)';
                      }
                    }}
                  />
                  <div className="day-label">
                    {item.day}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Hour of Day */}
      <div className="hour-chart-container">
        <div className="hour-chart-header">
          <h2><Icons.Clock /> Upload Times</h2>
          <p>Peak upload hours</p>
        </div>
        
        {byHourOfDay.length === 0 ? (
          <div style={{ height: '250px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <p style={{ color: '#6b7280' }}>No hourly trends data available</p>
          </div>
        ) : (
          <div className="hour-bars-container">
            {byHourOfDay.map((item, index) => {
              const height = maxHourCount > 0 ? (item.count / maxHourCount) * 200 : 0;
              return (
                <div key={index} className="hour-bar-item">
                  <div
                    title={`${item.hour}: ${item.count} uploads`}
                    className={item.count > 0 ? "hour-bar active" : "hour-bar inactive"}
                    style={{ 
                      height: `${height}px`,
                      backgroundColor: item.count > 0 ? VIBRANT_COLORS[index % VIBRANT_COLORS.length] : '#e5e7eb'
                    }}
                    onMouseEnter={(e) => {
                      if (item.count > 0) {
                        e.currentTarget.style.transform = 'scale(1.05)';
                        e.currentTarget.style.filter = 'brightness(1.1)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (item.count > 0) {
                        e.currentTarget.style.transform = 'scale(1)';
                        e.currentTarget.style.filter = 'brightness(1)';
                      }
                    }}
                  />
                  <div className="hour-label">
                    {item.hour}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default TrendsCharts;
