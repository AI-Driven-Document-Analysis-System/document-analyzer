import React, { useState, useEffect } from 'react';
import './analytics.css';

// ... (All your interfaces remain unchanged)
interface ChartData {
  date: string;
  uploads: number;
  totalSize: number;
}

interface SummaryData {
  totalDocuments: number;
  totalSize: number;
  averageSize: number;
  firstUpload: string | null;
  lastUpload: string | null;
}

interface DocumentTypeData {
  type: string;
  count: number;
  avgSize: number;
}

interface TrendData {
  day: string;
  count: number;
}

interface HourData {
  hour: string;
  count: number;
}

// ... (Your helper functions remain unchanged)
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  });
};

// SVG Icons Component
const Icons = {
  Document: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z" />
      <path d="M14 2v6h6" />
      <path d="M16 13H8" />
      <path d="M16 17H8" />
      <path d="M10 9H8" />
    </svg>
  ),
  Storage: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="2" y="6" width="20" height="12" rx="2" />
      <path d="M2 12h20" />
      <path d="M6 6v12" />
      <path d="M18 6v12" />
    </svg>
  ),
  Chart: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M3 3v18h18" />
      <path d="M17 9L12 4L7 9" />
      <path d="M12 4v16" />
    </svg>
  ),
  Calendar: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="4" width="18" height="18" rx="2" />
      <path d="M16 2v4" />
      <path d="M8 2v4" />
      <path d="M3 10h18" />
    </svg>
  ),
  LineChart: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M3 3v18h18" />
      <path d="M7 16l4-6l4 4l4-6" />
    </svg>
  ),
  BarChart: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M3 3v18h18" />
      <rect x="7" y="13" width="4" height="7" rx="1" />
      <rect x="13" y="8" width="4" height="12" rx="1" />
      <rect x="19" y="16" width="4" height="4" rx="1" />
    </svg>
  ),
  Clock: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="10" />
      <path d="M12 6v6l4 2" />
    </svg>
  ),
  FileType: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z" />
      <path d="M14 2v6h6" />
    </svg>
  ),
  Refresh: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M21 12a9 9 0 0 1-9 9 9 9 0 0 1-9-9 9 9 0 0 1 9-9" />
      <path d="M21 12H12V3" />
    </svg>
  )
};

const Analytics: React.FC = () => {
  const [chartData, setChartData] = useState<ChartData[]>([]);
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [documentTypes, setDocumentTypes] = useState<DocumentTypeData[]>([]);
  const [trends, setTrends] = useState<{ byDayOfWeek: TrendData[]; byHourOfDay: HourData[] }>({ byDayOfWeek: [], byHourOfDay: [] });
  const [selectedPeriod, setSelectedPeriod] = useState('30d');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // ... (All your data fetching and processing functions remain unchanged)
  const fetchAnalyticsData = async (period: string, isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);

      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      console.log('Fetching analytics data for period:', period);

      let uploadsData: any = null;
      let typesData: any = null;
      let trendsData: any = null;

      try {
        const uploadsUrl = `http://localhost:8000/api/analytics/document-uploads-over-time?period=${period}`;
        console.log('Trying analytics endpoint:', uploadsUrl);
        
        const uploadsResponse = await fetch(uploadsUrl, { headers });
        if (uploadsResponse.ok) {
          uploadsData = await uploadsResponse.json();
          console.log('Analytics data received:', uploadsData);
        } else {
          throw new Error('Analytics endpoint not available');
        }

        const typesUrl = 'http://localhost:8000/api/analytics/document-types-distribution';
        const typesResponse = await fetch(typesUrl, { headers });
        if (typesResponse.ok) {
          typesData = await typesResponse.json();
        }

        const trendsUrl = 'http://localhost:8000/api/analytics/upload-trends';
        const trendsResponse = await fetch(trendsUrl, { headers });
        if (trendsResponse.ok) {
          trendsData = await trendsResponse.json();
        }

      } catch (analyticsError) {
        console.log('Analytics endpoints not available, fetching from documents endpoint');
        
        const documentsUrl = 'http://localhost:8000/api/documents/?limit=1000';
        const documentsResponse = await fetch(documentsUrl, { headers });
        
        if (!documentsResponse.ok) {
          throw new Error(`Failed to fetch documents: ${documentsResponse.status}`);
        }
        
        const documentsData = await documentsResponse.json();
        const documents = documentsData.documents || [];
        
        console.log('Documents fetched:', documents.length);
        
        uploadsData = processDocumentsForChart(documents, period);
        typesData = processDocumentsForTypes(documents);
        trendsData = processDocumentsForTrends(documents);
      }

      setChartData(uploadsData?.chartData || []);
      setSummary(uploadsData?.summary || null);
      setDocumentTypes(typesData?.chartData || []);
      setTrends(trendsData || { byDayOfWeek: [], byHourOfDay: [] });
      setLastUpdated(new Date());

    } catch (err) {
      console.error('Error fetching analytics ', err);
      setError(err instanceof Error ? err.message : 'Failed to load analytics data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const processDocumentsForChart = (documents: any[], period: string) => {
    console.log('Processing documents for chart:', documents.length, 'documents');
    
    const now = new Date();
    let startDate = new Date();
    
    switch (period) {
      case '7d':
        startDate.setDate(now.getDate() - 7);
        break;
      case '30d':
        startDate.setDate(now.getDate() - 30);
        break;
      case '90d':
        startDate.setDate(now.getDate() - 90);
        break;
      case '1y':
        startDate.setFullYear(now.getFullYear() - 1);
        break;
    }

    console.log('Date range:', startDate.toISOString(), 'to', now.toISOString());

    const filteredDocs = documents.filter(doc => {
      if (!doc.upload_date && !doc.created_at) {
        return false;
      }
      const uploadDate = new Date(doc.upload_date || doc.created_at);
      return uploadDate >= startDate && uploadDate <= now;
    });

    console.log('Filtered documents:', filteredDocs.length);

    const groupedData: { [key: string]: { uploads: number; totalSize: number } } = {};
    
    filteredDocs.forEach(doc => {
      const date = new Date(doc.upload_date || doc.created_at).toISOString().split('T')[0];
      if (!groupedData[date]) {
        groupedData[date] = { uploads: 0, totalSize: 0 };
      }
      groupedData[date].uploads += 1;
      groupedData[date].totalSize += doc.file_size || 0;
    });

    const chartData: ChartData[] = [];
    const currentDate = new Date(startDate);
    
    while (currentDate <= now) {
      const dateStr = currentDate.toISOString().split('T')[0];
      const data = groupedData[dateStr] || { uploads: 0, totalSize: 0 };
      
      chartData.push({
        date: dateStr,
        uploads: data.uploads,
        totalSize: data.totalSize
      });
      
      currentDate.setDate(currentDate.getDate() + 1);
    }

    const totalDocuments = documents.length;
    const totalSize = documents.reduce((sum, doc) => sum + (doc.file_size || 0), 0);
    const averageSize = totalDocuments > 0 ? totalSize / totalDocuments : 0;
    
    const sortedDocs = documents
      .filter(doc => doc.upload_date || doc.created_at)
      .sort((a, b) => new Date(a.upload_date || a.created_at).getTime() - new Date(b.upload_date || b.created_at).getTime());
    
    const firstUpload = sortedDocs.length > 0 ? (sortedDocs[0].upload_date || sortedDocs[0].created_at) : null;
    const lastUpload = sortedDocs.length > 0 ? (sortedDocs[sortedDocs.length - 1].upload_date || sortedDocs[sortedDocs.length - 1].created_at) : null;

    return {
      chartData,
      summary: {
        totalDocuments,
        totalSize,
        averageSize,
        firstUpload,
        lastUpload
      }
    };
  };

  const processDocumentsForTypes = (documents: any[]) => {
    const typeCounts: { [key: string]: { count: number; totalSize: number } } = {};
    
    documents.forEach(doc => {
      let type = 'Unknown';
      if (doc.filename) {
        const extension = doc.filename.split('.').pop()?.toUpperCase();
        type = extension || 'Unknown';
      } else if (doc.content_type) {
        const mimeMap: { [key: string]: string } = {
          'application/pdf': 'PDF',
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'DOCX',
          'application/msword': 'DOC',
          'text/plain': 'TXT',
          'image/png': 'PNG',
          'image/jpeg': 'JPG',
          'image/jpg': 'JPG',
          'application/vnd.ms-excel': 'XLS',
          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'XLSX'
        };
        type = mimeMap[doc.content_type] || doc.content_type.split('/').pop()?.toUpperCase() || 'Unknown';
      }
      
      if (!typeCounts[type]) {
        typeCounts[type] = { count: 0, totalSize: 0 };
      }
      typeCounts[type].count += 1;
      typeCounts[type].totalSize += doc.file_size || 0;
    });

    return {
      chartData: Object.entries(typeCounts).map(([type, data]) => ({
        type,
        count: data.count,
        avgSize: data.count > 0 ? data.totalSize / data.count : 0
      })).sort((a, b) => b.count - a.count)
    };
  };

  const processDocumentsForTrends = (documents: any[]) => {
    const dayCounts: { [key: number]: number } = {};
    const hourCounts: { [key: number]: number } = {};
    
    documents.forEach(doc => {
      const dateStr = doc.upload_date || doc.created_at;
      if (dateStr) {
        const date = new Date(dateStr);
        const dayOfWeek = date.getDay();
        const hour = date.getHours();
        
        dayCounts[dayOfWeek] = (dayCounts[dayOfWeek] || 0) + 1;
        hourCounts[hour] = (hourCounts[hour] || 0) + 1;
      }
    });

    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const byDayOfWeek = days.map((day, index) => ({
      day,
      count: dayCounts[index] || 0
    }));

    const hourRanges = [
      { label: '6AM', hours: [6, 7] },
      { label: '8AM', hours: [8, 9] },
      { label: '10AM', hours: [10, 11] },
      { label: '12PM', hours: [12, 13] },
      { label: '2PM', hours: [14, 15] },
      { label: '4PM', hours: [16, 17] },
      { label: '6PM', hours: [18, 19] },
      { label: '8PM', hours: [20, 21] }
    ];

    const byHourOfDay = hourRanges.map(range => ({
      hour: range.label,
      count: range.hours.reduce((sum, hour) => sum + (hourCounts[hour] || 0), 0)
    }));

    return { byDayOfWeek, byHourOfDay };
  };

  useEffect(() => {
    fetchAnalyticsData(selectedPeriod);
  }, [selectedPeriod]);

  const handlePeriodChange = (period: string) => {
    setSelectedPeriod(period);
  };

  if (loading) {
    return (
      <div className="analytics-container">
        <div className="analytics-header">
          <div className="analytics-title">
            <h1>Analytics Dashboard</h1>
            <p>Loading...</p>
          </div>
        </div>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          height: '200px',
          backgroundColor: '#f9fafb',
          borderRadius: '8px'
        }}>
          <div style={{ textAlign: 'center' }}>
            <div className="spinner"></div>
            <p>Loading analytics data...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <p className="error-text">Error: {error}</p>
        <button 
          onClick={() => fetchAnalyticsData(selectedPeriod)}
          className="error-btn"
        >
          Try Again
        </button>
      </div>
    );
  }

  const maxUploads = chartData.length > 0 ? Math.max(...chartData.map(d => d.uploads)) : 1;
  const maxDayCount = trends.byDayOfWeek.length > 0 ? Math.max(...trends.byDayOfWeek.map(d => d.count)) : 1;
  const maxHourCount = trends.byHourOfDay.length > 0 ? Math.max(...trends.byHourOfDay.map(d => d.count)) : 1;
  const maxTypeCount = documentTypes.length > 0 ? Math.max(...documentTypes.map(d => d.count)) : 1;

  return (
    <div className="analytics-container">
      {/* Header */}
      <div className="analytics-header">
        <div className="analytics-title">
          <h1>Analytics Dashboard</h1>
          <p>Document upload insights and trends</p>
        </div>
        <div className="analytics-controls">
          <button
            onClick={() => fetchAnalyticsData(selectedPeriod, true)}
            disabled={refreshing}
            className="refresh-btn"
          >
            <span className="refresh-icon" style={{ transform: refreshing ? 'rotate(360deg)' : 'none' }}>
              <Icons.Refresh />
            </span>
            <span>{refreshing ? "Refreshing..." : "Refresh"}</span>
          </button>
          <select 
            value={selectedPeriod} 
            onChange={(e) => handlePeriodChange(e.target.value)}
            className="period-select"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
        </div>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="summary-grid">
          <div className="summary-card">
            <div className="summary-card-header">
              <h3>Total Documents</h3>
              <div className="summary-icon"><Icons.Document /></div>
            </div>
            <div className="summary-value">{summary.totalDocuments}</div>
            <p className="summary-subtitle">All time uploads</p>
          </div>
          
          <div className="summary-card">
            <div className="summary-card-header">
              <h3>Total Storage</h3>
              <div className="summary-icon"><Icons.Storage /></div>
            </div>
            <div className="summary-value">{formatFileSize(summary.totalSize)}</div>
            <p className="summary-subtitle">Storage used</p>
          </div>
          
          <div className="summary-card">
            <div className="summary-card-header">
              <h3>Average Size</h3>
              <div className="summary-icon"><Icons.Chart /></div>
            </div>
            <div className="summary-value">{formatFileSize(summary.averageSize)}</div>
            <p className="summary-subtitle">Per document</p>
          </div>
          
          <div className="summary-card">
            <div className="summary-card-header">
              <h3>Last Upload</h3>
              <div className="summary-icon"><Icons.Calendar /></div>
            </div>
            <div className="summary-value">
              {summary.lastUpload ? formatDate(summary.lastUpload) : 'N/A'}
            </div>
            <p className="summary-subtitle">Most recent</p>
          </div>
        </div>
      )}

      {/* Main Chart - Document Uploads Over Time */}
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
                      style={{ height: `${height}px` }}
                      onMouseEnter={(e) => {
                        if (item.uploads > 0) {
                          e.currentTarget.style.backgroundColor = '#2563eb';
                          e.currentTarget.style.transform = 'scale(1.05)';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (item.uploads > 0) {
                          e.currentTarget.style.backgroundColor = '#3b82f6';
                          e.currentTarget.style.transform = 'scale(1)';
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
                <p className="summary-item-label">Peak Day</p>
                <div className="summary-item-value">
                  {maxUploads}
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
      </div>

      {/* Document Types and Day of Week Charts */}
      <div className="two-column-grid">
        {/* Document Types */}
        <div className="doc-types-container">
          <div className="doc-types-header">
            <h2><Icons.FileType /> Document Types</h2>
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
                    <div className="doc-type-label">
                      {item.type}
                    </div>
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

        {/* Day of Week */}
        <div className="day-chart-container">
          <div className="day-chart-header">
            <h2><Icons.BarChart /> Uploads by Day</h2>
            <p>Weekly upload patterns</p>
          </div>
          
          {trends.byDayOfWeek.length === 0 ? (
            <div style={{ height: '250px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <p style={{ color: '#6b7280' }}>No day-wise trends data available</p>
            </div>
          ) : (
            <div className="day-bars-container">
              {trends.byDayOfWeek.map((item, index) => {
                const height = maxDayCount > 0 ? (item.count / maxDayCount) * 200 : 0;
                return (
                  <div key={index} className="day-bar-item">
                    <div
                      title={`${item.day}: ${item.count} uploads`}
                      className={item.count > 0 ? "day-bar active" : "day-bar inactive"}
                      style={{ height: `${height}px` }}
                      onMouseEnter={(e) => {
                        if (item.count > 0) {
                          e.currentTarget.style.backgroundColor = '#2563eb';
                          e.currentTarget.style.transform = 'scale(1.05)';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (item.count > 0) {
                          e.currentTarget.style.backgroundColor = '#3b82f6';
                          e.currentTarget.style.transform = 'scale(1)';
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
      </div>

      {/* Hour of Day Chart */}
      <div className="hour-chart-container">
        <div className="hour-chart-header">
          <h2><Icons.Clock /> Upload Times</h2>
          <p>Peak hours during the day</p>
        </div>
        
        {trends.byHourOfDay.length === 0 ? (
          <div style={{ height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <p style={{ color: '#6b7280' }}>No hourly trends data available</p>
          </div>
        ) : (
          <div className="hour-chart-wrapper">
            {/* Grid lines */}
            {[25, 50, 75, 100].map(percent => (
              <div 
                key={percent}
                className="grid-line"
                style={{
                  bottom: `${(percent * 150) / 100 + 10}px`
                }}
              />
            ))}
            
            {/* Line connecting the points */}
            <svg className="line-chart">
              <polyline
                fill="none"
                stroke="#3b82f6"
                strokeWidth="2"
                points={trends.byHourOfDay.map((item, index) => {
                  const x = (index / (trends.byHourOfDay.length - 1)) * 100;
                  const y = maxHourCount > 0 ? 100 - (item.count / maxHourCount) * 100 : 100;
                  return `${x}%,${y}%`;
                }).join(' ')}
              />
            </svg>
            
            {trends.byHourOfDay.map((item, index) => {
              const height = maxHourCount > 0 ? (item.count / maxHourCount) * 150 : 0;
              return (
                <div key={index} className="bar-item" style={{ flex: 1 }}>
                  <div
                    style={{ marginBottom: `${height}px` }}
                    className="hour-point"
                    title={`${item.hour}: ${item.count} uploads`}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'scale(1.5)';
                      e.currentTarget.style.backgroundColor = '#1d4ed8';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'scale(1)';
                      e.currentTarget.style.backgroundColor = '#3b82f6';
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

      {lastUpdated && (
        <div className="last-updated">
          Last updated: {lastUpdated.toLocaleString()}
        </div>
      )}
    </div>
  );
};

export default Analytics;