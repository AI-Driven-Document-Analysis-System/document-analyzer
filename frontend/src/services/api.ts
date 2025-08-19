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

        // Default configuration with JSON content type

        // Default configuration for fetch requests what this code does is to set the Content-Type header to application/json and merge it with any additional headers provided in the options parameter. This ensures that the request will be sent with the correct content type for JSON data.
    const config = { // Default configuration
      headers: {
        "Content-Type": "application/json",
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

    return this.request("/documents/upload", {
      method: "POST",
      body: formData,
      headers: {}, // Remove Content-Type to let browser set it for FormData
    })
  }

  async getDocuments() {
    return this.request("/documents")
  }

  async getDocument(id: string) {
    return this.request(`/documents/${id}`)
  }

  // Summarization endpoints
  async generateSummary(documentId: string, model: string, options: any) {
    return this.request("/summarization/generate", {
      method: "POST",
      body: JSON.stringify({
        document_id: documentId,
        model,
        ...options,
      }),
    })
  }

  // Search endpoints
  async searchDocuments(query: string, filters: any) {
    return this.request("/search/documents", {
      method: "POST",
      body: JSON.stringify({
        query,
        filters,
      }),
    })
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
