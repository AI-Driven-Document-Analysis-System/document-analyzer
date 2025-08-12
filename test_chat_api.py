#!/usr/bin/env python3
"""
Test script for Chat API endpoints
This script tests the main chat API functionality
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API base URL
BASE_URL = "http://localhost:8000/api/chat"

def test_health_check():
    """Test the health check endpoint"""
    print("🧪 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_system_stats():
    """Test the system stats endpoint"""
    print("\n🧪 Testing System Stats...")
    try:
        response = requests.get(f"{BASE_URL}/system/stats")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ System Stats: {json.dumps(stats, indent=2)}")
        else:
            print(f"❌ Failed: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ System stats failed: {e}")
        return False

def test_document_indexing():
    """Test document indexing"""
    print("\n🧪 Testing Document Indexing...")
    try:
        document_data = {
            "id": "test-doc-1",
            "text": """
            Python is a high-level, interpreted programming language known for its simplicity and readability.
            It was created by Guido van Rossum and first released in 1991. Python supports multiple programming paradigms,
            including procedural, object-oriented, and functional programming.
            
            Key features of Python include:
            - Easy to learn and use
            - Extensive standard library
            - Cross-platform compatibility
            - Strong community support
            
            Python is widely used in:
            - Web development (Django, Flask)
            - Data science and machine learning
            - Scientific computing
            - Automation and scripting
            """,
            "filename": "python_intro.txt",
            "user_id": "test-user-1"
        }
        
        response = requests.post(f"{BASE_URL}/documents/index", json=document_data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Document indexed: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Failed: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Document indexing failed: {e}")
        return False

def test_document_search():
    """Test document search"""
    print("\n🧪 Testing Document Search...")
    try:
        search_data = {
            "query": "What is Python used for?",
            "k": 3,
            "user_id": "test-user-1"
        }
        
        response = requests.post(f"{BASE_URL}/documents/search", json=search_data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Search results: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Failed: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Document search failed: {e}")
        return False

def test_chat_message():
    """Test chat message endpoint"""
    print("\n🧪 Testing Chat Message...")
    try:
        chat_data = {
            "message": "What is Python and what is it used for?",
            "user_id": "test-user-1",
            "memory_type": "window"
        }
        
        response = requests.post(f"{BASE_URL}/message", json=chat_data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Chat response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Failed: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Chat message failed: {e}")
        return False

def test_conversation_history():
    """Test conversation history"""
    print("\n🧪 Testing Conversation History...")
    try:
        # First send a message to create a conversation
        chat_data = {
            "message": "Hello, how are you?",
            "user_id": "test-user-1"
        }
        
        response = requests.post(f"{BASE_URL}/message", json=chat_data)
        if response.status_code == 200:
            result = response.json()
            conversation_id = result.get("conversation_id")
            
            if conversation_id:
                # Now get the conversation history
                history_response = requests.get(f"{BASE_URL}/conversations/{conversation_id}/history")
                print(f"History Status Code: {history_response.status_code}")
                if history_response.status_code == 200:
                    history = history_response.json()
                    print(f"✅ Conversation history: {json.dumps(history, indent=2)}")
                    return True
                else:
                    print(f"❌ History failed: {history_response.text}")
            else:
                print("❌ No conversation ID returned")
        else:
            print(f"❌ Failed to create conversation: {response.text}")
        return False
    except Exception as e:
        print(f"❌ Conversation history failed: {e}")
        return False

def main():
    """Run all API tests"""
    print("🚀 Starting Chat API Tests")
    print("=" * 60)
    
    # Check if server is running
    print("📋 Checking if server is running...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server is not responding properly")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the server first:")
        print("   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return
    
    # Run tests
    tests = [
        ("Health Check", test_health_check),
        ("System Stats", test_system_stats),
        ("Document Indexing", test_document_indexing),
        ("Document Search", test_document_search),
        ("Chat Message", test_chat_message),
        ("Conversation History", test_conversation_history)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 API TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All API tests passed! Your chat endpoints are working properly.")
    else:
        print("⚠️  Some API tests failed. Check the output above for details.")
    
    print("\n📖 API Documentation available at:")
    print("   http://localhost:8000/docs")
    print("   http://localhost:8000/redoc")

if __name__ == "__main__":
    main()
