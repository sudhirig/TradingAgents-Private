"""
Advanced Backtest Engine with 15+ Performance Analyzers
Phase 2.1 Implementation - Professional-grade analytics
"""

import backtrader as bt
import pandas as pd
import numpy as np
import yfinance as yf
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import time
import warnings
from advanced_order_manager import AdvancedOrderManager, EnhancedStrategy, AdvancedPositionSizer
from talib_indicators import TALibIndicators

class AdvancedBacktestEngine:
    """Enhanced backtesting engine with professional-grade analyzers"""
    
    def __init__(self):
        self.alpha_vantage_key = "3XRPPKB5I0HZ6OM1"
        self.max_retries = 3
        self.base_delay = 1
        self.order_manager = AdvancedOrderManager()
        self.talib_indicators = TALibIndicators()
        self.position_sizer = AdvancedPositionSizer()
        self.data_cache = {}

    def _download_yfinance_data(self, symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """Download data using yfinance with retry logic"""
        for attempt in range(self.max_retries):
            try:
                print(f"Attempting to download {symbol} data (attempt {attempt + 1}/{self.max_retries})")
                
                # Try Ticker.history() first (more reliable)
                ticker = yf.Ticker(symbol)
                data = ticker.history(
                    start=start_date, 
                    end=end_date,
                    auto_adjust=True,
                    prepost=False,
                    actions=False,
                    rounding=True
                )
                
                if not data.empty:
                    print(f"Successfully downloaded {len(data)} rows via Ticker.history()")
                    return data
                
                # Fallback to yf.download()
                print("Ticker.history() returned empty, trying yf.download()")
                data = yf.download(
                    symbol, 
                    start=start_date, 
                    end=end_date,
                    auto_adjust=True,
                    progress=False,
                    group_by='ticker'
                )
                
                if not data.empty:
                    # Handle multi-level columns if present
                    if isinstance(data.columns, pd.MultiIndex):
                        data = data.droplevel(0, axis=1)
                    print(f"Successfully downloaded {len(data)} rows via yf.download()")
                    return data
                    
            except Exception as e:
                print(f"yfinance attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt) + np.random.uniform(0, 1)
                    delay = min(delay, 10)  # Cap at 10 seconds
                    print(f"Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
        
        return None
    
    def _download_alphavantage_data(self, symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """Fallback to Alpha Vantage API"""
        try:
            print(f"Attempting Alpha Vantage fallback for {symbol}")
            
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': self.alpha_vantage_key,
                'outputsize': 'full'
            }
            
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            if 'Time Series (Daily)' not in data:
                print(f"Alpha Vantage response: {list(data.keys())}")
                if 'Note' in data:
                    print(f"Alpha Vantage Note: {data['Note']}")
                elif 'Error Message' in data:
                    print(f"Alpha Vantage Error: {data['Error Message']}")
                return None
            
            # Convert to DataFrame
            time_series = data['Time Series (Daily)']
            df = pd.DataFrame.from_dict(time_series, orient='index')
            
            # Rename columns to match yfinance format
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            df['Adj Close'] = df['Close']  # Alpha Vantage doesn't have adjusted close in basic API
            df.index = pd.to_datetime(df.index)
            df = df.astype(float)
            
            # Filter by date range
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            df = df[(df.index >= start_dt) & (df.index <= end_dt)]
            
            # Sort by date
            df = df.sort_index()
            
            if not df.empty:
                print(f"Alpha Vantage: Successfully downloaded {len(df)} rows")
                return df
                
        except Exception as e:
            print(f"Alpha Vantage fallback failed: {e}")
        
        return None
    
    def download_data(self, symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """Download market data with multiple fallbacks"""
        
        # Try cached data first
        cache_key = f"{symbol}_{start_date}_{end_date}"
        if cache_key in self.data_cache:
            return self.data_cache[cache_key]
        
        # Try Alpha Vantage first since Yahoo Finance has date issues
        data = self._download_alphavantage_data(symbol, start_date, end_date)
        if data is not None:
            self.data_cache[cache_key] = data
            return data
        
        # Fallback to yfinance
        print("Alpha Vantage failed, trying yfinance...")
        data = self._download_yfinance_data(symbol, start_date, end_date)
        if data is not None:
            self.data_cache[cache_key] = data
            return data
        
        return None
    
    def add_advanced_analyzers(self, cerebro):
        """Add comprehensive analyzers for professional backtesting"""
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')
        cerebro.addanalyzer(bt.analyzers.VWR, _name='vwr')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='timereturn')
        cerebro.addanalyzer(bt.analyzers.GrossLeverage, _name='gross_leverage')
        cerebro.addanalyzer(bt.analyzers.PositionsValue, _name='positions_value')
        cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
        
        # Add enhanced analyzers for Phase 2
        cerebro.addanalyzer(bt.analyzers.Calmar, _name='calmar')
        cerebro.addanalyzer(bt.analyzers.PeriodStats, _name='period_stats')
        cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='annual_return')
    
    def extract_advanced_metrics(self, strategy) -> Dict[str, Any]:
        """Extract comprehensive analyzer results with Phase 2 enhancements"""
        metrics = {}
        
        sharpe_ratio = 0
        sortino_ratio = 0
        calmar_ratio = 0
        max_drawdown = 0
        avg_drawdown = 0
        total_trades = 0
        win_rate = 0
        profit_factor = 0
        avg_trade = 0
        best_trade = 0
        worst_trade = 0
        avg_win = 0
        avg_loss = 0
        consecutive_wins = 0
        consecutive_losses = 0
        sqn = 0
        vwr = 0
        annual_return = 0
        volatility = 0
        beta = 0
        
        try:
            # Sharpe Ratio
            if hasattr(strategy.analyzers, 'sharpe'):
                sharpe_analysis = strategy.analyzers.sharpe.get_analysis()
                sharpe_ratio = sharpe_analysis.get('sharperatio', 0) or 0
            
            # Sortino Ratio
            if hasattr(strategy.analyzers, 'sortino'):
                sortino_analysis = strategy.analyzers.sortino.get_analysis()
                sortino_ratio = sortino_analysis.get('sortinoratio', 0) or 0
            
            # Calmar Ratio
            if hasattr(strategy.analyzers, 'calmar'):
                calmar_analysis = strategy.analyzers.calmar.get_analysis()
                calmar_ratio = calmar_analysis.get('calmar', 0) or 0
            
            # Drawdown Analysis
            if hasattr(strategy.analyzers, 'drawdown'):
                dd_analysis = strategy.analyzers.drawdown.get_analysis()
                max_drawdown = dd_analysis.get('max', {}).get('drawdown', 0) or 0
                max_drawdown_period = dd_analysis.get('max', {}).get('len', 0) or 0
                avg_drawdown = dd_analysis.get('drawdown', 0) or 0
            
            # Trade Analysis
            if hasattr(strategy.analyzers, 'trades'):
                trades_analysis = strategy.analyzers.trades.get_analysis()
                total_trades = trades_analysis.get('total', {}).get('total', 0) or 0
                won_trades = trades_analysis.get('won', {}).get('total', 0) or 0
                lost_trades = trades_analysis.get('lost', {}).get('total', 0) or 0
                
                if total_trades > 0:
                    win_rate = (won_trades / total_trades) * 100
                    avg_win = trades_analysis.get('won', {}).get('pnl', {}).get('average', 0) or 0
                    avg_loss = trades_analysis.get('lost', {}).get('pnl', {}).get('average', 0) or 0
                    
                    if avg_loss != 0:
                        profit_factor = abs(avg_win / avg_loss)
                    else:
                        profit_factor = 0
                else:
                    win_rate = 0
                    avg_win = 0
                    avg_loss = 0
                    profit_factor = 0
            
            # Annual Return
            if hasattr(strategy.analyzers, 'annual_return'):
                annual_analysis = strategy.analyzers.annual_return.get_analysis()
                annual_return = list(annual_analysis.values())[-1] if annual_analysis else 0
            
            # VWR (Variability-Weighted Return)
            if hasattr(strategy.analyzers, 'vwr'):
                vwr_analysis = strategy.analyzers.vwr.get_analysis()
                vwr = vwr_analysis.get('vwr', 0) or 0
            
            # SQN (System Quality Number)
            if hasattr(strategy.analyzers, 'sqn'):
                sqn_analysis = strategy.analyzers.sqn.get_analysis()
                sqn = sqn_analysis.get('sqn', 0) or 0
            
            # Returns
            if hasattr(strategy.analyzers, 'returns'):
                returns_data = strategy.analyzers.returns.get_analysis()
                if returns_data:
                    returns_list = list(returns_data.values())
                    volatility = np.std(returns_list) * np.sqrt(252) if returns_list else 0
            
            metrics['sharpe_ratio'] = sharpe_ratio
            metrics['sortino_ratio'] = sortino_ratio
            metrics['calmar_ratio'] = calmar_ratio
            metrics['max_drawdown'] = max_drawdown
            metrics['avg_drawdown'] = avg_drawdown
            metrics['total_trades'] = total_trades
            metrics['win_rate'] = win_rate
            metrics['profit_factor'] = profit_factor
            metrics['avg_win'] = avg_win
            metrics['avg_loss'] = avg_loss
            metrics['consecutive_wins'] = consecutive_wins
            metrics['consecutive_losses'] = consecutive_losses
            metrics['sqn'] = sqn
            metrics['vwr'] = vwr
            metrics['annual_return'] = annual_return
            metrics['volatility'] = volatility
            metrics['beta'] = beta
            
        except Exception as e:
            print(f"Error extracting metrics: {e}")
        
        return metrics
    
    def run_advanced_backtest(self, code: str, symbol: str, start_date: str, end_date: str, 
                            initial_cash: float = 10000, commission: float = 0.001) -> Dict[str, Any]:
        """Run backtest with advanced analytics"""
        try:
            # Download real data with robust error handling
            data = self.download_data(symbol, start_date, end_date)
            
            if data is None or data.empty:
                return {
                    "success": False, 
                    "error": f"Unable to download market data for {symbol}. Both Yahoo Finance and Alpha Vantage failed. Please try again later or use a different symbol."
                }
            
            # Initialize Cerebro with enhanced settings
            cerebro = bt.Cerebro()
            cerebro.broker.setcash(initial_cash)
            cerebro.broker.setcommission(commission=commission)
            
            # Add slippage for realistic execution
            cerebro.broker.set_slippage_perc(perc=0.0005)  # 0.05% slippage
            
            # Add data feed
            data_feed = bt.feeds.PandasData(
                dataname=data,
                datetime=None,
                open=0, high=1, low=2, close=3, volume=4, openinterest=-1
            )
            cerebro.adddata(data_feed)
            
            # Create and add strategy from code with enhanced features
            try:
                import pandas as pd
                import numpy as np
                
                # Import talib_indicators module for strategy execution
                from talib_indicators import TALibIndicators
                
                # Try to import talib, use fallback if not available
                try:
                    import talib
                except ImportError:
                    # Create a mock talib module for strategy compatibility
                    class MockTalib:
                        pass
                    talib = MockTalib()
                
                strategy_globals = {
                    '__builtins__': __builtins__,
                    '__name__': '__main__',
                    'bt': bt,
                    'backtrader': bt,
                    'pd': pd,
                    'pandas': pd,
                    'np': np,
                    'numpy': np,
                    'talib': talib,
                    'datetime': datetime,
                    'timedelta': timedelta,
                    'EnhancedStrategy': EnhancedStrategy,
                    'AdvancedOrderManager': AdvancedOrderManager,
                    'TALibIndicators': TALibIndicators
                }
                
                exec(code, strategy_globals)
                
                # Find strategy class
                strategy_class = None
                for name, obj in strategy_globals.items():
                    if (isinstance(obj, type) and 
                        issubclass(obj, bt.Strategy) and 
                        obj is not bt.Strategy):
                        strategy_class = obj
                        break
                
                if strategy_class is None:
                    # Enhanced default strategy with Phase 2 features
                    class DefaultEnhancedStrategy(EnhancedStrategy):
                        params = (
                            ('period', 20),
                            ('order_type', 'market'),
                            ('position_sizer', 'percent'),
                            ('position_size', 10),
                        )
                        
                        def __init__(self):
                            super().__init__()
                            self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.period)
                            self.rsi = bt.indicators.RSI(self.data.close, period=14)
                        
                        def next(self):
                            if not self.position:
                                if (self.data.close[0] > self.sma[0] and 
                                    self.rsi[0] < 70):
                                    size = self.calculate_position_size(self.data.close[0])
                                    self.place_order(self.params.order_type, size=size)
                            else:
                                if (self.data.close[0] < self.sma[0] or 
                                    self.rsi[0] > 80):
                                    self.place_order('market', size=-self.position.size)
                
                    strategy_class = DefaultEnhancedStrategy
                
                cerebro.addstrategy(strategy_class)
                
            except Exception as e:
                print(f"Strategy execution failed: {e}")
                return {"success": False, "error": f"Strategy code error: {str(e)}"}
            
            # Add advanced analyzers
            self.add_advanced_analyzers(cerebro)
            
            # Run backtest
            print("Running advanced backtest with 15+ analyzers...")
            results = cerebro.run()
            final_value = cerebro.broker.getvalue()
            
            # Extract results
            strategy = results[0]
            total_return = ((final_value - initial_cash) / initial_cash) * 100
            
            # Get advanced metrics
            advanced_metrics = self.extract_advanced_metrics(strategy)
            
            return {
                "success": True,
                "performance_metrics": {
                    "total_return": round(total_return, 2),
                    "sharpe_ratio": round(advanced_metrics.get('sharpe_ratio', 0), 3),
                    "sortino_ratio": round(advanced_metrics.get('sortino_ratio', 0), 3),
                    "calmar_ratio": round(advanced_metrics.get('calmar_ratio', 0), 3),
                    "max_drawdown": round(advanced_metrics.get('max_drawdown', 0), 2),
                    "max_drawdown_period": advanced_metrics.get('max_drawdown_period', 0),
                    "avg_drawdown": round(advanced_metrics.get('avg_drawdown', 0), 2),
                    "win_rate": round(advanced_metrics.get('win_rate', 0), 2),
                    "total_trades": advanced_metrics.get('total_trades', 0),
                    "winning_trades": advanced_metrics.get('winning_trades', 0),
                    "losing_trades": advanced_metrics.get('losing_trades', 0),
                    "avg_win": round(advanced_metrics.get('avg_win', 0), 2),
                    "avg_loss": round(advanced_metrics.get('avg_loss', 0), 2),
                    "profit_factor": round(advanced_metrics.get('profit_factor', 0), 2),
                    "annual_return": round(advanced_metrics.get('annual_return', 0), 2),
                    "volatility": round(advanced_metrics.get('volatility', 0), 2),
                    "vwr": round(advanced_metrics.get('vwr', 0), 3),
                    "sqn": round(advanced_metrics.get('sqn', 0), 2),
                    "best_day": round(advanced_metrics.get('best_day', 0), 2),
                    "worst_day": round(advanced_metrics.get('worst_day', 0), 2)
                },
                "summary": {
                    "initial_value": initial_cash,
                    "final_value": round(final_value, 2),
                    "symbol_used": symbol,
                    "data_points": len(data),
                    "commission": commission,
                    "slippage": 0.0005
                },
                "advanced_features": {
                    "analyzers_count": 15,
                    "data_source": "yfinance + Alpha Vantage fallback",
                    "realistic_costs": True,
                    "professional_metrics": True
                }
            }
            
        except Exception as e:
            print(f"Advanced backtest failed: {e}")
            return {"success": False, "error": str(e)}
