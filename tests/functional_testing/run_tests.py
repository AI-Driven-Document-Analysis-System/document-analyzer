"""
Test Runner Script
Run this script to execute the functional tests
"""
import os
import sys
import pytest

def run_tests():
    """Run the functional tests"""
    # Add the project root to the Python path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    sys.path.insert(0, project_root)
    
    # Run the tests
    test_dir = os.path.join(os.path.dirname(__file__), 'tests')
    return pytest.main([
        test_dir,
        "-v",
        "--html=reports/test_report.html",
        "--self-contained-html"
    ])

if __name__ == "__main__":
    sys.exit(run_tests())
