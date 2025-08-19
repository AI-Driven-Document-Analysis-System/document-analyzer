
from .langchain_chroma import LangChainChromaStore
from langchain.schema import Document
from .chunking import DocumentChunker
from typing import Dict, List
import logging


class LangChainDocumentIndexer:
    """
    A document indexer that processes and stores documents in a vector database.
    
    This class orchestrates the complete document indexing pipeline:
    1. Document chunking using either layout-based or sentence-based strategies
    2. Metadata cleaning and preparation for vector database compatibility
    3. Conversion to LangChain Document objects
    4. Storage in the vector database with embeddings
    
    The indexer supports both structured documents (with layout data) and
    plain text documents, automatically choosing the appropriate chunking strategy.
    """
    
    def __init__(self, vectorstore: LangChainChromaStore, chunker: DocumentChunker):
        """
        Initialize the document indexer with vector store and chunker components.
        
        Args:
            vectorstore: The vector database store for storing document chunks
            chunker: The document chunker for splitting documents into manageable pieces
        """
        self.vectorstore = vectorstore
        self.chunker = chunker
        self.logger = logging.getLogger(__name__)

    def _clean_metadata(self, metadata: Dict) -> Dict:
        """
        Clean metadata values to be compatible with ChromaDB.
        
        ChromaDB only accepts str, int, float, or bool values. This method
        converts incompatible data types to string representations to ensure
        successful storage in the vector database.
        
        Args:
            metadata: Original metadata dictionary with potentially incompatible values
            
        Returns:
            Cleaned metadata dictionary with ChromaDB-compatible values
        """
        cleaned_metadata = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                # These types are already compatible with ChromaDB
                cleaned_metadata[key] = value
            elif isinstance(value, list):
                # Convert lists to string representation for storage
                cleaned_metadata[key] = str(value)
            elif isinstance(value, dict):
                # Convert dictionaries to string representation for storage
                cleaned_metadata[key] = str(value)
            elif value is None:
                # Convert None values to empty string to avoid null issues
                cleaned_metadata[key] = ""
            else:
                # Convert any other type to string for compatibility
                cleaned_metadata[key] = str(value)
        
        return cleaned_metadata

    def index_document(self, document_data: Dict) -> List[str]:
        """
        Index a document by chunking it and storing the chunks in the vector database.
        
        This method processes document data and creates vector embeddings for
        efficient retrieval. It supports both layout-based and sentence-based chunking.
        
        Args:
            document_data: Dictionary containing document information including:
                - id: Unique document identifier
                - type: Document type (optional)
                - filename: Original filename (optional)
                - upload_date: Upload timestamp (optional)
                - user_id: User identifier (optional)
                - layout_data: Structured layout data for layout-based chunking
                - text: Raw text content for sentence-based chunking
                
        Returns:
            List of chunk IDs that were stored in the vector database
            
        Raises:
            Exception: If indexing fails due to processing or storage errors
        """
        try:
            # ===== DOCUMENT METADATA PREPARATION =====
            # Extract and prepare document metadata for vector storage
            # This metadata will be attached to each chunk for traceability
            document_metadata = {
                'document_id': document_data['id'],
                'document_type': document_data.get('type', 'unknown'),
                'filename': document_data.get('filename', ''),
                'upload_date': document_data.get('upload_date', ''),
                'user_id': document_data.get('user_id', '')
            }

            # ===== CHUNKING STRATEGY SELECTION =====
            # Choose chunking strategy based on available data
            # Layout-based chunking preserves document structure and is preferred
            if 'layout_data' in document_data:
                # Use layout-based chunking when structured layout data is available
                # This preserves document formatting, tables, and spatial relationships
                chunks = self.chunker.chunk_by_layout(
                    document_data['layout_data'],
                    document_metadata
                )
            else:
                # Fallback to sentence-based chunking for plain text
                # This is used when only raw text content is available
                chunks = self.chunker.chunk_by_sentences(
                    document_data['text'],
                    document_metadata
                )

            # ===== LANGCHAIN DOCUMENT CONVERSION =====
            # Convert chunks to LangChain Document objects for vector storage
            # Each chunk becomes a separate Document with its own metadata
            documents = []
            for chunk in chunks:
                # Clean metadata to be compatible with ChromaDB
                cleaned_metadata = self._clean_metadata(chunk['metadata'])
                
                # Create LangChain Document object with chunk content and metadata
                doc = Document(
                    page_content=chunk['text'],
                    metadata=cleaned_metadata
                )
                documents.append(doc)

            # ===== VECTOR DATABASE STORAGE =====
            # Store documents in vector database and get their IDs
            # The vectorstore will create embeddings and store them for retrieval
            ids = self.vectorstore.add_documents(documents)
           
            self.logger.info(f"Indexed document {document_data['id']} with {len(chunks)} chunks")
            return ids

        except Exception as e:
            # Log error and re-raise for proper error handling upstream
            self.logger.error(f"Error indexing document {document_data['id']}: {str(e)}")
            raise