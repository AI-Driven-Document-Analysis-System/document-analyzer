import React, { useState, useEffect } from 'react';
import { Icons } from './icons';

const ChatDistributionChart: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    fetchChatData();
  }, []);

  const fetchChatData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/analytics/chat-distribution-by-day', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        setData(result);
      }
    } catch (error) {
      console.error('Error fetching chat distribution data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="chart-container" style={{ width: '50%' }}>
        <div className="chart-header">
          <h2><Icons.Chart /> Daily Chat Activity</h2>
        </div>
        <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>
          Loading...
        </div>
      </div>
    );
  }

  const dailyData = data?.daily_data || [];
  const statistics = data?.statistics || {};
  const hasData = dailyData.length > 0;

  const maxCount = hasData ? Math.max(...dailyData.map((item: any) => item.count)) : 1;

  return (
    <div className="chart-container" style={{ width: '50%' }}>
      <div className="chart-header">
        <h2><Icons.Chart /> Daily Chat Activity</h2>
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
          <div style={{ fontSize: '3rem', opacity: 0.3 }}>💬</div>
          <div style={{ fontSize: '1.1rem', fontWeight: 600, color: '#cbd5e1' }}>No Chat Data Available</div>
          <div style={{ fontSize: '0.9rem', maxWidth: '500px', lineHeight: '1.5' }}>
            Start conversations to see your monthly chat distribution.
          </div>
        </div>
      ) : (
        <div style={{ padding: '16px', display: 'flex', gap: '24px', alignItems: 'flex-end' }}>
          {/* Histogram */}
          <div style={{ flex: 1 }}>
            <div style={{ 
              display: 'flex', 
              alignItems: 'flex-end', 
              gap: '8px',
              height: '180px',
              padding: '0 20px'
            }}>
              {dailyData.map((item: any, index: number) => {
                const barHeight = maxCount > 0 ? (item.count / maxCount) * 180 : 0;
                // Blue gradient
                const lightness = 60 - (index / dailyData.length) * 20; // 60% to 40%
                const color = `hsl(210, 90%, ${lightness}%)`;

                return (
                  <div
                    key={index}
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
                      {item.count > 0 && (
                        <div style={{
                          fontSize: '0.7rem',
                          color: '#fff',
                          fontWeight: 600,
                          marginBottom: '4px'
                        }}>
                          {item.count}
                        </div>
                      )}
                      <div
                        title={`${item.full_date}: ${item.count} chats`}
                        style={{
                          width: '100%',
                          height: `${barHeight}px`,
                          background: color,
                          borderRadius: '6px 6px 0 0',
                          transition: 'all 0.3s ease',
                          cursor: 'pointer',
                          border: `1px solid ${color}`,
                          boxShadow: `0 0 8px ${color}40`
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

                    {/* Day Label */}
                    <div style={{ 
                      textAlign: 'center',
                      fontSize: '0.65rem',
                      color: '#9ca3af',
                      fontWeight: 500,
                      lineHeight: '1.2'
                    }}>
                      {item.day}
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
              <div style={{ fontSize: '0.6rem', color: '#94a3b8', marginBottom: '2px', textTransform: 'uppercase', fontWeight: 600 }}>Total Chats</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 600, color: '#ffffff' }}>
                {statistics.total || 0}
              </div>
            </div>

            <div style={{ width: '100%', height: '1px', background: '#334155' }}></div>

            <div>
              <div style={{ fontSize: '0.6rem', color: '#94a3b8', marginBottom: '2px', textTransform: 'uppercase', fontWeight: 600 }}>Avg/Month</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 600, color: '#3b82f6' }}>
                {statistics.average || 0}
              </div>
            </div>

            <div style={{ width: '100%', height: '1px', background: '#334155' }}></div>

            <div style={{ display: 'flex', gap: '8px' }}>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '0.55rem', color: '#94a3b8', marginBottom: '2px', textTransform: 'uppercase', fontWeight: 600 }}>Min</div>
                <div style={{ fontSize: '1rem', fontWeight: 600, color: '#ef4444' }}>
                  {statistics.min || 0}
                </div>
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '0.55rem', color: '#94a3b8', marginBottom: '2px', textTransform: 'uppercase', fontWeight: 600 }}>Max</div>
                <div style={{ fontSize: '1rem', fontWeight: 600, color: '#22c55e' }}>
                  {statistics.max || 0}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatDistributionChart;
