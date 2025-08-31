#!/usr/bin/env python3
"""
Test authentication setup and create test user if needed
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

def test_auth_setup():
    """Test authentication and create test user if needed"""
    
    print("🔐 Testing Authentication Setup")
    print("=" * 50)
    
    # Step 1: Try to login with test credentials
    print("\n1. Testing login...")
    try:
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if login_response.status_code == 200:
            print("✅ Login successful - test user exists")
            token = login_response.json().get("access_token")
            print(f"   Token: {token[:20]}...")
            return token
        elif login_response.status_code == 401:
            print("⚠️  Login failed - user doesn't exist, creating test user...")
        else:
            print(f"❌ Unexpected login response: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None
    
    # Step 2: Create test user
    print("\n2. Creating test user...")
    try:
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "username": "testuser",
            "full_name": "Test User"
        })
        
        if register_response.status_code == 200:
            print("✅ Test user created successfully")
            user_data = register_response.json()
            print(f"   Response: {user_data}")
            token = user_data.get("access_token")
            if token:
                print(f"   Token: {token[:20]}...")
                return token
            else:
                print("   ⚠️  No token in response, trying login...")
                # Try login after registration
                login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD
                })
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    token = login_data.get("access_token")
                    if token:
                        print(f"   ✅ Login successful, token: {token[:20]}...")
                        return token
        elif register_response.status_code == 400:
            print("⚠️  User might already exist, trying login again...")
            # Try login again
            login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            if login_response.status_code == 200:
                print("✅ Login successful after registration attempt")
                token = login_response.json().get("access_token")
                print(f"   Token: {token[:20]}...")
                return token
        else:
            print(f"❌ Registration failed: {register_response.status_code}")
            print(f"Response: {register_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None
    
    return None

def test_document_types(token):
    """Test document types endpoint with authentication"""
    
    print("\n3. Testing document types endpoint...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        types_response = requests.get(f"{BASE_URL}/api/documents/types", headers=headers)
        
        if types_response.status_code == 200:
            types_data = types_response.json()
            document_types = types_data.get("document_types", [])
            print(f"✅ Document types loaded successfully")
            print(f"   Found {len(document_types)} types: {document_types}")
            return True
        else:
            print(f"❌ Document types request failed: {types_response.status_code}")
            print(f"Response: {types_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Document types error: {e}")
        return False

def test_search_endpoint(token):
    """Test search endpoint with authentication"""
    
    print("\n4. Testing search endpoint...")
    try:
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        search_payload = {
            "query": "test",
            "filters": {
                "document_type": "All Types",
                "date_range": "all",
                "limit": 10,
                "offset": 0
            }
        }
        
        search_response = requests.post(f"{BASE_URL}/api/documents/search", 
                                      headers=headers, json=search_payload)
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            documents = search_data.get("documents", [])
            total_results = search_data.get("total_results", 0)
            print(f"✅ Search endpoint working")
            print(f"   Found {total_results} documents")
            print(f"   Showing {len(documents)} in current page")
            return True
        else:
            print(f"❌ Search request failed: {search_response.status_code}")
            print(f"Response: {search_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Search error: {e}")
        return False

def main():
    """Main test function"""
    
    print("🚀 Starting authentication and API tests...")
    
    # Test authentication setup
    token = test_auth_setup()
    if not token:
        print("\n❌ Failed to get authentication token")
        print("Please check if the backend is running and accessible")
        return False
    
    # Test document types endpoint
    types_success = test_document_types(token)
    
    # Test search endpoint
    search_success = test_search_endpoint(token)
    
    print("\n" + "=" * 50)
    print("🎉 Authentication and API tests completed!")
    print(f"\nResults:")
    print(f"✅ Authentication: {'Working' if token else 'Failed'}")
    print(f"✅ Document Types: {'Working' if types_success else 'Failed'}")
    print(f"✅ Search Endpoint: {'Working' if search_success else 'Failed'}")
    
    if token and types_success and search_success:
        print(f"\n🔑 Test credentials:")
        print(f"   Email: {TEST_EMAIL}")
        print(f"   Password: {TEST_PASSWORD}")
        print(f"\n💡 You can now use these credentials to test the frontend")
        return True
    else:
        print(f"\n❌ Some tests failed. Please check the backend configuration.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
