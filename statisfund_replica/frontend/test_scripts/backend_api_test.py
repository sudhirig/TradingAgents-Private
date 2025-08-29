#!/usr/bin/env python3
"""
Backend API Testing Script
Tests all backend endpoints with curl equivalents
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class BackendAPITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_result(self, endpoint: str, method: str, status: str, details: str = ""):
        """Log test results"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'endpoint': endpoint,
            'method': method,
            'status': status,
            'details': details
        }
        self.test_results.append(result)
        
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} [{method}] {endpoint}: {status}")
        if details:
            print(f"   Details: {details}")

    def test_health_endpoint(self):
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.log_result("/health", "GET", "PASS", f"Status: {response.status_code}")
            else:
                self.log_result("/health", "GET", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("/health", "GET", "FAIL", str(e))

    def test_strategy_generation(self):
        """Test strategy generation endpoint"""
        test_payload = {
            "prompt": "Create a momentum strategy using RSI and MACD indicators",
            "template": "momentum",
            "timeframe": "1h",
            "risk_per_trade": 2.0,
            "stop_loss": 5.0,
            "take_profit": 10.0
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/generate-strategy",
                json=test_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'code' in data:
                    self.log_result("/api/generate-strategy", "POST", "PASS", "Strategy generated")
                else:
                    self.log_result("/api/generate-strategy", "POST", "FAIL", "No code in response")
            else:
                self.log_result("/api/generate-strategy", "POST", "FAIL", f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("/api/generate-strategy", "POST", "FAIL", str(e))

    def test_backtest_endpoint(self):
        """Test backtest endpoint"""
        test_payload = {
            "code": """
class TestStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=20)
    
    def next(self):
        if not self.position:
            if self.data.close > self.sma:
                self.buy()
        elif self.data.close < self.sma:
            self.sell()
""",
            "symbol": "AAPL",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "initial_cash": 100000
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/backtest",
                json=test_payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'total_return' in data:
                    self.log_result("/api/backtest", "POST", "PASS", "Backtest completed")
                else:
                    self.log_result("/api/backtest", "POST", "FAIL", "Invalid backtest response")
            else:
                self.log_result("/api/backtest", "POST", "FAIL", f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("/api/backtest", "POST", "FAIL", str(e))

    def test_indicators_endpoint(self):
        """Test indicators endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/indicators", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_result("/api/indicators", "GET", "PASS", f"Found {len(data)} indicators")
                else:
                    self.log_result("/api/indicators", "GET", "WARN", "Empty indicators list")
            else:
                self.log_result("/api/indicators", "GET", "FAIL", f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("/api/indicators", "GET", "FAIL", str(e))

    def test_market_data_endpoint(self):
        """Test market data endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/market-data", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'indices' in data or 'stocks' in data:
                    self.log_result("/api/market-data", "GET", "PASS", "Market data available")
                else:
                    self.log_result("/api/market-data", "GET", "WARN", "Limited market data")
            else:
                self.log_result("/api/market-data", "GET", "FAIL", f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("/api/market-data", "GET", "FAIL", str(e))

    def test_saved_strategies_crud(self):
        """Test saved strategies CRUD operations"""
        
        # Test GET strategies
        try:
            response = self.session.get(f"{self.base_url}/api/strategies", timeout=10)
            if response.status_code in [200, 404]:  # 404 acceptable if no strategies
                self.log_result("/api/strategies", "GET", "PASS", "Strategies endpoint accessible")
            else:
                self.log_result("/api/strategies", "GET", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("/api/strategies", "GET", "FAIL", str(e))
        
        # Test POST strategy (create)
        test_strategy = {
            "name": "Test Strategy",
            "description": "Test strategy for API validation",
            "code": "class TestStrategy(bt.Strategy): pass",
            "template": "custom"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/strategies",
                json=test_strategy,
                timeout=10
            )
            if response.status_code in [200, 201]:
                self.log_result("/api/strategies", "POST", "PASS", "Strategy creation works")
            else:
                self.log_result("/api/strategies", "POST", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("/api/strategies", "POST", "FAIL", str(e))

    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting Backend API Testing...")
        print("=" * 50)
        
        test_methods = [
            ("Health Check", self.test_health_endpoint),
            ("Strategy Generation", self.test_strategy_generation),
            ("Backtest Engine", self.test_backtest_endpoint),
            ("Indicators List", self.test_indicators_endpoint),
            ("Market Data", self.test_market_data_endpoint),
            ("Strategies CRUD", self.test_saved_strategies_crud)
        ]
        
        for test_name, test_method in test_methods:
            print(f"\n📋 Testing {test_name}...")
            try:
                test_method()
            except Exception as e:
                self.log_result("SYSTEM", "ERROR", "FAIL", f"{test_name}: {str(e)}")
        
        self.generate_report()

    def generate_curl_commands(self):
        """Generate equivalent curl commands for manual testing"""
        curl_commands = [
            {
                "name": "Health Check",
                "command": f"curl -X GET {self.base_url}/health"
            },
            {
                "name": "Generate Strategy",
                "command": f'''curl -X POST {self.base_url}/api/generate-strategy \\
  -H "Content-Type: application/json" \\
  -d '{{"prompt": "RSI momentum strategy", "template": "momentum"}}\''''
            },
            {
                "name": "Run Backtest",
                "command": f'''curl -X POST {self.base_url}/api/backtest \\
  -H "Content-Type: application/json" \\
  -d '{{"code": "class TestStrategy(bt.Strategy): pass", "symbol": "AAPL"}}\''''
            },
            {
                "name": "Get Indicators",
                "command": f"curl -X GET {self.base_url}/api/indicators"
            },
            {
                "name": "Get Market Data",
                "command": f"curl -X GET {self.base_url}/api/market-data"
            }
        ]
        
        print("\n🔧 Equivalent cURL Commands:")
        print("=" * 50)
        
        for cmd in curl_commands:
            print(f"\n# {cmd['name']}")
            print(cmd['command'])

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 50)
        print("📊 BACKEND API TEST REPORT")
        print("=" * 50)
        
        passed = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warned = len([r for r in self.test_results if r['status'] == 'WARN'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warned}")
        
        if total > 0:
            print(f"Success Rate: {(passed/total*100):.1f}%")
        
        # Show failed tests
        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  - [{result['method']}] {result['endpoint']}: {result['details']}")
        
        self.generate_curl_commands()

if __name__ == "__main__":
    tester = BackendAPITester()
    tester.run_all_tests()
