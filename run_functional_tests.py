"""
Functional Test Runner
Run this script to execute all functional tests
"""
import os
import sys
import pytest

def run_tests():
    """Run the functional tests"""
    # Add the project root to the Python path
    project_root = os.path.abspath(os.path.dirname(__file__))
    sys.path.insert(0, project_root)
    
    # Run the tests
    test_dir = os.path.join(project_root, 'tests', 'functional_testing', 'tests')
    return pytest.main([
        test_dir,
        "-v",
        "--html=test_reports/functional_test_report.html",
        "--self-contained-html"
    ])

if __name__ == "__main__":
    # Create test reports directory if it doesn't exist
    os.makedirs('test_reports', exist_ok=True)
    sys.exit(run_tests())
