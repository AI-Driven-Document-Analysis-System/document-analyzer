#!/usr/bin/env python3
"""
Test runner for vector_db unit tests.
This script runs all unit tests for the vector_db module and provides a summary.
"""

import unittest
import sys
import os

# Add the current directory and backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

class CustomTestResult(unittest.TestResult):
    """Custom test result class that shows individual test results with emojis."""
    
    def __init__(self, stream=None, descriptions=None, verbosity=None):
        super().__init__(stream, descriptions, verbosity)
        self.test_results = []
    
    def addSuccess(self, test):
        super().addSuccess(test)
        test_name = f"{test._testMethodName}"
        self.test_results.append(('✅', test_name))
        print(f"✅ PASS: {test_name}")
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        test_name = f"{test._testMethodName}"
        self.test_results.append(('❌', test_name))
        print(f"❌ FAIL: {test_name}")
        print(f"   Error: {err[1]}")
    
    def addError(self, test, err):
        super().addError(test, err)
        test_name = f"{test._testMethodName}"
        self.test_results.append(('❌', test_name))
        print(f"❌ ERROR: {test_name}")
        print(f"   Error: {err[1]}")

def run_all_tests():
    """Run all unit tests for the vector_db module."""
    print("🧪 Running Vector DB Unit Tests")
    print("=" * 60)
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Create custom test runner
    runner = unittest.TextTestRunner(verbosity=0, resultclass=CustomTestResult)
    
    # Run tests
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for status, _ in result.test_results if status == '✅')
    failed = sum(1 for status, _ in result.test_results if status == '❌')
    
    print(f"Total tests: {len(result.test_results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed > 0:
        print("\n❌ FAILED TESTS:")
        for status, test in result.test_results:
            if status == '❌':
                print(f"  - {test}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    
    return result.wasSuccessful()

def run_individual_test_file(test_file):
    """Run a specific test file with detailed output."""
    print(f"🧪 Running {test_file}")
    print("=" * 60)
    
    # Check if it's in vector_db subfolder
    vector_db_test_path = os.path.join(os.path.dirname(__file__), 'vector_db', test_file)
    if os.path.exists(vector_db_test_path):
        print(f"Found in vector_db subfolder: {test_file}")
        # Add the backend directory to the path BEFORE importing
        backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        print(f"Added backend path: {backend_path}")
        
        # Import the test module directly
        test_module_name = f'tests.vector_db.{test_file.replace(".py", "")}'
        print(f"Importing: {test_module_name}")
    else:
        # Direct test file
        test_module_name = f'tests.{test_file.replace(".py", "")}'
        print(f"Using direct test file: {test_module_name}")
    
    try:
        # Import the test module
        test_module = __import__(test_module_name, fromlist=['*'])
        
        # Create test suite from the module
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(test_module)
        
        # Run tests with custom result
        runner = unittest.TextTestRunner(verbosity=0, resultclass=CustomTestResult)
        result = runner.run(suite)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for status, _ in result.test_results if status == '✅')
        failed = sum(1 for status, _ in result.test_results if status == '❌')
        
        print(f"Total tests: {len(result.test_results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for status, test in result.test_results:
                if status == '❌':
                    print(f"  - {test}")
        
        if failed == 0:
            print("\n🎉 All tests passed!")
            print("\n✅ PASSED TESTS:")
            for status, test in result.test_results:
                if status == '✅':
                    print(f"  - {test}")
        
        return result.wasSuccessful()
        
    except ImportError as e:
        print(f"❌ ERROR: Could not import {test_file}: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: Failed to run tests: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run specific test file
        test_name = sys.argv[1]
        success = run_individual_test_file(test_name)
    else:
        # Run all tests
        success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1) 