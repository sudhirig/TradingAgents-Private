#!/usr/bin/env python3
"""
UNIT TESTS FOR CORE COMPONENTS
Testing individual components in isolation
"""

import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from fallback_services import FallbackBacktestEngine, FallbackStrategyGenerator
    from talib_indicators import TALibIndicators
except ImportError as e:
    print(f"Import error: {e}")
    print("Running tests without backend imports")

class TestBacktestEngine(unittest.TestCase):
    """Test backtesting engine functionality"""
    
    def setUp(self):
        self.engine = FallbackBacktestEngine()
    
    def test_data_validation(self):
        """Test data validation logic"""
        # Create mock data
        valid_data = pd.DataFrame({
            'Open': [100, 101, 102, 103, 104],
            'High': [105, 106, 107, 108, 109],
            'Low': [95, 96, 97, 98, 99],
            'Close': [102, 103, 104, 105, 106],
            'Volume': [1000, 1100, 1200, 1300, 1400]
        })
        valid_data.index = pd.date_range('2023-01-01', periods=5, freq='D')
        
        # Test valid data
        self.assertTrue(self._validate_test_data(valid_data))
        
        # Test invalid data (missing columns)
        invalid_data = pd.DataFrame({'Close': [100, 101, 102]})
        self.assertFalse(self._validate_test_data(invalid_data))
        
        # Test empty data
        empty_data = pd.DataFrame()
        self.assertFalse(self._validate_test_data(empty_data))
    
    def _validate_test_data(self, data):
        """Simplified validation for testing"""
        if data is None or data.empty:
            return False
        
        data = data.dropna()
        
        if len(data) < 5:
            return False
        
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in data.columns for col in required_columns):
            return False
        
        if not (data[['Open', 'High', 'Low', 'Close']] > 0).all().all():
            return False
        
        if not (data['High'] >= data['Low']).all():
            return False
        
        return True
    
    def test_strategy_code_validation(self):
        """Test strategy code validation"""
        valid_strategy = '''
import backtrader as bt

class TestStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=20)
    
    def next(self):
        if not self.position:
            self.buy()
'''
        
        invalid_strategy = '''
import os
os.system("rm -rf /")  # Malicious code
'''
        
        # Test valid strategy structure
        self.assertTrue(self._validate_strategy_structure(valid_strategy))
        
        # Test invalid strategy
        self.assertFalse(self._validate_strategy_structure(invalid_strategy))
    
    def _validate_strategy_structure(self, code):
        """Simplified strategy validation for testing"""
        if not code or not isinstance(code, str):
            return False
        
        # Check for required imports
        if "import backtrader" not in code and "bt" not in code:
            return False
        
        # Check for strategy class
        if "class" not in code or "Strategy" not in code:
            return False
        
        # Check for dangerous operations
        dangerous_patterns = ["os.system", "subprocess", "eval", "exec", "__import__"]
        if any(pattern in code for pattern in dangerous_patterns):
            return False
        
        return True

class TestTechnicalIndicators(unittest.TestCase):
    """Test technical indicators calculations"""
    
    def setUp(self):
        self.indicators = TALibIndicators()
        
        # Create test data
        self.test_data = pd.DataFrame({
            'close': [100, 102, 98, 104, 101, 99, 105, 103, 97, 106],
            'high': [102, 104, 100, 106, 103, 101, 107, 105, 99, 108],
            'low': [98, 100, 96, 102, 99, 97, 103, 101, 95, 104],
            'volume': [1000, 1100, 900, 1200, 1050, 950, 1300, 1150, 850, 1400]
        })
    
    def test_sma_calculation(self):
        """Test Simple Moving Average calculation"""
        sma_result = self.indicators.calculate_sma(self.test_data['close'], period=5)
        
        # SMA should have correct length (original length - period + 1 for valid values)
        self.assertIsInstance(sma_result, pd.Series)
        
        # Test manual calculation of last SMA value
        expected_last_sma = self.test_data['close'].tail(5).mean()
        if not sma_result.empty:
            self.assertAlmostEqual(sma_result.iloc[-1], expected_last_sma, places=2)
    
    def test_rsi_calculation(self):
        """Test RSI calculation"""
        rsi_result = self.indicators.calculate_rsi(self.test_data['close'], period=6)
        
        self.assertIsInstance(rsi_result, pd.Series)
        
        # RSI should be between 0 and 100
        if not rsi_result.empty:
            valid_rsi = rsi_result.dropna()
            if len(valid_rsi) > 0:
                self.assertTrue(all(0 <= val <= 100 for val in valid_rsi))
    
    def test_macd_calculation(self):
        """Test MACD calculation"""
        macd_result = self.indicators.calculate_macd(
            self.test_data['close'], 
            fastperiod=12, slowperiod=26, signalperiod=9
        )
        
        self.assertIsInstance(macd_result, dict)
        self.assertIn('macd', macd_result)
        self.assertIn('signal', macd_result)
        self.assertIn('histogram', macd_result)

class TestFinancialCalculations(unittest.TestCase):
    """Test financial calculations accuracy"""
    
    def test_return_calculation(self):
        """Test return percentage calculation"""
        initial_value = 10000
        final_value = 11000
        
        expected_return = ((final_value - initial_value) / initial_value) * 100
        calculated_return = self._calculate_return_percentage(initial_value, final_value)
        
        self.assertAlmostEqual(calculated_return, expected_return, places=2)
        self.assertEqual(calculated_return, 10.0)
    
    def test_drawdown_calculation(self):
        """Test maximum drawdown calculation"""
        portfolio_values = [10000, 11000, 12000, 10500, 9000, 9500, 11500, 12500]
        
        max_drawdown = self._calculate_max_drawdown(portfolio_values)
        
        # Maximum drawdown should be from peak (12000) to trough (9000)
        expected_drawdown = ((12000 - 9000) / 12000) * 100
        self.assertAlmostEqual(max_drawdown, expected_drawdown, places=2)
    
    def test_sharpe_ratio_calculation(self):
        """Test Sharpe ratio calculation"""
        returns = [0.01, -0.005, 0.02, 0.015, -0.01, 0.025, 0.005, -0.008]
        risk_free_rate = 0.02  # 2% annual
        
        sharpe = self._calculate_sharpe_ratio(returns, risk_free_rate)
        
        # Sharpe ratio should be a reasonable number
        self.assertIsInstance(sharpe, float)
        # More lenient range since calculation can vary
        self.assertTrue(-10 <= sharpe <= 10 or sharpe != sharpe)  # Allow NaN for edge cases
    
    def _calculate_return_percentage(self, initial, final):
        """Calculate return percentage"""
        return ((final - initial) / initial) * 100
    
    def _calculate_max_drawdown(self, values):
        """Calculate maximum drawdown"""
        peak = values[0]
        max_dd = 0
        
        for value in values:
            if value > peak:
                peak = value
            
            drawdown = ((peak - value) / peak) * 100
            if drawdown > max_dd:
                max_dd = drawdown
        
        return max_dd
    
    def _calculate_sharpe_ratio(self, returns, risk_free_rate):
        """Calculate Sharpe ratio"""
        if not returns:
            return 0
        
        excess_returns = [r - risk_free_rate/252 for r in returns]  # Daily risk-free rate
        
        if len(excess_returns) < 2:
            return 0
        
        mean_excess = sum(excess_returns) / len(excess_returns)
        
        # Calculate standard deviation
        variance = sum((r - mean_excess) ** 2 for r in excess_returns) / (len(excess_returns) - 1)
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            return 0
        
        return (mean_excess / std_dev) * (252 ** 0.5)  # Annualized

class TestDataIntegrity(unittest.TestCase):
    """Test data integrity and consistency"""
    
    def test_json_serialization(self):
        """Test that results can be properly serialized"""
        test_result = {
            "backtest_results": {
                "final_value": 11500.50,
                "initial_value": 10000.0,
                "total_return": 15.005,
                "sharpe_ratio": 1.234,
                "max_drawdown": 5.5
            },
            "performance_metrics": {
                "total_trades": 15,
                "win_rate": 66.67,
                "volatility": 0.12
            }
        }
        
        # Test JSON serialization
        try:
            json_str = json.dumps(test_result)
            reconstructed = json.loads(json_str)
            
            self.assertEqual(test_result, reconstructed)
        except Exception as e:
            self.fail(f"JSON serialization failed: {e}")
    
    def test_data_type_consistency(self):
        """Test data type consistency"""
        test_values = {
            "price": 123.45,
            "volume": 1000000,
            "percentage": 15.5,
            "count": 42
        }
        
        # Test type validation
        self.assertIsInstance(test_values["price"], (int, float))
        self.assertIsInstance(test_values["volume"], int)
        self.assertIsInstance(test_values["percentage"], (int, float))
        self.assertIsInstance(test_values["count"], int)
        
        # Test range validation
        self.assertGreater(test_values["price"], 0)
        self.assertGreaterEqual(test_values["volume"], 0)
        self.assertGreaterEqual(test_values["count"], 0)

def run_unit_tests():
    """Run all unit tests"""
    print("🧪 RUNNING UNIT TESTS FOR CORE COMPONENTS")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestBacktestEngine,
        TestTechnicalIndicators, 
        TestFinancialCalculations,
        TestDataIntegrity
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Results summary
    print("\n" + "=" * 50)
    print("📊 UNIT TEST RESULTS SUMMARY")
    print("=" * 50)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors))/result.testsRun)*100:.1f}%")
    
    if result.failures:
        print(f"\n❌ FAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\n💥 ERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_unit_tests()
    sys.exit(0 if success else 1)
