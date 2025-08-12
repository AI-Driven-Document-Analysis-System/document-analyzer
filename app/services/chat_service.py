from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

from .chatbot.vector_db.langchain_chroma import LangChainChromaStore
from .chatbot.vector_db.chunking import DocumentChunker
from .chatbot.vector_db.indexing import LangChainDocumentIndexer
from .chatbot.vector_db.embeddings import EmbeddingGenerator
from .chatbot.llm.llm_factory import LLMFactory
from .chatbot.chains.conversational_chain import CustomConversationalChain
from .chatbot.rag.chat_engine import LangChainChatEngine
from .chatbot.rag.conversation_manager import ConversationManager


class ChatbotService:
    """
    Main service class that orchestrates all chatbot components.

    This class serves as the central coordinator for the document analysis chatbot,
    managing the lifecycle and interactions between all components including:
    - Vector database operations
    - Document indexing and retrieval
    - Language model interactions
    - Conversation management
    - Chat engine operations
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the ChatbotService with configuration parameters.

        Args:
            config: Dictionary containing all configuration parameters:
                - vector_db_path: Path to ChromaDB storage
                - collection_name: ChromaDB collection name
                - chunk_size: Document chunk size
                - chunk_overlap: Chunk overlap size
                - embedding_model: Sentence transformer model name
                - max_history_length: Conversation history length
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Core components - initialized lazily
        self._vectorstore = None
        self._chunker = None
        self._indexer = None
        self._embedding_generator = None
        self._conversation_manager = None
        self._chat_engines = {}  # Cache chat engines per user/session

        # Component initialization flags
        self._initialized = False

    def initialize(self) -> None:
        """
        Initialize all core components of the chatbot system.

        This method sets up the vector database, document processing components,
        and other essential services. It should be called once during application
        startup to prepare the chatbot for use.
        """
        try:
            self.logger.info("Initializing ChatbotService...")

            self._vectorstore = LangChainChromaStore(
                persist_directory=self.config['vector_db_path'],
                collection_name=self.config.get('collection_name', 'documents'),
                embedding_model=self.config.get('embedding_model', 'all-MiniLM-L6-v2')
            )

            self._chunker = DocumentChunker(
                chunk_size=self.config.get('chunk_size', 1000),
                chunk_overlap=self.config.get('chunk_overlap', 200)
            )

            self._indexer = LangChainDocumentIndexer(
                vectorstore=self._vectorstore,
                chunker=self._chunker
            )

            self._embedding_generator = EmbeddingGenerator(
                model_name=self.config.get('embedding_model', 'all-MiniLM-L6-v2')
            )

            self._conversation_manager = ConversationManager(
                max_history_length=self.config.get('max_history_length', 10)
            )

            self._initialized = True
            self.logger.info("ChatbotService initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize ChatbotService: {str(e)}")
            raise

    def get_or_create_chat_engine(self, llm_config: Dict[str, Any],
                                  user_id: Optional[str] = None,
                                  memory_type: str = "window") -> LangChainChatEngine:
        """
        Get or create a chat engine for a specific user/session.

        This method manages chat engine instances, creating new ones as needed
        and reusing existing ones for the same user to maintain conversation state.

        Args:
            llm_config: Configuration for the language model:
                - provider: 'openai', 'gemini', 'groq', or 'llama'
                - api_key: API key for external providers
                - model: Model name
                - temperature: Generation temperature
                - streaming: Enable streaming responses
            user_id: Optional user identifier for engine caching
            memory_type: Type of conversation memory ('window' or 'summary')

        Returns:
            LangChainChatEngine: Configured chat engine ready for use
        """
        self._ensure_initialized()

        # Create cache key for this configuration
        cache_key = f"{user_id}_{llm_config.get('provider')}_{llm_config.get('model')}_{memory_type}"

        # Return existing engine if available
        if cache_key in self._chat_engines:
            return self._chat_engines[cache_key]

        try:
            # Create LLM based on provider
            llm = self._create_llm(llm_config)

            # Create retriever with optional user filtering
            retriever = self._create_retriever(user_id)

            # Create conversational chain
            chain = CustomConversationalChain(
                llm=llm,
                retriever=retriever,
                memory_type=memory_type
            )

            # Create chat engine
            chat_engine = LangChainChatEngine(chain)

            # Cache the engine
            self._chat_engines[cache_key] = chat_engine

            self.logger.info(f"Created new chat engine for user {user_id} with {llm_config.get('provider')} provider")
            return chat_engine

        except Exception as e:
            self.logger.error(f"Failed to create chat engine: {str(e)}")
            raise

    def index_document(self, document_data: Dict[str, Any]) -> List[str]:
        """
        Index a document in the vector database.

        Args:
            document_data: Document data dictionary containing text or layout_data

        Returns:
            List of chunk IDs that were indexed
        """
        self._ensure_initialized()
        return self._indexer.index_document(document_data)

    def delete_document(self, document_id: str) -> None:
        """
        Delete a document and all its chunks from the vector database.

        Args:
            document_id: Unique identifier of the document to delete
        """
        self._ensure_initialized()

        try:
            # Search for all chunks belonging to this document
            filter_criteria = {"document_id": document_id}
            documents = self._vectorstore.similarity_search(
                query="",
                k=1000,  # Large number to get all chunks
                filter=filter_criteria
            )

            if documents:
                # Extract chunk IDs and delete them
                chunk_ids = [doc.metadata.get('chunk_id') for doc in documents if doc.metadata.get('chunk_id')]
                if chunk_ids:
                    self._vectorstore.delete_documents(chunk_ids)
                    self.logger.info(f"Deleted document {document_id} with {len(chunk_ids)} chunks")
            else:
                self.logger.warning(f"No chunks found for document {document_id}")

        except Exception as e:
            self.logger.error(f"Failed to delete document {document_id}: {str(e)}")
            raise

    def search_documents(self, query: str, k: int = 4,
                         user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for documents similar to the query.

        Args:
            query: Search query text
            k: Number of results to return
            user_id: Optional user ID for filtering results

        Returns:
            List of document chunks with metadata and similarity scores
        """
        self._ensure_initialized()

        try:
            # Create filter for user-specific search if user_id provided
            search_filter = {"user_id": user_id} if user_id else None

            # Perform similarity search with scores
            results = self._vectorstore.similarity_search_with_score(
                query=query,
                k=k,
                filter=search_filter
            )

            # Format results for API response
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": float(score)
                })

            return formatted_results

        except Exception as e:
            self.logger.error(f"Failed to search documents: {str(e)}")
            raise

    def get_conversation_history(self, conversation_id: str) -> str:
        """
        Retrieve conversation history for a given conversation ID.

        Args:
            conversation_id: Unique conversation identifier

        Returns:
            Formatted conversation history
        """
        self._ensure_initialized()
        return self._conversation_manager.get_conversation_history(conversation_id)

    def clear_conversation(self, conversation_id: str) -> None:
        """
        Clear conversation history for a specific conversation.

        Args:
            conversation_id: Unique conversation identifier
        """
        # Clear from conversation manager
        if hasattr(self._conversation_manager, 'conversations'):
            self._conversation_manager.conversations.pop(conversation_id, None)

        # Clear from cached chat engines
        engines_to_remove = [key for key in self._chat_engines.keys() if conversation_id in key]
        for key in engines_to_remove:
            self._chat_engines[key].chain.clear_memory()

    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system statistics and health information.

        Returns:
            Dictionary containing system statistics
        """
        self._ensure_initialized()

        try:
            # Get vector database stats
            vectorstore_stats = {
                "collection_name": self.config.get('collection_name', 'documents'),
                "persist_directory": self.config['vector_db_path']
            }

            return {
                "initialized": self._initialized,
                "active_chat_engines": len(self._chat_engines),
                "vectorstore": vectorstore_stats,
                "config": {
                    "chunk_size": self.config.get('chunk_size', 1000),
                    "chunk_overlap": self.config.get('chunk_overlap', 200),
                    "embedding_model": self.config.get('embedding_model', 'all-MiniLM-L6-v2'),
                    "max_history_length": self.config.get('max_history_length', 10)
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Failed to get system stats: {str(e)}")
            return {"error": str(e), "initialized": self._initialized}

    def cleanup(self) -> None:
        """
        Clean up resources and connections.

        This method should be called during application shutdown to properly
        release database connections and other resources.
        """
        try:
            self.logger.info("Cleaning up ChatbotService...")

            # Clear chat engine cache
            self._chat_engines.clear()

            # Clean up vector store
            if self._vectorstore:
                self._vectorstore.cleanup()

            self._initialized = False
            self.logger.info("ChatbotService cleanup completed")

        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")

    def _ensure_initialized(self) -> None:
        """Ensure the service is initialized before use."""
        if not self._initialized:
            raise RuntimeError("ChatbotService not initialized. Call initialize() first.")

    def _create_llm(self, llm_config: Dict[str, Any]):
        """Create LLM instance based on configuration."""
        provider = llm_config.get('provider', 'openai').lower()

        if provider == 'openai':
            return LLMFactory.create_openai_llm(
                api_key=llm_config['api_key'],
                model=llm_config.get('model', 'gpt-3.5-turbo'),
                temperature=llm_config.get('temperature', 0.7),
                streaming=llm_config.get('streaming', False),
                callbacks=llm_config.get('callbacks')
            )
        elif provider == 'gemini':
            return LLMFactory.create_gemini_llm(
                api_key=llm_config['api_key'],
                model=llm_config.get('model', 'gemini-1.5-flash'),
                temperature=llm_config.get('temperature', 0.7),
                streaming=llm_config.get('streaming', False),
                callbacks=llm_config.get('callbacks')
            )
        elif provider == 'groq':
            return LLMFactory.create_groq_llm(
                api_key=llm_config['api_key'],
                model=llm_config.get('model', 'llama-3.1-8b-instant'),
                temperature=llm_config.get('temperature', 0.7),
                streaming=llm_config.get('streaming', False),
                callbacks=llm_config.get('callbacks')
            )
        elif provider == 'llama':
            return LLMFactory.create_llama_llm(
                model_path=llm_config['model_path'],
                temperature=llm_config.get('temperature', 0.7),
                max_tokens=llm_config.get('max_tokens', 1000),
                streaming=llm_config.get('streaming', False),
                callbacks=llm_config.get('callbacks')
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def _create_retriever(self, user_id: Optional[str] = None):
        """Create retriever with optional user filtering."""
        if user_id:
            # Create user-filtered retriever
            return self._vectorstore.as_retriever(
                search_kwargs={"filter": {"user_id": user_id}, "k": 4}
            )
        else:
            # Create general retriever
            return self._vectorstore.as_retriever(
                search_kwargs={"k": 4}
            )


# Singleton instance for global access
_chatbot_service_instance: Optional[ChatbotService] = None


def get_chatbot_service() -> ChatbotService:
    """
    Get the global ChatbotService instance.

    Returns:
        ChatbotService: The global chatbot service instance

    Raises:
        RuntimeError: If service hasn't been initialized
    """
    global _chatbot_service_instance
    if _chatbot_service_instance is None:
        raise RuntimeError("ChatbotService not initialized. Call initialize_chatbot_service() first.")
    return _chatbot_service_instance


def initialize_chatbot_service(config: Dict[str, Any]) -> ChatbotService:
    """
    Initialize the global ChatbotService instance.

    Args:
        config: Configuration dictionary for the chatbot service

    Returns:
        ChatbotService: The initialized chatbot service instance
    """
    global _chatbot_service_instance
    _chatbot_service_instance = ChatbotService(config)
    _chatbot_service_instance.initialize()
    return _chatbot_service_instance


def cleanup_chatbot_service() -> None:
    """Clean up the global ChatbotService instance."""
    global _chatbot_service_instance
    if _chatbot_service_instance:
        _chatbot_service_instance.cleanup()
        _chatbot_service_instance = None