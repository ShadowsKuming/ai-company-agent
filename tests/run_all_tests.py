"""
Master Test Runner
Runs all test suites in sequence and provides comprehensive system health report
Run directly: python tests/run_all_tests.py
"""

import os
import sys
import time
import subprocess
from datetime import datetime

# Test files to run in order
TEST_FILES = [
    ('test_apis.py', 'API Connectivity Tests'),
    ('test_llm.py', 'LLM Functionality Tests'),
    ('test_tools.py', 'Tools Functionality Tests'),
    ('test_agents.py', 'Agents End-to-End Tests')
]


class MasterTestRunner:
    """Runs all test suites and provides comprehensive health report"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
        
    def run_test_file(self, test_file, description):
        """Run a single test file and capture results"""
        print(f"\n{'='*60}")
        print(f"🧪 Running {description}")
        print(f"📁 File: {test_file}")
        print(f"{'='*60}")
        
        test_path = os.path.join('tests', test_file)
        
        if not os.path.exists(test_path):
            self.test_results[test_file] = {
                'status': 'missing',
                'description': description,
                'error': f'Test file {test_path} not found',
                'duration': 0
            }
            print(f"❌ Test file missing: {test_path}")
            return
        
        try:
            start_time = time.time()
            
            # Run the test file
            result = subprocess.run(
                [sys.executable, test_path],
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout per test
            )
            
            duration = time.time() - start_time
            
            self.test_results[test_file] = {
                'status': 'passed' if result.returncode == 0 else 'failed',
                'description': description,
                'returncode': result.returncode,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            if result.returncode == 0:
                print(f"✅ {description} - PASSED ({duration:.1f}s)")
            else:
                print(f"❌ {description} - FAILED ({duration:.1f}s)")
                print(f"Exit code: {result.returncode}")
                
                # Show last few lines of output for debugging
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    print("Last output lines:")
                    for line in lines[-5:]:
                        print(f"  {line}")
                
                if result.stderr:
                    print("Error output:")
                    error_lines = result.stderr.strip().split('\n')
                    for line in error_lines[-3:]:
                        print(f"  {line}")
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            self.test_results[test_file] = {
                'status': 'timeout',
                'description': description,
                'duration': duration,
                'error': f'Test timed out after {duration:.1f} seconds'
            }
            print(f"⏰ {description} - TIMEOUT ({duration:.1f}s)")
            
        except Exception as e:
            duration = time.time() - start_time
            self.test_results[test_file] = {
                'status': 'error',
                'description': description,
                'duration': duration,
                'error': str(e)
            }
            print(f"💥 {description} - ERROR: {str(e)}")
    
    def generate_health_report(self):
        """Generate comprehensive system health report"""
        total_duration = time.time() - self.start_time
        
        print(f"\n{'='*80}")
        print(f"🏥 SYSTEM HEALTH REPORT")
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Total test duration: {total_duration:.1f}s")
        print(f"{'='*80}")
        
        # Count results
        passed = sum(1 for r in self.test_results.values() if r['status'] == 'passed')
        failed = sum(1 for r in self.test_results.values() if r['status'] == 'failed')
        timeout = sum(1 for r in self.test_results.values() if r['status'] == 'timeout')
        error = sum(1 for r in self.test_results.values() if r['status'] == 'error')
        missing = sum(1 for r in self.test_results.values() if r['status'] == 'missing')
        total = len(self.test_results)
        
        print(f"\n📊 TEST SUITE RESULTS:")
        print(f"  ✅ Passed: {passed}/{total}")
        print(f"  ❌ Failed: {failed}/{total}")
        print(f"  ⏰ Timeout: {timeout}/{total}")
        print(f"  💥 Error: {error}/{total}")
        print(f"  📁 Missing: {missing}/{total}")
        
        print(f"\n📋 DETAILED RESULTS:")
        print("-" * 80)
        
        for test_file, result in self.test_results.items():
            status = result['status']
            description = result['description']
            duration = result.get('duration', 0)
            
            status_icon = {
                'passed': '✅',
                'failed': '❌',
                'timeout': '⏰',
                'error': '💥',
                'missing': '📁'
            }.get(status, '❓')
            
            print(f"{status_icon} {description}")
            print(f"   File: {test_file}")
            print(f"   Status: {status.upper()}")
            print(f"   Duration: {duration:.1f}s")
            
            if 'error' in result:
                print(f"   Error: {result['error']}")
            elif 'returncode' in result and result['returncode'] != 0:
                print(f"   Exit code: {result['returncode']}")
            
            print()
        
        # System health assessment
        print("🔍 SYSTEM HEALTH ASSESSMENT:")
        print("-" * 40)
        
        if passed == total:
            health_status = "EXCELLENT"
            health_color = "🟢"
            health_desc = "All systems operational"
        elif passed >= total * 0.75:
            health_status = "GOOD"
            health_color = "🟡"
            health_desc = "Most systems working, minor issues"
        elif passed >= total * 0.5:
            health_status = "FAIR"
            health_color = "🟠"
            health_desc = "Core systems working, some components failing"
        else:
            health_status = "POOR"
            health_color = "🔴"
            health_desc = "Major system issues detected"
        
        print(f"{health_color} Overall Health: {health_status}")
        print(f"   Assessment: {health_desc}")
        
        # Specific recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if 'test_apis.py' in self.test_results and self.test_results['test_apis.py']['status'] != 'passed':
            print("  🔑 Check API keys in .env file - required for system functionality")
        
        if 'test_llm.py' in self.test_results and self.test_results['test_llm.py']['status'] != 'passed':
            print("  🤖 LLM connectivity issues - verify Gemini/OpenAI API keys")
        
        if 'test_tools.py' in self.test_results and self.test_results['test_tools.py']['status'] != 'passed':
            print("  🔧 Tools having issues - check dependencies and API access")
        
        if 'test_agents.py' in self.test_results and self.test_results['test_agents.py']['status'] != 'passed':
            print("  🤝 Agent integration issues - verify previous components work")
        
        if timeout > 0:
            print("  ⏰ Some tests timed out - consider checking network connectivity")
        
        if missing > 0:
            print("  📁 Missing test files - ensure you're running from project root")
        
        # Ready to use assessment
        print(f"\n🚀 READINESS ASSESSMENT:")
        
        critical_tests = ['test_apis.py', 'test_llm.py']
        critical_passed = sum(
            1 for test in critical_tests 
            if test in self.test_results and self.test_results[test]['status'] == 'passed'
        )
        
        if critical_passed == len(critical_tests):
            print("  ✅ System ready for production use")
            print("  ✅ All critical components functional")
        elif critical_passed > 0:
            print("  ⚠️  System partially ready - some limitations expected")
            print("  ⚠️  Fix critical issues before full deployment")
        else:
            print("  ❌ System not ready - critical issues must be resolved")
            print("  ❌ Cannot proceed without fixing API/LLM connectivity")
        
        return health_status.lower()
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 AI TICKER ANALYZER - COMPREHENSIVE TEST SUITE")
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🧪 Running {len(TEST_FILES)} test suites...")
        
        for test_file, description in TEST_FILES:
            self.run_test_file(test_file, description)
        
        health_status = self.generate_health_report()
        
        # Return appropriate exit code
        if health_status in ['excellent', 'good']:
            print(f"\n🎉 ALL TESTS COMPLETED - SYSTEM HEALTHY")
            return 0
        elif health_status == 'fair':
            print(f"\n⚠️  TESTS COMPLETED WITH WARNINGS")
            return 1
        else:
            print(f"\n❌ TESTS COMPLETED - CRITICAL ISSUES DETECTED")
            return 2


def main():
    """Main test runner"""
    # Change to project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    
    print(f"📁 Working directory: {os.getcwd()}")
    
    runner = MasterTestRunner()
    exit_code = runner.run_all_tests()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()