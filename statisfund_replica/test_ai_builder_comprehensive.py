#!/usr/bin/env python3
"""
Comprehensive AI Builder Testing Suite
Tests all aspects of the new LLM-style AI Builder interface
"""

import requests
import json
import time
import sys
from typing import Dict, List, Any

class AIBuilderTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_time: float = 0):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response_time": response_time
        })
        print(f"{status} {test_name} ({response_time:.2f}s)")
        if details:
            print(f"    {details}")
    
    def test_backend_health(self) -> bool:
        """Test if backend is running and healthy"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Health Check", True, f"Status: {data.get('status')}", response_time)
                return True
            else:
                self.log_test("Backend Health Check", False, f"HTTP {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_strategy_generation(self) -> bool:
        """Test AI strategy generation with various prompts"""
        example_prompts = [
            "Create a swing trading strategy using moving average crossovers with stop losses",
            "Build a momentum strategy that buys on RSI oversold and sells on overbought",
            "Design a mean reversion strategy using Bollinger Bands",
            "Create a breakout strategy that trades channel breakouts with volume confirmation",
            "Build a pairs trading strategy for correlated stocks",
            "Design a simple buy and hold strategy with rebalancing"
        ]
        
        symbols = ["AAPL", "TSLA", "MSFT"]
        success_count = 0
        
        for i, prompt in enumerate(example_prompts):
            try:
                start_time = time.time()
                payload = {
                    "description": prompt,
                    "symbols": symbols,
                    "start_date": "2023-01-01",
                    "end_date": "2023-12-31"
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/generate-strategy",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("code"):
                        code_length = len(data["code"])
                        self.log_test(f"Strategy Generation #{i+1}", True, 
                                    f"Generated {code_length} chars", response_time)
                        success_count += 1
                    else:
                        self.log_test(f"Strategy Generation #{i+1}", False, 
                                    f"No code generated: {data.get('error', 'Unknown error')}", response_time)
                else:
                    self.log_test(f"Strategy Generation #{i+1}", False, 
                                f"HTTP {response.status_code}", response_time)
                
                # Small delay between requests
                time.sleep(1)
                
            except Exception as e:
                self.log_test(f"Strategy Generation #{i+1}", False, f"Error: {str(e)}")
        
        overall_success = success_count >= len(example_prompts) * 0.8  # 80% success rate
        self.log_test("Overall Strategy Generation", overall_success, 
                     f"{success_count}/{len(example_prompts)} successful")
        return overall_success
    
    def test_backtest_integration(self) -> bool:
        """Test basic and advanced backtest integration"""
        # First generate a simple strategy
        try:
            strategy_payload = {
                "description": "Create a simple moving average crossover strategy",
                "symbols": ["AAPL"],
                "start_date": "2023-01-01",
                "end_date": "2023-12-31"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/generate-strategy",
                json=strategy_payload,
                timeout=30
            )
            
            if response.status_code != 200:
                self.log_test("Backtest Integration Setup", False, "Failed to generate strategy")
                return False
            
            strategy_data = response.json()
            if not strategy_data.get("success") or not strategy_data.get("code"):
                self.log_test("Backtest Integration Setup", False, "No strategy code generated")
                return False
            
            strategy_code = strategy_data["code"]
            
            # Test basic backtest
            basic_success = self._test_basic_backtest(strategy_code)
            
            # Test advanced backtest
            advanced_success = self._test_advanced_backtest(strategy_code)
            
            overall_success = basic_success and advanced_success
            self.log_test("Overall Backtest Integration", overall_success, 
                         f"Basic: {basic_success}, Advanced: {advanced_success}")
            return overall_success
            
        except Exception as e:
            self.log_test("Backtest Integration", False, f"Error: {str(e)}")
            return False
    
    def _test_basic_backtest(self, strategy_code: str) -> bool:
        """Test basic backtest functionality"""
        try:
            start_time = time.time()
            backtest_payload = {
                "code": strategy_code,
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-30",
                "initial_cash": 10000
            }
            
            response = self.session.post(
                f"{self.base_url}/api/backtest",
                json=backtest_payload,
                timeout=60
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    final_value = data.get("final_portfolio_value", 0)
                    self.log_test("Basic Backtest", True, 
                                f"Final value: ${final_value:,.2f}", response_time)
                    return True
                else:
                    self.log_test("Basic Backtest", False, 
                                f"Backtest failed: {data.get('error')}", response_time)
                    return False
            else:
                self.log_test("Basic Backtest", False, f"HTTP {response.status_code}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Basic Backtest", False, f"Error: {str(e)}")
            return False
    
    def _test_advanced_backtest(self, strategy_code: str) -> bool:
        """Test advanced backtest functionality"""
        try:
            start_time = time.time()
            backtest_payload = {
                "code": strategy_code,
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-30",
                "initial_cash": 10000,
                "commission": 0.001
            }
            
            response = self.session.post(
                f"{self.base_url}/api/advanced-backtest",
                json=backtest_payload,
                timeout=60
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    metrics = data.get("performance_metrics", {})
                    sharpe = metrics.get("sharpe_ratio", 0)
                    self.log_test("Advanced Backtest", True, 
                                f"Sharpe ratio: {sharpe:.3f}", response_time)
                    return True
                else:
                    self.log_test("Advanced Backtest", False, 
                                f"Advanced backtest failed: {data.get('error')}", response_time)
                    return False
            else:
                self.log_test("Advanced Backtest", False, f"HTTP {response.status_code}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Advanced Backtest", False, f"Error: {str(e)}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling with invalid inputs"""
        error_tests = [
            {
                "name": "Empty Description",
                "payload": {"description": "", "symbols": ["AAPL"]},
                "expected_error": True
            },
            {
                "name": "Invalid Symbol",
                "payload": {"description": "Simple strategy", "symbols": ["INVALID_SYMBOL_XYZ"]},
                "expected_error": False  # Should handle gracefully
            },
            {
                "name": "Invalid Date Range",
                "payload": {
                    "description": "Simple strategy", 
                    "symbols": ["AAPL"],
                    "start_date": "2025-01-01",
                    "end_date": "2024-01-01"
                },
                "expected_error": True
            }
        ]
        
        success_count = 0
        for test in error_tests:
            try:
                start_time = time.time()
                response = self.session.post(
                    f"{self.base_url}/api/generate-strategy",
                    json=test["payload"],
                    timeout=15
                )
                response_time = time.time() - start_time
                
                if test["expected_error"]:
                    # Should return error or handle gracefully
                    if response.status_code != 200 or not response.json().get("success", True):
                        self.log_test(f"Error Handling: {test['name']}", True, 
                                    "Properly handled error", response_time)
                        success_count += 1
                    else:
                        self.log_test(f"Error Handling: {test['name']}", False, 
                                    "Should have returned error", response_time)
                else:
                    # Should handle gracefully
                    if response.status_code == 200:
                        self.log_test(f"Error Handling: {test['name']}", True, 
                                    "Handled gracefully", response_time)
                        success_count += 1
                    else:
                        self.log_test(f"Error Handling: {test['name']}", False, 
                                    f"HTTP {response.status_code}", response_time)
                
            except Exception as e:
                self.log_test(f"Error Handling: {test['name']}", False, f"Exception: {str(e)}")
        
        overall_success = success_count >= len(error_tests) * 0.7  # 70% success rate
        self.log_test("Overall Error Handling", overall_success, 
                     f"{success_count}/{len(error_tests)} tests passed")
        return overall_success
    
    def test_performance_load(self) -> bool:
        """Test performance under concurrent requests"""
        import threading
        import queue
        
        results_queue = queue.Queue()
        num_threads = 3
        requests_per_thread = 2
        
        def worker():
            try:
                for i in range(requests_per_thread):
                    start_time = time.time()
                    payload = {
                        "description": f"Create a simple strategy #{i}",
                        "symbols": ["AAPL"],
                        "start_date": "2023-01-01",
                        "end_date": "2023-03-31"
                    }
                    
                    response = self.session.post(
                        f"{self.base_url}/api/generate-strategy",
                        json=payload,
                        timeout=30
                    )
                    response_time = time.time() - start_time
                    
                    success = response.status_code == 200 and response.json().get("success", False)
                    results_queue.put((success, response_time))
                    
            except Exception as e:
                results_queue.put((False, 0))
        
        # Start threads
        threads = []
        start_time = time.time()
        
        for _ in range(num_threads):
            thread = threading.Thread(target=worker)
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Collect results
        successes = 0
        total_requests = 0
        response_times = []
        
        while not results_queue.empty():
            success, resp_time = results_queue.get()
            total_requests += 1
            if success:
                successes += 1
            response_times.append(resp_time)
        
        success_rate = successes / total_requests if total_requests > 0 else 0
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        overall_success = success_rate >= 0.8  # 80% success rate under load
        self.log_test("Performance Load Test", overall_success, 
                     f"{successes}/{total_requests} successful, avg {avg_response_time:.2f}s", total_time)
        return overall_success
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results"""
        print("🚀 Starting Comprehensive AI Builder Testing Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all tests
        tests = [
            ("Backend Health", self.test_backend_health),
            ("Strategy Generation", self.test_strategy_generation),
            ("Backtest Integration", self.test_backtest_integration),
            ("Error Handling", self.test_error_handling),
            ("Performance Load", self.test_performance_load)
        ]
        
        results = {}
        for test_name, test_func in tests:
            print(f"\n📋 Running {test_name} Tests...")
            results[test_name] = test_func()
        
        total_time = time.time() - start_time
        
        # Calculate overall results
        passed_tests = sum(1 for result in results.values() if result)
        total_tests = len(results)
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 60)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n🎯 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        print(f"⏱️  Total Test Time: {total_time:.2f} seconds")
        
        # Detailed results
        print(f"\n📈 Detailed Results: {len(self.test_results)} individual tests")
        
        if success_rate >= 80:
            print("🎉 AI Builder is PRODUCTION READY!")
        elif success_rate >= 60:
            print("⚠️  AI Builder needs minor fixes before production")
        else:
            print("🔧 AI Builder needs significant fixes")
        
        return {
            "overall_success_rate": success_rate,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "total_time": total_time,
            "detailed_results": self.test_results,
            "test_results": results
        }

def main():
    """Main test runner"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    tester = AIBuilderTester(base_url)
    results = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    if results["overall_success_rate"] >= 80:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()
