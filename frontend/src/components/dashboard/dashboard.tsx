// //****************************CSS */
// import { useState, useEffect, useMemo } from "react"
// import './Dashboard.css' // Import the CSS file
// import '../../styles/components.css';
// //import DocumentViewer from '../DocumentViewer/DocumentViewer';


// // TypeScript interfaces
// interface Document {
//   id: string
//   original_filename: string
//   content_type: string
//   processing_status: 'completed' | 'processing' | 'failed'
//   upload_date: string
//   user_id: string
// }

// interface Summary {
//   id: number | string
//   summary_text: string
//   summary_type: string
//   word_count: number
//   model_used: string
//   created_at: string
//   from_cache: boolean
//   key_points?: string[] | null
//   document_type?: string | null
// }

// interface FormattedDocument {
//   id: string
//   name: string
//   type: string
//   status: string
//   uploadedAt: string
//   confidence: number | null
// }

// interface SummaryOption {
//   id: string
//   name: string
//   description: string
//   model: string
//   icon: string
// }

// interface DocumentWithSummary extends FormattedDocument {
//   showSummaryOptions: boolean
//   selectedModel: string | null
//   currentSummary: Summary | null
//   loadingSummary: boolean
//   generatingNew: boolean
//   summaryError: string | null
// }

// // Inline styles for modal
// const modalStyles = {
//   overlay: {
//     position: 'fixed' as const,
//     top: 0,
//     left: 0,
//     right: 0,
//     bottom: 0,
//     background: 'rgba(0, 0, 0, 0.75)',
//     backdropFilter: 'blur(8px)',
//     display: 'flex',
//     alignItems: 'center',
//     justifyContent: 'center',
//     zIndex: 9999,
//     padding: '20px',
//     animation: 'fadeInModal 0.3s ease-out'
//   },
//   container: {
//     background: 'white',
//     borderRadius: '16px',
//     width: '90vw',
//     maxWidth: '1200px',
//     height: '90vh',
//     maxHeight: '900px',
//     display: 'flex',
//     flexDirection: 'column' as const,
//     boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
//     overflow: 'hidden',
//     position: 'relative' as const,
//     animation: 'slideInModal 0.3s ease-out'
//   },
//   header: {
//     display: 'flex',
//     alignItems: 'center',
//     justifyContent: 'space-between',
//     padding: '20px 24px',
//     borderBottom: '1px solid #e5e7eb',
//     background: 'linear-gradient(135deg, #f8fafc, #e2e8f0)',
//     flexShrink: 0
//   },
//   title: {
//     flex: 1
//   },
//   titleH3: {
//     fontSize: '1.25rem',
//     fontWeight: 600,
//     color: '#1a202c',
//     margin: '0 0 4px 0'
//   },
//   titleP: {
//     fontSize: '0.875rem',
//     color: '#718096',
//     margin: 0
//   },
//   closeButton: {
//     background: 'none',
//     border: 'none',
//     fontSize: '24px',
//     color: '#718096',
//     cursor: 'pointer',
//     padding: '8px',
//     borderRadius: '8px',
//     transition: 'all 0.2s ease',
//     lineHeight: 1,
//     marginLeft: '16px'
//   },
//   body: {
//     flex: 1,
//     padding: 0,
//     overflow: 'hidden',
//     position: 'relative' as const,
//     background: '#f7fafc'
//   },
//   viewer: {
//     width: '100%',
//     height: '100%',
//     position: 'relative' as const
//   },
//   iframe: {
//     width: '100%',
//     height: '100%',
//     border: 'none',
//     background: 'white'
//   },
//   imageViewer: {
//     width: '100%',
//     height: '100%',
//     display: 'flex',
//     alignItems: 'center',
//     justifyContent: 'center',
//     padding: '20px',
//     overflow: 'auto'
//   },
//   image: {
//     maxWidth: '100%',
//     maxHeight: '100%',
//     objectFit: 'contain' as const,
//     borderRadius: '8px',
//     boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)'
//   },
//   loading: {
//     display: 'flex',
//     flexDirection: 'column' as const,
//     alignItems: 'center',
//     justifyContent: 'center',
//     height: '100%',
//     color: '#718096'
//   },
//   loadingSpinner: {
//     width: '48px',
//     height: '48px',
//     border: '4px solid #e2e8f0',
//     borderTop: '4px solid #667eea',
//     borderRadius: '50%',
//     animation: 'spin 1s linear infinite',
//     marginBottom: '16px'
//   },
//   error: {
//     display: 'flex',
//     flexDirection: 'column' as const,
//     alignItems: 'center',
//     justifyContent: 'center',
//     height: '100%',
//     textAlign: 'center' as const,
//     color: '#718096',
//     padding: '40px'
//   },
//   errorIcon: {
//     fontSize: '4rem',
//     marginBottom: '16px',
//     color: '#e53e3e'
//   },
//   errorH4: {
//     fontSize: '1.25rem',
//     color: '#2d3748',
//     marginBottom: '8px'
//   },
//   errorP: {
//     color: '#718096',
//     marginBottom: '24px'
//   },
//   unsupported: {
//     display: 'flex',
//     flexDirection: 'column' as const,
//     alignItems: 'center',
//     justifyContent: 'center',
//     height: '100%',
//     textAlign: 'center' as const,
//     padding: '40px',
//     color: '#718096'
//   },
//   fileIcon: {
//     fontSize: '4rem',
//     marginBottom: '16px',
//     color: '#a0aec0'
//   },
//   downloadBtn: {
//     background: 'linear-gradient(135deg, #667eea, #764ba2)',
//     color: 'white',
//     border: 'none',
//     padding: '12px 24px',
//     borderRadius: '8px',
//     fontSize: '1rem',
//     fontWeight: 600,
//     cursor: 'pointer',
//     transition: 'all 0.3s ease',
//     display: 'flex',
//     alignItems: 'center',
//     gap: '8px'
//   }
// };

// // Main Dashboard Component
// function Dashboard() {
//   const [documents, setDocuments] = useState<Document[]>([])
//   const [loading, setLoading] = useState(true)
//   const [error, setError] = useState<string | null>(null)
//   const [documentsWithSummary, setDocumentsWithSummary] = useState<DocumentWithSummary[]>([])
//   // Chat and modal states
//   const [activeView, setActiveView] = useState<'documents' | 'chat'>('documents')
//   const [selectedDocument, setSelectedDocument] = useState<any>(null)
//   const [summaryModalOpen, setSummaryModalOpen] = useState(false)
//   const [selectedDocumentForSummary, setSelectedDocumentForSummary] = useState<{id: string, name: string} | null>(null)
  
//   // Document preview states
//   const [previewDocument, setPreviewDocument] = useState<DocumentWithSummary | null>(null)
//   const [showPreview, setShowPreview] = useState(false)
//   const [previewUrl, setPreviewUrl] = useState<string | null>(null)
//   const [loadingPreview, setLoadingPreview] = useState(false)

//   // Summary options configuration
//   const summaryOptions: SummaryOption[] = [
//     {
//       id: 'brief',
//       name: 'Brief Summary',
//       description: 'Quick overview with key points (50-150 words)',
//       model: 'BART',
//       icon: 'fas fa-file-text'
//     },
//     {
//       id: 'detailed',
//       name: 'Detailed Summary',
//       description: 'Comprehensive analysis with full context (80-250 words)',
//       model: 'PEGASUS',
//       icon: 'fas fa-file-alt'
//     },
//     {
//       id: 'domain_specific',
//       name: 'Domain-Specific',
//       description: 'Specialized summary based on document type (70-200 words)',
//       model: 'Auto-Selected',
//       icon: 'fas fa-bullseye'
//     }
//   ]

//   // JWT token handling
//   const getToken = () => {
//     const token = localStorage.getItem("token")
//     return token
//   }

//   // Document preview handler
//   const previewDocumentHandler = async (doc: DocumentWithSummary) => {
//     setLoadingPreview(true)
//     setPreviewDocument(doc)
//     setShowPreview(true)

//     try {
//       const token = getToken()
//       if (!token) return

//       const response = await fetch(`http://localhost:8000/api/documents/${doc.id}/download`, {
//         headers: {
//           "Authorization": `Bearer ${token}`,
//           "Content-Type": "application/json",
//         },
//       })

//       if (response.ok) {
//         const data = await response.json()
//         setPreviewUrl(data.download_url)
//       } else {
//         console.error("Failed to get preview URL")
//         alert("Failed to load document preview")
//       }
//     } catch (err) {
//       console.error("Error getting preview URL:", err)
//       alert("Error loading document preview")
//     } finally {
//       setLoadingPreview(false)
//     }
//   }

//   // Close preview
//   const closePreview = () => {
//     setShowPreview(false)
//     setPreviewDocument(null)
//     setPreviewUrl(null)
//   }

//   // Fetch user documents with JWT authentication and fallback
//   useEffect(() => {
//     const fetchDocuments = async () => {
//       const tryFallback = async () => {
//         try {
//           const userStr = localStorage.getItem("user")
//           if (!userStr) {
//             throw new Error("No user info found for fallback fetch")
//           }
//           const user = JSON.parse(userStr)
//           const userId = user?.id || user?.user?.id || user?.user_id
//           if (!userId) {
//             throw new Error("No user_id in local storage user")
//           }
//           const res = await fetch(`http://localhost:8000/api/documents/by-user?user_id=${encodeURIComponent(userId)}`)
//           if (!res.ok) {
//             throw new Error("Fallback fetch failed")
//           }
//           const data = await res.json()
//           setDocuments(data.documents || [])
//           setError(null)
//         } catch (e) {
//           console.error("Fallback documents fetch error:", e)
//           setError("Failed to load documents")
//         } finally {
//           setLoading(false)
//         }
//       }

//       try {
//         const token = getToken()
//         if (!token) {
//           await tryFallback()
//           return
//         }

//         const response = await fetch("http://localhost:8000/api/documents/", {
//           headers: {
//             "Authorization": `Bearer ${token}`,
//             "Content-Type": "application/json",
//           },
//         })

//         if (response.status === 401) {
//           localStorage.removeItem("token")
//           await tryFallback()
//           return
//         }

//         if (!response.ok) {
//           await tryFallback()
//           return
//         }

//         const data = await response.json()
//         setDocuments(data.documents || [])
//         setLoading(false)
//       } catch (err) {
//         console.error("Error fetching documents:", err)
//         await tryFallback()
//       }
//     }

//     fetchDocuments()
//   }, [])

//   // Format date to relative time
//   const formatRelativeTime = (isoString: string): string => {
//     const past = new Date(isoString)
//     const now = new Date()
//     const diffInMs = now.getTime() - past.getTime()
//     const diffInHours = diffInMs / (1000 * 60 * 60)
//     const diffInDays = diffInHours / 24

//     if (diffInHours < 1) return "Less than an hour ago"
//     if (diffInHours < 24) return `${Math.floor(diffInHours)} hours ago`
//     if (diffInDays < 7) return `${Math.floor(diffInDays)} days ago`
//     return past.toLocaleDateString()
//   }

//   // Compute stats from real documents
//   const stats = useMemo(() => {
//     const total = documents.length
//     const today = new Date().setHours(0, 0, 0, 0)
//     const processedToday = documents.filter(
//       (doc) =>
//         doc.processing_status === "completed" &&
//         new Date(doc.upload_date).getTime() >= today
//     ).length
//     const inQueue = documents.filter(doc => doc.processing_status === "processing").length
//     const successRate = total > 0 ? ((documents.filter(doc => doc.processing_status === "completed").length / total) * 100).toFixed(1) : "0"

//     return [
//       {
//         title: "Total Documents",
//         value: total.toLocaleString(),
//         change: "+12%",
//         icon: "fas fa-file-alt",
//         positive: true
//       },
//       {
//         title: "Processed Today",
//         value: processedToday.toString(),
//         change: "+23%",
//         icon: "fas fa-check-circle",
//         positive: true
//       },
//       {
//         title: "Processing Queue",
//         value: inQueue.toString(),
//         change: inQueue > 0 ? "-5%" : "0%",
//         icon: "fas fa-clock",
//         positive: inQueue === 0
//       },
//       {
//         title: "Success Rate",
//         value: `${successRate}%`,
//         change: "+0.5%",
//         icon: "fas fa-chart-line",
//         positive: true
//       },
//     ]
//   }, [documents])

//   // Format recent documents with summary state
//   const recentDocuments = useMemo((): DocumentWithSummary[] => {
//     const formatted = documents
//       .sort((a, b) => new Date(b.upload_date).getTime() - new Date(a.upload_date).getTime())
//       .map((doc): DocumentWithSummary => ({
//         id: doc.id,
//         name: doc.original_filename,
//         type: doc.content_type?.split("/")[1]?.toUpperCase() || "FILE",
//         status: doc.processing_status === "completed" ? "Completed" :
//                 doc.processing_status === "processing" ? "Processing" : "Failed",
//         uploadedAt: formatRelativeTime(doc.upload_date),
//         confidence: doc.processing_status === "completed" ? 95 : null,
//         showSummaryOptions: false,
//         selectedModel: null,
//         currentSummary: null,
//         loadingSummary: false,
//         generatingNew: false,
//         summaryError: null
//       }))

//     setDocumentsWithSummary(formatted)
//     return formatted
//   }, [documents])

//   // Other handler functions
//   const handleChatWithDoc = (doc: DocumentWithSummary) => {
//     setSelectedDocument(doc)
//     setActiveView('chat')
//   }

//   const handleSummarizeDoc = (doc: DocumentWithSummary) => {
//     setSelectedDocumentForSummary({
//       id: doc.id,
//       name: doc.name
//     })
//     setSummaryModalOpen(true)
//   }

//   if (loading) {
//     return (
//       <div className="min-h-screen flex items-center justify-center">
//         <div className="text-center">
//           <div className="loading-spinner mx-auto"></div>
//           <p className="mt-4 text-gray-600">Loading your dashboard...</p>
//         </div>
//       </div>
//     )
//   }

//   if (error) {
//     return (
//       <div className="min-h-screen flex items-center justify-center p-6">
//         <div className="error-message max-w-md w-full">
//           <div className="flex items-center gap-3">
//             <i className="fas fa-exclamation-triangle text-2xl text-yellow-500"></i>
//             <p>{error}</p>
//           </div>
//         </div>
//       </div>
//     )
//   }

//   return (
//     <div className="main-container">
//       <div className="max-w-7xl mx-auto space-y-6">
//         {/* Stats Grid */}
//         <div className="grid grid-cols-4 gap-4">
//           {stats.map((stat) => (
//             <div key={stat.title} className="stats-card fade-in">
//               <div className="stats-header">
//                 <i className={`stats-icon ${stat.icon}`}></i>
//                 <span className={`stats-change ${stat.positive ? 'positive' : 'negative'}`}>
//                   {stat.change}
//                 </span>
//               </div>
//               <div className="stats-content">
//                 <div className="stats-value">{stat.value}</div>
//                 <div className="stats-title">{stat.title}</div>
//               </div>
//             </div>
//           ))}
//         </div>

//         {/* Search and Chat Feature */}
//         <div className="feature-container">
//           <div className="tabs-container d-flex">
//             <button
//               className={`tab-btn ${activeView === 'documents' ? 'active' : ''}`}
//               onClick={() => setActiveView('documents')}
//             >
//               <i className="fas fa-search me-2"></i>Search Documents
//             </button>
//             <button
//               className={`tab-btn ${activeView === 'chat' ? 'active' : ''}`}
//               onClick={() => setActiveView('chat')}
//             >
//               <i className="fas fa-robot me-2"></i>Ask DocuMind AI
//             </button>
//           </div>

//           <div className="tab-content-container">
//             {activeView === 'documents' && (
//               <div id="search-tab" className="tab-content active">
//                 <div className="search-input-group">
//                   <span className="search-icon"><i className="fas fa-search"></i></span>
//                   <input
//                     type="text"
//                     className="form-control"
//                     placeholder="Search across all your documents..."
//                   />
//                 </div>

//                 <div id="searchResults">
//                   <h5 className="mb-4"><i className="fas fa-history me-2"></i>Recent Documents</h5>

//                   {documentsWithSummary.length === 0 ? (
//                     <div className="text-center py-5">
//                       <i className="fas fa-file-alt" style={{fontSize: '4rem', color: '#dee2e6'}}></i>
//                       <p className="mt-3 text-muted">No documents uploaded yet.</p>
//                     </div>
//                   ) : (
//                     documentsWithSummary.map((doc) => (
//                       <div key={doc.id} className="result-item">
//                         <div className="d-flex">
//                           <div className="result-icon">
//                             <i className="fas fa-file-invoice"></i>
//                           </div>
//                           <div className="flex-grow-1">
//                             <div className="result-title">
//                               {doc.name}
//                               <span className="doc-type-tag tag-invoice">{doc.type}</span>
//                             </div>
//                             <div className="result-snippet">
//                               Financial summary for Q4 2023 showing a 12% increase in revenue compared to previous year...
//                             </div>
//                             <div className="result-meta">
//                               PDF • 2.4 MB • Last accessed: {doc.uploadedAt}
//                             </div>
//                             <div className="result-actions">
//                               <button
//                                 className="btn summarize-btn"
//                                 onClick={() => handleSummarizeDoc(doc)}
//                               >
//                                 <i className="fas fa-file-contract me-1"></i>Summarize
//                               </button>
//                               <button
//                                 className="btn chat-doc-btn"
//                                 onClick={() => handleChatWithDoc(doc)}
//                               >
//                                 <i className="fas fa-comments me-1"></i>Chat with Doc
//                               </button>
//                               <button
//                                 onClick={() => previewDocumentHandler(doc)}
//                                 className="btn btn-secondary"
//                               >
//                                 <i className="fas fa-eye me-1"></i>Preview
//                               </button>
//                             </div>
//                           </div>
//                         </div>
//                       </div>
//                     ))
//                   )}
//                 </div>
//                 <div className="chat-input-group">
//                   <input
//                     type="text"
//                     className="form-control"
//                     placeholder={selectedDocument
//                       ? `Ask about ${selectedDocument.name}...`
//                       : "Ask DocuMind AI anything about your documents..."
//                     }
//                   />
//                   <button className="btn btn-primary">
//                     <i className="fas fa-paper-plane"></i>
//                   </button>
//                 </div>
//               </div>
//             )}

//             {/* Chat Tab */}
//             {activeView === 'chat' && (
//               <div className="tab-content active">
//                 {selectedDocument && (
//                   <div className="selected-document-context">
//                     <div className="context-header">
//                       <i className="fas fa-file-alt"></i>
//                       <span>Chatting about: {selectedDocument.name}</span>
//                       <button 
//                         className="btn btn-sm btn-outline-secondary"
//                         onClick={() => setSelectedDocument(null)}
//                       >
//                         <i className="fas fa-times"></i>
//                       </button>
//                     </div>
//                   </div>
//                 )}
//                 <div className="chat-messages">
//                   <div className="message bot">
//                     <div className="message-content">
//                       {selectedDocument 
//                         ? `Hello! I'm ready to help you with "${selectedDocument.name}". What would you like to know about this document?`
//                         : "Hello! I'm DocuMind AI. I can help you analyze and understand your documents. What would you like to know?"
//                       }
//                     </div>
//                   </div>
//                   {selectedDocument && (
//                     <div className="message bot">
//                       <div className="message-content">
//                         I can see you've selected "{selectedDocument.name}". I can help you:
//                         <ul>
//                           <li>Summarize key points</li>
//                           <li>Answer specific questions about the content</li>
//                           <li>Extract important data or insights</li>
//                           <li>Compare with other documents</li>
//                         </ul>
//                         What would you like to explore?
//                       </div>
//                     </div>
//                   )}
//                 </div>
//                 <div className="chat-input-group">
//                   <input 
//                     type="text" 
//                     className="form-control" 
//                     placeholder={selectedDocument 
//                       ? `Ask about ${selectedDocument.name}...` 
//                       : "Ask DocuMind AI anything about your documents..."
//                     } 
//                   />
//                   <button className="btn btn-primary">
//                     <i className="fas fa-paper-plane"></i>
//                   </button>
//                 </div>
//               </div>
//             )}
//           </div>
//         </div>

//         {/* Document Preview Modal */}
//         {showPreview && (
//           <div style={modalStyles.overlay}>
//             <div style={modalStyles.container}>
//               <div style={modalStyles.header}>
//                 <div style={modalStyles.title}>
//                   <h3 style={modalStyles.titleH3}>{previewDocument?.name}</h3>
//                   <p style={modalStyles.titleP}>{previewDocument?.type} • {previewDocument?.uploadedAt}</p>
//                 </div>
//                 <button
//                   onClick={closePreview}
//                   style={modalStyles.closeButton}
//                 >
//                   ✕
//                 </button>
//               </div>

//               <div style={modalStyles.body}>
//                 {loadingPreview ? (
//                   <div style={modalStyles.loading}>
//                     <div style={modalStyles.loadingSpinner}></div>
//                     <p>Loading document preview...</p>
//                   </div>
//                 ) : previewUrl ? (
//                   <div style={modalStyles.viewer}>
//                     {previewDocument?.type === 'PDF' ? (
//                       <iframe
//                         src={previewUrl}
//                         style={modalStyles.iframe}
//                         title="Document Preview"
//                       />
//                     ) : previewDocument?.type?.startsWith('image/') ||
//                          ['JPG', 'JPEG', 'PNG', 'GIF'].includes(previewDocument?.type || '') ? (
//                       <div style={modalStyles.imageViewer}>
//                         <img
//                           src={previewUrl}
//                           alt="Document Preview"
//                           style={modalStyles.image}
//                         />
//                       </div>
//                     ) : (
//                       <div style={modalStyles.unsupported}>
//                         <div style={modalStyles.fileIcon}><i className="fas fa-file"></i></div>
//                         <h4 style={modalStyles.titleH3}>Preview not available</h4>
//                         <p style={modalStyles.titleP}>Preview not available for this file type</p>
//                         <a
//                           href={previewUrl}
//                           download={previewDocument?.name}
//                           style={modalStyles.downloadBtn}
//                         >
//                           <i className="fas fa-download"></i>
//                           Download Document
//                         </a>
//                       </div>
//                     )}
//                   </div>
//                 ) : (
//                   <div style={modalStyles.error}>
//                     <div style={modalStyles.errorIcon}><i className="fas fa-exclamation-triangle"></i></div>
//                     <h4 style={modalStyles.errorH4}>Failed to load document preview</h4>
//                     <p style={modalStyles.errorP}>Unable to load the document preview</p>
//                   </div>
//                 )}
//               </div>
//             </div>
//           </div>
//         )}
//       </div>

//       <style jsx>{`
//         @keyframes fadeInModal {
//           from { opacity: 0; }
//           to { opacity: 1; }
//         }

//         @keyframes slideInModal {
//           from {
//             opacity: 0;
//             transform: scale(0.95) translateY(-20px);
//           }
//           to {
//             opacity: 1;
//             transform: scale(1) translateY(0);
//           }
//         }

//         @keyframes spin {
//           0% { transform: rotate(0deg); }
//           100% { transform: rotate(360deg); }
//         }

//         @media (max-width: 768px) {
//           .modal-overlay { padding: 10px; }
//           .modal-container { width: 95vw; height: 95vh; }
//           .modal-header { padding: 16px 20px; }
//           .modal-header h3 { font-size: 1.125rem; }
//           .image-viewer { padding: 16px; }
//         }

//         ${showPreview ? 'body { overflow: hidden; }' : ''}
//       `}</style>

//       {/* Summarize Modal */}
//       {summaryModalOpen && selectedDocumentForSummary && (
//         <div 
//           style={{
//             position: 'fixed',
//             top: 0,
//             left: 0,
//             right: 0,
//             bottom: 0,
//             backgroundColor: 'rgba(0, 0, 0, 0.5)',
//             display: 'flex',
//             alignItems: 'center',
//             justifyContent: 'center',
//             zIndex: 9999
//           }}
//           onClick={() => setSummaryModalOpen(false)}
//         >
//           <div 
//             style={{
//               backgroundColor: 'white',
//               borderRadius: '8px',
//               maxWidth: '800px',
//               width: '90%',
//               maxHeight: '90vh',
//               overflow: 'auto',
//               boxShadow: '0 10px 25px rgba(0, 0, 0, 0.2)'
//             }}
//             onClick={(e) => e.stopPropagation()}
//           >
//             <div style={{ padding: '1.5rem', borderBottom: '1px solid #dee2e6', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
//               <h5 style={{ margin: 0, fontSize: '1.25rem', fontWeight: '600' }}>Document Summary</h5>
//               <button 
//                 onClick={() => setSummaryModalOpen(false)}
//                 style={{ 
//                   background: 'none',
//                   border: 'none', 
//                   fontSize: '2.2rem', 
//                   cursor: 'pointer',
//                   color: '#6c757d',
//                   display: 'flex',
//                   alignItems: 'center',
//                   justifyContent: 'center',
//                   fontWeight: 'bold',
//                   transition: 'all 0.2s ease'
//                 }}
//               >
//                 ×
//               </button>
//             </div>

//             <div style={{ padding: '1.5rem' }}>
//               <div style={{ marginBottom: '1rem' }}>
//                 <strong>Document:</strong> {selectedDocumentForSummary.name}
//               </div>

//               <div style={{ display: 'flex', alignItems: 'end', gap: '1rem', marginBottom: '1.5rem' }}>
//                 <div style={{ flex: 1 }}>
//                   <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
//                     Summarization Model:
//                   </label>
//                   <select 
//                     style={{ 
//                       width: '100%', 
//                       padding: '0.5rem', 
//                       border: '1px solid #ced4da', 
//                       borderRadius: '4px',
//                       fontSize: '1rem'
//                     }}
//                   >
//                     <option value="pegasus">Pegasus (Default - High Quality)</option>
//                     <option value="bart">BART (Balanced)</option>
//                     <option value="t5">T5 (Flexible for Technical Docs)</option>
//                   </select>
//                 </div>
//                 <button 
//                   style={{
//                     padding: '0.5rem 1rem',
//                     backgroundColor: '#007bff',
//                     color: 'white',
//                     border: 'none',
//                     borderRadius: '4px',
//                     cursor: 'pointer',
//                     display: 'flex',
//                     alignItems: 'center',
//                     gap: '0.5rem'
//                   }}
//                 >
//                   <i className="fas fa-sync-alt"></i>
//                   Regenerate
//                 </button>
//               </div>

//               <div style={{ 
//                 display: 'grid', 
//                 gridTemplateColumns: 'repeat(4, 1fr)', 
//                 gap: '1rem', 
//                 marginBottom: '1rem',
//                 padding: '1rem',
//                 backgroundColor: '#f8f9fa',
//                 borderRadius: '4px'
//               }}>
//                 <div>
//                   <small style={{ color: '#6c757d' }}>Word Count:</small><br />
//                   <span>245</span>
//                 </div>
//                 <div>
//                   <small style={{ color: '#6c757d' }}>Model:</small><br />
//                   <span>Pegasus</span>
//                 </div>
//                 <div>
//                   <small style={{ color: '#6c757d' }}>Cache:</small><br />
//                   <span style={{ 
//                     backgroundColor: '#28a745', 
//                     color: 'white', 
//                     padding: '0.25rem 0.5rem', 
//                     borderRadius: '4px', 
//                     fontSize: '0.75rem' 
//                   }}>
//                     Cached
//                   </span>
//                 </div>
//                 <div>
//                   <small style={{ color: '#6c757d' }}>Generated:</small><br />
//                   <span>Just now</span>
//                 </div>
//               </div>

//               <div style={{ 
//                 border: '1px solid #dee2e6', 
//                 borderRadius: '4px', 
//                 padding: '1rem', 
//                 backgroundColor: '#f8f9fa',
//                 marginBottom: '1rem'
//               }}>
//                 This document provides a comprehensive overview of computer vision fundamentals and applications. Key growth drivers included expansion in international markets and successful launch of new product lines. Operating expenses increased by 8%, primarily due to R&D investments. Net profit margin improved to 18.5% from 17.2% last year.
//               </div>

//               <div>
//                 <h6 style={{ marginBottom: '0.5rem' }}>Key Points:</h6>
//                 <ul style={{ paddingLeft: '1.5rem' }}>
//                   <li>Computer vision fundamentals covered comprehensively</li>
//                   <li>International market expansion drove growth</li>
//                   <li>R&D investments increased operating expenses by 8%</li>
//                   <li>Net profit margin improved from 17.2% to 18.5%</li>
//                 </ul>
//               </div>

//               <div style={{ textAlign: 'right', marginTop: '2rem' }}>
//                 <button 
//                   onClick={() => setSummaryModalOpen(false)}
//                   style={{
//                     padding: '0.75rem 2rem',
//                     backgroundColor: '#6c757d',
//                     color: 'white',
//                     border: 'none',
//                     borderRadius: '4px',
//                     cursor: 'pointer',
//                     fontSize: '1rem'
//                   }}
//                 >
//                   Close
//                 </button>
//               </div>
//             </div>
//           </div>
//         </div>
//       )}
//     </div>
//   )
// }

// export default Dashboard



//****************************CSS */
import { useState, useEffect, useMemo } from "react"
import './Dashboard.css' // Import the CSS file
import '../../styles/components.css';
//import DocumentViewer from '../DocumentViewer/DocumentViewer';

// TypeScript interfaces
interface Document {
  id: string
  original_filename: string
  content_type: string
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
    color: '#718096'
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
  }, [])

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
    setSelectedDocument(doc)
    setActiveView('chat')
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
        <div className="grid grid-cols-4 gap-4">
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
              onClick={() => setActiveView('chat')}
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
                      <i className="fas fa-file-alt" style={{fontSize: '4rem', color: '#dee2e6'}}></i>
                      <p className="mt-3 text-muted">No documents uploaded yet.</p>
                    </div>
                  ) : (
                    documentsWithSummary.map((doc) => (
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
                            <div className="result-snippet">
                              Financial summary for Q4 2023 showing a 12% increase in revenue compared to previous year...
                            </div>
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
                                onClick={() => previewDocumentHandler(doc)}
                                className="btn summarize-btn"
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
                <div className="chat-input-group">
                  <input
                    type="text"
                    className="form-control"
                    placeholder={selectedDocument
                      ? `Ask about ${selectedDocument.name}...`
                      : "Ask DocuMind AI anything about your documents..."
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
                <div className="chat-input-group">
                  <input 
                    type="text" 
                    className="form-control" 
                    placeholder={selectedDocument 
                      ? `Ask about ${selectedDocument.name}...` 
                      : "Ask DocuMind AI anything about your documents..."
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
              backgroundColor: 'white',
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
              borderBottom: '1px solid #e5e7eb', 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              background: 'linear-gradient(135deg, #f8fafc, #e2e8f0)'
            }}>
              <div>
                <h5 style={{ margin: 0, fontSize: '1.25rem', fontWeight: '600', color: '#1a202c' }}>
                  Document Summary
                </h5>
                <p style={{ margin: '4px 0 0 0', fontSize: '0.875rem', color: '#718096' }}>
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
                  color: '#718096',
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