import { useState } from 'react'
import type { Document, DocumentFilters } from '../types'

export const useDocumentManagement = () => {
  const [showDocumentModal, setShowDocumentModal] = useState(false)
  const [selectedDocuments, setSelectedDocuments] = useState<number[]>([])
  const [documentFilter, setDocumentFilter] = useState('all')
  const [documentSearch, setDocumentSearch] = useState('')
  const [sortDate, setSortDate] = useState('none')
  const [sortSize, setSortSize] = useState('none')

  const toggleDocumentSelection = (docId: number) => {
    setSelectedDocuments(prev => 
      prev.includes(docId) 
        ? prev.filter(id => id !== docId)
        : [...prev, docId]
    )
  }

  const removeDocument = (docId: number) => {
    setSelectedDocuments(prev => prev.filter(id => id !== docId))
  }

  const clearAllDocuments = () => {
    setSelectedDocuments([])
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
    clearAllDocuments
  }
}
