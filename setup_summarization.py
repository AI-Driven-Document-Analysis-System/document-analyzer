#!/usr/bin/env python3
"""
Setup script for the summarization system
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def install_backend_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing backend dependencies...")
    
    # Upgrade pip first
    if not run_command("python -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python packages"):
        return False
    
    return True

def check_database_connection():
    """Check if database connection is available"""
    print("\n🗄️  Checking database connection...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("⚠️  DATABASE_URL environment variable not set")
            print("   Please set it in your .env file")
            return False
        
        print("✅ DATABASE_URL is configured")
        return True
        
    except ImportError:
        print("❌ python-dotenv not installed")
        return False

def setup_database():
    """Set up database tables"""
    print("\n🏗️  Setting up database...")
    
    try:
        # Check if app directory exists
        app_dir = Path("app")
        if not app_dir.exists():
            print("❌ app directory not found")
            return False
        
        # Try to run database initialization
        if run_command("python -m app.db.init_db", "Initializing database tables"):
            print("✅ Database setup completed")
            return True
        else:
            print("⚠️  Database setup failed - you may need to run it manually")
            return False
            
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        return False

def check_frontend():
    """Check if frontend is properly set up"""
    print("\n🎨 Checking frontend setup...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ frontend directory not found")
        return False
    
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        print("❌ package.json not found in frontend directory")
        return False
    
    print("✅ Frontend directory found")
    
    # Check if node_modules exists
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("⚠️  Frontend dependencies not installed")
        print("   Run 'cd frontend && npm install' to install them")
        return False
    
    print("✅ Frontend dependencies are installed")
    return True

def create_env_template():
    """Create a template .env file if it doesn't exist"""
    print("\n📝 Creating environment template...")
    
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    template = """# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# API Configuration
API_HOST=localhost
API_PORT=8000

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Logging
LOG_LEVEL=INFO

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(template)
        print("✅ .env template created")
        print("   Please update it with your actual configuration")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env template: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Document Analyzer Summarization System")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install backend dependencies
    if not install_backend_dependencies():
        print("\n❌ Backend setup failed")
        sys.exit(1)
    
    # Check database connection
    if not check_database_connection():
        print("\n⚠️  Database connection not configured")
        print("   Please set up your database and update .env file")
    
    # Create environment template
    create_env_template()
    
    # Setup database
    setup_database()
    
    # Check frontend
    check_frontend()
    
    print("\n" + "=" * 60)
    print("🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Update your .env file with database credentials")
    print("2. Start the backend: uvicorn app.main:app --reload")
    print("3. Start the frontend: cd frontend && npm run dev")
    print("4. Test the system: python test_summarization.py")
    print("\nFor more information, see SUMMARIZATION_README.md")

if __name__ == "__main__":
    main()
