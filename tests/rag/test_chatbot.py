import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
api_key = os.getenv("GEMINI_API_KEY")

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from app.services.chatbot.vector_db.langchain_chroma import LangChainChromaStore
from app.services.chatbot.chains.conversational_chain import CustomConversationalChain
from app.services.chatbot.llm.llm_factory import LLMFactory
from app.services.chatbot.vector_db.chunking import DocumentChunker
from app.services.chatbot.vector_db.indexing import LangChainDocumentIndexer

vectorstore = LangChainChromaStore("./test_chroma_db", "test_docs")
llm = LLMFactory.create_gemini_llm(api_key, "gemini-1.5-flash")
retriever = vectorstore.as_retriever()
chain = CustomConversationalChain(llm, retriever)

chunker = DocumentChunker(chunk_size=500, chunk_overlap=100)
indexer = LangChainDocumentIndexer(vectorstore, chunker)

test_doc = {
   'id': 'test-1',
   'text': 'Python is a programming language. It is used for web development, data science, and machine learning. Django and Flask are popular Python web frameworks.',
   'filename': 'python_info.txt',
   'user_id': 'test-user'
}

print("1. Indexing document...")
try:
   ids = indexer.index_document(test_doc)
   print(f"✅ Document indexed with IDs: {ids}")
except Exception as e:
   print(f"❌ Indexing failed: {e}")

print("\n2. Testing query...")
try:
   result = chain.run("What is Python used for?")
   print(f"✅ Answer: {result['answer']}")
   print(f"✅ Found {len(result['source_documents'])} sources")
except Exception as e:
   print(f"❌ Query failed: {e}")

print("\n3. Testing follow-up...")
try:
   result2 = chain.run("What are Python web frameworks?")
   print(f"✅ Follow-up: {result2['answer']}")
except Exception as e:
   print(f"❌ Follow-up failed: {e}")
