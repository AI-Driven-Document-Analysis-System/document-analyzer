import type { Document, DocumentIconInfo } from '../types'

export const formatDate = (dateString: string) => {
  const options: Intl.DateTimeFormatOptions = { year: 'numeric', month: 'short', day: 'numeric' }
  return new Date(dateString).toLocaleDateString(undefined, options)
}

export const sizeToBytes = (sizeStr: string) => {
  const units: { [key: string]: number } = { 'B': 1, 'KB': 1024, 'MB': 1024 * 1024, 'GB': 1024 * 1024 * 1024 }
  const match = sizeStr.match(/(\d+(?:\.\d+)?)\s*(B|KB|MB|GB)/i)
  if (!match) return 0
  const value = parseFloat(match[1])
  const unit = match[2].toUpperCase()
  return value * (units[unit] || 1)
}

export const getDocumentIcon = (type: string): DocumentIconInfo => {
  switch(type) {
    case 'pdf':
      return { icon: 'fa-file-pdf', color: '#ef4444', bg: '#fef2f2' }
    case 'png':
    case 'jpg':
    case 'jpeg':
      return { icon: 'fa-file-image', color: '#8b5cf6', bg: '#f3e8ff' }
    case 'txt':
      return { icon: 'fa-file-alt', color: '#6b7280', bg: '#f9fafb' }
    case 'doc':
    case 'docx':
      return { icon: 'fa-file-word', color: '#3b82f6', bg: '#dbeafe' }
    case 'xls':
    case 'xlsx':
      return { icon: 'fa-file-excel', color: '#22c55e', bg: '#dcfce7' }
    case 'ppt':
    case 'pptx':
      return { icon: 'fa-file-powerpoint', color: '#0ea5e9', bg: '#f0f9ff' }
    default:
      return { icon: 'fa-file', color: '#6b7280', bg: '#f3f4f6' }
  }
}

export const getFilteredAndSortedDocuments = (
  documents: Document[],
  documentFilter: string,
  documentSearch: string,
  sortDate: string,
  sortSize: string
) => {
  let filtered = documents.filter(doc => {
    // Debug logging for filtering
    if (documentFilter === 'img') {
      console.log('IMG Filter - Document:', {
        name: doc.name,
        type: doc.type,
        isImageType: ['png', 'jpg', 'jpeg'].includes(doc.type)
      })
    }
    
    // Type filter
    if (documentFilter !== 'all') {
      if (documentFilter === 'img') {
        // For 'img' filter, include png, jpg, and jpeg files
        if (!['png', 'jpg', 'jpeg'].includes(doc.type)) {
          return false
        }
      } else if (doc.type !== documentFilter) {
        return false
      }
    }

    // Search filter
    if (documentSearch && !doc.name.toLowerCase().includes(documentSearch.toLowerCase())) {
      return false
    }

    return true
  })

  // Sort documents
  filtered.sort((a, b) => {
    if (sortDate === 'none') {
      if (sortSize === 'none') {
        return 0
      }
      if (sortSize === 'size-desc') {
        return sizeToBytes(b.size) - sizeToBytes(a.size)
      } else if (sortSize === 'size-asc') {
        return sizeToBytes(a.size) - sizeToBytes(b.size)
      }
    }

    if (sortDate === 'date-desc') {
      return new Date(b.date).getTime() - new Date(a.date).getTime()
    } else if (sortDate === 'date-asc') {
      return new Date(a.date).getTime() - new Date(b.date).getTime()
    }

    if (sortSize === 'size-desc') {
      return sizeToBytes(b.size) - sizeToBytes(a.size)
    } else if (sortSize === 'size-asc') {
      return sizeToBytes(a.size) - sizeToBytes(b.size)
    }

    return 0
  })

  return filtered
}
