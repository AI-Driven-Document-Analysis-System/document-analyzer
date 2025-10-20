import React, { useState } from 'react';

interface Document {
  id: string;
  name: string;
  type: string;
  uploadedAt: string;
  document_type?: string;
  original_filename?: string;
  file_size?: number;
  created_at?: string;
}

interface RecentDocumentsProps {
  documents: Document[];
  onSummarize: (doc: Document) => void;
  onChatWithDoc: (doc: Document) => void;
  onPreview: (doc: Document) => void;
}

const RecentDocuments: React.FC<RecentDocumentsProps> = ({
  documents,
  onSummarize,
  onChatWithDoc,
  onPreview
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Document[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    
    if (query.trim().length === 0) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/documents/?limit=100`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        const allDocuments = data.documents || [];
        
        // Filter documents based on search query
        const filtered = allDocuments.filter((doc: any) => 
          doc.original_filename?.toLowerCase().includes(query.toLowerCase()) ||
          doc.document_type?.toLowerCase().includes(query.toLowerCase())
        );
        
        setSearchResults(filtered);
      }
    } catch (error) {
      console.error('Error searching documents:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(hours / 24);
    
    if (hours < 1) return 'Just now';
    if (hours < 24) return `${hours} hours ago`;
    if (days < 7) return `${days} days ago`;
    return date.toLocaleDateString();
  };

  const displayedDocuments = searchQuery ? searchResults : documents.slice(0, 5);
  const showingSearchResults = searchQuery.trim().length > 0;

  return (
    <div className="feature-container" style={{ flex: '0 0 50%', borderRight: '2px solid var(--border-color)' }}>
      <div className="tab-content-container">
        <div className="search-input-group" style={{ marginBottom: '1.5rem' }}>
          <span className="search-icon"><i className="fas fa-search"></i></span>
          <input
            type="text"
            className="form-control"
            placeholder="Search across all your documents..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            style={{
              background: 'var(--bg-primary)',
              border: '2px solid #3b82f6',
              borderRadius: '12px',
              padding: '12px 12px 12px 45px',
              fontSize: '15px',
              color: 'var(--text-primary)',
              width: '100%',
              transition: 'all 0.3s ease',
              boxShadow: searchQuery ? '0 0 0 3px rgba(59, 130, 246, 0.1)' : 'none'
            }}
          />
          {searchQuery && (
            <button
              onClick={() => {
                setSearchQuery('');
                setSearchResults([]);
              }}
              style={{
                position: 'absolute',
                right: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'none',
                border: 'none',
                color: '#9ca3af',
                cursor: 'pointer',
                fontSize: '16px',
                padding: '4px 8px'
              }}
            >
              <i className="fas fa-times"></i>
            </button>
          )}
        </div>

        <h5 className="mb-4">
          <i className={`fas ${showingSearchResults ? 'fa-search' : 'fa-history'} me-2`}></i>
          {showingSearchResults ? `Search Results (${searchResults.length})` : 'Recent Documents'}
        </h5>

        {isSearching ? (
          <div className="text-center py-5">
            <div style={{
              width: '40px',
              height: '40px',
              border: '4px solid var(--border-color)',
              borderTop: '4px solid #3b82f6',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
              margin: '0 auto 16px'
            }}></div>
            <p className="mt-3 text-muted">Searching...</p>
          </div>
        ) : displayedDocuments.length === 0 ? (
          <div className="text-center py-5">
            <i className="fas fa-file-alt empty-state-icon"></i>
            <p className="mt-3 text-muted">
              {showingSearchResults ? `No documents found matching "${searchQuery}"` : 'No documents uploaded yet.'}
            </p>
          </div>
        ) : (
          <div>
            {displayedDocuments.map((doc) => (
              <div key={doc.id} className="result-item">
                <div className="d-flex">
                  <div className="flex-grow-1">
                    <div className="result-title">
                      {doc.original_filename || doc.name}
                      {doc.document_type && (
                        <span className={`classification-label classification-${doc.document_type.toLowerCase().replace(/\s+/g, '-')}`}>
                          {doc.document_type}
                        </span>
                      )}
                    </div>
                    <div className="result-meta">
                      PDF • {doc.file_size ? formatFileSize(doc.file_size) : '2.4 MB'} • Last accessed: {doc.created_at ? formatDate(doc.created_at) : doc.uploadedAt}
                    </div>
                    <div className="result-actions">
                      <button
                        className="btn summarize-btn"
                        onClick={() => onSummarize(doc)}
                      >
                        <i className="fas fa-file-contract me-1"></i>Summarize
                      </button>
                      <button
                        className="btn chat-doc-btn"
                        onClick={() => onChatWithDoc(doc)}
                      >
                        <i className="fas fa-comments me-1"></i>Chat with Doc
                      </button>
                      <button
                        className="btn preview-btn"
                        onClick={() => onPreview(doc)}
                      >
                        <i className="fas fa-eye me-1"></i>Preview
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default RecentDocuments;
