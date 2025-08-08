import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
import uuid


class ChromaClient:
    """
    A wrapper class for ChromaDB operations that provides a simplified interface
    for document storage, retrieval, and management in a vector database.
    
    This class handles:
    - Persistent ChromaDB client initialization
    - Collection management (creation and retrieval)
    - Document addition with metadata
    - Vector similarity search queries
    - Document deletion
    - Collection information retrieval
    """
    
    def __init__(self, db_path: str, collection_name: str):
        """
        Args:
            db_path (str): Path to the persistent ChromaDB storage directory
            collection_name (str): Name of the collection to work with
        """
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection_name = collection_name
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        """
        Retrieve an existing collection or create a new one if it doesn't exist.
        
        Returns:
            Collection: The ChromaDB collection object
        """
        try:
            # Try to get an existing collection
            return self.client.get_collection(name=self.collection_name)
        except:
            # If collection doesn't exist, create a new one with default settings
            import chromadb.utils.embedding_functions as embedding_functions
            embedding_function = embedding_functions.DefaultEmbeddingFunction()
            return self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
                embedding_function=embedding_function
            )

    def add_documents(self, documents: List[str], metadatas: List[Dict],
                      ids: Optional[List[str]] = None):
        """
        Args:
            documents (List[str]): List of document texts to add
            metadatas (List[Dict]): List of metadata dictionaries for each document
            ids (Optional[List[str]]): Optional list of document IDs. If not provided, UUIDs will be generated
            
        Returns:
            List[str]: List of document IDs (either provided or generated)
        """
        # Generate UUIDs for documents if no IDs are provided
        if not ids:
            ids = [str(uuid.uuid4()) for _ in documents]

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        return ids

    def query(self, query_text: str, n_results: int = 5,
              where: Optional[Dict] = None):
        """
        Perform a similarity search query on the collection.
        
        Args:
            query_text (str): The text to search for similar documents
            n_results (int): Number of most similar results to return (default: 5)
            where (Optional[Dict]): Optional filter conditions for metadata
            
        Returns:
            Dict: Query results containing documents, metadata, distances, and IDs
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where
        )
        return results

    def delete_document(self, document_id: str):
        self.collection.delete(ids=[document_id])

    def get_collection_info(self):
        return {
            "count": self.collection.count(),
            "name": self.collection.name
        }