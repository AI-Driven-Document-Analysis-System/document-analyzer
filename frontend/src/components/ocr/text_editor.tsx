import React, { useState, useEffect } from 'react';
import { authService } from "../../services/authService"
import { useTheme } from "../../contexts/ThemeContext"

// Define TypeScript interfaces
interface LayoutSection {
  text: string;
  confidence: number;
  page_number: number;
  bounding_box: number[];
  element_type: string;
}

interface Document {
  documentId: string;
  content: string;
  fileUrl: string;
  fileName: string;
  fileType: string;
  pageCount?: number;
  characterCount?: number;
  wordCount?: number;
  documentType?: string;
  classification?: string;
  layoutSections?: LayoutSection[];
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
  // Get theme context
  const { isDarkMode } = useTheme();
  
  // State management
  const [document, setDocument] = useState<Document | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
//   const [authToken] = useState<string>(getStoredAuthToken());
  const [authToken, setAuthToken] = useState<string | null>(null)
  const [selectedClassification, setSelectedClassification] = useState<string>('');
  const [classificationChanged, setClassificationChanged] = useState(false);
  const [displayMode, setDisplayMode] = useState<'structured' | 'raw'>('structured');

  // Predefined document categories
  const documentCategories = [
    'Research Paper',
    'Financial Report',
    'Medical Record',
    'Invoice or Receipt',
    'Legal Document',
    'Other'
  ];
  
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
          documentType: metadataData.document_type,
          classification: metadataData.document_type || metadataData.classification,
          layoutSections: contentData.layout_sections || [],
        });

        // Set initial classification
        const initialClassification = metadataData.document_type || metadataData.classification || 'Other';
        setSelectedClassification(initialClassification);
        setClassificationChanged(false);
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

  // Handle classification changes
  const handleClassificationChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newClassification = e.target.value;
    setSelectedClassification(newClassification);
    setClassificationChanged(newClassification !== (document?.classification || document?.documentType || 'Other'));
    
    if (document) {
      setDocument({
        ...document,
        classification: newClassification,
        documentType: newClassification
      });
    }
  };

  // Function to get element type styling
  const getElementTypeStyle = (elementType: string) => {
    const baseStyle = {
      marginBottom: '12px',
      padding: '8px 12px',
      borderRadius: '6px',
      border: '1px solid',
      fontSize: '14px',
      lineHeight: '1.6',
    };

    switch (elementType) {
      case 'LAYOUT_TITLE':
        return {
          ...baseStyle,
          fontSize: '24px',
          fontWeight: '700',
          color: isDarkMode ? '#f1f5f9' : '#1f2937',
          backgroundColor: isDarkMode ? '#1e40af' : '#dbeafe',
          borderColor: isDarkMode ? '#3b82f6' : '#60a5fa',
          marginBottom: '20px',
        };
      case 'LAYOUT_SECTION_HEADER':
        return {
          ...baseStyle,
          fontSize: '18px',
          fontWeight: '600',
          color: isDarkMode ? '#f1f5f9' : '#1f2937',
          backgroundColor: isDarkMode ? '#0f766e' : '#ccfbf1',
          borderColor: isDarkMode ? '#14b8a6' : '#5eead4',
          marginBottom: '16px',
          marginTop: '24px',
        };
      case 'LAYOUT_HEADER':
        return {
          ...baseStyle,
          fontSize: '12px',
          fontStyle: 'italic',
          color: isDarkMode ? '#94a3b8' : '#6b7280',
          backgroundColor: isDarkMode ? '#374151' : '#f9fafb',
          borderColor: isDarkMode ? '#4b5563' : '#e5e7eb',
        };
      case 'LAYOUT_FOOTER':
        return {
          ...baseStyle,
          fontSize: '12px',
          fontStyle: 'italic',
          color: isDarkMode ? '#94a3b8' : '#6b7280',
          backgroundColor: isDarkMode ? '#374151' : '#f9fafb',
          borderColor: isDarkMode ? '#4b5563' : '#e5e7eb',
        };
      case 'LAYOUT_LIST':
        return {
          ...baseStyle,
          backgroundColor: isDarkMode ? '#422006' : '#fef3c7',
          borderColor: isDarkMode ? '#d97706' : '#f59e0b',
          color: isDarkMode ? '#fbbf24' : '#92400e',
          paddingLeft: '20px',
        };
      case 'LAYOUT_TABLE':
        return {
          ...baseStyle,
          backgroundColor: isDarkMode ? '#312e81' : '#ede9fe',
          borderColor: isDarkMode ? '#6366f1' : '#a78bfa',
          color: isDarkMode ? '#c4b5fd' : '#5b21b6',
          fontFamily: 'monospace',
        };
      case 'LAYOUT_FIGURE':
        return {
          ...baseStyle,
          textAlign: 'center' as const,
          backgroundColor: isDarkMode ? '#0f172a' : '#f8fafc',
          borderColor: isDarkMode ? '#4b5563' : '#e5e7eb',
          color: isDarkMode ? '#cbd5e1' : '#374151',
        };
      case 'LAYOUT_KEY_VALUE':
        return {
          ...baseStyle,
          backgroundColor: isDarkMode ? '#1f2937' : '#f3f4f6',
          borderColor: isDarkMode ? '#4b5563' : '#9ca3af',
          color: isDarkMode ? '#e5e7eb' : '#374151',
          fontFamily: 'monospace',
        };
      case 'LAYOUT_PAGE_NUMBER':
        return {
          ...baseStyle,
          fontSize: '11px',
          textAlign: 'center' as const,
          color: isDarkMode ? '#94a3b8' : '#6b7280',
          backgroundColor: isDarkMode ? '#374151' : '#f9fafb',
          borderColor: isDarkMode ? '#4b5563' : '#e5e7eb',
        };
      default: // LAYOUT_TEXT
        return {
          ...baseStyle,
          backgroundColor: isDarkMode ? '#334155' : 'white',
          borderColor: isDarkMode ? '#64748b' : '#e5e7eb',
          color: isDarkMode ? '#f1f5f9' : '#374151',
        };
    }
  };

  // Function to get element type label
  const getElementTypeLabel = (elementType: string) => {
    switch (elementType) {
      case 'layout_title':
        return 'Title';
      case 'layout_section_header':
      case 'SectionHeader': 
        return 'Section Header';
      case 'layout_header': 
      case 'PageHeader': 
        return 'Page Header';
      case 'layout_footer': 
      case 'PageFooter': 
        return 'Page Footer';
      case 'layout_list': 
      case 'ListItem': 
        return 'List';
      case 'layout_table': 
      case 'Table': 
        return 'Table';
      case 'layout_figure':
      case 'Figure':
        return 'Figure';
      case 'Picture':
        return 'Picture';
      case 'layout_key_value': 
      case 'Form':
        return 'Form';
      case 'layout_page_number':
        return 'Page Number';
      case 'Caption':
        return 'Caption';
      case 'Footnote':
        return 'Footnote';
      case 'Formula':
        return 'Formula';
      case 'TableOfContents':
        return 'Table of Contents';
      case 'Handwriting':
        return 'Handwriting';
      case 'TextInlineMath':
        return 'Inline Math';
      case 'layout_text':
      case 'text':
        return 'Text';
      default: return 'Text';
    }
  };

  // Function to handle structured text editing
  const handleStructuredTextEdit = (pageNum: number, sectionIndex: number, newText: string) => {
    if (!document?.layoutSections) return;
    
    const sections = document.layoutSections!;
    const updatedSections = [...sections];
    const flatIndex = sections.findIndex((section, idx) => {
      const page = section.page_number || 1;
      const currentPageSections = sections.filter(s => (s.page_number || 1) === page);
      const sectionInPageIndex = currentPageSections.indexOf(section);
      return page === pageNum && sectionInPageIndex === sectionIndex;
    });
    
    if (flatIndex !== -1) {
      updatedSections[flatIndex] = { ...updatedSections[flatIndex], text: newText };
      
      // Also update the raw content by combining all sections
      const combinedText = updatedSections.map(section => section.text).join('\n\n');
      
      setDocument({
        ...document,
        layoutSections: updatedSections,
        content: combinedText
      });
    }
  };

  // Function to render structured content
  // Function to safely format HTML-like syntax in text
  const formatHtmlTags = (text: string) => {
    const formattedText = text.split('\n').map(line => {
      // Replace common HTML tags with styled spans
      return line
        .replace(/<b>(.*?)<\/b>/g, (_, content) => `<span style="font-weight: bold;">${content}</span>`)
        .replace(/<i>(.*?)<\/i>/g, (_, content) => `<span style="font-style: italic;">${content}</span>`)
        .replace(/<u>(.*?)<\/u>/g, (_, content) => `<span style="text-decoration: underline;">${content}</span>`)
        .replace(/<sup>(.*?)<\/sup>/g, (_, content) => `<span style="vertical-align: super; font-size: smaller;">${content}</span>`)
        .replace(/<sub>(.*?)<\/sub>/g, (_, content) => `<span style="vertical-align: sub; font-size: smaller;">${content}</span>`)
        .replace(/<strike>(.*?)<\/strike>/g, (_, content) => `<span style="text-decoration: line-through;">${content}</span>`)
        .replace(/<strong>(.*?)<\/strong>/g, (_, content) => `<span style="font-weight: bold;">${content}</span>`)
        .replace(/<em>(.*?)<\/em>/g, (_, content) => `<span style="font-style: italic;">${content}</span>`)
        .replace(/<small>(.*?)<\/small>/g, (_, content) => `<span style="font-size: smaller;">${content}</span>`)
        .replace(/<mark>(.*?)<\/mark>/g, (_, content) => `<span style="background-color: ${isDarkMode ? '#374151' : '#fef3c7'}; padding: 0 2px;">${content}</span>`)
        .replace(/<code>(.*?)<\/code>/g, (_, content) => `<span style="font-family: monospace; background-color: ${isDarkMode ? '#1e293b' : '#f1f5f9'}; padding: 0 4px; border-radius: 4px;">${content}</span>`);
    }).join('\n');

    return <div dangerouslySetInnerHTML={{ __html: formattedText }} />;
  };

  const renderStructuredContent = () => {
    if (!document?.layoutSections || document.layoutSections.length === 0 ) {
      return (
        <div style={{
          padding: '20px',
          textAlign: 'center',
          color: isDarkMode ? '#94a3b8' : '#6b7280',
          backgroundColor: isDarkMode ? '#334155' : '#f9fafb',
          borderRadius: '8px',
          border: isDarkMode ? '1px solid #64748b' : '1px solid #e5e7eb',
        }}>
          <p>No structured layout data available for this document.</p>
          <p style={{ fontSize: '12px', marginTop: '8px' }}>
            Switch to "Raw Text" mode to view the extracted text.
          </p>
        </div>
      );
    }

    // Group sections by page
    const sectionsByPage = document.layoutSections.reduce((acc, section) => {
      const page = section.page_number || 1;
      if (!acc[page]) {
        acc[page] = [];
      }
      acc[page].push(section);
      return acc;
    }, {} as Record<number, LayoutSection[]>);

    return (
      <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
        {Object.entries(sectionsByPage)
          .sort(([a], [b]) => parseInt(a) - parseInt(b))
          .map(([pageNum, sections]) => (
            <div key={pageNum} style={{ marginBottom: '32px' }}>
              {parseInt(pageNum) >= 1 && (
                <div style={{
                  fontSize: '16px',
                  fontWeight: '600',
                  color: isDarkMode ? '#60a5fa' : '#3b82f6',
                  marginBottom: '16px',
                  paddingBottom: '8px',
                  borderBottom: isDarkMode ? '2px solid #475569' : '2px solid #e5e7eb',
                }}>
                  Page {pageNum}
                </div>
              )}
              {sections.map((section, index) => {
                if (getElementTypeLabel(section.element_type) === 'Picture' || getElementTypeLabel(section.element_type) === 'Figure') {
                  return null; // Skip rendering Picture and Figure elements
                }
                const sectionStyle = getElementTypeStyle(section.element_type);
                return (
                  <div key={`${pageNum}-${index}`} style={sectionStyle}>
                    <div style={{
                      fontSize: '10px',
                      fontWeight: '500',
                      marginBottom: '4px',
                      opacity: 0.7,
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px',
                    }}>
                      {getElementTypeLabel(section.element_type)}
                      {section.confidence && (
                        <span style={{ marginLeft: '8px' }}>
                          ({Math.round(section.confidence * 100)}% confidence)
                        </span>
                      )}
                    </div>
                    <div style={{
                      width: '100%',
                      minHeight: Math.max(60, Math.ceil(section.text.length / 80) * 20 + 40) + 'px',
                      padding: '8px',
                      border: 'none',
                      borderRadius: '4px',
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                      color: 'inherit',
                      fontSize: 'inherit',
                      fontFamily: 'inherit',
                      fontWeight: 'inherit',
                      fontStyle: 'inherit',
                      textAlign: 'inherit',
                      lineHeight: 'inherit',
                      outline: 'none',
                      boxSizing: 'border-box',
                      overflow: 'hidden',
                      cursor: 'text',
                    }} 
                    onClick={(e) => {
                      const textArea = e.currentTarget.querySelector('textarea');
                      if (textArea) textArea.focus();
                    }}>
                      {/* Hidden textarea for editing */}
                      <textarea
                        value={section.text}
                        onChange={(e) => handleStructuredTextEdit(parseInt(pageNum), index, e.target.value)}
                        style={{
                          position: 'absolute',
                          left: '-9999px',
                          width: '1px',
                          height: '1px',
                          overflow: 'hidden',
                        }}
                      />
                      {/* Formatted display */}
                      {formatHtmlTags(section.text)}
                    </div>
                  </div>
                );
              })}
            </div>
          ))}
      </div>
    );
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
            extracted_text: document.content,
            document_type: selectedClassification,
            classification: selectedClassification
          })
        }
      );

      if (!response.ok) {
        throw new Error('Failed to save document');
      }

      // Reset classification changed flag on successful save
      setClassificationChanged(false);
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
        background: isDarkMode ? 'rgba(0,0,0,0.8)' : 'rgba(0,0,0,0.5)', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        zIndex: 9999
      }}
      onClick={onClose}
    >
      <div 
        style={{
          background: isDarkMode ? '#1e293b' : 'white', 
          borderRadius: 10, 
          width: '90%',
          maxWidth: 1400,
          height: '90vh',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: isDarkMode ? '0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 10px 10px -5px rgba(0, 0, 0, 0.2)' : '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
          border: isDarkMode ? '1px solid #475569' : 'none'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{
          padding: '20px 24px',
          borderBottom: isDarkMode ? '1px solid #475569' : '1px solid #e5e7eb',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: isDarkMode ? '#334155' : 'white'
        }}>
          <div style={{ flex: 1 }}>
            <h2 style={{ 
              margin: 0, 
              fontSize: '20px', 
              fontWeight: '600', 
              color: isDarkMode ? '#f1f5f9' : '#1f2937'
            }}>
              Document Editor
            </h2>
            <p style={{ 
              margin: '4px 0 0 0', 
              fontSize: '14px', 
              color: isDarkMode ? '#cbd5e1' : '#6b7280'
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
              color: isDarkMode ? '#94a3b8' : '#9ca3af',
              cursor: 'pointer',
              padding: '4px 8px',
              borderRadius: '4px',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = '#ef4444';
              e.currentTarget.style.background = isDarkMode ? '#475569' : '#fee2e2';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = isDarkMode ? '#94a3b8' : '#9ca3af';
              e.currentTarget.style.background = 'transparent';
            }}
          >
            ×
          </button>
        </div>

        {/* Classification Section */}
        {!isLoading && !error && document && (
          <div style={{
            padding: '12px 20px',
            borderBottom: isDarkMode ? '1px solid #475569' : '1px solid #e5e7eb',
            backgroundColor: isDarkMode ? '#334155' : 'white',
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}>
            <span style={{
              fontSize: '14px',
              fontWeight: '500',
              color: isDarkMode ? '#f1f5f9' : '#374151',
            }}>
              Classified Type :
            </span>
            <select
              value={selectedClassification}
              onChange={handleClassificationChange}
              style={{
                padding: '6px 10px',
                border: `1px solid ${classificationChanged ? '#f59e0b' : (isDarkMode ? '#64748b' : '#d1d5db')}`,
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: '400',
                backgroundColor: isDarkMode ? '#1e293b' : 'white',
                color: isDarkMode ? '#f1f5f9' : '#374151',
                outline: 'none',
                cursor: 'pointer',
                transition: 'all 0.2s',
                minWidth: '160px'
              }}
              onFocus={(e) => {
                e.currentTarget.style.borderColor = '#3b82f6';
                e.currentTarget.style.boxShadow = '0 0 0 1px rgba(59, 130, 246, 0.1)';
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = classificationChanged ? '#f59e0b' : (isDarkMode ? '#64748b' : '#d1d5db');
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              {documentCategories.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
            {classificationChanged && (
              <div style={{
                fontSize: '10px',
                color: '#f59e0b',
                fontWeight: '600',
                padding: '2px 6px',
                backgroundColor: isDarkMode ? '#451a03' : '#fef3c7',
                borderRadius: '3px',
                border: '1px solid #f59e0b',
                display: 'flex',
                alignItems: 'center',
                gap: '2px'
              }}>
                <span style={{ fontSize: '8px' }}>⚠️</span>
                UNSAVED
              </div>
            )}
          </div>
        )}

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
              color: isDarkMode ? '#94a3b8' : '#6b7280'
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
                background: isDarkMode ? '#7f1d1d' : '#fee2e2',
                color: isDarkMode ? '#fca5a5' : '#991b1b',
                borderRadius: '6px',
                border: isDarkMode ? '1px solid #991b1b' : '1px solid #fecaca'
              }}>
                {error}
              </div>
            </div>
          ) : document ? (
            <>
              {/* Left Side - Text Editor */}
              <div style={{
                flex: 1,
                padding: '20px',
                overflowY: 'auto',
                borderRight: isDarkMode ? '1px solid #475569' : '1px solid #e5e7eb',
                display: 'flex',
                flexDirection: 'column',
                backgroundColor: isDarkMode ? '#1e293b' : 'white'
              }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '12px',
                  paddingBottom: '8px',
                  borderBottom: isDarkMode ? '1px solid #475569' : '1px solid #f3f4f6'
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px'
                  }}>
                    <label style={{
                      fontSize: '14px',
                      fontWeight: '600',
                      color: isDarkMode ? '#f1f5f9' : '#374151'
                    }}>
                      Extracted Text
                    </label>
                    
                    {/* Display Mode Toggle */}
                    <div style={{
                      display: 'flex',
                      backgroundColor: isDarkMode ? '#475569' : '#f3f4f6',
                      borderRadius: '6px',
                      padding: '2px',
                      border: isDarkMode ? '1px solid #64748b' : '1px solid #e5e7eb',
                    }}>
                      <button
                        onClick={() => setDisplayMode('structured')}
                        style={{
                          padding: '4px 8px',
                          fontSize: '11px',
                          fontWeight: '500',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          transition: 'all 0.2s',
                          backgroundColor: displayMode === 'structured' ? '#3b82f6' : 'transparent',
                          color: displayMode === 'structured' ? 'white' : (isDarkMode ? '#cbd5e1' : '#374151'),
                        }}
                      >
                        Structured
                      </button>
                      <button
                        onClick={() => setDisplayMode('raw')}
                        style={{
                          padding: '4px 8px',
                          fontSize: '11px',
                          fontWeight: '500',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          transition: 'all 0.2s',
                          backgroundColor: displayMode === 'raw' ? '#3b82f6' : 'transparent',
                          color: displayMode === 'raw' ? 'white' : (isDarkMode ? '#cbd5e1' : '#374151'),
                        }}
                      >
                        Raw Text
                      </button>
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '16px', fontSize: '12px', color: isDarkMode ? '#94a3b8' : '#6b7280' }}>
                    {document.wordCount && <span><strong>{document.wordCount}</strong> words</span>}
                    <span><strong>{document.content.length}</strong> characters</span>
                    {document.layoutSections && document.layoutSections.length > 0 && (
                      <span><strong>{document.layoutSections.length}</strong> sections</span>
                    )}
                  </div>
                </div>
                {displayMode === 'structured' ? (
                  <div style={{
                    width: '100%',
                    flex: 1,
                    padding: '16px',
                    border: isDarkMode ? '1px solid #64748b' : '1px solid #e5e7eb',
                    borderRadius: '8px',
                    backgroundColor: isDarkMode ? '#334155' : 'white',
                    boxSizing: 'border-box',
                    overflowY: 'auto',
                  }}>
                    {renderStructuredContent()}
                  </div>
                ) : (
                  <textarea
                    value={document.content}
                    onChange={handleContentChange}
                    style={{
                      width: '100%',
                      flex: 1,
                      padding: '16px',
                      fontSize: '14px',
                      lineHeight: '1.6',
                      border: isDarkMode ? '1px solid #64748b' : '1px solid #e5e7eb',
                      borderRadius: '8px',
                      color: isDarkMode ? '#f1f5f9' : '#111827',
                      backgroundColor: isDarkMode ? '#334155' : 'white',
                      resize: 'none',
                      boxSizing: 'border-box',
                      outline: 'none',
                      fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Monaco, Consolas, "Liberation Mono", "Courier New", monospace'
                    }}
                    placeholder="No text content extracted from this document..."
                    onFocus={(e) => {
                      e.currentTarget.style.borderColor = '#3b82f6';
                      e.currentTarget.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)';
                    }}
                    onBlur={(e) => {
                      e.currentTarget.style.borderColor = isDarkMode ? '#64748b' : '#e5e7eb';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                  />
                )}
              </div>

              {/* Right Side - Document Preview */}
              <div style={{
                flex: 1,
                padding: '20px',
                overflowY: 'auto',
                background: isDarkMode ? '#334155' : '#f8fafc',
                display: 'flex',
                flexDirection: 'column'
              }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  marginBottom: '12px',
                  paddingBottom: '8px',
                  borderBottom: isDarkMode ? '1px solid #475569' : '1px solid #e2e8f0'
                }}>
                  {/* <div style={{
                    width: '8px',
                    height: '8px',
                    backgroundColor: '#3b82f6',
                    borderRadius: '50%'
                  }}></div> */}
                  <label style={{
                    fontSize: '14px',
                    fontWeight: '600',
                    color: isDarkMode ? '#f1f5f9' : '#374151'
                  }}>
                    Document Preview
                  </label>
                </div>
                <div style={{
                  background: isDarkMode ? '#1e293b' : 'white',
                  border: isDarkMode ? '1px solid #64748b' : '1px solid #e5e7eb',
                  borderRadius: '8px',
                  flex: 1,
                  overflow: 'hidden',
                  boxShadow: isDarkMode ? '0 1px 3px 0 rgba(0, 0, 0, 0.3), 0 1px 2px 0 rgba(0, 0, 0, 0.2)' : '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
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
                      color: isDarkMode ? '#94a3b8' : '#6b7280'
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
            borderTop: isDarkMode ? '1px solid #475569' : '1px solid #e5e7eb',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            background: isDarkMode ? '#334155' : 'white',
            boxShadow: isDarkMode ? '0 -1px 3px 0 rgba(0, 0, 0, 0.3), 0 -1px 2px 0 rgba(0, 0, 0, 0.2)' : '0 -1px 3px 0 rgba(0, 0, 0, 0.1), 0 -1px 2px 0 rgba(0, 0, 0, 0.06)'
          }}>
            <div style={{
              fontSize: '12px',
              color: isDarkMode ? '#94a3b8' : '#6b7280',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span> Edit text and classification as needed</span>
              {classificationChanged && (
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '3px 8px',
                  backgroundColor: isDarkMode ? '#451a03' : '#fef3c7',
                  color: '#92400e',
                  borderRadius: '4px',
                  fontSize: '11px',
                  fontWeight: '600',
                  border: '1px solid #f59e0b'
                }}>
                  <span>⚠️</span>
                  Classification modified - save to apply
                </div>
              )}
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={onClose}
                style={{
                  padding: '7px 16px',
                  background: isDarkMode ? '#475569' : 'white',
                  color: isDarkMode ? '#cbd5e1' : '#6b7280',
                  border: isDarkMode ? '1px solid #64748b' : '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '14px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = isDarkMode ? '#64748b' : '#f9fafb';
                  e.currentTarget.style.borderColor = isDarkMode ? '#94a3b8' : '#9ca3af';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = isDarkMode ? '#475569' : 'white';
                  e.currentTarget.style.borderColor = isDarkMode ? '#64748b' : '#d1d5db';
                }}
              >
                Cancel
              </button>
              <button
                onClick={async () => {
                  await handleSave();
                  onClose();
                }}
                disabled={isSaving}
                style={{
                  padding: '7px 20px',
                  background: isSaving ? (isDarkMode ? '#4b5563' : '#9ca3af') : (classificationChanged ? '#f59e0b' : '#3b82f6'),
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: isSaving ? 'not-allowed' : 'pointer',
                  transition: 'all 0.2s',
                  boxShadow: classificationChanged ? '0 0 0 3px rgba(245, 158, 11, 0.2)' : '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
                onMouseEnter={(e) => {
                  if (!isSaving) {
                    e.currentTarget.style.background = classificationChanged ? '#d97706' : '#2563eb';
                    e.currentTarget.style.transform = 'translateY(-1px)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isSaving) {
                    e.currentTarget.style.background = classificationChanged ? '#f59e0b' : '#3b82f6';
                    e.currentTarget.style.transform = 'translateY(0)';
                  }
                }}
              >
                {isSaving ? (
                  <>
                    <span style={{ 
                      width: '12px', 
                      height: '12px', 
                      border: '2px solid #ffffff40',
                      borderTop: '2px solid white',
                      borderRadius: '50%',
                      animation: 'spin 1s linear infinite'
                    }}></span>
                    Saving...
                  </>
                ) : classificationChanged ? (
                  <>
                    Save Classification
                  </>
                ) : (
                  <>
                    Save Changes
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentEditor;