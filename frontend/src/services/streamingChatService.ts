// Streaming chat service for real-time responses with Knowledge Base support
export interface StreamingChatCallbacks {
  onToken?: (token: string) => void;
  onComplete?: (response: { response: string; conversation_id: string; sources: any[] }) => void;
  onError?: (error: string) => void;
  onStart?: () => void;
  onSources?: (sources: any[]) => void;
}

class StreamingChatService {
  private baseUrl = 'http://localhost:8000/api';

  async sendStreamingMessage(
    message: string,
    conversationId?: string,
    searchMode: 'standard' | 'rephrase' | 'multiple_queries' = 'standard',
    selectedDocumentIds?: string[], // Updated to use string[] for UUIDs
    selectedModel?: { provider: string; model: string; name: string },
    callbacks?: StreamingChatCallbacks
  ): Promise<void> {
    try {
      // Get user ID from localStorage (same as regular chat service)
      const storedUser = localStorage.getItem('user');
      if (!storedUser) {
        throw new Error('User not authenticated');
      }
      const userData = JSON.parse(storedUser);
      const userId = userData.id;

      const requestBody = {
        message,
        conversation_id: conversationId,
        user_id: userId,
        memory_type: 'window',
        search_mode: searchMode,
        selected_document_ids: selectedDocumentIds || null, // Pass selected documents for Knowledge Base
        llm_config: selectedModel ? {
          provider: selectedModel.provider,
          model: selectedModel.model,
          temperature: 0.7,
          streaming: true
        } : null
      };

      console.log('STREAMING: Sending request with selected documents:', selectedDocumentIds);
      console.log('STREAMING: Search mode:', searchMode);

      const response = await fetch(`${this.baseUrl}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body reader available');
      }

      let fullResponse = '';
      let sources: any[] = [];
      let currentConversationId = conversationId;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = new TextDecoder().decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.type === 'start') {
                console.log('STREAMING: Response generation started')
                callbacks?.onStart?.();
              } else if (data.type === 'token') {
                fullResponse += data.data;
                callbacks?.onToken?.(data.data);
              } else if (data.type === 'sources') {
                sources = data.data;
                console.log('STREAMING: Received sources:', sources.length)
                callbacks?.onSources?.(sources);
              } else if (data.type === 'complete') {
                currentConversationId = data.conversation_id;
                console.log('STREAMING: Response completed')
                callbacks?.onComplete?.({
                  response: fullResponse,
                  conversation_id: currentConversationId || '',
                  sources: sources
                });
              } else if (data.type === 'error') {
                console.error('STREAMING: Error received:', data.data)
                callbacks?.onError?.(data.data);
                return;
              }
            } catch (error) {
              // Skip invalid JSON lines
              console.warn('Invalid JSON in stream:', line);
            }
          }
        }
      }
    } catch (error) {
      console.error('STREAMING: Service error:', error);
      callbacks?.onError?.(error instanceof Error ? error.message : 'Unknown error occurred');
    }
  }

  // Helper method to get current user ID (same as regular chat service)
  private async getCurrentUserId(): Promise<string | null> {
    try {
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        const userData = JSON.parse(storedUser);
        return userData.id || null;
      }
      return null;
    } catch (error) {
      console.error('Error getting current user ID:', error);
      return null;
    }
  }
}

export const streamingChatService = new StreamingChatService();
