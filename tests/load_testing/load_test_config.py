"""
Load Testing Configuration
Defines different test scenarios and their parameters
"""

# Test scenarios as defined in HOW_TO_CONDUCT_TESTS.md
LOAD_TEST_SCENARIOS = {
    "basic": {
        "name": "Basic Load Test",
        "description": "Start with 10 users, spawn rate 1 user per second",
        "users": 10,
        "spawn_rate": 1,
        "run_time": "5m",
        "expected_response_time": 2.0,  # seconds
        "expected_failure_rate": 0.01,  # 1%
        "user_class": "DocAnalyzerUser"
    },
    
    "conservative": {
        "name": "Conservative Load Test",
        "description": "20 users with 1.2 users per second spawn rate - safe production load",
        "users": 20,
        "spawn_rate": 1.2,
        "run_time": "6m",
        "expected_response_time": 1.2,
        "expected_failure_rate": 0.003,  # 0.3%
        "user_class": "DocAnalyzerUser"
    },
    
    "production": {
        "name": "Production Load Test",
        "description": "30 users with 1.5 users per second spawn rate - target production load",
        "users": 30,
        "spawn_rate": 1.5,
        "run_time": "8m",
        "expected_response_time": 1.5,
        "expected_failure_rate": 0.005,  # 0.5%
        "user_class": "DocAnalyzerUser"
    },
    
    "moderate": {
        "name": "Moderate Load Test", 
        "description": "50 users with 2 users per second spawn rate",
        "users": 50,
        "spawn_rate": 2,
        "run_time": "10m",
        "expected_response_time": 2.0,
        "expected_failure_rate": 0.01,
        "user_class": "DocAnalyzerUser"
    },
    
    "heavy": {
        "name": "Heavy Load Test",
        "description": "100 users with 5 users per second spawn rate", 
        "users": 100,
        "spawn_rate": 5,
        "run_time": "15m",
        "expected_response_time": 3.0,  # Allow higher response time
        "expected_failure_rate": 0.02,  # 2%
        "user_class": "HeavyLoadTest"
    },
    
    "spike": {
        "name": "Spike Test",
        "description": "Sudden spike to 200 users",
        "users": 200,
        "spawn_rate": 20,  # Fast spawn rate for spike
        "run_time": "5m",
        "expected_response_time": 5.0,  # Higher tolerance for spike
        "expected_failure_rate": 0.05,  # 5%
        "user_class": "DocAnalyzerUser"
    },
    
    "endurance": {
        "name": "Endurance Test",
        "description": "Sustained load over extended period",
        "users": 30,
        "spawn_rate": 1,
        "run_time": "60m",  # 1 hour
        "expected_response_time": 2.0,
        "expected_failure_rate": 0.01,
        "user_class": "DocAnalyzerUser"
    },
    
    "quick": {
        "name": "Quick Health Check",
        "description": "Fast test focusing on health endpoints",
        "users": 5,
        "spawn_rate": 2,
        "run_time": "2m",
        "expected_response_time": 1.0,
        "expected_failure_rate": 0.001,
        "user_class": "QuickLoadTest"
    }
}

# API endpoints to monitor during load testing
MONITORED_ENDPOINTS = {
    "/health": {
        "name": "Health Check",
        "expected_response_time": 100,  # ms
        "critical": True
    },
    "/api/auth/login": {
        "name": "User Login",
        "expected_response_time": 500,
        "critical": True
    },
    "/api/documents/upload": {
        "name": "Document Upload",
        "expected_response_time": 2000,
        "critical": True
    },
    "/api/chat/query": {
        "name": "Chat Query",
        "expected_response_time": 3000,
        "critical": True
    },
    "/api/summarization/generate": {
        "name": "Document Summarization",
        "expected_response_time": 5000,
        "critical": False
    },
    "/api/documents/list": {
        "name": "Document List",
        "expected_response_time": 300,
        "critical": False
    },
    "/api/analytics/dashboard": {
        "name": "Analytics Dashboard",
        "expected_response_time": 1000,
        "critical": False
    }
}

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    "response_time_95th_percentile": 2000,  # ms
    "response_time_99th_percentile": 5000,  # ms
    "max_failure_rate": 0.01,  # 1%
    "min_requests_per_second": 10,
    "max_cpu_usage": 80,  # %
    "max_memory_usage": 80,  # %
    "max_database_connections": 20
}

# Test data configuration
TEST_DATA = {
    "sample_documents": [
        {
            "name": "sample_report.txt",
            "content": """
            Annual Performance Report
            
            Executive Summary:
            This report provides an overview of our company's performance 
            during the fiscal year. Key metrics include revenue growth,
            customer satisfaction, and operational efficiency.
            
            Key Findings:
            - Revenue increased by 15% year-over-year
            - Customer satisfaction scores improved to 4.2/5.0
            - Operational costs reduced by 8%
            
            Recommendations:
            1. Continue investment in customer service
            2. Expand marketing efforts in emerging markets
            3. Optimize supply chain processes
            """
        },
        {
            "name": "technical_spec.txt", 
            "content": """
            Technical Specification Document
            
            System Architecture:
            The system follows a microservices architecture with the following components:
            - API Gateway for request routing
            - Authentication service for user management
            - Document processing service for file handling
            - Vector database for semantic search
            
            Performance Requirements:
            - Response time: < 2 seconds for 95% of requests
            - Throughput: > 1000 requests per minute
            - Availability: 99.9% uptime
            
            Security Considerations:
            - JWT-based authentication
            - HTTPS encryption for all communications
            - Input validation and sanitization
            """
        }
    ],
    
    "sample_queries": [
        "What is the main topic of this document?",
        "Can you summarize the key points?",
        "What are the performance metrics mentioned?",
        "What recommendations are provided?",
        "Explain the technical architecture",
        "What security measures are described?",
        "How did revenue change year-over-year?",
        "What is the customer satisfaction score?",
        "List the system components mentioned",
        "What are the performance requirements?"
    ]
}

# Environment-specific configurations
ENVIRONMENTS = {
    "local": {
        "host": "http://localhost:8000",
        "database_url": "postgresql://localhost:5432/document_analyzer_test",
        "minio_url": "http://localhost:9000"
    },
    
    "staging": {
        "host": "http://staging.docanalyzer.com",
        "database_url": "postgresql://staging-db:5432/document_analyzer",
        "minio_url": "http://staging-minio:9000"
    },
    
    "production": {
        "host": "https://api.docanalyzer.com",
        "database_url": "postgresql://prod-db:5432/document_analyzer",
        "minio_url": "https://storage.docanalyzer.com"
    }
}
