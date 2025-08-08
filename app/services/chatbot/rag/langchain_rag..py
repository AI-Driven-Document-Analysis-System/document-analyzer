from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseRetriever, Document
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema.messages import HumanMessage, AIMessage
from typing import List, Dict, Any, Optional
import asyncio


class LangChainRAGPipeline:
    def __init__(self, llm, retriever, memory_key: str = "chat_history"):
        self.llm = llm
        self.retriever = retriever
        self.memory = ConversationBufferWindowMemory(
            memory_key=memory_key,
            return_messages=True,
            output_key='answer',
            k=10
        )

        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.retriever,
            memory=self.memory,
            return_source_documents=True,
            verbose=True
        )

    async def aquery(self, question: str, callbacks: Optional[List[BaseCallbackHandler]] = None) -> Dict[str, Any]:
        result = await self.qa_chain.ainvoke(
            {"question": question},
            callbacks=callbacks
        )

        return {
            "answer": result["answer"],
            "source_documents": result["source_documents"],
            "chat_history": result.get("chat_history", [])
        }

    def query(self, question: str, callbacks: Optional[List[BaseCallbackHandler]] = None) -> Dict[str, Any]:
        result = self.qa_chain.invoke(
            {"question": question},
            callbacks=callbacks
        )

        return {
            "answer": result["answer"],
            "source_documents": result["source_documents"],
            "chat_history": result.get("chat_history", [])
        }

    def clear_memory(self):
        self.memory.clear()

    def get_memory(self) -> List[Any]:
        return self.memory.chat_memory.messages