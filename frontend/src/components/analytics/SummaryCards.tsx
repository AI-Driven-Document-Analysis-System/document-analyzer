import React from 'react';
import { Icons } from './icons';

interface SummaryData {
  totalDocuments: number;
  totalSize: number;
  averageSize: number;
  lastUpload: string | null;
}

interface SummaryCardsProps {
  summary: SummaryData | null;
  formatFileSize: (bytes: number) => string;
  formatDate: (date: string) => string;
}

const SummaryCards: React.FC<SummaryCardsProps> = ({ summary, formatFileSize, formatDate }) => {
  if (!summary) return null;

  return (
    <div className="summary-grid" style={{ marginBottom: '24px' }}>
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
  );
};

export default SummaryCards;
