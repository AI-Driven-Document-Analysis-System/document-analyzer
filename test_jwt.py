#!/usr/bin/env python3
"""
Test script to verify JWT authentication is working
"""
import os
import sys
import jwt
from datetime import datetime, timedelta

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_jwt_creation():
    """Test JWT token creation and verification"""
    try:
        from app.core.security import create_access_token, verify_token, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
        
        print("🔑 Testing JWT functionality...")
        print(f"SECRET_KEY: {SECRET_KEY[:20]}...")
        print(f"ACCESS_TOKEN_EXPIRE_MINUTES: {ACCESS_TOKEN_EXPIRE_MINUTES}")
        
        # Test data
        test_data = {
            "sub": "test-user-id-123",
            "email": "test@example.com"
        }
        
        # Create token
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(data=test_data, expires_delta=expires_delta)
        
        print(f"✅ Token created successfully: {token[:50]}...")
        
        # Verify token
        payload = verify_token(token)
        if payload:
            print(f"✅ Token verified successfully")
            print(f"   User ID: {payload.get('sub')}")
            print(f"   Email: {payload.get('email')}")
            print(f"   Expires: {datetime.fromtimestamp(payload.get('exp'))}")
        else:
            print("❌ Token verification failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ JWT test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment():
    """Test environment variables"""
    print("\n🌍 Testing environment variables...")
    
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'ACCESS_TOKEN_EXPIRE_MINUTES'
    ]
    
    all_good = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:30] if len(value) > 30 else value}")
        else:
            print(f"❌ {var}: Not set")
            all_good = False
    
    return all_good

def main():
    """Main test function"""
    print("🚀 Starting JWT Authentication Tests...\n")
    
    # Test environment
    env_ok = test_environment()
    
    # Test JWT functionality
    jwt_ok = test_jwt_creation()
    
    print("\n" + "="*50)
    if env_ok and jwt_ok:
        print("🎉 All tests passed! JWT authentication should work properly.")
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
    
    return env_ok and jwt_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)