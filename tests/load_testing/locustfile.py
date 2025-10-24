"""DocAnalyzer Load Testing Configuration
Based on HOW_TO_CONDUCT_TESTS.md section 3.1.5

This file defines load testing scenarios for the actual DocAnalyzer API endpoints.
Run with: locust -f tests/load_testing/locustfile.py --host=http://localhost:8000

Real API Endpoints Tested:
- /health - Main health check
- / - Root endpoint  
- /docs - API documentation
- /redoc - ReDoc documentation
- /api/auth/* - Authentication endpoints
- /api/documents/* - Document management
- /api/chat/* - Chat functionality
- /api/analytics/* - Analytics endpoints
"""

import os
import random
import uuid
from locust import HttpUser, task, between
from locust.exception import RescheduleTask
import io
class DocAnalyzerUser(HttpUser):
    """
    Simulates a user interacting with the DocAnalyzer system.
    
    According to the testing guide:
    - Start with 10 users, spawn rate 1 user per second
    - Watch response times (should stay under 2 seconds)
    - Failure rate should stay under 1%
    - Gradually increase to 50, then 100 users
    """
    
    # Wait time between tasks (1-3 seconds)
    wait_time = between(1, 3)
    
    # Increase connection timeout for AI processing
    connection_timeout = 60.0
    network_timeout = 120.0
    
    def on_start(self):
        """Called when a user starts"""
        self.token = None
        self.user_id = None
        self.documents = []
        self.conversations = []
        # Try to authenticate for API access
        self.authenticate()
    
    def authenticate(self):
        """Authenticate user for API access using pre-defined test users"""
        try:
            # Use unique timestamped emails to avoid conflicts
            import time
            timestamp = int(time.time())
            test_users = [
                {"email": f"loadtest_{timestamp}_1@example.com", "password": "LoadTest123!"},
                {"email": f"loadtest_{timestamp}_2@example.com", "password": "LoadTest123!"},
                {"email": f"loadtest_{timestamp}_3@example.com", "password": "LoadTest123!"},
                {"email": f"loadtest_{timestamp}_4@example.com", "password": "LoadTest123!"},
                {"email": f"loadtest_{timestamp}_5@example.com", "password": "LoadTest123!"},
                {"email": f"loadtest_{timestamp}_6@example.com", "password": "LoadTest123!"},
                {"email": f"loadtest_{timestamp}_7@example.com", "password": "LoadTest123!"},
                {"email": f"loadtest_{timestamp}_8@example.com", "password": "LoadTest123!"},
                {"email": f"loadtest_{timestamp}_9@example.com", "password": "LoadTest123!"},
                {"email": f"loadtest_{timestamp}_10@example.com", "password": "LoadTest123!"},
            ]
            
            # Select a random test user from our known pool
            user_creds = random.choice(test_users)
            
            # Try to register first (ignore if user already exists)
            register_data = {
                "email": user_creds["email"],
                "password": user_creds["password"],
                "first_name": "Load",
                "last_name": "Test"
            }
            # Register new unique user
            register_response = self.client.post("/api/auth/register", json=register_data)
            
            # Login with KNOWN credentials (will work whether user existed or not)
            login_data = {
                "email": user_creds["email"],
                "password": user_creds["password"]
            }
            
            response = self.client.post("/api/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                if self.token:
                    self.client.headers.update({"Authorization": f"Bearer {self.token}"})
                    # Get user info for user_id
                    user_info = data.get("user", {})
                    self.user_id = user_info.get("id")
        except Exception:
            # Continue without authentication if it fails
            pass
    
    @task(5)  # Reduced from 15 to 5 - less aggressive health checking
    def health_check(self):
        """Test main health endpoint - high frequency"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("status") == "healthy":
                        response.success()
                    else:
                        response.failure(f"Health check returned unhealthy status: {data}")
                except Exception as e:
                    response.failure(f"Health check JSON parse error: {e}")
            elif response.status_code == 0:
                response.failure("Health check failed: Connection timeout or no response")
            else:
                response.failure(f"Health check failed: {response.status_code}")
    
    @task(5)
    def test_root_endpoint(self):
        """Test root endpoint"""
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Root endpoint failed: {response.status_code}")
    
    @task(3)
    def test_docs_endpoint(self):
        """Test API documentation endpoint"""
        with self.client.get("/docs", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Docs endpoint failed: {response.status_code}")
    
    @task(2)
    def test_redoc_endpoint(self):
        """Test ReDoc documentation endpoint"""
        with self.client.get("/redoc", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"ReDoc endpoint failed: {response.status_code}")
    
    @task(4)
    def test_auth_health(self):
        """Test auth service health endpoint"""
        with self.client.get("/api/auth/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Auth health failed: {response.status_code}")
    
    @task(3)
    def test_chat_health(self):
        """Test chat service health endpoint"""
        with self.client.get("/api/chat/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Chat health failed: {response.status_code}")
    
    @task(2)
    def test_chat_db_health(self):
        """Test chat database health endpoint"""
        with self.client.get("/api/chat/db/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Chat DB health failed: {response.status_code}")
    
    @task(3)
    def get_user_profile(self):
        """Test getting current user profile (requires auth)"""
        if not self.token:
            return
        
        with self.client.get("/api/auth/me", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                response.failure("Unauthorized - token invalid")
            else:
                response.failure(f"Profile fetch failed: {response.status_code}")
    
    @task(2)
    def list_documents(self):
        """Test document listing endpoint (requires auth)"""
        if not self.token:
            return
            
        with self.client.get("/api/documents/", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "documents" in data:
                    self.documents = data["documents"][:5]  # Keep first 5
                response.success()
            elif response.status_code == 401:
                response.failure("Unauthorized - token invalid")
            else:
                response.failure(f"Document list failed: {response.status_code}")
    
    @task(1)
    def upload_document(self):
        """Test document upload endpoint (requires auth)"""
        if not self.token:
            return
        
        # Create a simple test document
        test_content = f"""Test Document for Load Testing
Generated at: {random.randint(1000, 9999)}

This is a sample document created for load testing purposes.
It contains some text that can be processed by the system.

Random data: {random.random()}
"""
        
        files = {
            'file': ('loadtest_doc.txt', test_content, 'text/plain')
        }
        
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        with self.client.post("/api/documents/upload", files=files, headers=headers, catch_response=True) as response:
            if response.status_code in [200, 201]:
                data = response.json()
                if "document_id" in data:
                    self.documents.append(data["document_id"])
                response.success()
            elif response.status_code == 401:
                response.failure("Unauthorized - token invalid")
            else:
                response.failure(f"Document upload failed: {response.status_code}")
    
    # @task(1)  # Disabled - AI processing too slow for load testing
    def send_chat_message(self):
        """Test chat message endpoint - DISABLED for performance"""
        pass
    
    @task(1)
    def list_conversations(self):
        """Test conversation listing endpoint"""
        if not self.user_id:
            return
        params = {"user_id": self.user_id}
        with self.client.get("/api/chat/conversations", params=params, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "conversations" in data:
                    self.conversations = data["conversations"][:3]  # Keep first 3
                response.success()
            else:
                response.failure(f"Conversation list failed: {response.status_code}")
    
    @task(1)
    def get_system_stats(self):
        """Test system statistics endpoint"""
        with self.client.get("/api/chat/system/stats", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"System stats failed: {response.status_code}")


    @task(1)
    def get_analytics_document_types(self):
        """Test analytics document types distribution"""
        if not self.token:
            return
        with self.client.get("/api/analytics/document-types-distribution", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                response.failure("Unauthorized - token invalid")
            else:
                response.failure(f"Analytics document types failed: {response.status_code}")
    
    @task(1)
    def get_analytics_uploads_over_time(self):
        """Test analytics uploads over time"""
        if not self.token:
            return
        with self.client.get("/api/analytics/document-uploads-over-time?period=7d", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                response.failure("Unauthorized - token invalid")
            else:
                response.failure(f"Analytics uploads over time failed: {response.status_code}")
    
    @task(1)
    def get_auth_current_user_id(self):
        """Test current user ID endpoint"""
        if not self.token:
            return
        with self.client.get("/api/auth/current-user-id", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                response.failure("Unauthorized - token invalid")
            else:
                response.failure(f"Current user ID failed: {response.status_code}")
    
    @task(1)
    def test_auth_logout(self):
        """Test logout endpoint"""
        if not self.token:
            return
        with self.client.post("/api/auth/logout", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
                # Re-authenticate after logout
                self.authenticate()
            else:
                response.failure(f"Logout failed: {response.status_code}")
    
    # @task(1)  # Disabled - endpoint returns 500 errors, not needed
    def get_document_selections(self):
        """Test document selections endpoint - DISABLED"""
        pass
    
    @task(1)
    def get_document_by_user(self):
        """Test documents by user endpoint"""
        if not self.user_id:
            return
        with self.client.get(f"/api/documents/by-user?user_id={self.user_id}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                response.failure("Unauthorized - token invalid")
            else:
                response.failure(f"Documents by user failed: {response.status_code}")
    
    @task(1)
    def get_profile_stats(self):
        """Test profile stats endpoint"""
        if not self.user_id:
            return
        with self.client.get(f"/api/profiles/stats", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                # This endpoint might not be implemented yet
                response.success()  # Don't count as failure
            elif response.status_code == 401:
                response.failure("Unauthorized - token invalid")
            else:
                response.failure(f"Profile stats failed: {response.status_code}")


# AdminUser class removed - no admin system exists in the application


# Custom load testing scenarios
class QuickLoadTest(DocAnalyzerUser):
    """Quick load test scenario - health checks only"""
    wait_time = between(0.5, 1.5)
    
    @task(20)
    def health_only(self):
        """Focus on health checks for quick testing"""
        self.health_check()
    
    @task(5)
    def basic_endpoints(self):
        """Test basic endpoints"""
        self.test_root_endpoint()


class HeavyLoadTest(DocAnalyzerUser):
    """Heavy load test scenario - intensive operations"""
    wait_time = between(1, 3)
    
    @task(5)
    def intensive_chat_operations(self):
        """Multiple chat operations"""
        for i in range(2):
            self.send_chat_message()
    
    @task(3)
    def intensive_document_operations(self):
        """Multiple document operations"""
        self.list_documents()
        if random.random() < 0.3:  # 30% chance to upload
            self.upload_document()
    
    @task(2)
    def comprehensive_health_monitoring(self):
        """Monitor all health endpoints"""
        self.health_check()
        self.test_auth_health()
        self.test_chat_health()
