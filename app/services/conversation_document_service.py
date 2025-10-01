"""
Service for managing conversation document selections.
Handles saving and loading which documents are selected for each conversation.
"""

import logging
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.core.database import DatabaseManager
from app.db.models import ConversationDocumentSelection

logger = logging.getLogger(__name__)

class ConversationDocumentService:
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    async def save_conversation_document_selections(
        self, 
        conversation_id: str, 
        document_ids: List[str]
    ) -> bool:
        """
        Save the selected documents for a conversation.
        Replaces any existing selections for this conversation.
        
        Args:
            conversation_id: The conversation ID
            document_ids: List of document IDs to save as selected
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    # First, delete existing selections for this conversation
                    cursor.execute(
                        "DELETE FROM conversation_document_selections WHERE conversation_id = %s",
                        (conversation_id,)
                    )
                    
                    # Insert new selections
                    if document_ids:
                        insert_query = """
                            INSERT INTO conversation_document_selections 
                            (conversation_id, document_id, selected_at, created_at)
                            VALUES (%s, %s, %s, %s)
                        """
                        current_time = datetime.utcnow()
                        
                        for document_id in document_ids:
                            cursor.execute(insert_query, (
                                conversation_id,
                                document_id,
                                current_time,
                                current_time
                            ))
                    
                    conn.commit()
                    logger.info(f"Saved {len(document_ids)} document selections for conversation {conversation_id}")
                    return True
                    
        except Exception as e:
            logger.error(f"Error saving conversation document selections: {e}")
            return False
    
    async def get_conversation_document_selections(
        self, 
        conversation_id: str
    ) -> List[str]:
        """
        Get the selected document IDs for a conversation.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            List[str]: List of selected document IDs
        """
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT document_id 
                        FROM conversation_document_selections 
                        WHERE conversation_id = %s
                        ORDER BY selected_at ASC
                    """, (conversation_id,))
                    
                    logger.info(f"SQL Query executed for conversation {conversation_id}")
                    
                    results = cursor.fetchall()
                    logger.info(f"Raw database results: {results}")
                    
                    document_ids = [str(row[0]) for row in results]
                    logger.info(f"Processed document IDs: {document_ids}")
                    
                    logger.info(f"Retrieved {len(document_ids)} document selections for conversation {conversation_id}")
                    return document_ids
                    
        except Exception as e:
            logger.error(f"Error retrieving conversation document selections: {e}")
            return []
    
    async def add_document_to_conversation(
        self, 
        conversation_id: str, 
        document_id: str
    ) -> bool:
        """
        Add a single document to a conversation's selection.
        
        Args:
            conversation_id: The conversation ID
            document_id: The document ID to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    current_time = datetime.utcnow()
                    
                    cursor.execute("""
                        INSERT INTO conversation_document_selections 
                        (conversation_id, document_id, selected_at, created_at)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (conversation_id, document_id) DO NOTHING
                    """, (conversation_id, document_id, current_time, current_time))
                    
                    conn.commit()
                    logger.info(f"Added document {document_id} to conversation {conversation_id}")
                    return True
                    
        except Exception as e:
            logger.error(f"Error adding document to conversation: {e}")
            return False
    
    async def remove_document_from_conversation(
        self, 
        conversation_id: str, 
        document_id: str
    ) -> bool:
        """
        Remove a single document from a conversation's selection.
        
        Args:
            conversation_id: The conversation ID
            document_id: The document ID to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        DELETE FROM conversation_document_selections 
                        WHERE conversation_id = %s AND document_id = %s
                    """, (conversation_id, document_id))
                    
                    conn.commit()
                    logger.info(f"Removed document {document_id} from conversation {conversation_id}")
                    return True
                    
        except Exception as e:
            logger.error(f"Error removing document from conversation: {e}")
            return False
    
    async def clear_conversation_document_selections(
        self, 
        conversation_id: str
    ) -> bool:
        """
        Clear all document selections for a conversation.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM conversation_document_selections WHERE conversation_id = %s",
                        (conversation_id,)
                    )
                    
                    conn.commit()
                    logger.info(f"Cleared all document selections for conversation {conversation_id}")
                    return True
                    
        except Exception as e:
            logger.error(f"Error clearing conversation document selections: {e}")
            return False
