


//****************************CSS */
import { useState, useEffect, useMemo, useCallback } from "react"
import './Dashboard.css' // Import the CSS file
import DocumentActivityChart from './DocumentActivityChart';
import StorageUsageChart from './StorageUsageChart';
//import DocumentViewer from '../DocumentViewer/DocumentViewer';

// Cache for dashboard data (5-minute TTL)
const dashboardCache: { data: any; timestamp: number } | null = null;
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes
let cacheInstance: { data: any; timestamp: number } | null = null;

// TypeScript interfaces
interface Document {
  id: string
  original_filename: string
  content_type: string
  file_size: number
  processing_status: 'completed' | 'processing' | 'failed'
  upload_date: string
  user_id: string
}

interface Summary {
  id: number | string
  summary_text: string
  summary_type: string
  word_count: number
  model_used: string
  created_at: string
  from_cache: boolean
  key_points?: string[] | null
  document_type?: string | null
}

interface FormattedDocument {
  id: string
  name: string
  type: string
  status: string
  uploadedAt: string
  confidence: number | null
}

interface SummaryOption {
  id: string
  name: string
  description: string
  model: string
  icon: string
}

interface DocumentWithSummary extends FormattedDocument {
  showSummaryOptions: boolean
  selectedModel: string | null
  currentSummary: Summary | null
  loadingSummary: boolean
  generatingNew: boolean
  summaryError: string | null
}

interface DocumentTypeData {
  type: string;
  count: number;
  avgSize: number;
}

interface ResourceUsageData {
  id: string;
  name: string;
  size: number; // in bytes
  processingTime: number; // in seconds (approximated)
}

// Inline styles for modal
const modalStyles = {
  overlay: {
    position: 'fixed' as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(0, 0, 0, 0.75)',
    backdropFilter: 'blur(8px)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 9999,
    padding: '20px',
    animation: 'fadeInModal 0.3s ease-out'
  },
  container: {
    background: 'white',
    borderRadius: '16px',
    width: '90vw',
    maxWidth: '1200px',
    height: '90vh',
    maxHeight: '900px',
    display: 'flex',
    flexDirection: 'column' as const,
    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
    overflow: 'hidden',
    position: 'relative' as const,
    animation: 'slideInModal 0.3s ease-out'
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '20px 24px',
    borderBottom: '1px solid #e5e7eb',
    background: 'linear-gradient(135deg, #f8fafc, #e2e8f0)',
    flexShrink: 0
  },
  title: {
    flex: 1
  },
  titleH3: {
    fontSize: '1.25rem',
    fontWeight: 600,
    color: '#1a202c',
    margin: '0 0 4px 0'
  },
  titleP: {
    fontSize: '0.875rem',
    color: '#718096',
    margin: 0
  },
  closeButton: {
    background: 'none',
    border: 'none',
    fontSize: '24px',
    color: '#718096',
    cursor: 'pointer',
    padding: '8px',
    borderRadius: '8px',
    transition: 'all 0.2s ease',
    lineHeight: 1,
    marginLeft: '16px'
  },
  body: {
    flex: 1,
    padding: 0,
    overflow: 'hidden',
    position: 'relative' as const,
    background: '#f7fafc'
  },
  viewer: {
    width: '100%',
    height: '100%',
    position: 'relative' as const
  },
  iframe: {
    width: '100%',
    height: '100%',
    border: 'none',
    background: 'white'
  },
  imageViewer: {
    width: '100%',
    height: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '20px',
    overflow: 'auto'
  },
  image: {
    maxWidth: '100%',
    maxHeight: '100%',
    objectFit: 'contain' as const,
    borderRadius: '8px',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)'
  },
  loading: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    color: '#718096',
    
    

  },
  loadingSpinner: {
    
    width: '48px',
    height: '48px',
    border: '4px solid #e2e8f0',
    borderTop: '4px solid #667eea',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    marginBottom: '16px'
    
  },

  
  error: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    textAlign: 'center' as const,
    color: '#718096',
    padding: '40px'
  },
  errorIcon: {
    fontSize: '4rem',
    marginBottom: '16px',
    color: '#e53e3e'
  },
  errorH4: {
    fontSize: '1.25rem',
    color: '#2d3748',
    marginBottom: '8px'
  },
  errorP: {
    color: '#718096',
    marginBottom: '24px'
  },
  unsupported: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    textAlign: 'center' as const,
    padding: '40px',
    color: '#718096'
  },
  fileIcon: {
    fontSize: '4rem',
    marginBottom: '16px',
    color: '#a0aec0'
  },
  downloadBtn: {
    background: 'linear-gradient(135deg, #667eea, #764ba2)',
    color: 'white',
    border: 'none',
    padding: '12px 24px',
    borderRadius: '8px',
    fontSize: '1rem',
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  }
};

// Main Dashboard Component
function Dashboard() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [documentsWithSummary, setDocumentsWithSummary] = useState<DocumentWithSummary[]>([])
  
  // Storage usage state
  const [storageUsage, setStorageUsage] = useState({ used: 0, total: 1024 }) // Default to 2GB
  const [loadingStorage, setLoadingStorage] = useState(true)
  const [storageError, setStorageError] = useState<string | null>(null)
  
  // Chat and modal states
  const [activeView, setActiveView] = useState<'documents' | 'chat'>('documents')
  const [selectedDocument, setSelectedDocument] = useState<any>(null)
  const [summaryModalOpen, setSummaryModalOpen] = useState(false)
  const [selectedDocumentForSummary, setSelectedDocumentForSummary] = useState<{id: string, name: string} | null>(null)
  const [currentSummaryDoc, setCurrentSummaryDoc] = useState<DocumentWithSummary | null>(null)
  
  // Document preview states
  const [previewDocument, setPreviewDocument] = useState<DocumentWithSummary | null>(null)
  const [showPreview, setShowPreview] = useState(false)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [loadingPreview, setLoadingPreview] = useState(false)

  //***********************/
  // Document type distribution state
  const [documentTypes, setDocumentTypes] = useState<DocumentTypeData[]>([]);
  const [loadingTypes, setLoadingTypes] = useState(true);
  const [typesError, setTypesError] = useState<string | null>(null);
  const [chartType, setChartType] = useState<'bar' | 'pie'>('bar');

  // Resource usage state
  const [resourceUsageData, setResourceUsageData] = useState<ResourceUsageData[]>([]);
  const [loadingResourceUsage, setLoadingResourceUsage] = useState(true);
  const [resourceUsageError, setResourceUsageError] = useState<string | null>(null);
  const [resourceMetric, setResourceMetric] = useState<'size' | 'time'>('size');

  // Summary options configuration
  const summaryOptions: SummaryOption[] = [
    {
      id: 'brief',
      name: 'Brief Summary',
      description: 'Quick overview with key points (50-150 words)',
      model: 'BART',
      icon: 'fas fa-file-text'
    },
    {
      id: 'detailed',
      name: 'Detailed Summary',
      description: 'Comprehensive analysis with full context (80-250 words)',
      model: 'PEGASUS',
      icon: 'fas fa-file-alt'
    },
    {
      id: 'domain_specific',
      name: 'Domain-Specific',
      description: 'Specialized summary based on document type (70-200 words)',
      model: 'Auto-Selected',
      icon: 'fas fa-bullseye'
    }
  ]

  // JWT token handling
  const getToken = () => {
    const token = localStorage.getItem("token")
    return token
  }

  // Document activity data state
  const [documentActivityData, setDocumentActivityData] = useState<Array<{ date: string; count: number }>>([]);
  const [loadingActivity, setLoadingActivity] = useState(true);
  const [activityError, setActivityError] = useState<string | null>(null);

  // Helper function: Process documents for types (moved outside useEffect)
  const processDocumentsForTypes = useCallback((docs: Document[]) => {
    const typeCounts: { [key: string]: { count: number; totalSize: number } } = {};

    docs.forEach(doc => {
      let type = 'Unknown';
      if (doc.original_filename) {
        const ext = doc.original_filename.split('.').pop()?.toUpperCase();
        type = ext || 'Unknown';
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
  }, []);

  // UNIFIED DATA FETCHING with PARALLEL API CALLS
  useEffect(() => {
    const fetchAllDashboardData = async () => {
      // Check cache first
      if (cacheInstance && Date.now() - cacheInstance.timestamp < CACHE_TTL) {
        console.log('Using cached dashboard data');
        const cached = cacheInstance.data;
        setDocuments(cached.documents || []);
        setDocumentTypes(cached.documentTypes || []);
        setDocumentActivityData(cached.activityData || []);
        setStorageUsage(cached.storageUsage || { used: 0, total: 2048 });
        setResourceUsageData(cached.resourceUsage || []);
        setLoading(false);
        setLoadingTypes(false);
        setLoadingActivity(false);
        setLoadingStorage(false);
        setLoadingResourceUsage(false);
        return;
      }

      const token = getToken();
      if (!token) {
        console.warn('No token found');
        setLoading(false);
        setLoadingTypes(false);
        setLoadingActivity(false);
        setLoadingStorage(false);
        setLoadingResourceUsage(false);
        return;
      }

      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      };

      try {
        console.log('Fetching all dashboard data in parallel...');
        
        // PARALLEL FETCH - All API calls happen at once
        const [documentsRes, typesRes, activityRes, storageRes] = await Promise.all([
          fetch('http://localhost:8000/api/documents/?limit=100', { headers }), // Limit to 100 for faster load
          fetch('http://localhost:8000/api/analytics/document-types-distribution', { headers }),
          fetch('http://localhost:8000/api/profile/me', { headers }),
          fetch('http://localhost:8000/api/analytics/document-uploads-over-time?period=30d', { headers })
        ]);

        // Process responses
        const docsData = documentsRes.ok ? await documentsRes.json() : { documents: [] };
        const docs = docsData.documents || [];
        
        let types: DocumentTypeData[] = [];
        if (typesRes.ok) {
          const typesData = await typesRes.json();
          types = typesData.chartData || [];
        } else {
          types = processDocumentsForTypes(docs).chartData;
        }

        let activity: Array<{ date: string; count: number }> = [];
        if (activityRes.ok) {
          const actData = await activityRes.json();
          activity = actData.upload_activity || [];
        }

        let storage: { used: number; total: number } = { used: 0, total: 2048 };
        if (storageRes.ok) {
          const storData = await storageRes.json();
          if (storData.summary) {
            const usedMB = Math.round((storData.summary.totalSize || 0) / (1024 * 1024));
            storage = { used: usedMB, total: 5 * 1024 };
          }
        }

        // Process resource usage from documents
        const resourceData: ResourceUsageData[] = docs.map((doc: Document) => {
          const sizeInBytes = doc.file_size || 0;
          const sizeInMB = sizeInBytes / (1024 * 1024);
          const approximateProcessingTime = 2 + Math.floor(sizeInMB * 1.5);
          return {
            id: doc.id,
            name: doc.original_filename || 'Untitled Document',
            size: sizeInBytes,
            processingTime: approximateProcessingTime
          };
        });

        // Update all state at once
        setDocuments(docs);
        setDocumentTypes(types);
        setDocumentActivityData(activity);
        setStorageUsage(storage);
        setResourceUsageData(resourceData);

        // Cache the data
        cacheInstance = {
          data: {
            documents: docs,
            documentTypes: types,
            activityData: activity,
            storageUsage: storage,
            resourceUsage: resourceData
          },
          timestamp: Date.now()
        };

        console.log('Dashboard data cached successfully');

      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data');
      } finally {
        setLoading(false);
        setLoadingTypes(false);
        setLoadingActivity(false);
        setLoadingStorage(false);
        setLoadingResourceUsage(false);
      }
    };

    fetchAllDashboardData();
  }, []); // Only run once on mount

  //*********************** */
  // REMOVE OLD USEEFFECTS - Replaced by unified fetch above
  // Fetch document type distribution
/*useEffect(() => {
  const fetchDocumentTypes = async () => {
    const token = getToken();
    if (!token) {
      console.warn('No token, skipping document types fetch');
      setLoadingTypes(false);
      return;
    }

    try {
      setLoadingTypes(true);
      setTypesError(null);

      // Try dedicated endpoint first
      const response = await fetch('http://localhost:8000/api/analytics/document-types-distribution', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setDocumentTypes(data.chartData || []);
      } else {
        // Fallback: process from documents if needed
        const processed = processDocumentsForTypes(documents);
        setDocumentTypes(processed.chartData);
      }
    } catch (err) {
      console.error('Error fetching document types:', err);
      setTypesError('Failed to load document type data');
      // Fallback to local processing
      const processed = processDocumentsForTypes(documents);
      setDocumentTypes(processed.chartData);
    } finally {
      setLoadingTypes(false);
    }
  };

  // Helper function (same as in analytics.tsx)
  const processDocumentsForTypes = (docs: Document[]) => {
    const typeCounts: { [key: string]: { count: number; totalSize: number } } = {};

    docs.forEach(doc => {
      let type = 'Unknown';
      if (doc.original_filename) {
        const ext = doc.original_filename.split('.').pop()?.toUpperCase();
        type = ext || 'Unknown';
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

  fetchDocumentTypes();
}, [documents]); // Re-fetch when documents change */

// Process resource usage data from documents
/* COMMENTED OUT - Now handled by unified fetch
useEffect(() => {
  const processResourceUsageData = () => {
    try {
      setLoadingResourceUsage(true);
      setResourceUsageError(null);

      const resourceData: ResourceUsageData[] = documents.map(doc => {
        const sizeInBytes = doc.file_size || 0;
        // Approximate processing time based on file size (larger files take longer)
        // Base time: 2 seconds + 1 second per MB
        const sizeInMB = sizeInBytes / (1024 * 1024);
        const approximateProcessingTime = 2 + Math.floor(sizeInMB * 1.5); // seconds

        return {
          id: doc.id,
          name: doc.original_filename || 'Untitled Document',
          size: sizeInBytes,
          processingTime: approximateProcessingTime
        };
      });

      setResourceUsageData(resourceData);
    } catch (err) {
      console.error('Error processing resource usage data:', err);
      setResourceUsageError('Failed to process resource usage data');
    } finally {
      setLoadingResourceUsage(false);
    }
  };

  processResourceUsageData();
}, [documents]); */

// Pie Chart Component
const renderPieChart = () => {
  if (documentTypes.length === 0) return null;
  
  const total = documentTypes.reduce((sum, item) => sum + item.count, 0);
  //const colors = ['#3b82f6', '#2563eb', '#1d4ed8', '#1e40af', '#1e3a8a', '#172554', '#0f172a', '#020617'];
      const colors = [
      '#3b82f6', // Blue
      '#ef4444', // Red
      '#10b981', // Green
      '#f59e0b', // Amber
      '#8b5cf6', // Purple
      '#ec4899', // Pink
      '#06b6d4', // Cyan
      '#f97316'  // Orange
    ];
      
  let currentAngle = 0;
  const radius = 80;
  const centerX = 120;
  const centerY = 120;
  
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '24px', height: '100%' }}>
      <div style={{ position: 'relative' }}>
        <svg width="240" height="240" style={{ transform: 'rotate(-90deg)' }}>
          {documentTypes.slice(0, 8).map((item, index) => {
            const percentage = (item.count / total) * 100;
            const angle = (item.count / total) * 360;
            const startAngle = currentAngle;
            const endAngle = currentAngle + angle;
            
            const startAngleRad = (startAngle * Math.PI) / 180;
            const endAngleRad = (endAngle * Math.PI) / 180;
            
            const x1 = centerX + radius * Math.cos(startAngleRad);
            const y1 = centerY + radius * Math.sin(startAngleRad);
            const x2 = centerX + radius * Math.cos(endAngleRad);
            const y2 = centerY + radius * Math.sin(endAngleRad);
            
            const largeArcFlag = angle > 180 ? 1 : 0;
            
            const pathData = [
              `M ${centerX} ${centerY}`,
              `L ${x1} ${y1}`,
              `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
              'Z'
            ].join(' ');
            
            currentAngle += angle;
            return (
              <path
                key={index}
                d={pathData}
                fill={colors[index % colors.length]}
                stroke="var(--bg-primary)"
                strokeWidth="2"
                style={{ 
                  cursor: 'pointer',
                  transition: 'transform 0.2s ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'scale(1.05)';
                  e.currentTarget.style.transformOrigin = `${centerX}px ${centerY}px`;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'scale(1)';
                }}
              />
            );
          })}
        </svg>
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%) rotate(90deg)',
          textAlign: 'center',
          color: 'var(--text-primary)',
          fontSize: '0.875rem',
          fontWeight: 600
        }}>
          <div>{total}</div>
          <div style={{ fontSize: '0.75rem', fontWeight: 400 }}>Total</div>
        </div>
      </div>
      
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {documentTypes.slice(0, 8).map((item, index) => {
          const percentage = ((item.count / total) * 100).toFixed(1);
          return (
            <div key={index} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{
                width: '12px',
                height: '12px',
                backgroundColor: colors[index % colors.length],
                borderRadius: '2px',
                flexShrink: 0
              }} />
              <div style={{ 
                fontSize: '0.875rem', 
                color: 'var(--text-primary)', 
                fontWeight: 500,
                textTransform: 'uppercase',
                minWidth: '60px'
              }}>
                {item.type}
              </div>
              <div style={{ 
                fontSize: '0.875rem', 
                color: 'var(--text-secondary)',
                marginLeft: 'auto'
              }}>
                {item.count} ({percentage}%)
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Resource Usage Chart Component
const renderResourceUsageChart = () => {
  if (resourceUsageData.length === 0) return null;

  // Helper function to format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  // Helper function to format processing time
  const formatProcessingTime = (seconds: number): string => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return remainingSeconds > 0 ? `${minutes}m ${remainingSeconds}s` : `${minutes}m`;
  };

  // Sort data based on selected metric
  const sortedData = [...resourceUsageData].sort((a, b) => {
    if (resourceMetric === 'size') {
      return b.size - a.size; // Largest to smallest
    } else {
      return b.processingTime - a.processingTime; // Longest to shortest
    }
  });

  // Take top 10 documents to avoid overcrowding
  const displayData = sortedData.slice(0, 10);
  
  // Calculate max value for scaling
  const maxValue = resourceMetric === 'size' 
    ? Math.max(...displayData.map(d => d.size))
    : Math.max(...displayData.map(d => d.processingTime));

  //const colors = ['#3b82f6', '#2563eb', '#1d4ed8', '#1e40af', '#1e3a8a', '#172554', '#0f172a', '#020617'];
        const colors = [
        '#3b82f6', // Blue
        '#ef4444', // Red
        '#10b981', // Green
        '#f59e0b', // Amber
        '#8b5cf6', // Purple
        '#ec4899', // Pink
        '#06b6d4', // Cyan
        '#f97316'  // Orange
      ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '16px' }}>
      {/* Chart Area */}
      <div style={{ flex: 1, display: 'flex', alignItems: 'end', gap: '12px', padding: '0 16px 60px 16px' }}>
        {displayData.map((item, index) => {
          const value = resourceMetric === 'size' ? item.size : item.processingTime;
          const height = maxValue > 0 ? (value / maxValue) * 180 : 0; // Max height 180px to leave space for labels
          const displayValue = resourceMetric === 'size' 
            ? formatFileSize(item.size)
            : formatProcessingTime(item.processingTime);

          return (
            <div key={item.id} style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center',
              flex: 1,
              minWidth: '80px',
              position: 'relative'
            }}>
              {/* Value Label Above Bar */}
              <div style={{
                fontSize: '0.8rem',
                fontWeight: 600,
                color: '#374151',
                marginBottom: '4px',
                textAlign: 'center',
                background: 'rgba(255, 255, 255, 0.9)',
                padding: '2px 6px',
                borderRadius: '4px',
                border: '1px solid #e5e7eb',
                boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)'
              }}>
                {displayValue}
              </div>

              {/* Bar */}
              <div style={{
                width: '100%',
                maxWidth: '50px',
                height: `${height}px`,
                backgroundColor: colors[index % colors.length],
                borderRadius: '4px 4px 0 0',
                position: 'relative',
                transition: 'all 0.3s ease',
                cursor: 'pointer',
                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'scaleY(1.05)';
                e.currentTarget.style.filter = 'brightness(1.1)';
                e.currentTarget.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.15)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'scaleY(1)';
                e.currentTarget.style.filter = 'brightness(1)';
                e.currentTarget.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.1)';
              }}
              title={`${item.name}: ${displayValue}`}
              />
              
              {/* Document Name */}
              <div style={{
                marginTop: '12px',
                fontSize: '0.8rem',
                fontWeight: 500,
                color: '#374151',
                textAlign: 'center',
                maxWidth: '100px',
                lineHeight: '1.2',
                wordBreak: 'break-word',
                background: 'rgba(249, 250, 251, 0.9)',
                padding: '4px 6px',
                borderRadius: '4px',
                border: '1px solid #e5e7eb'
              }}
              title={item.name}
              >
                {item.name.length > 15 ? item.name.substring(0, 15) + '...' : item.name}
              </div>
            </div>
          );
        })}
      </div>

      {/* Y-axis label */}
      <div style={{
        position: 'absolute',
        left: '8px',
        top: '50%',
        transform: 'rotate(-90deg) translateX(-50%)',
        transformOrigin: 'center',
        fontSize: '0.8rem',
        color: '#374151',
        fontWeight: 600
      }}>
        {resourceMetric === 'size' ? 'File Size' : 'Processing Time'}
      </div>
    </div>
  );
};

  /* COMMENTED OUT - Now handled by unified fetch
  // Fetch upload activity data
  useEffect(() => {
    const fetchUploadActivity = async () => {
      const token = getToken();
      if (!token) {
        console.warn('No authentication token found, using empty activity data');
        setLoadingActivity(false);
        return;
      }

      try {
        setLoadingActivity(true);
        setActivityError(null);
        
        const response = await fetch('http://localhost:8000/api/profile/me', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (data && data.upload_activity) {
          setDocumentActivityData(data.upload_activity);
        } else {
          throw new Error('No upload activity data found');
        }
      } catch (err) {
        console.error('Error fetching upload activity:', err);
        setActivityError('Failed to load upload activity data');
      } finally {
        setLoadingActivity(false);
      }
    };

    fetchUploadActivity();
  }, []); */
  
  // Mock data fallback for development
  const mockStorageData = {
    used: 756, // 756MB used
    total: 2048 // 2GB total
  };

  // Document preview handler
  const previewDocumentHandler = async (doc: DocumentWithSummary) => {
    setLoadingPreview(true)
    setPreviewDocument(doc)
    setShowPreview(true)

    try {
      const token = getToken()
      if (!token) return

      const response = await fetch(`http://localhost:8000/api/documents/${doc.id}/download`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      })

      if (response.ok) {
        const data = await response.json()
        setPreviewUrl(data.download_url)
      } else {
        console.error("Failed to get preview URL")
        alert("Failed to load document preview")
      }
    } catch (err) {
      console.error("Error getting preview URL:", err)
      alert("Error loading document preview")
    } finally {
      setLoadingPreview(false)
    }
  }

  // Close preview
  const closePreview = () => {
    setShowPreview(false)
    setPreviewDocument(null)
    setPreviewUrl(null)
  }

  /* COMMENTED OUT - Now handled by unified fetch
  // Fetch storage usage data from API
  useEffect(() => {
    const fetchStorageUsage = async () => {
      const token = getToken();
      if (!token) {
        console.warn('No authentication token found, using mock data');
        setStorageUsage(mockStorageData);
        setLoadingStorage(false);
        return;
      }

      try {
        setLoadingStorage(true);
        
        // First try to get from localStorage cache if it's fresh (less than 5 minutes old)
        const cachedData = localStorage.getItem('cachedStorage');
        const cacheTime = localStorage.getItem('cachedStorageTime');
        const now = Date.now();
        const fiveMinutes = 5 * 60 * 1000; // 5 minutes in milliseconds
        
        if (cachedData && cacheTime && (now - parseInt(cacheTime)) < fiveMinutes) {
          const parsedData = JSON.parse(cachedData);
          setStorageUsage(parsedData);
          setStorageError(null);
          setLoadingStorage(false);
          return;
        }

        // Fetch from API - Fixed URL to match backend endpoint
        const response = await fetch('http://localhost:8000/api/analytics/document-uploads-over-time?period=30d', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (data && data.summary) {
          // Convert bytes to MB (1 MB = 1024 * 1024 bytes)
          const usedMB = Math.round((data.summary.totalSize || 0) / (1024 * 1024));
          // Default to 5GB total storage if not provided
          const totalMB = 5 * 1024; // 5GB in MB
          
          const storageData = { 
            used: usedMB, 
            total: totalMB 
          };
          
          setStorageUsage(storageData);
          setStorageError(null);
          
          // Cache the data
          try {
            localStorage.setItem('cachedStorage', JSON.stringify(storageData));
            localStorage.setItem('cachedStorageTime', now.toString());
          } catch (e) {
            console.warn('Failed to cache storage data', e);
          }
        } else {
          throw new Error('Invalid data format from API');
        }
      } catch (err) {
        console.error('Error fetching storage usage:', err);
        // Fallback to mock data in case of error
        setStorageUsage(mockStorageData);
        setStorageError('Using sample data (API unavailable)');
      } finally {
        setLoadingStorage(false);
      }
    };

    fetchStorageUsage();
  }, []); */

  /* COMMENTED OUT - Now handled by unified fetch
  // Fetch user documents with JWT authentication and fallback
  useEffect(() => {
    const fetchDocuments = async () => {
      const tryFallback = async () => {
        try {
          const userStr = localStorage.getItem("user")
          if (!userStr) {
            throw new Error("No user info found for fallback fetch")
          }
          const user = JSON.parse(userStr)
          const userId = user?.id || user?.user?.id || user?.user_id
          if (!userId) {
            throw new Error("No user_id in local storage user")
          }
          const res = await fetch(`http://localhost:8000/api/documents/by-user?user_id=${encodeURIComponent(userId)}`)
          if (!res.ok) {
            throw new Error("Fallback fetch failed")
          }
          const data = await res.json()
          setDocuments(data.documents || [])
          setError(null)
        } catch (e) {
          console.error("Fallback documents fetch error:", e)
          setError("Failed to load documents")
        } finally {
          setLoading(false)
        }
      }

      try {
        const token = getToken()
        if (!token) {
          await tryFallback()
          return
        }

        const response = await fetch("http://localhost:8000/api/documents/", {
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        })

        if (response.status === 401) {
          localStorage.removeItem("token")
          await tryFallback()
          return
        }

        if (!response.ok) {
          await tryFallback()
          return
        }

        const data = await response.json()
        setDocuments(data.documents || [])
        setLoading(false)
      } catch (err) {
        console.error("Error fetching documents:", err)
        await tryFallback()
      }
    }

    fetchDocuments()
  }, []) */

  // Format date to relative time
  const formatRelativeTime = (isoString: string): string => {
    const past = new Date(isoString)
    const now = new Date()
    const diffInMs = now.getTime() - past.getTime()
    const diffInHours = diffInMs / (1000 * 60 * 60)
    const diffInDays = diffInHours / 24

    if (diffInHours < 1) return "Less than an hour ago"
    if (diffInHours < 24) return `${Math.floor(diffInHours)} hours ago`
    if (diffInDays < 7) return `${Math.floor(diffInDays)} days ago`
    return past.toLocaleDateString()
  }

  // Compute stats from real documents
  const stats = useMemo(() => {
    const total = documents.length
    const today = new Date().setHours(0, 0, 0, 0)
    const processedToday = documents.filter(
      (doc) =>
        doc.processing_status === "completed" &&
        new Date(doc.upload_date).getTime() >= today
    ).length
    const inQueue = documents.filter(doc => doc.processing_status === "processing").length
    const successRate = total > 0 ? ((documents.filter(doc => doc.processing_status === "completed").length / total) * 100).toFixed(1) : "0"

    return [
      {
        title: "Total Documents",
        value: total.toLocaleString(),
        change: "+12%",
        icon: "fas fa-file-alt",
        positive: true
      },
      {
        title: "Processed Today",
        value: processedToday.toString(),
        change: "+23%",
        icon: "fas fa-check-circle",
        positive: true
      },
      {
        title: "Processing Queue",
        value: inQueue.toString(),
        change: inQueue > 0 ? "-5%" : "0%",
        icon: "fas fa-clock",
        positive: inQueue === 0
      },
      {
        title: "Success Rate",
        value: `${successRate}%`,
        change: "+0.5%",
        icon: "fas fa-chart-line",
        positive: true
      },
    ]
  }, [documents])

  // Format recent documents with summary state
  const recentDocuments = useMemo((): DocumentWithSummary[] => {
    const formatted = documents
      .sort((a, b) => new Date(b.upload_date).getTime() - new Date(a.upload_date).getTime())
      .map((doc): DocumentWithSummary => ({
        id: doc.id,
        name: doc.original_filename,
        type: doc.content_type?.split("/")[1]?.toUpperCase() || "FILE",
        status: doc.processing_status === "completed" ? "Completed" :
                doc.processing_status === "processing" ? "Processing" : "Failed",
        uploadedAt: formatRelativeTime(doc.upload_date),
        confidence: doc.processing_status === "completed" ? 95 : null,
        showSummaryOptions: false,
        selectedModel: null,
        currentSummary: null,
        loadingSummary: false,
        generatingNew: false,
        summaryError: null
      }))

    setDocumentsWithSummary(formatted)
    return formatted
  }, [documents])

  // Dynamic summary functions
  const selectModel = async (docId: string, modelId: string) => {
    setCurrentSummaryDoc(prev => prev ? {
      ...prev,
      selectedModel: modelId,
      loadingSummary: true,
      summaryError: null,
      currentSummary: null
    } : null)

    try {
      const token = getToken()
      if (!token) return

      const response = await fetch(`http://localhost:8000/api/summarize/document/${docId}`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      })

      if (response.status === 401) {
        localStorage.removeItem("token")
        localStorage.removeItem("user")
        setError("Session expired. Please log in again.")
        return
      }

      if (response.ok) {
        const data = await response.json()
        if (data.success && data.summaries) {
          const matchingSummaries = data.summaries.filter((summary: Summary) => 
            summary.summary_type === modelId || 
            summary.summary_type.toLowerCase() === modelId.toLowerCase() ||
            summary.summary_type.replace(/[\s_-]/g, '').toLowerCase() === modelId.replace(/[\s_-]/g, '').toLowerCase()
          )

          if (matchingSummaries.length > 0) {
            const latestSummary = matchingSummaries.sort((a: Summary, b: Summary) => 
              new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
            )[0]

            setCurrentSummaryDoc(prev => prev ? {
              ...prev,
              currentSummary: latestSummary,
              loadingSummary: false
            } : null)
          } else {
            setCurrentSummaryDoc(prev => prev ? {
              ...prev,
              currentSummary: null,
              loadingSummary: false
            } : null)
          }
        } else {
          setCurrentSummaryDoc(prev => prev ? {
            ...prev,
            currentSummary: null,
            loadingSummary: false
          } : null)
        }
      } else {
        console.error("Failed to fetch summaries")
        setCurrentSummaryDoc(prev => prev ? {
          ...prev,
          loadingSummary: false,
          summaryError: "Failed to load summary"
        } : null)
      }
    } catch (err) {
      console.error("Error fetching summaries:", err)
      setCurrentSummaryDoc(prev => prev ? {
        ...prev,
        loadingSummary: false,
        summaryError: "Failed to load summary"
      } : null)
    }
  }

  const generateSummary = async (docId: string, summaryType: string) => {
    setCurrentSummaryDoc(prev => prev ? {
      ...prev,
      generatingNew: true,
      summaryError: null
    } : null)

    try {
      const token = getToken()
      if (!token) return

      const response = await fetch("http://localhost:8000/api/summarize/", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          document_id: docId,
          summary_type: summaryType
        })
      })

      if (response.status === 401) {
        localStorage.removeItem("token")
        localStorage.removeItem("user")
        setError("Session expired. Please log in again.")
        return
      }

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Failed to generate summary")
      }

      const data = await response.json()
      
      if (data.success) {
        const newSummary: Summary = {
          id: Date.now(),
          summary_type: data.summary_type,
          summary_text: data.summary_text,
          word_count: data.word_count,
          model_used: data.model_used,
          created_at: data.created_at,
          from_cache: data.from_cache,
          document_type: data.document_type,
          key_points: data.key_points
        }

        setCurrentSummaryDoc(prev => prev ? {
          ...prev,
          currentSummary: newSummary,
          generatingNew: false
        } : null)
      } else {
        throw new Error("Summary generation failed")
      }
    } catch (err: any) {
      console.error("Error generating summary:", err)
      setCurrentSummaryDoc(prev => prev ? {
        ...prev,
        generatingNew: false,
        summaryError: `Failed to generate summary: ${err.message}`
      } : null)
    }
  }

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      alert("Summary copied to clipboard!")
    } catch (err) {
      console.error("Failed to copy:", err)
      alert("Failed to copy summary")
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const getSummaryTypeColor = (type: string) => {
    const colors: { [key: string]: string } = {
      "Brief Summary": "#28a745",
      "brief": "#28a745",
      "Detailed Summary": "#ffc107", 
      "detailed": "#ffc107",
      "Domain Specific Summary": "#17a2b8",
      "Domain-Specific": "#17a2b8",
      "domain_specific": "#17a2b8"
    }
    return colors[type] || "#6c757d"
  }

  // Other handler functions
  const handleChatWithDoc = (doc: DocumentWithSummary) => {
    // MVP: Disable chat functionality
    // MVP: Chat functionality disabled
    // setSelectedDocument(doc)
    // MVP: Chat functionality disabled - show alert instead
  }

  const handleSummarizeDoc = (doc: DocumentWithSummary) => {
    setSelectedDocumentForSummary({
      id: doc.id,
      name: doc.name
    })
    setCurrentSummaryDoc({
      ...doc,
      showSummaryOptions: false,
      selectedModel: null,
      currentSummary: null,
      loadingSummary: false,
      generatingNew: false,
      summaryError: null
    })
    setSummaryModalOpen(true)
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="error-message max-w-md w-full">
          <div className="flex items-center gap-3">
            <i className="fas fa-exclamation-triangle text-2xl text-yellow-500"></i>
            <p>{error}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="main-container">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          {stats.map((stat) => (
            <div key={stat.title} className="stats-card fade-in">
              <div className="stats-header">
                <i className={`stats-icon ${stat.icon}`}></i>
                <span className={`stats-change ${stat.positive ? 'positive' : 'negative'}`}>
                  {stat.change}
                </span>
              </div>
              <div className="stats-content">
                <div className="stats-value">{stat.value}</div>
                <div className="stats-title">{stat.title}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Charts Row */}
        {/* Charts Row - Activity + Document Types */}
<div style={{
  display: 'grid',
  gridTemplateColumns: '1fr 1fr',
  gap: '24px',
  marginBottom: '24px',
  width: '100%'
}}>
  {/* Document Activity Chart */}
  <div style={{
    backgroundColor: 'var(--bg-primary)',
    borderRadius: '8px',
    boxShadow: 'var(--card-shadow)',
    padding: '16px',
    height: '400px',
    display: 'flex',
    flexDirection: 'column',
    border: '1px solid var(--border-color)'
  }}>
    <DocumentActivityChart 
      data={documentActivityData} 
      loading={loadingActivity}
      error={activityError}
    />
  </div>

  {/* Document Type Distribution */}
  <div style={{
    backgroundColor: 'var(--bg-primary)',
    borderRadius: '8px',
    boxShadow: 'var(--card-shadow)',
    padding: '16px',
    height: '400px',
    display: 'flex',
    flexDirection: 'column',
    border: '1px solid var(--border-color)'
  }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
      <h3 style={{ fontSize: '1.1rem', fontWeight: 600, margin: 0, color: 'var(--text-primary)' }}>
        Document Types
      </h3>
      <button
        onClick={() => setChartType(chartType === 'bar' ? 'pie' : 'bar')}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '6px 12px',
          backgroundColor: chartType === 'pie' ? '#3b82f6' : '#f3f4f6',
          color: chartType === 'pie' ? 'white' : '#4b5563',
          border: 'none',
          borderRadius: '6px',
          fontSize: '0.75rem',
          fontWeight: 500,
          cursor: 'pointer',
          transition: 'all 0.2s ease',
          boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)'
        }}
        onMouseEnter={(e) => {
          if (chartType === 'bar') {
            e.currentTarget.style.backgroundColor = '#e5e7eb';
          }
        }}
        onMouseLeave={(e) => {
          if (chartType === 'bar') {
            e.currentTarget.style.backgroundColor = '#f3f4f6';
          }
        }}
      >
        <i className={chartType === 'bar' ? 'fas fa-chart-pie' : 'fas fa-chart-bar'} style={{ fontSize: '0.75rem' }}></i>
        {chartType === 'bar' ? 'Pie Chart' : 'Bar Chart'}
      </button>
    </div>
    {loadingTypes ? (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-secondary)' }}>
        Loading...
      </div>
    ) : typesError ? (
      <div style={{ color: 'var(--danger-color)', fontSize: '0.875rem', textAlign: 'center', marginTop: '1rem' }}>
        {typesError}
      </div>
    ) : documentTypes.length === 0 ? (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-tertiary)' }}>
        No data
      </div>
    ) : chartType === 'pie' ? (
      renderPieChart()
    ) : (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', flex: 1, overflowY: 'auto' }}>
        {documentTypes.slice(0, 8).map((item, index) => {
          const maxCount = documentTypes[0]?.count || 1;
          const width = maxCount > 0 ? (item.count / maxCount) * 100 : 0;
          // const blueShades = ['#3b82f6', '#2563eb', '#1d4ed8', '#1e40af', '#1e3a8a', '#172554'];
          const colors = [
                '#3b82f6', // Blue
                '#ef4444', // Red
                '#10b981', // Green
                '#f59e0b', // Amber
                '#8b5cf6', // Purple
                '#ec4899', // Pink
                '#06b6d4', // Cyan
                '#f97316'  // Orange
              ];
                        return (
            <div key={index} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ 
                width: '80px', 
                fontSize: '0.875rem', 
                color: '#4b5563', 
                fontWeight: 500,
                textTransform: 'uppercase'
              }}>
                {item.type}
              </div>
              <div style={{ 
                flex: 1, 
                height: '24px', 
                backgroundColor: '#e2e8f0', 
                borderRadius: '4px',
                position: 'relative'
              }}>
                <div
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    height: '100%',
                    width: `${width}%`,
                    //backgroundColor: blueShades[index % blueShades.length],
                    backgroundColor: colors[index % colors.length],
                    borderRadius: '4px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'flex-end',
                    paddingRight: '8px',
                    color: 'white',
                    fontSize: '0.75rem',
                    fontWeight: 600
                  }}
                >
                  {item.count}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    )}
  </div>
</div>

        {/* Resource Usage Chart */}
        <div style={{
          backgroundColor: 'var(--bg-primary)',
          borderRadius: '8px',
          boxShadow: 'var(--card-shadow)',
          padding: '16px',
          height: '400px',
          display: 'flex',
          flexDirection: 'column',
          marginBottom: '24px',
          position: 'relative',
          border: '1px solid var(--border-color)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, margin: 0, color: 'var(--text-primary)' }}>
              Resource Usage
            </h3>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={() => setResourceMetric('size')}
                style={{
                  padding: '6px 12px',
                  backgroundColor: resourceMetric === 'size' ? '#3b82f6' : '#f3f4f6',
                  color: resourceMetric === 'size' ? 'white' : '#4b5563',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '0.75rem',
                  fontWeight: 500,
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)'
                }}
                onMouseEnter={(e) => {
                  if (resourceMetric !== 'size') {
                    e.currentTarget.style.backgroundColor = '#e5e7eb';
                  }
                }}
                onMouseLeave={(e) => {
                  if (resourceMetric !== 'size') {
                    e.currentTarget.style.backgroundColor = '#f3f4f6';
                  }
                }}
              >
                <i className="fas fa-weight" style={{ fontSize: '0.75rem', marginRight: '4px' }}></i>
                By Storage Size
              </button>
              <button
                onClick={() => setResourceMetric('time')}
                style={{
                  padding: '6px 12px',
                  backgroundColor: resourceMetric === 'time' ? '#3b82f6' : '#f3f4f6',
                  color: resourceMetric === 'time' ? 'white' : '#4b5563',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '0.75rem',
                  fontWeight: 500,
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)'
                }}
                onMouseEnter={(e) => {
                  if (resourceMetric !== 'time') {
                    e.currentTarget.style.backgroundColor = '#e5e7eb';
                  }
                }}
                onMouseLeave={(e) => {
                  if (resourceMetric !== 'time') {
                    e.currentTarget.style.backgroundColor = '#f3f4f6';
                  }
                }}
              >
                <i className="fas fa-clock" style={{ fontSize: '0.75rem', marginRight: '4px' }}></i>
                By Processing Time
              </button>
            </div>
          </div>
          {loadingResourceUsage ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-secondary)' }}>
              Loading...
            </div>
          ) : resourceUsageError ? (
            <div style={{ color: 'var(--danger-color)', fontSize: '0.875rem', textAlign: 'center', marginTop: '1rem' }}>
              {resourceUsageError}
            </div>
          ) : resourceUsageData.length === 0 ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-tertiary)' }}>
              No data available
            </div>
          ) : (
            renderResourceUsageChart()
          )}
        </div>

        {/* Search and Chat Feature */}
        <div className="feature-container">
          <div className="tabs-container d-flex">
            <button
              className={`tab-btn ${activeView === 'documents' ? 'active' : ''}`}
              onClick={() => setActiveView('documents')}
            >
              <i className="fas fa-search me-2"></i>Search Documents
            </button>
            <button
              className={`tab-btn ${activeView === 'chat' ? 'active' : ''}`}
              onClick={() => alert('🚧 Ask DocuMind AI feature is coming soon!')}
            >
              <i className="fas fa-robot me-2"></i>Ask DocuMind AI
            </button>
          </div>

          <div className="tab-content-container">
            {activeView === 'documents' && (
              <div id="search-tab" className="tab-content active">
                <div className="search-input-group">
                  <span className="search-icon"><i className="fas fa-search"></i></span>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Search across all your documents..."
                  />
                </div>

                <div id="searchResults">
                  <h5 className="mb-4"><i className="fas fa-history me-2"></i>Recent Documents</h5>

                  {documentsWithSummary.length === 0 ? (
                    <div className="text-center py-5">
                      <i className="fas fa-file-alt empty-state-icon"></i>
                      <p className="mt-3 text-muted">No documents uploaded yet.</p>
                    </div>
                  ) : (
                    documentsWithSummary.slice(0, 10).map((doc) => (
                      <div key={doc.id} className="result-item">
                        <div className="d-flex">
                          <div className="result-icon">
                            <i className="fas fa-file-invoice"></i>
                          </div>
                          <div className="flex-grow-1">
                            <div className="result-title">
                              {doc.name}
                              <span className="doc-type-tag tag-invoice">{doc.type}</span>
                            </div>
                            {/* <div className="result-snippet">
                              Financial summary for Q4 2023 showing a 12% increase in revenue compared to previous year...
                            </div> */}
                            <div className="result-meta">
                              PDF • 2.4 MB • Last accessed: {doc.uploadedAt}
                            </div>
                            <div className="result-actions">
                              <button
                                className="btn summarize-btn"
                                onClick={() => handleSummarizeDoc(doc)}
                              >
                                <i className="fas fa-file-contract me-1"></i>Summarize
                              </button>
                              <button
                                className="btn chat-doc-btn"
                                onClick={() => handleChatWithDoc(doc)}
                              >
                                <i className="fas fa-comments me-1"></i>Chat with Doc
                              </button>
                              <button
                                className="btn preview-btn"
                                onClick={() => previewDocumentHandler(doc)}
                              >
                                <i className="fas fa-eye me-1"></i>Preview
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
                <div className="chat-input-group" style={{display: 'none'}}>
                  <input
                    type="text"
                    className="form-control"
                    placeholder={selectedDocument
                      ? `Ask about ${selectedDocument.name}...`
                      : "Search functionality coming soon..."
                    }
                  />
                  <button className="btn btn-primary">
                    <i className="fas fa-paper-plane"></i>
                  </button>
                </div>
              </div>
            )}

            {/* Chat Tab */}
            {activeView === 'chat' && (
              <div className="tab-content active">
                {selectedDocument && (
                  <div className="selected-document-context">
                    <div className="context-header">
                      <i className="fas fa-file-alt"></i>
                      <span>Chatting about: {selectedDocument.name}</span>
                      <button 
                        className="btn btn-sm btn-outline-secondary"
                        onClick={() => setSelectedDocument(null)}
                      >
                        <i className="fas fa-times"></i>
                      </button>
                    </div>
                  </div>
                )}
                <div className="chat-messages">
                  <div className="message bot">
                    <div className="message-content">
                      {selectedDocument 
                        ? `Hello! I'm ready to help you with "${selectedDocument.name}". What would you like to know about this document?`
                        : "Hello! I'm DocuMind AI. I can help you analyze and understand your documents. What would you like to know?"
                      }
                    </div>
                  </div>
                  {selectedDocument && (
                    <div className="message bot">
                      <div className="message-content">
                        I can see you've selected "{selectedDocument.name}". I can help you:
                        <ul>
                          <li>Summarize key points</li>
                          <li>Answer specific questions about the content</li>
                          <li>Extract important data or insights</li>
                          <li>Compare with other documents</li>
                        </ul>
                        What would you like to explore?
                      </div>
                    </div>
                  )}
                </div>
                <div className="chat-input-group" style={{display: 'none'}}>
                  <input 
                    type="text" 
                    className="form-control" 
                    placeholder={selectedDocument 
                      ? `Ask about ${selectedDocument.name}...` 
                      : "Search functionality coming soon..."
                    } 
                  />
                  <button className="btn btn-primary">
                    <i className="fas fa-paper-plane"></i>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Document Preview Modal */}
        {showPreview && (
          <div style={modalStyles.overlay}>
            <div style={modalStyles.container}>
              <div style={modalStyles.header}>
                <div style={modalStyles.title}>
                  <h3 style={modalStyles.titleH3}>{previewDocument?.name}</h3>
                  <p style={modalStyles.titleP}>{previewDocument?.type} • {previewDocument?.uploadedAt}</p>
                </div>
                <button
                  onClick={closePreview}
                  style={modalStyles.closeButton}
                >
                  ✕
                </button>
              </div>

              <div style={modalStyles.body}>
                {loadingPreview ? (
                  <div style={modalStyles.loading}>
                    <div style={modalStyles.loadingSpinner}></div>
                    <p>Loading document preview...</p>
                  </div>
                ) : previewUrl ? (
                  <div style={modalStyles.viewer}>
                    {previewDocument?.type === 'PDF' ? (
                      <iframe
                        src={previewUrl}
                        style={modalStyles.iframe}
                        title="Document Preview"
                      />
                    ) : previewDocument?.type?.startsWith('image/') ||
                         ['JPG', 'JPEG', 'PNG', 'GIF'].includes(previewDocument?.type || '') ? (
                      <div style={modalStyles.imageViewer}>
                        <img
                          src={previewUrl}
                          alt="Document Preview"
                          style={modalStyles.image}
                        />
                      </div>
                    ) : (
                      <div style={modalStyles.unsupported}>
                        <div style={modalStyles.fileIcon}><i className="fas fa-file"></i></div>
                        <h4 style={modalStyles.titleH3}>Preview not available</h4>
                        <p style={modalStyles.titleP}>Preview not available for this file type</p>
                        <a
                          href={previewUrl}
                          download={previewDocument?.name}
                          style={modalStyles.downloadBtn}
                        >
                          <i className="fas fa-download"></i>
                          Download Document
                        </a>
                      </div>
                    )}
                  </div>
                ) : (
                  <div style={modalStyles.error}>
                    <div style={modalStyles.errorIcon}><i className="fas fa-exclamation-triangle"></i></div>
                    <h4 style={modalStyles.errorH4}>Failed to load document preview</h4>
                    <p style={modalStyles.errorP}>Unable to load the document preview</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes fadeInModal {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        @keyframes slideInModal {
          from {
            opacity: 0;
            transform: scale(0.95) translateY(-20px);
          }
          to {
            opacity: 1;
            transform: scale(1) translateY(0);
          }
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
          .modal-overlay { padding: 10px; }
          .modal-container { width: 95vw; height: 95vh; }
          .modal-header { padding: 16px 20px; }
          .modal-header h3 { font-size: 1.125rem; }
          .image-viewer { padding: 16px; }
        }

        ${showPreview ? 'body { overflow: hidden; }' : ''}
      `}</style>

      {/* Enhanced Summary Modal */}
      {summaryModalOpen && selectedDocumentForSummary && currentSummaryDoc && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.75)',
            backdropFilter: 'blur(8px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
            padding: '20px'
          }}
          onClick={() => setSummaryModalOpen(false)}
        >
          <div 
            style={{
              backgroundColor: 'var(--bg-primary)',
              borderRadius: '16px',
              maxWidth: '900px',
              width: '90%',
              maxHeight: '90vh',
              overflow: 'auto',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
              position: 'relative'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ 
              padding: '1.5rem', 
              borderBottom: '1px solid var(--border-color)', 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              background: 'var(--bg-tertiary)'
            }}>
              <div>
                <h5 style={{ margin: 0, fontSize: '1.25rem', fontWeight: '600', color: 'var(--text-primary)' }}>
                  Document Summary
                </h5>
                <p style={{ margin: '4px 0 0 0', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                  {selectedDocumentForSummary.name}
                </p>
              </div>
              <button 
                onClick={() => setSummaryModalOpen(false)}
                style={{ 
                  background: 'none',
                  border: 'none', 
                  fontSize: '24px', 
                  cursor: 'pointer',
                  color: 'var(--text-secondary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: '8px',
                  borderRadius: '8px',
                  transition: 'all 0.2s ease'
                }}
              >
                ✕
              </button>
            </div>

            <div style={{ padding: '1.5rem' }}>
              {currentSummaryDoc.summaryError && (
                <div style={{ 
                  background: 'linear-gradient(135deg, #fed7d7, #feb2b2)',
                  color: '#742a2a',
                  padding: '1rem',
                  borderRadius: '8px',
                  marginBottom: '1rem',
                  borderLeft: '4px solid #e53e3e'
                }}>
                  <p style={{ margin: 0 }}>{currentSummaryDoc.summaryError}</p>
                </div>
              )}

              {/* Model Selection */}
              <div style={{ marginBottom: '1.5rem' }}>
                <h6 style={{ 
                  fontSize: '0.875rem', 
                  fontWeight: '500', 
                  color: '#374151',
                  marginBottom: '1rem' 
                }}>
                  Select Summary Type:
                </h6>
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
                  gap: '1rem' 
                }}>
                  {summaryOptions.map((option) => (
                    <button
                      key={option.id}
                      onClick={() => selectModel(selectedDocumentForSummary.id, option.id)}
                      disabled={currentSummaryDoc.loadingSummary || currentSummaryDoc.generatingNew}
                      style={{
                        background: currentSummaryDoc.selectedModel === option.id 
                          ? 'linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1))' 
                          : 'white',
                        border: currentSummaryDoc.selectedModel === option.id 
                          ? '2px solid #667eea' 
                          : '2px solid #e2e8f0',
                        borderRadius: '12px',
                        padding: '1.25rem',
                        cursor: currentSummaryDoc.loadingSummary || currentSummaryDoc.generatingNew ? 'not-allowed' : 'pointer',
                        transition: 'all 0.3s ease',
                        textAlign: 'left',
                        width: '100%',
                        opacity: currentSummaryDoc.loadingSummary || currentSummaryDoc.generatingNew ? 0.6 : 1
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
                        <i className={option.icon} style={{ 
                          fontSize: '1.25rem', 
                          color: '#667eea',
                          marginTop: '0.25rem' 
                        }}></i>
                        <div>
                          <div style={{ 
                            fontWeight: '600', 
                            fontSize: '0.95rem',
                            color: '#1f2937',
                            marginBottom: '0.5rem'
                          }}>
                            {option.name}
                          </div>
                          <div style={{ 
                            fontSize: '0.8rem', 
                            color: '#6b7280',
                            marginBottom: '0.5rem',
                            lineHeight: '1.4'
                          }}>
                            {option.description}
                          </div>
                          <div style={{ 
                            fontSize: '0.75rem', 
                            color: '#9ca3af',
                            fontWeight: '500'
                          }}>
                            Model: {option.model}
                          </div>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Summary Content Area */}
              {currentSummaryDoc.selectedModel && (
                <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: '1.5rem' }}>
                  {currentSummaryDoc.loadingSummary ? (
                    <div style={{ textAlign: 'center', padding: '3rem 1rem' }}>
                      <div style={{
                        width: '48px',
                        height: '48px',
                        border: '4px solid #e2e8f0',
                        borderTop: '4px solid #667eea',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite',
                        margin: '0 auto 1rem'
                      }}></div>
                      <p style={{ color: '#6b7280', fontSize: '0.9rem' }}>Loading summary...</p>
                    </div>
                  ) : currentSummaryDoc.currentSummary ? (
                    /* Show Existing Summary */
                    <div>
                      <div style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'space-between', 
                        marginBottom: '1rem' 
                      }}>
                        <h6 style={{ 
                          fontSize: '1rem', 
                          fontWeight: '600', 
                          color: '#1f2937',
                          margin: 0 
                        }}>
                          Summary Results
                        </h6>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          {currentSummaryDoc.currentSummary.from_cache && (
                            <span style={{
                              background: '#d1fae5',
                              color: '#065f46',
                              padding: '0.25rem 0.75rem',
                              borderRadius: '20px',
                              fontSize: '0.75rem',
                              fontWeight: '600'
                            }}>
                              From Cache
                            </span>
                          )}
                          <span style={{
                            backgroundColor: getSummaryTypeColor(currentSummaryDoc.currentSummary.summary_type),
                            color: 'white',
                            padding: '0.25rem 0.75rem',
                            borderRadius: '20px',
                            fontSize: '0.75rem',
                            fontWeight: '600'
                          }}>
                            {currentSummaryDoc.currentSummary.summary_type}
                          </span>
                        </div>
                      </div>

                      {/* Summary Details */}
                      <div style={{ 
                        background: '#f9fafb',
                        border: '1px solid #e5e7eb',
                        borderRadius: '8px',
                        padding: '1rem',
                        marginBottom: '1.5rem'
                      }}>
                        <div style={{ 
                          display: 'grid', 
                          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', 
                          gap: '1rem',
                          fontSize: '0.8rem'
                        }}>
                          <div>
                            <span style={{ color: '#6b7280' }}>Word Count:</span>{' '}
                            <strong>{currentSummaryDoc.currentSummary.word_count}</strong>
                          </div>
                          <div>
                            <span style={{ color: '#6b7280' }}>Model:</span>{' '}
                            <strong>{currentSummaryDoc.currentSummary.model_used}</strong>
                          </div>
                          <div>
                            <span style={{ color: '#6b7280' }}>Generated:</span>{' '}
                            <strong>{formatDate(currentSummaryDoc.currentSummary.created_at)}</strong>
                          </div>
                        </div>
                      </div>

                      {/* Summary Text */}
                      <div style={{ 
                        background: 'linear-gradient(135deg, #ebf4ff, #e6fffa)',
                        border: '2px solid #bee3f8',
                        borderLeft: '6px solid #4299e1',
                        borderRadius: '12px',
                        padding: '1.5rem',
                        marginBottom: '1.5rem'
                      }}>
                        <p style={{ 
                          color: '#2d3748', 
                          fontSize: '0.95rem', 
                          lineHeight: '1.6',
                          margin: 0,
                          whiteSpace: 'pre-wrap'
                        }}>
                          {currentSummaryDoc.currentSummary.summary_text}
                        </p>
                      </div>

                      {/* Key Points */}
                      {currentSummaryDoc.currentSummary.key_points && currentSummaryDoc.currentSummary.key_points.length > 0 && (
                        <div style={{ 
                          background: 'white',
                          border: '1px solid #e5e7eb',
                          borderRadius: '8px',
                          padding: '1.5rem',
                          marginBottom: '1.5rem'
                        }}>
                          <h6 style={{ 
                            fontSize: '0.9rem', 
                            fontWeight: '600', 
                            color: '#1f2937',
                            marginBottom: '1rem'
                          }}>
                            Key Points:
                          </h6>
                          <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
                            {currentSummaryDoc.currentSummary.key_points.map((point, index) => (
                              <li key={index} style={{ 
                                fontSize: '0.9rem',
                                color: '#4b5563',
                                marginBottom: '0.5rem',
                                lineHeight: '1.5'
                              }}>
                                {point}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Action Buttons */}
                      <div style={{ 
                        display: 'flex', 
                        gap: '0.75rem', 
                        flexWrap: 'wrap',
                        borderTop: '1px solid #e5e7eb',
                        paddingTop: '1.5rem'
                      }}>
                        <button 
                          onClick={() => copyToClipboard(currentSummaryDoc.currentSummary!.summary_text)}
                          style={{
                            background: 'linear-gradient(135deg, #667eea, #764ba2)',
                            color: 'white',
                            border: 'none',
                            padding: '0.75rem 1.5rem',
                            borderRadius: '8px',
                            fontSize: '0.85rem',
                            fontWeight: '600',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            transition: 'all 0.3s ease'
                          }}
                        >
                          <i className="fas fa-copy"></i>
                          Copy
                        </button>
                        <button style={{
                          background: 'linear-gradient(135deg, #48bb78, #38a169)',
                          color: 'white',
                          border: 'none',
                          padding: '0.75rem 1.5rem',
                          borderRadius: '8px',
                          fontSize: '0.85rem',
                          fontWeight: '600',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.5rem',
                          transition: 'all 0.3s ease'
                        }}>
                          <i className="fas fa-download"></i>
                          Export
                        </button>
                        <button 
                          onClick={() => generateSummary(selectedDocumentForSummary.id, currentSummaryDoc.selectedModel!)}
                          disabled={currentSummaryDoc.generatingNew}
                          style={{
                            background: currentSummaryDoc.generatingNew 
                              ? '#9ca3af' 
                              : 'linear-gradient(135deg, #ed8936, #dd6b20)',
                            color: 'white',
                            border: 'none',
                            padding: '0.75rem 1.5rem',
                            borderRadius: '8px',
                            fontSize: '0.85rem',
                            fontWeight: '600',
                            cursor: currentSummaryDoc.generatingNew ? 'not-allowed' : 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            marginLeft: 'auto',
                            transition: 'all 0.3s ease'
                          }}
                        >
                          {currentSummaryDoc.generatingNew ? (
                            <>
                              <div style={{
                                width: '16px',
                                height: '16px',
                                border: '2px solid transparent',
                                borderTop: '2px solid white',
                                borderRadius: '50%',
                                animation: 'spin 1s linear infinite'
                              }}></div>
                              Generating...
                            </>
                          ) : (
                            <>
                              <i className="fas fa-sync-alt"></i>
                              Regenerate
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  ) : (
                    /* Show Generate Option */
                    <div style={{ textAlign: 'center', padding: '3rem 1rem' }}>
                      <div style={{ 
                        fontSize: '3rem', 
                        marginBottom: '1rem',
                        color: '#9ca3af' 
                      }}>
                        <i className="fas fa-robot"></i>
                      </div>
                      <h6 style={{ 
                        color: '#374151', 
                        fontSize: '1.1rem',
                        fontWeight: '600',
                        marginBottom: '0.5rem'
                      }}>
                        Summary Not Available
                      </h6>
                      <p style={{ 
                        color: '#6b7280', 
                        fontSize: '0.9rem',
                        marginBottom: '2rem',
                        lineHeight: '1.5'
                      }}>
                        No summary available for this document with the selected model.
                        <br />
                        Generate a new summary to get insights from your document.
                      </p>
                      
                      <button
                        onClick={() => generateSummary(selectedDocumentForSummary.id, currentSummaryDoc.selectedModel!)}
                        disabled={currentSummaryDoc.generatingNew}
                        style={{
                          background: currentSummaryDoc.generatingNew 
                            ? '#9ca3af' 
                            : 'linear-gradient(135deg, #667eea, #764ba2)',
                          color: 'white',
                          border: 'none',
                          padding: '1rem 2rem',
                          borderRadius: '12px',
                          fontSize: '1rem',
                          fontWeight: '600',
                          cursor: currentSummaryDoc.generatingNew ? 'not-allowed' : 'pointer',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '0.75rem',
                          transition: 'all 0.3s ease',
                          boxShadow: '0 4px 15px rgba(102, 126, 234, 0.3)'
                        }}
                      >
                        {currentSummaryDoc.generatingNew ? (
                          <>
                            <div style={{
                              width: '20px',
                              height: '20px',
                              border: '3px solid transparent',
                              borderTop: '3px solid white',
                              borderRadius: '50%',
                              animation: 'spin 1s linear infinite'
                            }}></div>
                            Generating Summary...
                          </>
                        ) : (
                          <>
                            <i className="fas fa-magic"></i>
                            Generate Summary
                          </>
                        )}
                      </button>

                      {currentSummaryDoc.generatingNew && (
                        <div style={{ 
                          marginTop: '1rem', 
                          fontSize: '0.85rem', 
                          color: '#667eea',
                          fontWeight: '500'
                        }}>
                          This may take a few moments to complete...
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard


