// import React, { useState, useEffect } from 'react';
// import { apiService } from '../../services/api';

// interface SummaryModalProps {
//   isOpen: boolean;
//   onClose: () => void;
//   document: {
//     id: string;
//     name: string;
//   } | null;
// }

// interface SummaryData {
//   id: number | string;
//   summary_text: string;
//   summary_type: string;
//   word_count: number;
//   model_used: string;
//   created_at: string;
//   from_cache: boolean;
//   key_points?: string[] | null;
//   document_type?: string | null;
// }

// interface SummaryOption {
//   id: string;
//   name: string;
//   model: string;
// }

// const summaryModels = [
//   {
//     id: 'brief',
//     name: 'Brief Summary (BART)',
//     description: 'Quick overview with key points (50-150 words)',
//     model: 'bart'
//   },
//   {
//     id: 'detailed',
//     name: 'Detailed Summary (Pegasus)',
//     description: 'Comprehensive analysis with full context (80-250 words)',
//     model: 'pegasus'
//   },
//   {
//     id: 'domain_specific',
//     name: 'Domain-Specific (T5)',
//     description: 'Specialized summary based on document type (70-200 words)',
//     model: 't5'
//   }
// ];

// export function SummaryModal({ isOpen, onClose, document }: SummaryModalProps) {
//   const [selectedModel, setSelectedModel] = useState('brief');
//   const [currentSummary, setCurrentSummary] = useState<SummaryData | null>(null);
//   const [isGenerating, setIsGenerating] = useState(false);
//   const [error, setError] = useState<string | null>(null);
//   const [summaryOptions, setSummaryOptions] = useState<SummaryOption[]>([]);
//   const [documentSummaries, setDocumentSummaries] = useState<SummaryData[]>([]);

//   console.log('SummaryModal render - isOpen:', isOpen, 'document:', document);
  
//   if (!isOpen) return null;

//   // Get auth token
//   const getToken = () => {
//     return localStorage.getItem("token");
//   };

//   // Load summary options and existing summaries on mount
//   useEffect(() => {
//     if (isOpen && document) {
//       loadSummaryOptions();
//       loadExistingSummaries();
//     }
//   }, [isOpen, document]);

//   // Load available summary options from backend
//   const loadSummaryOptions = async () => {
//     try {
//       const response = await apiService.getSummaryOptions();
//       if (response.success && response.options) {
//         const options = Object.entries(response.options).map(([id, config]: [string, any]) => ({
//           id,
//           name: config.name,
//           model: config.model
//         }));
//         setSummaryOptions(options);
//       }
//     } catch (err) {
//       console.error("Error loading summary options:", err);
//       // Use default options if API fails
//       setSummaryOptions(summaryModels.map(m => ({ id: m.id, name: m.name, model: m.model })));
//     }
//   };

//   // Load existing summaries for this document
//   const loadExistingSummaries = async () => {
//     if (!document) return;
    
//     try {
//       const response = await apiService.getDocumentSummaries(document.id);
//       if (response.success && response.summaries) {
//         setDocumentSummaries(response.summaries);
        
//         // Check if we already have a summary for the selected model
//         const existingSummary = response.summaries.find(s => 
//           s.model_used === summaryModels.find(m => m.id === selectedModel)?.model
//         );
        
//         if (existingSummary) {
//           setCurrentSummary({
//             ...existingSummary,
//             summary_type: summaryModels.find(m => m.id === selectedModel)?.name || 'Summary',
//             from_cache: true
//           });
//         }
//       }
//     } catch (err) {
//       console.error("Error loading existing summaries:", err);
//     }
//   };

//   // Generate summary for selected model
//   const generateSummary = async (modelType: string) => {
//     if (!document) return;

//     setIsGenerating(true);
//     setError(null);

//     try {
//       const token = getToken();
//       if (!token) {
//         throw new Error('No authentication token found');
//       }

//       // Check if we already have a cached summary
//       const existingSummary = documentSummaries.find(s => 
//         s.model_used === summaryModels.find(m => m.id === modelType)?.model
//       );

//       if (existingSummary) {
//         console.log("Using cached summary");
//         setCurrentSummary({
//           ...existingSummary,
//           summary_type: summaryModels.find(m => m.id === modelType)?.name || 'Summary',
//           from_cache: true
//         });
//         setIsGenerating(false);
//         return;
//       }

//       // Generate new summary
//       const response = await apiService.generateSummary(document.id, modelType);
      
//       if (response.success) {
//         const newSummary: SummaryData = {
//           id: response.id || Date.now(),
//           summary_type: response.summary_type,
//           summary_text: response.summary_text,
//           word_count: response.word_count,
//           model_used: response.model_used,
//           created_at: response.created_at,
//           from_cache: response.from_cache,
//           document_type: response.document_type,
//           key_points: response.key_points
//         };
//         setCurrentSummary(newSummary);
        
//         // Add to local summaries list
//         setDocumentSummaries(prev => [...prev, newSummary]);
//       } else {
//         throw new Error("Summary generation failed");
//       }
//     } catch (err: any) {
//       console.error("Error generating summary:", err);
//       setError(err.message || 'Failed to generate summary');
//     } finally {
//       setIsGenerating(false);
//     }
//   };

//   // Handle model change
//   const handleModelChange = (modelType: string) => {
//     setSelectedModel(modelType);
    
//     // Check if we already have a summary for this model
//     const existingSummary = documentSummaries.find(s => 
//       s.model_used === summaryModels.find(m => m.id === modelType)?.model
//     );
    
//     if (existingSummary) {
//       setCurrentSummary({
//         ...existingSummary,
//         summary_type: summaryModels.find(m => m.id === modelType)?.name || 'Summary',
//         from_cache: true
//       });
//     } else {
//       // Generate new summary
//       generateSummary(modelType);
//     }
//   };

//   // Handle regenerate
//   const handleRegenerate = () => {
//     generateSummary(selectedModel);
//   };

//   return (
//     <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
//       <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden">
//         {/* Modal Header */}
//         <div className="flex items-center justify-between p-6 border-b border-gray-200">
//           <h2 className="text-xl font-semibold text-gray-900">Document Summary</h2>
//           <button
//             onClick={onClose}
//             className="text-gray-400 hover:text-gray-600 transition-colors"
//           >
//             <i className="fas fa-times text-xl"></i>
//           </button>
//         </div>

//         {/* Modal Body */}
//         <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
//           {/* Document Info */}
//           <div className="mb-4">
//             <span className="text-sm font-medium text-gray-700">Document: </span>
//             <span className="text-sm text-gray-900">{document?.name}</span>
//           </div>

//           {/* Model Selection */}
//           <div className="bg-gray-50 rounded-lg p-4 mb-6">
//             <div className="flex items-center justify-between">
//               <div className="flex-1">
//                 <label htmlFor="modelSelect" className="block text-sm font-medium text-gray-700 mb-2">
//                   Summarization Model:
//                 </label>
//                 <select
//                   id="modelSelect"
//                   value={selectedModel}
//                   onChange={(e) => handleModelChange(e.target.value)}
//                   className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
//                   disabled={isGenerating}
//                 >
//                   {summaryModels.map((model) => (
//                     <option key={model.id} value={model.id}>
//                       {model.name}
//                     </option>
//                   ))}
//                 </select>
//               </div>
//               <div className="ml-4">
//                 <button
//                   onClick={handleRegenerate}
//                   disabled={isGenerating}
//                   className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
//                 >
//                   <i className="fas fa-sync-alt mr-2"></i>
//                   {isGenerating ? 'Generating...' : 'Regenerate'}
//                 </button>
//               </div>
//             </div>
//           </div>

//           {/* Summary Content */}
//           <div className="border rounded-lg p-4 bg-gray-50">
//             {isGenerating ? (
//               <div className="flex items-center justify-center py-8">
//                 <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
//                 <span className="ml-3 text-gray-600">Generating summary using {summaryModels.find(m => m.id === selectedModel)?.name}...</span>
//               </div>
//             ) : error ? (
//               <div className="text-red-600 py-4">
//                 <i className="fas fa-exclamation-triangle mr-2"></i>
//                 {error}
//               </div>
//             ) : currentSummary ? (
//               <div>
//                 {/* Summary Metadata */}
//                 <div className="flex items-center gap-4 text-xs text-gray-500 mb-3">
//                   <span>Model: {currentSummary.model_used}</span>
//                   <span>Words: {currentSummary.word_count}</span>
//                   <span>Type: {currentSummary.summary_type}</span>
//                   {currentSummary.from_cache && (
//                     <span className="bg-green-100 text-green-800 px-2 py-1 rounded">
//                       <i className="fas fa-check-circle mr-1"></i>Cached
//                     </span>
//                   )}
//                   {currentSummary.document_type && (
//                     <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
//                       <i className="fas fa-tag mr-1"></i>{currentSummary.document_type}
//                     </span>
//                   )}
//                 </div>

//                 {/* Summary Text */}
//                 <div className="prose max-w-none">
//                   <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
//                     {currentSummary.summary_text}
//                   </p>
//                 </div>

//                 {/* Key Points */}
//                 {currentSummary.key_points && currentSummary.key_points.length > 0 && (
//                   <div className="mt-4 p-3 bg-blue-50 rounded-md">
//                     <h4 className="text-sm font-medium text-blue-900 mb-2">
//                       <i className="fas fa-key mr-1"></i>Key Points:
//                     </h4>
//                     <ul className="text-sm text-blue-800 space-y-1">
//                       {currentSummary.key_points.map((point, index) => (
//                         <li key={index} className="flex items-start">
//                           <i className="fas fa-chevron-right text-blue-600 mr-2 mt-1 text-xs"></i>
//                           {point}
//                         </li>
//                       ))}
//                     </ul>
//                   </div>
//                 )}
//               </div>
//             ) : (
//               <div className="text-gray-500 py-4">
//                 No summary available. Select a model to generate one.
//               </div>
//             )}
//           </div>

//           {/* Existing Summaries */}
//           {documentSummaries.length > 0 && (
//             <div className="mt-6">
//               <h4 className="text-sm font-medium text-gray-700 mb-3">
//                 <i className="fas fa-history mr-2"></i>Available Summaries:
//               </h4>
//               <div className="space-y-2">
//                 {documentSummaries.map((summary, index) => (
//                   <div key={index} className="flex items-center justify-between p-2 bg-white border rounded">
//                     <div className="flex items-center gap-2">
//                       <span className="text-xs bg-gray-100 px-2 py-1 rounded">
//                         {summary.model_used}
//                       </span>
//                       <span className="text-xs text-gray-500">
//                         {summary.word_count} words
//                       </span>
//                     </div>
//                     <button
//                       onClick={() => setCurrentSummary({
//                         ...summary,
//                         summary_type: summaryModels.find(m => m.model === summary.model_used)?.name || 'Summary',
//                         from_cache: true
//                       })}
//                       className="text-xs text-blue-600 hover:text-blue-800"
//                     >
//                       View
//                     </button>
//                   </div>
//                 ))}
//               </div>
//             </div>
//           )}
//         </div>

//         {/* Modal Footer */}
//         <div className="flex items-center justify-end p-6 border-t border-gray-200">
//           <button
//             onClick={onClose}
//             className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
//           >
//             Close
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// }
