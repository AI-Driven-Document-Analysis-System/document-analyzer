from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseRetriever, Document
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema.messages import HumanMessage, AIMessage
from typing import List, Dict, Any, Optional
import asyncio


class LangChainRAGPipeline:

    def __init__(self, llm, retriever, memory_key: str = "chat_history"):
        """
        Initialize the RAG pipeline with language model, retriever, and memory components.
        
        Args:
            llm: The language model to use for text generation
            retriever: The retriever component for document retrieval
            memory_key (str): Key used to store conversation history in memory (default: "chat_history")
        """
        self.llm = llm
        self.retriever = retriever
        
        # Initialize conversation memory with window-based storage
        # This keeps the last 10 conversation turns for context
        self.memory = ConversationBufferWindowMemory(
            memory_key=memory_key,
            return_messages=True,
            output_key='answer',
            k=10  # Keep last 10 conversation turns
        )

        # Combines LLM, retriever and memory to answer questions using retrieved documents while maintaining conversation context
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm, # Generates responses
            retriever=self.retriever, # Finds relevant documents from knowledge base
            memory=self.memory, #Maintains conversation context
            return_source_documents=True,  # Include source documents in response
            verbose=True
        )

    async def aquery(self, question: str, callbacks: Optional[List[BaseCallbackHandler]] = None) -> Dict[str, Any]:
        """
        Asynchronously query the RAG pipeline with a question.
        
        This method is designed for asynchronous applications like web servers
        and real-time chat interfaces. It processes the question through the
        conversational chain and returns the generated answer along with
        supporting source documents.
        
        Args:
            question (str): The user's question to process
            callbacks (Optional[List[BaseCallbackHandler]]): Optional list of callback handlers
                                                          for monitoring the generation process
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - answer: The generated response from the LLM
                - source_documents: List of source documents used for the response
                - chat_history: Current conversation history
        """
        # Process the question through the conversational chain
        result = await self.qa_chain.ainvoke(
            {"question": question},
            callbacks=callbacks
        )

        # Format the response with all relevant information
        return {
            "answer": result["answer"],
            "source_documents": result["source_documents"],
            "chat_history": result.get("chat_history", [])
        }

    def query(self, question: str, callbacks: Optional[List[BaseCallbackHandler]] = None) -> Dict[str, Any]:
        """
        Synchronously query the RAG pipeline with a question.
        
        This method is suitable for synchronous applications and provides
        the same functionality as aquery but in a blocking manner.
        
        Args:
            question (str): The user's question to process
            callbacks (Optional[List[BaseCallbackHandler]]): Optional list of callback handlers
                                                          for monitoring the generation process
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - answer: The generated response from the LLM
                - source_documents: List of source documents used for the response
                - chat_history: Current conversation history
        """
        # Process the question through the conversational chain
        result = self.qa_chain.invoke(
            {"question": question},
            callbacks=callbacks
        )

        # Format the response with all relevant information
        return {
            "answer": result["answer"],
            "source_documents": result["source_documents"],
            "chat_history": result.get("chat_history", [])
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