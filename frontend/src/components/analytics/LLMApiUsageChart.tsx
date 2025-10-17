import React, { useState } from 'react';
import { Icons } from './icons';

const LLMApiUsageChart: React.FC = () => {
  const [llmTab, setLlmTab] = useState<'tokens' | 'response'>('tokens');

  return (
    <div style={{ flex: 1 }} className="doc-types-container">
      <div className="doc-types-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2><Icons.Brain /> LLM API Usage Over Time</h2>
          <p>API requests per day</p>
        </div>
        
        {/* Model Toggle Tabs */}
        <div style={{ 
          display: 'flex', 
          gap: '0px',
          borderBottom: '2px solid #334155'
        }}>
          <button
            onClick={() => setLlmTab('tokens')}
            style={{
              padding: '4px 10px',
              background: llmTab === 'tokens' ? '#3b82f6' : '#1e293b',
              color: llmTab === 'tokens' ? 'white' : '#94a3b8',
              border: llmTab === 'tokens' ? '2px solid #3b82f6' : '2px solid #334155',
              borderBottom: llmTab === 'tokens' ? '2px solid #3b82f6' : '2px solid #334155',
              borderRadius: '0',
              fontWeight: 600,
              fontSize: '0.7rem',
              cursor: 'pointer',
              transition: 'all 0.2s',
              position: 'relative',
              marginBottom: '-2px'
            }}
            onMouseEnter={(e) => {
              if (llmTab !== 'tokens') {
                e.currentTarget.style.background = '#334155';
                e.currentTarget.style.color = '#cbd5e1';
              }
            }}
            onMouseLeave={(e) => {
              if (llmTab !== 'tokens') {
                e.currentTarget.style.background = '#1e293b';
                e.currentTarget.style.color = '#94a3b8';
              }
            }}
          >
            DeepSeek-V3
          </button>
          <button
            onClick={() => setLlmTab('response')}
            style={{
              padding: '4px 10px',
              background: llmTab === 'response' ? '#8b5cf6' : '#1e293b',
              color: llmTab === 'response' ? 'white' : '#94a3b8',
              border: llmTab === 'response' ? '2px solid #8b5cf6' : '2px solid #334155',
              borderBottom: llmTab === 'response' ? '2px solid #8b5cf6' : '2px solid #334155',
              borderRadius: '0',
              fontWeight: 600,
              fontSize: '0.7rem',
              cursor: 'pointer',
              transition: 'all 0.2s',
              position: 'relative',
              marginBottom: '-2px',
              marginLeft: '-2px'
            }}
            onMouseEnter={(e) => {
              if (llmTab !== 'response') {
                e.currentTarget.style.background = '#334155';
                e.currentTarget.style.color = '#cbd5e1';
              }
            }}
            onMouseLeave={(e) => {
              if (llmTab !== 'response') {
                e.currentTarget.style.background = '#1e293b';
                e.currentTarget.style.color = '#94a3b8';
              }
            }}
          >
            Llama-3.1-8B
          </button>
        </div>
      </div>

      {/* Histogram and Stats Container */}
      <div style={{ display: 'flex', gap: '16px', padding: '6px 0', alignItems: 'flex-start' }}>
        {/* GitHub-style Histogram */}
        <div style={{ 
          flex: 1,
          position: 'relative'
        }}>
          {/* Chart Container */}
          <div style={{
            display: 'flex',
            alignItems: 'flex-end',
            gap: '2px',
            height: '120px',
            paddingRight: '40px',
            position: 'relative'
          }}>
            {/* Y-axis labels on the right */}
            <div style={{ position: 'absolute', right: '0px', top: '0px', fontSize: '0.6rem', color: '#9ca3af', fontWeight: 500 }}>100</div>
            <div style={{ position: 'absolute', right: '0px', bottom: '0px', fontSize: '0.6rem', color: '#9ca3af', fontWeight: 500 }}>0</div>
            
            {/* Dotted grid lines (GitHub style) */}
            <div style={{ position: 'absolute', left: '0', right: '40px', top: '0px', height: '1px', borderTop: '1px dotted #e5e7eb' }}></div>
            <div style={{ position: 'absolute', left: '0', right: '40px', bottom: '0px', height: '1px', borderTop: '1px dotted #e5e7eb' }}></div>
            
            {/* Histogram bars */}
            {[
              { date: 'Oct 10', deepseek: 45, llama: 32 },
              { date: 'Oct 11', deepseek: 62, llama: 41 },
              { date: 'Oct 12', deepseek: 38, llama: 28 },
              { date: 'Oct 13', deepseek: 71, llama: 53 },
              { date: 'Oct 14', deepseek: 89, llama: 67 },
              { date: 'Oct 15', deepseek: 56, llama: 44 },
              { date: 'Oct 16', deepseek: 78, llama: 61 }
            ].map((day, index) => {
              const maxRequests = 100;
              const value = llmTab === 'tokens' ? day.deepseek : day.llama;
              const barHeight = (value / maxRequests) * 120;
              const barColor = llmTab === 'tokens' ? '#3b82f6' : '#8b5cf6';
              
              return (
                <div
                  key={index}
                  title={`${day.date}: ${value} requests`}
                  style={{
                    flex: 1,
                    height: `${barHeight}px`,
                    background: barColor,
                    borderRadius: '2px 2px 0 0',
                    transition: 'all 0.2s ease',
                    cursor: 'pointer',
                    position: 'relative'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.filter = 'brightness(1.2)';
                    e.currentTarget.style.transform = 'scaleY(1.02)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.filter = 'brightness(1)';
                    e.currentTarget.style.transform = 'scaleY(1)';
                  }}
                />
              );
            })}
          </div>
          
          {/* X-axis dates */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginTop: '12px',
            paddingRight: '40px'
          }}>
            {['Oct 10', 'Oct 11', 'Oct 12', 'Oct 13', 'Oct 14', 'Oct 15', 'Oct 16'].map((date, idx) => (
              <div key={idx} style={{
                flex: 1,
                textAlign: 'center',
                fontSize: '0.7rem',
                color: '#9ca3af',
                fontWeight: 500
              }}>
                {idx % 2 === 0 ? date : ''}
              </div>
            ))}
          </div>
        </div>

        {/* Summary Stats Box - On the right side */}
        <div style={{ 
          width: '220px',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
          padding: '16px',
          background: '#1e293b',
          borderRadius: '6px',
          border: `2px solid ${llmTab === 'tokens' ? '#3b82f6' : '#8b5cf6'}`,
          flexShrink: 0,
          marginLeft: '16px'
        }}>
          <div>
            <div style={{ fontSize: '0.65rem', color: '#94a3b8', marginBottom: '6px', textTransform: 'uppercase', fontWeight: 600, letterSpacing: '0.5px' }}>Total Requests</div>
            <div style={{ fontSize: '1.6rem', fontWeight: 600, color: '#ffffff', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
              {llmTab === 'tokens' ? '439' : '326'}
            </div>
            <div style={{ fontSize: '0.7rem', color: '#cbd5e1', marginTop: '4px' }}>Last 7 days</div>
          </div>
          <div style={{ height: '1px', background: '#334155' }}></div>
          <div>
            <div style={{ fontSize: '0.65rem', color: '#94a3b8', marginBottom: '6px', textTransform: 'uppercase', fontWeight: 600, letterSpacing: '0.5px' }}>Daily Average</div>
            <div style={{ fontSize: '1.6rem', fontWeight: 600, color: '#ffffff', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
              {llmTab === 'tokens' ? '63' : '47'}
            </div>
            <div style={{ fontSize: '0.7rem', color: '#cbd5e1', marginTop: '4px' }}>Requests/day</div>
          </div>
          <div style={{ height: '1px', background: '#334155' }}></div>
          <div>
            <div style={{ fontSize: '0.65rem', color: '#94a3b8', marginBottom: '6px', textTransform: 'uppercase', fontWeight: 600, letterSpacing: '0.5px' }}>Peak Day</div>
            <div style={{ fontSize: '1.6rem', fontWeight: 600, color: '#ffffff', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
              {llmTab === 'tokens' ? '89' : '67'}
            </div>
            <div style={{ fontSize: '0.7rem', color: '#cbd5e1', marginTop: '4px' }}>Oct {llmTab === 'tokens' ? '14' : '14'}</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LLMApiUsageChart;
