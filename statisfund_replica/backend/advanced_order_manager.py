"""
Advanced Order Management System
Phase 2.2 Implementation - 8+ Order Types with Professional Execution
"""

import backtrader as bt
from typing import Dict, Any, Optional, List
from enum import Enum
import numpy as np


class OrderType(Enum):
    """Enhanced order types for professional trading"""
    MARKET = "Market"
    LIMIT = "Limit"
    STOP = "Stop"
    STOP_LIMIT = "StopLimit"
    TRAILING_STOP = "TrailingStop"
    TRAILING_STOP_LIMIT = "TrailingStopLimit"
    OCO = "OCO"  # One-Cancels-Other
    BRACKET = "Bracket"


class PositionSizer(Enum):
    """Position sizing algorithms"""
    FIXED = "Fixed"
    PERCENT = "Percent"
    KELLY = "Kelly"
    OPTIMAL_F = "OptimalF"
    VOLATILITY = "Volatility"


class AdvancedOrderManager:
    """Professional order management with 8+ order types"""
    
    def __init__(self):
        self.active_orders = {}
        self.oco_groups = {}
        self.bracket_orders = {}
        
    def create_market_order(self, strategy, size: float, **kwargs):
        """Create market order"""
        if size > 0:
            return strategy.buy(size=abs(size))
        else:
            return strategy.sell(size=abs(size))
    
    def create_limit_order(self, strategy, size: float, price: float, **kwargs):
        """Create limit order"""
        if size > 0:
            return strategy.buy(size=abs(size), price=price, exectype=bt.Order.Limit)
        else:
            return strategy.sell(size=abs(size), price=price, exectype=bt.Order.Limit)
    
    def create_stop_order(self, strategy, size: float, stop_price: float, **kwargs):
        """Create stop order"""
        if size > 0:
            return strategy.buy(size=abs(size), price=stop_price, exectype=bt.Order.Stop)
        else:
            return strategy.sell(size=abs(size), price=stop_price, exectype=bt.Order.Stop)
    
    def create_stop_limit_order(self, strategy, size: float, stop_price: float, 
                              limit_price: float, **kwargs):
        """Create stop-limit order"""
        if size > 0:
            return strategy.buy(size=abs(size), price=stop_price, 
                              plimit=limit_price, exectype=bt.Order.StopLimit)
        else:
            return strategy.sell(size=abs(size), price=stop_price,
                               plimit=limit_price, exectype=bt.Order.StopLimit)
    
    def create_trailing_stop(self, strategy, size: float, trail_amount: float, 
                           trail_percent: Optional[float] = None, **kwargs):
        """Create trailing stop order"""
        if trail_percent:
            trail_amount = strategy.data.close[0] * (trail_percent / 100)
        
        if size > 0:
            return strategy.sell(size=abs(size), price=strategy.data.close[0] - trail_amount,
                               exectype=bt.Order.StopTrail, trailamount=trail_amount)
        else:
            return strategy.buy(size=abs(size), price=strategy.data.close[0] + trail_amount,
                              exectype=bt.Order.StopTrail, trailamount=trail_amount)
    
    def create_oco_order(self, strategy, orders: List[Dict], group_id: str, **kwargs):
        """Create One-Cancels-Other order group"""
        oco_orders = []
        
        for order_config in orders:
            order_type = order_config.get('type', 'market')
            size = order_config.get('size', 100)
            
            if order_type.lower() == 'limit':
                order = self.create_limit_order(strategy, size, order_config['price'])
            elif order_type.lower() == 'stop':
                order = self.create_stop_order(strategy, size, order_config['stop_price'])
            else:
                order = self.create_market_order(strategy, size)
            
            oco_orders.append(order)
        
        self.oco_groups[group_id] = oco_orders
        return oco_orders
    
    def create_bracket_order(self, strategy, entry_size: float, entry_price: float,
                           stop_loss: float, take_profit: float, **kwargs):
        """Create bracket order (entry + stop loss + take profit)"""
        # Entry order
        entry_order = self.create_limit_order(strategy, entry_size, entry_price)
        
        # Stop loss and take profit (will be activated after entry fills)
        bracket_id = f"bracket_{len(self.bracket_orders)}"
        self.bracket_orders[bracket_id] = {
            'entry': entry_order,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'size': entry_size,
            'filled': False
        }
        
        return entry_order


class AdvancedPositionSizer:
    """Professional position sizing algorithms"""
    
    @staticmethod
    def fixed_size(cash: float, price: float, fixed_amount: float) -> int:
        """Fixed dollar amount position sizing"""
        return int(fixed_amount / price)
    
    @staticmethod
    def percent_size(cash: float, price: float, percent: float) -> int:
        """Percentage of portfolio position sizing"""
        return int((cash * percent / 100) / price)
    
    @staticmethod
    def kelly_criterion(win_rate: float, avg_win: float, avg_loss: float, 
                       cash: float, price: float) -> int:
        """Kelly Criterion position sizing"""
        if avg_loss == 0 or win_rate == 0:
            return 0
        
        win_loss_ratio = avg_win / abs(avg_loss)
        kelly_fraction = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25%
        
        return int((cash * kelly_fraction) / price)
    
    @staticmethod
    def volatility_sizing(cash: float, price: float, volatility: float, 
                         target_risk: float = 0.02) -> int:
        """Volatility-based position sizing"""
        if volatility == 0:
            return int((cash * 0.1) / price)  # Default to 10%
        
        position_value = (cash * target_risk) / volatility
        return int(position_value / price)


class EnhancedStrategy(bt.Strategy):
    """Enhanced strategy base class with advanced order management"""
    
    params = (
        ('order_type', 'market'),
        ('position_sizer', 'percent'),
        ('position_size', 10),  # 10% default
        ('stop_loss_pct', 5),   # 5% stop loss
        ('take_profit_pct', 10), # 10% take profit
        ('trailing_stop_pct', 3), # 3% trailing stop
    )
    
    def __init__(self):
        self.order_manager = AdvancedOrderManager()
        self.position_sizer = AdvancedPositionSizer()
        self.active_orders = []
        
        # Performance tracking for Kelly Criterion
        self.trade_history = []
        self.win_rate = 0.5
        self.avg_win = 0
        self.avg_loss = 0
    
    def calculate_position_size(self, price: float) -> int:
        """Calculate position size based on selected algorithm"""
        cash = self.broker.getcash()
        
        if self.params.position_sizer == 'fixed':
            return self.position_sizer.fixed_size(cash, price, self.params.position_size)
        elif self.params.position_sizer == 'percent':
            return self.position_sizer.percent_size(cash, price, self.params.position_size)
        elif self.params.position_sizer == 'kelly':
            return self.position_sizer.kelly_criterion(
                self.win_rate, self.avg_win, self.avg_loss, cash, price
            )
        elif self.params.position_sizer == 'volatility':
            # Calculate recent volatility
            returns = np.diff(np.log([self.data.close[-i] for i in range(20, 0, -1)]))
            volatility = np.std(returns) * np.sqrt(252)
            return self.position_sizer.volatility_sizing(cash, price, volatility)
        else:
            return self.position_sizer.percent_size(cash, price, 10)  # Default 10%
    
    def place_order(self, order_type: str, size: float = None, **kwargs):
        """Place order using advanced order manager"""
        if size is None:
            size = self.calculate_position_size(self.data.close[0])
        
        if order_type.lower() == 'market':
            return self.order_manager.create_market_order(self, size, **kwargs)
        elif order_type.lower() == 'limit':
            return self.order_manager.create_limit_order(self, size, **kwargs)
        elif order_type.lower() == 'stop':
            return self.order_manager.create_stop_order(self, size, **kwargs)
        elif order_type.lower() == 'stop_limit':
            return self.order_manager.create_stop_limit_order(self, size, **kwargs)
        elif order_type.lower() == 'trailing_stop':
            return self.order_manager.create_trailing_stop(self, size, **kwargs)
        elif order_type.lower() == 'bracket':
            return self.order_manager.create_bracket_order(self, size, **kwargs)
        else:
            return self.order_manager.create_market_order(self, size)
    
    def update_performance_stats(self):
        """Update performance statistics for Kelly Criterion"""
        if len(self.trade_history) > 10:  # Need sufficient history
            wins = [t for t in self.trade_history if t > 0]
            losses = [t for t in self.trade_history if t < 0]
            
            self.win_rate = len(wins) / len(self.trade_history)
            self.avg_win = np.mean(wins) if wins else 0
            self.avg_loss = np.mean(losses) if losses else 0
    
    def notify_trade(self, trade):
        """Track trade performance"""
        if trade.isclosed:
            self.trade_history.append(trade.pnl)
            self.update_performance_stats()
    
    def notify_order(self, order):
        """Handle order notifications for advanced order management"""
        # Handle bracket order logic
        for bracket_id, bracket in self.order_manager.bracket_orders.items():
            if bracket['entry'] == order and order.status == order.Completed:
                # Entry filled, place stop loss and take profit
                if not bracket['filled']:
                    size = bracket['size']
                    
                    # Stop loss
                    self.order_manager.create_stop_order(
                        self, -size, bracket['stop_loss']
                    )
                    
                    # Take profit
                    self.order_manager.create_limit_order(
                        self, -size, bracket['take_profit']
                    )
                    
                    bracket['filled'] = True
        
        # Handle OCO logic
        for group_id, orders in self.order_manager.oco_groups.items():
            if order in orders and order.status == order.Completed:
                # Cancel other orders in the group
                for other_order in orders:
                    if other_order != order and other_order.status == order.Submitted:
                        self.cancel(other_order)


# Example advanced strategy using new order management
class AdvancedMomentumStrategy(EnhancedStrategy):
    """Example strategy using advanced order management"""
    
    params = (
        ('period', 20),
        ('rsi_period', 14),
        ('order_type', 'bracket'),
        ('position_sizer', 'kelly'),
    )
    
    def __init__(self):
        super().__init__()
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.period)
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)
        self.bb = bt.indicators.BollingerBands(self.data.close, period=self.params.period)
    
    def next(self):
        if not self.position:
            # Entry conditions
            if (self.data.close[0] > self.sma[0] and 
                self.rsi[0] < 70 and 
                self.data.close[0] > self.bb.lines.mid[0]):
                
                current_price = self.data.close[0]
                stop_loss = current_price * (1 - self.params.stop_loss_pct / 100)
                take_profit = current_price * (1 + self.params.take_profit_pct / 100)
                
                # Place bracket order
                self.place_order(
                    'bracket',
                    entry_price=current_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit
                )
        
        # Exit conditions (if not using bracket orders)
        elif self.position and self.params.order_type != 'bracket':
            if (self.data.close[0] < self.sma[0] or self.rsi[0] > 80):
                self.place_order('market', size=-self.position.size)
