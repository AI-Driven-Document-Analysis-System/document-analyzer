import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';
import {
  FileText, Upload, Clock, Database, CheckCircle, XCircle,
  TrendingUp, Tag, Languages, Image, Table, AlertCircle
} from 'lucide-react';

// Types
interface OverviewData {
  total_documents: number;
  documents_this_month: number;
  storage_used_bytes: number;
  processing_status: { status: string; count: number }[];
}

interface DocumentType {
  document_type: string;
  count: number;
  avg_confidence: number;
}

interface UploadTrend {
  date: string;
  document_count: number;
  total_size: number;
}

interface ProcessingPerformance {
  mime_type: string;
  total_processed: number;
  avg_ocr_time_minutes: number | null;
  avg_classification_time_minutes: number | null;
  success_rate: number;
  failed_count: number;
}

interface ContentInsights {
  overall: {
    documents_with_tables: number;
    documents_with_images: number;
    avg_ocr_confidence: number;
    total_documents: number;
  };
  language_distribution: { language: string; count: number }[];
}

interface UsageLimits {
  usage: {
    documents_processed_monthly: number;
    handwriting_recognition_used: number;
    risk_assessments_used: number;
    citation_analysis_used: number;
    reset_date: string | null;
  };
  subscription: {
    plan_name: string;
    features: Record<string, any>;
    status: string;
    expires_at: string | null;
  };
}

interface TagAnalytics {
  tag: string;
  tag_type: string;
  usage_count: number;
}

interface ProductivityInsights {
  peak_hours: { hour: number; upload_count: number; avg_file_size: number }[];
  velocity_trend: { date: string; daily_count: number; growth: number }[];
  efficiency_score: number;
  total_processed: number;
}

interface DocumentJourney {
  document_id: string;
  filename: string;
  document_type: string;
  completion_percentage: number;
  steps: { step: string; timestamp: string }[];
  has_summary: boolean;
  has_embedding: boolean;
}

interface ContentPatterns {
  size_patterns: { category: string; count: number; avg_confidence: number; avg_pages: number }[];
  day_patterns: { day_of_week: number; day_name: string; upload_count: number; avg_file_size: number }[];
  complexity_analysis: {
    mime_type: string;
    avg_pages: number;
    avg_text_length: number;
    table_percentage: number;
    image_percentage: number;
    avg_ocr_confidence: number;
  }[];
}

interface SmartRecommendations {
  recommendations: {
    type: string;
    title: string;
    description: string;
    action: string;
    priority: 'high' | 'medium' | 'low';
  }[];
  user_profile: {
    total_documents: number;
    avg_file_size: number;
    processing_success_rate: number;
    format_diversity_score: number;
  };
}

const Analytics: React.FC = () => {
  // State
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [documentTypes, setDocumentTypes] = useState<DocumentType[]>([]);
  const [uploadTrends, setUploadTrends] = useState<UploadTrend[]>([]);
  const [processingPerformance, setProcessingPerformance] = useState<ProcessingPerformance[]>([]);
  const [contentInsights, setContentInsights] = useState<ContentInsights | null>(null);
  const [usageLimits, setUsageLimits] = useState<UsageLimits | null>(null);
  const [tagAnalytics, setTagAnalytics] = useState<TagAnalytics[]>([]);
  const [productivityInsights, setProductivityInsights] = useState<ProductivityInsights | null>(null);
  const [documentJourneys, setDocumentJourneys] = useState<DocumentJourney[]>([]);
  const [contentPatterns, setContentPatterns] = useState<ContentPatterns | null>(null);
  const [smartRecommendations, setSmartRecommendations] = useState<SmartRecommendations | null>(null);
  const [timeRange, setTimeRange] = useState(30);

  // API calls
  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const userId = 'current-user-id'; // Replace with actual user ID logic
      const token = localStorage.getItem('token');
      
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };
      
      const toArray = (value: any) => Array.isArray(value) ? value : [];
      const toObject = (value: any) => (value && typeof value === 'object' && !Array.isArray(value)) ? value : null;

      const [
        overviewRes,
        documentTypesRes,
        uploadTrendsRes,
        processingRes,
        contentRes,
        usageRes,
        tagRes,
        productivityRes,
        journeyRes,
        patternsRes,
        recommendationsRes
      ] = await Promise.all([
        fetch(`/api/analytics/overview?user_id=${userId}`, { headers }),
        fetch(`/api/analytics/document-types?user_id=${userId}`, { headers }),
        fetch(`/api/analytics/upload-trends?user_id=${userId}&days=${timeRange}`, { headers }),
        fetch(`/api/analytics/processing-performance?user_id=${userId}`, { headers }),
        fetch(`/api/analytics/content-insights?user_id=${userId}`, { headers }),
        fetch(`/api/analytics/usage-limits?user_id=${userId}`, { headers }),
        fetch(`/api/analytics/tag-analytics?user_id=${userId}`, { headers }),
        fetch(`/api/analytics/productivity-insights?user_id=${userId}`, { headers }),
        fetch(`/api/analytics/document-journey?user_id=${userId}`, { headers }),
        fetch(`/api/analytics/content-patterns?user_id=${userId}`, { headers }),
        fetch(`/api/analytics/smart-recommendations?user_id=${userId}`, { headers })
      ]);

      const overviewJson = await overviewRes.json();
      const documentTypesJson = await documentTypesRes.json();
      const uploadTrendsJson = await uploadTrendsRes.json();
      const processingJson = await processingRes.json();
      const contentJson = await contentRes.json();
      const usageJson = await usageRes.json();
      const tagJson = await tagRes.json();
      const productivityJson = await productivityRes.json();
      const journeyJson = await journeyRes.json();
      const patternsJson = await patternsRes.json();
      const recommendationsJson = await recommendationsRes.json();

      setOverview(toObject(overviewJson));
      setDocumentTypes(toArray(documentTypesJson));
      setUploadTrends(toArray(uploadTrendsJson));
      setProcessingPerformance(toArray(processingJson));
      setContentInsights(toObject(contentJson));
      setUsageLimits(toObject(usageJson));
      setTagAnalytics(toArray(tagJson));
      setProductivityInsights(toObject(productivityJson));
      setDocumentJourneys(toArray(journeyJson));
      setContentPatterns(toObject(patternsJson));
      setSmartRecommendations(toObject(recommendationsJson));
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [timeRange]);

  // Helper functions
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getHourLabel = (hour: number) => {
    if (hour === 0) return '12 AM';
    if (hour < 12) return `${hour} AM`;
    if (hour === 12) return '12 PM';
    return `${hour - 12} PM`;
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 80) return 'bg-green-500';
    if (percentage >= 60) return 'bg-yellow-500';
    if (percentage >= 40) return 'bg-orange-500';
    return 'bg-red-500';
  };

  // Chart colors
  const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#8dd1e1', '#d084d0'];

  const tabButtons = [
    { id: 'overview', label: 'Overview', icon: TrendingUp },
    { id: 'productivity', label: 'Productivity', icon: Clock },
    { id: 'patterns', label: 'Patterns', icon: Database },
    { id: 'insights', label: 'Smart Insights', icon: AlertCircle }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Advanced Analytics Dashboard</h1>
        
        {/* Tab Navigation */}
        <div className="mb-8 border-b border-gray-200">
          <nav className="flex space-x-8">
            {tabButtons.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{label}</span>
              </button>
            ))}
          </nav>
        </div>
        
        {/* Time Range Selector */}
        <div className="mb-6">
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(Number(e.target.value))}
            className="border border-gray-300 rounded-md px-3 py-2 bg-white"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <>
            {/* Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Documents</p>
                    <p className="text-2xl font-bold text-gray-900">{overview?.total_documents || 0}</p>
                  </div>
                  <FileText className="h-8 w-8 text-blue-600" />
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">This Month</p>
                    <p className="text-2xl font-bold text-gray-900">{overview?.documents_this_month || 0}</p>
                  </div>
                  <Upload className="h-8 w-8 text-green-600" />
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Storage Used</p>
                    <p className="text-2xl font-bold text-gray-900">{formatBytes(overview?.storage_used_bytes || 0)}</p>
                  </div>
                  <Database className="h-8 w-8 text-purple-600" />
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Efficiency Score</p>
                    <p className="text-2xl font-bold text-gray-900">{productivityInsights?.efficiency_score || 0}%</p>
                  </div>
                  <CheckCircle className="h-8 w-8 text-indigo-600" />
                </div>
              </div>
            </div>

            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              {/* Upload Trends */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <TrendingUp className="h-5 w-5 mr-2" />
                  Upload Trends
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={uploadTrends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tickFormatter={formatDate} />
                    <YAxis />
                    <Tooltip labelFormatter={(value) => formatDate(value as string)} />
                    <Area type="monotone" dataKey="document_count" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* Document Types */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Document Types Distribution</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={documentTypes}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ document_type, count }) => `${document_type}: ${count}`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="count"
                    >
                      {documentTypes.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </>
        )}

        {activeTab === 'productivity' && (
          <>
            {/* Productivity Insights */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              {/* Peak Hours */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Clock className="h-5 w-5 mr-2" />
                  Peak Upload Hours
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={productivityInsights?.peak_hours || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="hour" tickFormatter={getHourLabel} />
                    <YAxis />
                    <Tooltip labelFormatter={(hour) => getHourLabel(hour as number)} />
                    <Bar dataKey="upload_count" fill="#8884d8" name="Uploads" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Velocity Trend */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <TrendingUp className="h-5 w-5 mr-2" />
                  Daily Upload Velocity
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={productivityInsights?.velocity_trend || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tickFormatter={formatDate} />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="daily_count" stroke="#8884d8" strokeWidth={2} />
                    <Line type="monotone" dataKey="growth" stroke="#82ca9d" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Document Journey Tracker */}
            <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Document Processing Journey</h3>
              <div className="space-y-4">
                {documentJourneys.slice(0, 5).map((journey, index) => (
                  <div key={journey.document_id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900 truncate">{journey.filename}</span>
                      <span className="text-sm text-gray-500">{journey.document_type}</span>
                    </div>
                    <div className="flex items-center mb-3">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${getProgressColor(journey.completion_percentage)}`}
                          style={{ width: `${journey.completion_percentage}%` }}
                        />
                      </div>
                      <span className="ml-3 text-sm font-medium text-gray-700">
                        {journey.completion_percentage.toFixed(0)}%
                      </span>
                    </div>
                    <div className="flex space-x-4 text-xs text-gray-500">
                      {journey.steps.map((step, stepIndex) => (
                        <div key={stepIndex} className="flex items-center">
                          <CheckCircle className="h-3 w-3 text-green-500 mr-1" />
                          <span className="capitalize">{step.step.replace('_', ' ')}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {activeTab === 'patterns' && (
          <>
            {/* Content Patterns */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              {/* File Size Patterns */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">File Size Distribution</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={contentPatterns?.size_patterns || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="category" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#8884d8" name="Document Count" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Day of Week Patterns */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Patterns by Day</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={contentPatterns?.day_patterns || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day_name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="upload_count" fill="#82ca9d" name="Uploads" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Complexity Analysis */}
            <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Document Complexity Analysis</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        File Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Avg Pages
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Avg Text Length
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Tables %
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Images %
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        OCR Confidence
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {contentPatterns?.complexity_analysis.map((item, index) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {item.mime_type}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {item.avg_pages}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {item.avg_text_length.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {item.table_percentage}%
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {item.image_percentage}%
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {(item.avg_ocr_confidence * 100).toFixed(1)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Tag Analytics */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Tag className="h-5 w-5 mr-2" />
                Most Used Tags
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={tagAnalytics} layout="horizontal">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="tag" type="category" width={100} />
                  <Tooltip />
                  <Bar dataKey="usage_count" fill="#d084d0" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </>
        )}

        {activeTab === 'insights' && (
          <>
            {/* Smart Recommendations */}
            <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <AlertCircle className="h-5 w-5 mr-2" />
                Smart Recommendations
              </h3>
              <div className="space-y-4">
                {smartRecommendations?.recommendations.map((rec, index) => (
                  <div key={index} className={`p-4 rounded-lg border ${getPriorityColor(rec.priority)}`}>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-semibold text-lg">{rec.title}</h4>
                        <p className="text-sm mt-1">{rec.description}</p>
                        <p className="text-xs font-medium mt-2 opacity-75">{rec.action}</p>
                      </div>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${rec.priority === 'high' ? 'bg-red-100 text-red-800' : 
                        rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
                        {rec.priority.toUpperCase()}
                      </span>
                    </div>
                  </div>
                ))}
                {(!smartRecommendations?.recommendations || smartRecommendations.recommendations.length === 0) && (
                  <div className="text-center py-8 text-gray-500">
                    <CheckCircle className="h-12 w-12 mx-auto mb-3 text-green-500" />
                    <p className="text-lg font-medium">Great job!</p>
                    <p>No recommendations at this time. You're using the platform efficiently!</p>
                  </div>
                )}
              </div>
            </div>

            {/* User Profile Score */}
            {smartRecommendations?.user_profile && (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <div className="text-center">
                    <p className="text-sm font-medium text-gray-600">Total Documents</p>
                    <p className="text-2xl font-bold text-gray-900">{smartRecommendations.user_profile.total_documents}</p>
                  </div>
                </div>
                
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <div className="text-center">
                    <p className="text-sm font-medium text-gray-600">Success Rate</p>
                    <p className="text-2xl font-bold text-green-600">{smartRecommendations.user_profile.processing_success_rate.toFixed(1)}%</p>
                  </div>
                </div>
                
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <div className="text-center">
                    <p className="text-sm font-medium text-gray-600">Format Diversity</p>
                    <p className="text-2xl font-bold text-purple-600">{smartRecommendations.user_profile.format_diversity_score}%</p>
                  </div>
                </div>
                
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <div className="text-center">
                    <p className="text-sm font-medium text-gray-600">Avg File Size</p>
                    <p className="text-2xl font-bold text-blue-600">{formatBytes(smartRecommendations.user_profile.avg_file_size)}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Content Insights */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Content Features</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center">
                      <Table className="h-5 w-5 text-blue-600 mr-3" />
                      <span>Documents with Tables</span>
                    </div>
                    <span className="font-semibold">{contentInsights?.overall.documents_with_tables || 0}</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center">
                      <Image className="h-5 w-5 text-green-600 mr-3" />
                      <span>Documents with Images</span>
                    </div>
                    <span className="font-semibold">{contentInsights?.overall.documents_with_images || 0}</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-purple-600 mr-3" />
                      <span>Avg OCR Confidence</span>
                    </div>
                    <span className="font-semibold">
                      {((contentInsights?.overall.avg_ocr_confidence || 0) * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Usage Limits */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Usage & Limits</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span>Documents Processed (Monthly)</span>
                    <span className="font-semibold">{usageLimits?.usage.documents_processed_monthly || 0}</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span>Handwriting Recognition Used</span>
                    <span className="font-semibold">{usageLimits?.usage.handwriting_recognition_used || 0}</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span>Risk Assessments Used</span>
                    <span className="font-semibold">{usageLimits?.usage.risk_assessments_used || 0}</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span>Citation Analysis Used</span>
                    <span className="font-semibold">{usageLimits?.usage.citation_analysis_used || 0}</span>
                  </div>
                </div>

                {usageLimits?.subscription.expires_at && (
                  <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <div className="flex items-center">
                      <AlertCircle className="h-5 w-5 text-blue-600 mr-2" />
                      <span className="text-sm text-blue-800">
                        Subscription expires: {formatDate(usageLimits.subscription.expires_at)}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Analytics;
