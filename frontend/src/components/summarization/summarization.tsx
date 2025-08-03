

//****************************************Backend Intergrated

// "use client"

// import { useState, useEffect } from "react"

// const models = [
//   {
//     id: "bart",
//     name: "BART",
//     description: "Excellent for detailed summaries (Currently Available)",
//     icon: "🎯",
//     strengths: ["Detailed summaries", "Technical content", "High accuracy"],
//     available: true
//   },
//   {
//     id: "pegasus",
//     name: "Pegasus",
//     description: "Best for news articles and general content (Coming Soon)",
//     icon: "⚡",
//     strengths: ["News articles", "General content", "Fast processing"],
//     available: false
//   },
//   {
//     id: "t5",
//     name: "T5",
//     description: "Great for academic and research papers (Coming Soon)",
//     icon: "📚",
//     strengths: ["Academic papers", "Research content", "Complex documents"],
//     available: false
//   },
// ]

// type GeneratedSummary = {
//   summary_text: string
//   key_points?: string[]
//   document_name?: string
//   model_used?: string
//   created_at?: string
//   word_count?: number
//   summary_type?: string
// }

// export default function Summarization() {
//   const [documents, setDocuments] = useState<any[]>([])
//   const [selectedDocument, setSelectedDocument] = useState("")
//   const [selectedModel, setSelectedModel] = useState("bart")
//   const [summaryType, setSummaryType] = useState("brief")
//   const [summaryLength, setSummaryLength] = useState(150)
//   const [isGenerating, setIsGenerating] = useState(false)
//   const [generatedSummary, setGeneratedSummary] = useState<GeneratedSummary | null>(null)
//   const [error, setError] = useState("")
//   const [progress, setProgress] = useState("")

//   // Fetch documents from backend on component mount
//   useEffect(() => {
//     fetchDocuments()
//   }, [])

//   const fetchDocuments = async () => {
//   try {
//     const token = localStorage.getItem('token');
//     console.log('Token from localStorage:', token ? 'Present' : 'Missing'); // Debug log
    
//     if (!token) {
//       setError('No authentication token found. Please log in again.');
//       // Redirect to login page or show login modal
//       return;
//     }

//     const response = await fetch('http://localhost:8000/api/documents/', {
//       headers: {
//         'Authorization': `Bearer ${token}`,
//         'Content-Type': 'application/json'
//       }
//     });
    
//     console.log('Response status:', response.status); // Debug log
    
//     if (response.status === 401) {
//       // Token is invalid or expired
//       localStorage.removeItem('token');
//       localStorage.removeItem('user');
//       setError('Session expired. Please log in again.');
//       // Redirect to login page
//       return;
//     }
    
//     if (response.ok) {
//       const data = await response.json();
//       setDocuments(data.documents || []);
//       setError(''); // Clear any previous errors
//     } else {
//       const errorData = await response.json();
//       setError(errorData.detail || 'Failed to fetch documents');
//     }
//   } catch (error) {
//     console.error('Error fetching documents:', error);
//     setError('Network error while fetching documents');
//   }
// };

//   const handleGenerateSummary = async () => {
//   if (!selectedDocument) {
//     setError("Please select a document first");
//     return;
//   }

//   setIsGenerating(true);
//   setError("");
//   setProgress("Initializing summarization...");
//   setGeneratedSummary(null);

//   try {
//     const response = await fetch("http://localhost:8000/api/summarize", {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//         Authorization: `Bearer ${localStorage.getItem("token")}`,
//       },
//       body: JSON.stringify({
//         document_id: selectedDocument,
//         model_name: selectedModel,
//         summary_type: summaryType,
//         summary_length: summaryLength,
//       }),
//     });

//     const data = await response.json();

//     if (response.ok && data.success) {
//       setProgress("Summary generated successfully!");
//       setGeneratedSummary({
//         ...data,
//         document_name: data.document_name || "Unknown Document",
//         model_used: data.model_used || selectedModel,
//         created_at: data.created_at || new Date().toISOString(),
//         word_count: data.word_count || 0,
//         summary_type: data.summary_type || summaryType,
//       });
//     } else {
//       setError(data.detail || "Failed to generate summary");
//     }
//   } catch (error) {
//     console.error("Error generating summary:", error);
//     setError("Network error occurred while generating summary");
//   } finally {
//     setIsGenerating(false);
//     setProgress("");
//   }
// };

//   const handleCopy = async () => {
//     if (generatedSummary?.summary_text) {
//       try {
//         await navigator.clipboard.writeText(generatedSummary.summary_text)
//         // You could add a toast notification here
//         console.log('Summary copied to clipboard')
//       } catch (error) {
//         console.error('Failed to copy:', error)
//       }
//     }
//   }

//   const handleExport = () => {
//     if (generatedSummary) {
//       const content = `Document: ${generatedSummary.document_name}\nModel: ${generatedSummary.model_used}\nType: ${generatedSummary.summary_type}\nGenerated: ${new Date(generatedSummary.created_at ?? Date.now()).toLocaleString()}\n\nSummary:\n${generatedSummary.summary_text}\n\nKey Points:\n${generatedSummary.key_points?.join('\n- ') || 'None'}`
      
//       const blob = new Blob([content], { type: 'text/plain' })
//       const url = URL.createObjectURL(blob)
//       const a = document.createElement('a')
//       a.href = url
//       a.download = `summary-${generatedSummary.document_name}.txt`
//       document.body.appendChild(a)
//       a.click()
//       document.body.removeChild(a)
//       URL.revokeObjectURL(url)
//     }
//   }

//   const selectedModelData = models.find((m) => m.id === selectedModel)
//   const selectedDocumentData = documents.find((d) => d.id === selectedDocument)

//   return (
//     <div className="p-6 space-y-6">
//       <div className="mb-6">
//         <h1 className="text-3xl font-bold text-gray-900 mb-2">Document Summarization</h1>
//         <p className="text-gray-600">Generate intelligent summaries using advanced AI models</p>
//       </div>

//       {error && (
//         <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
//           <div className="flex items-center">
//             <span className="text-red-600 mr-2">❌</span>
//             <span className="text-red-800">{error}</span>
//           </div>
//         </div>
//       )}

//       {progress && (
//         <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
//           <div className="flex items-center">
//             <span className="text-blue-600 mr-2">ℹ️</span>
//             <span className="text-blue-800">{progress}</span>
//           </div>
//         </div>
//       )}

//       <div className="grid grid-cols-3 gap-6">
//         {/* Configuration Panel */}
//         <div className="space-y-6">
//           {/* Document Selection */}
//           <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
//             <div className="p-4 border-b border-gray-200">
//               <h2 className="text-lg font-semibold flex items-center gap-2">📄 Select Document</h2>
//             </div>
//             <div className="p-4">
//               <select
//                 className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
//                 value={selectedDocument}
//                 onChange={(e) => setSelectedDocument(e.target.value)}
//               >
//                 <option value="">Choose a document</option>
//                 {documents.map((doc) => (
//                   <option key={doc.id} value={doc.id}>
//                     {doc.original_filename || doc.name} 
//                     {doc.document_type && ` (${doc.document_type})`}
//                     {doc.page_count && ` • ${doc.page_count} pages`}
//                   </option>
//                 ))}
//               </select>
              
//               {selectedDocumentData && (
//                 <div className="mt-3 p-3 bg-gray-50 rounded-md text-sm">
//                   <div className="flex justify-between">
//                     <span className="font-medium">File:</span>
//                     <span>{selectedDocumentData.original_filename}</span>
//                   </div>
//                   {selectedDocumentData.document_type && (
//                     <div className="flex justify-between">
//                       <span className="font-medium">Type:</span>
//                       <span>{selectedDocumentData.document_type}</span>
//                     </div>
//                   )}
//                   {selectedDocumentData.page_count && (
//                     <div className="flex justify-between">
//                       <span className="font-medium">Pages:</span>
//                       <span>{selectedDocumentData.page_count}</span>
//                     </div>
//                   )}
//                 </div>
//               )}
//             </div>
//           </div>

//           {/* Model Selection */}
//           <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
//             <div className="p-4 border-b border-gray-200">
//               <h2 className="text-lg font-semibold flex items-center gap-2">🧠 AI Model</h2>
//               <p className="text-sm text-gray-600 mt-1">Choose the best model for your content type</p>
//             </div>
//             <div className="p-4">
//               <div className="space-y-4">
//                 {models.map((model) => (
//                   <div key={model.id} className={`flex items-start gap-3 ${!model.available ? 'opacity-50' : ''}`}>
//                     <input
//                       type="radio"
//                       id={model.id}
//                       name="model"
//                       value={model.id}
//                       checked={selectedModel === model.id}
//                       onChange={(e) => setSelectedModel(e.target.value)}
//                       disabled={!model.available}
//                       className="mt-1"
//                     />
//                     <div className="flex-1">
//                       <label htmlFor={model.id} className={`cursor-pointer ${!model.available ? 'cursor-not-allowed' : ''}`}>
//                         <div className="flex items-center gap-2 mb-1">
//                           <span className="text-lg">{model.icon}</span>
//                           <span className="font-medium">{model.name}</span>
//                           {!model.available && <span className="text-xs bg-gray-200 px-2 py-1 rounded">Coming Soon</span>}
//                         </div>
//                         <p className="text-sm text-gray-600 mb-2">{model.description}</p>
//                         <div className="flex flex-wrap gap-1">
//                           {model.strengths.map((strength) => (
//                             <span key={strength} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
//                               {strength}
//                             </span>
//                           ))}
//                         </div>
//                       </label>
//                     </div>
//                   </div>
//                 ))}
//               </div>
//             </div>
//           </div>

//           {/* Summary Options */}
//           <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
//             <div className="p-4 border-b border-gray-200">
//               <h2 className="text-lg font-semibold flex items-center gap-2">⚙️ Summary Options</h2>
//             </div>
//             <div className="p-4 space-y-4">
//               <div>
//                 <label className="block text-sm font-medium text-gray-700 mb-2">Summary Type</label>
//                 <div className="space-y-2">
//                   {[
//                     { id: "brief", name: "Brief", desc: "Quick overview" },
//                     { id: "detailed", name: "Detailed", desc: "Comprehensive summary" },
//                     { id: "Key Points", name: "Key Points", desc: "Main conclusions only" },
//                     { id: "Executive Summary", name: "Executive Summary", desc: "Great for business/professional contexts" },
//                     //{ id: "business", name: "Business", desc: "Business implications" }
//                   ].map((type) => (
//                     <div key={type.id} className="flex items-center gap-2">
//                       <input
//                         type="radio"
//                         id={type.id}
//                         name="summaryType"
//                         value={type.id}
//                         checked={summaryType === type.id}
//                         onChange={(e) => setSummaryType(e.target.value)}
//                       />
//                       <label htmlFor={type.id} className="text-sm">
//                         <span className="font-medium">{type.name}</span>
//                         <span className="text-gray-500 ml-1">- {type.desc}</span>
//                       </label>
//                     </div>
//                   ))}
//                 </div>
//               </div>

//               <div>
//                 <label className="block text-sm font-medium text-gray-700 mb-2">
//                   Summary Length: {summaryLength} words
//                 </label>
//                 <input
//                   type="range"
//                   min="50"
//                   max="500"
//                   step="25"
//                   value={summaryLength}
//                   onChange={(e) => setSummaryLength(Number(e.target.value))}
//                   className="w-full"
//                 />
//                 <div className="flex justify-between text-xs text-gray-500 mt-1">
//                   <span>50</span>
//                   <span>500</span>
//                 </div>
//               </div>

//               <button
//                 onClick={handleGenerateSummary}
//                 disabled={!selectedDocument || isGenerating || !selectedModelData?.available}
//                 className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
//               >
//                 {isGenerating ? (
//                   <>
//                     <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
//                     Generating...
//                   </>
//                 ) : (
//                   <>✨ Generate Summary</>
//                 )}
//               </button>
//             </div>
//           </div>
//         </div>

//         {/* Results Panel */}
//         <div style={{ gridColumn: "span 2" }}>
//           <div className="bg-white rounded-lg border border-gray-200 shadow-sm h-full">
//             <div className="p-4 border-b border-gray-200">
//               <div className="flex items-center justify-between">
//                 <div>
//                   <h2 className="text-lg font-semibold flex items-center gap-2">✨ Generated Summary</h2>
//                   {selectedModelData && generatedSummary && (
//                     <p className="text-sm text-gray-600 flex items-center gap-2 mt-1">
//                       <span>{selectedModelData.icon}</span>
//                       Generated using {generatedSummary.model_used} model
//                     </p>
//                   )}
//                 </div>
//                 {generatedSummary && (
//                   <div className="flex gap-2">
//                     <button 
//                       onClick={handleCopy}
//                       className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
//                     >
//                       📋 Copy
//                     </button>
//                     <button 
//                       onClick={handleExport}
//                       className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
//                     >
//                       💾 Export
//                     </button>
//                   </div>
//                 )}
//               </div>
//             </div>
//             <div className="p-4">
//               {generatedSummary ? (
//                 <div className="space-y-4">
//                   <div className="p-4 bg-gray-50 rounded-lg border">
//                     <textarea
//                       value={generatedSummary.summary_text}
//                       readOnly
//                       className="w-full bg-transparent border-0 resize-none focus:outline-none"
//                       style={{ minHeight: "300px" }}
//                     />
//                   </div>
                  
//                   {generatedSummary.key_points && generatedSummary.key_points.length > 0 && (
//                     <div className="p-4 bg-blue-50 rounded-lg">
//                       <h4 className="font-medium text-blue-900 mb-2">Key Points:</h4>
//                       <ul className="text-sm text-blue-800 space-y-1">
//                         {generatedSummary.key_points.map((point, index) => (
//                           <li key={index} className="flex items-start gap-2">
//                             <span className="text-blue-600">•</span>
//                             <span>{point}</span>
//                           </li>
//                         ))}
//                       </ul>
//                     </div>
//                   )}
                  
//                   <div className="flex items-center gap-4 text-sm text-gray-500">
//                     <span>Word count: {generatedSummary.word_count}</span>
//                     <span>•</span>
//                     <span>Model: {generatedSummary.model_used}</span>
//                     <span>•</span>
//                     <span>Type: {generatedSummary.summary_type}</span>
//                     <span>•</span>
//                     <span>Generated: {new Date(generatedSummary.created_at ?? "").toLocaleString()}</span>
//                   </div>
//                 </div>
//               ) : (
//                 <div className="flex flex-col items-center justify-center text-center" style={{ height: "400px" }}>
//                   <div className="text-6xl mb-4">🧠</div>
//                   <h3 className="text-lg font-medium text-gray-600 mb-2">No summary generated yet</h3>
//                   <p className="text-sm text-gray-500 max-w-md">
//                     Select a document and configure your preferences, then click "Generate Summary" to create an
//                     AI-powered summary using your backend processing system.
//                   </p>
//                 </div>
//               )}
//             </div>
//           </div>
//         </div>
//       </div>
//     </div>
//   )
// }



// "use client"

// import { useState, useEffect } from "react"

// const models = [
//   {
//     id: "bart",
//     name: "BART",
//     description: "Excellent for detailed summaries (Currently Available)",
//     icon: "🎯",
//     strengths: ["Detailed summaries", "Technical content", "High accuracy"],
//     available: true
//   },
//   {
//     id: "pegasus",
//     name: "Pegasus",
//     description: "Best for news articles and general content (Coming Soon)",
//     icon: "⚡",
//     strengths: ["News articles", "General content", "Fast processing"],
//     available: false
//   },
//   {
//     id: "t5",
//     name: "T5",
//     description: "Great for academic and research papers (Coming Soon)",
//     icon: "📚",
//     strengths: ["Academic papers", "Research content", "Complex documents"],
//     available: false
//   },
// ]

// type GeneratedSummary = {
//   summary_text: string
//   key_points?: string[]
//   document_name?: string
//   model_used?: string
//   created_at?: string
//   word_count?: number
//   summary_type?: string
// }

// export default function Summarization() {
//   const [documents, setDocuments] = useState<any[]>([])
//   const [selectedDocument, setSelectedDocument] = useState("")
//   const [selectedModel, setSelectedModel] = useState("bart")
//   const [summaryType, setSummaryType] = useState("1") // Changed to match backend options
//   const [summaryLength, setSummaryLength] = useState(150)
//   const [isGenerating, setIsGenerating] = useState(false)
//   const [generatedSummary, setGeneratedSummary] = useState<GeneratedSummary | null>(null)
//   const [error, setError] = useState("")
//   const [progress, setProgress] = useState("")

//   // Updated summary type options to match backend
//   const summaryOptions = [
//     { id: "1", name: "Brief Summary", desc: "Quick overview (30-100 words)", icon: "📋" },
//     { id: "2", name: "Detailed Summary", desc: "Comprehensive summary (80-250 words)", icon: "📖" },
//     { id: "3", name: "Key Points", desc: "Important points as bullets", icon: "🔑" },
//     { id: "4", name: "Executive Summary", desc: "Professional business format (60-180 words)", icon: "💼" }
//   ]

//   // Fetch documents from backend on component mount
//   useEffect(() => {
//     fetchDocuments()
//   }, [])

//   const fetchDocuments = async () => {
//     try {
//       const token = localStorage.getItem('token');
//       console.log('Token from localStorage:', token ? 'Present' : 'Missing');
      
//       if (!token) {
//         setError('No authentication token found. Please log in again.');
//         return;
//       }

//       const response = await fetch('http://localhost:8000/api/documents/', {
//         headers: {
//           'Authorization': `Bearer ${token}`,
//           'Content-Type': 'application/json'
//         }
//       });
      
//       console.log('Response status:', response.status);
      
//       if (response.status === 401) {
//         localStorage.removeItem('token');
//         localStorage.removeItem('user');
//         setError('Session expired. Please log in again.');
//         return;
//       }
      
//       if (response.ok) {
//         const data = await response.json();
//         setDocuments(data.documents || []);
//         setError('');
//       } else {
//         const errorData = await response.json();
//         setError(errorData.detail || 'Failed to fetch documents');
//       }
//     } catch (error) {
//       console.error('Error fetching documents:', error);
//       setError('Network error while fetching documents');
//     }
//   };

//   const handleGenerateSummary = async () => {
//     if (!selectedDocument) {
//       setError("Please select a document first");
//       return;
//     }

//     setIsGenerating(true);
//     setError("");
//     setProgress("Initializing summarization...");
//     setGeneratedSummary(null);

//     try {
//       const response = await fetch("http://localhost:8000/api/summarize", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//           Authorization: `Bearer ${localStorage.getItem("token")}`,
//         },
//         body: JSON.stringify({
//           document_id: selectedDocument,
//           model_name: selectedModel,
//           summary_type: summaryType, // Now sends "1", "2", "3", or "4"
//           summary_length: summaryLength,
//         }),
//       });

//       const data = await response.json();

//       if (response.ok && data.success) {
//         setProgress("Summary generated successfully!");
//         setGeneratedSummary({
//           ...data,
//           document_name: data.document_name || "Unknown Document",
//           model_used: data.model_used || selectedModel,
//           created_at: data.created_at || new Date().toISOString(),
//           word_count: data.word_count || 0,
//           summary_type: data.summary_type || getSummaryTypeName(summaryType),
//         });
//       } else {
//         setError(data.detail || "Failed to generate summary");
//       }
//     } catch (error) {
//       console.error("Error generating summary:", error);
//       setError("Network error occurred while generating summary");
//     } finally {
//       setIsGenerating(false);
//       setProgress("");
//     }
//   };

//   const getSummaryTypeName = (typeId: string) => {
//     const option = summaryOptions.find(opt => opt.id === typeId);
//     return option ? option.name : "Unknown";
//   };

//   const handleCopy = async () => {
//     if (generatedSummary?.summary_text) {
//       try {
//         await navigator.clipboard.writeText(generatedSummary.summary_text)
//         console.log('Summary copied to clipboard')
//       } catch (error) {
//         console.error('Failed to copy:', error)
//       }
//     }
//   }

//   const handleExport = () => {
//     if (generatedSummary) {
//       const content = `Document: ${generatedSummary.document_name}\nModel: ${generatedSummary.model_used}\nType: ${generatedSummary.summary_type}\nGenerated: ${new Date(generatedSummary.created_at ?? Date.now()).toLocaleString()}\n\nSummary:\n${generatedSummary.summary_text}\n\nKey Points:\n${generatedSummary.key_points?.join('\n- ') || 'None'}`
      
//       const blob = new Blob([content], { type: 'text/plain' })
//       const url = URL.createObjectURL(blob)
//       const a = document.createElement('a')
//       a.href = url
//       a.download = `summary-${generatedSummary.document_name}.txt`
//       document.body.appendChild(a)
//       a.click()
//       document.body.removeChild(a)
//       URL.revokeObjectURL(url)
//     }
//   }

//   const selectedModelData = models.find((m) => m.id === selectedModel)
//   const selectedDocumentData = documents.find((d) => d.id === selectedDocument)
//   const selectedSummaryOption = summaryOptions.find(opt => opt.id === summaryType)

//   return (
//     <div className="p-6 space-y-6">
//       <div className="mb-6">
//         <h1 className="text-3xl font-bold text-gray-900 mb-2">Document Summarization</h1>
//         <p className="text-gray-600">Generate intelligent summaries with professional formatting</p>
//       </div>

//       {error && (
//         <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
//           <div className="flex items-center">
//             <span className="text-red-600 mr-2">❌</span>
//             <span className="text-red-800">{error}</span>
//           </div>
//         </div>
//       )}

//       {progress && (
//         <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
//           <div className="flex items-center">
//             <span className="text-blue-600 mr-2">ℹ️</span>
//             <span className="text-blue-800">{progress}</span>
//           </div>
//         </div>
//       )}

//       <div className="grid grid-cols-3 gap-6">
//         {/* Configuration Panel */}
//         <div className="space-y-6">
//           {/* Document Selection */}
//           <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
//             <div className="p-4 border-b border-gray-200">
//               <h2 className="text-lg font-semibold flex items-center gap-2">📄 Select Document</h2>
//             </div>
//             <div className="p-4">
//               <select
//                 className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
//                 value={selectedDocument}
//                 onChange={(e) => setSelectedDocument(e.target.value)}
//               >
//                 <option value="">Choose a document</option>
//                 {documents.map((doc) => (
//                   <option key={doc.id} value={doc.id}>
//                     {doc.original_filename || doc.name} 
//                     {doc.document_type && ` (${doc.document_type})`}
//                     {doc.page_count && ` • ${doc.page_count} pages`}
//                   </option>
//                 ))}
//               </select>
              
//               {selectedDocumentData && (
//                 <div className="mt-3 p-3 bg-gray-50 rounded-md text-sm">
//                   <div className="flex justify-between">
//                     <span className="font-medium">File:</span>
//                     <span>{selectedDocumentData.original_filename}</span>
//                   </div>
//                   {selectedDocumentData.document_type && (
//                     <div className="flex justify-between">
//                       <span className="font-medium">Type:</span>
//                       <span>{selectedDocumentData.document_type}</span>
//                     </div>
//                   )}
//                   {selectedDocumentData.page_count && (
//                     <div className="flex justify-between">
//                       <span className="font-medium">Pages:</span>
//                       <span>{selectedDocumentData.page_count}</span>
//                     </div>
//                   )}
//                 </div>
//               )}
//             </div>
//           </div>

//           {/* Model Selection */}
//           <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
//             <div className="p-4 border-b border-gray-200">
//               <h2 className="text-lg font-semibold flex items-center gap-2">🧠 AI Model</h2>
//               <p className="text-sm text-gray-600 mt-1">Currently using BART for all summary types</p>
//             </div>
//             <div className="p-4">
//               <div className="space-y-4">
//                 {models.map((model) => (
//                   <div key={model.id} className={`flex items-start gap-3 ${!model.available ? 'opacity-50' : ''}`}>
//                     <input
//                       type="radio"
//                       id={model.id}
//                       name="model"
//                       value={model.id}
//                       checked={selectedModel === model.id}
//                       onChange={(e) => setSelectedModel(e.target.value)}
//                       disabled={!model.available}
//                       className="mt-1"
//                     />
//                     <div className="flex-1">
//                       <label htmlFor={model.id} className={`cursor-pointer ${!model.available ? 'cursor-not-allowed' : ''}`}>
//                         <div className="flex items-center gap-2 mb-1">
//                           <span className="text-lg">{model.icon}</span>
//                           <span className="font-medium">{model.name}</span>
//                           {!model.available && <span className="text-xs bg-gray-200 px-2 py-1 rounded">Coming Soon</span>}
//                         </div>
//                         <p className="text-sm text-gray-600 mb-2">{model.description}</p>
//                         <div className="flex flex-wrap gap-1">
//                           {model.strengths.map((strength) => (
//                             <span key={strength} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
//                               {strength}
//                             </span>
//                           ))}
//                         </div>
//                       </label>
//                     </div>
//                   </div>
//                 ))}
//               </div>
//             </div>
//           </div>

//           {/* Summary Options */}
//           <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
//             <div className="p-4 border-b border-gray-200">
//               <h2 className="text-lg font-semibold flex items-center gap-2">⚙️ Summary Options</h2>
//               <p className="text-sm text-gray-600 mt-1">Each type has unique formatting and focus</p>
//             </div>
//             <div className="p-4 space-y-4">
//               <div>
//                 <label className="block text-sm font-medium text-gray-700 mb-3">Summary Type</label>
//                 <div className="space-y-3">
//                   {summaryOptions.map((option) => (
//                     <div key={option.id} className="flex items-start gap-3">
//                       <input
//                         type="radio"
//                         id={option.id}
//                         name="summaryType"
//                         value={option.id}
//                         checked={summaryType === option.id}
//                         onChange={(e) => setSummaryType(e.target.value)}
//                         className="mt-1"
//                       />
//                       <label htmlFor={option.id} className="flex-1 cursor-pointer">
//                         <div className="flex items-center gap-2 mb-1">
//                           <span className="text-lg">{option.icon}</span>
//                           <span className="font-medium text-sm">{option.name}</span>
//                         </div>
//                         <p className="text-xs text-gray-500 ml-6">{option.desc}</p>
//                       </label>
//                     </div>
//                   ))}
//                 </div>
//               </div>

//               {/* Remove summary length slider for Key Points since it uses extraction */}
//               {summaryType !== "3" && (
//                 <div>
//                   <label className="block text-sm font-medium text-gray-700 mb-2">
//                     Summary Length: {summaryLength} words
//                   </label>
//                   <input
//                     type="range"
//                     min="50"
//                     max="300"
//                     step="25"
//                     value={summaryLength}
//                     onChange={(e) => setSummaryLength(Number(e.target.value))}
//                     className="w-full"
//                   />
//                   <div className="flex justify-between text-xs text-gray-500 mt-1">
//                     <span>50</span>
//                     <span>300</span>
//                   </div>
//                 </div>
//               )}

//               <button
//                 onClick={handleGenerateSummary}
//                 disabled={!selectedDocument || isGenerating || !selectedModelData?.available}
//                 className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
//               >
//                 {isGenerating ? (
//                   <>
//                     <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
//                     Generating...
//                   </>
//                 ) : (
//                   <>
//                     {selectedSummaryOption?.icon} Generate {selectedSummaryOption?.name}
//                   </>
//                 )}
//               </button>
//             </div>
//           </div>
//         </div>

//         {/* Results Panel */}
//         <div style={{ gridColumn: "span 2" }}>
//           <div className="bg-white rounded-lg border border-gray-200 shadow-sm h-full">
//             <div className="p-4 border-b border-gray-200">
//               <div className="flex items-center justify-between">
//                 <div>
//                   <h2 className="text-lg font-semibold flex items-center gap-2">✨ Generated Summary</h2>
//                   {selectedModelData && generatedSummary && (
//                     <p className="text-sm text-gray-600 flex items-center gap-2 mt-1">
//                       <span>{selectedModelData.icon}</span>
//                       Generated using {generatedSummary.model_used} model • {generatedSummary.summary_type}
//                     </p>
//                   )}
//                 </div>
//                 {generatedSummary && (
//                   <div className="flex gap-2">
//                     <button 
//                       onClick={handleCopy}
//                       className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
//                     >
//                       📋 Copy
//                     </button>
//                     <button 
//                       onClick={handleExport}
//                       className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
//                     >
//                       💾 Export
//                     </button>
//                   </div>
//                 )}
//               </div>
//             </div>
//             <div className="p-4">
//               {generatedSummary ? (
//                 <div className="space-y-4">
//                   <div className="p-4 bg-gray-50 rounded-lg border">
//                     <pre 
//                       className="whitespace-pre-wrap font-sans text-sm leading-relaxed"
//                       style={{ fontFamily: "inherit" }}
//                     >
//                       {generatedSummary.summary_text}
//                     </pre>
//                   </div>
                  
//                   {generatedSummary.key_points && generatedSummary.key_points.length > 0 && (
//                     <div className="p-4 bg-blue-50 rounded-lg">
//                       <h4 className="font-medium text-blue-900 mb-2">Additional Key Points:</h4>
//                       <ul className="text-sm text-blue-800 space-y-1">
//                         {generatedSummary.key_points.map((point, index) => (
//                           <li key={index} className="flex items-start gap-2">
//                             <span className="text-blue-600">•</span>
//                             <span>{point}</span>
//                           </li>
//                         ))}
//                       </ul>
//                     </div>
//                   )}
                  
//                   <div className="flex items-center gap-4 text-sm text-gray-500">
//                     <span>Word count: {generatedSummary.word_count || 'N/A'}</span>
//                     <span>•</span>
//                     <span>Model: {generatedSummary.model_used}</span>
//                     <span>•</span>
//                     <span>Type: {generatedSummary.summary_type}</span>
//                     <span>•</span>
//                     <span>Generated: {new Date(generatedSummary.created_at ?? "").toLocaleString()}</span>
//                   </div>
//                 </div>
//               ) : (
//                 <div className="flex flex-col items-center justify-center text-center" style={{ height: "400px" }}>
//                   <div className="text-6xl mb-4">🎯</div>
//                   <h3 className="text-lg font-medium text-gray-600 mb-2">Ready to generate professional summaries</h3>
//                   <p className="text-sm text-gray-500 max-w-md">
//                     Choose your document and summary type. Each type has unique formatting - from brief overviews 
//                     to detailed analysis with professional headers and structured content.
//                   </p>
//                 </div>
//               )}
//             </div>
//           </div>
//         </div>
//       </div>
//     </div>
//   )
// }


"use client"

import { useState, useEffect } from "react"

const models = [
  {
    id: "bart",
    name: "BART",
    description: "Excellent for detailed summaries (Currently Available)",
    icon: "🎯",
    strengths: ["Detailed summaries", "Technical content", "High accuracy"],
    available: true
  },
  {
    id: "pegasus",
    name: "Pegasus",
    description: "Best for news articles and general content (Coming Soon)",
    icon: "⚡",
    strengths: ["News articles", "General content", "Fast processing"],
    available: false
  },
  {
    id: "t5",
    name: "T5",
    description: "Great for academic and research papers (Coming Soon)",
    icon: "📚",
    strengths: ["Academic papers", "Research content", "Complex documents"],
    available: false
  },
]

type GeneratedSummary = {
  summary_text: string
  key_points?: string[]
  document_name?: string
  model_used?: string
  created_at?: string
  word_count?: number
  summary_type?: string
}

export default function Summarization() {
  const [documents, setDocuments] = useState<any[]>([])
  const [selectedDocument, setSelectedDocument] = useState("")
  const [selectedModel, setSelectedModel] = useState("bart")
  const [summaryType, setSummaryType] = useState("1")
  const [summaryLength, setSummaryLength] = useState(150)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedSummary, setGeneratedSummary] = useState<GeneratedSummary | null>(null)
  const [error, setError] = useState("")
  const [progress, setProgress] = useState("")

  const summaryOptions = [
    { id: "1", name: "Brief Summary", desc: "Quick overview (30-100 words)", icon: "📋" },
    { id: "2", name: "Detailed Summary", desc: "Comprehensive summary (80-250 words)", icon: "📖" },
    { id: "3", name: "Key Points", desc: "Important points as bullets", icon: "🔑" },
    { id: "4", name: "Executive Summary", desc: "Professional business format (60-180 words)", icon: "💼" }
  ]

  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    try {
      const token = localStorage.getItem('token');
      console.log('Token from localStorage:', token ? 'Present' : 'Missing');
      
      if (!token) {
        setError('No authentication token found. Please log in again.');
        return;
      }

      const response = await fetch('http://localhost:8000/api/documents/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      console.log('Response status:', response.status);
      
      if (response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setError('Session expired. Please log in again.');
        return;
      }
      
      if (response.ok) {
        const data = await response.json();
        setDocuments(data.documents || []);
        setError('');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to fetch documents');
      }
    } catch (error) {
      console.error('Error fetching documents:', error);
      setError('Network error while fetching documents');
    }
  };

  const handleGenerateSummary = async () => {
    if (!selectedDocument) {
      setError("Please select a document first");
      return;
    }

    setIsGenerating(true);
    setError("");
    setProgress("Initializing summarization...");
    setGeneratedSummary(null);

    try {
      const response = await fetch("http://localhost:8000/api/summarize", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({
          document_id: selectedDocument,
          model_name: selectedModel,
          summary_type: summaryType,
          summary_length: summaryLength,
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setProgress("Summary generated successfully!");
        setGeneratedSummary({
          ...data,
          document_name: data.document_name || "Unknown Document",
          model_used: data.model_used || selectedModel,
          created_at: data.created_at || new Date().toISOString(),
          word_count: data.word_count || 0,
          summary_type: data.summary_type || getSummaryTypeName(summaryType),
        });
      } else {
        setError(data.detail || "Failed to generate summary");
      }
    } catch (error) {
      console.error("Error generating summary:", error);
      setError("Network error occurred while generating summary");
    } finally {
      setIsGenerating(false);
      setProgress("");
    }
  };

  const getSummaryTypeName = (typeId: string) => {
    const option = summaryOptions.find(opt => opt.id === typeId);
    return option ? option.name : "Unknown";
  };

  const [copySuccess, setCopySuccess] = useState(false)

  const handleCopy = async () => {
    if (generatedSummary?.summary_text) {
      try {
        await navigator.clipboard.writeText(generatedSummary.summary_text)
        setCopySuccess(true)
        setTimeout(() => setCopySuccess(false), 2000) // Reset after 2 seconds
        console.log('Summary copied to clipboard')
      } catch (error) {
        console.error('Failed to copy:', error)
        // Fallback for older browsers
        const textArea = document.createElement('textarea')
        textArea.value = generatedSummary.summary_text
        document.body.appendChild(textArea)
        textArea.select()
        document.execCommand('copy')
        document.body.removeChild(textArea)
        setCopySuccess(true)
        setTimeout(() => setCopySuccess(false), 2000)
      }
    }
  }

  const handleExport = () => {
    if (generatedSummary) {
      const content = `Document: ${generatedSummary.document_name}\nModel: ${generatedSummary.model_used}\nType: ${generatedSummary.summary_type}\nGenerated: ${new Date(generatedSummary.created_at ?? Date.now()).toLocaleString()}\n\nSummary:\n${generatedSummary.summary_text}\n\nKey Points:\n${generatedSummary.key_points?.join('\n- ') || 'None'}`
      
      const blob = new Blob([content], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `summary-${generatedSummary.document_name}.txt`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }
  }

  const selectedModelData = models.find((m) => m.id === selectedModel)
  const selectedDocumentData = documents.find((d) => d.id === selectedDocument)
  const selectedSummaryOption = summaryOptions.find(opt => opt.id === summaryType)

  // Animated loading component
  const LoadingAnimation = () => (
    <div className="flex flex-col items-center justify-center h-96 space-y-6">
      <div className="relative">
        <div className="w-20 h-20 border-4 border-blue-200 rounded-full animate-spin"></div>
        <div className="absolute top-0 left-0 w-20 h-20 border-4 border-blue-600 rounded-full animate-spin border-t-transparent"></div>
      </div>
      <div className="text-center space-y-3">
        <h3 className="text-xl font-semibold text-gray-800">Generating Summary...</h3>
        <p className="text-gray-600 max-w-md text-base">{progress}</p>
        <div className="flex space-x-1 justify-center">
          <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
          <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
        </div>
      </div>
    </div>
  )

  return (
    <div className="p-8 space-y-8 bg-gray-50 min-h-screen font-sans">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-3">Document Summarization</h1>
        <p className="text-lg text-gray-600">Generate intelligent summaries with professional formatting</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-300 rounded-xl p-5 mb-6 shadow-sm">
          <div className="flex items-center">
            <span className="text-red-600 mr-3 text-xl">❌</span>
            <span className="text-red-800 text-base font-medium">{error}</span>
          </div>
        </div>
      )}

      {progress && !isGenerating && (
        <div className="bg-blue-50 border border-blue-300 rounded-xl p-5 mb-6 shadow-sm">
          <div className="flex items-center">
            <span className="text-blue-600 mr-3 text-xl">ℹ️</span>
            <span className="text-blue-800 text-base font-medium">{progress}</span>
          </div>
        </div>
      )}

      <div className="grid grid-cols-3 gap-8">
        {/* Configuration Panel */}
        <div className="space-y-8">
          {/* Document Selection */}
          <div className="bg-white rounded-xl border border-gray-300 shadow-lg">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold flex items-center gap-3">📄 Select Document</h2>
            </div>
            <div className="p-6">
              <select
                className="w-full p-4 border-2 border-gray-300 rounded-lg focus:ring-3 focus:ring-blue-500 focus:border-blue-500 text-base font-medium bg-white transition-all duration-200 hover:border-gray-400"
                value={selectedDocument}
                onChange={(e) => setSelectedDocument(e.target.value)}
              >
                <option value="" className="text-base">Choose a document</option>
                {documents.map((doc) => (
                  <option key={doc.id} value={doc.id} className="text-base">
                    {doc.original_filename || doc.name} 
                    {doc.document_type && ` (${doc.document_type})`}
                    {doc.page_count && ` • ${doc.page_count} pages`}
                  </option>
                ))}
              </select>
              
              {selectedDocumentData && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="font-semibold text-gray-700">File:</span>
                      <span className="font-medium text-gray-900">{selectedDocumentData.original_filename}</span>
                    </div>
                    {selectedDocumentData.document_type && (
                      <div className="flex justify-between">
                        <span className="font-semibold text-gray-700">Type:</span>
                        <span className="font-medium text-gray-900">{selectedDocumentData.document_type}</span>
                      </div>
                    )}
                    {selectedDocumentData.page_count && (
                      <div className="flex justify-between">
                        <span className="font-semibold text-gray-700">Pages:</span>
                        <span className="font-medium text-gray-900">{selectedDocumentData.page_count}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Model Selection */}
          <div className="bg-white rounded-xl border border-gray-300 shadow-lg">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold flex items-center gap-3">🧠 AI Model</h2>
              <p className="text-base text-gray-600 mt-2">Currently using BART for all summary types</p>
            </div>
            <div className="p-6">
              <div className="space-y-5">
                {models.map((model) => (
                  <div key={model.id} className={`flex items-start gap-4 ${!model.available ? 'opacity-50' : ''}`}>
                    <input
                      type="radio"
                      id={model.id}
                      name="model"
                      value={model.id}
                      checked={selectedModel === model.id}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      disabled={!model.available}
                      className="mt-1 w-4 h-4 text-blue-600"
                    />
                    <div className="flex-1">
                      <label htmlFor={model.id} className={`cursor-pointer ${!model.available ? 'cursor-not-allowed' : ''}`}>
                        <div className="flex items-center gap-3 mb-2">
                          <span className="text-2xl">{model.icon}</span>
                          <span className="font-bold text-lg">{model.name}</span>
                          {!model.available && <span className="text-xs bg-gray-200 px-3 py-1 rounded-full font-medium">Coming Soon</span>}
                        </div>
                        <p className="text-base text-gray-600 mb-3">{model.description}</p>
                        <div className="flex flex-wrap gap-2">
                          {model.strengths.map((strength) => (
                            <span key={strength} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                              {strength}
                            </span>
                          ))}
                        </div>
                      </label>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Summary Options */}
          <div className="bg-white rounded-xl border border-gray-300 shadow-lg">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold flex items-center gap-3">⚙️ Summary Options</h2>
              <p className="text-base text-gray-600 mt-2">Each type has unique formatting and focus</p>
            </div>
            <div className="p-6 space-y-6">
              <div>
                <label className="block text-base font-bold text-gray-800 mb-4">Summary Type</label>
                <div className="space-y-4">
                  {summaryOptions.map((option) => (
                    <div key={option.id} className="flex items-start gap-4">
                      <input
                        type="radio"
                        id={option.id}
                        name="summaryType"
                        value={option.id}
                        checked={summaryType === option.id}
                        onChange={(e) => setSummaryType(e.target.value)}
                        className="mt-1 w-4 h-4 text-blue-600"
                      />
                      <label htmlFor={option.id} className="flex-1 cursor-pointer">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="text-xl">{option.icon}</span>
                          <span className="font-bold text-base">{option.name}</span>
                        </div>
                        <p className="text-sm text-gray-600 ml-7">{option.desc}</p>
                      </label>
                    </div>
                  ))}
                </div>
              </div>

              {summaryType !== "3" && (
                <div>
                  <label className="block text-base font-bold text-gray-800 mb-3">
                    Summary Length: {summaryLength} words
                  </label>
                  <input
                    type="range"
                    min="50"
                    max="300"
                    step="25"
                    value={summaryLength}
                    onChange={(e) => setSummaryLength(Number(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                  />
                  <div className="flex justify-between text-sm text-gray-500 mt-2 font-medium">
                    <span>50</span>
                    <span>300</span>
                  </div>
                </div>
              )}

              <button
                onClick={handleGenerateSummary}
                disabled={!selectedDocument || isGenerating || !selectedModelData?.available}
                className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-4 px-6 rounded-xl hover:from-blue-700 hover:to-blue-800 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed flex items-center justify-center gap-3 text-lg font-bold transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
              >
                {isGenerating ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    Generating...
                  </>
                ) : (
                  <>
                    {selectedSummaryOption?.icon} Generate {selectedSummaryOption?.name}
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Results Panel */}
        <div style={{ gridColumn: "span 2" }}>
          <div className="bg-white rounded-xl border border-gray-300 shadow-lg h-full">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold flex items-center gap-3">✨ Generated Summary</h2>
                  {selectedModelData && generatedSummary && (
                    <p className="text-base text-gray-600 flex items-center gap-3 mt-2">
                      <span>{selectedModelData.icon}</span>
                      Generated using {generatedSummary.model_used} model • {generatedSummary.summary_type}
                    </p>
                  )}
                </div>
                {generatedSummary && (
                  <div className="flex gap-3">
                    <button 
                      onClick={handleCopy}
                      className={`px-6 py-3 text-base font-bold rounded-xl transition-all duration-300 shadow-md hover:shadow-lg transform hover:-translate-y-0.5 ${
                        copySuccess 
                          ? 'bg-green-500 text-white border-2 border-green-500' 
                          : 'bg-blue-50 text-blue-700 border-2 border-blue-300 hover:bg-blue-100 hover:border-blue-400'
                      }`}
                    >
                      {copySuccess ? '✅ Copied!' : '📋 Copy Text'}
                    </button>
                    <button 
                      onClick={handleExport}
                      className="px-6 py-3 text-base font-bold bg-purple-50 text-purple-700 border-2 border-purple-300 rounded-xl hover:bg-purple-100 hover:border-purple-400 transition-all duration-300 shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
                    >
                      💾 Export File
                    </button>
                  </div>
                )}
              </div>
            </div>
            
            <div className="p-6">
              {isGenerating ? (
                <LoadingAnimation />
              ) : generatedSummary ? (
                <div className="space-y-6">
                  <div className="p-6 bg-gray-50 rounded-xl border-2 border-gray-200 shadow-sm">
                    <div 
                      className="text-lg leading-relaxed font-medium text-gray-800"
                      style={{ 
                        fontFamily: "ui-serif, Georgia, Cambria, Times New Roman, Times, serif",
                        lineHeight: "1.7"
                      }}
                    >
                      {generatedSummary.summary_text.split('\n').map((paragraph, index) => (
                        <p key={index} className="mb-4 last:mb-0">
                          {paragraph}
                        </p>
                      ))}
                    </div>
                  </div>
                  
                  {generatedSummary.key_points && generatedSummary.key_points.length > 0 && (
                    <div className="p-6 bg-blue-50 rounded-xl border-2 border-blue-200">
                      <h4 className="font-bold text-lg text-blue-900 mb-4">Additional Key Points:</h4>
                      <ul className="text-base text-blue-800 space-y-2">
                        {generatedSummary.key_points.map((point, index) => (
                          <li key={index} className="flex items-start gap-3">
                            <span className="text-blue-600 font-bold">•</span>
                            <span className="font-medium leading-relaxed">{point}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  <div className="flex items-center gap-6 text-base text-gray-500 font-medium">
                    <span>Word count: {generatedSummary.word_count || 'N/A'}</span>
                    <span>•</span>
                    <span>Model: {generatedSummary.model_used}</span>
                    <span>•</span>
                    <span>Type: {generatedSummary.summary_type}</span>
                    <span>•</span>
                    <span>Generated: {new Date(generatedSummary.created_at ?? "").toLocaleString()}</span>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center text-center h-96">
                  <div className="text-8xl mb-6">🎯</div>
                  <h3 className="text-2xl font-bold text-gray-700 mb-4">Ready to generate professional summaries</h3>
                  <p className="text-lg text-gray-600 max-w-2xl leading-relaxed">
                    Choose your document and summary type. Each type has unique formatting - from brief overviews 
                    to detailed analysis with professional headers and structured content.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      
      <style jsx>{`
        .slider::-webkit-slider-thumb {
          appearance: none;
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #3B82F6;
          cursor: pointer;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .slider::-moz-range-thumb {
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #3B82F6;
          cursor: pointer;
          border: none;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
      `}</style>
    </div>
  )
}