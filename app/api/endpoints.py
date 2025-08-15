from fastapi import FastAPI

from app.services.chatbot.vector_db.indexing import LangChainDocumentIndexer
from app.services.chatbot.vector_db.langchain_chroma import LangChainChromaStore
from app.services.chatbot.rag.custom_retriever import ChromaRetriever
from app.services.chatbot.chains.conversational_chain import CustomConversationalChain
from app.services.chatbot.rag.chat_engine import LangChainChatEngine
from app.services.chatbot.llm.llm_factory import LLMFactory
from app.services.chatbot.vector_db.chunking import DocumentChunker

app = FastAPI()

vectorstore = LangChainChromaStore("./data/chroma_db")
llm = LLMFactory.create_gemini_llm(api_key="AIzaSyDC2A8PcGuYXMrWyQpVDoTutbIntgyOYyA", model="gemini-1.5-flash")
retriever = vectorstore.as_retriever()
chain = CustomConversationalChain(llm, retriever)
chat_engine = LangChainChatEngine(chain)
chunker = DocumentChunker(chunk_size=500, chunk_overlap=100)

@app.post("/documents/index")
async def index_document(document_data: dict):
    indexer = LangChainDocumentIndexer(vectorstore, chunker)
    ids = indexer.index_document(document_data)
    return {"status": "success", "ids": ids}

@app.post("/chat/query")
async def chat_query(query: str, conversation_id: str = None):
    result = await chat_engine.process_query(query, conversation_id)
    return result