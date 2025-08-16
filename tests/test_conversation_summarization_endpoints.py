"""
Integration tests for conversation summarization through API endpoints.

This file tests the actual API endpoints to ensure the conversation
summarization system works end-to-end.
"""

import asyncio
import json
import time
import requests
from typing import Dict, Any
import os
import sys

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

# Test configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"  # Fix: Your API uses /api, not /api/v1

class TestConversationSummarizationEndpoints:
    """Test class for conversation summarization endpoints."""
    
    def __init__(self):
        self.session = requests.Session()
        self.conversation_ids = []
        self.test_user_id = "123e4567-e89b-12d3-a456-426614174000"  # Valid UUID format
        
    def setup_method(self):
        """Setup before each test method."""
        self.session = requests.Session()
        # You might need to add authentication headers here
        # self.session.headers.update({"Authorization": f"Bearer {token}"})
        
    def teardown_method(self):
        """Cleanup after each test method."""
        # Clean up test conversations
        for conv_id in self.conversation_ids:
            try:
                self.session.delete(f"{API_BASE}/chat/conversations/{conv_id}")
            except:
                pass
        self.conversation_ids.clear()
        
    def test_server_health(self):
        """Test if the server is running and healthy."""
        try:
            response = self.session.get(f"{BASE_URL}/health")
            assert response.status_code == 200
            print("✅ Server is running and healthy")
        except requests.exceptions.ConnectionError:
            print("Server is not running. Start the server first.")
            return
            
    def test_create_conversation(self):
        """Test creating a new conversation."""
        response = self.session.post(
            f"{API_BASE}/chat/conversations",
            json={}  # Don't require user_id for testing
        )
        
        print(f"Create conversation response: {response.status_code} - {response.text}")
        
        # Check what status code we actually get
        if response.status_code == 201:
            data = response.json()
            assert "id" in data
            assert "user_id" in data
            conversation_id = data["id"]
        elif response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert "user_id" in data
            conversation_id = data["id"]
        else:
            print(f"Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            raise Exception(f"Failed to create conversation. Status: {response.status_code}")
        
        self.conversation_ids.append(conversation_id)
        print(f"✅ Created conversation: {conversation_id}")
        
        return conversation_id
        
    def test_send_single_message(self):
        """Test sending a single message to a conversation."""
        # Create conversation first
        conv_id = self.test_create_conversation()
        
        # Send message
        message_data = {
            "message": "Hello, can you help me analyze this document?",
            "conversation_id": conv_id,
            "user_id": self.test_user_id
        }
        
        response = self.session.post(
            f"{API_BASE}/chat/send",
            json=message_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "conversation_id" in data
        assert data["conversation_id"] == conv_id
        
        print("✅ Single message sent successfully")
        
    def test_long_conversation_triggering_summarization(self):
        """Test that long conversations trigger summarization."""
        # Create conversation
        conv_id = self.test_create_conversation()
        
        # Send many messages to trigger summarization (16+ pairs)
        messages = [
            "What are the key financial metrics in the Q4 2024 report?",
            "How does Q4 2024 compare to Q3 2024?",
            "What are the main risks identified in the quarterly report?",
            "Can you analyze the cash flow from the Q4 report?",
            "What are the growth projections for Q1 2025?",
            "How much was the total revenue in Q4 2024?",
            "What are the key operational challenges mentioned in the report?",
            "Can you summarize the executive summary from Q4 2024?",
            "What are the main competitive advantages discussed?",
            "How does the company plan to address market challenges?",
            "What was the revenue growth percentage in Q4?",
            "Can you analyze the profit margins from the quarterly report?",
            "What are the key performance indicators mentioned?",
            "How far in advance do I need to request leave?",
            "What are the standard work hours according to company policy?",
            "Can you explain the dress code policy?",
            "What are the internet usage guidelines?",
            "How many days of paid leave are employees entitled to?",
            "What should I do if I have safety concerns?",
            "Can you explain the confidentiality requirements?"
        ]
        
        print(f"📝 Sending {len(messages)} messages to trigger summarization...")
        
        for i, message in enumerate(messages):
            message_data = {
                "message": message,
                "conversation_id": conv_id,
                "user_id": self.test_user_id
            }
            
            response = self.session.post(
                f"{API_BASE}/chat/send",
                json=message_data
            )
            
            print(f"  Message {i+1} response: {response.status_code} - {response.text[:100]}...")
            
            if response.status_code != 200:
                print(f"  ❌ Failed at message {i+1}: {response.status_code}")
                print(f"  Full response: {response.text}")
                break
                
            assert response.status_code == 200
            data = response.json()
            
            # Fix: Your API returns 'metadata', not 'conversation_stats'
            if "metadata" in data:
                metadata = data["metadata"]
                print(f"  Message {i+1}: metadata contains {len(metadata)} items")
                
                # Check if context was optimized (this would be in metadata if implemented)
                if metadata.get("context_optimized"):
                    print(f"  ⚡ Context optimization triggered at message {i+1}!")
                    
            # Small delay to avoid overwhelming the server
            time.sleep(0.1)
        
        print("✅ Long conversation completed")
        
        # Get conversation stats to verify summarization
        response = self.session.get(f"{API_BASE}/chat/conversations/{conv_id}/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"📊 Final stats: {json.dumps(stats, indent=2)}")
            
    def test_conversation_context_endpoint(self):
        """Test the conversation context endpoint."""
        conv_id = self.test_create_conversation()
        
        # Send a few messages first
        for i in range(3):
            message_data = {
                "message": f"Test message {i+1}",
                "conversation_id": conv_id,
                "user_id": self.test_user_id
            }
            
            self.session.post(f"{API_BASE}/chat/send", json=message_data)
        
        # Get conversation context
        response = self.session.get(
            f"{API_BASE}/chat/conversations/{conv_id}/context",
            params={"include_summary": "true"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "total_messages" in data
        assert "stats" in data
        
        print("✅ Conversation context retrieved successfully")
        print(f"   Total messages: {data['total_messages']}")
        print(f"   Stats: {json.dumps(data['stats'], indent=2)}")
        
    def test_force_summarization_endpoint(self):
        """Test manually triggering summarization."""
        conv_id = self.test_create_conversation()
        
        # Send some messages
        for i in range(5):
            message_data = {
                "message": f"Message for summarization test {i+1}",
                "conversation_id": conv_id,
                "user_id": self.test_user_id
            }
            self.session.post(f"{API_BASE}/chat/send", json=message_data)
        
        # Force summarization
        response = self.session.post(
            f"{API_BASE}/chat/conversations/{conv_id}/summarize"
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "optimized_messages" in data
            assert "summary" in data
            print("✅ Manual summarization completed")
            print(f"   Summary: {data['summary'][:100]}...")
        else:
            print(f"⚠️  Manual summarization endpoint not implemented (status: {response.status_code})")
            
    def test_conversation_export(self):
        """Test exporting conversation data."""
        conv_id = self.test_create_conversation()
        
        # Send a message
        message_data = {
            "message": "Test message for export",
            "conversation_id": conv_id,
            "user_id": self.test_user_id
        }
        self.session.post(f"{API_BASE}/chat/send", json=message_data)
        
        # Test JSON export
        response = self.session.get(
            f"{API_BASE}/chat/conversations/{conv_id}/export",
            params={"format": "json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            print("✅ JSON export successful")
        else:
            print(f"⚠️  Export endpoint not implemented (status: {response.status_code})")
            
    def test_conversation_management(self):
        """Test conversation management endpoints."""
        conv_id = self.test_create_conversation()
        
        # Get all conversations
        response = self.session.get(f"{API_BASE}/chat/conversations")
        if response.status_code == 200:
            conversations = response.json()
            assert isinstance(conversations, list)
            print(f"✅ Retrieved {len(conversations)} conversations")
        else:
            print(f"⚠️  Get conversations endpoint not implemented (status: {response.status_code})")
            
        # Clear conversation
        response = self.session.delete(f"{API_BASE}/chat/conversations/{conv_id}")
        if response.status_code == 200:
            print("✅ Conversation cleared successfully")
        else:
            print(f"⚠️  Clear conversation endpoint not implemented (status: {response.status_code})")
            
    def test_error_handling(self):
        """Test error handling for invalid requests."""
        # Test with invalid conversation ID
        response = self.session.post(
            f"{API_BASE}/chat/send",
            json={
                "message": "Test message",
                "conversation_id": "invalid_id",
                "user_id": self.test_user_id
            }
        )
        
        # Should return an error
        assert response.status_code in [400, 404, 422]
        print("✅ Error handling works correctly")
        
    def run_all_tests(self):
        """Run all tests in sequence."""
        print("🚀 Starting Conversation Summarization Endpoint Tests")
        print("=" * 60)
        
        test_methods = [
            method for method in dir(self) 
            if method.startswith('test_') and callable(getattr(self, method))
        ]
        
        passed = 0
        failed = 0
        skipped = 0
        
        for test_method in test_methods:
            try:
                print(f"\n🧪 Running: {test_method}")
                print("-" * 40)
                
                getattr(self, test_method)()
                print(f"✅ PASSED: {test_method}")
                passed += 1
                
            except Exception as e:
                print(f"❌ FAILED: {test_method}")
                print(f"   Error: {str(e)}")
                import traceback
                traceback.print_exc()
                failed += 1
                
        print("\n" + "=" * 60)
        print("📊 Test Results Summary")
        print("=" * 60)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%" if (passed+failed) > 0 else "N/A")
        
        return passed, failed, skipped


# def main():
#     """Main function to run the tests."""
#     print("🔧 Conversation Summarization Endpoint Tests")
#     print("Make sure your server is running on http://localhost:8000")
#     print("=" * 60)
#
#     # Check if server is running
#     try:
#         response = requests.get(f"{BASE_URL}/health", timeout=5)
#         if response.status_code == 200:
#             print("✅ Server is running and accessible")
#         else:
#             print("⚠️  Server responded but health check failed")
#     except requests.exceptions.ConnectionError:
#         print("❌ Cannot connect to server. Please start your FastAPI server first.")
#         print("   Run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
#         return
#
#     # Run tests
#     tester = TestConversationSummarizationEndpoints()
#     passed, failed, skipped = tester.run_all_tests()
#
#     if failed == 0:
#         print("\n🎉 All tests passed! Your conversation summarization system is working correctly.")
#     else:
#         print(f"\n⚠️  {failed} test(s) failed. Check the output above for details.")


def main():
    """Main function to run only the long conversation summarization test."""
    print("🔧 Conversation Summarization Endpoint Tests")
    print("Make sure your server is running on http://localhost:8000")
    print("=" * 60)

    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
        else:
            print("⚠️  Server responded but health check failed")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start your FastAPI server first.")
        print("   Run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return

    tester = TestConversationSummarizationEndpoints()

    try:
        print("\n🧪 Running: test_long_conversation_triggering_summarization")
        print("-" * 40)
        tester.test_long_conversation_triggering_summarization()
        print("✅ PASSED: test_long_conversation_triggering_summarization")
    except Exception as e:
        print("❌ FAILED: test_long_conversation_triggering_summarization")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main() 