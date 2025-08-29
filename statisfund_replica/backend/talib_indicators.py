"""
TA-Lib Integration for 122+ Technical Indicators
Phase 2.1 Implementation - Professional Technical Analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List, Union
import warnings

# Try to import TA-Lib, fallback to mock if not available
try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    print("⚠️ TA-Lib not available. Using fallback implementations for basic indicators.")
    TALIB_AVAILABLE = False
    
    # Mock TA-Lib module for basic functionality
    class MockTALib:
        @staticmethod
        def SMA(data, timeperiod=20):
            return pd.Series(data).rolling(window=timeperiod).mean().values
        
        @staticmethod
        def EMA(data, timeperiod=20):
            return pd.Series(data).ewm(span=timeperiod).mean().values
        
        @staticmethod
        def RSI(data, timeperiod=14):
            delta = pd.Series(data).diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=timeperiod).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=timeperiod).mean()
            rs = gain / loss
            return (100 - (100 / (1 + rs))).values
        
        @staticmethod
        def MACD(data, fastperiod=12, slowperiod=26, signalperiod=9):
            exp1 = pd.Series(data).ewm(span=fastperiod).mean()
            exp2 = pd.Series(data).ewm(span=slowperiod).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=signalperiod).mean()
            histogram = macd - signal
            return macd.values, signal.values, histogram.values
    
    talib = MockTALib()

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore', category=RuntimeWarning)


class TALibIndicators:
    """Professional technical analysis with 122+ TA-Lib indicators"""
    
    # Indicator categories for organization
    OVERLAP_STUDIES = [
        'BBANDS', 'DEMA', 'EMA', 'HT_TRENDLINE', 'KAMA', 'MA', 'MAMA', 'MAVP',
        'MIDPOINT', 'MIDPRICE', 'SAR', 'SAREXT', 'SMA', 'T3', 'TEMA', 'TRIMA', 'WMA'
    ]
    
    MOMENTUM_INDICATORS = [
        'ADX', 'ADXR', 'APO', 'AROON', 'AROONOSC', 'BOP', 'CCI', 'CMO', 'DX',
        'MACD', 'MACDEXT', 'MACDFIX', 'MFI', 'MINUS_DI', 'MINUS_DM', 'MOM',
        'PLUS_DI', 'PLUS_DM', 'PPO', 'ROC', 'ROCP', 'ROCR', 'ROCR100', 'RSI',
        'STOCH', 'STOCHF', 'STOCHRSI', 'TRIX', 'ULTOSC', 'WILLR'
    ]
    
    VOLUME_INDICATORS = [
        'AD', 'ADOSC', 'OBV'
    ]
    
    VOLATILITY_INDICATORS = [
        'ATR', 'NATR', 'TRANGE'
    ]
    
    PRICE_TRANSFORM = [
        'AVGPRICE', 'MEDPRICE', 'TYPPRICE', 'WCLPRICE'
    ]
    
    CYCLE_INDICATORS = [
        'HT_DCPERIOD', 'HT_DCPHASE', 'HT_PHASOR', 'HT_SINE', 'HT_TRENDMODE'
    ]
    
    PATTERN_RECOGNITION = [
        'CDL2CROWS', 'CDL3BLACKCROWS', 'CDL3INSIDE', 'CDL3LINESTRIKE', 'CDL3OUTSIDE',
        'CDL3STARSINSOUTH', 'CDL3WHITESOLDIERS', 'CDLABANDONEDBABY', 'CDLADVANCEBLOCK',
        'CDLBELTHOLD', 'CDLBREAKAWAY', 'CDLCLOSINGMARUBOZU', 'CDLCONCEALBABYSWALL',
        'CDLCOUNTERATTACK', 'CDLDARKCLOUDCOVER', 'CDLDOJI', 'CDLDOJISTAR',
        'CDLDRAGONFLYDOJI', 'CDLENGULFING', 'CDLEVENINGDOJISTAR', 'CDLEVENINGSTAR',
        'CDLGAPSIDESIDEWHITE', 'CDLGRAVESTONEDOJI', 'CDLHAMMER', 'CDLHANGINGMAN',
        'CDLHARAMI', 'CDLHARAMICROSS', 'CDLHIGHWAVE', 'CDLHIKKAKE', 'CDLHIKKAKEMOD',
        'CDLHOMINGPIGEON', 'CDLIDENTICAL3CROWS', 'CDLINNECK', 'CDLINVERTEDHAMMER',
        'CDLKICKING', 'CDLKICKINGBYLENGTH', 'CDLLADDERBOTTOM', 'CDLLONGLEGGEDDOJI',
        'CDLLONGLINE', 'CDLMARUBOZU', 'CDLMATCHINGLOW', 'CDLMATHOLD', 'CDLMORNINGDOJISTAR',
        'CDLMORNINGSTAR', 'CDLONNECK', 'CDLPIERCING', 'CDLRICKSHAWMAN', 'CDLRISEFALL3METHODS',
        'CDLSEPARATINGLINES', 'CDLSHOOTINGSTAR', 'CDLSHORTLINE', 'CDLSPINNINGTOP',
        'CDLSTALLEDPATTERN', 'CDLSTICKSANDWICH', 'CDLTAKURI', 'CDLTASUKIGAP',
        'CDLTHRUSTING', 'CDLTRISTAR', 'CDLUNIQUE3RIVER', 'CDLUPSIDEGAP2CROWS',
        'CDLXSIDEGAP3METHODS'
    ]
    
    STATISTIC_FUNCTIONS = [
        'BETA', 'CORREL', 'LINEARREG', 'LINEARREG_ANGLE', 'LINEARREG_INTERCEPT',
        'LINEARREG_SLOPE', 'STDDEV', 'TSF', 'VAR'
    ]
    
    MATH_TRANSFORM = [
        'ACOS', 'ASIN', 'ATAN', 'CEIL', 'COS', 'COSH', 'EXP', 'FLOOR', 'LN',
        'LOG10', 'SIN', 'SINH', 'SQRT', 'TAN', 'TANH'
    ]
    
    MATH_OPERATORS = [
        'ADD', 'DIV', 'MAX', 'MAXINDEX', 'MIN', 'MININDEX', 'MINMAX', 'MINMAXINDEX',
        'MULT', 'SUB', 'SUM'
    ]
    
    def __init__(self):
        self.available_indicators = self._get_all_indicators()
        
    def _get_all_indicators(self) -> List[str]:
        """Get list of all available indicators"""
        return (self.OVERLAP_STUDIES + self.MOMENTUM_INDICATORS + self.VOLUME_INDICATORS +
                self.VOLATILITY_INDICATORS + self.PRICE_TRANSFORM + self.CYCLE_INDICATORS +
                self.PATTERN_RECOGNITION + self.STATISTIC_FUNCTIONS + self.MATH_TRANSFORM +
                self.MATH_OPERATORS)
    
    def calculate_indicator(self, data: pd.DataFrame, indicator: str, 
                          **params) -> Union[pd.Series, pd.DataFrame, Dict]:
        """Calculate any TA-Lib indicator with parameters"""
        try:
            # Ensure we have the required price data
            if not all(col in data.columns for col in ['Open', 'High', 'Low', 'Close']):
                raise ValueError("Data must contain Open, High, Low, Close columns")
            
            # Convert to numpy arrays for TA-Lib
            open_prices = data['Open'].values.astype(np.float64)
            high_prices = data['High'].values.astype(np.float64)
            low_prices = data['Low'].values.astype(np.float64)
            close_prices = data['Close'].values.astype(np.float64)
            volume = data['Volume'].values.astype(np.float64) if 'Volume' in data.columns else None
            
            # Handle basic indicators with fallback implementations
            if not TALIB_AVAILABLE:
                return self._calculate_fallback_indicator(data, indicator, **params)
            
            # Get the TA-Lib function
            talib_func = getattr(talib, indicator.upper())
            
            # Calculate indicator based on type
            if indicator.upper() in self.OVERLAP_STUDIES:
                result = self._calculate_overlap_study(talib_func, open_prices, high_prices, 
                                                     low_prices, close_prices, **params)
            elif indicator.upper() in self.MOMENTUM_INDICATORS:
                result = self._calculate_momentum_indicator(talib_func, open_prices, high_prices,
                                                          low_prices, close_prices, volume, **params)
            elif indicator.upper() in self.VOLUME_INDICATORS:
                if volume is None:
                    raise ValueError(f"Volume data required for {indicator}")
                result = self._calculate_volume_indicator(talib_func, high_prices, low_prices,
                                                        close_prices, volume, **params)
            elif indicator.upper() in self.VOLATILITY_INDICATORS:
                result = self._calculate_volatility_indicator(talib_func, high_prices, low_prices,
                                                            close_prices, **params)
            elif indicator.upper() in self.PATTERN_RECOGNITION:
                result = self._calculate_pattern_recognition(talib_func, open_prices, high_prices,
                                                           low_prices, close_prices, **params)
            else:
                # Generic calculation
                result = talib_func(close_prices, **params)
            
            # Convert result to pandas format with proper index
            if isinstance(result, tuple):
                # Multiple outputs (like MACD, Bollinger Bands)
                return {f"{indicator}_{i}": pd.Series(arr, index=data.index) 
                       for i, arr in enumerate(result)}
            else:
                # Single output
                return pd.Series(result, index=data.index, name=indicator)
                
        except Exception as e:
            print(f"Error calculating {indicator}: {e}")
            # Return empty series with same index as input data
            if hasattr(data, 'index'):
                return pd.Series(index=data.index, name=str(indicator))
            else:
                return pd.Series(name=str(indicator))
    
    def _calculate_fallback_indicator(self, data: pd.DataFrame, indicator: str, **params):
        """Fallback implementations for basic indicators when TA-Lib is not available"""
        close_prices = data['Close'].values
        
        if indicator.upper() == 'SMA':
            timeperiod = params.get('timeperiod', 20)
            # Simple Moving Average fallback
            result = pd.Series(close_prices).rolling(window=timeperiod).mean().values
        elif indicator.upper() == 'EMA':
            timeperiod = params.get('timeperiod', 20)
            # Exponential Moving Average fallback
            result = pd.Series(close_prices).ewm(span=timeperiod).mean().values
        elif indicator.upper() == 'RSI':
            timeperiod = params.get('timeperiod', 14)
            # RSI fallback calculation
            delta = pd.Series(close_prices).diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=timeperiod).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=timeperiod).mean()
            rs = gain / loss
            result = (100 - (100 / (1 + rs))).values
        elif indicator.upper() == 'MACD':
            fastperiod = params.get('fastperiod', 12)
            slowperiod = params.get('slowperiod', 26)
            signalperiod = params.get('signalperiod', 9)
            # MACD fallback calculation
            ema_fast = pd.Series(close_prices).ewm(span=fastperiod).mean()
            ema_slow = pd.Series(close_prices).ewm(span=slowperiod).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signalperiod).mean()
            histogram = macd_line - signal_line
            result = (macd_line.values, signal_line.values, histogram.values)
            return {
                f"{indicator}_0": pd.Series(macd_line.values, index=data.index),
                f"{indicator}_1": pd.Series(signal_line.values, index=data.index),
                f"{indicator}_2": pd.Series(histogram.values, index=data.index)
            }
        else:
            # Return empty series for unsupported indicators
            result = np.full(len(close_prices), np.nan)
        
        return pd.Series(result, index=data.index, name=indicator)
    
    def _calculate_overlap_study(self, func, open_p, high_p, low_p, close_p, **params):
        """Calculate overlap studies (moving averages, etc.)"""
        if func.__name__ in ['BBANDS']:
            return func(close_p, **params)
        elif func.__name__ in ['SAR', 'SAREXT']:
            return func(high_p, low_p, **params)
        elif func.__name__ in ['MIDPOINT']:
            return func(close_p, **params)
        elif func.__name__ in ['MIDPRICE']:
            return func(high_p, low_p, **params)
        else:
            return func(close_p, **params)
    
    def _calculate_momentum_indicator(self, func, open_p, high_p, low_p, close_p, volume, **params):
        """Calculate momentum indicators"""
        if func.__name__ in ['MACD', 'MACDEXT', 'MACDFIX']:
            return func(close_p, **params)
        elif func.__name__ in ['STOCH', 'STOCHF']:
            return func(high_p, low_p, close_p, **params)
        elif func.__name__ in ['STOCHRSI']:
            return func(close_p, **params)
        elif func.__name__ in ['AROON', 'AROONOSC']:
            return func(high_p, low_p, **params)
        elif func.__name__ == 'MFI' and volume is not None:
            return func(high_p, low_p, close_p, volume, **params)
        elif func.__name__ in ['ADX', 'ADXR', 'DX', 'MINUS_DI', 'MINUS_DM', 'PLUS_DI', 'PLUS_DM']:
            return func(high_p, low_p, close_p, **params)
        else:
            return func(close_p, **params)
    
    def _calculate_volume_indicator(self, func, high_p, low_p, close_p, volume, **params):
        """Calculate volume indicators"""
        if func.__name__ == 'AD':
            return func(high_p, low_p, close_p, volume)
        elif func.__name__ == 'ADOSC':
            return func(high_p, low_p, close_p, volume, **params)
        elif func.__name__ == 'OBV':
            return func(close_p, volume)
        else:
            return func(close_p, volume, **params)
    
    def _calculate_volatility_indicator(self, func, high_p, low_p, close_p, **params):
        """Calculate volatility indicators"""
        return func(high_p, low_p, close_p, **params)
    
    def _calculate_pattern_recognition(self, func, open_p, high_p, low_p, close_p, **params):
        """Calculate candlestick pattern recognition"""
        return func(open_p, high_p, low_p, close_p)
    
    def get_indicator_info(self, indicator: str) -> Dict[str, Any]:
        """Get information about a specific indicator"""
        try:
            func = getattr(talib, indicator.upper())
            info = func.info
            
            return {
                'name': info['name'],
                'group': info['group'],
                'display_name': info['display_name'],
                'flags': info.get('flags', []),
                'input_names': info.get('input_names', []),
                'output_names': info.get('output_names', []),
                'parameters': info.get('parameters', {}),
                'category': self._get_indicator_category(indicator.upper())
            }
        except:
            return {'error': f'Indicator {indicator} not found'}
    
    def _get_indicator_category(self, indicator: str) -> str:
        """Get the category of an indicator"""
        if indicator in self.OVERLAP_STUDIES:
            return 'Overlap Studies'
        elif indicator in self.MOMENTUM_INDICATORS:
            return 'Momentum Indicators'
        elif indicator in self.VOLUME_INDICATORS:
            return 'Volume Indicators'
        elif indicator in self.VOLATILITY_INDICATORS:
            return 'Volatility Indicators'
        elif indicator in self.PATTERN_RECOGNITION:
            return 'Pattern Recognition'
        elif indicator in self.CYCLE_INDICATORS:
            return 'Cycle Indicators'
        elif indicator in self.PRICE_TRANSFORM:
            return 'Price Transform'
        elif indicator in self.STATISTIC_FUNCTIONS:
            return 'Statistic Functions'
        elif indicator in self.MATH_TRANSFORM:
            return 'Math Transform'
        elif indicator in self.MATH_OPERATORS:
            return 'Math Operators'
        else:
            return 'Other'
    
    def calculate_multiple_indicators(self, data: pd.DataFrame, 
                                    indicators: List[Dict[str, Any]]) -> pd.DataFrame:
        """Calculate multiple indicators at once"""
        result_df = data.copy()
        
        for indicator_config in indicators:
            name = indicator_config['name']
            params = indicator_config.get('params', {})
            
            try:
                indicator_result = self.calculate_indicator(data, name, **params)
                
                if isinstance(indicator_result, dict):
                    # Multiple outputs
                    for key, series in indicator_result.items():
                        result_df[key] = series
                else:
                    # Single output
                    result_df[f"{name}_{list(params.values())[0] if params else 'default'}"] = indicator_result
                    
            except Exception as e:
                print(f"Failed to calculate {name}: {e}")
        
        return result_df
    
    def get_popular_indicators(self) -> Dict[str, List[Dict]]:
        """Get configuration for popular indicators"""
        return {
            'trend': [
                {'name': 'SMA', 'params': {'timeperiod': 20}},
                {'name': 'EMA', 'params': {'timeperiod': 20}},
                {'name': 'BBANDS', 'params': {'timeperiod': 20, 'nbdevup': 2, 'nbdevdn': 2}},
                {'name': 'SAR', 'params': {'acceleration': 0.02, 'maximum': 0.2}},
            ],
            'momentum': [
                {'name': 'RSI', 'params': {'timeperiod': 14}},
                {'name': 'MACD', 'params': {'fastperiod': 12, 'slowperiod': 26, 'signalperiod': 9}},
                {'name': 'STOCH', 'params': {'fastk_period': 14, 'slowk_period': 3, 'slowd_period': 3}},
                {'name': 'CCI', 'params': {'timeperiod': 14}},
                {'name': 'WILLR', 'params': {'timeperiod': 14}},
            ],
            'volatility': [
                {'name': 'ATR', 'params': {'timeperiod': 14}},
                {'name': 'NATR', 'params': {'timeperiod': 14}},
            ],
            'volume': [
                {'name': 'OBV', 'params': {}},
                {'name': 'AD', 'params': {}},
                {'name': 'MFI', 'params': {'timeperiod': 14}},
            ]
        }
    
    def create_indicator_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Create a comprehensive indicator summary"""
        popular = self.get_popular_indicators()
        all_indicators = []
        
        for category, indicators in popular.items():
            all_indicators.extend(indicators)
        
        # Calculate all popular indicators
        result_data = self.calculate_multiple_indicators(data, all_indicators)
        
        # Get latest values
        latest = result_data.iloc[-1]
        
        summary = {
            'trend_analysis': {
                'sma_20': latest.get('SMA_20', 0),
                'ema_20': latest.get('EMA_20', 0),
                'price_vs_sma': 'Above' if latest['Close'] > latest.get('SMA_20', 0) else 'Below',
                'price_vs_ema': 'Above' if latest['Close'] > latest.get('EMA_20', 0) else 'Below',
            },
            'momentum_analysis': {
                'rsi_14': latest.get('RSI_14', 50),
                'rsi_signal': self._get_rsi_signal(latest.get('RSI_14', 50)),
                'cci_14': latest.get('CCI_14', 0),
                'willr_14': latest.get('WILLR_14', -50),
            },
            'volatility_analysis': {
                'atr_14': latest.get('ATR_14', 0),
                'natr_14': latest.get('NATR_14', 0),
            },
            'volume_analysis': {
                'obv': latest.get('OBV_default', 0),
                'mfi_14': latest.get('MFI_14', 50),
            },
            'overall_signal': self._get_overall_signal(latest),
            'total_indicators': len(self.available_indicators)
        }
        
        return summary
    
    def _get_rsi_signal(self, rsi: float) -> str:
        """Get RSI signal interpretation"""
        if rsi > 70:
            return 'Overbought'
        elif rsi < 30:
            return 'Oversold'
        else:
            return 'Neutral'
    
    def _get_overall_signal(self, latest_data: pd.Series) -> str:
        """Get overall market signal based on multiple indicators"""
        signals = []
        
        # Trend signals
        if latest_data['Close'] > latest_data.get('SMA_20', 0):
            signals.append(1)
        else:
            signals.append(-1)
        
        # Momentum signals
        rsi = latest_data.get('RSI_14', 50)
        if rsi > 50:
            signals.append(1)
        else:
            signals.append(-1)
        
        # Overall signal
        avg_signal = sum(signals) / len(signals)
        
        if avg_signal > 0.3:
            return 'Bullish'
        elif avg_signal < -0.3:
            return 'Bearish'
        else:
            return 'Neutral'
    
    # Convenience methods for unit testing compatibility
    def calculate_sma(self, data, period=20):
        """Calculate Simple Moving Average"""
        if isinstance(data, pd.Series):
            return data.rolling(window=period).mean()
        else:
            return pd.Series(data).rolling(window=period).mean()
    
    def calculate_rsi(self, data, period=14):
        """Calculate RSI"""
        if isinstance(data, pd.Series):
            delta = data.diff()
        else:
            delta = pd.Series(data).diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def calculate_macd(self, data, fastperiod=12, slowperiod=26, signalperiod=9):
        """Calculate MACD"""
        if isinstance(data, pd.Series):
            prices = data
        else:
            prices = pd.Series(data)
        
        ema_fast = prices.ewm(span=fastperiod).mean()
        ema_slow = prices.ewm(span=slowperiod).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signalperiod).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
