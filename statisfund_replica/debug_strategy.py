#!/usr/bin/env python3
"""
Debug script to test strategy execution with detailed logging
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from fallback_services import FallbackBacktestEngine
import json

def test_simple_strategy():
    """Test a very simple strategy with debugging"""
    
    engine = FallbackBacktestEngine()
    
    # Simple strategy that should definitely generate trades
    strategy_code = """
import backtrader as bt

class DebugStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=5)
        self.trade_count = 0
        self.order = None
        
    def next(self):
        # Print debug info every 20 days
        if len(self.data) % 20 == 0:
            cash = self.broker.getcash()
            value = self.broker.getvalue()
            pos_size = self.position.size
            print(f"Day {len(self.data)}: Price={self.data.close[0]:.2f}, Cash=${cash:.2f}, Value=${value:.2f}, Position={pos_size}")
        
        # Cancel pending orders
        if self.order:
            return
        
        # Simple buy and hold with some selling
        if len(self.data) > 5:  # Wait for SMA to be ready
            if not self.position and len(self.data) % 30 == 10:  # Buy every 30 days
                # Calculate position size based on available cash
                cash = self.broker.getcash()
                price = self.data.close[0]
                size = int(cash * 0.95 / price)  # Use 95% of cash
                if size > 0:
                    print(f"BUY signal at day {len(self.data)}, price {price:.2f}, size {size}")
                    self.order = self.buy(size=size)
                    self.trade_count += 1
            elif self.position and len(self.data) % 30 == 25:  # Sell 5 days later
                print(f"SELL signal at day {len(self.data)}, price {self.data.close[0]:.2f}, size {self.position.size}")
                self.order = self.sell(size=self.position.size)
                self.trade_count += 1
                
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                print(f"BUY EXECUTED: Price {order.executed.price:.2f}, Size {order.executed.size}")
            else:
                print(f"SELL EXECUTED: Price {order.executed.price:.2f}, Size {order.executed.size}")
        self.order = None
                
    def stop(self):
        final_value = self.broker.getvalue()
        print(f"Strategy finished. Total trade signals: {self.trade_count}, Final value: ${final_value:.2f}")
"""
    
    print("Testing debug strategy with SPY...")
    result = engine.run_backtest(strategy_code, 'SPY', '2023-01-01', '2023-12-31', 10000)
    
    print("\n" + "="*60)
    print("RESULT:")
    print(json.dumps(result, indent=2))
    
    return result

if __name__ == "__main__":
    test_simple_strategy()
