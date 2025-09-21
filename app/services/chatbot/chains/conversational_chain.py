from langchain.chains import ConversationalRetrievalChain, RetrievalQAWithSourcesChain
from langchain.chains.question_answering import load_qa_chain
from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryBufferMemory
from langchain.prompts import PromptTemplate
from langchain.schema import BaseRetriever
from typing import Any, Dict, List, Optional
from ..rag.prompt_templates import PromptTemplates
from ....core.langfuse_config import get_langfuse_callbacks, get_langfuse_config

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

        # Define custom prompt template for document analysis
        # This prompt is specifically designed for document Q&A with context awareness
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
        Asynchronously run the conversational chain with pre-retrieved documents.
        
        This method is used when enhanced search has already retrieved specific documents
        and we want to use those documents directly instead of the retriever.
        
        Args:
            question (str): The user's question to process
            documents (List): Pre-retrieved documents to use for context
            callbacks (Optional[List]): Optional list of callback handlers
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - answer: The generated response from the LLM
                - source_documents: List of source documents used for the response
                - chat_history: Current conversation history from memory
        """
        # Use callbacks as-is (Langfuse callbacks already merged in chat service)
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
            print(f"Error in arun_with_documents: {e}")
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