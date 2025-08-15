from langchain.schema import BaseRetriever, Document
from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from ..vector_db.chroma_client import ChromaClient
from ..vector_db.embeddings import EmbeddingGenerator
from typing import List, Dict, Any, Optional


class ChromaRetriever(BaseRetriever):
    """
    A custom retriever that integrates ChromaDB with LangChain's retriever interface.
    
    This class implements LangChain's BaseRetriever interface to provide document
    retrieval functionality using ChromaDB as the underlying vector database. It
    supports similarity search with configurable parameters and score filtering.
    """
    
    def __init__(self, chroma_client: ChromaClient, embedding_generator: EmbeddingGenerator,
                 k: int = 4, score_threshold: float = 0.5):
        """
        Args:
            chroma_client (ChromaClient): The ChromaDB client for vector operations
            embedding_generator (EmbeddingGenerator): The embedding generator for query encoding
            k (int): Number of most similar documents to retrieve (default: 4)
            score_threshold (float): Minimum similarity score threshold for filtering results (default: 0.5)
        """
        super().__init__()
        self.chroma_client = chroma_client
        self.embedding_generator = embedding_generator
        self.k = k
        self.score_threshold = score_threshold

    def _get_relevant_documents(
            self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """
        Retrieve relevant documents for a given query.
        
        This method implements the core retrieval logic by:
        1. Generating embeddings for the query text
        2. Performing similarity search in ChromaDB
        3. Filtering results based on score threshold
        4. Converting results to LangChain Document objects
        
        Args:
            query (str): The search query text
            run_manager (CallbackManagerForRetrieverRun): LangChain callback manager for monitoring
            
        Returns:
            List[Document]: List of relevant documents with metadata and scores
        """
        # Generate embedding for the query text
        query_embedding = self.embedding_generator.generate_query_embedding(query)

        # Perform similarity search in ChromaDB
        results = self.chroma_client.query(
            query_embedding=query_embedding,
            n_results=self.k
        )

        # Convert ChromaDB results to LangChain Document objects
        documents = []
        for i in range(len(results['ids'][0])):
            # Filter results based on similarity score threshold
            if results['distances'][0][i] <= self.score_threshold:
                # Create LangChain Document with enhanced metadata
                doc = Document(
                    page_content=results['documents'][0][i],
                    metadata={
                        **results['metadatas'][0][i],  # Include original metadata
                        'score': 1 - results['distances'][0][i],  # Convert distance to similarity score
                        'chunk_id': results['ids'][0][i]  # Add chunk identifier
                    }
                )
                documents.append(doc)

        return documents

    async def _aget_relevant_documents(
            self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """
        Asynchronous version of document retrieval.
        
        This method provides async compatibility for LangChain's async interfaces.
        Currently delegates to the synchronous version since ChromaDB operations
        are handled synchronously.
        
        Args:
            query (str): The search query text
            run_manager (CallbackManagerForRetrieverRun): LangChain callback manager for monitoring
            
        Returns:
            List[Document]: List of relevant documents with metadata and scores
        """
        return self._get_relevant_documents(query, run_manager=run_manager)


class FilteredChromaRetriever(ChromaRetriever):
    """
    A specialized retriever that supports metadata filtering in addition to similarity search.
    
    This class extends ChromaRetriever to add metadata-based filtering capabilities.
    It allows for more precise document retrieval by combining vector similarity
    with metadata constraints (e.g., filtering by document type, user, date range).
    """
    
    def __init__(self, chroma_client: ChromaClient, embedding_generator: EmbeddingGenerator,
                 filters: Optional[Dict] = None, **kwargs):
        """
        Args:
            chroma_client (ChromaClient): The ChromaDB client for vector operations
            embedding_generator (EmbeddingGenerator): The embedding generator for query encoding
            filters (Optional[Dict]): Metadata filters to apply during retrieval
            **kwargs: Additional arguments passed to the parent ChromaRetriever
        """
        super().__init__(chroma_client, embedding_generator, **kwargs)
        # Store metadata filters for use during retrieval
        self.filters = filters or {}

    def _get_relevant_documents(
            self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """
        Retrieve relevant documents with metadata filtering.
        
        This method extends the base retrieval logic to include metadata filtering.
        It applies both similarity search and metadata constraints to provide
        more targeted document retrieval.
        
        Args:
            query (str): The search query text
            run_manager (CallbackManagerForRetrieverRun): LangChain callback manager for monitoring
            
        Returns:
            List[Document]: List of relevant documents that match both similarity and filter criteria
        """
        # Generate embedding for the query text
        query_embedding = self.embedding_generator.generate_query_embedding(query)

        # Perform similarity search with metadata filtering
        results = self.chroma_client.query(
            query_embedding=query_embedding,
            n_results=self.k,
            where=self.filters if self.filters else None  # Apply metadata filters if provided
        )

        # Convert ChromaDB results to LangChain Document objects
        documents = []
        for i in range(len(results['ids'][0])):
            # Filter results based on similarity score threshold
            if results['distances'][0][i] <= self.score_threshold:
                # Create LangChain Document with enhanced metadata
                doc = Document(
                    page_content=results['documents'][0][i],
                    metadata={
                        **results['metadatas'][0][i],  # Include original metadata
                        'score': 1 - results['distances'][0][i],  # Convert distance to similarity score
                        'chunk_id': results['ids'][0][i]  # Add chunk identifier
                    }
                )
                documents.append(doc)

        return documents