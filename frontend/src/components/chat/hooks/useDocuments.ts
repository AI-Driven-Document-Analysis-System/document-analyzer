import { useState, useEffect } from 'react'
import { apiService } from '../../../services/api'
import type { Document } from '../types'

export const useDocuments = () => {
  const [documents, setDocuments] = useState<Document[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchDocuments = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      const response = await apiService.getDocuments()
      
      if (response.documents && Array.isArray(response.documents)) {
        // Transform the API response to match our Document interface
        const transformedDocuments: Document[] = response.documents.map((doc: any) => {
          const detectedType = getFileExtension(doc.original_filename || '', doc.content_type || '')
          
          // Debug logging to see what's happening
          console.log('Document processing:', {
            filename: doc.original_filename,
            mimeType: doc.content_type,
            detectedType: detectedType
          })
          
          return {
            id: doc.id,
            name: doc.original_filename || 'Untitled Document',
            type: detectedType,
            size: formatFileSize(doc.file_size || 0),
            date: doc.upload_date ? new Date(doc.upload_date).toISOString().split('T')[0] : new Date().toISOString().split('T')[0]
          }
        })
        
        setDocuments(transformedDocuments)
      } else {
        setDocuments([])
      }
    } catch (err) {
      console.error('Error fetching documents:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch documents')
      setDocuments([]) // Set empty array on error
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [])

  // Helper function to extract file extension and map to document type
  const getFileExtension = (filename: string, mimeType: string = ''): string => {
    console.log('Processing file:', { filename, mimeType })
    
    // First try to get extension from filename
    if (filename) {
      // Use regex to find the actual file extension at the end
      const extensionMatch = filename.match(/\.([a-zA-Z0-9]+)(?:\s*\([^)]*\))?$/i)
      const extension = extensionMatch ? extensionMatch[1].toLowerCase() : null
      
      console.log('Extension detection:', {
        filename,
        extensionMatch,
        extension
      })
      
      if (extension) {
        switch (extension) {
          case 'pdf':
            return 'pdf'
          case 'png':
            return 'png'
          case 'jpg':
          case 'jpeg':
            return 'jpg'
          case 'txt':
            return 'txt'
          case 'doc':
          case 'docx':
            return 'doc'
          case 'xls':
          case 'xlsx':
            return 'xls'
          case 'ppt':
          case 'pptx':
            return 'ppt'
        }
      }
    }
    
    // If filename extension doesn't match, check MIME type as fallback
    if (mimeType) {
      switch (mimeType.toLowerCase()) {
        case 'application/pdf':
          return 'pdf'
        case 'image/png':
          return 'png'
        case 'image/jpeg':
        case 'image/jpg':
          return 'jpg'
        case 'text/plain':
          return 'txt'
        case 'application/msword':
        case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
          return 'doc'
        case 'application/vnd.ms-excel':
        case 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
          return 'xls'
        case 'application/vnd.ms-powerpoint':
        case 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
          return 'ppt'
      }
    }
    
    return 'unknown'
  }

  // Helper function to format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
  }

  return {
    documents,
    isLoading,
    error,
    refetch: fetchDocuments
  }
}
