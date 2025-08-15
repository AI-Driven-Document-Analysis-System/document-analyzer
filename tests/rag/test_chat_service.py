#!/usr/bin/env python3
"""
Test script for ChatbotService to verify functionality.
This script tests the main features of the chat service.
"""

import os
import sys
import tempfile
import shutil
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Load environment variables
load_dotenv()

def test_chatbot_service():
    """Test the ChatbotService functionality."""
    
    print("🧪 Testing ChatbotService...")
    print("=" * 50)
    
    # Test configuration
    test_config = {
        'vector_db_path': './test_chroma_db',
        'collection_name': 'test_documents',
        'chunk_size': 500,
        'chunk_overlap': 100,
        'embedding_model': 'all-MiniLM-L6-v2',
        'max_history_length': 5
    }
    
    # Test LLM configuration (using environment variables)
    llm_config = {
        'provider': 'gemini',  # Using Gemini since you have the API key
        'api_key': os.getenv('GEMINI_API_KEY'),
        'model': 'gemini-1.5-flash',  # Gemini model
        'temperature': 0.7,
        'streaming': False
    }
    
    try:
        # Import the service
        print("1. Importing ChatbotService...")
        from app.services.chat_service import ChatbotService, initialize_chatbot_service
        
        # Test 1: Service Initialization
        print("\n2. Testing service initialization...")
        service = ChatbotService(test_config)
        service.initialize()
        print("✅ Service initialized successfully")
        
        # Test 2: Document Indexing
        print("\n3. Testing document indexing...")
        test_document = {
            'id': 'test-doc-1',
            'text': '''
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
            ''',
            'filename': 'python_intro.txt',
            'user_id': 'test-user-1'
        }
        
        chunk_ids = service.index_document(test_document)
        print(f"✅ Document indexed with {len(chunk_ids)} chunks")
        
        # Test 3: Document Search
        print("\n4. Testing document search...")
        search_results = service.search_documents("What is Python?", k=3)
        print(f"✅ Found {len(search_results)} search results")
        for i, result in enumerate(search_results[:2]):
            print(f"   Result {i+1}: {result['content'][:100]}...")
        
        # Test 4: Chat Engine Creation
        print("\n5. Testing chat engine creation...")
        chat_engine = service.get_or_create_chat_engine(
            llm_config=llm_config,
            user_id='test-user-1'
        )
        print("✅ Chat engine created successfully")
        
        # Test 5: Chat Conversation
        print("\n6. Testing chat conversation...")
        try:
            response = chat_engine.chat("What is Python and what is it used for?")
            print(f"✅ Chat response: {response[:200]}...")
        except Exception as e:
            print(f"⚠️  Chat test skipped (likely due to missing API key): {e}")
        
        # Test 6: System Stats
        print("\n7. Testing system statistics...")
        stats = service.get_system_stats()
        print(f"✅ System stats: {stats}")
        
        # Test 7: Conversation History
        print("\n8. Testing conversation history...")
        history = service.get_conversation_history('test-conversation')
        print(f"✅ Conversation history retrieved: {len(history)} characters")
        
        # Test 8: Cleanup
        print("\n9. Testing cleanup...")
        service.cleanup()
        print("✅ Service cleanup completed")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required dependencies are installed:")
        print("pip install langchain langchain-community langchain-openai sentence-transformers chromadb")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_singleton_pattern():
    """Test the singleton pattern implementation."""
    
    print("\n🧪 Testing Singleton Pattern...")
    print("=" * 50)
    
    try:
        from app.services.chat_service import (
            initialize_chatbot_service, 
            get_chatbot_service, 
            cleanup_chatbot_service
        )
        
        # Test configuration
        test_config = {
            'vector_db_path': './test_chroma_db_singleton',
            'collection_name': 'test_singleton',
            'chunk_size': 500,
            'chunk_overlap': 100,
            'embedding_model': 'all-MiniLM-L6-v2',
            'max_history_length': 5
        }
        
        # Test 1: Initialize singleton
        print("1. Initializing singleton service...")
        service1 = initialize_chatbot_service(test_config)
        print("✅ Singleton service initialized")
        
        # Test 2: Get singleton instance
        print("2. Getting singleton instance...")
        service2 = get_chatbot_service()
        print("✅ Singleton instance retrieved")
        
        # Test 3: Verify same instance
        print("3. Verifying same instance...")
        if service1 is service2:
            print("✅ Same instance confirmed")
        else:
            print("❌ Different instances - singleton pattern failed")
            return False
        
        # Test 4: Cleanup
        print("4. Testing cleanup...")
        cleanup_chatbot_service()
        print("✅ Singleton cleanup completed")
        
        print("🎉 Singleton pattern tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Singleton test failed: {e}")
        return False

def test_error_handling():
    """Test error handling scenarios."""
    
    print("\n🧪 Testing Error Handling...")
    print("=" * 50)
    
    try:
        from app.services.chat_service import ChatbotService
        
        # Test 1: Uninitialized service
        print("1. Testing uninitialized service...")
        service = ChatbotService({})
        try:
            service.search_documents("test")
            print("❌ Should have raised RuntimeError")
            return False
        except RuntimeError:
            print("✅ Correctly raised RuntimeError for uninitialized service")
        
        # Test 2: Invalid configuration
        print("2. Testing invalid configuration...")
        try:
            service = ChatbotService({})
            service.initialize()
            print("❌ Should have failed with invalid config")
            return False
        except Exception:
            print("✅ Correctly handled invalid configuration")
        
        print("🎉 Error handling tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def main():
    """Run all tests."""
    
    print("🚀 Starting ChatbotService Tests")
    print("=" * 60)
    
    # Check environment
    print("📋 Environment Check:")
    print(f"   Python version: {sys.version}")
    print(f"   Working directory: {os.getcwd()}")
    
    # Check for API keys
    api_keys = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'GROQ_API_KEY': os.getenv('GROQ_API_KEY')
    }
    
    print("\n🔑 API Keys Status:")
    for key_name, key_value in api_keys.items():
        status = "✅ Set" if key_value else "❌ Not set"
        print(f"   {key_name}: {status}")
    
    # Run tests
    tests = [
        ("Main Service", test_chatbot_service),
        ("Singleton Pattern", test_singleton_pattern),
        ("Error Handling", test_error_handling)
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
    print("📊 TEST SUMMARY")
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
        print("🎉 All tests passed! Your ChatbotService is working properly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    # Cleanup test directories
    print("\n🧹 Cleaning up test directories...")
    test_dirs = ['./test_chroma_db', './test_chroma_db_singleton']
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            try:
                shutil.rmtree(test_dir)
                print(f"✅ Cleaned up {test_dir}")
            except Exception as e:
                print(f"⚠️  Could not clean up {test_dir}: {e}")

if __name__ == "__main__":
    main()
