#!/usr/bin/env python3
"""
Simple backend startup script for DocAnalyzer
"""
import os
import sys
import logging
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def setup_logging():
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/app.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are available"""
    logger = logging.getLogger(__name__)
    
    required_modules = [
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('PyJWT', 'jwt'),
        ('passlib', 'passlib'),
        ('psycopg2', 'psycopg2'),
        ('minio', 'minio'),
        ('python-multipart', 'multipart')
    ]
    
    missing_modules = []
    for display_name, import_name in required_modules:
        try:
            __import__(import_name)
            logger.info(f"✅ {display_name} available")
        except ImportError:
            missing_modules.append(display_name)
            logger.error(f"❌ {display_name} not available")
    
    if missing_modules:
        logger.error(f"Missing modules: {missing_modules}")
        logger.error("Please install missing dependencies with: pip install -r requirements.txt")
        return False
    
    return True

def check_environment():
    """Check if required environment variables are set"""
    logger = logging.getLogger(__name__)
    
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            logger.error(f"❌ {var} not set")
        else:
            logger.info(f"✅ {var} configured")
    
    if missing_vars:
        logger.error(f"Missing environment variables: {missing_vars}")
        logger.error("Please check your .env file")
        return False
    
    return True

def start_backend():
    """Start the FastAPI backend"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🚀 Starting DocAnalyzer Backend...")
        
        # Check dependencies
        if not check_dependencies():
            logger.error("❌ Dependency check failed")
            return False
        
        # Check environment
        if not check_environment():
            logger.error("❌ Environment check failed")
            return False
        
        # Import and start the app
        logger.info("📦 Importing application...")
        from app.main_minimal import app
        
        logger.info("✅ Application imported successfully")
        logger.info("🌐 Starting FastAPI server...")
        logger.info("📖 API Documentation: http://localhost:8000/docs")
        logger.info("🔍 Alternative Docs: http://localhost:8000/redoc")
        
        # Start the server
        import uvicorn
        uvicorn.run(
            "app.main_minimal:app",  # Use import string for reload support
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start backend: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger = setup_logging()
    
    try:
        start_backend()
    except KeyboardInterrupt:
        logger.info("🛑 Backend stopped by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)