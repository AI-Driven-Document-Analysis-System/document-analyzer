#!/usr/bin/env python3
"""
Test RAG QA over ChromaDB with GROQ LLM Generation

This script hardcodes questions and uses the RAG pipeline to answer them from the ChromaDB vector store.
It retrieves relevant chunks, passes them as context to GROQ, and prints the generated answer.
Also prints which document (filename) the answer came from and the raw retrieved chunks for debugging.

Requires: pip install groq
Set your GROQ API key in the GROQ_API_KEY environment variable.
"""

import os
import sys
from dotenv import load_dotenv
import warnings

# Suppress deprecation warnings
warnings.filterwarnings("ignore", message="`encoder_attention_mask` is deprecated", category=FutureWarning)
warnings.filterwarnings("ignore", message="The class `HuggingFaceEmbeddings` was deprecated", category=UserWarning)
warnings.filterwarnings("ignore", message="The class `Chroma` was deprecated", category=UserWarning)

# Load environment variables from .env file
load_dotenv()

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.chatbot.vector_db.langchain_chroma import LangChainChromaStore

# GROQ imports
from groq import Groq

# Hardcoded questions to test
QUESTIONS = [
    "What is the dress code policy for employees?",
    "What steps are required to install and launch the software?",
    "What key achievements were highlighted in the Q4 2024 business report?",
    "What should employees do regarding internet usage at work?",
    "What information must be provided to a Data Subject under data protection law?",
]

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def call_groq_llm(question, context):
    """Call GROQ LLM with question and context, return the answer string."""
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY environment variable not set.")

    client = Groq(api_key=GROQ_API_KEY)

    prompt = (
        "You are a helpful assistant. Use the provided context to answer the user's question. "
        "If the answer is not in the context, say 'I don't know.'\n\n"
        f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    )

    response = client.chat.completions.create(
        model="llama3-8b-8192",  # or "mixtral-8x7b-32768" or "gemma-7b-it"
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024,
        temperature=0.3
    )

    return response.choices[0].message.content.strip()


def main():
    db_path = "./chroma_db"
    collection_name = "documents"
    top_k = 3  # Number of top chunks to retrieve per question

    # Initialize vectorstore (RAG retriever)
    vectorstore = LangChainChromaStore(db_path, collection_name)

    print("\n🔍 RAG QA TEST OVER CHROMADB + GROQ\n" + "=" * 60)

    for q in QUESTIONS:
        print(f"\n❓ \033[94mQuestion: {q}\033[0m")
        retrieved = vectorstore.similarity_search(q, k=top_k)
        if not retrieved:
            print("❌ No answer found.")
            continue

        # Concatenate retrieved chunks as context
        context = "\n\n".join([doc.page_content.strip() for doc in retrieved])

        # Call GROQ LLM
        try:
            answer = call_groq_llm(q, context)
            print(f"💡 \033[92mAnswer: {answer}\033[0m")
        except Exception as e:
            print(f"❌ GROQ LLM call failed: {e}")
    print("\n✅ Done.")


if __name__ == "__main__":
    main()