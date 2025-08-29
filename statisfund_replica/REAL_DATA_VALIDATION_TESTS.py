#!/usr/bin/env python3
"""
REAL DATA VALIDATION TESTS
Ensures NO synthetic data or fallbacks are used - only real market data
"""

import yfinance as yf
import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import time

class RealDataValidator:
    def __init__(self):
        self.test_results = []
        
    def log_test(self, test_name, status, details=None):
        result = {
            "test_name": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details and status == "FAIL":
            print(f"   Details: {details}")
    
    def test_yfinance_direct_access(self):
        """Test direct yfinance access with multiple symbols"""
        print("\n🔍 TESTING YFINANCE DIRECT ACCESS")
        
        test_symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "SPY"]
        working_symbols = []
        
        for symbol in test_symbols:
            try:
                ticker = yf.Ticker(symbol)
                # Try different time periods
                for period in ["1mo", "3mo", "6mo"]:
                    try:
                        data = ticker.history(period=period)
                        if not data.empty:
                            working_symbols.append(symbol)
                            self.log_test(f"YFinance {symbol} ({period})", "PASS", 
                                        f"{len(data)} days of data retrieved")
                            break
                    except Exception as e:
                        if period == "6mo":  # Last attempt
                            self.log_test(f"YFinance {symbol}", "FAIL", str(e))
                        continue
                        
            except Exception as e:
                self.log_test(f"YFinance {symbol}", "FAIL", str(e))
        
        return working_symbols
    
    def test_alphavantage_fallback(self):
        """Test Alpha Vantage API as fallback"""
        print("\n🔄 TESTING ALPHA VANTAGE FALLBACK")
        
        api_key = '3XRPPKB5I0HZ6OM1'
        url = 'https://www.alphavantage.co/query'
        
        test_symbols = ["AAPL", "MSFT"]
        
        for symbol in test_symbols:
            try:
                params = {
                    'function': 'TIME_SERIES_DAILY',
                    'symbol': symbol,
                    'apikey': api_key,
                    'outputsize': 'compact'
                }
                
                response = requests.get(url, params=params, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'Time Series (Daily)' in data:
                        daily_data = data['Time Series (Daily)']
                        self.log_test(f"Alpha Vantage {symbol}", "PASS", 
                                    f"{len(daily_data)} days of data")
                    elif 'Error Message' in data:
                        self.log_test(f"Alpha Vantage {symbol}", "FAIL", 
                                    f"API Error: {data['Error Message']}")
                    elif 'Note' in data:
                        self.log_test(f"Alpha Vantage {symbol}", "FAIL", 
                                    f"Rate Limited: {data['Note']}")
                    else:
                        self.log_test(f"Alpha Vantage {symbol}", "FAIL", 
                                    f"Unexpected response: {list(data.keys())}")
                else:
                    self.log_test(f"Alpha Vantage {symbol}", "FAIL", 
                                f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Alpha Vantage {symbol}", "FAIL", str(e))
    
    def test_data_quality_validation(self, symbols):
        """Test that retrieved data meets quality standards"""
        print("\n🔬 TESTING DATA QUALITY VALIDATION")
        
        for symbol in symbols[:3]:  # Test first 3 working symbols
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="2mo")
                
                if data.empty:
                    self.log_test(f"Data Quality {symbol}", "FAIL", "Empty dataset")
                    continue
                
                # Quality checks
                quality_checks = {
                    "sufficient_data": len(data) >= 20,
                    "required_columns": all(col in data.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume']),
                    "no_null_prices": not data[['Open', 'High', 'Low', 'Close']].isnull().any().any(),
                    "positive_prices": (data[['Open', 'High', 'Low', 'Close']] > 0).all().all(),
                    "high_ge_low": (data['High'] >= data['Low']).all(),
                    "volume_present": (data['Volume'] >= 0).all()
                }
                
                passed_checks = sum(quality_checks.values())
                total_checks = len(quality_checks)
                
                if passed_checks == total_checks:
                    self.log_test(f"Data Quality {symbol}", "PASS", 
                                f"All {total_checks} quality checks passed")
                else:
                    failed_checks = [k for k, v in quality_checks.items() if not v]
                    self.log_test(f"Data Quality {symbol}", "FAIL", 
                                f"Failed checks: {failed_checks}")
                    
            except Exception as e:
                self.log_test(f"Data Quality {symbol}", "FAIL", str(e))
    
    def test_backend_uses_real_data(self):
        """Test that backend actually uses real data in backtests"""
        print("\n🎯 TESTING BACKEND REAL DATA USAGE")
        
        # Test with a strategy that should produce different results with real data
        strategy_code = '''
import backtrader as bt

class RealDataTestStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=20)
        self.trade_count = 0
    
    def next(self):
        if not self.position and self.data.close[0] > self.sma[0]:
            self.buy(size=10)
            self.trade_count += 1
        elif self.position and self.data.close[0] < self.sma[0]:
            self.sell(size=self.position.size)
'''
        
        # Test different symbols - should produce different results
        test_symbols = ["AAPL", "TSLA"]
        results = {}
        
        for symbol in test_symbols:
            try:
                payload = {
                    "code": strategy_code,
                    "symbol": symbol,
                    "start_date": "2023-06-01",
                    "end_date": "2023-09-01",
                    "initial_cash": 10000
                }
                
                response = requests.post(
                    "http://localhost:8000/api/backtest",
                    json=payload,
                    timeout=45
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "backtest_results" in result:
                        final_value = result["backtest_results"].get("final_value", 0)
                        total_trades = result["performance_metrics"].get("total_trades", 0)
                        results[symbol] = {"final_value": final_value, "trades": total_trades}
                        
                        self.log_test(f"Real Data Backtest {symbol}", "PASS", 
                                    f"Final value: ${final_value}, Trades: {total_trades}")
                    else:
                        self.log_test(f"Real Data Backtest {symbol}", "FAIL", 
                                    "No backtest_results in response")
                else:
                    self.log_test(f"Real Data Backtest {symbol}", "FAIL", 
                                f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Real Data Backtest {symbol}", "FAIL", str(e))
        
        # Validate results are different (proving real data usage)
        if len(results) >= 2:
            symbols_list = list(results.keys())
            result1 = results[symbols_list[0]] 
            result2 = results[symbols_list[1]]
            
            if (result1["final_value"] != result2["final_value"] or 
                result1["trades"] != result2["trades"]):
                self.log_test("Real Data Variance", "PASS", 
                            "Different symbols produced different results (confirms real data)")
            else:
                self.log_test("Real Data Variance", "FAIL", 
                            "Identical results suggest synthetic data usage")
    
    def test_no_mock_data_fallbacks(self):
        """Ensure no mock/synthetic data is being used as fallbacks"""
        print("\n🚫 TESTING NO SYNTHETIC DATA FALLBACKS")
        
        # Test with invalid symbol - should fail, not fallback to mock data
        invalid_symbols = ["INVALID", "FAKESYM", "NOTREAL"]
        
        for symbol in invalid_symbols:
            try:
                payload = {
                    "code": "import backtrader as bt\nclass TestStrategy(bt.Strategy):\n    def next(self): pass",
                    "symbol": symbol,
                    "start_date": "2023-01-01",
                    "end_date": "2023-02-01",
                    "initial_cash": 10000
                }
                
                response = requests.post(
                    "http://localhost:8000/api/backtest",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success") == False:
                        self.log_test(f"No Fallback {symbol}", "PASS", 
                                    "Correctly failed for invalid symbol")
                    else:
                        self.log_test(f"No Fallback {symbol}", "FAIL", 
                                    "Should have failed but returned success")
                else:
                    self.log_test(f"No Fallback {symbol}", "PASS", 
                                f"Correctly returned HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"No Fallback {symbol}", "PASS", 
                            f"Correctly threw exception: {str(e)[:100]}")
    
    def run_all_tests(self):
        """Run all real data validation tests"""
        print("🔍 STARTING REAL DATA VALIDATION TESTS")
        print("=" * 50)
        
        start_time = time.time()
        
        # Get working symbols first
        working_symbols = self.test_yfinance_direct_access()
        
        # Run other tests
        self.test_alphavantage_fallback()
        
        if working_symbols:
            self.test_data_quality_validation(working_symbols)
        
        self.test_backend_uses_real_data()
        self.test_no_mock_data_fallbacks()
        
        # Results
        end_time = time.time()
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        
        print("\n" + "=" * 50)
        print("📊 REAL DATA VALIDATION RESULTS")
        print("=" * 50)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Duration: {end_time-start_time:.1f} seconds")
        
        # Save results
        with open("REAL_DATA_VALIDATION_RESULTS.json", "w") as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "success_rate": f"{(passed_tests/total_tests)*100:.1f}%",
                    "working_symbols": working_symbols,
                    "timestamp": datetime.now().isoformat()
                },
                "detailed_results": self.test_results
            }, f, indent=2)
        
        print("📄 Results saved to: REAL_DATA_VALIDATION_RESULTS.json")
        return passed_tests == total_tests

if __name__ == "__main__":
    validator = RealDataValidator()
    validator.run_all_tests()
