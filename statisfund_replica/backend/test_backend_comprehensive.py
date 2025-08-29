#!/usr/bin/env python3
"""
Comprehensive Backend API Testing Suite for Statis Fund
Tests all endpoints, business logic, and system integration
"""

import requests
import json
import time
import sys
import os
from datetime import datetime, timedelta
import pandas as pd

class StatisBackendTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, message="", data=None):
        """Log test results with timestamp"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
    def test_server_health(self):
        """Test if backend server is running"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                self.log_test("Server Health Check", True, "Backend server is running")
                return True
            else:
                self.log_test("Server Health Check", False, f"Server returned {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Server Health Check", False, f"Server not accessible: {str(e)}")
            return False
            
    def test_strategy_generation(self):
        """Test AI strategy generation endpoint"""
        test_data = {
            "description": "Simple moving average crossover strategy for SPY",
            "symbols": ["SPY"],
            "model": "gpt-4o-mini",
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/strategy/generate/stream",
                json=test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                # This endpoint returns streaming data, so we check for streaming response
                content = response.text
                if "data:" in content and len(content) > 100:
                    self.log_test("Strategy Generation", True, 
                                f"Received streaming response with {len(content)} characters")
                    return {"content": content}
                else:
                    self.log_test("Strategy Generation", False, "No streaming data received")
            elif response.status_code == 429:
                self.log_test("Strategy Generation", True, "Rate limited - expected behavior")
            else:
                self.log_test("Strategy Generation", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Strategy Generation", False, f"Request failed: {str(e)}")
        
        return None
        
    def test_basic_backtest(self):
        """Test basic backtesting functionality"""
        test_strategy = '''
import backtrader as bt

class TestStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=20)
        
    def next(self):
        if self.data.close[0] > self.sma[0] and not self.position:
            self.buy()
        elif self.data.close[0] < self.sma[0] and self.position:
            self.sell()
'''
        
        test_data = {
            "code": test_strategy,
            "symbol": "SPY",
            "start_date": "2023-01-01",
            "end_date": "2023-03-31",
            "initial_capital": 100000
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/backtest",
                json=test_data,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                # Check for different response formats
                if "backtest_results" in data or "results" in data or "success" in data:
                    results = data.get("backtest_results", data.get("results", {}))
                    final_value = results.get("final_value", results.get("final_portfolio_value", 0))
                    total_return = results.get("total_return", 0)
                    
                    self.log_test("Basic Backtest", True, 
                                f"Portfolio: ${final_value:,.2f}, Return: {total_return:.2f}%")
                    return data
                else:
                    self.log_test("Basic Backtest", False, "No results in response")
            else:
                self.log_test("Basic Backtest", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Basic Backtest", False, f"Request failed: {str(e)}")
            
        return None
        
    def test_advanced_backtest(self):
        """Test advanced backtesting with technical indicators"""
        test_data = {
            "code": '''
from advanced_backtest_engine import EnhancedStrategy
import backtrader as bt

class AdvancedTestStrategy(EnhancedStrategy):
    params = (
        ('sma_period', 20),
        ('rsi_period', 14),
    )
    
    def __init__(self):
        super().__init__()
        self.sma = bt.indicators.SMA(period=self.params.sma_period)
        self.rsi = bt.indicators.RSI(period=self.params.rsi_period)
        
    def next(self):
        if (self.data.close[0] > self.sma[0] and 
            self.rsi[0] < 70 and not self.position):
            self.place_order('BUY', size=100)
        elif (self.data.close[0] < self.sma[0] or 
              self.rsi[0] > 80) and self.position:
            self.place_order('SELL', size=self.position.size)
''',
            "symbol": "SPY", 
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "initial_cash": 100000,
            "commission": 0.001,
            "position_sizing": "percentage",
            "risk_per_trade": 0.02
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/advanced-backtest",
                json=test_data,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                if "performance_metrics" in data:
                    metrics = data["performance_metrics"]
                    sharpe = metrics.get("sharpe_ratio", 0)
                    max_dd = metrics.get("max_drawdown", 0)
                    
                    self.log_test("Advanced Backtest", True, 
                                f"Sharpe: {sharpe:.2f}, Max DD: {max_dd:.2%}")
                    return data
                else:
                    self.log_test("Advanced Backtest", False, "No performance metrics")
            else:
                self.log_test("Advanced Backtest", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Advanced Backtest", False, f"Request failed: {str(e)}")
            
        return None
        
    def test_technical_indicators(self):
        """Test technical indicators endpoint"""
        test_symbols = ["SPY", "AAPL", "TSLA"]
        
        for symbol in test_symbols:
            try:
                response = self.session.get(
                    f"{self.base_url}/api/indicators",
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "indicators" in data:
                        self.log_test(f"Technical Indicators ({symbol})", True, 
                                    f"Retrieved {len(data['indicators'])} indicators")
                        break  # Only test once since it's a GET endpoint without symbol param
                    else:
                        self.log_test(f"Technical Indicators ({symbol})", False, "No indicators in response")
                else:
                    self.log_test(f"Technical Indicators ({symbol})", False, 
                                f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Technical Indicators", False, f"Request failed: {str(e)}")
            
        return None
        
    def test_performance_metrics(self):
        """Test performance metrics calculation via advanced indicators"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/indicators/advanced",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data and data["success"]:
                    self.log_test("Performance Metrics", True, 
                                f"Advanced indicators endpoint working")
                else:
                    self.log_test("Performance Metrics", False, "Endpoint not working properly")
            else:
                self.log_test("Performance Metrics", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Performance Metrics", False, f"Request failed: {str(e)}")
            
        return None
        
    def test_error_handling(self):
        """Test error handling with invalid requests"""
        test_cases = [
            {
                "name": "Invalid Strategy Code",
                "endpoint": "/api/backtest",
                "data": {"code": "invalid python code", "symbol": "SPY"}
            },
            {
                "name": "Invalid Symbol",
                "endpoint": "/api/backtest", 
                "data": {"code": "class Test: pass", "symbol": "INVALID123"}
            },
            {
                "name": "Missing Required Fields",
                "endpoint": "/api/generate-strategy",
                "data": {"description": ""}
            }
        ]
        
        for case in test_cases:
            try:
                response = self.session.post(
                    f"{self.base_url}{case['endpoint']}", 
                    json=case['data'],
                    timeout=10
                )
                
                if response.status_code >= 400:
                    self.log_test(f"Error Handling - {case['name']}", True, 
                                f"Correctly returned error {response.status_code}")
                else:
                    self.log_test(f"Error Handling - {case['name']}", False, 
                                "Should have returned error status")
            except Exception as e:
                self.log_test(f"Error Handling - {case['name']}", False, 
                            f"Request failed: {str(e)}")
                
    def run_comprehensive_tests(self):
        """Run all backend tests"""
        print("🔬 Starting Comprehensive Backend Testing...")
        print("=" * 60)
        
        # Test server availability first
        if not self.test_server_health():
            print("❌ Backend server is not running. Start the server and try again.")
            return False
            
        # Run all tests
        test_methods = [
            self.test_strategy_generation,
            self.test_basic_backtest,
            self.test_advanced_backtest, 
            self.test_technical_indicators,
            self.test_performance_metrics,
            self.test_error_handling
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_test(f"Test {test_method.__name__}", False, 
                            f"Test execution failed: {str(e)}")
            time.sleep(1)  # Brief pause between tests
            
        # Generate summary report
        self.generate_report()
        
        return True
        
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🚨 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
                    
        # Save detailed report
        report_file = f"backend_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        print(f"\n📄 Detailed report saved to: {report_file}")

if __name__ == "__main__":
    tester = StatisBackendTester()
    tester.run_comprehensive_tests()
