#!/usr/bin/env python3
"""
Load Testing Setup Script for DocAnalyzer

This script sets up the load testing environment by:
1. Installing required dependencies
2. Creating necessary directories
3. Validating the setup
4. Running a quick test

Usage:
    python tests/load_testing/setup_load_testing.py
"""

import subprocess
import sys
import os
from pathlib import Path
import requests
import time


def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_step(step, description):
    """Print a formatted step"""
    print(f"\n🔧 Step {step}: {description}")
    print("-" * 40)


def run_command(command, description=""):
    """Run a command and handle errors"""
    try:
        print(f"Running: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Success: {description}")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Failed: {description}")
            print(f"Error: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported")
        print("Please use Python 3.8 or higher")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def install_dependencies():
    """Install required dependencies"""
    dependencies = [
        "locust==2.17.0",
        "psutil>=5.9.0",
        "requests>=2.28.0",
        "pandas>=1.5.0"  # Optional for detailed analysis
    ]
    
    print("Installing load testing dependencies...")
    
    for dep in dependencies:
        print(f"\n📦 Installing {dep}...")
        success = run_command(f"pip install {dep}", f"Install {dep}")
        
        if not success:
            print(f"⚠️  Failed to install {dep}")
            if "pandas" in dep:
                print("   Note: pandas is optional for detailed analysis")
            else:
                return False
    
    return True


def create_directories():
    """Create necessary directories"""
    directories = [
        "tests/load_testing/results",
        "tests/load_testing/logs"
    ]
    
    print("Creating directories...")
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")
    
    return True


def validate_setup():
    """Validate that the setup is working"""
    print("Validating setup...")
    
    # Check if locust is installed
    try:
        import locust
        print(f"✅ Locust {locust.__version__} is installed")
    except ImportError:
        print("❌ Locust is not installed properly")
        return False
    
    # Check if psutil is installed
    try:
        import psutil
        print(f"✅ psutil {psutil.__version__} is installed")
    except ImportError:
        print("❌ psutil is not installed properly")
        return False
    
    # Check if test files exist
    test_files = [
        "tests/load_testing/locustfile.py",
        "tests/load_testing/load_test_config.py",
        "tests/load_testing/run_load_tests.py"
    ]
    
    for file_path in test_files:
        if Path(file_path).exists():
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            return False
    
    return True


def test_api_connection():
    """Test connection to the API"""
    api_url = "http://localhost:8000"
    
    print(f"Testing API connection to {api_url}...")
    
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ API is running and healthy")
            return True
        else:
            print(f"⚠️  API responded with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"⚠️  API is not running at {api_url}")
        print("   Start your API server with: python run.py")
        return False
    except Exception as e:
        print(f"⚠️  Error connecting to API: {e}")
        return False


def run_quick_test():
    """Run a quick load test to verify everything works"""
    print("Running quick validation test...")
    
    # First check if API is running
    if not test_api_connection():
        print("⚠️  Skipping quick test - API not available")
        return True  # Don't fail setup for this
    
    # Run a very short test
    command = (
        "locust -f tests/load_testing/locustfile.py "
        "--host http://localhost:8000 "
        "--users 2 --spawn-rate 1 --run-time 10s --headless"
    )
    
    print("Running 10-second test with 2 users...")
    success = run_command(command, "Quick load test")
    
    if success:
        print("✅ Quick test completed successfully!")
    else:
        print("⚠️  Quick test failed - check your API server")
    
    return success


def show_usage_instructions():
    """Show usage instructions"""
    print_header("Load Testing Setup Complete!")
    
    print("""
🎉 Load testing environment is ready!

📋 Quick Start Commands:

1. List available test scenarios:
   python tests/load_testing/run_load_tests.py --list-scenarios

2. Run basic load test:
   python tests/load_testing/run_load_tests.py --scenario basic

3. Run progressive testing (recommended):
   python tests/load_testing/run_load_tests.py --progressive

4. Monitor performance during tests:
   python tests/load_testing/monitor_performance.py --duration 300

5. Use Locust web interface:
   locust -f tests/load_testing/locustfile.py --host=http://localhost:8000
   Then open: http://localhost:8089

📊 Available Test Scenarios:
   - quick: 5 users, 2 minutes (health check focus)
   - basic: 10 users, 5 minutes (recommended start)
   - moderate: 50 users, 10 minutes
   - heavy: 100 users, 15 minutes
   - spike: 200 users, 5 minutes (stress test)
   - endurance: 30 users, 60 minutes (long-term stability)

📁 Results will be saved to: tests/load_testing/results/

📖 For detailed instructions, see: tests/load_testing/README.md

⚠️  Important Notes:
   - Make sure your API server is running: python run.py
   - Start with basic scenarios before heavy testing
   - Monitor system resources during tests
   - Don't run heavy tests on production systems

🆘 Troubleshooting:
   - If tests fail, check API server logs
   - Ensure database and external services are running
   - Review the README.md for common issues
""")


def main():
    """Main setup function"""
    print_header("DocAnalyzer Load Testing Setup")
    
    # Step 1: Check Python version
    print_step(1, "Checking Python version")
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Install dependencies
    print_step(2, "Installing dependencies")
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Step 3: Create directories
    print_step(3, "Creating directories")
    if not create_directories():
        print("❌ Failed to create directories")
        sys.exit(1)
    
    # Step 4: Validate setup
    print_step(4, "Validating setup")
    if not validate_setup():
        print("❌ Setup validation failed")
        sys.exit(1)
    
    # Step 5: Test API connection (optional)
    print_step(5, "Testing API connection")
    test_api_connection()
    
    # Step 6: Run quick test (optional)
    print_step(6, "Running quick validation test")
    run_quick_test()
    
    # Show usage instructions
    show_usage_instructions()
    
    print("\n✅ Setup completed successfully!")


if __name__ == "__main__":
    main()
