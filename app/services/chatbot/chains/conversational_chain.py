from langchain.chains import ConversationalRetrievalChain, RetrievalQAWithSourcesChain
from langchain.chains.question_answering import load_qa_chain
from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryBufferMemory
from langchain.prompts import PromptTemplate
from langchain.schema import BaseRetriever, Document
from typing import Any, Dict, List, Optional
from ..rag.prompt_templates import PromptTemplates
from ....core.langfuse_config import get_langfuse_callbacks, get_langfuse_config
from ..schemas.citation_models import CitedAnswer, DocumentCitation
import json
import re

class CustomConversationalChain:
    """
    A custom conversational chain implementation for document analysis and Q&A.
    
    This class provides a flexible conversational interface that combines:
    - A language model for text generation
    - A retriever for document retrieval
    - Configurable memory management (window-based or summary-based)
    - Custom prompt templates for specialized document analysis
    """
    
    def __init__(self, llm: Any, retriever: BaseRetriever, memory_type: str = "window"):
        """
        Args:
            llm (Any): The language model to use for text generation
            retriever (BaseRetriever): The retriever component for document retrieval
            memory_type (str): Type of memory to use - "window" for ConversationBufferWindowMemory
                              or "summary" for ConversationSummaryBufferMemory (default: "window")
        """
        self.llm = llm
        self.retriever = retriever
        
        # Don't use structured output - use regular LLM with JSON parsing
        # This approach works with ALL LLM providers (OpenAI, Groq, etc.)
        self.structured_llm = llm  # Use regular LLM, we'll parse JSON manually
        print(f"DEBUG: Using regular LLM with JSON parsing for universal compatibility")

        # Initialize memory based on the specified type
        if memory_type == "window":
            # Window-based memory keeps the last k conversation turns
            # This is efficient for short-term context but may lose older information
            self.memory = ConversationBufferWindowMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key='answer',
                k=10  # Keep last 10 conversation turns
            )
        elif memory_type == "summary":
            # Summary-based memory maintains a running summary of the conversation
            # This is better for long conversations but uses more computational resources
            self.memory = ConversationSummaryBufferMemory(
                llm=llm,
                memory_key="chat_history",
                return_messages=True,
                output_key='answer',
                max_token_limit=1000  # Limit summary to 1000 tokens
            )

        # Create citation prompt for JSON response (works with all LLM providers)
        self.citation_prompt = PromptTemplate(
            template="""You are a helpful assistant that provides accurate answers with exact source citations.

Document Sources:
{formatted_docs}

Chat History:
{chat_history}

Question: {question}

IMPORTANT INSTRUCTIONS:
1. Answer the question using ONLY the provided document sources
2. For each source you use, provide a SHORT but COMPLETE quote (max 120 characters)
3. Only cite sources that directly contributed to your answer
4. Ensure quotes are COMPLETE sentences or phrases, not fragments or broken text
5. Use the exact Source ID from the document sources above
6. Keep quotes concise but meaningful - avoid truncated text
7. If a concept spans multiple sentences, pick the most relevant complete sentence
8. IMPORTANT: Each citation must have a DIFFERENT quote - no duplicate quotes allowed
9. If you need multiple citations, find DIFFERENT text portions from the sources
10. CRITICAL: Quotes must be CLEAN and READABLE - no broken words, no "ad-" or "undercor-" fragments
11. CRITICAL: Copy quotes EXACTLY as they appear in the source - do not modify or truncate mid-word

RESPONSE FORMAT:
You MUST respond with ONLY a valid JSON object in this exact format:
{
  "answer": "Your answer here",
  "citations": [
    {
      "source_id": 0,
      "document_name": "Document Name.pdf",
      "quote": "Exact quote from the document"
    }
  ]
}

Do not include any text before or after the JSON. Only return the JSON object.""",
            input_variables=["formatted_docs", "chat_history", "question"]
        )
        
        # Keep the original prompt for fallback
        self.custom_prompt = PromptTemplate(
            template=PromptTemplates.CONVERSATIONAL_TEMPLATE,
            input_variables=["context", "chat_history", "question"]
        )

        # Create the retrieval QA chain with sources for accurate source tracking
        # This chain explicitly tracks which sources the LLM actually uses
        
        # Custom document prompt that uses 'source' field (now added to metadata)
        document_prompt = PromptTemplate(
            input_variables=["page_content", "source"],
            template="Content: {page_content}\nSource: {source}"
        )
        
        self.sources_chain = RetrievalQAWithSourcesChain.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=True,
            verbose=False,
            chain_type_kwargs={
                "document_prompt": document_prompt
            }
        )
        
        # Keep the conversational chain for memory management
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.retriever,
            memory=self.memory,
            return_source_documents=True,  # Include source documents in response
            combine_docs_chain_kwargs={"prompt": self.custom_prompt},  # Use custom prompt
            verbose=False  # Disable verbose logging to reduce terminal output
        )

    def _format_docs_with_ids(self, docs: List[Document]) -> str:
        """
        Format documents with source IDs for structured citation.
        
        Args:
            docs: List of LangChain Document objects
            
        Returns:
            Formatted string with numbered sources
        """
        formatted = []
        for i, doc in enumerate(docs):
            filename = doc.metadata.get('filename', 'Unknown Document')
            chunk_info = f"(Chunk {doc.metadata.get('chunk_index', 'N/A')})"
            formatted.append(
                f"Source ID: {i}\n"
                f"Document: {filename} {chunk_info}\n"
                f"Content: {doc.page_content}\n"
            )
        return "\n".join(formatted)
    
    def _extract_cited_sources(self, cited_answer: CitedAnswer, original_docs: List[Document]) -> List[Dict]:
        """
        Extract actual source information from LLM citations with exact quotes.
        
        Args:
            cited_answer: Structured answer with citations
            original_docs: Original documents that were provided to LLM
            
        Returns:
            List of formatted source information with quotes (deduplicated)
        """
        sources = []
        seen_quotes = set()  # Track unique quotes to avoid duplicates
        
        for citation in cited_answer.citations:
            # Get the actual document that was cited
            if 0 <= citation.source_id < len(original_docs):
                doc = original_docs[citation.source_id]
                quote = citation.quote.strip()
                
                # Skip duplicate quotes
                if quote in seen_quotes or quote == 'No quote available':
                    print(f"DEBUG: Skipping duplicate quote: {quote[:50]}...")
                    continue
                    
                seen_quotes.add(quote)
                sources.append({
                    'title': doc.metadata.get('filename', 'Unknown Document'),
                    'type': 'document',
                    'document_id': doc.metadata.get('document_id'),
                    'chunk_index': doc.metadata.get('chunk_index'),
                    'source_id': citation.source_id,
                    'quote': quote,  # Add the exact quote
                    'full_content': doc.page_content  # Add full content for verification
                })
        
        print(f"DEBUG: After deduplication: {len(sources)} unique sources from {len(cited_answer.citations)} citations")
        return sources
    
    def _is_valid_quote(self, quote: str) -> bool:
        """
        Validate if a quote is well-formed and readable.
        
        Args:
            quote: The quote text to validate
            
        Returns:
            bool: True if quote is valid, False if malformed
        """
        if not quote or quote == 'No quote available':
            return False
            
        # Check for broken words (fragments ending with -)
        if quote.count('-') > 2:  # Allow some hyphens but not excessive fragmentation
            return False
            
        # Check for very short fragments
        if len(quote.strip()) < 10:
            return False
            
        # Check for incomplete words at the end
        words = quote.strip().split()
        if len(words) > 0:
            last_word = words[-1]
            if last_word.endswith('-') or len(last_word) < 2:
                return False
                
        return True

    def _display_quoted_sources_in_terminal(self, sources: List[Dict]):
        """
        Display the quoted sources in terminal for debugging.
        
        Args:
            sources: List of source information with quotes
        """
        if not sources:
            print("\n🔍 No sources were cited by the LLM")
            return
            
        print(f"\n📚 LLM CITED {len(sources)} SOURCE(S) WITH EXACT QUOTES:")
        print("=" * 60)
        
        for i, source in enumerate(sources, 1):
            filename = source.get('title', 'Unknown Document')
            quote = source.get('quote', 'No quote provided')
            chunk_index = source.get('chunk_index', 'N/A')
            
            print(f"\n📄 SOURCE {i}: {filename}")
            print(f"   Chunk Index: {chunk_index}")
            print(f"   📝 EXACT QUOTE USED:")
            print(f"   \"{quote}\"")
            print("-" * 40)

    async def arun_with_structured_citations(self, question: str, callbacks: Optional[List] = None) -> Dict[str, Any]:
        """
        Run the chain with structured citations to get actual sources used.
        
        This method uses structured output to force the LLM to specify exactly
        which document chunks it used to generate the answer.
        
        Args:
            question (str): The user's question to process
            callbacks (Optional[List]): Optional list of callback handlers
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - answer: The generated response from the LLM
                - source_documents: List of actual source documents used
                - sources: Formatted source information
                - chat_history: Current conversation history
        """
        all_callbacks = callbacks or []
        
        # Always use JSON parsing approach (works with all LLM providers)
        print("DEBUG: Using JSON parsing approach for universal LLM compatibility")
        
        # Retrieve relevant documents
        relevant_docs = self.retriever.get_relevant_documents(question)
        print(f"DEBUG: Retrieved {len(relevant_docs)} documents for structured citation")
        
        if not relevant_docs:
            # No documents available, use general knowledge
            return {
                "answer": "I don't have any relevant documents to answer this question.",
                "source_documents": [],
                "sources": [],
                "chat_history": self.memory.chat_memory.messages
            }
        
        # Format documents with IDs for citation
        formatted_docs = self._format_docs_with_ids(relevant_docs)
        
        # Get chat history as string
        chat_history = "\n".join([f"{msg.type}: {msg.content}" for msg in self.memory.chat_memory.messages[-4:]])
        
        try:
            # Use structured LLM to get citations
            prompt_text = self.citation_prompt.format(
                formatted_docs=formatted_docs,
                chat_history=chat_history,
                question=question
            )
            print(f"DEBUG: Sending prompt to structured LLM (length: {len(prompt_text)} chars)")
            
            if all_callbacks:
                llm_response = await self.structured_llm.ainvoke(
                    prompt_text,
                    config={"callbacks": all_callbacks}
                )
            else:
                llm_response = await self.structured_llm.ainvoke(prompt_text)
            
            # Extract text content from LLM response
            if hasattr(llm_response, 'content'):
                response_text = llm_response.content
            else:
                response_text = str(llm_response)
            
            print(f"DEBUG: LLM returned response, parsing as JSON...")
            print(f"DEBUG: Response preview: {response_text[:200]}...")
            
            # Always parse as JSON (universal approach)
            import json
            try:
                # Clean the response text - remove any markdown formatting
                clean_text = response_text.strip()
                if clean_text.startswith('```json'):
                    clean_text = clean_text.replace('```json', '').replace('```', '').strip()
                elif clean_text.startswith('```'):
                    clean_text = clean_text.replace('```', '').strip()
                
                parsed_result = json.loads(clean_text)
                # Convert to CitedAnswer object
                citations = []
                
                # Handle citations field - could be string or array
                citations_data = parsed_result.get('citations', [])
                if isinstance(citations_data, str):
                        # LLM returned citations as string, try to parse it
                        try:
                            citations_data = json.loads(citations_data.replace("'", '"'))
                        except:
                            # If parsing fails, try eval as last resort
                            try:
                                citations_data = eval(citations_data)
                            except:
                                print(f"DEBUG: Failed to parse citations string: {citations_data}")
                                citations_data = []
                    
                    for cit in citations_data:
                        quote = cit.get('quote', 'No quote available').strip()
                        
                        # Validate quote quality - skip malformed quotes
                        if self._is_valid_quote(quote):
                            citations.append(DocumentCitation(
                                source_id=cit.get('source_id', 0),
                                document_name=cit.get('document_name', 'Unknown'),
                                quote=quote
                            ))
                        else:
                            print(f"DEBUG: Skipping malformed quote: {quote[:50]}...")
                    
                    cited_result = CitedAnswer(
                        answer=parsed_result.get('answer', ''),
                        citations=citations,
                        has_sources=len(citations) > 0
                    )
                    print(f"DEBUG: Successfully parsed string to CitedAnswer with {len(citations)} citations")
                except json.JSONDecodeError as je:
                    print(f"DEBUG: Failed to parse JSON from string: {je}")
                    raise ValueError("Invalid JSON in string response")
            
            # Validate that we have proper CitedAnswer object
            if not hasattr(cited_result, 'citations'):
                print(f"DEBUG: Invalid structured output, missing citations attribute")
                raise ValueError("Invalid structured output format")
            
            print(f"DEBUG: Final cited_result has {len(cited_result.citations)} citations")
            
            # Extract actual sources used with quotes
            actual_sources = self._extract_cited_sources(cited_result, relevant_docs)
            
            # Display the quoted sources in terminal
            self._display_quoted_sources_in_terminal(actual_sources)
            
            # Get only the documents that were actually cited
            cited_docs = []
            for citation in cited_result.citations:
                if 0 <= citation.source_id < len(relevant_docs):
                    cited_docs.append(relevant_docs[citation.source_id])
            
            print(f"\n✅ DEBUG: LLM cited {len(cited_docs)} out of {len(relevant_docs)} available documents")
            
            # Update memory
            self.memory.save_context(
                {"input": question},
                {"answer": cited_result.answer}
            )
            
            return {
                "answer": cited_result.answer,
                "source_documents": cited_docs,
                "sources": actual_sources,
                "chat_history": self.memory.chat_memory.messages
            }
            
        except Exception as e:
            print(f"DEBUG: Structured citation failed: {e}")
            print(f"DEBUG: Error type: {type(e).__name__}")
            
            # Check if it's a function call validation error
            error_str = str(e)
            if "tool_use_failed" in error_str or "Failed to call a function" in error_str:
                print("DEBUG: LLM generated invalid structured output format")
                if "failed_generation" in error_str:
                    # Try to extract the failed generation for debugging
                    try:
                        import re
                        match = re.search(r"'failed_generation': '(.+?)'\}", error_str)
                        if match:
                            failed_gen = match.group(1)
                            print(f"DEBUG: Failed generation preview: {failed_gen[:200]}...")
                    except:
                        pass
            
            print(f"DEBUG: Falling back to regular method")
            # Fallback to original method if structured output fails
            return await self.arun(question, callbacks)

    async def arun(self, question: str, callbacks: Optional[List] = None) -> Dict[str, Any]:
        """
        Asynchronously run the conversational chain with a question.
        
        This method is designed for asynchronous applications like web servers
        and real-time chat interfaces. It processes the question through the
        conversational chain and returns the generated answer along with
        supporting source documents and chat history.
        
        Args:
            question (str): The user's question to process
            callbacks (Optional[List]): Optional list of callback handlers
                                      for monitoring the generation process
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - answer: The generated response from the LLM
                - source_documents: List of source documents used for the response
                - chat_history: Current conversation history from memory
        """
        # Use callbacks as-is (Langfuse callbacks already merged in chat service)
        all_callbacks = callbacks or []
        
        # First check if we have relevant documents by doing a similarity search
        relevant_docs = self.retriever.get_relevant_documents(question)
        print(f"DEBUG: Retrieved {len(relevant_docs)} documents for question: {question}")
        
        # Debug: Add logging to see what's happening
        has_relevant_docs = False
        if relevant_docs:
            print(f"DEBUG: Found {len(relevant_docs)} relevant docs")
            try:
                # Use similarity search with score to get relevance scores
                scored_docs = self.retriever.vectorstore.similarity_search_with_score(question, k=3)
                print(f"DEBUG: Got {len(scored_docs)} scored docs")
                
                # Check if any document has a good similarity score (lower score = more similar)
                for doc, score in scored_docs:
                    print(f"DEBUG: Doc score: {score}")
                    if score < 1.5:  # Extremely permissive threshold for testing
                        has_relevant_docs = True
                        print(f"DEBUG: Document passed threshold with score {score}")
                        break
                        
            except Exception as e:
                print(f"DEBUG: Exception in similarity search: {e}")
                # Fallback: Always show sources if documents were retrieved
                has_relevant_docs = True
                print("DEBUG: Using fallback - showing sources")
        
        if has_relevant_docs:
            # Use LangChain's RetrievalQAWithSourcesChain for document-based questions
            if all_callbacks:
                sources_result = await self.sources_chain.ainvoke(
                    {"question": question},
                    config={"callbacks": all_callbacks}
                )
            else:
                sources_result = await self.sources_chain.ainvoke({"question": question})
            
            output_text = sources_result.get("answer") or sources_result.get("result", "")
            source_documents = sources_result.get("source_documents", [])
            # Limit to only the most relevant source
            if source_documents:
                source_documents = [source_documents[0]]
        else:
            # Use conversational chain for general knowledge questions
            if all_callbacks:
                conv_result = await self.chain.ainvoke(
                    {"question": question},
                    config={"callbacks": all_callbacks}
                )
            else:
                conv_result = await self.chain.ainvoke({"question": question})
            
            output_text = conv_result.get("answer") or conv_result.get("result", "")
            source_documents = []  # No sources for general knowledge
        
        # Update memory with the conversation
        self.memory.save_context(
            {"input": question},
            {"answer": output_text}
        )

        # Format the response with all relevant information
        return {
            "answer": output_text,
            "source_documents": source_documents,
            "sources": "",
            "chat_history": self.memory.chat_memory.messages
        }

    def run(self, question: str, callbacks: Optional[List] = None) -> Dict[str, Any]:
        """
        Synchronously run the conversational chain with a question.
        
        This method is suitable for synchronous applications and provides
        the same functionality as arun but in a blocking manner.
        
        Args:
            question (str): The user's question to process
            callbacks (Optional[List]): Optional list of callback handlers
                                      for monitoring the generation process
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - answer: The generated response from the LLM
                - source_documents: List of source documents used for the response
                - chat_history: Current conversation history from memory
        """
        # Use callbacks as-is (Langfuse callbacks already merged in chat service)
        all_callbacks = callbacks or []
        
        # First check if we have relevant documents by doing a similarity search
        relevant_docs = self.retriever.get_relevant_documents(question)
        print(f"DEBUG: Retrieved {len(relevant_docs)} documents for question: {question}")
        
        # Debug: Add logging to see what's happening
        has_relevant_docs = False
        if relevant_docs:
            print(f"DEBUG: Found {len(relevant_docs)} relevant docs")
            try:
                # Use similarity search with score to get relevance scores
                scored_docs = self.retriever.vectorstore.similarity_search_with_score(question, k=3)
                print(f"DEBUG: Got {len(scored_docs)} scored docs")
                
                # Check if any document has a good similarity score (lower score = more similar)
                for doc, score in scored_docs:
                    print(f"DEBUG: Doc score: {score}")
                    if score < 1.5:  # Extremely permissive threshold for testing
                        has_relevant_docs = True
                        print(f"DEBUG: Document passed threshold with score {score}")
                        break
                        
            except Exception as e:
                print(f"DEBUG: Exception in similarity search: {e}")
                # Fallback: Always show sources if documents were retrieved
                has_relevant_docs = True
                print("DEBUG: Using fallback - showing sources")
        
        if has_relevant_docs:
            # Use LangChain's RetrievalQAWithSourcesChain for document-based questions
            if all_callbacks:
                sources_result = self.sources_chain.invoke(
                    {"question": question},
                    config={"callbacks": all_callbacks}
                )
            else:
                sources_result = self.sources_chain.invoke({"question": question})
            
            output_text = sources_result.get("answer") or sources_result.get("result", "")
            source_documents = sources_result.get("source_documents", [])
            # Limit to only the most relevant source
            if source_documents:
                source_documents = [source_documents[0]]
        else:
            # Use conversational chain for general knowledge questions
            if all_callbacks:
                conv_result = self.chain.invoke(
                    {"question": question},
                    config={"callbacks": all_callbacks}
                )
            else:
                conv_result = self.chain.invoke({"question": question})
            
            output_text = conv_result.get("answer") or conv_result.get("result", "")
            source_documents = []  # No sources for general knowledge
        
        # Update memory with the conversation
        self.memory.save_context(
            {"input": question},
            {"answer": output_text}
        )

        # Format the response with all relevant information
        return {
            "answer": output_text,
            "source_documents": source_documents,
            "sources": "",
            "chat_history": self.memory.chat_memory.messages
        }

    def clear_memory(self):
        """
        Clear the conversation memory.

        This method resets the conversation history, allowing the RAG pipeline
        to start fresh without any previous context. Useful for starting new
        conversations or when memory management is needed.
        """
        self.memory.clear()

    def get_memory(self) -> List[Any]:
        """
        Retrieve the current conversation memory.

        Returns:
            List[Any]: List of conversation messages stored in memory
        """
        return self.memory.chat_memory.messages

    async def arun_with_documents(self, question: str, documents: List, callbacks: Optional[List] = None) -> Dict[str, Any]:
        """
        Asynchronously run the conversational chain with pre-retrieved documents using structured citations.
        
        This method is used when enhanced search has already retrieved specific documents
        and we want to use those documents directly with structured citations for quotes.
        
        Args:
            question (str): The user's question to process
            documents (List): Pre-retrieved documents to use for context
            callbacks (Optional[List]): Optional list of callback handlers
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - answer: The generated response from the LLM
                - source_documents: List of source documents used for the response
                - sources: Formatted source information with quotes
                - chat_history: Current conversation history from memory
        """
        all_callbacks = callbacks or []
        
        # Check if structured LLM is available
        if self.structured_llm is None:
            print("DEBUG: Structured LLM not available in arun_with_documents, using fallback")
            return await self._arun_with_documents_fallback(question, documents, callbacks)
        
        print(f"DEBUG: Using structured citations with {len(documents)} pre-retrieved documents")
        
        # Format documents with IDs for citation
        formatted_docs = self._format_docs_with_ids(documents)
        
        # Get chat history as string
        chat_history = "\n".join([f"{msg.type}: {msg.content}" for msg in self.memory.chat_memory.messages[-4:]])
        
        try:
            # Use structured LLM to get citations
            prompt_text = self.citation_prompt.format(
                formatted_docs=formatted_docs,
                chat_history=chat_history,
                question=question
            )
            print(f"DEBUG: Sending prompt to structured LLM for enhanced search (length: {len(prompt_text)} chars)")
            
            if all_callbacks:
                cited_result = await self.structured_llm.ainvoke(
                    prompt_text,
                    config={"callbacks": all_callbacks}
                )
            else:
                cited_result = await self.structured_llm.ainvoke(prompt_text)
            
            # Debug: Check if we got proper structured output
            print(f"DEBUG: Structured LLM returned type: {type(cited_result)}")
            
            # Handle case where LLM returns string instead of structured output
            if isinstance(cited_result, str):
                print(f"DEBUG: LLM returned string instead of structured output, attempting JSON parse")
                try:
                    parsed_result = json.loads(cited_result)
                    # Convert to CitedAnswer object
                    citations = []
                    
                    # Handle citations field - could be string or array
                    citations_data = parsed_result.get('citations', [])
                    if isinstance(citations_data, str):
                        # LLM returned citations as string, try to parse it
                        try:
                            citations_data = json.loads(citations_data.replace("'", '"'))
                        except:
                            # If parsing fails, try eval as last resort
                            try:
                                citations_data = eval(citations_data)
                            except:
                                print(f"DEBUG: Failed to parse citations string: {citations_data}")
                                citations_data = []
                    
                    for cit in citations_data:
                        quote = cit.get('quote', 'No quote available').strip()
                        
                        # Validate quote quality - skip malformed quotes
                        if self._is_valid_quote(quote):
                            citations.append(DocumentCitation(
                                source_id=cit.get('source_id', 0),
                                document_name=cit.get('document_name', 'Unknown'),
                                quote=quote
                            ))
                        else:
                            print(f"DEBUG: Skipping malformed quote: {quote[:50]}...")
                    
                    cited_result = CitedAnswer(
                        answer=parsed_result.get('answer', ''),
                        citations=citations,
                        has_sources=len(citations) > 0
                    )
                    print(f"DEBUG: Successfully parsed string to CitedAnswer with {len(citations)} citations")
                except json.JSONDecodeError as je:
                    print(f"DEBUG: Failed to parse JSON from string: {je}")
                    raise ValueError("Invalid JSON in string response")
            
            # Validate that we have proper CitedAnswer object
            if not hasattr(cited_result, 'citations'):
                print(f"DEBUG: Invalid structured output, missing citations attribute")
                raise ValueError("Invalid structured output format")
            
            print(f"DEBUG: Final cited_result has {len(cited_result.citations)} citations")
            
            # Extract actual sources used with quotes
            actual_sources = self._extract_cited_sources(cited_result, documents)
            
            # Display the quoted sources in terminal
            self._display_quoted_sources_in_terminal(actual_sources)
            
            # Get only the documents that were actually cited
            cited_docs = []
            for citation in cited_result.citations:
                if 0 <= citation.source_id < len(documents):
                    cited_docs.append(documents[citation.source_id])
            
            print(f"✅ DEBUG: LLM cited {len(cited_docs)} out of {len(documents)} available documents")
            
            # Update memory
            self.memory.save_context(
                {"input": question},
                {"answer": cited_result.answer}
            )
            
            return {
                "answer": cited_result.answer,
                "source_documents": cited_docs,
                "sources": actual_sources,
                "chat_history": self.memory.chat_memory.messages
            }
            
        except Exception as e:
            print(f"DEBUG: Structured citation failed in arun_with_documents: {e}")
            print(f"DEBUG: Error type: {type(e).__name__}")
            print(f"DEBUG: Falling back to regular method")
            # Fallback to original method if structured output fails
            return await self._arun_with_documents_fallback(question, documents, callbacks)
    
    async def _arun_with_documents_fallback(self, question: str, documents: List, callbacks: Optional[List] = None) -> Dict[str, Any]:
        """Fallback method for arun_with_documents when structured citations fail."""
        all_callbacks = callbacks or []
        
        # Create a simple QA chain that works directly with documents
        qa_chain = load_qa_chain(
            llm=self.llm,
            chain_type="stuff",
            verbose=False
        )
        
        try:
            if all_callbacks:
                result = await qa_chain.ainvoke(
                    {"input_documents": documents, "question": question},
                    config={"callbacks": all_callbacks}
                )
            else:
                result = await qa_chain.ainvoke(
                    {"input_documents": documents, "question": question}
                )
            
            output_text = result.get("output_text", "")
            source_documents = documents  # Use the enhanced documents as sources
            
        except Exception as e:
            print(f"Error in _arun_with_documents_fallback: {e}")
            # Fallback to regular arun if there's an issue
            return await self.arun(question, callbacks)
        
        # Update memory with the conversation
        self.memory.save_context(
            {"input": question},
            {"answer": output_text}
        )

        # Format the response with all relevant information
        return {
            "answer": output_text,
            "source_documents": source_documents,
            "sources": "",
            "chat_history": self.memory.chat_memory.messages
        }