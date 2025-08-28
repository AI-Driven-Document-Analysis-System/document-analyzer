#!/usr/bin/env python3
"""
Minimal test backend to verify core functionality
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_minimal_imports():
    """Test minimal imports without heavy dependencies"""
    try:
        print("🔧 Testing minimal imports...")
        
        # Test core security
        from app.core.security import create_access_token, verify_token, SECRET_KEY
        print("✅ Core security imported successfully")
        
        # Test database manager
        from app.core.database import db_manager
        print("✅ Database manager imported successfully")
        
        # Test auth API
        from app.api.auth import router as auth_router
        print("✅ Auth API imported successfully")
        
        # Test documents API
        from app.api.documents import router as documents_router
        print("✅ Documents API imported successfully")
        
        # Test user schemas
        from app.schemas.user_schemas import UserResponse
        print("✅ User schemas imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_jwt_with_real_data():
    """Test JWT with realistic user data"""
    try:
        print("\n🔑 Testing JWT with realistic data...")
        
        from app.core.security import create_access_token, verify_token
        from datetime import timedelta
        
        # Test data similar to what would be used in real auth
        test_user_data = {
            "sub": "550e8400-e29b-41d4-a716-446655440000",  # UUID format
            "email": "test@example.com",
            "user_type": "standard"
        }
        
        # Create token
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data=test_user_data, expires_delta=expires_delta)
        
        print(f"✅ Token created: {token[:50]}...")
        
        # Verify token
        payload = verify_token(token)
        if payload:
            print("✅ Token verified successfully")
            print(f"   User ID: {payload.get('sub')}")
            print(f"   Email: {payload.get('email')}")
            return True
        else:
            print("❌ Token verification failed")
            return False
            
    except Exception as e:
        print(f"❌ JWT test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection():
    """Test database connection"""
    try:
        print("\n🗄️  Testing database connection...")
        
        from app.core.database import db_manager
        
        # Test if we can get connection status
        status = db_manager.get_pool_status()
        print(f"Database pool status: {status['status']}")
        
        if status['status'] == 'initialized':
            print("✅ Database pool initialized")
            return True
        else:
            print(f"⚠️  Database pool status: {status}")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Minimal Backend Tests...\n")
    
    # Test minimal imports
    imports_ok = test_minimal_imports()
    
    # Test JWT with real data
    jwt_ok = test_jwt_with_real_data()
    
    # Test database connection
    db_ok = test_database_connection()
    
    print("\n" + "="*50)
    if imports_ok and jwt_ok and db_ok:
        print("🎉 All minimal tests passed! Core functionality should work.")
        print("✅ JWT authentication is working")
        print("✅ Database connection is available")
        print("✅ API endpoints can be imported")
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
    
    return imports_ok and jwt_ok and db_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)