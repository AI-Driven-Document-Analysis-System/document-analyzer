"""
Universal Citation Chain - Works with ALL LLM providers (OpenAI, Groq, Claude, etc.)
This replaces the problematic structured output approach with robust JSON parsing.
"""

import json
import re
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryBufferMemory
from langchain.chains.question_answering import load_qa_chain
from langchain_core.retrievers import BaseRetriever

from ..schemas.citation_models import CitedAnswer, DocumentCitation


class UniversalCitationChain:
    """
    Universal citation chain that works with ANY LLM provider.
    Uses JSON parsing instead of structured output for maximum compatibility.
    """
    
    def __init__(self, llm: Any, retriever: BaseRetriever, memory_type: str = "window"):
        """
        Initialize the universal citation chain.
        
        Args:
            llm: Any LLM instance (OpenAI, Groq, Claude, etc.)
            retriever: Document retriever
            memory_type: "window" or "summary"
        """
        self.llm = llm
        self.retriever = retriever
        
        # Initialize memory
        if memory_type == "window":
            self.memory = ConversationBufferWindowMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key='answer',
                k=10
            )
        else:
            self.memory = ConversationSummaryBufferMemory(
                llm=llm,
                memory_key="chat_history",
                return_messages=True,
                output_key='answer',
                max_token_limit=1000
            )
        
        # Create simple citation prompt that actually works
        self.citation_prompt = PromptTemplate(
            template="""Answer using documents. Return JSON with MARKDOWN-FORMATTED answer.

Documents:
{formatted_docs}

Question: {question}

Use ### headings, **bold**, - bullets, `backticks` in your answer.

JSON format:
{{"answer": "### Topic\\n\\n**Key** points:\\n\\n- **Point 1**: Details", "citations": [{{"source_id": 0, "document_name": "doc.pdf", "quote": "quote"}}]}}""",
            input_variables=["formatted_docs", "chat_history", "question"]
        )
        
        # Fallback prompt for regular QA
        self.fallback_prompt = PromptTemplate(
            template="""Use the following pieces of context to answer the question at the end.

Context:
{context}

Chat History:
{chat_history}

Question: {question}

**IMPORTANT**: Format your answer with ### headings, **bold** terms, - bullet points, and `backticks` for technical terms.

Answer:""",
            input_variables=["context", "chat_history", "question"]
        )
    
    def _format_docs_with_ids(self, docs: List[Document]) -> str:
        """Format documents with source IDs for citation."""
        formatted = []
        for i, doc in enumerate(docs):
            filename = doc.metadata.get('filename', f'Document_{i}')
            content = doc.page_content
            formatted.append(f"Source ID: {i}\nDocument: {filename}\nContent: {content}\n")
        return "\n".join(formatted)
    
    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """
        Simple JSON extraction that handles malformed responses.
        """
        print(f"DEBUG: Raw response: {repr(response_text[:200])}")
        
        # Clean response aggressively
        clean_text = response_text.strip('\n\r\t "')
        
        # Remove markdown
        clean_text = re.sub(r'```json|```', '', clean_text).strip()
        
        # If it starts with just "answer", wrap it in braces
        if clean_text.startswith('"answer"'):
            clean_text = '{' + clean_text + '}'
        
        # Try simple JSON parsing
        try:
            result = json.loads(clean_text)
            print(f"DEBUG: JSON parsed successfully")
            return result
        except:
            print(f"DEBUG: JSON parsing failed, using fallback")
            print(f"DEBUG: Raw response text: {response_text[:500]}...")
            
            # Check if the response indicates no relevant information
            if any(phrase in response_text.lower() for phrase in [
                "no information", "not mentioned", "doesn't contain", "not found", 
                "cannot find", "no details", "not discussed", "not available",
                "couldn't find any information", "i couldn't find", "no relevant information",
                "documents seem to be focused on", "documents don't contain",
                "do not mention", "does not mention", "don't mention", "doesn't mention",
                "no mention of", "there is no mention", "but there is no mention",
                "documents do not", "provided documents do not", "the documents do not"
            ]):
                print(f"DEBUG: Detected 'no information' response")
                return {
                    "answer": "I couldn't find information about your question in the selected documents. The documents may not contain the specific details you're looking for, or you may need to select different documents that are more relevant to your query.",
                    "citations": []
                }
            else:
                print(f"DEBUG: Using technical error fallback")
                return {
                    "answer": "I found information in the documents but encountered a technical issue while formatting the response. Please try rephrasing your question or contact support if this continues.",
                    "citations": []
                }
    
    def _is_valid_quote(self, quote: str) -> bool:
        """Validate quote quality - very permissive."""
        if not quote or quote == 'No quote available':
            return False
        
        # Only reject if extremely short
        if len(quote.strip()) < 5:
            return False
        
        return True
    
    def _create_cited_answer(self, parsed_result: Dict[str, Any], documents: List[Document]) -> CitedAnswer:
        """Create CitedAnswer object from parsed JSON."""
        citations = []
        seen_quotes = set()
        
        for cit_data in parsed_result.get('citations', []):
            quote = cit_data.get('quote', '').strip()
            
            # Validate and deduplicate quotes
            if self._is_valid_quote(quote) and quote not in seen_quotes:
                seen_quotes.add(quote)
                citations.append(DocumentCitation(
                    source_id=cit_data.get('source_id', 0),
                    document_name=cit_data.get('document_name', 'Unknown'),
                    quote=quote
                ))
            else:
                print(f"DEBUG: Skipping invalid/duplicate quote: {quote[:50]}...")
        
        return CitedAnswer(
            answer=parsed_result.get('answer', ''),
            citations=citations,
            has_sources=len(citations) > 0
        )
    
    def _extract_cited_sources(self, cited_answer: CitedAnswer, original_docs: List[Document]) -> List[Dict]:
        """Extract source information with quotes."""
        sources = []
        
        for citation in cited_answer.citations:
            if 0 <= citation.source_id < len(original_docs):
                doc = original_docs[citation.source_id]
                sources.append({
                    'title': doc.metadata.get('filename', 'Unknown Document'),
                    'type': 'document',
                    'document_id': doc.metadata.get('document_id'),
                    'chunk_index': doc.metadata.get('chunk_index'),
                    'source_id': citation.source_id,
                    'quote': citation.quote,
                    'full_content': doc.page_content
                })
        
        return sources
    
    def _display_quoted_sources_in_terminal(self, sources: List[Dict]):
        """Display quoted sources in terminal for debugging."""
        if not sources:
            print("\n🔍 No sources were cited by the LLM")
            return
        
        print(f"\n📚 LLM CITED {len(sources)} SOURCE(S) WITH EXACT QUOTES:")
        print("=" * 60)
        
        for i, source in enumerate(sources, 1):
            filename = source.get('title', 'Unknown Document')
            quote = source.get('quote', 'No quote provided')
            
            print(f"\n📄 SOURCE {i}: {filename}")
            print(f"   📝 EXACT QUOTE USED:")
            print(f"   \"{quote}\"")
            print("-" * 40)
    
    async def arun_with_structured_citations(self, question: str, callbacks: Optional[List] = None) -> Dict[str, Any]:
        """Run with structured citations using universal JSON parsing."""
        all_callbacks = callbacks or []
        
        # Retrieve documents
        relevant_docs = self.retriever.get_relevant_documents(question)
        print(f"DEBUG: Retrieved {len(relevant_docs)} documents for universal citation")
        
        if not relevant_docs:
            return {
                "answer": "I don't have any relevant documents to answer this question.",
                "source_documents": [],
                "sources": [],
                "chat_history": self.memory.chat_memory.messages
            }
        
        # Format documents and chat history
        formatted_docs = self._format_docs_with_ids(relevant_docs)
        chat_history = "\n".join([f"{msg.type}: {msg.content}" for msg in self.memory.chat_memory.messages[-4:]])
        
        try:
            # Get LLM response
            prompt_text = self.citation_prompt.format(
                formatted_docs=formatted_docs,
                chat_history=chat_history,
                question=question
            )
            
            print(f"DEBUG: Sending universal citation prompt (length: {len(prompt_text)} chars)")
            
            try:
                if all_callbacks:
                    llm_response = await self.llm.ainvoke(prompt_text, config={"callbacks": all_callbacks})
                else:
                    llm_response = await self.llm.ainvoke(prompt_text)
                print(f"DEBUG: LLM invocation successful")
            except Exception as llm_error:
                print(f"DEBUG: LLM invocation failed: {llm_error}")
                raise llm_error
            
            try:
                # Extract response text
                if hasattr(llm_response, 'content'):
                    response_text = llm_response.content
                else:
                    response_text = str(llm_response)
                print(f"DEBUG: Response text extraction successful, length: {len(response_text)}")
            except Exception as extract_error:
                print(f"DEBUG: Response text extraction failed: {extract_error}")
                raise extract_error
            
            print(f"DEBUG: LLM response received, parsing JSON...")
            print(f"DEBUG: Response preview: {response_text[:200]}...")
            
            try:
                # Parse JSON response
                parsed_result = self._extract_json_from_response(response_text)
                print(f"DEBUG: JSON parsing successful")
                
                # Check if the answer indicates no relevant information
                answer = parsed_result.get('answer', '').lower()
                if any(phrase in answer for phrase in [
                    "no information", "not mentioned", "doesn't contain", "not found", 
                    "cannot find", "no details", "not discussed", "not available",
                    "based on the provided documents, there is no information"
                ]):
                    print(f"DEBUG: LLM indicates no relevant information found")
                    return {
                        "answer": "I couldn't find information about your question in the selected documents. The documents may not contain the specific details you're looking for, or you may need to select different documents that are more relevant to your query.",
                        "source_documents": [],
                        "sources": [],
                        "chat_history": self.memory.chat_memory.messages
                    }
                    
            except Exception as json_error:
                print(f"DEBUG: JSON parsing failed: {json_error}")
                raise json_error
            
            try:
                cited_result = self._create_cited_answer(parsed_result, relevant_docs)
                print(f"DEBUG: CitedAnswer creation successful")
            except Exception as cited_error:
                print(f"DEBUG: CitedAnswer creation failed: {cited_error}")
                raise cited_error
            
            print(f"DEBUG: Successfully parsed response with {len(cited_result.citations)} citations")
            
            # Extract sources with quotes
            actual_sources = self._extract_cited_sources(cited_result, relevant_docs)
            self._display_quoted_sources_in_terminal(actual_sources)
            
            # Get cited documents
            cited_docs = []
            for citation in cited_result.citations:
                if 0 <= citation.source_id < len(relevant_docs):
                    cited_docs.append(relevant_docs[citation.source_id])
            
            # Update memory
            self.memory.save_context({"input": question}, {"answer": cited_result.answer})
            
            return {
                "answer": cited_result.answer,
                "source_documents": cited_docs,
                "sources": actual_sources,
                "chat_history": self.memory.chat_memory.messages
            }
            
        except Exception as e:
            print(f"DEBUG: Universal citation failed: {e}")
            print(f"DEBUG: Falling back to regular QA")
            return await self.arun(question, callbacks)
    
    async def arun_with_documents(self, question: str, documents: List, callbacks: Optional[List] = None) -> Dict[str, Any]:
        """Run with pre-retrieved documents using universal citations."""
        all_callbacks = callbacks or []
        
        print(f"DEBUG: Using universal citations with {len(documents)} pre-retrieved documents")
        
        # Format documents and chat history
        formatted_docs = self._format_docs_with_ids(documents)
        chat_history = "\n".join([f"{msg.type}: {msg.content}" for msg in self.memory.chat_memory.messages[-4:]])
        
        try:
            # Get LLM response
            prompt_text = self.citation_prompt.format(
                formatted_docs=formatted_docs,
                chat_history=chat_history,
                question=question
            )
            
            print(f"DEBUG: Sending universal citation prompt for enhanced search (length: {len(prompt_text)} chars)")
            
            if all_callbacks:
                llm_response = await self.llm.ainvoke(prompt_text, config={"callbacks": all_callbacks})
            else:
                llm_response = await self.llm.ainvoke(prompt_text)
            
            # Extract response text
            if hasattr(llm_response, 'content'):
                response_text = llm_response.content
            else:
                response_text = str(llm_response)
            
            print(f"DEBUG: LLM response received, parsing JSON...")
            print(f"DEBUG: Response preview: {response_text[:200]}...")
            
            # Parse JSON response
            parsed_result = self._extract_json_from_response(response_text)
            cited_result = self._create_cited_answer(parsed_result, documents)
            
            print(f"DEBUG: Successfully parsed response with {len(cited_result.citations)} citations")
            
            # Extract sources with quotes
            actual_sources = self._extract_cited_sources(cited_result, documents)
            self._display_quoted_sources_in_terminal(actual_sources)
            
            # Get cited documents
            cited_docs = []
            for citation in cited_result.citations:
                if 0 <= citation.source_id < len(documents):
                    cited_docs.append(documents[citation.source_id])
            
            # Update memory
            self.memory.save_context({"input": question}, {"answer": cited_result.answer})
            
            return {
                "answer": cited_result.answer,
                "source_documents": cited_docs,
                "sources": actual_sources,
                "chat_history": self.memory.chat_memory.messages
            }
            
        except Exception as e:
            print(f"DEBUG: Universal citation with documents failed: {e}")
            print(f"DEBUG: Falling back to regular QA")
            return await self._arun_fallback(question, documents, callbacks)
    
    async def arun(self, question: str, callbacks: Optional[List] = None) -> Dict[str, Any]:
        """Regular QA without citations."""
        all_callbacks = callbacks or []
        
        # Retrieve documents
        relevant_docs = self.retriever.get_relevant_documents(question)
        
        # Create QA chain
        qa_chain = load_qa_chain(llm=self.llm, chain_type="stuff", verbose=False)
        
        try:
            if all_callbacks:
                result = await qa_chain.ainvoke(
                    {"input_documents": relevant_docs, "question": question},
                    config={"callbacks": all_callbacks}
                )
            else:
                result = await qa_chain.ainvoke({"input_documents": relevant_docs, "question": question})
            
            output_text = result.get("output_text", "")
            
            # Update memory
            self.memory.save_context({"input": question}, {"answer": output_text})
            
            return {
                "answer": output_text,
                "source_documents": relevant_docs,
                "sources": [],
                "chat_history": self.memory.chat_memory.messages
            }
            
        except Exception as e:
            print(f"ERROR: Regular QA failed: {e}")
            return {
                "answer": "I'm sorry, I encountered an error processing your question.",
                "source_documents": [],
                "sources": [],
                "chat_history": self.memory.chat_memory.messages
            }
    
    async def _arun_fallback(self, question: str, documents: List, callbacks: Optional[List] = None) -> Dict[str, Any]:
        """Fallback QA with pre-retrieved documents."""
        all_callbacks = callbacks or []
        
        qa_chain = load_qa_chain(llm=self.llm, chain_type="stuff", verbose=False)
        
        try:
            if all_callbacks:
                result = await qa_chain.ainvoke(
                    {"input_documents": documents, "question": question},
                    config={"callbacks": all_callbacks}
                )
            else:
                result = await qa_chain.ainvoke({"input_documents": documents, "question": question})
            
            output_text = result.get("output_text", "")
            
            # Update memory
            self.memory.save_context({"input": question}, {"answer": output_text})
            
            return {
                "answer": output_text,
                "source_documents": documents,
                "sources": [],
                "chat_history": self.memory.chat_memory.messages
            }
            
        except Exception as e:
            print(f"ERROR: Fallback QA failed: {e}")
            return {
                "answer": "I'm sorry, I encountered an error processing your question.",
                "source_documents": [],
                "sources": [],
                "chat_history": self.memory.chat_memory.messages
            }
    
    def get_memory(self) -> List[Any]:
        """Get conversation memory."""
        return self.memory.chat_memory.messages
