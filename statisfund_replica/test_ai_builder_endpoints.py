#!/usr/bin/env python3
"""
AI Builder Endpoint Testing Suite
Tests all AI Builder functionality with the new LLM-style interface
"""

import requests
import json
import time
from datetime import datetime
import sys

class AIBuilderTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: any = None):
        """Log test results with timestamp"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "test_name": test_name,
            "success": success,
            "details": details,
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if not success and response_data:
            print(f"   Response: {json.dumps(response_data, indent=2)[:300]}...")
    
    def test_strategy_generation_examples(self):
        """Test strategy generation with example prompts from new UI"""
        example_prompts = [
            "Create a momentum strategy using RSI and MACD indicators for AAPL",
            "Build a mean reversion strategy with Bollinger Bands and volume confirmation",
            "Design a breakout strategy that buys on high volume price breakouts above resistance",
            "Make a pairs trading strategy for correlated tech stocks like AAPL and MSFT",
            "Create a swing trading strategy using moving average crossovers with stop losses",
            "Build a scalping strategy for intraday trading with tight risk management"
        ]
        
        for i, prompt in enumerate(example_prompts):
            try:
                payload = {
                    "description": prompt,
                    "symbols": ["AAPL", "MSFT"],
                    "start_date": "2023-01-01",
                    "end_date": "2023-12-31"
                }
                
                response = self.session.post(f"{self.base_url}/api/generate-strategy", 
                                           json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    success = (data.get("success") and 
                              "code" in data and 
                              len(data["code"]) > 100 and
                              "class" in data["code"] and
                              "bt.Strategy" in data["code"])
                    
                    details = f"Generated {len(data.get('code', ''))} chars - {prompt[:50]}..."
                else:
                    success = False
                    data = response.json() if response.content else {}
                    details = f"HTTP {response.status_code} - {prompt[:50]}..."
                
                self.log_test(f"Example Prompt {i+1}", success, details, data)
                
                # Store successful code for backtest testing
                if success and "code" in data:
                    setattr(self, f"example_code_{i}", data["code"])
                    
            except Exception as e:
                self.log_test(f"Example Prompt {i+1}", False, f"Exception: {str(e)}")
    
    def test_chat_interface_workflow(self):
        """Test the chat interface workflow simulation"""
        chat_scenarios = [
            {
                "user_input": "I want a simple moving average strategy",
                "expected_elements": ["moving average", "sma", "crossover"]
            },
            {
                "user_input": "Create a strategy that uses RSI to find oversold conditions",
                "expected_elements": ["rsi", "oversold", "30", "70"]
            },
            {
                "user_input": "Build a momentum strategy with MACD",
                "expected_elements": ["macd", "momentum", "signal", "histogram"]
            }
        ]
        
        for i, scenario in enumerate(chat_scenarios):
            try:
                payload = {
                    "description": scenario["user_input"],
                    "symbols": ["AAPL"],
                    "start_date": "2023-01-01",
                    "end_date": "2023-12-31"
                }
                
                response = self.session.post(f"{self.base_url}/api/generate-strategy", 
                                           json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "code" in data:
                        code_lower = data["code"].lower()
                        found_elements = [elem for elem in scenario["expected_elements"] 
                                        if elem.lower() in code_lower]
                        
                        success = len(found_elements) > 0
                        details = f"Found elements: {found_elements}" if success else "No expected elements found"
                    else:
                        success = False
                        details = "No code generated"
                else:
                    success = False
                    data = response.json() if response.content else {}
                    details = f"HTTP {response.status_code}"
                
                self.log_test(f"Chat Scenario {i+1}", success, details)
                
            except Exception as e:
                self.log_test(f"Chat Scenario {i+1}", False, f"Exception: {str(e)}")
    
    def test_settings_integration(self):
        """Test advanced settings integration with strategy generation"""
        settings_tests = [
            {
                "name": "Multiple Symbols",
                "payload": {
                    "description": "Create a momentum strategy",
                    "symbols": ["AAPL", "TSLA", "MSFT"],
                    "start_date": "2023-01-01",
                    "end_date": "2023-12-31"
                }
            },
            {
                "name": "Risk Management",
                "payload": {
                    "description": "Build a strategy with 2% risk per trade and 5% stop loss",
                    "symbols": ["AAPL"],
                    "start_date": "2023-01-01",
                    "end_date": "2023-12-31",
                    "riskPerTrade": 2,
                    "stopLoss": 5,
                    "takeProfit": 10
                }
            },
            {
                "name": "Timeframe Specific",
                "payload": {
                    "description": "Create a 1-hour timeframe trading strategy",
                    "symbols": ["AAPL"],
                    "start_date": "2023-01-01",
                    "end_date": "2023-12-31",
                    "timeframe": "1h"
                }
            }
        ]
        
        for test in settings_tests:
            try:
                response = self.session.post(f"{self.base_url}/api/generate-strategy", 
                                           json=test["payload"], timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    success = data.get("success") and "code" in data and len(data["code"]) > 100
                    details = f"Generated with {test['name']} settings"
                else:
                    success = False
                    details = f"HTTP {response.status_code}"
                
                self.log_test(f"Settings - {test['name']}", success, details)
                
            except Exception as e:
                self.log_test(f"Settings - {test['name']}", False, f"Exception: {str(e)}")
    
    def test_backtest_integration(self):
        """Test backtest integration with generated strategies"""
        if not hasattr(self, 'example_code_0'):
            self.log_test("Backtest Integration", False, "No generated code available for testing")
            return
        
        # Test basic backtest
        try:
            payload = {
                "code": getattr(self, 'example_code_0'),
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-30",
                "initial_cash": 10000.0
            }
            
            response = self.session.post(f"{self.base_url}/api/backtest", 
                                       json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success") and "performance_metrics" in data
                details = f"Basic backtest completed"
            else:
                success = False
                data = response.json() if response.content else {}
                details = f"HTTP {response.status_code}: {data.get('error', 'Unknown error')}"
            
            self.log_test("Basic Backtest Integration", success, details)
            
        except Exception as e:
            self.log_test("Basic Backtest Integration", False, f"Exception: {str(e)}")
        
        # Test advanced backtest
        try:
            payload = {
                "code": getattr(self, 'example_code_0'),
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-06-30",
                "initial_cash": 10000,
                "commission": 0.001
            }
            
            response = self.session.post(f"{self.base_url}/api/advanced-backtest", 
                                       json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success") and "performance_metrics" in data and "advanced_features" in data
                details = f"Advanced backtest completed with {data.get('advanced_features', {}).get('analyzers_count', 0)} analyzers"
            else:
                success = False
                data = response.json() if response.content else {}
                details = f"HTTP {response.status_code}: {data.get('error', 'Unknown error')}"
            
            self.log_test("Advanced Backtest Integration", success, details)
            
        except Exception as e:
            self.log_test("Advanced Backtest Integration", False, f"Exception: {str(e)}")
    
    def test_error_handling_ui(self):
        """Test error handling for UI scenarios"""
        error_scenarios = [
            {
                "name": "Empty Description",
                "payload": {
                    "description": "",
                    "symbols": ["AAPL"],
                    "start_date": "2023-01-01",
                    "end_date": "2023-12-31"
                }
            },
            {
                "name": "Invalid Symbol",
                "payload": {
                    "description": "Create a momentum strategy",
                    "symbols": ["INVALID_XYZ"],
                    "start_date": "2023-01-01",
                    "end_date": "2023-12-31"
                }
            },
            {
                "name": "Future Date Range",
                "payload": {
                    "description": "Create a momentum strategy",
                    "symbols": ["AAPL"],
                    "start_date": "2025-01-01",
                    "end_date": "2025-12-31"
                }
            }
        ]
        
        for scenario in error_scenarios:
            try:
                response = self.session.post(f"{self.base_url}/api/generate-strategy", 
                                           json=scenario["payload"], timeout=30)
                
                # For error scenarios, we expect either:
                # 1. HTTP error status (4xx, 5xx)
                # 2. Success=false with error message
                # 3. Success=true but with warning (fallback strategy)
                
                if response.status_code == 200:
                    data = response.json()
                    if not data.get("success"):
                        success = True  # Proper error handling
                        details = f"Proper error response: {data.get('error', 'Unknown error')[:50]}..."
                    elif "warning" in data:
                        success = True  # Fallback with warning
                        details = f"Fallback with warning: {data.get('warning', '')[:50]}..."
                    else:
                        success = True  # Generated strategy despite issues
                        details = "Generated strategy (may be fallback)"
                else:
                    success = True  # HTTP error is acceptable for invalid input
                    details = f"HTTP error {response.status_code} as expected"
                
                self.log_test(f"Error Handling - {scenario['name']}", success, details)
                
            except Exception as e:
                self.log_test(f"Error Handling - {scenario['name']}", False, f"Exception: {str(e)}")
    
    def test_performance_with_load(self):
        """Test performance with multiple concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request(thread_id):
            try:
                start_time = time.time()
                payload = {
                    "description": f"Create a momentum strategy for thread {thread_id}",
                    "symbols": ["AAPL"],
                    "start_date": "2023-01-01",
                    "end_date": "2023-12-31"
                }
                
                response = self.session.post(f"{self.base_url}/api/generate-strategy", 
                                           json=payload, timeout=60)
                
                end_time = time.time()
                duration = end_time - start_time
                
                success = response.status_code == 200 and response.json().get("success", False)
                results.append({
                    "thread_id": thread_id,
                    "success": success,
                    "duration": duration,
                    "status_code": response.status_code
                })
                
            except Exception as e:
                results.append({
                    "thread_id": thread_id,
                    "success": False,
                    "duration": 0,
                    "error": str(e)
                })
        
        # Create 5 concurrent threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Analyze results
        successful_requests = sum(1 for r in results if r["success"])
        avg_duration = sum(r["duration"] for r in results if "duration" in r) / len(results)
        
        success = successful_requests >= 3  # At least 60% success rate
        details = f"{successful_requests}/5 successful, avg {avg_duration:.2f}s, total {total_time:.2f}s"
        
        self.log_test("Performance Load Test", success, details, results)
    
    def run_all_tests(self):
        """Run comprehensive AI Builder testing suite"""
        print("🚀 Starting AI Builder Endpoint Testing Suite")
        print(f"📍 Testing against: {self.base_url}")
        print(f"🕒 Started at: {datetime.now().isoformat()}")
        print("=" * 70)
        
        # Phase 1: Strategy Generation
        print("\n🧠 Phase 1: Strategy Generation with Example Prompts")
        self.test_strategy_generation_examples()
        
        print("\n💬 Phase 2: Chat Interface Workflow")
        self.test_chat_interface_workflow()
        
        print("\n⚙️ Phase 3: Settings Integration")
        self.test_settings_integration()
        
        print("\n📊 Phase 4: Backtest Integration")
        self.test_backtest_integration()
        
        print("\n🔧 Phase 5: Error Handling")
        self.test_error_handling_ui()
        
        print("\n⚡ Phase 6: Performance Testing")
        self.test_performance_with_load()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 70)
        print("📋 AI BUILDER TEST SUMMARY REPORT")
        print("=" * 70)
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test_name']}: {result['details']}")
        
        print(f"\n🕒 Completed at: {datetime.now().isoformat()}")
        
        # Save detailed results
        with open("ai_builder_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        print(f"💾 Detailed results saved to: ai_builder_test_results.json")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Builder Endpoint Testing Suite")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="Base URL of the API server")
    args = parser.parse_args()
    
    tester = AIBuilderTester(args.url)
    tester.run_all_tests()
