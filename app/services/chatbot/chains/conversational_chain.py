from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryBufferMemory
from langchain.prompts import PromptTemplate
from langchain.schema import BaseRetriever
from typing import Any, Dict, List, Optional


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
            template="""You are an intelligent document analysis assistant. Use the following pieces of context to answer the question at the end. If you don't know the answer based on the context, just say that you don't have enough information.

Context:
{context}

Chat History:
{chat_history}

Question: {question}
Answer:""",
            input_variables=["context", "chat_history", "question"]
        )

        # Create the conversational retrieval chain with custom configuration
        # This combines the LLM, retriever, memory, and custom prompt into a single pipeline
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.retriever,
            memory=self.memory,
            return_source_documents=True,  # Include source documents in response
            combine_docs_chain_kwargs={"prompt": self.custom_prompt},  # Use custom prompt
            verbose=True  # Enable verbose logging for debugging
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
        # Process the question through the conversational chain asynchronously
        result = await self.chain.ainvoke(
            {"question": question},
            callbacks=callbacks
        )

        # Format the response with all relevant information
        return {
            "answer": result["answer"],
            "source_documents": result["source_documents"],
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
        # Process the question through the conversational chain synchronously
        result = self.chain.invoke(
            {"question": question},
            callbacks=callbacks
        )

        # Format the response with all relevant information
        return {
            "answer": result["answer"],
            "source_documents": result["source_documents"],
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