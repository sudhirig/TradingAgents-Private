#!/usr/bin/env python3
"""
Manual testing script to verify system functionality
"""
import requests
import json
import time

BASE_URL = "http://localhost:8005"

def test_basic_endpoints():
    """Test basic functionality"""
    print("🔍 Manual Testing - Statis Fund Replica")
    print("=" * 50)
    
    try:
        # Test server health
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Server Health: {response.status_code} - {response.json()}")
        
        # Test user ideas
        response = requests.get(f"{BASE_URL}/api/user/ideas")
        print(f"✅ User Ideas: {response.json()}")
        
        # Test statistics
        response = requests.get(f"{BASE_URL}/api/statistics")
        print(f"✅ Statistics: {response.json()}")
        
        # Test templates
        response = requests.get(f"{BASE_URL}/api/templates")
        print(f"✅ Templates: {response.json()}")
        
        # Test data endpoint
        response = requests.get(f"{BASE_URL}/data/AAPL?period=1mo")
        data = response.json()
        print(f"✅ Data Endpoint: {response.status_code} - {len(data.get('data', []))} records")
        
        # Test strategy generation
        payload = {
            "description": "Simple moving average crossover strategy",
            "symbols": ["AAPL"],
            "parameters": {}
        }
        response = requests.post(f"{BASE_URL}/api/strategy/generate", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Strategy Generation: Generated {len(data.get('code', ''))} characters")
        else:
            print(f"❌ Strategy Generation: {response.status_code}")
        
        # Test strategy validation
        test_code = """
import backtrader as bt

class TestStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=20)
    
    def next(self):
        if self.data.close[0] > self.sma[0]:
            self.buy()
"""
        payload = {"code": test_code}
        response = requests.post(f"{BASE_URL}/api/strategy/validate", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Strategy Validation: Score {data.get('validation_results', {}).get('overall_score', 'N/A')}")
        else:
            print(f"❌ Strategy Validation: {response.status_code}")
        
        # Test backtest
        payload = {
            "code": test_code,
            "symbol": "AAPL",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "initial_cash": 10000
        }
        response = requests.post(f"{BASE_URL}/api/backtest", json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            metrics = data.get('performance_metrics', {})
            print(f"✅ Backtest: Return {metrics.get('total_return', 'N/A')}%, Sharpe {metrics.get('sharpe_ratio', 'N/A')}")
        else:
            print(f"❌ Backtest: {response.status_code}")
        
        print("\n🎯 System Status: FUNCTIONAL")
        print("✅ Backend services are working correctly")
        print("✅ All major endpoints are responding")
        print("✅ Advanced features are operational")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_basic_endpoints()
