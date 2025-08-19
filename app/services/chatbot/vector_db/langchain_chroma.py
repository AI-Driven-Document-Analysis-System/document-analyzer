from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.schema import Document
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings



class LangChainChromaStore:
    """
    A wrapper class that integrates ChromaDB with LangChain for document storage and retrieval.
    
    This class provides a high-level interface for:
    - Storing documents with their embeddings in a persistent ChromaDB database
    - Performing similarity searches using LangChain's retriever interface
    - Managing document collections with metadata filtering
    - Converting the store to LangChain retrievers for use in chains
    """
    
    def __init__(self, persist_directory: str, collection_name: str = "documents",
                 embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize the LangChain ChromaDB store with persistent storage.
        
        Args:
            persist_directory (str): Directory path where ChromaDB will store its data
            collection_name (str): Name of the collection to use (default: "documents")
            embedding_model (str): Name of the SentenceTransformer model to use for embeddings
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embeddings = SentenceTransformerEmbeddings(model_name=embedding_model)
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.vectorstore = Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embeddings,
        )

    def add_documents(self, documents: List[Document], ids: Optional[List[str]] = None):
        """
        Add LangChain Document objects to the vector store.
        
        Args:
            documents (List[Document]): List of LangChain Document objects to add
            ids (Optional[List[str]]): Optional list of document IDs
            
        Returns:
            List[str]: List of document IDs that were added to the store
        """
        # Handle empty documents list to avoid unnecessary processing
        if not documents:
            return []
        return self.vectorstore.add_documents(documents, ids=ids)

    def similarity_search(self, query: str, k: int = 4,
                          filter: Optional[Dict] = None) -> List[Document]:
        """
        Perform similarity search and return the most similar documents.
        
        Args:
            query (str): The query text to search for similar documents
            k (int): Number of most similar documents to return (default: 4)
            filter (Optional[Dict]): Optional metadata filter to apply to the search
            
        Returns:
            List[Document]: List of LangChain Document objects most similar to the query
        """
        return self.vectorstore.similarity_search(query, k=k, filter=filter)

    def similarity_search_with_score(self, query: str, k: int = 4,
                                     filter: Optional[Dict] = None) -> List[tuple]:
        """
        Perform similarity search and return documents with their similarity scores.
        
        Args:
            query (str): The query text to search for similar documents
            k (int): Number of most similar documents to return (default: 4)
            filter (Optional[Dict]): Optional metadata filter to apply to the search
            
        Returns:
            List[tuple]: List of tuples containing (Document, score) pairs
        """
        return self.vectorstore.similarity_search_with_score(query, k=k, filter=filter)

    def as_retriever(self, search_type: str = "similarity", search_kwargs: Dict = None):
        """
        Convert the vector store to a LangChain retriever for use in chains.
        
        Args:
            search_type (str): Type of search to perform (default: "similarity")
            search_kwargs (Dict): Additional search parameters (default: {"k": 4})
            
        Returns:
            Retriever: LangChain retriever object that can be used in chains
        """
        # Set default search parameters if none provided
        if search_kwargs is None:
            search_kwargs = {"k": 4}
        return self.vectorstore.as_retriever(
            search_type=search_type,
            search_kwargs=search_kwargs
        )

    def delete_documents(self, ids: List[str]):
        self.vectorstore.delete(ids=ids)

    def cleanup(self):
        """
        Clean up resources to prevent file locking issues.
        
        This method resets the ChromaDB client to release any file handles
        and prevent issues when the application is shut down or restarted.
        """
        try:
            # Reset the ChromaDB client to release file handles
            if hasattr(self, 'vectorstore') and self.vectorstore:
                self.vectorstore._client.reset()
        except:
            # Ignore any errors during cleanup to prevent crashes
            pass