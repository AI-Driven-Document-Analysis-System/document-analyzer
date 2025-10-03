"""
Simple Test Runner
A straightforward test runner without Unicode characters
"""
import os
import sys
import subprocess
from datetime import datetime

def run_tests():
    """Run all test suites"""
    print("\n" + "=" * 80)
    print("  FUNCTIONAL TESTING")
    print("  " + "=" * 80)
    
    # List of test files to run
    test_files = [
        "tests/test_user_registration.py",
        "tests/test_document_upload.py",
        "tests/test_chat_functionality.py",
        "tests/test_summary_generation.py"
    ]
    
    # Run each test file
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\nRunning tests in: {test_file}")
            print("-" * 80)
            
            # Run pytest on the test file
            result = subprocess.run(
                ["pytest", test_file, "-v"],
                capture_output=True,
                text=True
            )
            
            # Print the test results
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
        else:
            print(f"\nTest file not found: {test_file}")
    
    print("\n" + "=" * 80)
    print("  TESTING COMPLETED")
    print("  " + "=" * 80)

if __name__ == "__main__":
    run_tests()
