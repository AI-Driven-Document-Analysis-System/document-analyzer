from langchain.schema import HumanMessage, AIMessage
from ..chains.conversational_chain import CustomConversationalChain
from ..callbacks.streaming_callback import AsyncStreamingCallbackHandler
from ..search.enhanced_search import EnhancedSearchEngine
from typing import Dict, Any, Optional, AsyncGenerator
import uuid
import json
import asyncio


class LangChainChatEngine:
    """
    A chat engine that provides both synchronous and streaming interfaces for document-based conversations.
    
    This class serves as a high-level interface for document Q&A interactions, offering:
    - Standard query processing with full response generation
    - Streaming query processing for real-time token-by-token responses
    - Conversation management with unique conversation IDs
    - Source document extraction and formatting
    - Error handling and graceful failure recovery
    
    The chat engine is designed to work with custom conversational chains
    and provides a unified interface for both web and streaming applications.
    """
    
    def __init__(self, conversational_chain: CustomConversationalChain):
        """
        Args:
            conversational_chain (CustomConversationalChain): The conversational chain
                                                           that handles the core RAG processing
        """
        self.chain = conversational_chain
        # Store active conversations for potential future use
        self.conversations = {}
        # Initialize enhanced search engine
        self.enhanced_search = EnhancedSearchEngine(
            retriever=conversational_chain.retriever,
            llm=conversational_chain.llm
        )

    async def process_query(self, query: str, conversation_id: Optional[str] = None,
                            user_id: Optional[str] = None, search_mode: str = "standard") -> Dict[str, Any]:
        """
        Process a query and return a complete response with sources.
        
        This method provides a standard synchronous-like interface for query processing.
        It generates the full response and returns it along with source documents
        and conversation history in a single response.
        
        Args:
            query (str): The user's question or query to process
            conversation_id (Optional[str]): Unique identifier for the conversation.
                                           If not provided, a new UUID will be generated
            user_id (Optional[str]): User identifier for tracking (currently unused)
            search_mode (str): Search mode ('standard', 'rephrase', 'multiple_queries')
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - conversation_id: Unique identifier for the conversation
                - response: The generated answer from the LLM
                - sources: List of source documents used for the response
                - chat_history: Current conversation history
                
        Raises:
            Exception: If query processing fails
        """
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = str(uuid.uuid4())

        try:
            print(f"DEBUG CHAT ENGINE: Processing query: {query} with search mode: {search_mode}")
            
            # Use enhanced search based on search mode
            if search_mode != "standard":
                # Get enhanced search results
                enhanced_docs = await self.enhanced_search.search(query, search_mode, k=5)
                
                # Create a custom chain result with enhanced documents
                # Instead of overriding retriever, we'll modify the chain's behavior
                result = await self.chain.arun(query)
                
                # Replace the source documents with enhanced search results
                result["source_documents"] = enhanced_docs
            else:
                # Standard processing
                result = await self.chain.arun(query)
            
            print(f"DEBUG CHAT ENGINE: Got result with keys: {result.keys()}")
            print(f"DEBUG CHAT ENGINE: Source documents count: {len(result.get('source_documents', []))}")

            # Extract and format source documents for the response
            sources = []
            for doc in result["source_documents"]:
                sources.append({
                    'content': doc.page_content[:200] + "...",  # Truncate content for display
                    'metadata': doc.metadata,
                    'score': doc.metadata.get('score', 0)  # Extract relevance score if available
                })

            # Format the complete response
            return {
                'conversation_id': conversation_id,
                'response': result["answer"],
                'sources': sources,
                'chat_history': [msg.dict() for msg in result["chat_history"]],
                'search_mode': search_mode
            }

        except Exception as e:
            raise Exception(f"Error processing query: {str(e)}")

    async def process_streaming_query(self, query: str,
                                      conversation_id: Optional[str] = None) -> AsyncGenerator[Dict, None]:
        """
        Process a query with streaming response generation.
        
        This method provides a streaming interface that yields tokens as they are generated,
        followed by source documents and completion information. This is ideal for
        real-time chat interfaces where users expect immediate feedback.
        
        Args:
            query (str): The user's question or query to process
            conversation_id (Optional[str]): Unique identifier for the conversation.
                                           If not provided, a new UUID will be generated
            
        Yields:
            Dict: Streaming events with the following types:
                - 'start': Initial event indicating response generation has begun
                - 'token': Individual tokens as they are generated by the LLM
                - 'sources': Source documents used for the response
                - 'complete': Final event with complete response and sources
                - 'error': Error event if processing fails
        """
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = str(uuid.uuid4())

        try:
            # Create streaming callback handler for token-by-token processing
            streaming_callback = AsyncStreamingCallbackHandler()

            # Start the query processing task asynchronously
            # This allows us to stream tokens while the full response is being generated
            task = asyncio.create_task(
                # streaming_callback.get_tokens() function gets "called back" every time the LLM generates a new token
                self.chain.arun(query, callbacks=[streaming_callback])
            )

            # Send initial event to indicate processing has started
            yield {
                'type': 'start',
                'conversation_id': conversation_id,
                'data': 'Starting response generation...'
            }

            # Stream tokens as they are generated by the LLM
            async for token in streaming_callback.get_tokens():
                yield {
                    'type': 'token',
                    'conversation_id': conversation_id,
                    'data': token
                }

            # Wait for the complete result to get source documents
            result = await task

            # Extract and format source documents
            sources = []
            for doc in result["source_documents"]:
                sources.append({
                    'content': doc.page_content[:200] + "...",  # Truncate content for display
                    'metadata': doc.metadata,
                    'score': doc.metadata.get('score', 0)  # Extract relevance score if available
                })

            # Send source documents event
            yield {
                'type': 'sources',
                'conversation_id': conversation_id,
                'data': sources
            }

            # Send completion event with full response and sources
            yield {
                'type': 'complete',
                'conversation_id': conversation_id,
                'data': {
                    'response': result["answer"],
                    'sources': sources
                }
            }

        except Exception as e:
            # Send error event if processing fails
            yield {
                'type': 'error',
                'conversation_id': conversation_id,
                'data': str(e)
            }