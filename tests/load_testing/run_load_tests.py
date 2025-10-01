#!/usr/bin/env python3
"""
Load Test Runner Script

Executes different load testing scenarios as defined in the testing guide.
Usage:
    python run_load_tests.py --scenario basic
    python run_load_tests.py --scenario heavy --host http://localhost:8000
    python run_load_tests.py --list-scenarios
"""

import argparse
import subprocess
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.load_testing.load_test_config import LOAD_TEST_SCENARIOS, ENVIRONMENTS


class LoadTestRunner:
    """Manages execution of load testing scenarios"""
    
    def __init__(self):
        self.results_dir = Path("tests/load_testing/results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def list_scenarios(self):
        """List all available test scenarios"""
        print("\n🧪 Available Load Testing Scenarios:")
        print("=" * 50)
        
        for key, scenario in LOAD_TEST_SCENARIOS.items():
            print(f"\n📊 {key.upper()}")
            print(f"   Name: {scenario['name']}")
            print(f"   Description: {scenario['description']}")
            print(f"   Users: {scenario['users']}")
            print(f"   Spawn Rate: {scenario['spawn_rate']}/sec")
            print(f"   Duration: {scenario['run_time']}")
            print(f"   Expected Response Time: {scenario['expected_response_time']}s")
            print(f"   Expected Failure Rate: {scenario['expected_failure_rate']*100}%")
    
    def run_scenario(self, scenario_name, host="http://localhost:8000", environment="local"):
        """Run a specific load testing scenario"""
        
        if scenario_name not in LOAD_TEST_SCENARIOS:
            print(f"❌ Scenario '{scenario_name}' not found!")
            self.list_scenarios()
            return False
        
        scenario = LOAD_TEST_SCENARIOS[scenario_name]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"{scenario_name}_{timestamp}.json"
        
        print(f"\n🚀 Starting Load Test: {scenario['name']}")
        print(f"📊 Scenario: {scenario_name}")
        print(f"🌐 Host: {host}")
        print(f"👥 Users: {scenario['users']}")
        print(f"⚡ Spawn Rate: {scenario['spawn_rate']}/sec")
        print(f"⏱️  Duration: {scenario['run_time']}")
        print(f"📁 Results will be saved to: {results_file}")
        
        # Build locust command
        locust_file = Path(__file__).parent / "locustfile.py"
        cmd = [
            "locust",
            "-f", str(locust_file),
            "--host", host,
            "--users", str(scenario['users']),
            "--spawn-rate", str(scenario['spawn_rate']),
            "--run-time", scenario['run_time'],
            "--html", str(self.results_dir / f"{scenario_name}_{timestamp}.html"),
            "--csv", str(self.results_dir / f"{scenario_name}_{timestamp}"),
            "--headless"  # Run without web UI
        ]
        
        print(f"\n🔧 Command: {' '.join(cmd)}")
        print("\n" + "="*60)
        
        try:
            # Run the load test
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)  # 1 hour timeout
            end_time = time.time()
            
            # Save results
            test_results = {
                "scenario": scenario_name,
                "config": scenario,
                "host": host,
                "environment": environment,
                "start_time": datetime.fromtimestamp(start_time).isoformat(),
                "end_time": datetime.fromtimestamp(end_time).isoformat(),
                "duration_seconds": end_time - start_time,
                "command": " ".join(cmd),
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            with open(results_file, 'w') as f:
                json.dump(test_results, f, indent=2)
            
            if result.returncode == 0:
                print(f"\n✅ Load test completed successfully!")
                print(f"📊 Results saved to: {results_file}")
                self.analyze_results(results_file, scenario)
                return True
            else:
                print(f"\n❌ Load test failed with return code: {result.returncode}")
                print(f"Error output: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"\n⏰ Load test timed out after 1 hour")
            return False
        except Exception as e:
            print(f"\n❌ Error running load test: {e}")
            return False
    
    def analyze_results(self, results_file, scenario_config):
        """Analyze load test results and provide recommendations"""
        print(f"\n📈 Analyzing Results...")
        print("=" * 40)
        
        # Try to read CSV results if available
        csv_stats_file = str(results_file).replace('.json', '_stats.csv')
        
        if os.path.exists(csv_stats_file):
            print(f"📊 Detailed statistics available in: {csv_stats_file}")
            
            # Basic analysis from CSV
            try:
                import pandas as pd
                df = pd.read_csv(csv_stats_file)
                
                print(f"\n🎯 Performance Summary:")
                print(f"   Total Requests: {df['Request Count'].sum()}")
                print(f"   Failed Requests: {df['Failure Count'].sum()}")
                print(f"   Average Response Time: {df['Average Response Time'].mean():.2f}ms")
                print(f"   95th Percentile: {df['95%'].mean():.2f}ms")
                print(f"   99th Percentile: {df['99%'].mean():.2f}ms")
                
                # Compare against expectations
                failure_rate = df['Failure Count'].sum() / df['Request Count'].sum()
                avg_response_time = df['Average Response Time'].mean() / 1000  # Convert to seconds
                
                print(f"\n🎯 Performance vs Expectations:")
                print(f"   Expected Response Time: {scenario_config['expected_response_time']}s")
                print(f"   Actual Response Time: {avg_response_time:.2f}s")
                print(f"   Expected Failure Rate: {scenario_config['expected_failure_rate']*100:.1f}%")
                print(f"   Actual Failure Rate: {failure_rate*100:.1f}%")
                
                # Recommendations
                print(f"\n💡 Recommendations:")
                if avg_response_time > scenario_config['expected_response_time']:
                    print("   ⚠️  Response times exceeded expectations - consider optimization")
                else:
                    print("   ✅ Response times within acceptable range")
                    
                if failure_rate > scenario_config['expected_failure_rate']:
                    print("   ⚠️  Failure rate exceeded expectations - investigate errors")
                else:
                    print("   ✅ Failure rate within acceptable range")
                    
            except ImportError:
                print("   📝 Install pandas for detailed analysis: pip install pandas")
            except Exception as e:
                print(f"   ⚠️  Could not analyze CSV results: {e}")
        
        print(f"\n📁 Full results available in:")
        print(f"   JSON: {results_file}")
        print(f"   HTML: {str(results_file).replace('.json', '.html')}")
        print(f"   CSV: {csv_stats_file}")
    
    def run_progressive_test(self, host="http://localhost:8000"):
        """Run progressive load testing as recommended in the guide"""
        print("\n🔄 Running Progressive Load Test")
        print("Following the testing guide: start small, increase complexity")
        print("=" * 60)
        
        scenarios = ["basic", "conservative", "production", "moderate", "heavy"]
        results = {}
        
        for scenario_name in scenarios:
            print(f"\n🎯 Running {scenario_name.upper()} scenario...")
            success = self.run_scenario(scenario_name, host)
            results[scenario_name] = success
            
            if not success:
                print(f"❌ {scenario_name} failed - stopping progressive test")
                break
            
            # Wait between tests
            if scenario_name != scenarios[-1]:
                print("⏳ Waiting 30 seconds before next test...")
                time.sleep(30)
        
        # Summary
        print(f"\n📊 Progressive Test Summary:")
        print("=" * 40)
        for scenario, success in results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   {scenario.upper()}: {status}")
        
        return all(results.values())


def main():
    parser = argparse.ArgumentParser(description="DocAnalyzer Load Test Runner")
    parser.add_argument("--scenario", "-s", help="Load test scenario to run")
    parser.add_argument("--host", default="http://localhost:8000", help="Target host URL")
    parser.add_argument("--environment", "-e", default="local", choices=ENVIRONMENTS.keys(), help="Environment configuration")
    parser.add_argument("--list-scenarios", "-l", action="store_true", help="List available scenarios")
    parser.add_argument("--progressive", "-p", action="store_true", help="Run progressive load test")
    
    args = parser.parse_args()
    
    runner = LoadTestRunner()
    
    if args.list_scenarios:
        runner.list_scenarios()
        return
    
    if args.progressive:
        success = runner.run_progressive_test(args.host)
        sys.exit(0 if success else 1)
    
    if args.scenario:
        success = runner.run_scenario(args.scenario, args.host, args.environment)
        sys.exit(0 if success else 1)
    
    # If no specific action, show help
    parser.print_help()


if __name__ == "__main__":
    main()
