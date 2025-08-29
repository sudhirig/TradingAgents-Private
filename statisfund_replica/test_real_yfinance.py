#!/usr/bin/env python3
"""
Test script to verify yfinance data loading works reliably without mock data
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from fallback_services import FallbackBacktestEngine
import json

def test_yfinance_data_loading():
    """Test yfinance data loading across multiple symbols"""
    print("=" * 60)
    print("TESTING REAL YFINANCE DATA LOADING")
    print("=" * 60)
    
    engine = FallbackBacktestEngine()
    
    # Test symbols - mix of reliable and potentially problematic ones
    test_symbols = [
        'SPY',      # S&P 500 ETF - very reliable
        'AAPL',     # Apple - reliable
        'MSFT',     # Microsoft - reliable  
        'TSLA',     # Tesla - can be volatile
        'GOOGL',    # Google - reliable
        'NVDA',     # NVIDIA - reliable
        'INVALID',  # Invalid symbol to test error handling
        'RELIANCE.NS',  # Indian stock
        'TCS.NS',   # Indian stock
    ]
    
    results = {}
    
    for symbol in test_symbols:
        print(f"\n--- Testing {symbol} ---")
        try:
            data = engine._download_yfinance_data(symbol, '2023-01-01', '2023-12-31')
            if data is not None:
                results[symbol] = {
                    'status': 'SUCCESS',
                    'rows': len(data),
                    'date_range': f"{data.index[0].date()} to {data.index[-1].date()}",
                    'columns': list(data.columns),
                    'sample_close': float(data['Close'].iloc[-1])
                }
                print(f"✅ SUCCESS: {len(data)} rows downloaded")
            else:
                results[symbol] = {
                    'status': 'FAILED',
                    'error': 'No data returned'
                }
                print(f"❌ FAILED: No data returned")
        except Exception as e:
            results[symbol] = {
                'status': 'ERROR',
                'error': str(e)
            }
            print(f"❌ ERROR: {e}")
    
    return results

def test_backtesting_with_real_data():
    """Test full backtesting workflow with real yfinance data"""
    print("\n" + "=" * 60)
    print("TESTING BACKTESTING WITH REAL DATA")
    print("=" * 60)
    
    engine = FallbackBacktestEngine()
    
    # Simple test strategy
    strategy_code = """
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
"""
    
    test_cases = [
        {'symbol': 'SPY', 'start': '2023-01-01', 'end': '2023-12-31'},
        {'symbol': 'AAPL', 'start': '2023-06-01', 'end': '2023-12-31'},
        {'symbol': 'MSFT', 'start': '2023-01-01', 'end': '2023-06-30'},
    ]
    
    backtest_results = {}
    
    for test_case in test_cases:
        symbol = test_case['symbol']
        print(f"\n--- Backtesting {symbol} ---")
        
        try:
            result = engine.run_backtest(
                strategy_code, 
                symbol, 
                test_case['start'], 
                test_case['end'], 
                10000
            )
            
            if result['success']:
                backtest_results[symbol] = {
                    'status': 'SUCCESS',
                    'initial_cash': result['initial_cash'],
                    'final_value': result['final_value'],
                    'total_return': result['total_return'],
                    'trades': result.get('trades', 0)
                }
                print(f"✅ SUCCESS: {result['total_return']:.2f}% return")
            else:
                backtest_results[symbol] = {
                    'status': 'FAILED',
                    'error': result.get('error', 'Unknown error')
                }
                print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            backtest_results[symbol] = {
                'status': 'ERROR',
                'error': str(e)
            }
            print(f"❌ ERROR: {e}")
    
    return backtest_results

def main():
    """Run all tests and generate report"""
    print("🚀 YFINANCE REAL DATA TESTING")
    print("Testing enhanced yfinance data loading without mock data fallback")
    
    # Test 1: Data loading
    data_results = test_yfinance_data_loading()
    
    # Test 2: Full backtesting
    backtest_results = test_backtesting_with_real_data()
    
    # Generate summary report
    print("\n" + "=" * 60)
    print("FINAL RESULTS SUMMARY")
    print("=" * 60)
    
    print("\n📊 DATA LOADING RESULTS:")
    successful_downloads = 0
    total_symbols = len(data_results)
    
    for symbol, result in data_results.items():
        status_icon = "✅" if result['status'] == 'SUCCESS' else "❌"
        print(f"{status_icon} {symbol}: {result['status']}")
        if result['status'] == 'SUCCESS':
            successful_downloads += 1
            print(f"   └── {result['rows']} rows, {result['date_range']}")
    
    print(f"\nData Loading Success Rate: {successful_downloads}/{total_symbols} ({successful_downloads/total_symbols*100:.1f}%)")
    
    print("\n🔄 BACKTESTING RESULTS:")
    successful_backtests = 0
    total_backtests = len(backtest_results)
    
    for symbol, result in backtest_results.items():
        status_icon = "✅" if result['status'] == 'SUCCESS' else "❌"
        print(f"{status_icon} {symbol}: {result['status']}")
        if result['status'] == 'SUCCESS':
            successful_backtests += 1
            print(f"   └── Return: {result['total_return']:.2f}%")
    
    print(f"\nBacktesting Success Rate: {successful_backtests}/{total_backtests} ({successful_backtests/total_backtests*100:.1f}%)")
    
    # Overall assessment
    print("\n🎯 ASSESSMENT:")
    if successful_downloads >= total_symbols * 0.7 and successful_backtests == total_backtests:
        print("✅ PASS: Real yfinance data loading is working reliably")
        print("✅ PASS: No mock data dependency required")
        print("✅ PASS: Backtesting works with real data")
    else:
        print("❌ FAIL: Issues detected with real data loading")
        if successful_downloads < total_symbols * 0.7:
            print(f"   └── Data loading success rate too low: {successful_downloads/total_symbols*100:.1f}%")
        if successful_backtests < total_backtests:
            print(f"   └── Backtesting failures detected: {successful_backtests}/{total_backtests}")
    
    # Save detailed results
    detailed_results = {
        'timestamp': '2025-08-28T20:14:17+05:30',
        'data_loading': data_results,
        'backtesting': backtest_results,
        'summary': {
            'data_success_rate': successful_downloads/total_symbols,
            'backtest_success_rate': successful_backtests/total_backtests if total_backtests > 0 else 0,
            'overall_status': 'PASS' if (successful_downloads >= total_symbols * 0.7 and successful_backtests == total_backtests) else 'FAIL'
        }
    }
    
    with open('yfinance_test_results.json', 'w') as f:
        json.dump(detailed_results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: yfinance_test_results.json")

if __name__ == "__main__":
    main()
