/**
 * Service for managing conversation document selections
 * Handles saving and loading which documents are selected for each conversation
 */

const API_BASE_URL = "http://localhost:8000/api/chat";

export interface ConversationDocumentsResponse {
  status: string;
  document_ids: string[];
  conversation_id: string;
  document_count: number;
}

export interface SaveDocumentsResponse {
  status: string;
  message: string;
  conversation_id: string;
  document_count: number;
}

export class ConversationDocumentService {
  /**
   * Save the selected documents for a conversation
   */
  static async saveConversationDocuments(
    conversationId: string, 
    documentIds: number[]
  ): Promise<SaveDocumentsResponse> {
    try {
      // Filter out invalid IDs and convert to strings
      const validIds = documentIds.filter(id => !isNaN(id) && id !== null && id !== undefined);
      const stringIds = validIds.map(id => id.toString());
      
      console.log('🔍 Processing document IDs:', {
        original: documentIds,
        filtered: validIds,
        strings: stringIds
      });
      
      const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}/documents`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document_ids: stringIds
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('💾 Saved conversation documents:', {
        conversationId,
        documentCount: documentIds.length,
        response: data
      });
      
      return data;
    } catch (error) {
      console.error('❌ Error saving conversation documents:', error);
      throw error;
    }
  }

  /**
   * Get the selected documents for a conversation
   */
  static async getConversationDocuments(
    conversationId: string
  ): Promise<number[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}/documents`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ConversationDocumentsResponse = await response.json();
      
      // Convert the stored string IDs back to numbers
      console.log('Raw document IDs from database:', data.document_ids);
      
      const numberIds = data.document_ids
        .map(id => parseInt(id, 10))
        .filter(id => !isNaN(id));
      
      console.log('📄 Loaded conversation documents:', {
        conversationId,
        documentCount: numberIds.length,
        documentIds: numberIds,
        originalStrings: data.document_ids
      });
      
      return numberIds;
    } catch (error) {
      console.error('❌ Error loading conversation documents:', error);
      // Return empty array on error instead of throwing
      return [];
    }
  }

  /**
   * Clear all document selections for a conversation
   */
  static async clearConversationDocuments(
    conversationId: string
  ): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}/documents`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('🗑️ Cleared conversation documents:', {
        conversationId,
        response: data
      });
    } catch (error) {
      console.error('❌ Error clearing conversation documents:', error);
      throw error;
    }
  }
}
