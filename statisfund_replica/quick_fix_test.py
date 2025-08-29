#!/usr/bin/env python3
"""
Quick test to identify and fix remaining issues
"""

import requests
import json

BASE_URL = "http://localhost:8005"

def test_strategy_saving():
    """Test strategy saving with proper request format"""
    strategy_data = {
        "name": "Test Strategy",
        "description": "Test strategy for debugging",
        "code": "import backtrader as bt\nclass TestStrategy(bt.Strategy):\n    pass",
        "tags": ["test"],
        "symbols": ["AAPL"],
        "parameters": {}
    }
    
    response = requests.post(f"{BASE_URL}/api/strategy/save", json=strategy_data)
    print(f"Strategy Save Response: {response.status_code}")
    print(f"Response: {response.text}")

def test_backtest():
    """Test backtesting with proper parameters"""
    backtest_data = {
        "code": "import backtrader as bt\nclass TestStrategy(bt.Strategy):\n    pass",
        "symbol": "AAPL",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "initial_cash": 10000
    }
    
    response = requests.post(f"{BASE_URL}/api/backtest", json=backtest_data)
    print(f"Backtest Response: {response.status_code}")
    print(f"Response: {response.text}")

def test_data_apis():
    """Test data APIs with proper parameters"""
    
    # Test stock data
    response = requests.get(f"{BASE_URL}/data/AAPL?period=1mo")
    print(f"Stock Data Response: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    
    # Test RSI
    response = requests.get(f"{BASE_URL}/indicator/rsi/AAPL?period=14")
    print(f"RSI Response: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    
    # Test Moving Average
    response = requests.get(f"{BASE_URL}/moving_average/AAPL?period=20&days=30")
    print(f"Moving Average Response: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    print("🔍 QUICK DIAGNOSTIC TESTS")
    print("=" * 40)
    
    print("\n💾 Testing Strategy Saving...")
    test_strategy_saving()
    
    print("\n📊 Testing Backtesting...")
    test_backtest()
    
    print("\n📈 Testing Data APIs...")
    test_data_apis()
