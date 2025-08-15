#!/usr/bin/env python3
"""
Test RAG QA System via API Endpoints

This script tests the RAG chatbot system by sending queries through the API endpoints
to get answers from already indexed documents in ChromaDB.

Usage:
    python tests/rag/test_rag_endpoints.py
"""

import requests
import json
import time
import os
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
BASE_URL = "http://localhost:8000"
CHAT_API_URL = f"{BASE_URL}/api/chat"

# Test questions to ask your existing documents
TEST_QUESTIONS = [
    "What is the dress code policy for employees?",
    "What steps are required to install and launch the software?",
    "What key achievements were highlighted in the Q4 2024 business report?",
    "What should employees do regarding internet usage at work?",
    "What information must be provided to a Data Subject under data protection law?",
]

class RAGEndpointTester:
    """Test RAG system via API endpoints using existing documents"""
    
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def check_server_health(self) -> bool:
        """Check if the server is running and healthy"""
        print("🔍 Checking server health...")
        try:
            response = self.session.get(f"{BASE_URL}/health", timeout=10)
            if response.status_code == 200:
                print("✅ Server is healthy and running")
                return True
            else:
                print(f"❌ Server health check failed: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Server is not running. Please start the server first:")
            print("   python run.py")
            return False
        except Exception as e:
            print(f"❌ Error checking server health: {e}")
            return False
    
    def test_chat_message(self, question: str, question_number: int) -> Dict[str, Any]:
        """Test sending a chat message and getting RAG response from existing documents"""
        print(f"\n❓ Testing Question {question_number}: {question}")
        
        chat_data = {
            "message": question,
            "user_id": "test-user-rag",
            "memory_type": "window",
            "conversation_id": f"test-conversation-{int(time.time())}",
            "llm_config": {
                "provider": "groq",  # Use Groq API
                "model": "llama3-8b-8192",  # Groq model
                "temperature": 0.3,
                "streaming": False
            }
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{CHAT_API_URL}/message",
                json=chat_data,
                timeout=120  # 2 minutes timeout
            )
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('response', '')
                conversation_id = result.get('conversation_id', '')
                
                print(f"✅ Answer received in {processing_time:.2f}s")
                print(f"   Answer: {answer[:200]}{'...' if len(answer) > 200 else ''}")
                print(f"   Conversation ID: {conversation_id}")
                
                return {
                    "question": question,
                    "answer": answer,
                    "conversation_id": conversation_id,
                    "processing_time": processing_time,
                    "status": "success",
                    "response_code": response.status_code
                }
            else:
                print(f"❌ Chat request failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
                return {
                    "question": question,
                    "answer": "",
                    "conversation_id": "",
                    "processing_time": 0,
                    "status": "failed",
                    "response_code": response.status_code,
                    "error": response.text
                }
                
        except requests.exceptions.Timeout:
            print(f"❌ Request timed out after 120 seconds")
            return {
                "question": question,
                "answer": "",
                "conversation_id": "",
                "processing_time": 0,
                "status": "timeout",
                "response_code": 0,
                "error": "Request timed out"
            }
        except Exception as e:
            print(f"❌ Error sending chat message: {e}")
            return {
                "question": question,
                "answer": "",
                "conversation_id": "",
                "processing_time": 0,
                "status": "error",
                "response_code": 0,
                "error": str(e)
            }
    
    def test_document_search(self, query: str) -> Dict[str, Any]:
        """Test document search functionality on existing documents"""
        print(f"\n🔍 Testing document search for: {query}")
        
        search_data = {
            "query": query,
            "k": 3,
            "user_id": "test-user-rag"
        }
        
        try:
            response = self.session.post(
                f"{CHAT_API_URL}/documents/search",
                json=search_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                documents = result.get('documents', [])
                print(f"✅ Search successful, found {len(documents)} documents")
                
                for i, doc in enumerate(documents[:2]):  # Show first 2 results
                    content = doc.get('content', '')[:100]
                    print(f"   Doc {i+1}: {content}...")
                
                return {
                    "query": query,
                    "status": "success",
                    "document_count": len(documents),
                    "response_code": response.status_code
                }
            else:
                print(f"❌ Search failed: {response.status_code}")
                return {
                    "query": query,
                    "status": "failed",
                    "document_count": 0,
                    "response_code": response.status_code,
                    "error": response.text
                }
                
        except Exception as e:
            print(f"❌ Error in document search: {e}")
            return {
                "query": query,
                "status": "error",
                "document_count": 0,
                "response_code": 0,
                "error": str(e)
            }
    
    def run_all_tests(self):
        """Run RAG endpoint tests using existing documents"""
        print("🚀 Starting RAG Endpoint Tests (Using Existing Documents)")
        print("=" * 70)
        
        # Step 1: Check server health
        if not self.check_server_health():
            return
        
        # Step 2: Test document search on existing documents
        print("\n" + "="*60)
        print("🔍 TESTING DOCUMENT SEARCH (Existing Documents)")
        print("="*60)
        
        search_results = []
        for i, question in enumerate(TEST_QUESTIONS[:2], 1):  # Test first 2 questions for search
            result = self.test_document_search(question)
            search_results.append(result)
        
        # Step 3: Test chat messages on existing documents
        print("\n" + "="*60)
        print("💬 TESTING CHAT MESSAGES (Existing Documents)")
        print("="*60)
        
        chat_results = []
        for i, question in enumerate(TEST_QUESTIONS, 1):
            result = self.test_chat_message(question, i)
            chat_results.append(result)
            time.sleep(2)  # 2 second delay between requests
        
        # Step 4: Generate summary
        self.generate_summary(search_results, chat_results)
    
    def generate_summary(self, search_results: List[Dict], chat_results: List[Dict]):
        """Generate a comprehensive test summary"""
        print("\n" + "="*60)
        print("📊 RAG ENDPOINT TEST SUMMARY")
        print("="*60)
        
        # Search results summary
        search_success = sum(1 for r in search_results if r['status'] == 'success')
        print(f"\n🔍 Document Search: {search_success}/{len(search_results)} successful")
        
        # Chat results summary
        chat_success = sum(1 for r in chat_results if r['status'] == 'success')
        print(f"💬 Chat Messages: {chat_success}/{len(chat_results)} successful")
        
        if chat_success > 0:
            avg_processing_time = sum(r['processing_time'] for r in chat_results if r['status'] == 'success') / chat_success
            print(f"⏱️  Average processing time: {avg_processing_time:.2f}s")
        
        # Detailed results
        print(f"\n📋 DETAILED RESULTS:")
        print("-" * 40)
        
        for i, result in enumerate(chat_results, 1):
            status_icon = "✅" if result['status'] == 'success' else "❌"
            print(f"{status_icon} Q{i}: {result['status']}")
            if result['status'] == 'success':
                print(f"   Time: {result['processing_time']:.2f}s")
                print(f"   Answer: {result['answer'][:100]}...")
            elif 'error' in result:
                print(f"   Error: {result['error']}")
        
        # Overall assessment
        total_tests = len(search_results) + len(chat_results)
        total_success = search_success + chat_success
        
        print(f"\n🎯 OVERALL ASSESSMENT:")
        print(f"   Total tests: {total_tests}")
        print(f"   Successful: {total_success}")
        print(f"   Success rate: {(total_success/total_tests)*100:.1f}%")
        
        if total_success == total_tests:
            print("🎉 All RAG endpoint tests passed! Your system is working correctly.")
        elif total_success > total_tests * 0.7:
            print("⚠️  Most tests passed. Check failed tests above for issues.")
        else:
            print("❌ Many tests failed. Please check your RAG system configuration.")
        
        print(f"\n📖 API Documentation: {BASE_URL}/docs")
        print(f"🔍 Alternative Docs: {BASE_URL}/redoc")


def main():
    """Main function to run RAG endpoint tests"""
    tester = RAGEndpointTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
