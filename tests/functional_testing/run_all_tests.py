# run_all_tests.py
"""
Main Test Executor
Runs all functional tests with monitoring and reporting
"""

import subprocess
import json
import os
import sys
import io
import sys
from datetime import datetime
from utilities.system_monitor import SystemMonitor
from utilities.data_generator import TestDataGenerator
import time

# Set up console output to handle Unicode
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class TestExecutor:
    def __init__(self):
        self.monitor = SystemMonitor()
        self.test_results = []
        self.start_time = None
        self.end_time = None
        
        # Create necessary directories
        os.makedirs('config', exist_ok=True)
        os.makedirs('tests', exist_ok=True)
        os.makedirs('utilities', exist_ok=True)
        os.makedirs('test_files', exist_ok=True)
        os.makedirs('screenshots', exist_ok=True)
        os.makedirs('reports', exist_ok=True)
        
    def print_header(self, text):
        """Print formatted header"""
        print("\n" + "="*80)
        print(f"  {text}")
        print("="*80 + "\n")
    
    def setup_test_environment(self):
        """Setup test environment and generate test data"""
        self.print_header("PHASE 1: TEST ENVIRONMENT SETUP")
        
        print("Step 1: Checking configuration files...")
        if not os.path.exists('config/config.json'):
            print("⚠ config.json not found. Creating default configuration...")
            self.create_default_config()
        else:
            print("✓ Configuration file exists")
        
        print("\nStep 2: Generating test data...")
        generator = TestDataGenerator()
        generator.save_test_data('config/test_data.json')
        print("✓ Test data generated successfully")
        
        print("\nStep 3: Creating test files...")
        pdf_file = generator.generate_test_file('pdf', 1, "Sample PDF for Testing")
        txt_file = generator.generate_test_file('txt', 1)
        print(f"✓ PDF file created: {pdf_file}")
        print(f"✓ TXT file created: {txt_file}")
        
        print("\n✅ Test environment setup complete!")
        time.sleep(2)
    
    def create_default_config(self):
        """Create default configuration file"""
        config = {
            "base_url": "http://localhost:3000",
            "minio_url": "http://localhost:9000",
            "timeout": 30,
            "screenshot_on_failure": True,
            "browser": "chrome",
            "headless": False,
            "test_users": {
                "valid_user": {
                    "email": "testuser@example.com",
                    "password": "SecurePass123!",
                    "name": "Test User"
                }
            },
            "performance_thresholds": {
                "max_response_time": 3000,
                "max_cpu_usage": 80,
                "max_memory_usage": 70
            }
        }
        
        with open('config/config.json', 'w') as f:
            json.dump(config, f, indent=2)
    
    def run_test_suite(self, test_file, test_name):
        """Run a specific test suite"""
        print(f"\n▶ Running {test_name}...")
        print(f"  Test file: {test_file}")
        
        start = datetime.now()
        
        try:
            # Run pytest
            result = subprocess.run(
                ['pytest', test_file, '-v', '--tb=short'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            end = datetime.now()
            duration = (end - start).total_seconds()
            
            # Parse results
            passed = result.stdout.count('PASSED')
            failed = result.stdout.count('FAILED')
            
            test_result = {
                "suite_name": test_name,
                "test_file": test_file,
                "status": "PASS" if result.returncode == 0 else "FAIL",
                "passed": passed,
                "failed": failed,
                "duration_seconds": duration,
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
                "output": result.stdout
            }
            
            print(f"  ✓ Completed in {duration:.2f} seconds")
            print(f"  Results: {passed} passed, {failed} failed")
            
        except subprocess.TimeoutExpired:
            test_result = {
                "suite_name": test_name,
                "test_file": test_file,
                "status": "TIMEOUT",
                "error": "Test suite exceeded timeout limit"
            }
            print(f"  ⚠ Test suite timed out")
        
        except Exception as e:
            test_result = {
                "suite_name": test_name,
                "test_file": test_file,
                "status": "ERROR",
                "error": str(e)
            }
            print(f"  ✗ Error: {str(e)}")
        
        self.test_results.append(test_result)
        return test_result
    
    def run_all_tests(self):
        """Execute all test suites"""
        self.start_time = datetime.now()
        print(f"Test execution started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Start system monitoring
        self.monitor.start_monitoring(interval=2)
        
        test_suites = [
            ("tests/test_user_registration.py", "User Registration Tests"),
            ("tests/test_document_upload.py", "Document Upload Tests"),
            ("tests/test_chat_functionality.py", "Chat Functionality Tests"),
            ("tests/test_summary_generation.py", "Summary Generation Tests")
        ]
        
        # Run each test suite
        for i, (test_file, test_name) in enumerate(test_suites, 1):
            print(f"\n[{i}/{len(test_suites)}] Test Suite: {test_name}")

            print("-" * 80)
            
            if os.path.exists(test_file):
                self.run_test_suite(test_file, test_name)
            else:
                print(f"  ⚠ Test file not found: {test_file}")
                self.test_results.append({
                    "suite_name": test_name,
                    "test_file": test_file,
                    "status": "SKIPPED",
                    "reason": "Test file not found"
                })
            
            time.sleep(2)  # Brief pause between suites
        
        # Stop monitoring
        self.end_time = datetime.now()
        self.monitor.stop_monitoring()
        
        print("\n" + "="*80)
        print("  TESTING EXECUTION COMPLETED")
        print("="*80)
    
    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        self.print_header("PHASE 3: REPORT GENERATION")
        
        total_duration = (self.end_time - self.start_time).total_seconds()
        
        # Calculate statistics
        total_suites = len(self.test_results)
        passed_suites = sum(1 for r in self.test_results if r.get('status') == 'PASS')
        failed_suites = sum(1 for r in self.test_results if r.get('status') == 'FAIL')
        skipped_suites = sum(1 for r in self.test_results if r.get('status') == 'SKIPPED')
        
        total_tests = sum(r.get('passed', 0) + r.get('failed', 0) for r in self.test_results)
        total_passed = sum(r.get('passed', 0) for r in self.test_results)
        total_failed = sum(r.get('failed', 0) for r in self.test_results)
        
        # Get system metrics
        system_summary = self.monitor.get_summary()
        
        # Create comprehensive report
        report = {
            "test_execution": {
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "total_duration_seconds": total_duration,
                "total_duration_formatted": f"{int(total_duration//60)}m {int(total_duration%60)}s"
            },
            "test_summary": {
                "total_test_suites": total_suites,
                "passed_suites": passed_suites,
                "failed_suites": failed_suites,
                "skipped_suites": skipped_suites,
                "total_test_cases": total_tests,
                "passed_test_cases": total_passed,
                "failed_test_cases": total_failed,
                "success_rate": f"{(total_passed/total_tests*100):.1f}%" if total_tests > 0 else "N/A"
            },
            "system_performance": system_summary,
            "test_results": self.test_results,
            "screenshots_directory": "screenshots/",
            "test_files_directory": "test_files/"
        }
        
        # Save JSON report
        report_filename = f"reports/functional_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✓ JSON report saved: {report_filename}")
        
        # Generate HTML report
        html_report = self.generate_html_report(report)
        html_filename = report_filename.replace('.json', '.html')
        with open(html_filename, 'w') as f:
            f.write(html_report)
        
        print(f"✓ HTML report saved: {html_filename}")
        
        # Print summary to console
        self.print_test_summary(report)
        
        return report
    
    def print_test_summary(self, report):
        """Print test summary to console"""
        self.print_header("FUNCTIONAL TESTING SUMMARY REPORT")
        
        exec_info = report['test_execution']
        summary = report['test_summary']
        perf = report['system_performance']
        
        print("📊 TEST EXECUTION DETAILS")
        print("-" * 80)
        print(f"Start Time:        {exec_info['start_time']}")
        print(f"End Time:          {exec_info['end_time']}")
        print(f"Total Duration:    {exec_info['total_duration_formatted']}")
        
        print("\n📋 TEST RESULTS SUMMARY")
        print("-" * 80)
        print(f"Test Suites:       {summary['total_test_suites']} total")
        print(f"  ✅ Passed:       {summary['passed_suites']}")
        print(f"  ❌ Failed:       {summary['failed_suites']}")
        print(f"  ⊝ Skipped:       {summary['skipped_suites']}")
        
        print(f"\nTest Cases:        {summary['total_test_cases']} total")
        print(f"  ✅ Passed:       {summary['passed_test_cases']}")
        print(f"  ❌ Failed:       {summary['failed_test_cases']}")
        print(f"  Success Rate:    {summary['success_rate']}")
        
        print("\n💻 SYSTEM PERFORMANCE")
        print("-" * 80)
        print(f"Monitoring Duration:  {perf.get('duration_seconds', 0)} seconds")
        print(f"Samples Collected:    {perf.get('samples_collected', 0)}")
        
        cpu = perf.get('cpu', {})
        print(f"\nCPU Usage:")
        print(f"  Average:       {cpu.get('average', 0):.2f}%")
        print(f"  Maximum:       {cpu.get('max', 0):.2f}%")
        print(f"  Minimum:       {cpu.get('min', 0):.2f}%")
        
        memory = perf.get('memory', {})
        print(f"\nMemory Usage:")
        print(f"  Average:       {memory.get('average', 0):.2f}%")
        print(f"  Maximum:       {memory.get('max', 0):.2f}%")
        print(f"  Minimum:       {memory.get('min', 0):.2f}%")
        
        print("\n📁 TEST ARTIFACTS")
        print("-" * 80)
        print(f"Screenshots:       {report['screenshots_directory']}")
        print(f"Test Files:        {report['test_files_directory']}")
        
        # Performance evaluation
        print("\n✅ PERFORMANCE EVALUATION")
        print("-" * 80)
        
        cpu_status = "✓ PASS" if cpu.get('average', 0) < 80 else "⚠ WARNING"
        memory_status = "✓ PASS" if memory.get('average', 0) < 70 else "⚠ WARNING"
        
        print(f"CPU Usage:         {cpu_status} (Threshold: <80%)")
        print(f"Memory Usage:      {memory_status} (Threshold: <70%)")
        
        # Overall verdict
        print("\n" + "="*80)
        if summary['failed_test_cases'] == 0 and summary['failed_suites'] == 0:
            print("  🎉 OVERALL RESULT: ALL TESTS PASSED")
        else:
            print("  ⚠ OVERALL RESULT: SOME TESTS FAILED - REVIEW REQUIRED")
        print("="*80 + "\n")
    
    def generate_html_report(self, report):
        """Generate HTML test report"""
        exec_info = report['test_execution']
        summary = report['test_summary']
        perf = report['system_performance']
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Functional Testing Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .summary-card.success {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }}
        .summary-card.danger {{
            background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
        }}
        .summary-card.warning {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            font-size: 14px;
            opacity: 0.9;
        }}
        .summary-card .value {{
            font-size: 36px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .test-suite {{
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }}
        .test-suite.passed {{
            border-left-color: #27ae60;
        }}
        .test-suite.failed {{
            border-left-color: #e74c3c;
        }}
        .test-suite.skipped {{
            border-left-color: #95a5a6;
        }}
        .badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 10px;
        }}
        .badge.pass {{
            background: #27ae60;
            color: white;
        }}
        .badge.fail {{
            background: #e74c3c;
            color: white;
        }}
        .badge.skip {{
            background: #95a5a6;
            color: white;
        }}
        .metric-row {{
            display: flex;
            justify-content: space-between;
            padding: 10px;
            border-bottom: 1px solid #ecf0f1;
        }}
        .metric-row:last-child {{
            border-bottom: none;
        }}
        .metric-label {{
            font-weight: 600;
            color: #34495e;
        }}
        .metric-value {{
            color: #7f8c8d;
        }}
        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #ecf0f1;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            transition: width 0.3s ease;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 14px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }}
        th {{
            background: #34495e;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 Functional Testing Report</h1>
        <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>📊 Executive Summary</h2>
        <div class="summary-grid">
            <div class="summary-card">
                <h3>Total Test Suites</h3>
                <div class="value">{summary['total_test_suites']}</div>
            </div>
            <div class="summary-card success">
                <h3>Passed Tests</h3>
                <div class="value">{summary['passed_test_cases']}</div>
            </div>
            <div class="summary-card danger">
                <h3>Failed Tests</h3>
                <div class="value">{summary['failed_test_cases']}</div>
            </div>
            <div class="summary-card warning">
                <h3>Success Rate</h3>
                <div class="value">{summary['success_rate']}</div>
            </div>
        </div>
        
        <h2>⏱️ Execution Details</h2>
        <div class="metric-row">
            <span class="metric-label">Start Time:</span>
            <span class="metric-value">{exec_info['start_time']}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">End Time:</span>
            <span class="metric-value">{exec_info['end_time']}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Total Duration:</span>
            <span class="metric-value">{exec_info['total_duration_formatted']}</span>
        </div>
        
        <h2>📋 Test Suite Results</h2>
"""
        
        # Add test suite results
        for result in report['test_results']:
            status = result.get('status', 'UNKNOWN').lower()
            status_class = 'passed' if status == 'pass' else 'failed' if status == 'fail' else 'skipped'
            badge_class = 'pass' if status == 'pass' else 'fail' if status == 'fail' else 'skip'
            
            html += f"""
        <div class="test-suite {status_class}">
            <h3>{result.get('suite_name', 'Unknown Suite')}
                <span class="badge {badge_class}">{status.upper()}</span>
            </h3>
            <div class="metric-row">
                <span class="metric-label">Test File:</span>
                <span class="metric-value">{result.get('test_file', 'N/A')}</span>
            </div>
"""
            
            if 'passed' in result:
                html += f"""
            <div class="metric-row">
                <span class="metric-label">Passed:</span>
                <span class="metric-value">{result.get('passed', 0)}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Failed:</span>
                <span class="metric-value">{result.get('failed', 0)}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Duration:</span>
                <span class="metric-value">{result.get('duration_seconds', 0):.2f} seconds</span>
            </div>
"""
            
            if 'error' in result:
                html += f"""
            <div class="metric-row">
                <span class="metric-label">Error:</span>
                <span class="metric-value" style="color: #e74c3c;">{result['error']}</span>
            </div>
"""
            
            html += "        </div>\n"
        
        # System performance
        cpu = perf.get('cpu', {})
        memory = perf.get('memory', {})
        
        html += f"""
        <h2>💻 System Performance</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Average</th>
                <th>Maximum</th>
                <th>Minimum</th>
            </tr>
            <tr>
                <td><strong>CPU Usage</strong></td>
                <td>{cpu.get('average', 0):.2f}%</td>
                <td>{cpu.get('max', 0):.2f}%</td>
                <td>{cpu.get('min', 0):.2f}%</td>
            </tr>
            <tr>
                <td><strong>Memory Usage</strong></td>
                <td>{memory.get('average', 0):.2f}%</td>
                <td>{memory.get('max', 0):.2f}%</td>
                <td>{memory.get('min', 0):.2f}%</td>
            </tr>
        </table>
        
        <h2>📂 Test Artifacts</h2>
        <div class="metric-row">
            <span class="metric-label">Screenshots:</span>
            <span class="metric-value">{report['screenshots_directory']}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Test Files:</span>
            <span class="metric-value">{report['test_files_directory']}</span>
        </div>
        
        <h2>✅ Overall Assessment</h2>
        <div style="padding: 20px; background: {'#d4edda' if summary['failed_test_cases'] == 0 else '#f8d7da'}; 
                    border-radius: 8px; margin: 20px 0;">
            <h3 style="margin: 0; color: {'#155724' if summary['failed_test_cases'] == 0 else '#721c24'};">
                {'🎉 ALL TESTS PASSED' if summary['failed_test_cases'] == 0 else '⚠️ SOME TESTS FAILED'}
            </h3>
            <p style="margin: 10px 0 0 0; color: {'#155724' if summary['failed_test_cases'] == 0 else '#721c24'};">
                {f'All {summary["total_test_cases"]} test cases passed successfully!' if summary['failed_test_cases'] == 0 
                  else f'{summary["failed_test_cases"]} test case(s) failed. Please review the results above.'}
            </p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def run(self):
        """Main execution flow"""
        try:
            print("\n")
            print("="*80)
            print("  FUNCTIONAL TESTING AUTOMATION SUITE")
            print("  Document Management System")
            print("="*80)
            print(f"\n  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # Phase 1: Setup
            self.setup_test_environment()
            
            # Phase 2: Execute tests
            self.run_all_tests()
            
            # Phase 3: Generate report
            report = self.generate_comprehensive_report()
            
            print("\n✅ TESTING COMPLETE!")
            print(f"\nView detailed report at: reports/")
            
            return report
            
        except KeyboardInterrupt:
            print("\n\n⚠ Testing interrupted by user")
            self.monitor.stop_monitoring()
            sys.exit(1)
        
        except Exception as e:
            print(f"\n\n❌ Fatal error: {str(e)}")
            self.monitor.stop_monitoring()
            sys.exit(1)

if __name__ == "__main__":
    executor = TestExecutor()
    executor.run()