#!/usr/bin/env python3
"""
Master test runner for TradingAgents Web Application
Runs all test suites and generates comprehensive reports
"""

import asyncio
import subprocess
import sys
import time
import json
import os
from pathlib import Path
from typing import Dict, Any, List

class TestRunner:
    """Master test runner for all test suites"""
    
    def __init__(self):
        self.test_results = {
            'timestamp': time.time(),
            'test_suites': {},
            'overall_success': False,
            'summary': {}
        }
        
    def run_backend_tests(self) -> Dict[str, Any]:
        """Run backend unit and integration tests"""
        print("🧪 Running Backend Tests...")
        
        results = {
            'unit_tests': {'passed': 0, 'failed': 0, 'skipped': 0},
            'integration_tests': {'passed': 0, 'failed': 0, 'skipped': 0},
            'success': False,
            'output': '',
            'duration': 0
        }
        
        start_time = time.time()
        
        try:
            # Run pytest on backend directory
            backend_path = Path(__file__).parent.parent / 'backend'
            if backend_path.exists():
                cmd = [sys.executable, '-m', 'pytest', str(backend_path), '-v', '--tb=short']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                results['output'] = result.stdout + result.stderr
                results['success'] = result.returncode == 0
                
                # Parse pytest output for counts (simplified)
                if 'passed' in results['output']:
                    # This is a simplified parser - in production you'd want more robust parsing
                    lines = results['output'].split('\n')
                    for line in lines:
                        if 'passed' in line and 'failed' in line:
                            # Extract numbers from pytest summary line
                            parts = line.split()
                            for i, part in enumerate(parts):
                                if part == 'passed':
                                    results['unit_tests']['passed'] = int(parts[i-1])
                                elif part == 'failed':
                                    results['unit_tests']['failed'] = int(parts[i-1])
            else:
                results['output'] = "Backend test directory not found"
                
        except subprocess.TimeoutExpired:
            results['output'] = "Backend tests timed out"
        except Exception as e:
            results['output'] = f"Backend test error: {str(e)}"
            
        results['duration'] = time.time() - start_time
        return results
        
    def run_frontend_tests(self) -> Dict[str, Any]:
        """Run frontend unit and component tests"""
        print("⚛️  Running Frontend Tests...")
        
        results = {
            'unit_tests': {'passed': 0, 'failed': 0, 'skipped': 0},
            'component_tests': {'passed': 0, 'failed': 0, 'skipped': 0},
            'success': False,
            'output': '',
            'duration': 0
        }
        
        start_time = time.time()
        
        try:
            frontend_path = Path(__file__).parent.parent / 'frontend'
            if frontend_path.exists():
                # Run npm test
                cmd = ['npm', 'test', '--', '--watchAll=false', '--coverage=false']
                result = subprocess.run(cmd, cwd=frontend_path, capture_output=True, text=True, timeout=300)
                
                results['output'] = result.stdout + result.stderr
                results['success'] = result.returncode == 0
                
                # Parse test output for counts
                if 'Tests:' in results['output']:
                    lines = results['output'].split('\n')
                    for line in lines:
                        if 'Tests:' in line:
                            # Extract test counts from Jest output
                            if 'passed' in line:
                                parts = line.split()
                                for i, part in enumerate(parts):
                                    if part == 'passed,':
                                        results['unit_tests']['passed'] = int(parts[i-1])
            else:
                results['output'] = "Frontend test directory not found"
                
        except subprocess.TimeoutExpired:
            results['output'] = "Frontend tests timed out"
        except Exception as e:
            results['output'] = f"Frontend test error: {str(e)}"
            
        results['duration'] = time.time() - start_time
        return results
        
    async def run_e2e_tests(self) -> Dict[str, Any]:
        """Run end-to-end tests"""
        print("🎭 Running E2E Tests...")
        
        results = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'success': False,
            'output': '',
            'duration': 0,
            'detailed_results': {}
        }
        
        start_time = time.time()
        
        try:
            # Run E2E test
            e2e_test_path = Path(__file__).parent / 'e2e' / 'test_full_analysis_flow.py'
            if e2e_test_path.exists():
                cmd = [sys.executable, str(e2e_test_path)]
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
                
                results['output'] = stdout.decode() + stderr.decode()
                results['success'] = process.returncode == 0
                results['tests_run'] = 1
                
                if results['success']:
                    results['tests_passed'] = 1
                else:
                    results['tests_failed'] = 1
                    
                # Try to load detailed results
                results_file = Path('e2e_test_results.json')
                if results_file.exists():
                    with open(results_file) as f:
                        results['detailed_results'] = json.load(f)
            else:
                results['output'] = "E2E test file not found"
                
        except asyncio.TimeoutError:
            results['output'] = "E2E tests timed out"
        except Exception as e:
            results['output'] = f"E2E test error: {str(e)}"
            
        results['duration'] = time.time() - start_time
        return results
        
    async def run_load_tests(self) -> Dict[str, Any]:
        """Run load tests"""
        print("🔥 Running Load Tests...")
        
        results = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'success': False,
            'output': '',
            'duration': 0,
            'performance_metrics': {}
        }
        
        start_time = time.time()
        
        try:
            # Run load test
            load_test_path = Path(__file__).parent / 'load' / 'test_concurrent_load.py'
            if load_test_path.exists():
                cmd = [sys.executable, str(load_test_path)]
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=600)
                
                results['output'] = stdout.decode() + stderr.decode()
                results['success'] = process.returncode == 0
                results['tests_run'] = 1
                
                if results['success']:
                    results['tests_passed'] = 1
                else:
                    results['tests_failed'] = 1
                    
                # Try to load performance metrics
                results_file = Path('load_test_results.json')
                if results_file.exists():
                    with open(results_file) as f:
                        results['performance_metrics'] = json.load(f)
            else:
                results['output'] = "Load test file not found"
                
        except asyncio.TimeoutError:
            results['output'] = "Load tests timed out"
        except Exception as e:
            results['output'] = f"Load test error: {str(e)}"
            
        results['duration'] = time.time() - start_time
        return results
        
    def check_servers_running(self) -> Dict[str, bool]:
        """Check if backend and frontend servers are running"""
        print("🔍 Checking server status...")
        
        import requests
        
        status = {
            'backend': False,
            'frontend': False
        }
        
        # Check backend
        try:
            response = requests.get('http://localhost:8003/health', timeout=5)
            status['backend'] = response.status_code == 200
        except:
            pass
            
        # Check frontend
        try:
            response = requests.get('http://localhost:5174', timeout=5)
            status['frontend'] = response.status_code == 200
        except:
            # Try alternative port
            try:
                response = requests.get('http://localhost:80', timeout=5)
                status['frontend'] = response.status_code == 200
            except:
                pass
                
        return status
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites"""
        print("🚀 Starting Comprehensive Test Suite...")
        print("="*60)
        
        # Check server status
        server_status = self.check_servers_running()
        self.test_results['server_status'] = server_status
        
        if not server_status['backend']:
            print("⚠️  Warning: Backend server not running on localhost:8003")
        if not server_status['frontend']:
            print("⚠️  Warning: Frontend server not running on localhost:5174 or localhost:80")
            
        # Run backend tests
        self.test_results['test_suites']['backend'] = self.run_backend_tests()
        
        # Run frontend tests
        self.test_results['test_suites']['frontend'] = self.run_frontend_tests()
        
        # Run E2E tests (only if servers are running)
        if server_status['backend'] and server_status['frontend']:
            self.test_results['test_suites']['e2e'] = await self.run_e2e_tests()
        else:
            print("⏭️  Skipping E2E tests - servers not running")
            self.test_results['test_suites']['e2e'] = {
                'success': False,
                'output': 'Skipped - servers not running',
                'tests_run': 0,
                'tests_passed': 0,
                'tests_failed': 0
            }
            
        # Run load tests (only if backend is running)
        if server_status['backend']:
            self.test_results['test_suites']['load'] = await self.run_load_tests()
        else:
            print("⏭️  Skipping load tests - backend not running")
            self.test_results['test_suites']['load'] = {
                'success': False,
                'output': 'Skipped - backend not running',
                'tests_run': 0,
                'tests_passed': 0,
                'tests_failed': 0
            }
            
        # Calculate overall results
        self.calculate_summary()
        
        return self.test_results
        
    def calculate_summary(self):
        """Calculate overall test summary"""
        summary = {
            'total_test_suites': len(self.test_results['test_suites']),
            'successful_suites': 0,
            'failed_suites': 0,
            'total_tests': 0,
            'total_passed': 0,
            'total_failed': 0,
            'total_duration': 0
        }
        
        for suite_name, suite_results in self.test_results['test_suites'].items():
            if suite_results.get('success', False):
                summary['successful_suites'] += 1
            else:
                summary['failed_suites'] += 1
                
            # Add test counts
            if 'tests_run' in suite_results:
                summary['total_tests'] += suite_results['tests_run']
                summary['total_passed'] += suite_results.get('tests_passed', 0)
                summary['total_failed'] += suite_results.get('tests_failed', 0)
            else:
                # For backend/frontend tests with different structure
                unit_tests = suite_results.get('unit_tests', {})
                summary['total_tests'] += unit_tests.get('passed', 0) + unit_tests.get('failed', 0)
                summary['total_passed'] += unit_tests.get('passed', 0)
                summary['total_failed'] += unit_tests.get('failed', 0)
                
            summary['total_duration'] += suite_results.get('duration', 0)
            
        # Overall success if all critical tests pass
        critical_suites = ['backend', 'frontend']
        critical_success = all(
            self.test_results['test_suites'].get(suite, {}).get('success', False)
            for suite in critical_suites
        )
        
        # E2E and load tests are important but not critical for basic functionality
        self.test_results['overall_success'] = critical_success
        self.test_results['summary'] = summary
        
    def print_results(self):
        """Print comprehensive test results"""
        print("\n" + "="*80)
        print("🧪 COMPREHENSIVE TEST RESULTS")
        print("="*80)
        
        # Server status
        server_status = self.test_results.get('server_status', {})
        print(f"🖥️  Backend Server: {'✅ Running' if server_status.get('backend') else '❌ Not Running'}")
        print(f"🌐 Frontend Server: {'✅ Running' if server_status.get('frontend') else '❌ Not Running'}")
        
        # Test suite results
        for suite_name, suite_results in self.test_results['test_suites'].items():
            status = '✅ PASSED' if suite_results.get('success') else '❌ FAILED'
            duration = suite_results.get('duration', 0)
            
            print(f"\n📊 {suite_name.upper()} TESTS: {status} ({duration:.1f}s)")
            
            if 'tests_run' in suite_results:
                print(f"   Tests Run: {suite_results['tests_run']}")
                print(f"   Passed: {suite_results.get('tests_passed', 0)}")
                print(f"   Failed: {suite_results.get('tests_failed', 0)}")
            else:
                unit_tests = suite_results.get('unit_tests', {})
                print(f"   Passed: {unit_tests.get('passed', 0)}")
                print(f"   Failed: {unit_tests.get('failed', 0)}")
                print(f"   Skipped: {unit_tests.get('skipped', 0)}")
                
        # Summary
        summary = self.test_results['summary']
        print(f"\n🎯 OVERALL SUMMARY")
        print("-" * 40)
        print(f"   Test Suites: {summary['successful_suites']}/{summary['total_test_suites']} passed")
        print(f"   Total Tests: {summary['total_passed']}/{summary['total_tests']} passed")
        print(f"   Total Duration: {summary['total_duration']:.1f}s")
        
        # Final result
        overall_status = '✅ SUCCESS' if self.test_results['overall_success'] else '❌ FAILURE'
        print(f"\n🏆 FINAL RESULT: {overall_status}")
        print("="*80)
        
    def save_results(self, filename: str = 'comprehensive_test_results.json'):
        """Save test results to file"""
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"📄 Test results saved to {filename}")

async def main():
    """Main test execution"""
    runner = TestRunner()
    results = await runner.run_all_tests()
    runner.print_results()
    runner.save_results()
    
    return results['overall_success']

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
