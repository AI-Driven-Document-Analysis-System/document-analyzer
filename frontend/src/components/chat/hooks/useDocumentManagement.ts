import { useState, useEffect } from 'react'
import type { Document, DocumentFilters } from '../types'

const API_BASE_URL = "http://localhost:8000"

interface DocumentSelectionResponse {
  user_id: string
  document_ids: string[]  // Changed from number[] to string[]
  created_at: string
  updated_at: string
}

export const useDocumentManagement = () => {
  const [showDocumentModal, setShowDocumentModal] = useState(false)
  const [showRestoredNotification, setShowRestoredNotification] = useState(false)
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(false)
  
  const [documentFilter, setDocumentFilter] = useState('all')
  const [documentSearch, setDocumentSearch] = useState('')
  const [sortDate, setSortDate] = useState('none')
  const [sortSize, setSortSize] = useState('none')

  // Load selected documents from database on mount
  useEffect(() => {
    console.log('🔄 useEffect triggered - loading document selection...')
    loadDocumentSelection()
  }, [])

  // Debug: Track when selectedDocuments changes
  useEffect(() => {
    console.log('🔍 selectedDocuments changed:', selectedDocuments)
  }, [selectedDocuments])

  const loadDocumentSelection = async () => {
    try {
      setIsLoading(true)
      const token = localStorage.getItem('token')
      if (!token) {
        console.log('❌ No token found for loading document selection')
        return
      }

      console.log('📥 Loading document selection from database...')

      const response = await fetch(`${API_BASE_URL}/api/document-selections/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data: DocumentSelectionResponse = await response.json()
        console.log('📥 Loaded document selection:', data)
        
        if (data.document_ids && data.document_ids.length > 0) {
          console.log('✅ About to restore document selection:', data.document_ids)
          setSelectedDocuments(data.document_ids)
          console.log('✅ Document selection state updated:', data.document_ids)
          
          // Show notification if documents were restored
          setTimeout(() => {
            setShowRestoredNotification(true)
            setTimeout(() => setShowRestoredNotification(false), 3000)
          }, 1000)
        } else {
          console.log('📥 No saved document selection found')
        }
      } else {
        const error = await response.text()
        console.error('❌ Failed to load document selection:', response.status, error)
      }
    } catch (error) {
      console.error('❌ Error loading document selection:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const saveDocumentSelection = async (documentIds: string[]) => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        console.log('❌ No token found for saving document selection')
        return
      }

      console.log('💾 Saving document selection:', documentIds)
      
      const response = await fetch(`${API_BASE_URL}/api/document-selections/save`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ document_ids: documentIds })
      })

      if (response.ok) {
        const result = await response.json()
        console.log('✅ Document selection saved successfully:', result)
      } else {
        const error = await response.text()
        console.error('❌ Failed to save document selection:', response.status, error)
      }
    } catch (error) {
      console.error('❌ Error saving document selection:', error)
    }
  }

  const toggleDocumentSelection = (docId: string) => {
    const newSelection = selectedDocuments.includes(docId) 
      ? selectedDocuments.filter(id => id !== docId)
      : [...selectedDocuments, docId]
    
    setSelectedDocuments(newSelection)
    saveDocumentSelection(newSelection)
  }

  const removeDocument = (docId: string) => {
    const newSelection = selectedDocuments.filter(id => id !== docId)
    setSelectedDocuments(newSelection)
    saveDocumentSelection(newSelection)
  }

  const clearAllDocuments = async () => {
    try {
      const token = localStorage.getItem('token')
      if (!token) return

      await fetch(`${API_BASE_URL}/api/document-selections/clear`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      setSelectedDocuments([])
    } catch (error) {
      console.error('Error clearing document selection:', error)
    }
  }

  const clearPersistedSelection = async () => {
    await clearAllDocuments()
  }

  return {
    showDocumentModal,
    setShowDocumentModal,
    selectedDocuments,
    setSelectedDocuments,
    documentFilter,
    setDocumentFilter,
    documentSearch,
    setDocumentSearch,
    sortDate,
    setSortDate,
    sortSize,
    setSortSize,
    toggleDocumentSelection,
    removeDocument,
    clearAllDocuments,
    clearPersistedSelection,
    showRestoredNotification,
    setShowRestoredNotification,
    isLoading
  }
}
