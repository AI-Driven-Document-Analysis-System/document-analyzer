"""
Document Embedding Service

Automatically embeds documents into ChromaDB after OCR processing is complete.
Uses the same chunking strategy as the manual embedding script.
"""

import os
import sys
import uuid
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

# Add the app directory to Python path for imports
app_dir = os.path.join(os.path.dirname(__file__), '..')
if app_dir not in sys.path:
    sys.path.append(app_dir)

from services.chatbot.vector_db.chunking import DocumentChunker
from services.chatbot.vector_db.indexing import LangChainDocumentIndexer
from services.chatbot.vector_db.langchain_chroma import LangChainChromaStore
from core.database import db_manager

logger = logging.getLogger(__name__)

class DocumentEmbeddingService:
    """Service for automatically embedding documents into ChromaDB"""
    
    def __init__(self):
        """Initialize the embedding service with ChromaDB configuration"""
        # Use the same configuration as manual script
        self.db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'chroma_db')
        self.collection_name = "documents"
        self.chunk_size = 1000
        self.chunk_overlap = 200
        
        # Initialize components
        self.vectorstore = None
        self.chunker = None
        self.indexer = None
        
        logger.info(f"DocumentEmbeddingService initialized with ChromaDB path: {self.db_path}")
    
    def _initialize_components(self):
        """Lazy initialization of ChromaDB components"""
        if self.vectorstore is None:
            try:
                self.vectorstore = LangChainChromaStore(self.db_path, self.collection_name)
                self.chunker = DocumentChunker(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
                self.indexer = LangChainDocumentIndexer(self.vectorstore, self.chunker)
                logger.info("ChromaDB components initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB components: {str(e)}")
                raise
    
    def get_document_content_from_db(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve document content from PostgreSQL for embedding
        
        Args:
            document_id: UUID of the document
            
        Returns:
            Dictionary with document content and metadata, or None if not found
        """
        try:
            with db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Get document metadata and content
                    cursor.execute("""
                        SELECT 
                            d.id,
                            d.original_filename,
                            d.uploaded_by_user_id,
                            d.user_id,
                            d.upload_timestamp,
                            dc.extracted_text,
                            dc.searchable_content
                        FROM documents d
                        JOIN document_content dc ON d.id = dc.document_id
                        WHERE d.id = %s
                    """, (document_id,))
                    
                    result = cursor.fetchone()
                    if not result:
                        logger.warning(f"Document {document_id} not found in database")
                        return None
                    
                    return {
                        'id': str(result[0]),
                        'filename': result[1],
                        'user_id': str(result[3]),
                        'upload_date': result[4].isoformat() if result[4] else datetime.now().isoformat(),
                        'text': result[5] or result[6],  # Use extracted_text, fallback to searchable_content
                        'type': 'document'  # Generic type for uploaded documents
                    }
                
        except Exception as e:
            logger.error(f"Error retrieving document {document_id} from database: {str(e)}")
            return None
    
    def embed_document(self, document_id: str) -> Dict[str, Any]:
        """
        Embed a single document into ChromaDB
        
        Args:
            document_id: UUID of the document to embed
            
        Returns:
            Dictionary with embedding results
        """
        try:
            # Initialize components if needed
            self._initialize_components()
            
            # Get document content from database
            doc_data = self.get_document_content_from_db(document_id)
            if not doc_data:
                raise Exception(f"Document {document_id} not found or has no content")
            
            # Check if document has sufficient content for embedding
            if not doc_data['text'] or len(doc_data['text'].strip()) < 50:
                logger.warning(f"Document {document_id} has insufficient content for embedding")
                return {
                    'success': False,
                    'error': 'Insufficient content for embedding',
                    'chunks_created': 0
                }
            
            logger.info(f"Starting embedding for document: {doc_data['filename']} (ID: {document_id})")
            
            # Create embeddings using the indexer
            chunk_ids = self.indexer.index_document(doc_data)
            
            logger.info(f"Successfully embedded document {document_id}: {len(chunk_ids)} chunks created")
            
            return {
                'success': True,
                'document_id': document_id,
                'filename': doc_data['filename'],
                'chunks_created': len(chunk_ids),
                'chunk_ids': chunk_ids
            }
            
        except Exception as e:
            logger.error(f"Error embedding document {document_id}: {str(e)}")
            return {
                'success': False,
                'document_id': document_id,
                'error': str(e),
                'chunks_created': 0
            }
    
    def embed_document_async(self, document_id: str) -> None:
        """
        Asynchronously embed a document (for background processing)
        
        Args:
            document_id: UUID of the document to embed
        """
        try:
            result = self.embed_document(document_id)
            if result['success']:
                logger.info(f"Background embedding completed for document {document_id}: {result['chunks_created']} chunks")
            else:
                logger.error(f"Background embedding failed for document {document_id}: {result['error']}")
        except Exception as e:
            logger.error(f"Background embedding error for document {document_id}: {str(e)}")
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the ChromaDB collection
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            self._initialize_components()
            collection = self.vectorstore.client.get_collection(name=self.collection_name)
            count = collection.count()
            
            return {
                'collection_name': self.collection_name,
                'total_chunks': count,
                'db_path': self.db_path
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return {
                'collection_name': self.collection_name,
                'total_chunks': 0,
                'error': str(e)
            }
    
    def check_document_embedded(self, document_id: str) -> bool:
        """
        Check if a document is already embedded in ChromaDB
        
        Args:
            document_id: UUID of the document to check
            
        Returns:
            True if document has embeddings, False otherwise
        """
        try:
            self._initialize_components()
            collection = self.vectorstore.client.get_collection(name=self.collection_name)
            
            # Query for chunks with this document_id
            results = collection.get(
                where={"document_id": document_id},
                limit=1
            )
            
            return len(results['ids']) > 0
            
        except Exception as e:
            logger.error(f"Error checking if document {document_id} is embedded: {str(e)}")
            return False


# Global instance for use across the application
document_embedding_service = DocumentEmbeddingService()
