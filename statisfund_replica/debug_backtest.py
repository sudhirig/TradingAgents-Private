#!/usr/bin/env python3
"""
Debug script to isolate and fix backtesting data feed issues
"""
import asyncio
import requests
import json

async def test_backtest_fix():
    """Test backtesting with enhanced debugging"""
    
    # Test data
    test_code = '''
import backtrader as bt

class TestStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=20)
    
    def next(self):
        if not self.position:
            if self.data.close[0] > self.sma[0]:
                self.buy(size=100)
        else:
            if self.data.close[0] < self.sma[0]:
                self.sell(size=self.position.size)
'''
    
    backtest_request = {
        "code": test_code,
        "symbol": "SPY",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "initial_cash": 10000
    }
    
    print("🔧 Testing Backtest Fix...")
    print(f"Request: {json.dumps(backtest_request, indent=2)}")
    
    try:
        response = requests.post("http://localhost:8005/api/backtest", json=backtest_request, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Backtest Success!")
            print(f"Result: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Backtest Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request Failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_backtest_fix())
