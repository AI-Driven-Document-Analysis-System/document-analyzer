from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryBufferMemory
from langchain.prompts import PromptTemplate
from langchain.schema import BaseRetriever
from typing import Any, Dict, List, Optional


class CustomConversationalChain:
    def __init__(self, llm: Any, retriever: BaseRetriever, memory_type: str = "window"):
        self.llm = llm
        self.retriever = retriever

        if memory_type == "window":
            self.memory = ConversationBufferWindowMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key='answer',
                k=10
            )
        elif memory_type == "summary":
            self.memory = ConversationSummaryBufferMemory(
                llm=llm,
                memory_key="chat_history",
                return_messages=True,
                output_key='answer',
                max_token_limit=1000
            )

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

        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.retriever,
            memory=self.memory,
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": self.custom_prompt},
            verbose=True
        )

    async def arun(self, question: str, callbacks: Optional[List] = None) -> Dict[str, Any]:
        result = await self.chain.ainvoke(
            {"question": question},
            callbacks=callbacks
        )

        return {
            "answer": result["answer"],
            "source_documents": result["source_documents"],
            "chat_history": self.memory.chat_memory.messages
        }

    def run(self, question: str, callbacks: Optional[List] = None) -> Dict[str, Any]:
        result = self.chain.invoke(
            {"question": question},
            callbacks=callbacks
        )

        return {
            "answer": result["answer"],
            "source_documents": result["source_documents"],
            "chat_history": self.memory.chat_memory.messages
        }