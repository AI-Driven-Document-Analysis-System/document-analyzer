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
        # Use SentenceTransformer for consistent embedding across indexing and retrieval
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

    def similarity_search_by_documents(self, query: str, document_ids: List[str], k: int = 4) -> List[Document]:
        """
        Perform similarity search filtered by specific document IDs.
        
        This method filters chunks to only those belonging to the specified documents
        before performing semantic search, which is more efficient than searching
        the entire vector DB and then filtering.
        
        Args:
            query (str): The query text to search for similar documents
            document_ids (List[str]): List of document IDs to filter by
            k (int): Number of most similar documents to return (default: 4)
            
        Returns:
            List[Document]: List of LangChain Document objects from specified documents
        """
        if not document_ids:
            # If no document IDs specified, fall back to regular search
            return self.similarity_search(query, k=k)
        
        print(f"\n🔍 VECTOR DB FILTERING:")
        print(f"Query: '{query}'")
        print(f"Document IDs to filter by: {document_ids}")
        print(f"Document ID types: {[type(doc_id) for doc_id in document_ids]}")
        
        # Create filter for document IDs
        # ChromaDB supports filtering with $in operator for multiple values
        filter_dict = {
            "document_id": {"$in": document_ids}
        }
        
        print(f"ChromaDB filter: {filter_dict}")
        
        results = self.vectorstore.similarity_search(query, k=k, filter=filter_dict)
        
        print(f"Filtered search returned {len(results)} results")
        if results:
            print("✅ FILTERED RESULTS:")
            for i, doc in enumerate(results):
                doc_id = doc.metadata.get('document_id', 'MISSING')
                filename = doc.metadata.get('filename', 'MISSING')
                source = doc.metadata.get('source', 'MISSING')
                print(f"  {i+1}. Document ID: {doc_id} (type: {type(doc_id)}) - File: {filename} - Source: {source}")
                print(f"      Full metadata: {doc.metadata}")
                print(f"      Content preview: {doc.page_content[:100]}...")
                
            # Check if any results match our expected document ID
            expected_ids = set(document_ids)
            actual_ids = set(doc.metadata.get('document_id', 'MISSING') for doc in results)
            print(f"\n🔍 ID COMPARISON:")
            print(f"Expected document IDs: {expected_ids}")
            print(f"Actual document IDs in results: {actual_ids}")
            print(f"Match: {expected_ids.intersection(actual_ids)}")
            print(f"Mismatch: {expected_ids - actual_ids}")
        else:
            print("❌ NO RESULTS FOUND - This indicates the filter is not working!")
            
            # Let's try a regular search to see what document IDs exist
            print("\n🔍 DEBUG: Trying regular search to see available document IDs...")
            regular_results = self.vectorstore.similarity_search(query, k=k)
            print(f"Regular search returned {len(regular_results)} results")
            if regular_results:
                print("Available document IDs in vector DB:")
                seen_ids = set()
                for doc in regular_results:
                    doc_id = doc.metadata.get('document_id', 'MISSING')
                    filename = doc.metadata.get('filename', 'MISSING')
                    source = doc.metadata.get('source', 'MISSING')
                    print(f"  - Full metadata: {doc.metadata}")
                    if doc_id not in seen_ids:
                        seen_ids.add(doc_id)
                        print(f"  - Document ID: {doc_id} (type: {type(doc_id)}) - File: {filename} - Source: {source}")
                        
            # Let's also try different filter approaches
            print("\n🔍 DEBUG: Trying alternative filter approaches...")
            
            # Try with different metadata field names
            alternative_filters = [
                {"doc_id": {"$in": document_ids}},
                {"id": {"$in": document_ids}},
                {"source": {"$in": [f"{doc_id}.pdf" for doc_id in document_ids]}},
            ]
            
            for i, alt_filter in enumerate(alternative_filters):
                print(f"Trying alternative filter {i+1}: {alt_filter}")
                try:
                    alt_results = self.vectorstore.similarity_search(query, k=k, filter=alt_filter)
                    print(f"Alternative filter {i+1} returned {len(alt_results)} results")
                    if alt_results:
                        print("✅ This filter worked!")
                        break
                except Exception as e:
                    print(f"Alternative filter {i+1} failed: {e}")
        
        return results

    def similarity_search_by_documents_with_score(self, query: str, document_ids: List[str], k: int = 4) -> List[tuple]:
        """
        Perform similarity search filtered by specific document IDs with scores.
        
        Args:
            query (str): The query text to search for similar documents
            document_ids (List[str]): List of document IDs to filter by
            k (int): Number of most similar documents to return (default: 4)
            
        Returns:
            List[tuple]: List of tuples containing (Document, score) pairs from specified documents
        """
        if not document_ids:
            # If no document IDs specified, fall back to regular search
            return self.similarity_search_with_score(query, k=k)
        
        # Create filter for document IDs
        filter_dict = {
            "document_id": {"$in": document_ids}
        }
        
        return self.vectorstore.similarity_search_with_score(query, k=k, filter=filter_dict)

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