#!/usr/bin/env python3
"""
Test script for the search functionality
"""

import requests
import json
import os
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000/api"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"

def test_auth():
    """Test authentication and get token"""
    print("🔐 Testing authentication...")
    
    # Try to login first
    login_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"✅ Login successful, token: {token[:20]}...")
            return token
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_get_document_types(token):
    """Test getting document types"""
    print("\n📋 Testing get document types...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE_URL}/documents/types", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Document types retrieved: {data}")
            return True
        else:
            print(f"❌ Get document types failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get document types error: {e}")
        return False

def test_search_documents(token):
    """Test searching documents"""
    print("\n🔍 Testing search documents...")
    
    headers = {"Authorization": f"Bearer {token}"}
    search_data = {
        "query": "test",
        "filters": {
            "document_type": "All Types",
            "date_range": "all",
            "limit": 10,
            "offset": 0
        }
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/documents/search", 
                               json=search_data, 
                               headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search successful:")
            print(f"   - Total results: {data.get('total_results', 0)}")
            print(f"   - Documents found: {len(data.get('documents', []))}")
            print(f"   - Query: {data.get('query', '')}")
            return True
        else:
            print(f"❌ Search failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Search error: {e}")
        return False

def test_get_documents(token):
    """Test getting all documents"""
    print("\n📄 Testing get all documents...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE_URL}/documents", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Get documents successful:")
            print(f"   - Total documents: {data.get('pagination', {}).get('total', 0)}")
            print(f"   - Documents returned: {len(data.get('documents', []))}")
            return True
        else:
            print(f"❌ Get documents failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get documents error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting search functionality tests...")
    print(f"📅 Test time: {datetime.now()}")
    print(f"🌐 API URL: {API_BASE_URL}")
    
    # Test authentication
    token = test_auth()
    if not token:
        print("❌ Authentication failed, cannot continue tests")
        return
    
    # Test document types
    types_success = test_get_document_types(token)
    
    # Test get documents
    docs_success = test_get_documents(token)
    
    # Test search
    search_success = test_search_documents(token)
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    print(f"Authentication: {'✅ PASS' if token else '❌ FAIL'}")
    print(f"Get Document Types: {'✅ PASS' if types_success else '❌ FAIL'}")
    print(f"Get Documents: {'✅ PASS' if docs_success else '❌ FAIL'}")
    print(f"Search Documents: {'✅ PASS' if search_success else '❌ FAIL'}")
    
    if all([token, types_success, docs_success, search_success]):
        print("\n🎉 All tests passed! Search functionality is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main()
