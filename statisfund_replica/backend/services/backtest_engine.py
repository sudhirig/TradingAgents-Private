import backtrader as bt
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import io
import sys
import types
import warnings
import asyncio
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import base64

# Suppress warnings
warnings.filterwarnings('ignore')

class BacktestEngine:
    def __init__(self):
        self.cerebro = None
        self.data_cache = {}
        
    async def run_backtest(self, code: str, symbols: List[str], start_date: str, 
                          end_date: str, initial_cash: float, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute comprehensive backtest using Backtrader"""
        
        # Initialize Cerebro with optimized settings
        cerebro = bt.Cerebro(stdstats=False)
        cerebro.broker.setcash(initial_cash)
        
        # Set realistic commission for USA stocks (0.005% per trade)
        cerebro.broker.setcommission(commission=0.00005)
        
        # Add slippage simulation
        cerebro.broker.set_slippage_perc(perc=0.001)  # 0.1% slippage
        
        # Add data feeds for all symbols with enhanced error handling
        data_feeds = {}
        for symbol in symbols:
            try:
                print(f"Loading data for {symbol}...")
                data = await self._get_data(symbol, start_date, end_date)
                if not data.empty and len(data) > 0:
                    # Validate data quality
                    if len(data) < 10:
                        print(f"Warning: Insufficient data for {symbol} ({len(data)} rows)")
                        continue
                    
                    # Create data feed with proper datetime index
                    data_feed = bt.feeds.PandasData(
                        dataname=data,
                        name=symbol,
                        plot=False,  # Disable plotting for performance
                        datetime=None,  # Use index as datetime
                        open=0, high=1, low=2, close=3, volume=4, openinterest=-1
                    )
                    cerebro.adddata(data_feed)
                    data_feeds[symbol] = data
                    print(f"Successfully loaded {len(data)} rows for {symbol}")
                else:
                    print(f"Warning: Empty data for {symbol}")
            except Exception as e:
                print(f"Error loading data for {symbol}: {e}")
                # Try fallback with different date range
                try:
                    fallback_start = pd.to_datetime(start_date) - pd.Timedelta(days=30)
                    fallback_data = await self._get_data(symbol, fallback_start.strftime('%Y-%m-%d'), end_date)
                    if not fallback_data.empty and len(fallback_data) > 10:
                        data_feed = bt.feeds.PandasData(
                            dataname=fallback_data,
                            name=symbol,
                            plot=False,
                            datetime=None,
                            open=0, high=1, low=2, close=3, volume=4, openinterest=-1
                        )
                        cerebro.adddata(data_feed)
                        data_feeds[symbol] = fallback_data
                        print(f"Fallback: loaded {len(fallback_data)} rows for {symbol}")
                except Exception as fallback_error:
                    print(f"Fallback also failed for {symbol}: {fallback_error}")
        
        if not data_feeds:
            raise ValueError(f"Unable to download market data for {', '.join(symbols)}. Yahoo Finance API is currently experiencing issues or rate limiting. Please try again later or use a different symbol.")
        
        # Load and add strategy
        strategy_class = self._load_strategy_from_code(code)
        cerebro.addstrategy(strategy_class, **parameters)
        
        # Add comprehensive analyzers
        analyzers = self._add_analyzers(cerebro)
        
        # Add observers for detailed tracking
        cerebro.addobserver(bt.observers.Broker)
        cerebro.addobserver(bt.observers.Trades)
        cerebro.addobserver(bt.observers.BuySell)
        
        # Capture strategy logs
        old_stdout = sys.stdout
        sys.stdout = log_capture = io.StringIO()
        
        try:
            # Run backtest
            print(f"Starting backtest for {symbols} from {start_date} to {end_date}")
            results = cerebro.run()
            final_value = cerebro.broker.getvalue()
            
            # Extract comprehensive results
            strategy = results[0]
            analyzer_results = self._extract_analyzer_results(strategy, analyzers)
            
            # Generate performance chart
            chart_data = self._generate_performance_chart(cerebro, initial_cash, final_value)
            
        except Exception as e:
            raise ValueError(f"Backtest execution failed: {str(e)}")
        finally:
            logs = log_capture.getvalue()
            sys.stdout = old_stdout
        
        # Calculate additional metrics
        total_return = ((final_value - initial_cash) / initial_cash) * 100
        
        return {
            'summary': {
                'initial_cash': initial_cash,
                'final_value': round(final_value, 2),
                'total_return': round(total_return, 2),
                'total_return_abs': round(final_value - initial_cash, 2),
                'symbols': symbols,
                'period': f"{start_date} to {end_date}",
                'duration_days': (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days
            },
            'performance_metrics': analyzer_results,
            'logs': logs,
            'chart_data': chart_data,
            'data_feeds': list(data_feeds.keys()),
            'timestamp': datetime.now().isoformat()
        }
    
    async def _get_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch and cache historical data"""
        
        cache_key = f"{symbol}_{start_date}_{end_date}"
        
        if cache_key in self.data_cache:
            return self.data_cache[cache_key]
        
        try:
            # Handle different symbol formats
            if not any(symbol.endswith(suffix) for suffix in ['.NS', '.BO']):
                # USA stock - no suffix needed
                ticker = symbol
            else:
                # Indian stock
                ticker = symbol
            
            # Download data with retry logic
            for attempt in range(3):
                try:
                    data = yf.download(
                        ticker, 
                        start=start_date, 
                        end=end_date, 
                        auto_adjust=True, 
                        progress=False,
                        threads=True
                    )
                    
                    if not data.empty:
                        # Clean and validate data
                        data = data.dropna()
                        
                        # Ensure required columns exist
                        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                        if all(col in data.columns for col in required_cols):
                            # Cache the data
                            self.data_cache[cache_key] = data
                            return data
                        
                except Exception as e:
                    if attempt == 2:  # Last attempt
                        raise e
                    import asyncio
                    await asyncio.sleep(1)  # Wait before retry
            
            raise ValueError(f"No valid data found for {symbol}")
            
        except Exception as e:
            raise ValueError(f"Data fetch failed for {symbol}: {str(e)}")
    
    def _load_strategy_from_code(self, code: str) -> type:
        """Safely load strategy class from code string with enhanced security"""
        
        # Create isolated module
        module = types.ModuleType("user_strategy")
        
        # Define comprehensive safe builtins
        safe_builtins = {
            '__builtins__': {
                # Math functions
                'abs': abs, 'round': round, 'min': min, 'max': max, 'sum': sum,
                'len': len, 'range': range, 'enumerate': enumerate,
                'zip': zip, 'map': map, 'filter': filter, 'sorted': sorted,
                'any': any, 'all': all, 'bool': bool, 'int': int, 'float': float,
                'str': str, 'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
                
                # Safe imports
                'datetime': datetime, 'pd': pd, 'np': np, 'bt': bt,
                
                # Debug functions
                'print': print,
                
                # Exception handling
                'Exception': Exception, 'ValueError': ValueError, 'TypeError': TypeError
            }
        }
        
        # Add safe numpy and pandas to module namespace
        module.__dict__['np'] = np
        module.__dict__['pd'] = pd
        module.__dict__['bt'] = bt
        module.__dict__['datetime'] = datetime
        
        try:
            # Execute code in sandboxed environment
            exec(code, safe_builtins, module.__dict__)
        except Exception as e:
            raise ValueError(f"Strategy code execution failed: {str(e)}")
        
        # Find and validate strategy class
        strategy_classes = []
        for name, obj in module.__dict__.items():
            if (isinstance(obj, type) and 
                issubclass(obj, bt.Strategy) and 
                obj is not bt.Strategy):
                strategy_classes.append(obj)
        
        if not strategy_classes:
            raise ValueError("No valid Strategy class found in code")
        
        if len(strategy_classes) > 1:
            raise ValueError("Multiple Strategy classes found. Please define only one.")
        
        return strategy_classes[0]
    
    def _add_analyzers(self, cerebro: bt.Cerebro) -> Dict[str, str]:
        """Add comprehensive analyzers for detailed performance metrics"""
        
        analyzers = {
            'sharpe': 'SharpeRatio',
            'drawdown': 'DrawDown', 
            'returns': 'Returns',
            'trades': 'TradeAnalyzer',
            'sqn': 'SQN',
            'vwr': 'VWR',
            'calmar': 'CalmarRatio',
            'positions': 'PositionsValue',
            'transactions': 'Transactions'
        }
        
        for name, analyzer_class in analyzers.items():
            try:
                analyzer = getattr(bt.analyzers, analyzer_class)
                cerebro.addanalyzer(analyzer, _name=name)
            except AttributeError:
                print(f"Warning: Analyzer {analyzer_class} not available")
        
        return analyzers
    
    def _extract_analyzer_results(self, strategy, analyzers: Dict[str, str]) -> Dict[str, Any]:
        """Extract and format analyzer results"""
        
        results = {}
        
        try:
            # Sharpe Ratio
            if hasattr(strategy.analyzers, 'sharpe'):
                sharpe_analysis = strategy.analyzers.sharpe.get_analysis()
                results['sharpe_ratio'] = round(sharpe_analysis.get('sharperatio', 0), 3)
            
            # Drawdown Analysis
            if hasattr(strategy.analyzers, 'drawdown'):
                dd_analysis = strategy.analyzers.drawdown.get_analysis()
                results['max_drawdown'] = round(dd_analysis.get('max', {}).get('drawdown', 0), 2)
                results['max_drawdown_period'] = dd_analysis.get('max', {}).get('len', 0)
            
            # Returns Analysis
            if hasattr(strategy.analyzers, 'returns'):
                returns_analysis = strategy.analyzers.returns.get_analysis()
                results['total_return'] = round(returns_analysis.get('rtot', 0) * 100, 2)
                results['annual_return'] = round(returns_analysis.get('rnorm', 0) * 100, 2)
            
            # Trade Analysis
            if hasattr(strategy.analyzers, 'trades'):
                trades_analysis = strategy.analyzers.trades.get_analysis()
                results['total_trades'] = trades_analysis.get('total', {}).get('total', 0)
                results['winning_trades'] = trades_analysis.get('won', {}).get('total', 0)
                results['losing_trades'] = trades_analysis.get('lost', {}).get('total', 0)
                
                if results['total_trades'] > 0:
                    results['win_rate'] = round((results['winning_trades'] / results['total_trades']) * 100, 2)
                    results['avg_win'] = round(trades_analysis.get('won', {}).get('pnl', {}).get('average', 0), 2)
                    results['avg_loss'] = round(trades_analysis.get('lost', {}).get('pnl', {}).get('average', 0), 2)
                    
                    if results['avg_loss'] != 0:
                        results['profit_factor'] = round(abs(results['avg_win'] / results['avg_loss']), 2)
            
            # SQN (System Quality Number)
            if hasattr(strategy.analyzers, 'sqn'):
                sqn_analysis = strategy.analyzers.sqn.get_analysis()
                results['sqn'] = round(sqn_analysis.get('sqn', 0), 3)
            
            # VWR (Variability-Weighted Return)
            if hasattr(strategy.analyzers, 'vwr'):
                vwr_analysis = strategy.analyzers.vwr.get_analysis()
                results['vwr'] = round(vwr_analysis.get('vwr', 0), 3)
                
        except Exception as e:
            print(f"Warning: Error extracting analyzer results: {e}")
        
        return results
    
    def _generate_performance_chart(self, cerebro: bt.Cerebro, initial_cash: float, final_value: float) -> Dict[str, Any]:
        """Generate performance visualization data"""
        
        try:
            # Create a simple performance summary
            chart_data = {
                'initial_value': initial_cash,
                'final_value': final_value,
                'return_pct': ((final_value - initial_cash) / initial_cash) * 100,
                'chart_available': False  # Placeholder for future chart implementation
            }
            
            return chart_data
            
        except Exception as e:
            print(f"Warning: Chart generation failed: {e}")
            return {'chart_available': False, 'error': str(e)}
    
    async def get_historical_data(self, ticker: str, start: str, end: str, interval: str = "1d") -> Dict[str, Any]:
        """Get historical stock data - Statis Fund API compatibility"""
        
        try:
            data = await self._get_data(ticker, start, end)
            
            # Convert to API format
            result = {
                'symbol': ticker,
                'data': data.reset_index().to_dict('records'),
                'interval': interval,
                'start_date': start,
                'end_date': end
            }
            
            return result
            
        except Exception as e:
            raise ValueError(f"Failed to fetch data for {ticker}: {str(e)}")
    
    async def calculate_indicator(self, indicator: str, ticker: str, start: str, end: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate technical indicators - Statis Fund API compatibility"""
        
        try:
            data = await self._get_data(ticker, start, end)
            
            if indicator.lower() == 'rsi':
                period = params.get('period', 14)
                rsi_values = self._calculate_rsi(data['Close'], period)
                return {'indicator': 'RSI', 'values': rsi_values.to_dict()}
            
            elif indicator.lower() == 'macd':
                fast = params.get('fast', 12)
                slow = params.get('slow', 26)
                signal = params.get('signal', 9)
                macd_data = self._calculate_macd(data['Close'], fast, slow, signal)
                return {'indicator': 'MACD', 'values': macd_data}
            
            else:
                raise ValueError(f"Indicator {indicator} not supported")
                
        except Exception as e:
            raise ValueError(f"Indicator calculation failed: {str(e)}")
    
    async def calculate_moving_average(self, ticker: str, days: int, start: str, end: str, interval: str = "1d") -> Dict[str, Any]:
        """Calculate moving average - Statis Fund API compatibility"""
        
        try:
            data = await self._get_data(ticker, start, end)
            ma = data['Close'].rolling(window=days).mean()
            
            return {
                'symbol': ticker,
                'indicator': f'SMA_{days}',
                'values': ma.to_dict(),
                'period': days
            }
            
        except Exception as e:
            raise ValueError(f"Moving average calculation failed: {str(e)}")
    
    async def calculate_bollinger_bands(self, ticker: str, window: int, start: str, end: str, interval: str = "1d") -> Dict[str, Any]:
        """Calculate Bollinger Bands - Statis Fund API compatibility"""
        
        try:
            data = await self._get_data(ticker, start, end)
            
            sma = data['Close'].rolling(window=window).mean()
            std = data['Close'].rolling(window=window).std()
            
            upper_band = sma + (std * 2)
            lower_band = sma - (std * 2)
            
            return {
                'symbol': ticker,
                'indicator': f'BB_{window}',
                'values': {
                    'upper': upper_band.to_dict(),
                    'middle': sma.to_dict(),
                    'lower': lower_band.to_dict()
                },
                'window': window
            }
            
        except Exception as e:
            raise ValueError(f"Bollinger Bands calculation failed: {str(e)}")
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, Any]:
        """Calculate MACD indicator"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line
        
        return {
            'macd': macd.to_dict(),
            'signal': signal_line.to_dict(),
            'histogram': histogram.to_dict()
        }
