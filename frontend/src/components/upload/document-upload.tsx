

import React, { useState, useCallback } from "react"

interface UploadedFile {
  id: string
  file: File
  progress: number
  status: "uploading" | "processing" | "completed" | "error"
  error?: string
  documentId?: string
}

interface DocumentUploadProps {
  authToken?: string
  onAuthError?: () => void
}

const getFileIcon = (type: string) => {
  if (type.includes("pdf")) return "fas fa-file-pdf"
  if (type.includes("image")) return "fas fa-image"
  if (type.includes("spreadsheet") || type.includes("excel")) return "fas fa-file-excel"
  return "fas fa-folder"
}

// Mock auth service - replace with your actual implementation
const getStoredAuthToken = () => {
  try {
    // Try to get from localStorage first, then sessionStorage
    return window.localStorage?.getItem('authToken') || 
           window.sessionStorage?.getItem('authToken') ||
           'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3OWQwYmVkNS1jMWMxLTRmYWYtODJkNC1mZWQxYTI4NDcyZDUiLCJlbWFpbCI6InRlc3QxQGdtYWlsLmNvbSIsImV4cCI6MTc1NzMyNzc5OH0.h_P47qNaOhJ9r34alekxTlvXxen45dbTXokBans669c'; // Your actual token as fallback for demo
  } catch (e) {
    // Fallback token for environments without localStorage
    return 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3OWQwYmVkNS1jMWMxLTRmYWYtODJkNC1mZWQxYTI4NDcyZDUiLCJlbWFpbCI6InRlc3QxQGdtYWlsLmNvbSIsImV4cCI6MTc1NzMyNzc5OH0.h_P47qNaOhJ9r34alekxTlvXxen45dbTXokBans669c';
  }
}

export function DocumentUpload({ authToken: propAuthToken, onAuthError }: DocumentUploadProps = {}) {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [isDragActive, setIsDragActive] = useState(false)
  const [authToken, setAuthToken] = useState<string | null>(null)
  
  // Update token on mount and when prop changes
  React.useEffect(() => {
    const token = propAuthToken || getStoredAuthToken();
    setAuthToken(token);
  }, [propAuthToken])

  const uploadToAPI = async (file: File, fileId: string) => {
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('filename', file.name)
      formData.append('content_type', file.type)

      // Attach user_id if we have it in localStorage
      try {
        const userStr = localStorage.getItem('user')
        if (userStr) {
          const user = JSON.parse(userStr)
          const uid = user?.id || user?.user?.id || user?.user_id
          if (uid) {
            formData.append('override_user_id', String(uid))
          }
        }
      } catch {}

      if (!authToken) {
        throw new Error('No authentication token provided')
      }

      // Also set X-User-Id header as a secondary hint
      let userIdHeader: Record<string, string> = {}
      try {
        const userStr = localStorage.getItem('user')
        if (userStr) {
          const user = JSON.parse(userStr)
          const uid = user?.id || user?.user?.id || user?.user_id
          if (uid) {
            userIdHeader['X-User-Id'] = String(uid)
          }
        }
      } catch {}

      const response = await fetch('http://localhost:8000/api/documents/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          ...userIdHeader,
        },
        body: formData,
      })

      if (!response.ok) {
        if (response.status === 401) {
          onAuthError?.()
          throw new Error('Authentication failed. Please log in again.')
        }
        const errorText = await response.text()
        let errorMessage
        try {
          const errorData = JSON.parse(errorText)
          errorMessage = errorData.detail || `Upload failed with status ${response.status}`
        } catch {
          errorMessage = `Upload failed with status ${response.status}: ${errorText}`
        }
        throw new Error(errorMessage)
      }

      const result = await response.json()
      return {
        success: true,
        document_id: result.document_id,
        status: result.status
      }
    } catch (error) {
      console.error('Upload error:', error)
      throw error
    }
  }

  const handleFiles = useCallback((files: FileList | null) => {
    if (!files) return

    if (!authToken) {
      alert('Please log in to upload files')
      return
    }

    const newFiles = Array.from(files).map((file) => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      progress: 0,
      status: "uploading" as const,
    }))

    setUploadedFiles((prev) => [...prev, ...newFiles])

    // Actually upload files to the API
    newFiles.forEach(async (uploadFile) => {
      try {
        // Start upload progress simulation
        const progressInterval = setInterval(() => {
          setUploadedFiles((prev) =>
            prev.map((f) => {
              if (f.id === uploadFile.id && f.progress < 90) {
                return { ...f, progress: f.progress + 10 }
              }
              return f
            }),
          )
        }, 200)

        // Make actual API call
        const result = await uploadToAPI(uploadFile.file, uploadFile.id)
        
        // Clear progress interval
        clearInterval(progressInterval)

        // Update file status based on API response
        setUploadedFiles((prev) =>
          prev.map((f) => {
            if (f.id === uploadFile.id) {
              if (result.success) {
                return { 
                  ...f, 
                  status: result.status === 'duplicate' ? 'completed' : 'processing', 
                  progress: 100,
                  documentId: result.document_id
                }
              } else {
                return { ...f, status: 'error', error: 'Upload failed' }
              }
            }
            return f
          }),
        )

        // If processing, simulate processing completion
        if (result.success && result.status !== 'duplicate') {
          setTimeout(() => {
            setUploadedFiles((prev) =>
              prev.map((f) => 
                f.id === uploadFile.id ? { ...f, status: "completed" } : f
              ),
            )
          }, 2000)
        }

      } catch (error) {
        // Clear any intervals and mark as error
        setUploadedFiles((prev) =>
          prev.map((f) =>
            f.id === uploadFile.id 
              ? { ...f, status: "error", error: error.message || 'Upload failed' }
              : f
          ),
        )
      }
    })
  }, [authToken, onAuthError])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files)
  }

  const handleDropZoneClick = () => {
    if (!authToken) return
    
    // Create a file input and trigger click
    const fileInput = document.createElement('input')
    fileInput.type = 'file'
    fileInput.multiple = true
    fileInput.accept = '.pdf,.doc,.docx,.png,.jpg,.jpeg,.gif'
    fileInput.onchange = (e) => {
      const target = e.target as HTMLInputElement
      handleFiles(target.files)
    }
    fileInput.click()
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragActive(false)
    handleFiles(e.dataTransfer.files)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragActive(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragActive(false)
  }

  const removeFile = (id: string) => {
    setUploadedFiles((prev) => prev.filter((f) => f.id !== id))
  }

  return (
    <div className="p-6 space-y-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Documents</h1>
        <p className="text-gray-600">Upload your documents for AI-powered analysis and processing</p>
        {!authToken && (
          <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-yellow-800"><i className="fas fa-exclamation-triangle"></i> Please log in to upload documents</p>
          </div>
        )}
      </div>

      {/* Upload Area */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Document Upload</h2>
          <p className="text-sm text-gray-600 mt-1">
            Drag and drop your files here, or click to browse. Supported formats: PDF, DOC, DOCX, Images
          </p>
        </div>
        <div className="p-6">
          <div
            onClick={handleDropZoneClick}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            className={`
              border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all relative
              ${!authToken ? "opacity-50 cursor-not-allowed" : "hover:bg-blue-50"}
              ${isDragActive ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-blue-400"}
            `}
          >
            <div className="flex flex-col items-center gap-4">
              <div className={`text-6xl transition-colors ${isDragActive ? "text-blue-600" : "text-blue-500"}`}>
                <i className="fas fa-cloud-upload-alt"></i>
              </div>
              <div>
                <p className="text-lg font-medium text-gray-900">
                  {isDragActive ? "Drop files here..." : "Click here to upload or drag & drop files"}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  Select multiple files or <span className="text-blue-600 font-medium">browse from your computer</span>
                </p>
              </div>
              <div className="flex gap-2 text-xs text-gray-500">
                <span className="px-2 py-1 bg-gray-100 rounded-md">PDF</span>
                <span className="px-2 py-1 bg-gray-100 rounded-md">DOC</span>
                <span className="px-2 py-1 bg-gray-100 rounded-md">DOCX</span>
                <span className="px-2 py-1 bg-gray-100 rounded-md">Images</span>
              </div>
              {/* {authToken && (
                <div className="text-xs text-gray-400 bg-gray-50 px-3 py-1 rounded-full">
                  <i className="fas fa-mouse-pointer mr-1"></i>
                  Click anywhere in this area to upload
                </div>
              )} */}
            </div>
          </div>
        </div>
      </div>

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Upload Progress</h2>
            <p className="text-sm text-gray-600 mt-1">Track the progress of your document uploads and processing</p>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {uploadedFiles.map((uploadFile) => {
                const fileIcon = getFileIcon(uploadFile.file.type)
                return (
                  <div key={uploadFile.id} className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg border">
                    <div className="text-2xl text-blue-600"><i className={fileIcon}></i></div>

                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-gray-900 truncate">{uploadFile.file.name}</h4>
                      <div className="flex items-center gap-4 mt-1">
                        <span className="text-sm text-gray-500">
                          {(uploadFile.file.size / 1024 / 1024).toFixed(2)} MB
                        </span>
                        <span
                          className={`px-2 py-1 text-xs rounded-full font-medium ${
                            uploadFile.status === "completed"
                              ? "bg-green-100 text-green-800"
                              : uploadFile.status === "error"
                                ? "bg-red-100 text-red-800"
                                : uploadFile.status === "processing"
                                ? "bg-yellow-100 text-yellow-800"
                                : "bg-blue-100 text-blue-800"
                          }`}
                        >
                          {uploadFile.status === "uploading" && "Uploading"}
                          {uploadFile.status === "processing" && "Processing"}
                          {uploadFile.status === "completed" && "Completed"}
                          {uploadFile.status === "error" && "Error"}
                        </span>
                      </div>

                      {uploadFile.error && (
                        <p className="text-sm text-red-600 mt-1">{uploadFile.error}</p>
                      )}

                      {uploadFile.status !== "completed" && uploadFile.status !== "error" && (
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                            style={{ width: `${uploadFile.progress}%` }}
                          />
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      {uploadFile.status === "completed" && <span className="text-green-600"><i className="fas fa-check-circle"></i></span>}
                      {uploadFile.status === "error" && <span className="text-red-600"><i className="fas fa-times-circle"></i></span>}
                      <button 
                        className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 transition-colors" 
                        onClick={() => removeFile(uploadFile.id)}
                      >
                        <i className="fas fa-times"></i>
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