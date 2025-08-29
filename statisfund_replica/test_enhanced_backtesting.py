#!/usr/bin/env python3
"""
Comprehensive test of enhanced yfinance data loading and backtesting functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from fallback_services import FallbackBacktestEngine
import json
from datetime import datetime

def test_enhanced_backtesting():
    """Test complete backtesting workflow with enhanced features"""
    print("=" * 80)
    print("TESTING ENHANCED BACKTESTING FUNCTIONALITY")
    print("=" * 80)
    
    engine = FallbackBacktestEngine()
    
    # Test strategies with varying complexity - Fixed to ensure trades are generated
    test_strategies = {
        "Simple SMA Strategy": """
import backtrader as bt

class SimpleSMAStrategy(bt.Strategy):
    params = (('period', 10),)
    
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.period)
        self.order = None
        
    def next(self):
        if self.order:
            return
            
        if len(self.data) < self.params.period:
            return
            
        if not self.position:
            if self.data.close[0] > self.sma[0]:
                cash = self.broker.getcash()
                size = int(cash * 0.95 / self.data.close[0])
                if size > 0:
                    self.order = self.buy(size=size)
        else:
            if self.data.close[0] < self.sma[0]:
                self.order = self.sell(size=self.position.size)
                
    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Rejected]:
            self.order = None
""",
        
        "RSI Mean Reversion": """
import backtrader as bt

class RSIMeanReversionStrategy(bt.Strategy):
    params = (('rsi_period', 14), ('rsi_low', 30), ('rsi_high', 70))
    
    def __init__(self):
        self.rsi = bt.indicators.RelativeStrengthIndex(period=self.params.rsi_period)
        self.order = None
        
    def next(self):
        if self.order:
            return
            
        if len(self.data) < self.params.rsi_period:
            return
            
        if not self.position:
            if self.rsi[0] < self.params.rsi_low:
                cash = self.broker.getcash()
                size = int(cash * 0.95 / self.data.close[0])
                if size > 0:
                    self.order = self.buy(size=size)
        else:
            if self.rsi[0] > self.params.rsi_high:
                self.order = self.sell(size=self.position.size)
                
    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Rejected]:
            self.order = None
""",
        
        "Multi-Indicator Strategy": """
import backtrader as bt

class MultiIndicatorStrategy(bt.Strategy):
    params = (('sma_period', 10), ('rsi_period', 14))
    
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(period=self.params.sma_period)
        self.rsi = bt.indicators.RelativeStrengthIndex(period=self.params.rsi_period)
        self.order = None
        
    def next(self):
        if self.order:
            return
            
        if len(self.data) < max(self.params.sma_period, self.params.rsi_period):
            return
            
        if not self.position:
            # Buy when price > SMA and RSI < 70
            if self.data.close[0] > self.sma[0] and self.rsi[0] < 70:
                cash = self.broker.getcash()
                size = int(cash * 0.95 / self.data.close[0])
                if size > 0:
                    self.order = self.buy(size=size)
        else:
            # Sell when price < SMA or RSI > 70
            if self.data.close[0] < self.sma[0] or self.rsi[0] > 70:
                self.order = self.sell(size=self.position.size)
                
    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Rejected]:
            self.order = None
"""
    }
    
    # Test symbols including real and synthetic fallback scenarios
    test_symbols = ['SPY', 'AAPL', 'INVALID_SYMBOL']
    
    results = {}
    
    for strategy_name, strategy_code in test_strategies.items():
        print(f"\n{'='*60}")
        print(f"TESTING: {strategy_name}")
        print(f"{'='*60}")
        
        strategy_results = {}
        
        for symbol in test_symbols:
            print(f"\n--- Testing {strategy_name} with {symbol} ---")
            
            try:
                result = engine.run_backtest(
                    strategy_code,
                    symbol,
                    '2023-01-01',
                    '2023-12-31',
                    10000
                )
                
                if result.get('success'):
                    metrics = result.get('performance_metrics', {})
                    strategy_results[symbol] = {
                        'status': 'SUCCESS',
                        'total_return': metrics.get('total_return', 0),
                        'sharpe_ratio': metrics.get('sharpe_ratio', 0),
                        'max_drawdown': metrics.get('max_drawdown', 0),
                        'total_trades': metrics.get('total_trades', 0),
                        'win_rate': metrics.get('win_rate', 0),
                        'final_value': metrics.get('final_value', 0)
                    }
                    print(f"✅ SUCCESS: {metrics.get('total_return', 0):.2f}% return, {metrics.get('total_trades', 0)} trades")
                else:
                    strategy_results[symbol] = {
                        'status': 'FAILED',
                        'error': result.get('error', 'Unknown error')
                    }
                    print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                strategy_results[symbol] = {
                    'status': 'ERROR',
                    'error': str(e)
                }
                print(f"❌ ERROR: {e}")
        
        results[strategy_name] = strategy_results
    
    return results

def test_data_quality():
    """Test data quality and validation"""
    print("\n" + "=" * 80)
    print("TESTING DATA QUALITY AND VALIDATION")
    print("=" * 80)
    
    engine = FallbackBacktestEngine()
    
    test_cases = [
        {'symbol': 'SPY', 'start': '2023-01-01', 'end': '2023-12-31', 'expected': 'real_or_synthetic'},
        {'symbol': 'AAPL', 'start': '2023-06-01', 'end': '2023-12-31', 'expected': 'real_or_synthetic'},
        {'symbol': 'INVALID', 'start': '2023-01-01', 'end': '2023-06-30', 'expected': 'synthetic'},
        {'symbol': 'RELIANCE.NS', 'start': '2023-01-01', 'end': '2023-12-31', 'expected': 'real_or_synthetic'},
    ]
    
    data_quality_results = {}
    
    for test_case in test_cases:
        symbol = test_case['symbol']
        print(f"\n--- Testing data quality for {symbol} ---")
        
        try:
            data = engine._download_yfinance_data(
                symbol, 
                test_case['start'], 
                test_case['end']
            )
            
            if data is not None:
                # Analyze data quality
                quality_metrics = {
                    'rows': len(data),
                    'date_range': f"{data.index[0].date()} to {data.index[-1].date()}",
                    'price_range': f"${data['Low'].min():.2f} - ${data['High'].max():.2f}",
                    'avg_volume': int(data['Volume'].mean()),
                    'missing_values': data.isnull().sum().sum(),
                    'valid_ohlc': (data['High'] >= data['Low']).all(),
                    'positive_prices': (data[['Open', 'High', 'Low', 'Close']] > 0).all().all(),
                    'columns': list(data.columns)
                }
                
                data_quality_results[symbol] = {
                    'status': 'SUCCESS',
                    'quality_metrics': quality_metrics
                }
                
                print(f"✅ SUCCESS: {quality_metrics['rows']} rows, {quality_metrics['date_range']}")
                print(f"   Price range: {quality_metrics['price_range']}")
                print(f"   Valid OHLC: {quality_metrics['valid_ohlc']}")
                print(f"   Positive prices: {quality_metrics['positive_prices']}")
                
            else:
                data_quality_results[symbol] = {
                    'status': 'FAILED',
                    'error': 'No data returned'
                }
                print(f"❌ FAILED: No data returned")
                
        except Exception as e:
            data_quality_results[symbol] = {
                'status': 'ERROR',
                'error': str(e)
            }
            print(f"❌ ERROR: {e}")
    
    return data_quality_results

def generate_comprehensive_report(backtest_results, data_quality_results):
    """Generate comprehensive test report"""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE TEST RESULTS REPORT")
    print("=" * 80)
    
    # Backtest results summary
    print("\n📊 BACKTESTING RESULTS SUMMARY:")
    total_tests = 0
    successful_tests = 0
    
    for strategy_name, strategy_results in backtest_results.items():
        print(f"\n🔹 {strategy_name}:")
        for symbol, result in strategy_results.items():
            total_tests += 1
            status_icon = "✅" if result['status'] == 'SUCCESS' else "❌"
            print(f"  {status_icon} {symbol}: {result['status']}")
            
            if result['status'] == 'SUCCESS':
                successful_tests += 1
                print(f"     └── Return: {result['total_return']:.2f}%, Trades: {result['total_trades']}, Sharpe: {result['sharpe_ratio']:.3f}")
    
    backtest_success_rate = successful_tests / total_tests if total_tests > 0 else 0
    print(f"\nBacktest Success Rate: {successful_tests}/{total_tests} ({backtest_success_rate*100:.1f}%)")
    
    # Data quality summary
    print("\n📈 DATA QUALITY RESULTS SUMMARY:")
    data_tests = 0
    data_successes = 0
    
    for symbol, result in data_quality_results.items():
        data_tests += 1
        status_icon = "✅" if result['status'] == 'SUCCESS' else "❌"
        print(f"{status_icon} {symbol}: {result['status']}")
        
        if result['status'] == 'SUCCESS':
            data_successes += 1
            metrics = result['quality_metrics']
            print(f"   └── {metrics['rows']} rows, {metrics['price_range']}, Valid: {metrics['valid_ohlc']}")
    
    data_success_rate = data_successes / data_tests if data_tests > 0 else 0
    print(f"\nData Quality Success Rate: {data_successes}/{data_tests} ({data_success_rate*100:.1f}%)")
    
    # Overall assessment
    print("\n🎯 OVERALL ASSESSMENT:")
    if backtest_success_rate >= 0.8 and data_success_rate >= 0.8:
        print("✅ EXCELLENT: Enhanced backtesting system is working reliably")
        print("✅ Data loading is robust with proper fallbacks")
        print("✅ Multiple strategy types execute successfully")
        print("✅ Ready for Phase 2 enhancements")
    elif backtest_success_rate >= 0.6 and data_success_rate >= 0.6:
        print("⚠️  GOOD: System is functional with minor issues")
        print("⚠️  Some improvements needed before Phase 2")
    else:
        print("❌ NEEDS WORK: Significant issues detected")
        print("❌ Address core issues before proceeding")
    
    # Performance insights
    print("\n💡 PERFORMANCE INSIGHTS:")
    best_strategy = None
    best_return = float('-inf')
    
    for strategy_name, strategy_results in backtest_results.items():
        avg_return = 0
        successful_symbols = 0
        
        for symbol, result in strategy_results.items():
            if result['status'] == 'SUCCESS':
                avg_return += result['total_return']
                successful_symbols += 1
        
        if successful_symbols > 0:
            avg_return /= successful_symbols
            print(f"📈 {strategy_name}: Avg Return {avg_return:.2f}%")
            
            if avg_return > best_return:
                best_return = avg_return
                best_strategy = strategy_name
    
    if best_strategy:
        print(f"🏆 Best Performing Strategy: {best_strategy} ({best_return:.2f}% avg return)")
    
    return {
        'backtest_success_rate': backtest_success_rate,
        'data_success_rate': data_success_rate,
        'total_tests': total_tests,
        'successful_tests': successful_tests,
        'best_strategy': best_strategy,
        'best_return': best_return,
        'timestamp': datetime.now().isoformat()
    }

def main():
    """Run comprehensive enhanced backtesting tests"""
    print("🚀 ENHANCED BACKTESTING SYSTEM TEST")
    print("Testing improved yfinance data loading and backtesting capabilities")
    
    # Test 1: Enhanced backtesting with multiple strategies
    backtest_results = test_enhanced_backtesting()
    
    # Test 2: Data quality validation
    data_quality_results = test_data_quality()
    
    # Test 3: Generate comprehensive report
    summary = generate_comprehensive_report(backtest_results, data_quality_results)
    
    # Save detailed results
    detailed_results = {
        'summary': summary,
        'backtest_results': backtest_results,
        'data_quality_results': data_quality_results,
        'test_metadata': {
            'test_date': datetime.now().isoformat(),
            'test_version': 'enhanced_v2.0',
            'features_tested': [
                'Enhanced yfinance data loading',
                'Synthetic data fallback',
                'Multiple strategy types',
                'Data quality validation',
                'Performance analytics'
            ]
        }
    }
    
    with open('enhanced_backtesting_test_results.json', 'w') as f:
        json.dump(detailed_results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: enhanced_backtesting_test_results.json")
    
    return summary

if __name__ == "__main__":
    main()
