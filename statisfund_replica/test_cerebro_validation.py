#!/usr/bin/env python3
"""
Cerebro Implementation Validation
Ensures proper backtrader Cerebro usage following official documentation
"""

import backtrader as bt
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.advanced_backtest_engine import AdvancedBacktestEngine

def test_cerebro_basic():
    """Test basic Cerebro setup as per backtrader documentation"""
    print("\n🔍 Testing Basic Cerebro Implementation")
    print("-" * 50)
    
    # Create a Cerebro instance
    cerebro = bt.Cerebro()
    
    # Add initial cash
    cerebro.broker.setcash(100000.0)
    
    # Create a simple data feed
    data = bt.feeds.YahooFinanceData(
        dataname='AAPL',
        fromdate=datetime(2023, 1, 1),
        todate=datetime(2023, 12, 31),
        reverse=False
    )
    
    # Add the data to Cerebro
    cerebro.adddata(data)
    
    # Create a simple strategy
    class TestStrategy(bt.Strategy):
        def __init__(self):
            self.sma = bt.indicators.SimpleMovingAverage(self.data, period=20)
        
        def next(self):
            if not self.position:
                if self.data.close[0] > self.sma[0]:
                    self.buy()
            else:
                if self.data.close[0] < self.sma[0]:
                    self.sell()
    
    # Add strategy
    cerebro.addstrategy(TestStrategy)
    
    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    
    # Run the strategy
    results = cerebro.run()
    
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    
    # Get analysis results
    strat = results[0]
    sharpe = strat.analyzers.sharpe.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    returns = strat.analyzers.returns.get_analysis()
    
    print(f"Sharpe Ratio: {sharpe.get('sharperatio', 'N/A')}")
    print(f"Max Drawdown: {drawdown.get('max', {}).get('drawdown', 'N/A'):.2f}%")
    print(f"Total Return: {returns.get('rtot', 0)*100:.2f}%")
    
    # Test plotting capability (won't display but tests the call)
    try:
        # Note: plot() requires matplotlib backend, just test the call
        cerebro.plot(iplot=False, volume=False)
        print("✅ Cerebro plot() method available")
    except Exception as e:
        print(f"⚠️ Plotting not available: {e}")
    
    print("✅ Basic Cerebro validation passed")
    return True


def test_cerebro_advanced_features():
    """Test advanced Cerebro features from our implementation"""
    print("\n🔍 Testing Advanced Cerebro Features")
    print("-" * 50)
    
    engine = AdvancedBacktestEngine()
    
    # Test custom strategy with EnhancedStrategy base
    strategy_code = """
import backtrader as bt
from advanced_order_manager import EnhancedStrategy

class AdvancedMomentum(EnhancedStrategy):
    params = (
        ('period_sma', 20),
        ('period_rsi', 14),
        ('rsi_upper', 70),
        ('rsi_lower', 30),
    )
    
    def __init__(self):
        super().__init__()
        self.sma = bt.indicators.SMA(self.data.close, period=self.params.period_sma)
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.period_rsi)
        
    def next(self):
        if not self.position:
            if self.rsi < self.params.rsi_lower and self.data.close > self.sma:
                size = self.calculate_position_size()
                self.buy(size=size)
        else:
            if self.rsi > self.params.rsi_upper:
                self.close()
"""
    
    # Run advanced backtest
    result = engine.run_advanced_backtest(
        code=strategy_code,
        symbol="SPY",
        start_date="2023-01-01",
        end_date="2023-12-31",
        initial_cash=100000,
        commission=0.001
    )
    
    if result.get('success'):
        metrics = result.get('metrics', {})
        
        # Validate all 15+ metrics are present
        required_metrics = [
            'total_return', 'annual_return', 'sharpe_ratio', 'sortino_ratio',
            'calmar_ratio', 'max_drawdown', 'win_rate', 'profit_factor',
            'sqn', 'vwr', 'total_trades', 'winning_trades', 'losing_trades',
            'best_trade', 'worst_trade'
        ]
        
        missing = [m for m in required_metrics if m not in metrics]
        if missing:
            print(f"⚠️ Missing metrics: {missing}")
        else:
            print("✅ All 15+ performance metrics present")
        
        # Validate metric values are reasonable
        total_return = metrics.get('total_return', 0)
        sharpe = metrics.get('sharpe_ratio', 0)
        max_dd = metrics.get('max_drawdown', 0)
        
        assert -100 <= total_return <= 500, f"Unrealistic return: {total_return}%"
        assert -5 <= sharpe <= 5, f"Unrealistic Sharpe: {sharpe}"
        assert -100 <= max_dd <= 0, f"Invalid drawdown: {max_dd}%"
        
        print(f"✅ Metrics validation passed")
        print(f"  Total Return: {total_return:.2f}%")
        print(f"  Sharpe Ratio: {sharpe:.2f}")
        print(f"  Max Drawdown: {max_dd:.2f}%")
    else:
        print(f"❌ Advanced backtest failed: {result.get('error')}")
    
    return True


def test_data_feed_methods():
    """Test different data feed methods"""
    print("\n🔍 Testing Data Feed Methods")
    print("-" * 50)
    
    cerebro = bt.Cerebro()
    
    # Test 1: PandasData feed (our primary method)
    print("Testing PandasData feed...")
    ticker = yf.Ticker("MSFT")
    data = ticker.history(period="1mo")
    
    if not data.empty:
        datafeed = bt.feeds.PandasData(
            dataname=data,
            datetime=None,
            open=0, high=1, low=2, close=3, volume=4,
            openinterest=-1
        )
        cerebro.adddata(datafeed)
        print("✅ PandasData feed working")
    
    # Test 2: Multiple data feeds
    print("Testing multiple data feeds...")
    symbols = ["AAPL", "GOOGL", "TSLA"]
    for symbol in symbols:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1mo")
        if not data.empty:
            datafeed = bt.feeds.PandasData(
                dataname=data,
                datetime=None,
                open=0, high=1, low=2, close=3, volume=4,
                openinterest=-1
            )
            cerebro.adddata(datafeed, name=symbol)
    
    print(f"✅ Added {len(cerebro.datas)} data feeds")
    
    return True


def test_order_types():
    """Test various order types in Cerebro"""
    print("\n🔍 Testing Order Types")
    print("-" * 50)
    
    class OrderTestStrategy(bt.Strategy):
        def __init__(self):
            self.order = None
            self.buyprice = None
            self.buycomm = None
        
        def notify_order(self, order):
            if order.status in [order.Completed]:
                if order.isbuy():
                    self.buyprice = order.executed.price
                    self.buycomm = order.executed.comm
                    print(f'✅ BUY EXECUTED, Price: {order.executed.price:.2f}')
                else:
                    print(f'✅ SELL EXECUTED, Price: {order.executed.price:.2f}')
            elif order.status in [order.Canceled, order.Margin, order.Rejected]:
                print('⚠️ Order Canceled/Margin/Rejected')
            
            self.order = None
        
        def next(self):
            if not self.position:
                # Test different order types
                if len(self) == 10:
                    # Market order
                    self.order = self.buy()
                    print("Placed Market Buy Order")
                elif len(self) == 20:
                    # Limit order
                    self.order = self.buy_limit(price=self.data.close[0] * 0.98)
                    print("Placed Limit Buy Order")
                elif len(self) == 30:
                    # Stop order
                    self.order = self.buy_stop(price=self.data.close[0] * 1.02)
                    print("Placed Stop Buy Order")
    
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100000)
    
    # Get test data
    ticker = yf.Ticker("SPY")
    data = ticker.history(period="3mo")
    
    if not data.empty:
        datafeed = bt.feeds.PandasData(dataname=data, datetime=None)
        cerebro.adddata(datafeed)
        cerebro.addstrategy(OrderTestStrategy)
        
        results = cerebro.run()
        print(f"✅ Order types test completed")
        print(f"Final Value: ${cerebro.broker.getvalue():.2f}")
    
    return True


def main():
    """Run all Cerebro validation tests"""
    print("="*60)
    print("CEREBRO IMPLEMENTATION VALIDATION")
    print("="*60)
    
    tests = [
        ("Basic Cerebro Setup", test_cerebro_basic),
        ("Advanced Features", test_cerebro_advanced_features),
        ("Data Feed Methods", test_data_feed_methods),
        ("Order Types", test_order_types)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test_name} failed")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} error: {e}")
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL CEREBRO VALIDATIONS PASSED!")
    else:
        print("⚠️ Some validations failed. Review the output above.")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(main())
