import React, { useState, useCallback } from "react"
import './documentUpload.css' 
import DocumentEditor from "../ocr/text_editor" 

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
    return window.localStorage?.getItem('token') ||
           window.sessionStorage?.getItem('token') ||
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
  const [showPopup, setShowPopup] = useState(false);
  const [popupFile, setPopupFile] = useState<UploadedFile | null>(null);

  // Update token on mount and when prop changes
  React.useEffect(() => {
    const token = propAuthToken || getStoredAuthToken();
    setAuthToken(token);
  }, [propAuthToken])

  React.useEffect(() => {
  // Find the most recently completed file
  const justCompleted = uploadedFiles.find(
    (f) => f.status === "completed" && !f['popupShown']
  );
  if (justCompleted) {
    setPopupFile(justCompleted);
    setShowPopup(true);
    // Mark as shown so it doesn't trigger again
    setUploadedFiles((prev) =>
      prev.map((f) =>
        f.id === justCompleted.id ? { ...f, popupShown: true } : f
      )
    );
  }
}, [uploadedFiles]);

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
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: 'var(--bg-secondary)', 
      padding: '24px',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <h1 style={{ 
            fontSize: '24px', 
            fontWeight: '600', 
            color: 'var(--text-primary)', 
            marginBottom: '8px',
            margin: '0 0 8px 0'
          }}>Document Upload</h1>
          <p style={{ 
            color: 'var(--text-secondary)',
            fontSize: '16px',
            margin: '0'
          }}>
            Upload your documents for AI-powered analysis and processing
          </p>
        </div>

        {/* Upload Card */}
        <div style={{ 
          backgroundColor: 'var(--bg-primary)', 
          borderRadius: '8px', 
          border: '1px solid var(--border-color)', 
          boxShadow: 'var(--card-shadow)',
          marginBottom: '24px'
        }}>
          <div style={{ 
            padding: '24px', 
            borderBottom: '1px solid var(--border-color)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <h2 style={{ 
                  fontSize: '18px', 
                  fontWeight: '500', 
                  color: 'var(--text-primary)',
                  margin: '0 0 4px 0'
                }}>Upload Documents</h2>
                <p style={{ 
                  fontSize: '14px', 
                  color: 'var(--text-secondary)', 
                  margin: '0'
                }}>
                  Drag and drop files or click to browse
                </p>
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <span style={{ 
                  padding: '4px 8px', 
                  backgroundColor: '#f3f4f6', 
                  color: '#374151', 
                  borderRadius: '4px', 
                  fontSize: '12px', 
                  fontWeight: '500'
                }}>PDF</span>
                <span style={{ 
                  padding: '4px 8px', 
                  backgroundColor: '#f3f4f6', 
                  color: '#374151', 
                  borderRadius: '4px', 
                  fontSize: '12px', 
                  fontWeight: '500'
                }}>DOC</span>
                <span style={{ 
                  padding: '4px 8px', 
                  backgroundColor: '#f3f4f6', 
                  color: '#374151', 
                  borderRadius: '4px', 
                  fontSize: '12px', 
                  fontWeight: '500'
                }}>Images</span>
              </div>
            </div>
          </div>
          
          <div style={{ padding: '24px' }}>
            <input
              type="file"
              multiple
              accept=".pdf,.doc,.docx,.png,.jpg,.jpeg,.gif"
              onChange={handleFileInput}
              disabled={!authToken}
              style={{ display: 'none' }}
              id="fileInput"
            />
            
            <div
              onClick={handleDropZoneClick}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              style={{
                border: `2px dashed ${isDragActive ? '#3b82f6' : '#d1d5db'}`,
                borderRadius: '8px',
                padding: '48px',
                textAlign: 'center',
                cursor: authToken ? 'pointer' : 'not-allowed',
                backgroundColor: isDragActive ? '#eff6ff' : 'transparent',
                transition: 'all 0.2s ease',
                opacity: authToken ? 1 : 0.5
              }}
            >
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <div style={{ 
                  fontSize: '48px', 
                  color: '#3b82f6', 
                  marginBottom: '16px'
                }}>
                  <i className="fas fa-cloud-upload-alt"></i>
                </div>
                
                <div style={{ marginBottom: '16px' }}>
                  <p style={{ 
                    fontSize: '18px', 
                    fontWeight: '500', 
                    color: 'var(--text-primary)', 
                    marginBottom: '8px',
                    margin: '0 0 8px 0'
                  }}>
                    {isDragActive ? "Drop files here" : "Drag & drop files here"} or{' '}
                    <span style={{ color: '#3b82f6', textDecoration: 'underline' }}>browse files</span>
                  </p>
                  <p style={{ 
                    fontSize: '14px', 
                    color: 'var(--text-secondary)',
                    margin: '0'
                  }}>
                    Supports PDF, DOC, DOCX, PNG, JPG, GIF up to 50MB each
                  </p>
                </div>
                
                <button 
                  style={{
                    padding: '12px 16px',
                    backgroundColor: '#3b82f6',
                    color: 'white',
                    borderRadius: '8px',
                    border: 'none',
                    fontSize: '14px',
                    fontWeight: '500',
                    cursor: 'pointer',
                    transition: 'background-color 0.2s ease'
                  }}
                  onClick={(e) => {
                    e.stopPropagation();
                    document.getElementById('fileInput')?.click();
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#2563eb';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = '#3b82f6';
                  }}
                >
                  Browse Files
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Upload Progress Section */}
        {uploadedFiles.length > 0 && (
          <div style={{ 
            backgroundColor: 'var(--bg-primary)', 
            borderRadius: '8px', 
            border: '1px solid var(--border-color)', 
            boxShadow: 'var(--card-shadow)'
          }}>
            <div style={{ 
              padding: '24px', 
              borderBottom: '1px solid var(--border-color)'
            }}>
              <h2 style={{ 
                fontSize: '18px', 
                fontWeight: '500', 
                color: 'var(--text-primary)',
                margin: '0 0 4px 0'
              }}>Upload Progress</h2>
              <p style={{ 
                fontSize: '14px', 
                color: 'var(--text-secondary)', 
                margin: '0'
              }}>
                Track your document uploads and processing status
              </p>
            </div>
            <div style={{ padding: '24px' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {uploadedFiles.map((uploadFile) => {
                  const fileIcon = getFileIcon(uploadFile.file.type)
                  return (
                    <div key={uploadFile.id} style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '16px',
                      padding: '12px',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      backgroundColor: '#f9fafb',
                      transition: 'background-color 0.2s ease'
                    }}>
                      <div style={{ fontSize: '20px', color: '#3b82f6' }}>
                        <i className={fileIcon}></i>
                      </div>

                      <div style={{ flex: 1, minWidth: 0 }}>
                        <h4 style={{ 
                          fontWeight: '500', 
                          color: '#1f2937', 
                          fontSize: '14px',
                          margin: '0 0 4px 0',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap'
                        }}>{uploadFile.file.name}</h4>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '4px' }}>
                          <span style={{ fontSize: '12px', color: '#6b7280' }}>
                            {(uploadFile.file.size / 1024 / 1024).toFixed(2)} MB
                          </span>
                          <span style={{
                            padding: '2px 8px',
                            fontSize: '12px',
                            borderRadius: '4px',
                            fontWeight: '500',
                            ...(uploadFile.status === "completed" && {
                              backgroundColor: '#dcfce7',
                              color: '#166534'
                            }),
                            ...(uploadFile.status === "error" && {
                              backgroundColor: '#fecaca',
                              color: '#991b1b'
                            }),
                            ...(uploadFile.status === "processing" && {
                              backgroundColor: '#fef3c7',
                              color: '#92400e'
                            }),
                            ...(uploadFile.status === "uploading" && {
                              backgroundColor: '#dbeafe',
                              color: '#1e40af'
                            })
                          }}>
                            {uploadFile.status === "uploading" && "Uploading"}
                            {uploadFile.status === "processing" && "Processing"}
                            {uploadFile.status === "completed" && "Completed"}
                            {uploadFile.status === "error" && "Error"}
                          </span>
                        </div>

                        {uploadFile.error && (
                          <p style={{ fontSize: '12px', color: '#dc2626', margin: '4px 0 0 0' }}>
                            {uploadFile.error}
                          </p>
                        )}
                        
                        {uploadFile.status !== "completed" && uploadFile.status !== "error" && (
                          <div style={{
                            width: '100%',
                            backgroundColor: '#e5e7eb',
                            borderRadius: '4px',
                            height: '6px',
                            marginTop: '8px',
                            overflow: 'hidden'
                          }}>
                            <div style={{
                              backgroundColor: '#3b82f6',
                              height: '100%',
                              borderRadius: '4px',
                              width: `${uploadFile.progress}%`,
                              transition: 'width 0.3s ease'
                            }} />
                          </div>
                        )}
                        </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        {uploadFile.status === "completed" && (
                          <button
                            style={{
                              marginLeft: '8px',
                              padding: '2px 8px',
                              backgroundColor: '#dcfce7',
                              color: '#166534',
                              border: '1px solid #166534',
                              borderRadius: '4px',
                              cursor: 'pointer',
                              fontSize: '12px',
                              fontWeight: '500',

                            }}
                            onClick={() => {
                              console.log('View clicked:', uploadFile);
                              setPopupFile(uploadFile);
                              setShowPopup(true);
                            }}
                          >
                            View
                          </button>
                        )}
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        {uploadFile.status === "completed" && (
                          <span style={{ color: '#10b981', fontSize: '18px' }}>
                            <i className="fas fa-check-circle"></i>
                          </span>
                        )}
                        {uploadFile.status === "error" && (
                          <span style={{ color: '#ef4444', fontSize: '18px' }}>
                            <i className="fas fa-times-circle"></i>
                          </span>
                        )}
                        
                        <button
                          style={{
                            padding: '4px',
                            color: '#9ca3af',
                            backgroundColor: 'transparent',
                            border: 'none',
                            cursor: 'pointer',
                            borderRadius: '4px',
                            transition: 'color 0.2s ease'
                          }}
                          onClick={() => removeFile(uploadFile.id)}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.color = '#ef4444';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.color = '#9ca3af';
                          }}
                        >
                          <i className="fas fa-times" style={{ fontSize: '14px' }}></i>
                        </button>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        )}
        
        {/* Empty State */}
        {uploadedFiles.length === 0 && (
          <div style={{ textAlign: 'center', padding: '64px 0' }}>
            <div style={{ fontSize: '48px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
              <i className="fas fa-file-upload"></i>
            </div>
            <h3 style={{ 
              fontSize: '18px', 
              fontWeight: '500', 
              color: 'var(--text-secondary)',
              margin: '0 0 4px 0'
            }}>No files uploaded yet</h3>
            <p style={{ 
              color: 'var(--text-tertiary)', 
              margin: '0',
              fontSize: '14px'
            }}>Upload your first document to get started</p>
          </div>
        )}
      </div>
      {showPopup && popupFile && popupFile.documentId && (
        <DocumentEditor
          documentId={popupFile.documentId}
          onClose={() => setShowPopup(false)}
          authToken={authToken || undefined}
        />
      )}
    </div>
  )
}