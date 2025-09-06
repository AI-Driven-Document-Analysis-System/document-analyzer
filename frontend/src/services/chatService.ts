// Chat service for connecting to backend APIs
export interface ChatMessage {
  id: string;
  type: "user" | "assistant";
  content: string;
  timestamp: Date;
  sources?: Array<{
    title: string;
    type: string;
    confidence: number;
  }>;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  sources: Array<{
    title: string;
    type: string;
    confidence: number;
  }>;
  metadata?: any;
}

export interface Document {
  id: number | string;
  name: string;
  type: string;
  size: string;
  date: string;
  original_filename?: string;
  file_size?: number;
  upload_date?: string;
  content_type?: string;
}

class ChatService {
  private baseUrl = 'http://localhost:8000/api';
  private currentUserId: string | null = null;

  async sendMessage(message: string, conversationId?: string, searchMode: string = 'standard'): Promise<ChatResponse> {
    try {
      const userId = await this.getCurrentUserId();
      if (!userId) {
        throw new Error('User not authenticated');
      }

      const response = await fetch(`${this.baseUrl}/chat/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
          user_id: userId,
          memory_type: 'window',
          search_mode: searchMode,
          llm_config: {
            provider: 'groq',
            model: 'llama-3.1-8b-instant',
            temperature: 0.7,
            streaming: false
          }
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return {
        response: data.response,
        conversation_id: data.conversation_id,
        sources: data.sources || [],
        metadata: data.metadata
      };
    } catch (error) {
      console.error('Error sending message:', error);
      console.error('Full error details:', error);
      
      // Log more details about the error
      if (error instanceof Error) {
        console.error('Error message:', error.message);
        console.error('Error stack:', error.stack);
      }
      
      // Fallback to mock response if API fails
      return {
        response: `I apologize, but I'm currently unable to process your request due to a technical issue. Please try again later. Your message was: ${message}`,
        conversation_id: conversationId || `fallback-${Date.now()}`,
        sources: []
      };
    }
  }

  async getDocuments(): Promise<Document[]> {
    try {
      const userId = await this.getCurrentUserId();
      if (!userId) {
        throw new Error('User not authenticated');
      }

      const response = await fetch(`${this.baseUrl}/documents?user_id=${userId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.documents || [];
    } catch (error) {
      console.error('Error fetching documents:', error);
      return [];
    }
  }

  async getConversationHistory(conversationId: string) {
    try {
      const response = await fetch(`${this.baseUrl}/chat/conversations/${conversationId}/history`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching conversation history:', error);
      return { messages: [] };
    }
  }

  async createConversation(title?: string) {
    try {
      const userId = await this.getCurrentUserId();
      if (!userId) {
        throw new Error('User not authenticated');
      }

      const response = await fetch(`${this.baseUrl}/chat/conversations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          title: title || null
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating conversation:', error);
      return null;
    }
  }

  async listConversations() {
    try {
      const userId = await this.getCurrentUserId();
      if (!userId) {
        throw new Error('User not authenticated');
      }

      const response = await fetch(`${this.baseUrl}/chat/conversations?user_id=${userId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error listing conversations:', error);
      return { conversations: [] };
    }
  }

  private getFileExtension(filename: string): string {
    if (!filename) return 'file';
    
    const ext = filename.toLowerCase().split('.').pop();
    switch (ext) {
      case 'pdf': return 'pdf';
      case 'doc':
      case 'docx': return 'doc';
      case 'xls':
      case 'xlsx': return 'xls';
      case 'ppt':
      case 'pptx': return 'ppt';
      default: return 'file';
    }
  }

  private formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }

  setUserId(userId: string) {
    this.currentUserId = userId;
  }

  clearUserData() {
    this.currentUserId = null;
  }

  async getCurrentUserId(): Promise<string | null> {
    // If we have a cached user ID, return it
    if (this.currentUserId) {
      return this.currentUserId;
    }

    // Try to get user ID from stored user data
    try {
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        const userData = JSON.parse(storedUser);
        console.log('Stored user data:', userData);
        if (userData.id) {
          this.currentUserId = userData.id;
          console.log('Using stored user ID:', userData.id);
          return userData.id;
        }
      }

      // If no stored user data, try to fetch from auth service
      const token = localStorage.getItem('token');
      if (!token) {
        console.log('No token found');
        return null;
      }

      console.log('Fetching user data from API...');
      const response = await fetch('http://localhost:8000/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        console.log('API user data:', userData);
        if (userData.id) {
          this.currentUserId = userData.id;
          // Update stored user data
          localStorage.setItem('user', JSON.stringify(userData));
          console.log('Set user ID from API:', userData.id);
          return userData.id;
        }
      } else {
        console.log('API response not ok:', response.status);
      }
    } catch (error) {
      console.error('Error getting current user ID:', error);
    }

    return null;
  }
}

export const chatService = new ChatService();
