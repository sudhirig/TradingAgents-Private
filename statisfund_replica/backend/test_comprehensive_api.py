#!/usr/bin/env python3
"""
Comprehensive API Testing Suite for Statis Fund Replica Backend
Tests all endpoints with real stock data (AAPL, TSLA, MSFT) and edge cases
"""

import requests
import json
import time
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List
import traceback

class ComprehensiveAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.symbols = ["AAPL", "TSLA", "MSFT", "GOOGL", "NVDA"]
        self.session = requests.Session()
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
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
            print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
        
    def test_health_check(self):
        """Test basic health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            success = response.status_code == 200 and "healthy" in response.json().get("status", "")
            self.log_test("Health Check", success, f"Status: {response.status_code}", response.json())
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
    
    def test_cors_preflight(self):
        """Test CORS preflight requests"""
        origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000", 
            "http://localhost:5173",
            "http://127.0.0.1:8080"
        ]
        
        for origin in origins:
            try:
                headers = {
                    "Origin": origin,
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type"
                }
                response = self.session.options(f"{self.base_url}/api/generate-strategy", headers=headers, timeout=5)
                
                success = (response.status_code == 200 and 
                          "access-control-allow-origin" in response.headers)
                
                self.log_test(f"CORS Preflight - {origin}", success, 
                            f"Status: {response.status_code}, Headers: {dict(response.headers)}")
            except Exception as e:
                self.log_test(f"CORS Preflight - {origin}", False, f"Exception: {str(e)}")
    
    def test_strategy_generation(self):
        """Test strategy generation with various descriptions"""
        test_cases = [
            {
                "description": "Simple moving average crossover strategy for AAPL",
                "symbols": ["AAPL"]
            },
            {
                "description": "RSI momentum strategy with Bollinger Bands for TSLA",
                "symbols": ["TSLA"]
            },
            {
                "description": "Mean reversion strategy using MACD for MSFT",
                "symbols": ["MSFT"]
            }
        ]
        
        for i, case in enumerate(test_cases):
            try:
                payload = {
                    "description": case["description"],
                    "symbols": case["symbols"],
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
                    
                    details = f"Generated {len(data.get('code', ''))} chars of code"
                    if "warning" in data:
                        details += f", Warning: {data['warning'][:50]}..."
                        
                else:
                    success = False
                    data = response.json() if response.content else {}
                    details = f"HTTP {response.status_code}"
                
                self.log_test(f"Strategy Generation - Case {i+1}", success, details, data)
                
                # Store generated code for backtest tests
                if success and "code" in data:
                    case["generated_code"] = data["code"]
                    
            except Exception as e:
                self.log_test(f"Strategy Generation - Case {i+1}", False, f"Exception: {str(e)}")
        
        return test_cases
    
    def test_basic_backtest(self, test_cases: List[Dict]):
        """Test basic backtest endpoint with generated strategies"""
        for i, case in enumerate(test_cases):
            if "generated_code" not in case:
                continue
                
            try:
                payload = {
                    "code": case["generated_code"],
                    "symbol": case["symbols"][0],
                    "start_date": "2023-01-01",
                    "end_date": "2023-06-30",
                    "initial_cash": 10000.0
                }
                
                response = self.session.post(f"{self.base_url}/api/backtest", 
                                           json=payload, timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    success = (data.get("success") and
                              "performance_metrics" in data and
                              "summary" in data)
                    
                    if success:
                        metrics = data["performance_metrics"]
                        summary = data["summary"]
                        details = (f"Return: {metrics.get('total_return', 0):.2f}%, "
                                 f"Sharpe: {metrics.get('sharpe_ratio', 0):.3f}, "
                                 f"Trades: {metrics.get('total_trades', 0)}")
                    else:
                        details = f"Missing required fields in response"
                else:
                    success = False
                    data = response.json() if response.content else {}
                    details = f"HTTP {response.status_code}: {data.get('error', 'Unknown error')}"
                
                self.log_test(f"Basic Backtest - {case['symbols'][0]}", success, details, data)
                
            except Exception as e:
                self.log_test(f"Basic Backtest - {case['symbols'][0]}", False, f"Exception: {str(e)}")
    
    def test_advanced_backtest(self, test_cases: List[Dict]):
        """Test advanced backtest endpoint with Phase 2 features"""
        for i, case in enumerate(test_cases):
            if "generated_code" not in case:
                continue
                
            try:
                payload = {
                    "code": case["generated_code"],
                    "symbol": case["symbols"][0],
                    "start_date": "2023-01-01",
                    "end_date": "2023-06-30",
                    "initial_cash": 10000,
                    "commission": 0.001,
                    "order_type": "market",
                    "position_sizer": "percent",
                    "position_size": 100
                }
                
                response = self.session.post(f"{self.base_url}/api/advanced-backtest", 
                                           json=payload, timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    success = (data.get("success") and
                              "performance_metrics" in data and
                              "advanced_features" in data)
                    
                    if success:
                        metrics = data["performance_metrics"]
                        features = data["advanced_features"]
                        details = (f"Return: {metrics.get('total_return', 0):.2f}%, "
                                 f"Sharpe: {metrics.get('sharpe_ratio', 0):.3f}, "
                                 f"Analyzers: {features.get('analyzers_count', 0)}")
                    else:
                        details = f"Missing required fields in response"
                else:
                    success = False
                    data = response.json() if response.content else {}
                    details = f"HTTP {response.status_code}: {data.get('error', 'Unknown error')}"
                
                self.log_test(f"Advanced Backtest - {case['symbols'][0]}", success, details, data)
                
            except Exception as e:
                self.log_test(f"Advanced Backtest - {case['symbols'][0]}", False, f"Exception: {str(e)}")
    
    def test_fenced_code_handling(self):
        """Test markdown fence stripping in both backtest endpoints"""
        fenced_strategy = '''```python
import backtrader as bt

class TestStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=20)
    
    def next(self):
        if not self.position and self.data.close[0] > self.sma[0]:
            self.buy(size=100)
        elif self.position and self.data.close[0] < self.sma[0]:
            self.sell(size=self.position.size)
```'''
        
        # Test basic backtest
        try:
            payload = {
                "code": fenced_strategy,
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-03-31",
                "initial_cash": 10000.0
            }
            
            response = self.session.post(f"{self.base_url}/api/backtest", json=payload, timeout=30)
            success = response.status_code == 200 and response.json().get("success", False)
            details = f"Basic backtest with fences: {response.status_code}"
            
            self.log_test("Fenced Code - Basic Backtest", success, details, response.json())
            
        except Exception as e:
            self.log_test("Fenced Code - Basic Backtest", False, f"Exception: {str(e)}")
        
        # Test advanced backtest
        try:
            payload = {
                "code": fenced_strategy,
                "symbol": "AAPL", 
                "start_date": "2023-01-01",
                "end_date": "2023-03-31",
                "initial_cash": 10000,
                "commission": 0.001
            }
            
            response = self.session.post(f"{self.base_url}/api/advanced-backtest", json=payload, timeout=30)
            success = response.status_code == 200 and response.json().get("success", False)
            details = f"Advanced backtest with fences: {response.status_code}"
            
            self.log_test("Fenced Code - Advanced Backtest", success, details, response.json())
            
        except Exception as e:
            self.log_test("Fenced Code - Advanced Backtest", False, f"Exception: {str(e)}")
    
    def test_error_handling(self):
        """Test error handling with invalid inputs"""
        error_cases = [
            {
                "name": "Invalid Symbol",
                "endpoint": "/api/backtest",
                "payload": {
                    "code": "import backtrader as bt\nclass TestStrategy(bt.Strategy):\n    pass",
                    "symbol": "INVALID_SYMBOL_XYZ",
                    "start_date": "2023-01-01",
                    "end_date": "2023-02-01",
                    "initial_cash": 10000
                }
            },
            {
                "name": "Invalid Date Range",
                "endpoint": "/api/backtest",
                "payload": {
                    "code": "import backtrader as bt\nclass TestStrategy(bt.Strategy):\n    pass",
                    "symbol": "AAPL",
                    "start_date": "2025-01-01",
                    "end_date": "2025-12-31",
                    "initial_cash": 10000
                }
            },
            {
                "name": "Malformed Code",
                "endpoint": "/api/backtest",
                "payload": {
                    "code": "this is not valid python code!!!",
                    "symbol": "AAPL",
                    "start_date": "2023-01-01",
                    "end_date": "2023-02-01",
                    "initial_cash": 10000
                }
            },
            {
                "name": "Missing Required Field",
                "endpoint": "/api/generate-strategy",
                "payload": {
                    "symbols": ["AAPL"]
                    # Missing description
                }
            }
        ]
        
        for case in error_cases:
            try:
                response = self.session.post(f"{self.base_url}{case['endpoint']}", 
                                           json=case["payload"], timeout=30)
                
                # Error handling should return proper error messages, not crash
                if response.status_code == 200:
                    data = response.json()
                    success = not data.get("success", True) and "error" in data
                    details = f"Proper error handling: {data.get('error', '')[:50]}..."
                elif response.status_code in [400, 422, 500]:
                    success = True
                    details = f"HTTP error code {response.status_code} as expected"
                else:
                    success = False
                    details = f"Unexpected status code: {response.status_code}"
                
                self.log_test(f"Error Handling - {case['name']}", success, details)
                
            except Exception as e:
                self.log_test(f"Error Handling - {case['name']}", False, f"Exception: {str(e)}")
    
    def test_indicators_endpoint(self):
        """Test indicators and market data endpoints"""
        endpoints = [
            "/api/indicators",
            "/api/indicators/advanced", 
            "/api/market-data",
            "/api/orders/types",
            "/api/assets/supported",
            "/api/trading/brokers"
        ]
        
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    success = data.get("success", True)  # Some endpoints don't have success field
                    details = f"Returned {len(str(data))} chars of data"
                else:
                    success = False
                    details = f"HTTP {response.status_code}"
                
                self.log_test(f"Endpoint - {endpoint}", success, details)
                
            except Exception as e:
                self.log_test(f"Endpoint - {endpoint}", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Comprehensive API Testing Suite")
        print(f"📍 Testing against: {self.base_url}")
        print(f"🕒 Started at: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Phase 1: Basic connectivity
        print("\n📡 Phase 1: Basic Connectivity Tests")
        self.test_health_check()
        self.test_cors_preflight()
        
        # Phase 2: Core functionality
        print("\n🧠 Phase 2: Strategy Generation Tests")
        test_cases = self.test_strategy_generation()
        
        print("\n📊 Phase 3: Backtesting Tests")
        self.test_basic_backtest(test_cases)
        self.test_advanced_backtest(test_cases)
        
        # Phase 4: Edge cases
        print("\n🔧 Phase 4: Edge Case Tests")
        self.test_fenced_code_handling()
        self.test_error_handling()
        
        # Phase 5: Supporting endpoints
        print("\n📈 Phase 5: Supporting Endpoint Tests")
        self.test_indicators_endpoint()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY REPORT")
        print("=" * 60)
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
        with open("test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        print(f"💾 Detailed results saved to: test_results.json")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive API Testing Suite")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="Base URL of the API server")
    args = parser.parse_args()
    
    tester = ComprehensiveAPITester(args.url)
    tester.run_all_tests()
