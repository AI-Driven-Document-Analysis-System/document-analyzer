export interface Message {
  id: string
  type: "user" | "assistant"
  content: string
  timestamp: Date
  sources?: Array<{
    title: string
    type: string
    confidence: number
  }>
  rephrasedQueries?: string[]
}

export interface Document {
  id: string  // Changed from number to string (UUIDs)
  name: string
  type: string
  size: string
  date: string
}

export interface ChatHistory {
  id: string
  title: string
  timestamp: string
  messageCount?: number
}

export interface ExpandedSections {
  sources: boolean
  history: boolean
  knowledge: boolean
}

export interface DocumentIconInfo {
  icon: string
  color: string
  bg: string
}

export interface DocumentFilters {
  filter: string
  search: string
  sortDate: string
  sortSize: string
}
