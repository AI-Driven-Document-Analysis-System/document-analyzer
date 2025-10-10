import React, { useState, useEffect } from 'react';
import { authService } from "../../services/authService"

// Define TypeScript interfaces
interface Document {
  documentId: string;
  content: string;
  fileUrl: string;
  fileName: string;
  fileType: string;
  pageCount?: number;
  characterCount?: number;
  wordCount?: number;
}

interface DocumentEditorProps {
  documentId: string;
  onClose: () => void;
  authToken?: string; 
}

// // Mock auth service - replace with your actual implementation
// const getStoredAuthToken = () => {
//   try {
//     return window.localStorage?.getItem('token') ||
//            window.sessionStorage?.getItem('token') ||
//            'AUTH_TOKEN_NOT_FOUND';
//   } catch (e) {
//     return 'AUTH_TOKEN_NOT_FOUND';
//   }
// };

const DocumentEditor: React.FC<DocumentEditorProps> = ({ documentId, onClose, authToken: propAuthToken }) => {
  // State management
  const [document, setDocument] = useState<Document | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
//   const [authToken] = useState<string>(getStoredAuthToken());
  const [authToken, setAuthToken] = useState<string | null>(null)
  
    // Get auth token
    React.useEffect(() => {
      const token = propAuthToken || authService.getToken()
      setAuthToken(token)
    }, [propAuthToken])


  // Fetch document content and download URL on component mount
  useEffect(() => {
    if (!authToken) return; // Only fetch when authToken is available
    const fetchDocument = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Fetch document content (extracted text)
        const contentResponse = await fetch(
          `http://localhost:8000/api/documents/${documentId}/content`,
          {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${authToken}`,
              'Content-Type': 'application/json',
            },
          }
        );

        if (!contentResponse.ok) {
          throw new Error(`Failed to fetch document content: ${contentResponse.status}`);
        }

        const contentData = await contentResponse.json();

        // Fetch document metadata and download URL
        const downloadResponse = await fetch(
          `http://localhost:8000/api/documents/${documentId}/download`,
          {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${authToken}`,
              'Content-Type': 'application/json',
            },
          }
        );

        if (!downloadResponse.ok) {
          throw new Error(`Failed to fetch download URL: ${downloadResponse.status}`);
        }

        const downloadData = await downloadResponse.json();

        // Fetch document metadata
        const metadataResponse = await fetch(
          `http://localhost:8000/api/documents/${documentId}`,
          {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${authToken}`,
              'Content-Type': 'application/json',
            },
          }
        );

        if (!metadataResponse.ok) {
          throw new Error(`Failed to fetch document metadata: ${metadataResponse.status}`);
        }

        const metadataData = await metadataResponse.json();

        // Set document state
        setDocument({
          documentId: documentId,
          content: contentData.extracted_text || 'No text content extracted from this document',
          fileUrl: downloadData.download_url,
          fileName: contentData.filename || metadataData.original_filename,
          fileType: metadataData.content_type || 'application/pdf',
          pageCount: contentData.page_count,
          characterCount: contentData.character_count,
          wordCount: contentData.word_count,
        });
      } catch (err) {
        console.error('Error fetching document:', err);
        setError(err instanceof Error ? err.message : 'Failed to load document');
      } finally {
        setIsLoading(false);
      }
    };

    fetchDocument();
  }, [documentId, authToken]);

  // Handle content changes
  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (document) {
      setDocument({
        ...document,
        content: e.target.value
      });
    }
  };

  // Save document content (you'll need to implement a PUT endpoint for this)
  const handleSave = async () => {
    if (!document) return;
    
    setIsSaving(true);
    setError(null);
    
    try {
      const response = await fetch(
        `http://localhost:8000/api/documents/${documentId}/save_changes`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            extracted_text: document.content
          })
        }
      );

      if (!response.ok) {
        throw new Error('Failed to save document');
      }

      alert('Document saved successfully!');
    } catch (err) {
      console.error('Error saving document:', err);
      setError('Failed to save document');
      alert('Failed to save document.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div 
      style={{
        position: 'fixed', 
        top: 0, 
        left: 0, 
        width: '100vw', 
        height: '100vh',
        background: 'rgba(0,0,0,0.5)', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        zIndex: 9999
      }}
      onClick={onClose}
    >
      <div 
        style={{
          background: 'white', 
          borderRadius: 8, 
          width: '95%',
          maxWidth: 1400,
          height: '90vh',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{
          padding: '20px 24px',
          borderBottom: '1px solid #e5e7eb',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <h2 style={{ 
              margin: 0, 
              fontSize: '20px', 
              fontWeight: '600', 
              color: '#1f2937' 
            }}>
              Document Editor
            </h2>
            <p style={{ 
              margin: '4px 0 0 0', 
              fontSize: '14px', 
              color: '#6b7280' 
            }}>
              {document?.fileName || `Document ID: ${documentId}`}
              {document?.pageCount && ` • ${document.pageCount} pages`}
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              fontSize: '24px',
              color: '#9ca3af',
              cursor: 'pointer',
              padding: '4px 8px',
              borderRadius: '4px',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = '#ef4444';
              e.currentTarget.style.background = '#fee2e2';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = '#9ca3af';
              e.currentTarget.style.background = 'transparent';
            }}
          >
            ×
          </button>
        </div>

        {/* Content - Side by Side */}
        <div style={{ 
          flex: 1, 
          display: 'flex',
          overflow: 'hidden'
        }}>
          {isLoading ? (
            <div style={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center', 
              width: '100%',
              color: '#6b7280'
            }}>
              <div>
                <div style={{ 
                  fontSize: '48px', 
                  marginBottom: '16px',
                  textAlign: 'center'
                }}>
                  ⏳
                </div>
                <p>Loading document...</p>
              </div>
            </div>
          ) : error ? (
            <div style={{
              padding: '24px',
              width: '100%'
            }}>
              <div style={{
                padding: '16px',
                background: '#fee2e2',
                color: '#991b1b',
                borderRadius: '6px',
                border: '1px solid #fecaca'
              }}>
                {error}
              </div>
            </div>
          ) : document ? (
            <>
              {/* Left Side - Text Editor */}
              <div style={{
                flex: 1,
                padding: 24,
                overflowY: 'auto',
                borderRight: '1px solid #e5e7eb'
              }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: 12
                }}>
                  <label style={{
                    fontSize: '14px',
                    fontWeight: '600',
                    color: '#374151'
                  }}>
                    Extracted Text
                  </label>
                  <div style={{ display: 'flex', gap: '12px', fontSize: '12px', color: '#6b7280' }}>
                    {document.wordCount && <span>{document.wordCount} words</span>}
                    <span>{document.content.length} characters</span>
                  </div>
                </div>
                <textarea
                  value={document.content}
                  onChange={handleContentChange}
                  style={{
                    width: '100%',
                    height: 'calc(100% - 40px)',
                    padding: '12px',
                    fontSize: '14px',
                    lineHeight: '1.6',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    // fontFamily: 'system-ui, -apple-system, sans-serif',
                    color: '#111827',
                    resize: 'none',
                    boxSizing: 'border-box',
                    outline: 'none'
                  }}
                  placeholder="Enter document content..."
                  onFocus={(e) => {
                    e.currentTarget.style.borderColor = '#3b82f6';
                    e.currentTarget.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)';
                  }}
                  onBlur={(e) => {
                    e.currentTarget.style.borderColor = '#d1d5db';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                />
              </div>

              {/* Right Side - Document Preview */}
              <div style={{
                flex: 1,
                padding: 24,
                overflowY: 'auto',
                background: '#f9fafb'
              }}>
                <div style={{
                  marginBottom: 12
                }}>
                  <label style={{
                    fontSize: '14px',
                    fontWeight: '600',
                    color: '#374151'
                  }}>
                    Document Preview
                  </label>
                </div>
                <div style={{
                  background: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '6px',
                  height: 'calc(100% - 40px)',
                  overflow: 'hidden'
                }}>
                  {document.fileType === 'application/pdf' ? (
                    <iframe
                      src={document.fileUrl}
                      style={{
                        width: '100%',
                        height: '100%',
                        border: 'none'
                      }}
                      title="PDF Preview"
                    />
                  ) : document.fileType.startsWith('image/') ? (
                    <div style={{
                      width: '100%',
                      height: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      padding: 16
                    }}>
                      <img 
                        src={document.fileUrl} 
                        alt="Document preview"
                        style={{
                          maxWidth: '100%',
                          maxHeight: '100%',
                          objectFit: 'contain'
                        }}
                      />
                    </div>
                  ) : (
                    <div style={{
                      width: '100%',
                      height: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#6b7280'
                    }}>
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '48px', marginBottom: 16 }}>📄</div>
                        <p>Preview not available for this file type</p>
                        <a 
                          href={document.fileUrl} 
                          download={document.fileName}
                          style={{
                            color: '#3b82f6',
                            textDecoration: 'underline',
                            fontSize: '14px'
                          }}
                        >
                          Download Document
                        </a>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </>
          ) : null}
        </div>

        {/* Footer */}
        {!isLoading && !error && (
          <div style={{
            padding: '16px 24px',
            borderTop: '1px solid #e5e7eb',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            background: '#f9fafb'
          }}>
            <div style={{
              fontSize: '12px',
              color: '#6b7280'
            }}>
              Edit the extracted text and save changes
            </div>
            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                onClick={onClose}
                style={{
                  padding: '10px 20px',
                  background: 'white',
                  color: '#374151',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '14px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = '#f3f4f6';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'white';
                }}
              >
                Close
              </button>
              <button
                onClick={handleSave}
                disabled={isSaving}
                style={{
                  padding: '10px 20px',
                  background: isSaving ? '#9ca3af' : '#3b82f6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '14px',
                  fontWeight: '500',
                  cursor: isSaving ? 'not-allowed' : 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  if (!isSaving) {
                    e.currentTarget.style.background = '#2563eb';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isSaving) {
                    e.currentTarget.style.background = '#3b82f6';
                  }
                }}
              >
                {isSaving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentEditor;