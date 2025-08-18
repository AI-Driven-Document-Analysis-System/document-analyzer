// API service layer for connecting to FastAPI backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

class ApiService {
  private async request(endpoint: string, options: RequestInit = {}) {
    const url = `${API_BASE_URL}${endpoint}`
    const config = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    }

    const response = await fetch(url, config)

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
