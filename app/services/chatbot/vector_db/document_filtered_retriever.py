"""
Document-filtered retriever that supports filtering by document IDs before semantic search
"""
from typing import List, Optional, Dict, Any
from langchain.schema import Document
from langchain.retrievers.base import BaseRetriever
from .langchain_chroma import LangChainChromaStore
import logging

logger = logging.getLogger(__name__)


class DocumentFilteredRetriever(BaseRetriever):
    """
    A custom retriever that filters by document IDs before performing semantic search.
    
    This retriever is designed to support Knowledge Base mode where users select
    specific documents and want to search only within those documents.
    """
    
    def __init__(self, vectorstore: LangChainChromaStore, document_ids: Optional[List[str]] = None, k: int = 4):
        """
        Initialize the document-filtered retriever.
        
        Args:
            vectorstore: The LangChainChromaStore instance
            document_ids: Optional list of document IDs to filter by
            k: Number of documents to retrieve
        """
        super().__init__()
        self.vectorstore = vectorstore
        self.document_ids = document_ids
        self.k = k
    
    def get_relevant_documents(self, query: str) -> List[Document]:
        """
        Retrieve relevant documents, optionally filtered by document IDs.
        
        Args:
            query: The search query
            
        Returns:
            List of relevant documents
        """
        try:
            if self.document_ids:
                logger.info(f"Performing document-filtered search for {len(self.document_ids)} documents")
                logger.info(f"Document IDs: {self.document_ids}")
                
                # Use the new document-filtered search method
                documents = self.vectorstore.similarity_search_by_documents(
                    query=query,
                    document_ids=self.document_ids,
                    k=self.k
                )
                
                logger.info(f"Document-filtered search returned {len(documents)} results")
                return documents
            else:
                logger.info("No document filter specified, using regular search")
                # Fall back to regular search if no document IDs specified
                return self.vectorstore.similarity_search(query, k=self.k)
                
        except Exception as e:
            logger.error(f"Error in document-filtered retrieval: {e}")
            # Fallback to regular search on error
            return self.vectorstore.similarity_search(query, k=self.k)
    
    async def aget_relevant_documents(self, query: str) -> List[Document]:
        """
        Async version of get_relevant_documents.
        
        Args:
            query: The search query
            
        Returns:
            List of relevant documents
        """
        # For now, just call the sync version
        # In a production system, you might want to implement true async retrieval
        return self.get_relevant_documents(query)
    
    def update_document_filter(self, document_ids: Optional[List[str]]):
        """
        Update the document IDs filter.
        
        Args:
            document_ids: New list of document IDs to filter by
        """
        self.document_ids = document_ids
        logger.info(f"Updated document filter to: {document_ids}")
