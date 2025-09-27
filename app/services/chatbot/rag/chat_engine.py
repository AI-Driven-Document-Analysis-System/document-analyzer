from langchain.schema import HumanMessage, AIMessage
from ..chains.universal_citation_chain import UniversalCitationChain
from ..callbacks.streaming_callback import AsyncStreamingCallbackHandler
from ..search.enhanced_search import EnhancedSearchEngine
from typing import Dict, Any, Optional, AsyncGenerator, List
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
    
    def __init__(self, llm, retriever, memory_type: str = "default"):
        """
        Args:
          llm: The LLM to use for the conversational chain
          retriever: The retriever to use for the conversational chain
          memory_type: The type of memory to use for the conversational chain (default: "default")
        """
        # Create universal citation chain with memory
        self.chain = UniversalCitationChain(
            llm=llm,
            retriever=retriever,
            memory_type=memory_type
        )
        # Store active conversations for potential future use
        self.conversations = {}
        # Initialize enhanced search engine
        self.enhanced_search = EnhancedSearchEngine(
            retriever=retriever,
            llm=llm
        )

    async def process_query(self, query: str, conversation_id: Optional[str] = None,
                            user_id: Optional[str] = None, search_mode: str = "standard", 
                            selected_document_ids: Optional[List[str]] = None) -> Dict[str, Any]:
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
            selected_document_ids (Optional[List[str]]): Document IDs to search within (Knowledge Base mode)
            
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
            # Set document filter for Knowledge Base mode
            if selected_document_ids:
                print(f"\n🔍 KNOWLEDGE BASE MODE: Searching within {len(selected_document_ids)} selected documents")
                print(f"Selected document IDs: {selected_document_ids}")
                print(f"Document ID types: {[type(doc_id) for doc_id in selected_document_ids]}")
                self.enhanced_search.set_document_filter(selected_document_ids)
            else:
                print(f"\n🔍 FULL DATABASE MODE: Searching all documents")
                self.enhanced_search.set_document_filter(None)
            
            # Processing query with search mode
            
            # Use enhanced search based on search mode OR if documents are selected
            if search_mode != "standard" or selected_document_ids:
                # Get enhanced search results (with document filtering if specified)
                enhanced_docs = await self.enhanced_search.search(query, search_mode, k=5)
                
                print(f"🔍 USING ENHANCED SEARCH: Retrieved {len(enhanced_docs)} documents")
                if enhanced_docs:
                    print("Enhanced search results (showing chunk metadata):")
                    for i, doc in enumerate(enhanced_docs):
                        doc_id = doc.metadata.get('document_id', 'MISSING')
                        filename = doc.metadata.get('filename', 'MISSING')
                        print(f"  {i+1}. CHUNK METADATA: {doc.metadata}")
                        print(f"      Document ID in metadata: {doc_id} - File: {filename}")
                        print(f"      Content preview: {doc.page_content[:100]}...")
                
                # Use enhanced documents directly with the chain
                callbacks = getattr(self.chain.llm, 'callbacks', None)
                result = await self.chain.arun_with_documents(query, enhanced_docs, callbacks=callbacks)
            else:
                # Use structured citations for accurate source tracking (only when no documents selected)
                print("🔍 USING REGULAR RETRIEVER: No document filtering")
                callbacks = getattr(self.chain.llm, 'callbacks', None)
                try:
                    result = await self.chain.arun_with_structured_citations(query, callbacks=callbacks)
                    print(f"DEBUG: Using structured citations, got {len(result.get('sources', []))} actual sources")
                except Exception as e:
                    print(f"DEBUG: Structured citations failed: {e}, falling back to regular method")
                    result = await self.chain.arun(query, callbacks=callbacks)
            
            # Got result from chain
            # Source documents processed

            # Use the sources from universal citations (these contain quotes)
            if 'sources' in result and result['sources']:
                # Use the actual sources identified by the LLM with quotes
                sources = result['sources']
                print(f"DEBUG: Using universal citation sources with quotes: {[s.get('title', 'Unknown') for s in sources]}")
            else:
                # Fallback to formatting all retrieved documents (no quotes)
                sources = []
                for doc in result["source_documents"]:
                    sources.append({
                        'content': doc.page_content[:200] + "...",  # Truncate content for display
                        'metadata': doc.metadata,
                        'score': doc.metadata.get('score', 0),  # Extract relevance score if available
                        'title': doc.metadata.get('filename', 'Unknown Document'),
                        'type': 'document'
                    })
                print(f"DEBUG: Using fallback sources (no quotes): {[s.get('title', 'Unknown') for s in sources]}")

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
            callbacks = getattr(self.chain.llm, 'callbacks', [])
            all_callbacks = callbacks + [streaming_callback] if callbacks else [streaming_callback]
            
            # Try structured citations first, fallback to regular if needed
            try:
                task = asyncio.create_task(
                    self.chain.arun_with_structured_citations(query, callbacks=all_callbacks)
                )
            except Exception as e:
                print(f"DEBUG: Structured citations not available for streaming: {e}")
                task = asyncio.create_task(
                    self.chain.arun(query, callbacks=all_callbacks)
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

            # Use the sources from structured citations if available, otherwise format documents
            if 'sources' in result and result['sources']:
                # Use the actual sources identified by the LLM
                sources = result['sources']
            else:
                # Fallback to formatting all retrieved documents
                sources = []
                for doc in result["source_documents"]:
                    sources.append({
                        'content': doc.page_content[:200] + "...",  # Truncate content for display
                        'metadata': doc.metadata,
                        'score': doc.metadata.get('score', 0),  # Extract relevance score if available
                        'title': doc.metadata.get('filename', 'Unknown Document'),
                        'type': 'document'
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