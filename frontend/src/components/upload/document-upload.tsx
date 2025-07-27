"use client"

import type React from "react"
import { useState, useCallback } from "react"

interface UploadedFile {
  id: string
  file: File
  progress: number
  status: "uploading" | "processing" | "completed" | "error"
  error?: string
}

const getFileIcon = (type: string) => {
  if (type.includes("pdf")) return "📄"
  if (type.includes("image")) return "🖼️"
  if (type.includes("spreadsheet") || type.includes("excel")) return "📊"
  return "📁"
}

export function DocumentUpload() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [isDragActive, setIsDragActive] = useState(false)

  const handleFiles = useCallback((files: FileList | null) => {
    if (!files) return

    const newFiles = Array.from(files).map((file) => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      progress: 0,
      status: "uploading" as const,
    }))

    setUploadedFiles((prev) => [...prev, ...newFiles])

    // Simulate upload progress
    newFiles.forEach((uploadFile) => {
      const interval = setInterval(() => {
        setUploadedFiles((prev) =>
          prev.map((f) => {
            if (f.id === uploadFile.id) {
              if (f.progress >= 100) {
                clearInterval(interval)
                return { ...f, status: "processing" }
              }
              return { ...f, progress: f.progress + 10 }
            }
            return f
          }),
        )
      }, 200)

      // Simulate processing completion
      setTimeout(() => {
        setUploadedFiles((prev) =>
          prev.map((f) => (f.id === uploadFile.id ? { ...f, status: "completed", progress: 100 } : f)),
        )
      }, 3000)
    })
  }, [])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files)
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
    <div className="p-6 space-y-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Documents</h1>
        <p className="text-gray-600">Upload your documents for AI-powered analysis and processing</p>
      </div>

      {/* Upload Area */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Document Upload</h2>
          <p className="card-description">
            Drag and drop your files here, or click to browse. Supported formats: PDF, DOC, DOCX, Images
          </p>
        </div>
        <div className="card-content">
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            className={`
              border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all relative
              ${isDragActive ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-gray-400 hover:bg-gray-50"}
            `}
          >
            <input
              type="file"
              multiple
              accept=".pdf,.doc,.docx,.png,.jpg,.jpeg,.gif"
              onChange={handleFileInput}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <div className="flex flex-col items-center gap-4 pointer-events-none">
              <div className="text-6xl">📤</div>
              <div>
                <p className="text-lg font-medium text-gray-900">
                  {isDragActive ? "Drop files here..." : "Drag & drop files here"}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  or <span className="text-blue-600 font-medium">browse files</span> from your computer
                </p>
              </div>
              <div className="flex gap-2 text-xs text-gray-500">
                <span className="badge badge-secondary">PDF</span>
                <span className="badge badge-secondary">DOC</span>
                <span className="badge badge-secondary">DOCX</span>
                <span className="badge badge-secondary">Images</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Upload Progress</h2>
            <p className="card-description">Track the progress of your document uploads and processing</p>
          </div>
          <div className="card-content">
            <div className="space-y-4">
              {uploadedFiles.map((uploadFile) => {
                const fileIcon = getFileIcon(uploadFile.file.type)
                return (
                  <div key={uploadFile.id} className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg border">
                    <div className="text-2xl">{fileIcon}</div>

                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-gray-900">{uploadFile.file.name}</h4>
                      <div className="flex items-center gap-4 mt-1">
                        <span className="text-sm text-gray-500">
                          {(uploadFile.file.size / 1024 / 1024).toFixed(2)} MB
                        </span>
                        <span
                          className={`badge ${
                            uploadFile.status === "completed"
                              ? "badge-success"
                              : uploadFile.status === "error"
                                ? "badge-error"
                                : "badge-warning"
                          }`}
                        >
                          {uploadFile.status === "uploading" && "Uploading"}
                          {uploadFile.status === "processing" && "Processing"}
                          {uploadFile.status === "completed" && "Completed"}
                          {uploadFile.status === "error" && "Error"}
                        </span>
                      </div>

                      {uploadFile.status !== "completed" && uploadFile.status !== "error" && (
                        <div className="progress mt-2">
                          <div className="progress-bar" style={{ width: `${uploadFile.progress}%` }}></div>
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      {uploadFile.status === "completed" && <span className="text-green-600">✅</span>}
                      {uploadFile.status === "error" && <span className="text-red-600">❌</span>}
                      <button className="btn btn-sm btn-outline" onClick={() => removeFile(uploadFile.id)}>
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
