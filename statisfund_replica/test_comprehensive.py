#!/usr/bin/env python3
"""
Comprehensive Testing Suite for Statis Fund Replica
Tests all backend services, API endpoints, and system functionality
"""

import asyncio
import json
import requests
import time
from datetime import datetime, timedelta
import sys
import os

# Add backend to path
sys.path.append('/Users/Gautam/TradingAgents/statisfund_replica/backend')

# Test configuration
BASE_URL = "http://localhost:8005"
TEST_RESULTS = {
    "timestamp": datetime.now().isoformat(),
    "tests_passed": 0,
    "tests_failed": 0,
    "test_details": []
}

def log_test(test_name, passed, details=""):
    """Log test results"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   {details}")
    
    TEST_RESULTS["test_details"].append({
        "test": test_name,
        "passed": passed,
        "details": details,
        "timestamp": datetime.now().isoformat()
    })
    
    if passed:
        TEST_RESULTS["tests_passed"] += 1
    else:
        TEST_RESULTS["tests_failed"] += 1

def test_server_health():
    """Test if backend server is running"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        log_test("Server Health Check", response.status_code == 200, 
                f"Status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        log_test("Server Health Check", False, f"Error: {str(e)}")
        return False

def test_user_ideas_endpoint():
    """Test user ideas tracking"""
    try:
        response = requests.get(f"{BASE_URL}/api/user/ideas", timeout=5)
        data = response.json()
        log_test("User Ideas Endpoint", response.status_code == 200 and 'ideas_remaining' in data,
                f"Ideas remaining: {data.get('ideas_remaining', 'N/A')}")
        return response.status_code == 200
    except Exception as e:
        log_test("User Ideas Endpoint", False, f"Error: {str(e)}")
        return False

def test_strategy_generation():
    """Test strategy generation endpoint (non-streaming)"""
    try:
        payload = {
            "description": "Simple moving average crossover strategy for testing",
            "symbols": ["AAPL"],
            "parameters": {"fast_period": 10, "slow_period": 20}
        }
        
        response = requests.post(f"{BASE_URL}/api/strategy/generate", 
                               json=payload, timeout=30)
        data = response.json()
        
        success = (response.status_code == 200 and 
                  'code' in data and 
                  len(data['code']) > 100)
        
        log_test("Strategy Generation", success,
                f"Generated {len(data.get('code', ''))} characters of code")
        return success
    except Exception as e:
        log_test("Strategy Generation", False, f"Error: {str(e)}")
        return False

def test_strategy_validation():
    """Test strategy validation service"""
    try:
        # Test with valid strategy code
        valid_code = """
import backtrader as bt

class TestStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=20)
    
    def next(self):
        if self.data.close[0] > self.sma[0]:
            self.buy()
        elif self.data.close[0] < self.sma[0]:
            self.sell()
"""
        
        payload = {"code": valid_code}
        response = requests.post(f"{BASE_URL}/api/strategy/validate", 
                               json=payload, timeout=15)
        data = response.json()
        
        success = (response.status_code == 200 and 
                  data.get('success', False) and
                  'validation_results' in data)
        
        log_test("Strategy Validation", success,
                f"Validation score: {data.get('validation_results', {}).get('overall_score', 'N/A')}")
        return success
    except Exception as e:
        log_test("Strategy Validation", False, f"Error: {str(e)}")
        return False

def test_backtest_engine():
    """Test backtesting functionality"""
    try:
        # Simple strategy for backtesting
        strategy_code = """
import backtrader as bt

class TestStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=20)
    
    def next(self):
        if not self.position:
            if self.data.close[0] > self.sma[0]:
                self.buy()
        else:
            if self.data.close[0] < self.sma[0]:
                self.sell()
"""
        
        payload = {
            "code": strategy_code,
            "symbol": "AAPL",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "initial_cash": 10000
        }
        
        response = requests.post(f"{BASE_URL}/api/backtest", 
                               json=payload, timeout=60)
        data = response.json()
        
        success = (response.status_code == 200 and 
                  data.get('success', False) and
                  'performance_metrics' in data)
        
        metrics = data.get('performance_metrics', {})
        log_test("Backtest Engine", success,
                f"Total return: {metrics.get('total_return', 'N/A')}%, Sharpe: {metrics.get('sharpe_ratio', 'N/A')}")
        return success
    except Exception as e:
        log_test("Backtest Engine", False, f"Error: {str(e)}")
        return False

def test_strategy_management():
    """Test strategy save/load functionality"""
    try:
        # Save a strategy
        strategy_data = {
            "name": "Test Strategy",
            "description": "Test strategy for comprehensive testing",
            "code": "import backtrader as bt\n\nclass TestStrategy(bt.Strategy):\n    pass",
            "tags": ["test", "simple"],
            "symbols": ["AAPL"],
            "parameters": {"test_param": 1}
        }
        
        # Save strategy
        save_response = requests.post(f"{BASE_URL}/api/strategy/save", 
                                    json=strategy_data, timeout=10)
        save_data = save_response.json()
        
        if not (save_response.status_code == 200 and save_data.get('success')):
            log_test("Strategy Management - Save", False, "Failed to save strategy")
            return False
        
        strategy_id = save_data.get('strategy_id')
        
        # Load strategies list
        list_response = requests.get(f"{BASE_URL}/api/strategies", timeout=10)
        list_data = list_response.json()
        
        # Load specific strategy
        load_response = requests.get(f"{BASE_URL}/api/strategy/{strategy_id}", timeout=10)
        load_data = load_response.json()
        
        success = (list_response.status_code == 200 and 
                  load_response.status_code == 200 and
                  load_data.get('success', False))
        
        log_test("Strategy Management", success,
                f"Saved strategy ID: {strategy_id}, Total strategies: {len(list_data.get('strategies', []))}")
        return success
    except Exception as e:
        log_test("Strategy Management", False, f"Error: {str(e)}")
        return False

def test_data_endpoints():
    """Test Statis Fund compatible data endpoints"""
    try:
        # Test stock data endpoint
        data_response = requests.get(f"{BASE_URL}/data/AAPL?period=1mo", timeout=15)
        
        # Test indicator endpoint
        rsi_response = requests.get(f"{BASE_URL}/indicator/rsi/AAPL?period=14", timeout=15)
        
        # Test moving average endpoint
        ma_response = requests.get(f"{BASE_URL}/moving_average/AAPL?period=20&days=30", timeout=15)
        
        success = (data_response.status_code == 200 and 
                  rsi_response.status_code == 200 and
                  ma_response.status_code == 200)
        
        log_test("Data Endpoints", success,
                f"Data: {data_response.status_code}, RSI: {rsi_response.status_code}, MA: {ma_response.status_code}")
        return success
    except Exception as e:
        log_test("Data Endpoints", False, f"Error: {str(e)}")
        return False

def test_statistics_endpoint():
    """Test platform statistics"""
    try:
        response = requests.get(f"{BASE_URL}/api/statistics", timeout=10)
        data = response.json()
        
        success = (response.status_code == 200 and 
                  data.get('success', False) and
                  'statistics' in data)
        
        stats = data.get('statistics', {})
        log_test("Statistics Endpoint", success,
                f"Total strategies: {stats.get('total_strategies', 'N/A')}")
        return success
    except Exception as e:
        log_test("Statistics Endpoint", False, f"Error: {str(e)}")
        return False

def test_templates_endpoint():
    """Test strategy templates"""
    try:
        response = requests.get(f"{BASE_URL}/api/templates", timeout=10)
        data = response.json()
        
        success = (response.status_code == 200 and 
                  data.get('success', False))
        
        templates = data.get('templates', [])
        log_test("Templates Endpoint", success,
                f"Available templates: {len(templates)}")
        return success
    except Exception as e:
        log_test("Templates Endpoint", False, f"Error: {str(e)}")
        return False

def test_streaming_endpoint():
    """Test SSE streaming endpoint"""
    try:
        import requests
        
        payload = {
            "description": "Simple test strategy for streaming",
            "symbols": ["AAPL"]
        }
        
        # Test streaming endpoint (just check if it starts)
        response = requests.post(f"{BASE_URL}/api/strategy/generate/stream", 
                               json=payload, stream=True, timeout=10)
        
        # Read first few chunks
        chunks_received = 0
        for chunk in response.iter_lines():
            if chunk:
                chunks_received += 1
                if chunks_received >= 3:  # Just test first few chunks
                    break
        
        success = response.status_code == 200 and chunks_received > 0
        log_test("SSE Streaming", success,
                f"Received {chunks_received} chunks")
        return success
    except Exception as e:
        log_test("SSE Streaming", False, f"Error: {str(e)}")
        return False

def run_comprehensive_tests():
    """Run all tests"""
    print("🚀 Starting Comprehensive Statis Fund Replica Tests")
    print("=" * 60)
    
    # Check if server is running
    if not test_server_health():
        print("❌ Backend server is not running. Please start it first.")
        return False
    
    print("\n📡 Testing API Endpoints...")
    test_user_ideas_endpoint()
    test_data_endpoints()
    test_statistics_endpoint()
    test_templates_endpoint()
    
    print("\n🧠 Testing AI Services...")
    test_strategy_generation()
    test_streaming_endpoint()
    test_strategy_validation()
    
    print("\n📊 Testing Backtesting...")
    test_backtest_engine()
    
    print("\n💾 Testing Strategy Management...")
    test_strategy_management()
    
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    total_tests = TEST_RESULTS["tests_passed"] + TEST_RESULTS["tests_failed"]
    pass_rate = (TEST_RESULTS["tests_passed"] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"✅ Tests Passed: {TEST_RESULTS['tests_passed']}")
    print(f"❌ Tests Failed: {TEST_RESULTS['tests_failed']}")
    print(f"📊 Pass Rate: {pass_rate:.1f}%")
    
    if TEST_RESULTS["tests_failed"] > 0:
        print("\n❌ Failed Tests:")
        for test in TEST_RESULTS["test_details"]:
            if not test["passed"]:
                print(f"   • {test['test']}: {test['details']}")
    
    # Save detailed results
    with open('/Users/Gautam/TradingAgents/statisfund_replica/test_results.json', 'w') as f:
        json.dump(TEST_RESULTS, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: test_results.json")
    
    return TEST_RESULTS["tests_failed"] == 0

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
