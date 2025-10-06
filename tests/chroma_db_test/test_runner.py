#!/usr/bin/env python3
"""
ChromaDB Test Runner - Main entry point for all ChromaDB tests
"""

import os
import sys
import time
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

from metadata_filtering_test import MetadataFilteringTest
from performance_test import PerformanceTest
from concurrent_access_test import ConcurrentAccessTest
from corruption_recovery_test import CorruptionRecoveryTest
from embedding_consistency_test import EmbeddingConsistencyTest
from integration_test import IntegrationTest


class ChromaDBTestRunner:
    """Main test runner for ChromaDB test suite"""
    
    def __init__(self):
        self.tests = [
            MetadataFilteringTest(),
            PerformanceTest(),
            ConcurrentAccessTest(),
            CorruptionRecoveryTest(),
            EmbeddingConsistencyTest(),
            IntegrationTest()
        ]
        self.results = {}
    
    def run_all_tests(self):
        """Run all ChromaDB tests and report results"""
        print("ChromaDB Test Suite")
        print("=" * 60)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for test in self.tests:
            print(f"\nRunning {test.__class__.__name__}...")
            print("-" * 40)
            
            try:
                start_time = time.time()
                result = test.run()
                end_time = time.time()
                
                test_name = test.__class__.__name__
                self.results[test_name] = {
                    'status': 'PASSED' if result else 'FAILED',
                    'duration': end_time - start_time,
                    'details': getattr(test, 'last_result_details', 'No details available')
                }
                
                if result:
                    passed_tests += 1
                    print(f"RESULT: PASSED ({end_time - start_time:.2f}s)")
                else:
                    failed_tests += 1
                    print(f"RESULT: FAILED ({end_time - start_time:.2f}s)")
                
                total_tests += 1
                
            except Exception as e:
                failed_tests += 1
                total_tests += 1
                test_name = test.__class__.__name__
                self.results[test_name] = {
                    'status': 'ERROR',
                    'duration': 0,
                    'details': str(e)
                }
                print(f"RESULT: ERROR - {str(e)}")
        
        self.print_summary(total_tests, passed_tests, failed_tests)
    
    def print_summary(self, total, passed, failed):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "0%")
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\nDETAILED RESULTS:")
        print("-" * 40)
        for test_name, result in self.results.items():
            status = result['status']
            duration = result['duration']
            print(f"{test_name}: {status} ({duration:.2f}s)")
            if result['details'] and status != 'PASSED':
                print(f"  Details: {result['details']}")


def main():
    """Main function"""
    runner = ChromaDBTestRunner()
    runner.run_all_tests()


if __name__ == "__main__":
    main()
