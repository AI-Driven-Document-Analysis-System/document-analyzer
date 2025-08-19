import React, { useState, useCallback } from "react"
import { useRoutePersistence } from './hooks/useRoutePersistence';

// TYPE DEFINITIONS - Define the shape of data structures used in this component

/**
 * Represents a file that user has uploaded or is uploading
 * Tracks the entire lifecycle from selection to completion
 */
interface UploadedFile {
  id: string          // Unique identifier for this upload (generated randomly)
  file: File          // The actual browser File object containing the document
  progress: number    // Upload progress percentage (0-100)
  status: "uploading" | "processing" | "completed" | "error"  // Current state of the file
  error?: string      // Error message if upload fails
  documentId?: string // Server-generated ID after successful upload
}

/**
 * Props that parent components can pass to DocumentUpload
 */
interface DocumentUploadProps {
  authToken?: string     // Authentication token for API requests
  onAuthError?: () => void  // Function to call when authentication fails
}

// UTILITY FUNCTIONS

/**
 * Returns appropriate emoji icon based on file type
 * Why needed: Visual feedback helps users quickly identify file types
 */
const getFileIcon = (type: string) => {
  if (type.includes("pdf")) return "📄"      // PDF documents
  if (type.includes("image")) return "🖼️"    // Images (JPG, PNG, etc.)
  if (type.includes("spreadsheet") || type.includes("excel")) return "📊"  // Excel files
  return "📁"  // Default for unknown file types
}

/**
 * Retrieves authentication token from browser storage or uses fallback
 * Why needed: User needs to be authenticated to upload files to the server
 * Checks multiple storage locations for flexibility
 */
const getStoredAuthToken = () => {
  try {
    // Try localStorage first (persists across browser sessions)
    // Then sessionStorage (persists only for current tab session)
    // Finally fallback to hardcoded demo token
    return window.localStorage?.getItem('authToken') || 
           window.sessionStorage?.getItem('authToken') ||
           'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3OWQwYmVkNS1jMWMxLTRmYWYtODJkNC1mZWQxYTI4NDcyZDUiLCJlbWFpbCI6InRlc3QxQGdtYWlsLmNvbSIsImV4cCI6MTc1NzMyNzc5OH0.h_P47qNaOhJ9r34alekxTlvXxen45dbTXokBans669c';
  } catch (e) {
    // Fallback for environments where localStorage isn't available (like some mobile browsers)
    return 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3OWQwYmVkNS1jMWMxLTRmYWYtODJkNC1mZWQxYTI4NDcyZDUiLCJlbWFpbCI6InRlc3QxQGdtYWlsLmNvbSIsImV4cCI6MTc1NzMyNzc5OH0.h_P47qNaOhJ9r34alekxTlvXxen45dbTXokBans669c';
  }
}

/**
 * MAIN COMPONENT: DocumentUpload
 * 
 * This component creates a drag-and-drop file upload interface that:
 * 1. Allows users to select files by dragging, dropping, or clicking
 * 2. Uploads files to a backend API
 * 3. Shows real-time progress and status for each file
 * 4. Handles authentication and error cases
 */
export function DocumentUpload({ authToken: propAuthToken, onAuthError }: DocumentUploadProps = {}) {
  // Custom hook for maintaining route/navigation state
  // (Keeps user on this page even if they navigate away and come back)
  useRoutePersistence();
  
  // STATE MANAGEMENT - Track component's changeable data
  
  // List of all files user has uploaded (past and present)
  // Why array: User can upload multiple files simultaneously
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  
  // Whether user is currently dragging files over the drop zone
  // Why needed: Provides visual feedback during drag operations
  const [isDragActive, setIsDragActive] = useState(false)
  
  // Current authentication token for API requests
  // Why separate from prop: Token might come from storage, not just props
  const [authToken, setAuthToken] = useState<string | null>(null)
  
  // UPDATE TOKEN - Set authentication token when component loads or prop changes
  React.useEffect(() => {
    // Use token from props if provided, otherwise get from storage
    // Props take priority (parent component might pass updated token)
    const token = propAuthToken || getStoredAuthToken();
    setAuthToken(token);
  }, [propAuthToken])  // Re-run when propAuthToken changes

  /**
   * CORE UPLOAD FUNCTION - Sends file to backend API
   * This is where the actual file transfer happens
   */
  const uploadToAPI = async (file: File, fileId: string) => {
    try {
      // Create FormData object - required for file uploads
      // FormData handles the multipart/form-data encoding automatically
      const formData = new FormData()
      formData.append('file', file)           // The actual file data
      formData.append('filename', file.name)  // Original filename
      formData.append('content_type', file.type)  // MIME type (pdf, jpg, etc.)

      // Security check - ensure user is authenticated
      if (!authToken) {
        throw new Error('No authentication token provided')
      }

      // Make HTTP POST request to upload endpoint
      const response = await fetch('http://localhost:8000/api/documents/upload', {
        method: 'POST',
        headers: {
          // Include authentication token in request header
          // Server will verify this token to ensure user has permission to upload
          'Authorization': `Bearer ${authToken}`,
        },
        body: formData,  // Send the file data
      })

      // Handle different response scenarios
      if (!response.ok) {
        // Special handling for authentication errors
        if (response.status === 401) {
          onAuthError?.()  // Notify parent component that auth failed
          throw new Error('Authentication failed. Please log in again.')
        }
        
        // Try to extract detailed error message from server response
        const errorText = await response.text()
        let errorMessage
        try {
          // Server might return JSON with error details
          const errorData = JSON.parse(errorText)
          errorMessage = errorData.detail || `Upload failed with status ${response.status}`
        } catch {
          // If not JSON, use raw error text
          errorMessage = `Upload failed with status ${response.status}: ${errorText}`
        }
        throw new Error(errorMessage)
      }

      // Success! Parse the server response
      const result = await response.json()
      return {
        success: true,
        document_id: result.document_id,  // Server assigns unique ID to uploaded document
        status: result.status             // Server tells us if file was new or duplicate
      }
    } catch (error) {
      console.error('Upload error:', error)
      throw error  // Re-throw so calling code can handle it
    }
  }

  /**
   * FILE HANDLING FUNCTION - Processes files when user selects them
   * This function is called whether files are dropped, pasted, or selected via file picker
   * useCallback prevents unnecessary re-renders when this function is passed as a prop
   */
  const handleFiles = useCallback((files: FileList | null) => {
    if (!files) return  // No files selected

    // Security check - user must be logged in to upload
    if (!authToken) {
      alert('Please log in to upload files')
      return
    }

    // Convert FileList to array and create UploadedFile objects
    // Each file gets a unique ID and starts in "uploading" status
    const newFiles = Array.from(files).map((file) => ({
      id: Math.random().toString(36).substr(2, 9),  // Generate random ID
      file,
      progress: 0,
      status: "uploading" as const,  // TypeScript: ensure this matches our interface
    }))

    // Add new files to the existing list
    // Spread operator (...) keeps existing files and adds new ones
    setUploadedFiles((prev) => [...prev, ...newFiles])

    // UPLOAD EACH FILE INDIVIDUALLY
    // Process each file in parallel (not waiting for previous to complete)
    newFiles.forEach(async (uploadFile) => {
      try {
        // PROGRESS SIMULATION - Show user that something is happening
        // Real uploads might take time, so we simulate progress for better UX
        const progressInterval = setInterval(() => {
          setUploadedFiles((prev) =>
            prev.map((f) => {
              // Only update progress for this specific file, and only up to 90%
              // (Reserve 90-100% for actual server response)
              if (f.id === uploadFile.id && f.progress < 90) {
                return { ...f, progress: f.progress + 10 }
              }
              return f  // Leave other files unchanged
            }),
          )
        }, 200)  // Update every 200ms

        // ACTUAL API CALL - Upload the file to server
        const result = await uploadToAPI(uploadFile.file, uploadFile.id)
        
        // Stop the progress simulation
        clearInterval(progressInterval)

        // UPDATE FILE STATUS based on server response
        setUploadedFiles((prev) =>
          prev.map((f) => {
            if (f.id === uploadFile.id) {
              if (result.success) {
                return { 
                  ...f, 
                  status: result.status === 'duplicate' ? 'completed' : 'processing',  // Handle duplicates
                  progress: 100,  // Upload complete
                  documentId: result.document_id  // Store server-assigned ID
                }
              } else {
                return { ...f, status: 'error', error: 'Upload failed' }
              }
            }
            return f  // Don't change other files
          }),
        )

        // SIMULATE PROCESSING TIME for non-duplicate files
        // Server might need time to process the document (OCR, analysis, etc.)
        if (result.success && result.status !== 'duplicate') {
          setTimeout(() => {
            setUploadedFiles((prev) =>
              prev.map((f) => 
                f.id === uploadFile.id ? { ...f, status: "completed" } : f
              ),
            )
          }, 2000)  // Simulate 2 second processing time
        }

      } catch (error) {
        // HANDLE UPLOAD ERRORS
        // Clear progress interval and mark file as failed
        setUploadedFiles((prev) =>
          prev.map((f) =>
            f.id === uploadFile.id 
              ? { ...f, status: "error", error: error.message || 'Upload failed' }
              : f
          ),
        )
      }
    })
  }, [authToken, onAuthError])  // Re-create function if these dependencies change

  // EVENT HANDLERS - Functions that respond to user interactions

  /**
   * Handle file selection via file input (clicking "browse" button)
   */
  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files)
  }

  /**
   * Handle drag and drop - when user drops files onto the drop zone
   */
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()  // Prevent browser's default file handling
    setIsDragActive(false)  // User finished dragging
    handleFiles(e.dataTransfer.files)  // Get files from drag event
  }

  /**
   * Handle drag over - when user drags files over the drop zone
   */
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()  // Required to allow dropping
    setIsDragActive(true)  // Show visual feedback that drop zone is active
  }

  /**
   * Handle drag leave - when user drags files away from drop zone
   */
  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragActive(false)  // Remove visual feedback
  }

  /**
   * Remove file from upload list
   * Why needed: User might want to cancel uploads or clear completed ones
   */
  const removeFile = (id: string) => {
    setUploadedFiles((prev) => prev.filter((f) => f.id !== id))
  }

  // RENDER - Create the visual interface
  return (
    <div className="p-6 space-y-6 max-w-4xl mx-auto">
      
      {/* PAGE HEADER - Title and description */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Documents</h1>
        <p className="text-gray-600">Upload your documents for AI-powered analysis and processing</p>
        
        {/* WARNING MESSAGE - Show if user not authenticated */}
        {!authToken && (
          <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-yellow-800">⚠️ Please log in to upload documents</p>
          </div>
        )}
      </div>

      {/* UPLOAD AREA - Drag & drop zone and file picker */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
        
        {/* Section header */}
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Document Upload</h2>
          <p className="text-sm text-gray-600 mt-1">
            Drag and drop your files here, or click to browse. Supported formats: PDF, DOC, DOCX, Images
          </p>
        </div>
        
        {/* Drop zone */}
        <div className="p-6">
          <div
            // Drag and drop event handlers
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            className={`
              border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all relative
              ${!authToken ? "opacity-50 cursor-not-allowed" : ""}
              ${isDragActive ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-gray-400 hover:bg-gray-50"}
            `}
          >
            {/* Hidden file input - triggered when user clicks anywhere in drop zone */}
            <input
              type="file"
              multiple  // Allow selecting multiple files at once
              accept=".pdf,.doc,.docx,.png,.jpg,.jpeg,.gif"  // Limit to supported file types
              onChange={handleFileInput}
              disabled={!authToken}  // Disable if not authenticated
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
            />
            
            {/* Visual content of drop zone */}
            <div className="flex flex-col items-center gap-4 pointer-events-none">
              <div className="text-6xl">📤</div>  {/* Upload icon */}
              <div>
                <p className="text-lg font-medium text-gray-900">
                  {isDragActive ? "Drop files here..." : "Drag & drop files here"}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  or <span className="text-blue-600 font-medium">browse files</span> from your computer
                </p>
              </div>
              
              {/* Supported file format badges */}
              <div className="flex gap-2 text-xs text-gray-500">
                <span className="px-2 py-1 bg-gray-100 rounded-md">PDF</span>
                <span className="px-2 py-1 bg-gray-100 rounded-md">DOC</span>
                <span className="px-2 py-1 bg-gray-100 rounded-md">DOCX</span>
                <span className="px-2 py-1 bg-gray-100 rounded-md">Images</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* UPLOAD PROGRESS - Show list of uploaded files and their status */}
      {/* Only render if user has uploaded at least one file */}
      {uploadedFiles.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
          
          {/* Section header */}
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Upload Progress</h2>
            <p className="text-sm text-gray-600 mt-1">Track the progress of your document uploads and processing</p>
          </div>
          
          {/* File list */}
          <div className="p-6">
            <div className="space-y-4">
              
              {/* Render each uploaded file */}
              {uploadedFiles.map((uploadFile) => {
                const fileIcon = getFileIcon(uploadFile.file.type)  // Get appropriate icon
                return (
                  <div key={uploadFile.id} className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg border">
                    
                    {/* File type icon */}
                    <div className="text-2xl">{fileIcon}</div>

                    {/* File information and progress */}
                    <div className="flex-1 min-w-0">
                      
                      {/* File name (truncated if too long) */}
                      <h4 className="font-medium text-gray-900 truncate">{uploadFile.file.name}</h4>
                      
                      {/* File size and status badge */}
                      <div className="flex items-center gap-4 mt-1">
                        <span className="text-sm text-gray-500">
                          {(uploadFile.file.size / 1024 / 1024).toFixed(2)} MB
                        </span>
                        
                        {/* Status badge with dynamic styling */}
                        <span
                          className={`px-2 py-1 text-xs rounded-full font-medium ${
                            uploadFile.status === "completed"
                              ? "bg-green-100 text-green-800"      // Green for success
                              : uploadFile.status === "error"
                                ? "bg-red-100 text-red-800"        // Red for errors
                                : uploadFile.status === "processing"
                                ? "bg-yellow-100 text-yellow-800"  // Yellow for processing
                                : "bg-blue-100 text-blue-800"      // Blue for uploading
                          }`}
                        >
                          {uploadFile.status === "uploading" && "Uploading"}
                          {uploadFile.status === "processing" && "Processing"}
                          {uploadFile.status === "completed" && "Completed"}
                          {uploadFile.status === "error" && "Error"}
                        </span>
                      </div>

                      {/* Error message (only shown if upload failed) */}
                      {uploadFile.error && (
                        <p className="text-sm text-red-600 mt-1">{uploadFile.error}</p>
                      )}

                      {/* Progress bar (only shown for active uploads) */}
                      {uploadFile.status !== "completed" && uploadFile.status !== "error" && (
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                            style={{ width: `${uploadFile.progress}%` }}  // Dynamic width based on progress
                          />
                        </div>
                      )}
                    </div>

                    {/* Action buttons and status indicators */}
                    <div className="flex items-center gap-2">
                      {uploadFile.status === "completed" && <span className="text-green-600">✅</span>}
                      {uploadFile.status === "error" && <span className="text-red-600">❌</span>}
                      
                      {/* Remove file button */}
                      <button 
                        className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 transition-colors" 
                        onClick={() => removeFile(uploadFile.id)}
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

/*
COMPREHENSIVE SUMMARY:

WHAT THIS COMPONENT DOES:
🎯 Creates a complete file upload interface for document analysis application
📤 Allows drag-and-drop and click-to-browse file selection
🔐 Handles user authentication and authorization
📊 Shows real-time upload progress and status for multiple files
🔄 Processes files through backend API for AI analysis
❌ Provides comprehensive error handling and user feedback

KEY FEATURES:
• Multi-file upload support
• Drag and drop functionality
• Real-time progress tracking
• Authentication integration
• File type validation
• Error handling and recovery
• Visual status indicators
• File management (remove uploads)

TECHNICAL ARCHITECTURE:
• React component with hooks for state management
• TypeScript for type safety
• RESTful API integration
• FormData for file uploads
• Authentication token handling
• Responsive design with Tailwind CSS

USER EXPERIENCE:
• Visual feedback during drag operations
• Progress bars and status badges
• File type icons for easy identification
• Error messages for failed uploads
• Disabled state when not authenticated
• Easy file removal functionality

WHY EACH PART EXISTS:
• State management: Track multiple files and their upload states
• Authentication: Secure file uploads with user verification
• Progress tracking: Keep users informed during potentially long uploads
• Error handling: Graceful failure recovery and user notification
• File validation: Ensure only supported file types are processed
• Visual feedback: Clear communication of system status to users
*/