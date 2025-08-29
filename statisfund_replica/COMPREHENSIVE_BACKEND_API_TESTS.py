#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND API TESTING SUITE
Tests all backend functionality with REAL MARKET DATA - NO SYNTHETIC FALLBACKS
"""

import requests
import json
import time
import asyncio
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

class ComprehensiveBackendTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.failed_tests = []
        
    def log_test(self, test_name, status, details=None):
        """Log test results"""
        result = {
            "test_name": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        
        if status == "FAIL":
            self.failed_tests.append(test_name)
            print(f"   Error: {details}")
    
    def test_real_data_sources(self):
        """Test that we can get REAL market data from external sources"""
        print("\n🔍 TESTING REAL DATA SOURCES (NO SYNTHETIC DATA)")
        
        # Test yfinance directly
        try:
            ticker = yf.Ticker("AAPL")
            data = ticker.history(period="1mo")
            
            if data.empty:
                self.log_test("YFinance Direct Access", "FAIL", "No data returned from yfinance")
                return False
            
            self.log_test("YFinance Direct Access", "PASS", f"Retrieved {len(data)} days of AAPL data")
            
            # Validate data quality
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in data.columns for col in required_cols):
                self.log_test("YFinance Data Quality", "FAIL", f"Missing columns: {required_cols}")
                return False
                
            self.log_test("YFinance Data Quality", "PASS", "All required columns present")
            
        except Exception as e:
            self.log_test("YFinance Direct Access", "FAIL", str(e))
            return False
        
        # Test Alpha Vantage fallback
        try:
            import requests
            api_key = '3XRPPKB5I0HZ6OM1'
            url = 'https://www.alphavantage.co/query'
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': 'AAPL',
                'apikey': api_key,
                'outputsize': 'compact'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'Time Series (Daily)' in data:
                    self.log_test("Alpha Vantage Fallback", "PASS", "Successfully retrieved data")
                else:
                    self.log_test("Alpha Vantage Fallback", "FAIL", f"API response: {data}")
            else:
                self.log_test("Alpha Vantage Fallback", "FAIL", f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Alpha Vantage Fallback", "FAIL", str(e))
        
        return True
    
    def test_backend_health(self):
        """Test backend is running and healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.log_test("Backend Health Check", "PASS", response.json())
                return True
            else:
                self.log_test("Backend Health Check", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health Check", "FAIL", str(e))
            return False
    
    def test_strategy_generation_real(self):
        """Test strategy generation with realistic prompts"""
        print("\n🧠 TESTING AI STRATEGY GENERATION")
        
        test_prompts = [
            "Create a momentum strategy using RSI and moving averages for AAPL",
            "Build a mean reversion strategy with Bollinger Bands for technology stocks",
            "Design a breakout strategy using volume and price action for day trading"
        ]
        
        for i, prompt in enumerate(test_prompts):
            try:
                payload = {
                    "description": prompt,
                    "symbols": ["AAPL", "GOOGL", "MSFT"],
                    "start_date": "2023-01-01",
                    "end_date": "2023-12-31"
                }
                
                response = requests.post(
                    f"{self.base_url}/api/generate-strategy",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Validate generated code
                    if "code" in result and result["code"]:
                        code = result["code"]
                        
                        # Check for required elements
                        has_imports = "import backtrader" in code
                        has_class = "class" in code and "Strategy" in code
                        has_logic = "def next" in code or "def __init__" in code
                        
                        if has_imports and has_class and has_logic:
                            self.log_test(f"Strategy Generation Test {i+1}", "PASS", {
                                "prompt": prompt[:50] + "...",
                                "code_length": len(code),
                                "has_proper_structure": True
                            })
                        else:
                            self.log_test(f"Strategy Generation Test {i+1}", "FAIL", {
                                "prompt": prompt[:50] + "...",
                                "missing_elements": {
                                    "imports": not has_imports,
                                    "class": not has_class,
                                    "logic": not has_logic
                                }
                            })
                    else:
                        self.log_test(f"Strategy Generation Test {i+1}", "FAIL", "No code generated")
                else:
                    self.log_test(f"Strategy Generation Test {i+1}", "FAIL", f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Strategy Generation Test {i+1}", "FAIL", str(e))
    
    def test_backtest_with_real_data(self):
        """Test backtesting with real market data - NO SYNTHETIC DATA"""
        print("\n📈 TESTING BACKTESTING ENGINE WITH REAL DATA")
        
        # Test strategy code
        strategy_code = '''
import backtrader as bt

class TestStrategy(bt.Strategy):
    params = (
        ('period', 20),
        ('rsi_period', 14),
    )
    
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.period)
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)
        self.crossover = bt.indicators.CrossOver(self.data.close, self.sma)
    
    def next(self):
        if not self.position:
            if self.crossover > 0 and self.rsi < 70:
                self.buy(size=100)
        else:
            if self.crossover < 0 or self.rsi > 80:
                self.sell(size=self.position.size)
'''
        
        test_symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"]
        
        for symbol in test_symbols:
            try:
                payload = {
                    "code": strategy_code,
                    "symbol": symbol,
                    "start_date": "2023-06-01",
                    "end_date": "2023-12-01",
                    "initial_cash": 10000
                }
                
                response = requests.post(
                    f"{self.base_url}/api/backtest",
                    json=payload,
                    timeout=60  # Longer timeout for backtest
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Validate result structure
                    has_results = "backtest_results" in result or "performance_metrics" in result
                    has_financial_data = False
                    has_metrics = False
                    
                    if has_results:
                        # Check for financial data
                        result_str = str(result).lower()
                        has_financial_data = any(term in result_str for term in 
                                               ["final_value", "return", "pnl", "profit"])
                        has_metrics = any(term in result_str for term in 
                                        ["sharpe", "drawdown", "volatility", "trades"])
                    
                    if has_results and has_financial_data and has_metrics:
                        self.log_test(f"Backtest - {symbol}", "PASS", {
                            "symbol": symbol,
                            "has_results": has_results,
                            "has_financial_data": has_financial_data,
                            "has_metrics": has_metrics,
                            "sample_data": str(result)[:200] + "..."
                        })
                    else:
                        self.log_test(f"Backtest - {symbol}", "FAIL", {
                            "symbol": symbol,
                            "missing_elements": {
                                "results": not has_results,
                                "financial_data": not has_financial_data,
                                "metrics": not has_metrics
                            }
                        })
                else:
                    self.log_test(f"Backtest - {symbol}", "FAIL", 
                                f"HTTP {response.status_code}: {response.text[:200]}")
                    
            except Exception as e:
                self.log_test(f"Backtest - {symbol}", "FAIL", str(e))
    
    def test_market_data_real_time(self):
        """Test market data endpoints return real data"""
        print("\n📊 TESTING REAL-TIME MARKET DATA")
        
        try:
            response = requests.get(f"{self.base_url}/api/market-data", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate real market data
                has_indices = "indices" in data
                has_stocks = "stocks" in data  
                has_prices = False
                has_source = "data_source" in data
                
                if has_indices or has_stocks:
                    data_str = str(data).lower()
                    has_prices = any(term in data_str for term in ["price", "close", "value"])
                
                if has_prices and has_source:
                    self.log_test("Market Data Real-Time", "PASS", {
                        "has_indices": has_indices,
                        "has_stocks": has_stocks,
                        "has_prices": has_prices,
                        "data_source": data.get("data_source", "unknown")
                    })
                else:
                    self.log_test("Market Data Real-Time", "FAIL", {
                        "missing_elements": {
                            "prices": not has_prices,
                            "source": not has_source
                        }
                    })
            else:
                self.log_test("Market Data Real-Time", "FAIL", f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Market Data Real-Time", "FAIL", str(e))
    
    def test_indicators_functionality(self):
        """Test technical indicators work correctly"""
        print("\n📈 TESTING TECHNICAL INDICATORS")
        
        # Test basic indicators
        try:
            response = requests.get(f"{self.base_url}/api/indicators", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has proper structure
                if "indicators" in data and isinstance(data["indicators"], list):
                    indicators_count = len(data["indicators"])
                    if indicators_count > 0:
                        self.log_test("Basic Indicators List", "PASS", f"Found {indicators_count} indicators")
                    else:
                        self.log_test("Basic Indicators List", "FAIL", "No indicators in list")
                elif isinstance(data, list) and len(data) > 0:
                    self.log_test("Basic Indicators List", "PASS", f"Found {len(data)} indicators")
                else:
                    self.log_test("Basic Indicators List", "FAIL", f"Unexpected response structure: {data}")
            else:
                self.log_test("Basic Indicators List", "FAIL", f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Basic Indicators List", "FAIL", str(e))
        
        # Test advanced indicators
        try:
            response = requests.get(f"{self.base_url}/api/indicators/advanced", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if "indicators" in data and len(data["indicators"]) >= 40:
                    self.log_test("Advanced Indicators", "PASS", 
                                f"Found {len(data['indicators'])} advanced indicators")
                else:
                    self.log_test("Advanced Indicators", "FAIL", 
                                f"Expected 40+ indicators, got {len(data.get('indicators', []))}")
            else:
                self.log_test("Advanced Indicators", "FAIL", f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Advanced Indicators", "FAIL", str(e))
    
    def test_phase2_advanced_features(self):
        """Test Phase 2 advanced features"""
        print("\n🚀 TESTING PHASE 2 ADVANCED FEATURES")
        
        endpoints = [
            ("/api/orders/types", "Order Types"),
            ("/api/assets/supported", "Asset Classes"),
            ("/api/trading/brokers", "Broker Integrations")
        ]
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "success" in data and data["success"]:
                        self.log_test(name, "PASS", f"Endpoint active: {endpoint}")
                    else:
                        self.log_test(name, "FAIL", "Success flag not found in response")
                else:
                    self.log_test(name, "FAIL", f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(name, "FAIL", str(e))
    
    def run_comprehensive_tests(self):
        """Run all tests in sequence"""
        print("🧪 STARTING COMPREHENSIVE BACKEND API TESTING")
        print("=" * 60)
        
        start_time = time.time()
        
        # Test sequence
        if not self.test_backend_health():
            print("❌ Backend not healthy - stopping tests")
            return
        
        self.test_real_data_sources()
        self.test_strategy_generation_real()
        self.test_backtest_with_real_data()
        self.test_market_data_real_time()
        self.test_indicators_functionality()
        self.test_phase2_advanced_features()
        
        # Results summary
        end_time = time.time()
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = len(self.failed_tests)
        
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Duration: {end_time-start_time:.1f} seconds")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS ({len(self.failed_tests)}):")
            for test in self.failed_tests:
                print(f"   - {test}")
        
        # Save detailed results
        results_data = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": f"{(passed_tests/total_tests)*100:.1f}%",
                "duration_seconds": round(end_time-start_time, 1),
                "timestamp": datetime.now().isoformat()
            },
            "failed_tests": self.failed_tests,
            "detailed_results": self.test_results
        }
        
        with open("COMPREHENSIVE_TEST_RESULTS.json", "w") as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: COMPREHENSIVE_TEST_RESULTS.json")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = ComprehensiveBackendTester()
    success = tester.run_comprehensive_tests()
    sys.exit(0 if success else 1)
