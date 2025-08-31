// API service layer for connecting to FastAPI backend

/**
 * API service layer for connecting to FastAPI backend
 * Provides a centralized interface for all API communications
 */

// Base URL for the API - defaults to localhost if not set in environment

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

/**
 * ApiService class handles all HTTP requests to the FastAPI backend
 * Implements error handling and request configuration
 */

class ApiService {

   /**
   * Generic request method that handles common HTTP operations
   * @param endpoint - The API endpoint to call (e.g., "/documents")
   * @param options - Fetch API options (method, headers, body, etc.)
   * @returns Promise with parsed JSON response
   * @throws Error if the HTTP request fails
   */

  private async request(endpoint: string, options: RequestInit = {}) {

    // Construct full URL by combining base URL with endpoint

    const url = `${API_BASE_URL}${endpoint}`

    // Get authentication token
    const token = localStorage.getItem("token")

    // Default configuration with JSON content type and auth header
    const config = { // Default configuration
      headers: {
        "Content-Type": "application/json",
        ...(token && { "Authorization": `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    } // Merge with provided options

    const response = await fetch(url, config) // Perform the fetch request

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`)
    }

    return response.json()
  }

  // Document endpoints
  async uploadDocument(file: File) {
    const formData = new FormData()
    formData.append("file", file)

    const token = localStorage.getItem("token")
    
    return fetch(`${API_BASE_URL}/documents/upload`, {
      method: "POST",
      body: formData,
      headers: {
        ...(token && { "Authorization": `Bearer ${token}` }),
      },
    }).then(response => {
      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`)
      }
      return response.json()
    })
  }

  async getDocuments() {
    return this.request("/documents")
  }

  async getDocument(id: string) {
    return this.request(`/documents/${id}`)
  }

  // Search endpoints
  async searchDocuments(query: string, filters: any) {
    return this.request("/documents/search", {
      method: "POST",
      body: JSON.stringify({
        query,
        filters,
      }),
    })
  }

  async getDocumentTypes() {
    return this.request("/documents/types")
  }

  // Document actions
  async downloadDocument(documentId: string) {
    return this.request(`/documents/${documentId}/download`)
  }

  // Summarization endpoints
  async generateSummary(documentId: string, summaryType: string) {
    return this.request("/summarize", {
      method: "POST",
      body: JSON.stringify({
        document_id: documentId,
        summary_type: summaryType
      }),
    })
  }

  async getSummaryOptions() {
    return this.request("/summarize/options")
  }

  async getDocumentSummaries(documentId: string) {
    return this.request(`/summarize/document/${documentId}`)
  }

  // RAG Chat endpoints
  async chatWithRAG(message: string, conversationId?: string) {
    return this.request("/chat/rag", {
      method: "POST",
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
      }),
    })
  }

  // Classification endpoints
  async getClassification(documentId: string) {
    return this.request(`/classification/${documentId}`)
  }

  // Analytics endpoints
  async getAnalytics() {
    return this.request("/analytics")
  }

  // Auth endpoints
  async login(email: string, password: string) {
    return this.request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    })
  }

  async register(userData: any) {
    return this.request("/auth/register", {
      method: "POST",
      body: JSON.stringify(userData),
    })
  }
}

export const apiService = new ApiService()
