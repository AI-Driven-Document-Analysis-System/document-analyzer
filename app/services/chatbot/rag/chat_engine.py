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
            }

        except Exception as e:
            raise Exception(f"Error processing query: {str(e)}")

    async def process_streaming_query(self, query: str, conversation_id: Optional[str] = None,
                                      user_id: Optional[str] = None, search_mode: str = "standard",
                                      selected_document_ids: Optional[List[str]] = None) -> AsyncGenerator[Dict, None]:
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
            # Set document filter for Knowledge Base mode (same as process_query)
            if selected_document_ids:
                print(f"\nSTREAMING KNOWLEDGE BASE MODE: Searching within {len(selected_document_ids)} selected documents")
                print(f"Selected document IDs: {selected_document_ids}")
                self.enhanced_search.set_document_filter(selected_document_ids)
            else:
                print(f"\nSTREAMING FULL DATABASE MODE: Searching all documents")
                self.enhanced_search.set_document_filter(None)

            # Use enhanced search based on search mode (same as process_query)
            enhanced_docs = None
            if search_mode != "standard" or selected_document_ids:
                enhanced_docs = await self.enhanced_search.search(query, search_mode, k=5)
                
                if enhanced_docs:
                    print("Enhanced search results for streaming:")
                    for i, doc in enumerate(enhanced_docs):
                        doc_id = doc.metadata.get('document_id', 'MISSING')
                        filename = doc.metadata.get('filename', 'MISSING')
                        print(f"  {i+1}. Document ID: {doc_id} - File: {filename}")

            # Create streaming callback handler
            streaming_callback = AsyncStreamingCallbackHandler()
            callbacks = getattr(self.chain.llm, 'callbacks', [])
            all_callbacks = callbacks + [streaming_callback] if callbacks else [streaming_callback]
            
            # For streaming, use a simple QA chain that returns clean markdown
            from langchain.chains.question_answering import load_qa_chain
            from langchain.prompts import PromptTemplate
            
            # Create a simple streaming prompt that returns clean markdown
            streaming_prompt = PromptTemplate(
                template="""Answer the question using the provided documents. Format your response in clean markdown.

Documents:
{context}

Question: {question}

Use ### headings, **bold text**, - bullet points, and `code` formatting in your response.
Provide a comprehensive answer based on the documents. Do not include JSON formatting - just return clean markdown text.""",
                input_variables=["context", "question"]
            )
            
            # Create simple QA chain for streaming
            streaming_chain = load_qa_chain(self.chain.llm, chain_type="stuff", prompt=streaming_prompt)
            
            # Use enhanced docs or retrieve new ones
            if enhanced_docs:
                docs_to_use = enhanced_docs
            else:
                # Get documents from retriever
                docs_to_use = self.chain.retriever.get_relevant_documents(query)
            
            # Start streaming task
            task = asyncio.create_task(
                streaming_chain.ainvoke(
                    {"input_documents": docs_to_use, "question": query},
                    config={"callbacks": all_callbacks}
                )
            )

            # Send initial event to indicate processing has started
            yield {
                'type': 'start',
                'conversation_id': conversation_id,
                'data': 'Starting response generation...'
            }

            # Stream tokens as they are generated by the LLM in real-time
            async for token in streaming_callback.get_tokens():
                yield {
                    'type': 'token',
                    'conversation_id': conversation_id,
                    'data': token
                }

            # Wait for the complete result to get source documents
            result = await task
            
            # Get the actual response text
            response_text = result.get('output_text', '') if isinstance(result, dict) else str(result)
            
            # Now run a quick citation detection to find ONLY the sources actually used
            citation_prompt = f"""Given this response and the available documents, identify which specific document passages were actually referenced or used in the response.

Response: {response_text}

Available Documents:
"""
            for i, doc in enumerate(docs_to_use):
                citation_prompt += f"\n[{i}] {doc.metadata.get('filename', 'Unknown')}: {doc.page_content[:300]}...\n"
            
            citation_prompt += """
Return ONLY a JSON list of the documents that were actually used/referenced:
[{"source_id": 0, "quote": "exact passage used", "document_name": "filename.pdf"}]

If no specific documents were clearly referenced, return an empty list: []
"""

            # Quick LLM call to identify actual citations
            try:
                citation_result = await self.chain.llm.ainvoke(citation_prompt)
                citation_text = citation_result.content if hasattr(citation_result, 'content') else str(citation_result)
                
                # Parse the JSON response
                import json
                import re
                json_match = re.search(r'\[.*\]', citation_text, re.DOTALL)
                if json_match:
                    citations_data = json.loads(json_match.group())
                    sources = []
                    for citation in citations_data:
                        if isinstance(citation, dict) and 'source_id' in citation:
                            source_id = citation['source_id']
                            if 0 <= source_id < len(docs_to_use):
                                doc = docs_to_use[source_id]
                                sources.append({
                                    'quote': citation.get('quote', doc.page_content[:200] + "..."),
                                    'content': citation.get('quote', doc.page_content[:200] + "..."),
                                    'metadata': doc.metadata,
                                    'score': doc.metadata.get('score', 0),
                                    'title': doc.metadata.get('filename', 'Unknown Document'),
                                    'type': 'document'
                                })
                else:
                    # Fallback: no specific citations found
                    sources = []
                    
            except Exception as e:
                print(f"Citation detection failed: {e}")
                # Fallback: show no sources rather than all documents
                sources = []

            # Send source documents event
            yield {
                'type': 'sources',
                'conversation_id': conversation_id,
                'data': sources
            }
            
            # Send retrieved documents for RAGAS evaluation
            yield {
                'type': 'retrieved_docs',
                'conversation_id': conversation_id,
                'data': [
                    {
                        'content': doc.page_content,
                        'metadata': doc.metadata,
                        'score': doc.metadata.get('score', 0)
                    } for doc in docs_to_use
                ]
            }

            # Send completion event with full response and sources
            yield {
                'type': 'complete',
                'conversation_id': conversation_id,
                'data': {
                    'response': response_text,
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