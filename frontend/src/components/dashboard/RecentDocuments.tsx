import React from 'react';

interface Document {
  id: string;
  name: string;
  type: string;
  uploadedAt: string;
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
  return (
    <div className="feature-container" style={{ flex: '0 0 50%', borderRight: '2px solid var(--border-color)' }}>
      <div className="tab-content-container">
        <div className="search-input-group">
          <span className="search-icon"><i className="fas fa-search"></i></span>
          <input
            type="text"
            className="form-control"
            placeholder="Search across all your documents..."
          />
        </div>

        <h5 className="mb-4"><i className="fas fa-history me-2"></i>Recent Documents</h5>

        {documents.length === 0 ? (
          <div className="text-center py-5">
            <i className="fas fa-file-alt empty-state-icon"></i>
            <p className="mt-3 text-muted">No documents uploaded yet.</p>
          </div>
        ) : (
          <div>
            {documents.slice(0, 5).map((doc) => (
              <div key={doc.id} className="result-item">
                <div className="d-flex">
                  <div className="flex-grow-1">
                    <div className="result-title">
                      {doc.name}
                      <span className="doc-type-tag tag-invoice">{doc.type}</span>
                    </div>
                    <div className="result-meta">
                      PDF • 2.4 MB • Last accessed: {doc.uploadedAt}
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
