from fastapi import FastAPI

from backend.vector_db.indexing import LangChainDocumentIndexer
from backend.vector_db.langchain_chroma import LangChainChromaStore
from backend.rag.custom_retriever import ChromaRetriever
from backend.chains.conversational_chain import CustomConversationalChain
from backend.rag.chat_engine import LangChainChatEngine
from backend.llm.llm_factory import LLMFactory

app = FastAPI()

vectorstore = LangChainChromaStore("./data/chroma_db")
llm = LLMFactory.create_openai_llm(api_key="your-key")
retriever = vectorstore.as_retriever()
chain = CustomConversationalChain(llm, retriever)
chat_engine = LangChainChatEngine(chain)

@app.post("/documents/index")
async def index_document(document_data: dict):
    indexer = LangChainDocumentIndexer(vectorstore, chunker)
    ids = indexer.index_document(document_data)
    return {"status": "success", "ids": ids}

@app.post("/chat/query")
async def chat_query(query: str, conversation_id: str = None):
    result = await chat_engine.process_query(query, conversation_id)
    return result