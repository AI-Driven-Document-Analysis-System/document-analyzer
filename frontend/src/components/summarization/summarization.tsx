

"use client"

import { useState, useEffect } from "react"

// Type definition for the summary response from the backend API
// This ensures type safety when handling API responses
type GeneratedSummary = {
  summary_text: string
  document_name?: string
  model_used?: string
  created_at?: string
  word_count?: number
  summary_type?: string
}

export default function Summarization() {
  // State management for the component
  // documents: stores the list of available documents fetched from API
  const [documents, setDocuments] = useState<any[]>([])
  
  // selectedDocument: tracks which document ID is currently selected for summarization
  const [selectedDocument, setSelectedDocument] = useState("")
  
  // summaryType: determines which AI model/approach to use (brief, detailed, domain_specific)
  const [summaryType, setSummaryType] = useState("brief")
  
  // summaryLength: allows user to control the desired word count of the summary
  const [summaryLength, setSummaryLength] = useState(150)
  
  // isGenerating: boolean flag to show loading state during API calls
  const [isGenerating, setIsGenerating] = useState(false)
  
  // generatedSummary: stores the complete summary response from the API
  const [generatedSummary, setGeneratedSummary] = useState<GeneratedSummary | null>(null)
  
  // error: displays error messages to the user when operations fail
  const [error, setError] = useState("")
  
  // progress: shows status messages during the summary generation process
  const [progress, setProgress] = useState("")

  // Configuration object defining the three AI summary options
  // Each option uses a different model with specific characteristics
  const summaryOptions = [
    { 
      id: "brief", 
      name: "Brief Summary", 
      desc: "Quick overview using BART model", 
      icon: "📋",
      model: "BART" // BART is good for concise, factual summaries
    },
    { 
      id: "detailed", 
      name: "Detailed Summary", 
      desc: "Comprehensive analysis using Pegasus model", 
      icon: "📖",
      model: "Pegasus" // Pegasus excels at longer, more detailed summaries
    },
    { 
      id: "domain_specific", 
      name: "Domain Specific", 
      desc: "Specialized summary using T5 model", 
      icon: "🎯",
      model: "Domain Specific Model" // T5 can be fine-tuned for specific domains/contexts
    }
  ];

  // useEffect hook to fetch documents when component mounts
  // Empty dependency array means this runs only once on initial render
  useEffect(() => {
    fetchDocuments()
  }, [])

  // Function to retrieve the user's uploaded documents from the backend
  const fetchDocuments = async () => {
    try {
      // Get JWT token from localStorage for authenticated requests
      // This token proves the user is logged in and authorized
      const token = localStorage.getItem('token');
      
      // If no token exists, user needs to log in again
      if (!token) {
        setError('No authentication token found. Please log in again.');
        return;
      }

      // Make authenticated API call to get user's documents
      const response = await fetch('http://localhost:8000/api/documents/', {
        headers: {
          'Authorization': `Bearer ${token}`, // JWT authentication
          'Content-Type': 'application/json'
        }
      });
      
      // Handle expired or invalid tokens (401 Unauthorized)
      if (response.status === 401) {
        // Clear invalid credentials and prompt re-login
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setError('Session expired. Please log in again.');
        return;
      }
      
      // Process successful response
      if (response.ok) {
        const data = await response.json();
        // Update state with fetched documents, fallback to empty array if none
        setDocuments(data.documents || []);
        setError(''); // Clear any previous errors
      } else {
        // Handle other HTTP errors (400, 500, etc.)
        const errorData = await response.json();
        const errorMessage = typeof errorData.detail === 'string' 
          ? errorData.detail 
          : errorData.message || 'Failed to fetch documents';
        setError(errorMessage);
      }
    } catch (error) {
      // Handle network errors, CORS issues, or other fetch failures
      console.error('Error fetching documents:', error);
      setError('Network error while fetching documents');
    }
  };

  // Main function to generate AI summary of selected document
  const handleGenerateSummary = async () => {
    // Validation: ensure user has selected a document
    if (!selectedDocument) {
      setError("Please select a document first");
      return;
    }

    // Set loading state and clear previous results
    setIsGenerating(true);
    setError("");
    setProgress("AI is generating summary...");
    setGeneratedSummary(null);

    try {
      // Get authentication token for API request
      const token = localStorage.getItem("token");
      
      // Prepare request payload matching backend API expectations
      const requestBody = {
        document_id: selectedDocument, // Which document to summarize
        summary_type: summaryType, // Which AI model/approach to use
        summary_length: summaryLength // Desired word count
      };

      // Log for debugging purposes
      console.log("Request body:", requestBody);

      // Make POST request to summarization endpoint
      const response = await fetch("http://localhost:8000/api/summarize/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`, // JWT authentication
        },
        body: JSON.stringify(requestBody),
      });

      console.log("Response status:", response.status);

      const data = await response.json();
      console.log("Response data:", data);

      // Process successful response
      if (response.ok && data.success) {
        setProgress("Summary generated successfully!");
        
        // Create complete summary object with fallback values
        // This ensures the UI has all necessary data even if some fields are missing
        setGeneratedSummary({
          ...data, // Spread all response data
          document_name: data.document_name || "Unknown Document",
          model_used: data.model_used || "AI Selected",
          created_at: data.created_at || new Date().toISOString(),
          word_count: data.word_count || 0,
          summary_type: data.summary_type || getSummaryTypeName(summaryType),
        });
      } else {
        // Handle API errors with detailed error messaging
        let errorMessage = `Request failed (${response.status})`;
        
        // Special handling for validation errors (422 Unprocessable Entity)
        if (response.status === 422) {
          if (data.detail) {
            if (Array.isArray(data.detail)) {
              // Parse validation error array from FastAPI/Pydantic
              const validationErrors = data.detail.map(err => {
                const field = err.loc ? err.loc.join('.') : 'unknown';
                const message = err.msg || 'validation error';
                return `${field}: ${message}`;
              }).join(', ');
              errorMessage = `Validation error: ${validationErrors}`;
            } else {
              errorMessage = `Validation error: ${data.detail}`;
            }
          }
        } else if (data.detail) {
          // Handle other error types
          errorMessage = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
        }

        console.error("API Error:", errorMessage);
        setError(errorMessage);
      }
    } catch (error) {
      // Handle network errors, timeout, or other fetch failures
      console.error("Network error:", error);
      setError(`Network error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      // Always reset loading state regardless of success/failure
      setIsGenerating(false);
      setProgress("");
    }
  };

  // Helper function to get human-readable summary type name from ID
  const getSummaryTypeName = (typeId: string) => {
    const option = summaryOptions.find(opt => opt.id === typeId);
    return option ? option.name : "Unknown";
  };

  // State for copy-to-clipboard functionality
  const [copySuccess, setCopySuccess] = useState(false)

  // Function to copy summary text to user's clipboard
  const handleCopy = async () => {
    if (generatedSummary?.summary_text) {
      try {
        // Modern clipboard API (preferred method)
        await navigator.clipboard.writeText(generatedSummary.summary_text)
        setCopySuccess(true)
        setTimeout(() => setCopySuccess(false), 2000) // Reset after 2 seconds
      } catch (error) {
        // Fallback for older browsers or when clipboard API fails
        const textArea = document.createElement('textarea')
        textArea.value = generatedSummary.summary_text
        document.body.appendChild(textArea)
        textArea.select()
        document.execCommand('copy') // Deprecated but still works as fallback
        document.body.removeChild(textArea)
        setCopySuccess(true)
        setTimeout(() => setCopySuccess(false), 2000)
      }
    }
  }

  // Function to export summary as a downloadable text file
  const handleExport = () => {
    if (generatedSummary) {
      // Create formatted text content with metadata
      const content = `Document: ${generatedSummary.document_name}\nModel: ${generatedSummary.model_used}\nType: ${generatedSummary.summary_type}\nGenerated: ${new Date(generatedSummary.created_at ?? Date.now()).toLocaleString()}\n\nSummary:\n${generatedSummary.summary_text}`
      
      // Create downloadable file using Blob API
      const blob = new Blob([content], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      
      // Programmatically trigger download
      const a = document.createElement('a')
      a.href = url
      a.download = `summary-${generatedSummary.document_name}.txt`
      document.body.appendChild(a)
      a.click() // Simulate click to start download
      document.body.removeChild(a)
      URL.revokeObjectURL(url) // Clean up memory
    }
  }

  // Helper to get selected document data for display
  const selectedDocumentData = documents.find((d) => d.id === selectedDocument)
  
  // Helper to get selected summary option for UI display
  const selectedSummaryOption = summaryOptions.find(opt => opt.id === summaryType)

  // Loading animation component shown during AI processing
  // Separated into its own component for better organization and reusability
  const LoadingAnimation = () => (
    <div className="flex flex-col items-center justify-center h-96 space-y-6">
      {/* Dual-ring spinner animation */}
      <div className="relative">
        <div className="w-20 h-20 border-4 border-blue-200 rounded-full animate-spin"></div>
        <div className="absolute top-0 left-0 w-20 h-20 border-4 border-blue-600 rounded-full animate-spin border-t-transparent"></div>
      </div>
      
      {/* Status text and bouncing dots */}
      <div className="text-center space-y-3">
        <h3 className="text-xl font-semibold text-gray-800">AI is Working...</h3>
        <p className="text-gray-600 max-w-md text-base">{progress}</p>
        {/* Three bouncing dots with staggered animation delays */}
        <div className="flex space-x-1 justify-center">
          <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
          <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
        </div>
      </div>
    </div>
  )

  // Main component render
  return (
    <div className="p-8 space-y-8 bg-gray-50 min-h-screen font-sans">
      {/* Page header with title and description */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-3">AI-Powered Document Summarization</h1>
        <p className="text-lg text-gray-600">Choose from BART, Pegasus, or T5 models for different summary types</p>
      </div>

      {/* Error message display - only shows when error state exists */}
      {error && (
        <div className="bg-red-50 border border-red-300 rounded-xl p-5 mb-6 shadow-sm">
          <div className="flex items-center">
            <span className="text-red-600 mr-3 text-xl">❌</span>
            <span className="text-red-800 text-base font-medium">{error}</span>
          </div>
        </div>
      )}

      {/* Success/info message display - shows when progress exists but not generating */}
      {progress && !isGenerating && (
        <div className="bg-blue-50 border border-blue-300 rounded-xl p-5 mb-6 shadow-sm">
          <div className="flex items-center">
            <span className="text-blue-600 mr-3 text-xl">ℹ️</span>
            <span className="text-blue-800 text-base font-medium">{progress}</span>
          </div>
        </div>
      )}

      {/* Main layout: 3-column grid with configuration panel (1 col) and results panel (2 cols) */}
      <div className="grid grid-cols-3 gap-8">
        
        {/* Left side: Configuration Panel */}
        <div className="space-y-8">
          
          {/* Document Selection Section */}
          <div className="bg-white rounded-xl border border-gray-300 shadow-lg">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold flex items-center gap-3">📄 Select Document</h2>
            </div>
            <div className="p-6">
              {/* Dropdown to select from available documents */}
              <select
                className="w-full p-4 border-2 border-gray-300 rounded-lg focus:ring-3 focus:ring-blue-500 focus:border-blue-500 text-base font-medium bg-white transition-all duration-200 hover:border-gray-400"
                value={selectedDocument}
                onChange={(e) => setSelectedDocument(e.target.value)}
              >
                <option value="" className="text-base">Choose a document</option>
                {/* Map through available documents to create options */}
                {documents.map((doc) => (
                  <option key={doc.id} value={doc.id} className="text-base">
                    {/* Show filename, type, and page count if available */}
                    {doc.original_filename || doc.name} 
                    {doc.document_type && ` (${doc.document_type})`}
                    {doc.page_count && ` • ${doc.page_count} pages`}
                  </option>
                ))}
              </select>
              
              {/* Document details display - only shows when document is selected */}
              {selectedDocumentData && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <div className="space-y-2 text-sm">
                    {/* Display document metadata */}
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

          {/* AI Summary Options Section */}
          <div className="bg-white rounded-xl border border-gray-300 shadow-lg">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold flex items-center gap-3">🤖 AI Summary Options</h2>
            </div>
            <div className="p-6 space-y-6">
              
              {/* Summary Type Selection - Radio buttons for different AI models */}
              <div>
                <label className="block text-base font-bold text-gray-800 mb-4">Summary Type</label>
                <div className="space-y-4">
                  {/* Map through summary options to create radio buttons */}
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
                        {/* Option header with icon and name */}
                        <div className="flex items-center gap-3 mb-2">
                          <span className="text-xl">{option.icon}</span>
                          <span className="font-bold text-base">{option.name}</span>
                        </div>
                        {/* Option description and model info */}
                        <p className="text-sm text-gray-600 ml-7 mb-1">{option.desc}</p>
                        <p className="text-xs text-blue-600 ml-7 font-medium">🧠 Model: {option.model}</p>
                      </label>
                    </div>
                  ))}
                </div>
              </div>

              {/* Summary Length Slider */}
              <div>
                {/* <label className="block text-base font-bold text-gray-800 mb-3">
                  Summary Length: {summaryLength} words
                </label> */}
                {/* Range slider for word count selection */}
                {/* <input
                  type="range"
                  min="50"
                  max="300"
                  step="25" // 25-word increments
                  value={summaryLength}
                  onChange={(e) => setSummaryLength(Number(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                /> */}
                {/* Min/max value indicators */}
                {/* <div className="flex justify-between text-sm text-gray-500 mt-2 font-medium">
                  <span>50</span>
                  <span>300</span>
                </div> */}
              </div>

              {/* Generate Summary Button */}
              <button
                onClick={handleGenerateSummary}
                disabled={!selectedDocument || isGenerating} // Disable if no document selected or already generating
                className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-4 px-6 rounded-xl hover:from-blue-700 hover:to-blue-800 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed flex items-center justify-center gap-3 text-lg font-bold transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
              >
                {/* Dynamic button content based on state */}
                {isGenerating ? (
                  <>
                    {/* Spinner animation during generation */}
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    AI Processing...
                  </>
                ) : (
                  <>
                    {/* Show selected option icon and name */}
                    {selectedSummaryOption?.icon} Generate {selectedSummaryOption?.name}
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Right side: Results Panel - spans 2 columns */}
        <div style={{ gridColumn: "span 2" }}>
          <div className="bg-white rounded-xl border border-gray-300 shadow-lg h-full">
            
            {/* Results panel header */}
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold flex items-center gap-3">✨ AI Generated Summary</h2>
                  {/* Show generation metadata when summary exists */}
                  {generatedSummary && (
                    <p className="text-base text-gray-600 flex items-center gap-3 mt-2">
                      <span>🤖</span>
                      Generated using {generatedSummary.model_used} • {generatedSummary.summary_type}
                    </p>
                  )}
                </div>
                
                {/* Action buttons - only show when summary exists */}
                {generatedSummary && (
                  <div className="flex gap-3">
                    {/* Copy to clipboard button */}
                    <button 
                      onClick={handleCopy}
                      className={`px-6 py-3 text-base font-bold rounded-xl transition-all duration-300 shadow-md hover:shadow-lg transform hover:-translate-y-0.5 ${
                        copySuccess 
                          ? 'bg-green-500 text-white border-2 border-green-500'  // Success state
                          : 'bg-blue-50 text-blue-700 border-2 border-blue-300 hover:bg-blue-100 hover:border-blue-400' // Default state
                      }`}
                    >
                      {copySuccess ? '✅ Copied!' : '📋 Copy Text'}
                    </button>
                    
                    {/* Export to file button */}
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
            
            {/* Results content area */}
            <div className="p-6">
              {/* Conditional rendering based on current state */}
              {isGenerating ? (
                // Show loading animation while generating
                <LoadingAnimation />
              ) : generatedSummary ? (
                // Show generated summary and metadata
                <div className="space-y-6">
                  {/* Summary text display */}
                  <div className="p-6 bg-gray-50 rounded-xl border-2 border-gray-200 shadow-sm">
                    <div 
                      className="text-lg leading-relaxed font-medium text-gray-800"
                      style={{ 
                        // Use serif font for better readability of longer text
                        fontFamily: "ui-serif, Georgia, Cambria, Times New Roman, Times, serif",
                        lineHeight: "1.7"
                      }}
                    >
                      {/* Split text into paragraphs for better formatting */}
                      {generatedSummary.summary_text.split('\n').map((paragraph, index) => (
                        <p key={index} className="mb-4 last:mb-0">
                          {paragraph}
                        </p>
                      ))}
                    </div>
                  </div>
                  
                  {/* Summary metadata display */}
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
                // Show welcome/instructions when no summary exists
                <div className="flex flex-col items-center justify-center text-center h-96">
                  <div className="text-8xl mb-6">🤖</div>
                  <h3 className="text-2xl font-bold text-gray-700 mb-4">AI Ready to Generate Summaries</h3>
                  <p className="text-lg text-gray-600 max-w-2xl leading-relaxed">
                    Select your document and summary type. Choose from BART for brief summaries, 
                    Pegasus for detailed analysis, or T5 for domain-specific content.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      
      {/* Custom CSS for slider styling - needed because Tailwind doesn't include slider thumb styles */}
      <style jsx>{`
        /* Webkit browsers (Chrome, Safari, Edge) */
        .slider::-webkit-slider-thumb {
          appearance: none;
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #3B82F6; /* Blue-600 */
          cursor: pointer;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        /* Firefox */
        .slider::-moz-range-thumb {
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #3B82F6; /* Blue-600 */
          cursor: pointer;
          border: none;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
      `}</style>
    </div>
  )
}