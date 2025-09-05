# #!/usr/bin/env python3
# """
# Startup script for DocAnalyzer backend
# """
# import os
# import sys
# import logging
# from pathlib import Path

# # Add the app directory to Python path
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# from app.db.init_db import initialize_database
# from app.main import app

# def setup_directories():
#     """Create necessary directories"""
#     directories = [
#         "logs",
#         "storage/documents",
#         "storage/thumbnails", 
#         "storage/processed"
#     ]
    
#     for directory in directories:
#         Path(directory).mkdir(parents=True, exist_ok=True)
#         print(f"✓ Created directory: {directory}")

# def main():
#     """Main startup function"""
#     print("🚀 Starting DocAnalyzer Backend...")
    
#     try:
#         # Setup directories
#         print("\n📁 Setting up directories...")
#         setup_directories()
        
#         # Initialize database
#         print("\n🗄️  Initializing database...")
#         initialize_database()
        
#         print("\n✅ Backend initialization completed successfully!")
#         print("\n🌐 Starting FastAPI server...")
#         print("📖 API Documentation: http://localhost:8000/docs")
#         print("🔍 Alternative Docs: http://localhost:8000/redoc")
        
#         # Start the server
#         import uvicorn
#         uvicorn.run(
#                 "app.main:app",
#                 host="0.0.0.0",
#                 port=8000,
#                 reload=False,  # Set to True for development
#                 log_level="info",
#                 reload_dirs=["app/"],
#                 reload_excludes=["logs/*", "storage/*", "*.log", "__pycache__/*"]
#             )
        
#     except Exception as e:
#         print(f"❌ Error during startup: {e}")
#         sys.exit(1)

# if __name__ == "__main__":
#     main()




#!/usr/bin/env python3
"""
Startup script for DocAnalyzer backend
"""
import os
import sys
import logging
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.db.init_db import initialize_database
from app.main import app
from app.services.chatbot.title_generation.title_listener import start_title_listener
import asyncio

def setup_directories():
    """Create necessary directories"""
    directories = [
        "logs",
        "storage/documents",
        "storage/thumbnails", 
        "storage/processed"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def main():
    """Main startup function"""
    print("🚀 Starting DocAnalyzer Backend...")
    
    try:
        # Setup directories
        print("\n📁 Setting up directories...")
        setup_directories()
        
        # Initialize database
        print("\n🗄️  Initializing database...")
        initialize_database()
        
        print("\n✅ Backend initialization completed successfully!")
        print("\n🌐 Starting FastAPI server...")
        print("📖 API Documentation: http://localhost:8000/docs")
        print("🔍 Alternative Docs: http://localhost:8000/redoc")
        
        # Start the server - clean configuration
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
        
    except Exception as e:
        print(f"❌ Error during startup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()