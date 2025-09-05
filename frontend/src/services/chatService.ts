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
  private currentUserId = '550e8400-e29b-41d4-a716-446655440000'; // Valid UUID format

  async sendMessage(message: string, conversationId?: string): Promise<ChatResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
          user_id: "user-1",
          memory_type: 'window',
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
        conversation_id: conversationId || 'fallback-conv',
        sources: []
      };
    }
  }

  async getDocuments(): Promise<Document[]> {
    try {
      // Skip documents API call for now to avoid UUID errors
      return [];
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
      const response = await fetch(`${this.baseUrl}/chat/conversations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: this.currentUserId,
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
      const response = await fetch(`${this.baseUrl}/chat/conversations?user_id=${this.currentUserId}`);
      
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

  getCurrentUserId(): string {
    return this.currentUserId;
  }
}

export const chatService = new ChatService();
