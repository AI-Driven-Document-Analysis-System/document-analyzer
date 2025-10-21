
// "use client";

// import { useState, useEffect } from "react";
// import "./summarization.css";

// type GeneratedSummary = {
//   summary_text: string;
//   document_name?: string;
//   model_used?: string;
//   created_at?: string;
//   word_count?: number;
//   summary_type?: string;
// };

// export default function Summarization() {
//   const [documents, setDocuments] = useState<any[]>([]);
//   const [selectedDocument, setSelectedDocument] = useState("");
//   const [summaryType, setSummaryType] = useState("brief");
//   const [summaryLength, setSummaryLength] = useState(150);
//   const [isGenerating, setIsGenerating] = useState(false);
//   const [generatedSummary, setGeneratedSummary] = useState<GeneratedSummary | null>(null);
//   const [error, setError] = useState("");
//   const [progress, setProgress] = useState("");
//   const [copySuccess, setCopySuccess] = useState(false);

//   // Preview states
//   const [previewUrl, setPreviewUrl] = useState<string | null>(null);
//   const [previewLoading, setPreviewLoading] = useState(false);
//   const [previewError, setPreviewError] = useState<string | null>(null);

//   const summaryOptions = [
//     { id: "brief", name: "Brief Summary", desc: "Quick overview using BART model", model: "BART" },
//     { id: "detailed", name: "Detailed Summary", desc: "Comprehensive analysis using Pegasus model", model: "Pegasus" },
//     { id: "domain_specific", name: "Domain Specific", desc: "Specialized summary using T5 model", model: "Domain Specific Model" },
//   ];

//   useEffect(() => {
//     fetchDocuments();
//   }, []);

//   useEffect(() => {
//     if (selectedDocument) {
//       fetchDocumentPreview(selectedDocument);
//     } else {
//       setPreviewUrl(null);
//       setPreviewError(null);
//     }
//   }, [selectedDocument]);

//   const fetchDocuments = async () => {
//     try {
//       const token = localStorage.getItem("token");
//       if (!token) {
//         setError("No authentication token found. Please log in again.");
//         return;
//       }

//       const response = await fetch("http://localhost:8000/api/documents/", {
//         headers: {
//           Authorization: `Bearer ${token}`,
//           "Content-Type": "application/json",
//         },
//       });

//       if (response.status === 401) {
//         localStorage.removeItem("token");
//         localStorage.removeItem("user");
//         setError("Session expired. Please log in again.");
//         return;
//       }

//       if (response.ok) {
//         const data = await response.json();
//         setDocuments(data.documents || []);
//         setError("");
//       } else {
//         const errorData = await response.json();
//         const msg = typeof errorData.detail === "string" ? errorData.detail : errorData.message || "Failed to fetch documents";
//         setError(msg);
//       }
//     } catch (err) {
//       console.error("Error fetching documents:", err);
//       setError("Network error while fetching documents");
//     }
//   };

//   // 👇 EXACT SAME AS DASHBOARD: Fetch signed URL for preview
//   const fetchDocumentPreview = async (docId: string) => {
//     setPreviewLoading(true);
//     setPreviewError(null);
//     try {
//       const token = localStorage.getItem("token");
//       if (!token) return;

//       const response = await fetch(`http://localhost:8000/api/documents/${docId}/download`, {
//         headers: {
//           "Authorization": `Bearer ${token}`,
//           "Content-Type": "application/json",
//         },
//       });

//       if (response.ok) {
//         const data = await response.json();
//         setPreviewUrl(data.download_url);
//       } else {
//         setPreviewError("Failed to load document preview");
//       }
//     } catch (err) {
//       console.error("Error getting preview URL:", err);
//       setPreviewError("Error loading document preview");
//     } finally {
//       setPreviewLoading(false);
//     }
//   };

//   // 👇 NEW: Open document in new tab using same signed URL
//   const openDocumentInNewTab = async () => {
//     if (!selectedDocument) return;

//     try {
//       const token = localStorage.getItem("token");
//       if (!token) {
//         setError("No authentication token found. Please log in again.");
//         return;
//       }

//       const response = await fetch(`http://localhost:8000/api/documents/${selectedDocument}/download`, {
//         headers: {
//           "Authorization": `Bearer ${token}`,
//           "Content-Type": "application/json",
//         },
//       });

//       if (response.ok) {
//         const data = await response.json();
//         window.open(data.download_url, "_blank");
//       } else {
//         setError("Failed to open document. Please try again.");
//       }
//     } catch (err) {
//       console.error("Error opening document in new tab:", err);
//       setError("Error opening document in new tab");
//     }
//   };

//   const handleGenerateSummary = async () => {
//     if (!selectedDocument) {
//       setError("Please select a document first");
//       return;
//     }

//     setIsGenerating(true);
//     setError("");
//     setProgress("AI is generating summary...");
//     setGeneratedSummary(null);

//     try {
//       const token = localStorage.getItem("token");
//       const requestBody = {
//         document_id: selectedDocument,
//         summary_type: summaryType,
//         summary_length: summaryLength,
//       };

//       const response = await fetch("http://localhost:8000/api/summarize/", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//           Authorization: `Bearer ${token}`,
//         },
//         body: JSON.stringify(requestBody),
//       });

//       const data = await response.json();

//       if (response.ok && data.success) {
//         setProgress("Summary generated successfully!");
//         setGeneratedSummary({
//           ...data,
//           document_name: data.document_name || "Unknown Document",
//           model_used: data.model_used || "AI Selected",
//           created_at: data.created_at || new Date().toISOString(),
//           word_count: data.word_count || 0,
//           summary_type: data.summary_type || getSummaryTypeName(summaryType),
//         });
//       } else {
//         let errorMessage = `Request failed (${response.status})`;
//         if (response.status === 422 && data.detail) {
//           errorMessage = Array.isArray(data.detail)
//             ? data.detail.map((e: any) => `${e.loc?.join(".")}: ${e.msg}`).join(", ")
//             : data.detail;
//         } else if (data.detail) {
//           errorMessage = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
//         }
//         setError(errorMessage);
//       }
//     } catch (err) {
//       setError(`Network error: ${err instanceof Error ? err.message : "Unknown error"}`);
//     } finally {
//       setIsGenerating(false);
//       setProgress("");
//     }
//   };

//   const getSummaryTypeName = (typeId: string) => {
//     const option = summaryOptions.find((opt) => opt.id === typeId);
//     return option ? option.name : "Unknown";
//   };

//   const handleCopy = async () => {
//     if (generatedSummary?.summary_text) {
//       try {
//         await navigator.clipboard.writeText(generatedSummary.summary_text);
//         setCopySuccess(true);
//         setTimeout(() => setCopySuccess(false), 2000);
//       } catch {
//         const textArea = document.createElement("textarea");
//         textArea.value = generatedSummary.summary_text;
//         document.body.appendChild(textArea);
//         textArea.select();
//         document.execCommand("copy");
//         document.body.removeChild(textArea);
//         setCopySuccess(true);
//         setTimeout(() => setCopySuccess(false), 2000);
//       }
//     }
//   };

//   const handleExport = () => {
//     if (generatedSummary) {
//       const content = `Document: ${generatedSummary.document_name}
// Model: ${generatedSummary.model_used}
// Type: ${generatedSummary.summary_type}
// Generated: ${new Date(generatedSummary.created_at ?? "").toLocaleString()}

// Summary:
// ${generatedSummary.summary_text}`;

//       const blob = new Blob([content], { type: "text/plain" });
//       const url = URL.createObjectURL(blob);
//       const a = document.createElement("a");
//       a.href = url;
//       a.download = `summary-${generatedSummary.document_name}.txt`;
//       document.body.appendChild(a);
//       a.click();
//       document.body.removeChild(a);
//       URL.revokeObjectURL(url);
//     }
//   };

//   const selectedDocumentData = documents.find((d) => d.id === selectedDocument);

//   // Determine file type for preview
//   const getFileType = () => {
//     if (!selectedDocumentData) return null;
//     const filename = selectedDocumentData.original_filename || "";
//     const contentType = selectedDocumentData.content_type || "";

//     if (contentType.includes("pdf") || filename.toLowerCase().endsWith(".pdf")) {
//       return "PDF";
//     }
//     if (
//       contentType.includes("image") ||
//       /\.(jpg|jpeg|png|gif|bmp|webp)$/i.test(filename)
//     ) {
//       return "IMAGE";
//     }
//     return "OTHER";
//   };

//   const fileType = getFileType();
//   const isPdf = fileType === "PDF";
//   const isImage = fileType === "IMAGE";

//   return (
//   <div className="summarization-container">
//     {/* Header */}
//     <div className="summarization-header">
//       <h1>AI-Powered Document Summarization</h1>
//       <p>Select your document and summary type to generate intelligent summaries</p>
//     </div>

//     {progress && !isGenerating && <div className="message-success">{progress}</div>}
//     {error && <div className="message-error">{error}</div>}
//     {copySuccess && <div className="message-success">Copied to clipboard!</div>}

//     <div className="layout-grid">
//       <div className="left-panel">
//         {/* Document Selection */}
//         <div className="card">
//           <div className="card-header">
//             <h2>Select Document</h2>
//           </div>
//           <div className="card-body document-select">
//             <select
//               value={selectedDocument}
//               onChange={(e) => setSelectedDocument(e.target.value)}
//             >
//               <option value="">Select a document from the list</option>
//               {documents.map((doc) => (
//                 <option key={doc.id} value={doc.id}>
//                   {doc.original_filename || doc.name}
//                   {doc.document_type && ` (${doc.document_type})`}
//                   {doc.page_count && ` • ${doc.page_count} pages`}
//                 </option>
//               ))}
//             </select>

//             {selectedDocumentData && (
//               <div className="document-info">
//                 <div>
//                   <span className="label">Document:</span>{" "}
//                   <span className="value">{selectedDocumentData.original_filename}</span>
//                 </div>
//                 {selectedDocumentData.document_type && (
//                   <div>
//                     <span className="label">Type:</span>{" "}
//                     <span className="value">{selectedDocumentData.document_type}</span>
//                   </div>
//                 )}
//                 {selectedDocumentData.page_count && (
//                   <div>
//                     <span className="label">Pages:</span>{" "}
//                     <span className="value">{selectedDocumentData.page_count}</span>
//                   </div>
//                 )}

//                 {/* Open in New Tab Button */}
//                 <div style={{ marginTop: "16px" }}>
//                   <button
//                     onClick={openDocumentInNewTab}
//                     className="open-in-tab-btn"
//                     title="Open full document in new tab"
//                   >
//                     <i className="fas fa-external-link-alt"></i>
//                     Open in New Tab
//                   </button>
//                 </div>
//               </div>
//             )}

//             {/* Document Preview */}
//             {selectedDocument && (
//               <div className="document-preview-container">
//                 <h3 className="preview-title">Document Preview</h3>
//                 {previewLoading ? (
//                   <div className="preview-loading">
//                     <div className="spinner small"></div>
//                     <p>Loading preview...</p>
//                   </div>
//                 ) : previewError ? (
//                   <div className="preview-error">
//                     <i className="fas fa-exclamation-triangle"></i> {previewError}
//                   </div>
//                 ) : previewUrl ? (
//                   <div className="preview-viewer">
//                     {isPdf ? (
//                       <iframe
//                         src={previewUrl}
//                         title="Document Preview"
//                         className="preview-iframe"
//                       ></iframe>
//                     ) : isImage ? (
//                       <img
//                         src={previewUrl}
//                         alt="Document Preview"
//                         className="preview-image"
//                       />
//                     ) : (
//                       <div className="preview-unsupported">
//                         <i className="fas fa-file-alt"></i>
//                         <p>Preview not available for this file type.</p>
//                       </div>
//                     )}
//                   </div>
//                 ) : null}
//               </div>
//             )}
//           </div>
//         </div>

//         {/* Summary Options */}
//         <div className="card">
//           <div className="card-header">
//             <h2>Summary Options</h2>
//           </div>
//           <div className="card-body">
//             <div className="model-options">
//               {summaryOptions.map((option) => (
//                 <div
//                   key={option.id}
//                   className={`model-option ${
//                     summaryType === option.id ? "selected" : ""
//                   }`}
//                   onClick={() => setSummaryType(option.id)}
//                 >
//                   <div className="model-option-content">
//                     <div className="model-option-radio"></div>
//                     <div>
//                       <div className="model-option-title">{option.name}</div>
//                       <p className="model-option-desc">{option.desc}</p>
//                       <p className="model-option-model">Model: {option.model}</p>
//                     </div>
//                   </div>
//                 </div>
//               ))}
//             </div>

//             <button
//               onClick={handleGenerateSummary}
//               disabled={!selectedDocument || isGenerating}
//               className="generate-button"
//             >
//               {isGenerating ? (
//                 <>
//                   <span className="spinner"></span>
//                   AI Processing...
//                 </>
//               ) : (
//                 "Generate Summary"
//               )}
//             </button>
//           </div>
//         </div>
//       </div>

//       {/* Right Panel */}
//       <div className="right-panel">
//         <div className="results-card">
//           <div className="results-header">
//             <div>
//               <h2>AI Generated Summary</h2>
//               {generatedSummary && (
//                 <p>
//                   Generated using {generatedSummary.model_used} • {generatedSummary.summary_type}
//                 </p>
//               )}
//             </div>
//           </div>
//           <div className="results-content">
//             {isGenerating ? (
//               <div className="loading-state">
//                 <div className="ripple-spinner"></div>
//                 <h3 className="processing-text">AI is Processing Your Document</h3>
//                 <p>
//                   This may take a few minutes. Please wait while our AI analyzes your document and
//                   generates a comprehensive summary.
//                 </p>
//                 <div className="dots">
//                   <div className="dot"></div>
//                   <div className="dot"></div>
//                   <div className="dot"></div>
//                 </div>
//               </div>
//             ) : generatedSummary ? (
//               <div>
//                 <div className="summary-box">
//                   {generatedSummary.summary_text.split("\n").map((paragraph, index) => (
//                     <p key={index}>{paragraph}</p>
//                   ))}
//                 </div>
//                 <div className="summary-meta">
//                   <div>
//                     <span>Word count: {generatedSummary.word_count || "N/A"}</span>
//                   </div>
//                   <div>
//                     <span>Model: {generatedSummary.model_used}</span>
//                   </div>
//                   <div>
//                     <span>Type: {generatedSummary.summary_type}</span>
//                   </div>
//                   <div>
//                     <span>
//                       Generated: {new Date(generatedSummary.created_at ?? "").toLocaleString()}
//                     </span>
//                   </div>
//                 </div>

//                 {/* 👇 NEW: ACTION BUTTONS WITH INLINE CSS */}
//                 <div style={{ marginTop: "24px", display: "flex", gap: "12px", flexWrap: "wrap" }}>
//                   {/* Copy Button */}
//                   <button
//                     onClick={handleCopy}
//                     style={{
//                       padding: "12px 24px",
//                       backgroundColor: "#3b82f6",
//                       color: "white",
//                       border: "none",
//                       borderRadius: "8px",
//                       fontSize: "1rem",
//                       fontWeight: "600",
//                       cursor: "pointer",
//                       display: "flex",
//                       alignItems: "center",
//                       gap: "8px",
//                       boxShadow: "0 2px 6px rgba(59, 130, 246, 0.3)",
//                       transition: "background-color 0.2s",
//                     }}
//                     onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#2563eb")}
//                     onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "#3b82f6")}
//                   >
//                     <i className="fas fa-copy"></i>
//                     Copy Summary
//                   </button>

//                   {/* Export Button */}
//                   <button
//                     onClick={handleExport}
//                     style={{
//                       padding: "12px 24px",
//                       backgroundColor: "#10b981",
//                       color: "white",
//                       border: "none",
//                       borderRadius: "8px",
//                       fontSize: "1rem",
//                       fontWeight: "600",
//                       cursor: "pointer",
//                       display: "flex",
//                       alignItems: "center",
//                       gap: "8px",
//                       boxShadow: "0 2px 6px rgba(16, 185, 129, 0.3)",
//                       transition: "background-color 0.2s",
//                     }}
//                     onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#0da271")}
//                     onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "#10b981")}
//                   >
//                     <i className="fas fa-download"></i>
//                     Export as TXT
//                   </button>

//                   {/* Email Button */}
//                   <button
//                     onClick={async () => {
//                       // Fetch email and send
//                       try {
//                         const token = localStorage.getItem("token");
//                         if (!token) {
//                           setError("Please log in to email your summary.");
//                           return;
//                         }
//                         const res = await fetch("http://localhost:8000/api/profile/me", {
//                           headers: { Authorization: `Bearer ${token}` },
//                         });
//                         if (res.ok) {
//                           const profile = await res.json();
//                           const emailRes = await fetch("http://localhost:8000/api/summarize/email", {
//                             method: "POST",
//                             headers: {
//                               "Content-Type": "application/json",
//                               Authorization: `Bearer ${token}`,
//                             },
//                             body: JSON.stringify({
//                               document_id: selectedDocument,
//                               summary_type: summaryType,
//                               email: profile.email,
//                             }),
//                           });
//                           if (emailRes.ok) {
//                             setCopySuccess(true);
//                             setTimeout(() => setCopySuccess(false), 2000);
//                           } else {
//                             setError("Failed to email summary.");
//                           }
//                         }
//                       } catch (err) {
//                         setError("Error sending email.");
//                       }
//                     }}
//                     style={{
//                       padding: "12px 24px",
//                       backgroundColor: "#8b5cf6",
//                       color: "white",
//                       border: "none",
//                       borderRadius: "8px",
//                       fontSize: "1rem",
//                       fontWeight: "600",
//                       cursor: "pointer",
//                       display: "flex",
//                       alignItems: "center",
//                       gap: "8px",
//                       boxShadow: "0 2px 6px rgba(139, 92, 246, 0.3)",
//                       transition: "background-color 0.2s",
//                     }}
//                     onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#7c3aed")}
//                     onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "#8b5cf6")}
//                   >
//                     <i className="fas fa-envelope"></i>
//                     Email Summary
//                   </button>
//                 </div>

//                 {copySuccess && (
//                   <div
//                     style={{
//                       marginTop: "16px",
//                       padding: "12px",
//                       backgroundColor: "#dcfce7",
//                       color: "#166534",
//                       border: "1px solid #bbf7d0",
//                       borderRadius: "8px",
//                       fontWeight: "500",
//                       textAlign: "center",
//                     }}
//                   >
//                     ✅ Summary copied or emailed successfully!
//                   </div>
//                 )}
//               </div>
//             ) : (
//               <div className="empty-state">
//                 <div style={{ fontSize: "3rem" }}>📝</div>
//                 <h3>Ready to Generate</h3>
//                 <p>
//                   Select a document from the dropdown menu on the left and choose a summary type.
//                   Click the "Generate Summary" button to create an AI-powered summary of your
//                   document.
//                 </p>
//               </div>
//             )}
//           </div>
//         </div>
//       </div>
//     </div>
//   </div>
// );}




"use client";

import { useState, useEffect } from "react";
import "./summarization.css";

type GeneratedSummary = {
  summary_text: string;
  document_name?: string;
  model_used?: string;
  created_at?: string;
  word_count?: number;
  summary_type?: string;
};

// Storage keys for persistence
const STORAGE_KEYS = {
  PROCESSING_STATE: 'summarization_processing_state',
  SELECTED_DOCUMENT: 'summarization_selected_document',
  SUMMARY_TYPE: 'summarization_summary_type',
  GENERATED_SUMMARY: 'summarization_generated_summary'
};

// Helper functions for localStorage
const saveToStorage = (key: string, value: any) => {
  try {
    localStorage.setItem(key, JSON.stringify({
      data: value,
      timestamp: Date.now()
    }));
  } catch (error) {
    console.warn('Failed to save to localStorage:', error);
  }
};

const loadFromStorage = (key: string, maxAge: number = 30 * 60 * 1000) => { // 30 minutes default
  try {
    const stored = localStorage.getItem(key);
    if (!stored) return null;
    
    const parsed = JSON.parse(stored);
    const age = Date.now() - parsed.timestamp;
    
    if (age > maxAge) {
      localStorage.removeItem(key);
      return null;
    }
    
    return parsed.data;
  } catch (error) {
    console.warn('Failed to load from localStorage:', error);
    return null;
  }
};

const clearFromStorage = (key: string) => {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.warn('Failed to clear from localStorage:', error);
  }
};

export default function Summarization() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [selectedDocument, setSelectedDocument] = useState("");
  const [summaryType, setSummaryType] = useState("brief");
  const [summaryLength, setSummaryLength] = useState(150);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedSummary, setGeneratedSummary] = useState<GeneratedSummary | null>(null);
  const [error, setError] = useState("");
  const [progress, setProgress] = useState("");
  const [copySuccess, setCopySuccess] = useState(false);
  
  // AbortController for cancelling requests
  const [abortController, setAbortController] = useState<AbortController | null>(null);
  const [isCancelling, setIsCancelling] = useState(false);

  // Preview states
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);

  const summaryOptions = [
    { id: "brief", name: "Brief Summary", desc: "Quick overview using BART model", model: "BART" },
    { id: "detailed", name: "Detailed Summary", desc: "Comprehensive analysis using Pegasus model", model: "Pegasus" },
    { id: "domain_specific", name: "Domain Specific", desc: "Specialized summary using T5 model", model: "Domain Specific Model" },
  ];

  // Cancel current processing
  const cancelProcessing = () => {
    setIsCancelling(true);
    setProgress("Cancelling request...");
    
    if (abortController) {
      abortController.abort();
    }
    
    // Clear states after a short delay to show cancellation feedback
    setTimeout(() => {
      setIsGenerating(false);
      setProgress("");
      setError("");
      setIsCancelling(false);
      setAbortController(null);
      clearFromStorage(STORAGE_KEYS.PROCESSING_STATE);
    }, 500);
  };

  // Cleanup stale processing states
  const cleanupStaleProcessingState = () => {
    const savedProcessingState = loadFromStorage(STORAGE_KEYS.PROCESSING_STATE, 10 * 60 * 1000); // 10 minutes
    if (savedProcessingState && savedProcessingState.isGenerating) {
      // If processing state is older than 10 minutes, consider it stale
      setError("Previous processing session was interrupted. Please try generating the summary again.");
      clearFromStorage(STORAGE_KEYS.PROCESSING_STATE);
      return true;
    }
    return false;
  };

  // Restore state from localStorage on component mount
  useEffect(() => {
    // Check for stale processing states first
    const hadStaleState = cleanupStaleProcessingState();
    
    if (!hadStaleState) {
      // Restore processing state only if not stale
      const savedProcessingState = loadFromStorage(STORAGE_KEYS.PROCESSING_STATE);
      if (savedProcessingState) {
        setIsGenerating(savedProcessingState.isGenerating);
        setProgress(savedProcessingState.progress || "AI is processing your document...");
        setError(savedProcessingState.error || "");
      }
    }

    // Restore selected document
    const savedSelectedDocument = loadFromStorage(STORAGE_KEYS.SELECTED_DOCUMENT);
    if (savedSelectedDocument) {
      setSelectedDocument(savedSelectedDocument);
    }

    // Restore summary type
    const savedSummaryType = loadFromStorage(STORAGE_KEYS.SUMMARY_TYPE);
    if (savedSummaryType) {
      setSummaryType(savedSummaryType);
    }

    // Restore generated summary
    const savedGeneratedSummary = loadFromStorage(STORAGE_KEYS.GENERATED_SUMMARY);
    if (savedGeneratedSummary) {
      setGeneratedSummary(savedGeneratedSummary);
    }

    fetchDocuments();
  }, []);

  // Cleanup on component unmount
  useEffect(() => {
    return () => {
      // Cancel any ongoing requests when component unmounts
      if (abortController) {
        abortController.abort();
      }
    };
  }, [abortController]);

  useEffect(() => {
    if (selectedDocument) {
      fetchDocumentPreview(selectedDocument);
    } else {
      setPreviewUrl(null);
      setPreviewError(null);
    }
  }, [selectedDocument]);

  const fetchDocuments = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("No authentication token found. Please log in again.");
        return;
      }

      const response = await fetch("http://localhost:8000/api/documents/", {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.status === 401) {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        setError("Session expired. Please log in again.");
        return;
      }

      if (response.ok) {
        const data = await response.json();
        setDocuments(data.documents || []);
        setError("");
      } else {
        const errorData = await response.json();
        const msg = typeof errorData.detail === "string" ? errorData.detail : errorData.message || "Failed to fetch documents";
        setError(msg);
      }
    } catch (err) {
      console.error("Error fetching documents:", err);
      setError("Network error while fetching documents");
    }
  };

  const fetchDocumentPreview = async (docId: string) => {
    setPreviewLoading(true);
    setPreviewError(null);
    try {
      const token = localStorage.getItem("token");
      if (!token) return;

      const response = await fetch(`http://localhost:8000/api/documents/${docId}/download`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        setPreviewUrl(data.download_url);
      } else {
        setPreviewError("Failed to load document preview");
      }
    } catch (err) {
      console.error("Error getting preview URL:", err);
      setPreviewError("Error loading document preview");
    } finally {
      setPreviewLoading(false);
    }
  };

  const openDocumentInNewTab = async () => {
    if (!selectedDocument) return;

    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("No authentication token found. Please log in again.");
        return;
      }

      const response = await fetch(`http://localhost:8000/api/documents/${selectedDocument}/download`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        window.open(data.download_url, "_blank");
      } else {
        setError("Failed to open document. Please try again.");
      }
    } catch (err) {
      console.error("Error opening document in new tab:", err);
      setError("Error opening document in new tab");
    }
  };

  const handleGenerateSummary = async () => {
    if (!selectedDocument) {
      setError("Please select a document first");
      return;
    }

    // Cancel any existing request
    if (abortController) {
      abortController.abort();
    }

    // Create new AbortController for this request
    const newAbortController = new AbortController();
    setAbortController(newAbortController);

    setIsGenerating(true);
    setError("");
    setProgress("AI is generating summary...");
    setGeneratedSummary(null);

    // Save processing state to localStorage
    saveToStorage(STORAGE_KEYS.PROCESSING_STATE, {
      isGenerating: true,
      progress: "AI is generating summary...",
      error: ""
    });
    saveToStorage(STORAGE_KEYS.SELECTED_DOCUMENT, selectedDocument);
    saveToStorage(STORAGE_KEYS.SUMMARY_TYPE, summaryType);
    clearFromStorage(STORAGE_KEYS.GENERATED_SUMMARY);

    try {
      const token = localStorage.getItem("token");
      const requestBody = {
        document_id: selectedDocument,
        summary_type: summaryType,
        summary_length: summaryLength,
      };

      // Set a timeout for the request (2 minutes for faster response)
      const timeoutId = setTimeout(() => {
        newAbortController.abort();
        setError("Request timed out. Please try again with a shorter document or different summary type.");
      }, 2 * 60 * 1000); // 2 minutes - optimized for faster response

      const response = await fetch("http://localhost:8000/api/summarize/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(requestBody),
        signal: newAbortController.signal, // Add abort signal
      });

      // Clear timeout if request completes
      clearTimeout(timeoutId);

      const data = await response.json();

      if (response.ok && data.success) {
        const summaryData = {
          ...data,
          document_name: data.document_name || "Unknown Document",
          model_used: data.model_used || "AI Selected",
          created_at: data.created_at || new Date().toISOString(),
          word_count: data.word_count || 0,
          summary_type: data.summary_type || getSummaryTypeName(summaryType),
        };
        
        setProgress("Summary generated successfully!");
        setGeneratedSummary(summaryData);
        
        // Save successful result to localStorage
        saveToStorage(STORAGE_KEYS.GENERATED_SUMMARY, summaryData);
        clearFromStorage(STORAGE_KEYS.PROCESSING_STATE);
      } else {
        let errorMessage = `Request failed (${response.status})`;
        if (response.status === 422 && data.detail) {
          errorMessage = Array.isArray(data.detail)
            ? data.detail.map((e: any) => `${e.loc?.join(".")}: ${e.msg}`).join(", ")
            : data.detail;
        } else if (data.detail) {
          errorMessage = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
        }
        setError(errorMessage);
        
        // Save error state to localStorage
        saveToStorage(STORAGE_KEYS.PROCESSING_STATE, {
          isGenerating: false,
          progress: "",
          error: errorMessage
        });
      }
    } catch (err) {
      // Don't show error if request was cancelled
      if (err instanceof Error && err.name === 'AbortError') {
        console.log('Summary generation was cancelled');
        setProgress("Request cancelled");
        setTimeout(() => {
          setProgress("");
        }, 2000);
        return;
      }
      
      const errorMessage = `Network error: ${err instanceof Error ? err.message : "Unknown error"}`;
      setError(errorMessage);
      
      // Save error state to localStorage
      saveToStorage(STORAGE_KEYS.PROCESSING_STATE, {
        isGenerating: false,
        progress: "",
        error: errorMessage
      });
    } finally {
      setIsGenerating(false);
      setProgress("");
      setAbortController(null);
      
      // Clear processing state from localStorage when done
      clearFromStorage(STORAGE_KEYS.PROCESSING_STATE);
    }
  };

  const getSummaryTypeName = (typeId: string) => {
    const option = summaryOptions.find((opt) => opt.id === typeId);
    return option ? option.name : "Unknown";
  };

  const handleCopy = async () => {
    if (generatedSummary?.summary_text) {
      try {
        await navigator.clipboard.writeText(generatedSummary.summary_text);
        setCopySuccess(true);
        setTimeout(() => setCopySuccess(false), 2000);
      } catch {
        const textArea = document.createElement("textarea");
        textArea.value = generatedSummary.summary_text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand("copy");
        document.body.removeChild(textArea);
        setCopySuccess(true);
        setTimeout(() => setCopySuccess(false), 2000);
      }
    }
  };

  const handleExport = () => {
    if (generatedSummary) {
      const content = `Document: ${generatedSummary.document_name}
Model: ${generatedSummary.model_used}
Type: ${generatedSummary.summary_type}
Generated: ${new Date(generatedSummary.created_at ?? "").toLocaleString()}

Summary:
${generatedSummary.summary_text}`;

      const blob = new Blob([content], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `summary-${generatedSummary.document_name}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  const selectedDocumentData = documents.find((d) => d.id === selectedDocument);

  const getFileType = () => {
    if (!selectedDocumentData) return null;
    const filename = selectedDocumentData.original_filename || "";
    const contentType = selectedDocumentData.content_type || "";

    if (contentType.includes("pdf") || filename.toLowerCase().endsWith(".pdf")) {
      return "PDF";
    }
    if (
      contentType.includes("image") ||
      /\.(jpg|jpeg|png|gif|bmp|webp)$/i.test(filename)
    ) {
      return "IMAGE";
    }
    return "OTHER";
  };

  const fileType = getFileType();
  const isPdf = fileType === "PDF";
  const isImage = fileType === "IMAGE";

  return (
    <div className="summarization-container">
      {/* Header */}
      <div className="summarization-header">
        <h1>AI-Powered Document Summarization</h1>
        <p>Select your document and summary type to generate intelligent summaries</p>
      </div>

      {progress && !isGenerating && <div className="message-success">{progress}</div>}
      {error && <div className="message-error">{error}</div>}
      {copySuccess && <div className="message-success">Copied to clipboard!</div>}

      <div className="layout-grid">
        <div className="left-panel">
          {/* Document Selection */}
          <div className="card" style={{ backgroundColor: "var(--bg-primary)", borderColor: "var(--border-color)" }} >
            <div className="card-header">
              <h2>Select Document</h2>
            </div>
            <div className="card-body document-select">
              <select
                value={selectedDocument}
                onChange={(e) => {
                  const newValue = e.target.value;
                  setSelectedDocument(newValue);
                  saveToStorage(STORAGE_KEYS.SELECTED_DOCUMENT, newValue);
                }}
                className="form-select"
              >
                <option value="">Select a document from the list</option>
                {documents.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    {doc.original_filename || doc.name}
                    {doc.document_type && ` (${doc.document_type})`}
                    {doc.page_count && ` • ${doc.page_count} pages`}
                  </option>
                ))}
              </select>

              {selectedDocumentData && (
                <div className="document-info">
                  <div>
                    <span className="label">Document:</span>{" "}
                    <span className="value">{selectedDocumentData.original_filename}</span>
                  </div>
                  {selectedDocumentData.document_type && (
                    <div>
                      <span className="label">Type:</span>{" "}
                      <span className="value">{selectedDocumentData.document_type}</span>
                    </div>
                  )}
                  {selectedDocumentData.page_count && (
                    <div>
                      <span className="label">Pages:</span>{" "}
                      <span className="value">{selectedDocumentData.page_count}</span>
                    </div>
                  )}

                  <div style={{ marginTop: "16px" }}>
                    <button
                      onClick={openDocumentInNewTab}
                      className="open-in-tab-btn"
                      title="Open full document in new tab"
                    >
                      <i className="fas fa-external-link-alt"></i>
                      Open in New Tab
                    </button>
                  </div>
                </div>
              )}

              {/* Document Preview */}
              {selectedDocument && (
                <div className="document-preview-container">
                  <h3 className="preview-title">Document Preview</h3>
                  {previewLoading ? (
                    <div className="preview-loading">
                      <div className="spinner small"></div>
                      <p>Loading preview...</p>
                    </div>
                  ) : previewError ? (
                    <div className="preview-error">
                      <i className="fas fa-exclamation-triangle"></i> {previewError}
                    </div>
                  ) : previewUrl ? (
                    <div className="preview-viewer">
                      {isPdf ? (
                        <iframe
                          src={previewUrl}
                          title="Document Preview"
                          className="preview-iframe"
                        ></iframe>
                      ) : isImage ? (
                        <img
                          src={previewUrl}
                          alt="Document Preview"
                          className="preview-image"
                        />
                      ) : (
                        <div className="preview-unsupported">
                          <i className="fas fa-file-alt"></i>
                          <p>Preview not available for this file type.</p>
                        </div>
                      )}
                    </div>
                  ) : null}
                </div>
              )}
            </div>
          </div>

          {/* Summary Options — NOW A DROPDOWN */}
          <div className="card" style={{ backgroundColor: "var(--bg-primary)", borderColor: "var(--border-color)" }}>
            <div className="card-header" style={{ backgroundColor: "var(--bg-primary)", borderColor: "var(--border-color)" }}>
              <h2>Summary Options</h2>
            </div>
            <div className="card-body" style={{ backgroundColor: "var(--bg-primary)", borderColor: "var(--border-color)" }}>
              <div className="model-select">
                <select
                  value={summaryType}
                  onChange={(e) => {
                    const newValue = e.target.value;
                    setSummaryType(newValue);
                    saveToStorage(STORAGE_KEYS.SUMMARY_TYPE, newValue);
                  }}
                  className="form-select"
                  style={{
                    backgroundColor: "var(--input-bg)",
                    color: "var(--text-primary)",
                    borderColor: "var(--input-border)",
                    colorScheme: "dark",
                  }}
                >
                  
                {/* <option value="" disabled >
                  Select a summary type
                </option> */}
                <option value="">Select a summary type from the list</option>
                {summaryOptions.map((option) => (
                  <option key={option.id} value={option.id}>
                    {option.name} – {option.model}
                  </option>
                ))}
              </select>
              </div>

              <button
                onClick={handleGenerateSummary}
                disabled={!selectedDocument || isGenerating}
                className="generate-button"
              >
                {isGenerating ? (
                  <>
                    <span className="spinner"></span>
                    AI Processing...
                  </>
                ) : (
                  "Generate Summary"
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Right Panel */}
        <div className="right-panel">
          <div className="results-card">
            <div className="results-header">
              <div>
                <h2>AI Generated Summary</h2>
                {generatedSummary && (
                  <p>
                    Generated using {generatedSummary.model_used} • {generatedSummary.summary_type}
                  </p>
                )}
              </div>
            </div>
            <div className="results-content">
              {isGenerating ? (
                <div className="loading-state">
                  <div className="ripple-spinner"></div>
                  <h3 className="processing-text">
                    {isCancelling ? "Cancelling Request..." : "AI is Processing Your Document"}
                  </h3>
                  <p>
                    {isCancelling 
                      ? "Please wait while we cancel the current request."
                      : "This may take a few minutes. Please wait while our AI analyzes your document and generates a comprehensive summary."
                    }
                  </p>
                  {progress && (
                    <div style={{ 
                      marginTop: "16px", 
                      padding: "12px", 
                      backgroundColor: "var(--bg-secondary)", 
                      borderRadius: "8px",
                      color: "var(--text-secondary)",
                      fontSize: "0.9rem"
                    }}>
                      {progress}
                    </div>
                  )}
                  <div className="dots">
                    <div className="dot"></div>
                    <div className="dot"></div>
                    <div className="dot"></div>
                  </div>
                  <div style={{ marginTop: "20px" }}>
                    <button
                      onClick={cancelProcessing}
                      disabled={isCancelling}
                      style={{
                        padding: "8px 16px",
                        backgroundColor: isCancelling ? "#6b7280" : "var(--error-color, #ef4444)",
                        color: "white",
                        border: "none",
                        borderRadius: "6px",
                        fontSize: "0.9rem",
                        cursor: isCancelling ? "not-allowed" : "pointer",
                        transition: "background-color 0.2s",
                        opacity: isCancelling ? 0.7 : 1
                      }}
                      onMouseEnter={(e) => {
                        if (!isCancelling) {
                          e.currentTarget.style.backgroundColor = "#dc2626";
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (!isCancelling) {
                          e.currentTarget.style.backgroundColor = "var(--error-color, #ef4444)";
                        }
                      }}
                    >
                      {isCancelling ? "Cancelling..." : "Cancel Processing"}
                    </button>
                  </div>
                </div>
              ) : generatedSummary ? (
                <div>
                  <div className="summary-box">
                    {generatedSummary.summary_text.split("\n").map((paragraph, index) => (
                      <p key={index}>{paragraph}</p>
                    ))}
                  </div>
                  <div className="summary-meta">
                    <div>
                      <span>Word count: {generatedSummary.word_count || "N/A"}</span>
                    </div>
                    <div>
                      <span>Model: {generatedSummary.model_used}</span>
                    </div>
                    <div>
                      <span>Type: {generatedSummary.summary_type}</span>
                    </div>
                    <div>
                      <span>
                        Generated: {new Date(generatedSummary.created_at ?? "").toLocaleString()}
                      </span>
                    </div>
                  </div>

                  <div style={{ marginTop: "24px", display: "flex", gap: "12px", flexWrap: "wrap" }}>
                    <button
                      onClick={handleCopy}
                      style={{
                        padding: "12px 24px",
                        backgroundColor: "#3b82f6",
                        color: "white",
                        border: "none",
                        borderRadius: "8px",
                        fontSize: "1rem",
                        fontWeight: "600",
                        cursor: "pointer",
                        display: "flex",
                        alignItems: "center",
                        gap: "8px",
                        boxShadow: "0 2px 6px rgba(59, 130, 246, 0.3)",
                        transition: "background-color 0.2s",
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#2563eb")}
                      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "#3b82f6")}
                    >
                      <i className="fas fa-copy"></i>
                      Copy Summary
                    </button>

                    <button
                      onClick={handleExport}
                      style={{
                        padding: "12px 24px",
                        backgroundColor: "#10b981",
                        color: "white",
                        border: "none",
                        borderRadius: "8px",
                        fontSize: "1rem",
                        fontWeight: "600",
                        cursor: "pointer",
                        display: "flex",
                        alignItems: "center",
                        gap: "8px",
                        boxShadow: "0 2px 6px rgba(16, 185, 129, 0.3)",
                        transition: "background-color 0.2s",
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#0da271")}
                      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "#10b981")}
                    >
                      <i className="fas fa-download"></i>
                      Export as TXT
                    </button>

                    {/* <button
                      onClick={async () => {
                        try {
                          const token = localStorage.getItem("token");
                          if (!token) {
                            setError("Please log in to email your summary.");
                            return;
                          }
                          const res = await fetch("http://localhost:8000/api/profile/me", {
                            headers: { Authorization: `Bearer ${token}` },
                          });
                          if (res.ok) {
                            const profile = await res.json();
                            const emailRes = await fetch("http://localhost:8000/api/summarize/email", {
                              method: "POST",
                              headers: {
                                "Content-Type": "application/json",
                                Authorization: `Bearer ${token}`,
                              },
                              body: JSON.stringify({
                                document_id: selectedDocument,
                                summary_type: summaryType,
                                email: profile.email,
                              }),
                            });
                            if (emailRes.ok) {
                              setCopySuccess(true);
                              setTimeout(() => setCopySuccess(false), 2000);
                            } else {
                              setError("Failed to email summary.");
                            }
                          }
                        } catch (err) {
                          setError("Error sending email.");
                        }
                      }}
                      style={{
                        padding: "12px 24px",
                        backgroundColor: "#8b5cf6",
                        color: "white",
                        border: "none",
                        borderRadius: "8px",
                        fontSize: "1rem",
                        fontWeight: "600",
                        cursor: "pointer",
                        display: "flex",
                        alignItems: "center",
                        gap: "8px",
                        boxShadow: "0 2px 6px rgba(139, 92, 246, 0.3)",
                        transition: "background-color 0.2s",
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#7c3aed")}
                      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "#8b5cf6")}
                    >
                      <i className="fas fa-envelope"></i>
                      Email Summary
                    </button> */}
                  </div>

                  {copySuccess && (
                    <div
                      style={{
                        marginTop: "16px",
                        padding: "12px",
                        backgroundColor: "#dcfce7",
                        color: "#166534",
                        border: "1px solid #bbf7d0",
                        borderRadius: "8px",
                        fontWeight: "500",
                        textAlign: "center",
                      }}
                    >
                      ✅ Summary copied or emailed successfully!
                    </div>
                  )}
                </div>
              ) : (
                <div className="empty-state">
                  <div style={{ fontSize: "3rem" }}>📝</div>
                  <h3>Ready to Generate</h3>
                  <p>
                    Select a document from the dropdown menu on the left and choose a summary type.
                    Click the "Generate Summary" button to create an AI-powered summary of your
                    document.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

