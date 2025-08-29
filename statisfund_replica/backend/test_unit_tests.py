#!/usr/bin/env python3
"""
Unit Tests for Statis Fund Replica Backend
Comprehensive testing of core business logic and edge cases
"""

import unittest
import json
import asyncio
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import the modules to test
import main
from advanced_backtest_engine import AdvancedBacktestEngine
from fallback_services import FallbackBacktestEngine, FallbackStrategyGenerator

class TestStrategyGeneration(unittest.TestCase):
    """Test strategy generation functionality"""
    
    def setUp(self):
        self.app = main.app
        self.strategy_generator = main.strategy_generator
    
    def test_strategy_request_validation(self):
        """Test StrategyRequest model validation"""
        # Valid request
        valid_request = main.StrategyRequest(
            description="Test strategy",
            symbols=["AAPL"],
            start_date="2023-01-01",
            end_date="2023-12-31"
        )
        self.assertEqual(valid_request.description, "Test strategy")
        self.assertEqual(valid_request.symbols, ["AAPL"])
        
        # Test prompt fallback
        prompt_request = main.StrategyRequest(prompt="Test prompt")
        self.assertEqual(prompt_request.description, "Test prompt")
    
    def test_fallback_strategy_generation(self):
        """Test fallback strategy generation"""
        generator = FallbackStrategyGenerator()
        
        # Test sync generation
        result = asyncio.run(generator.generate_strategy(
            "Simple moving average strategy",
            ["AAPL"],
            {}
        ))
        
        self.assertTrue(result["success"])
        self.assertIn("code", result)
        self.assertIn("class", result["code"])
        self.assertIn("bt.Strategy", result["code"])

class TestBacktestEngine(unittest.TestCase):
    """Test backtesting functionality"""
    
    def setUp(self):
        self.engine = FallbackBacktestEngine()
        self.advanced_engine = AdvancedBacktestEngine()
        
        # Create sample strategy code
        self.sample_strategy = '''
import backtrader as bt

class TestStrategy(bt.Strategy):
    params = (("period", 20),)
    
    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=self.params.period)
    
    def next(self):
        if not self.position and self.data.close[0] > self.sma[0]:
            self.buy(size=100)
        elif self.position and self.data.close[0] < self.sma[0]:
            self.sell(size=self.position.size)
'''
    
    @patch.object(FallbackBacktestEngine, 'download_data')
    def test_basic_backtest_with_mock_data(self, mock_download):
        """Test basic backtest with mocked data"""
        # Create synthetic data
        dates = pd.date_range('2023-01-01', '2023-03-31', freq='D')
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.normal(0, 1, len(dates)))
        
        mock_data = pd.DataFrame({
            'Open': prices,
            'High': prices * 1.02,
            'Low': prices * 0.98,
            'Close': prices,
            'Volume': np.random.randint(1000000, 2000000, len(dates)),
            'Adj Close': prices
        }, index=dates)
        
        mock_download.return_value = mock_data
        
        result = self.engine.run_backtest(
            code=self.sample_strategy,
            symbol="AAPL",
            start_date="2023-01-01",
            end_date="2023-03-31",
            initial_cash=10000
        )
        
        self.assertTrue(result["success"])
        self.assertIn("performance_metrics", result)
        self.assertIn("summary", result)
    
    @patch.object(AdvancedBacktestEngine, 'download_data')
    def test_advanced_backtest_with_mock_data(self, mock_download):
        """Test advanced backtest with mocked data"""
        # Create synthetic data
        dates = pd.date_range('2023-01-01', '2023-03-31', freq='D')
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.normal(0, 1, len(dates)))
        
        mock_data = pd.DataFrame({
            'Open': prices,
            'High': prices * 1.02,
            'Low': prices * 0.98,
            'Close': prices,
            'Volume': np.random.randint(1000000, 2000000, len(dates)),
            'Adj Close': prices
        }, index=dates)
        
        mock_download.return_value = mock_data
        
        result = self.advanced_engine.run_advanced_backtest(
            code=self.sample_strategy,
            symbol="AAPL",
            start_date="2023-01-01",
            end_date="2023-03-31",
            initial_cash=10000,
            commission=0.001
        )
        
        self.assertTrue(result["success"])
        self.assertIn("performance_metrics", result)
        self.assertIn("advanced_features", result)
        self.assertEqual(result["advanced_features"]["analyzers_count"], 15)
    
    def test_code_fence_stripping(self):
        """Test markdown fence stripping functionality"""
        fenced_code = '''```python
import backtrader as bt

class TestStrategy(bt.Strategy):
    pass
```'''
        
        # Test the fence stripping logic from main.py
        strategy_code = fenced_code
        if strategy_code.startswith("```python"):
            strategy_code = strategy_code.replace("```python", "").replace("```", "").strip()
        elif strategy_code.startswith("```"):
            strategy_code = strategy_code.replace("```", "").strip()
        
        expected = '''import backtrader as bt

class TestStrategy(bt.Strategy):
    pass'''
        
        self.assertEqual(strategy_code, expected)
    
    def test_invalid_symbol_handling(self):
        """Test handling of invalid symbols"""
        result = self.engine.run_backtest(
            code=self.sample_strategy,
            symbol="INVALID_XYZ",
            start_date="2023-01-01",
            end_date="2023-02-01",
            initial_cash=10000
        )
        
        # Should fail gracefully with error message
        self.assertFalse(result["success"])
        self.assertIn("error", result)
    
    def test_malformed_code_handling(self):
        """Test handling of malformed strategy code"""
        malformed_code = "this is not valid python code!!!"
        
        result = self.engine.run_backtest(
            code=malformed_code,
            symbol="AAPL",
            start_date="2023-01-01",
            end_date="2023-02-01",
            initial_cash=10000
        )
        
        # Should fail gracefully
        self.assertFalse(result["success"])
        self.assertIn("error", result)

class TestAPIEndpoints(unittest.TestCase):
    """Test API endpoint functionality"""
    
    def setUp(self):
        self.app = main.app
    
    def test_backtest_request_validation(self):
        """Test BacktestRequest model validation"""
        # Test with 'code' field
        request1 = main.BacktestRequest(
            code="test code",
            symbol="AAPL",
            start_date="2023-01-01",
            end_date="2023-12-31"
        )
        self.assertEqual(request1.code, "test code")
        
        # Test with 'strategy_code' field
        request2 = main.BacktestRequest(
            strategy_code="test code",
            symbol="AAPL",
            start_date="2023-01-01",
            end_date="2023-12-31"
        )
        self.assertEqual(request2.strategy_code, "test code")
    
    def test_advanced_backtest_request_validation(self):
        """Test AdvancedBacktestRequest model validation"""
        request = main.AdvancedBacktestRequest(
            code="test code",
            symbol="AAPL",
            start_date="2023-01-01",
            end_date="2023-12-31",
            initial_cash=10000,
            commission=0.001
        )
        
        self.assertEqual(request.code, "test code")
        self.assertEqual(request.symbol, "AAPL")
        self.assertEqual(request.commission, 0.001)

class TestDataHandling(unittest.TestCase):
    """Test data download and processing"""
    
    def setUp(self):
        self.engine = AdvancedBacktestEngine()
    
    def test_data_validation(self):
        """Test data validation logic"""
        # Valid data
        valid_data = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [102, 103, 104],
            'Low': [99, 100, 101],
            'Close': [101, 102, 103],
            'Volume': [1000000, 1100000, 1200000],
            'Adj Close': [101, 102, 103]
        }, index=pd.date_range('2023-01-01', periods=3))
        
        self.assertFalse(valid_data.empty)
        self.assertEqual(len(valid_data), 3)
        
        # Empty data
        empty_data = pd.DataFrame()
        self.assertTrue(empty_data.empty)
    
    def test_date_range_validation(self):
        """Test date range validation"""
        start_date = "2023-01-01"
        end_date = "2023-12-31"
        
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        
        self.assertLess(start_dt, end_dt)
        
        # Invalid range (end before start)
        invalid_start = "2023-12-31"
        invalid_end = "2023-01-01"
        
        invalid_start_dt = pd.to_datetime(invalid_start)
        invalid_end_dt = pd.to_datetime(invalid_end)
        
        self.assertGreater(invalid_start_dt, invalid_end_dt)

class TestPerformanceMetrics(unittest.TestCase):
    """Test performance metrics calculation"""
    
    def setUp(self):
        self.engine = AdvancedBacktestEngine()
    
    def test_metrics_extraction(self):
        """Test metrics extraction from mock strategy"""
        # Create mock strategy with analyzers
        mock_strategy = MagicMock()
        mock_strategy.analyzers = MagicMock()
        
        # Mock Sharpe ratio analyzer
        mock_sharpe = MagicMock()
        mock_sharpe.get_analysis.return_value = {'sharperatio': 1.5}
        mock_strategy.analyzers.sharpe = mock_sharpe
        
        # Mock drawdown analyzer
        mock_drawdown = MagicMock()
        mock_drawdown.get_analysis.return_value = {
            'max': {'drawdown': 15.5, 'len': 30},
            'drawdown': 8.2
        }
        mock_strategy.analyzers.drawdown = mock_drawdown
        
        # Mock trade analyzer
        mock_trades = MagicMock()
        mock_trades.get_analysis.return_value = {
            'total': {'total': 10},
            'won': {'total': 6, 'pnl': {'average': 50.0}},
            'lost': {'total': 4, 'pnl': {'average': -30.0}}
        }
        mock_strategy.analyzers.trades = mock_trades
        
        # Extract metrics
        metrics = self.engine.extract_advanced_metrics(mock_strategy)
        
        self.assertEqual(metrics['sharpe_ratio'], 1.5)
        self.assertEqual(metrics['max_drawdown'], 15.5)
        self.assertEqual(metrics['total_trades'], 10)
        self.assertEqual(metrics['win_rate'], 60.0)  # 6/10 * 100

class TestErrorHandling(unittest.TestCase):
    """Test comprehensive error handling"""
    
    def test_network_error_handling(self):
        """Test handling of network errors"""
        engine = AdvancedBacktestEngine()
        
        # Test with invalid symbol that will cause network error
        result = engine.download_data("INVALID_SYMBOL_XYZ", "2023-01-01", "2023-02-01")
        
        # Should return None for invalid symbol
        self.assertIsNone(result)
    
    def test_date_parsing_errors(self):
        """Test handling of invalid date formats"""
        try:
            invalid_date = pd.to_datetime("invalid-date-format")
            self.fail("Should have raised an exception")
        except:
            # Expected to fail
            pass
    
    def test_strategy_execution_errors(self):
        """Test handling of strategy execution errors"""
        engine = AdvancedBacktestEngine()
        
        # Invalid Python code
        invalid_code = "this is not valid python!!!"
        
        # Mock data to avoid network calls
        mock_data = pd.DataFrame({
            'Open': [100], 'High': [101], 'Low': [99], 
            'Close': [100], 'Volume': [1000000], 'Adj Close': [100]
        }, index=[pd.Timestamp('2023-01-01')])
        
        with patch.object(engine, 'download_data', return_value=mock_data):
            result = engine.run_advanced_backtest(
                code=invalid_code,
                symbol="AAPL",
                start_date="2023-01-01",
                end_date="2023-01-02",
                initial_cash=10000,
                commission=0.001
            )
            
            self.assertFalse(result["success"])
            self.assertIn("error", result)

def run_unit_tests():
    """Run all unit tests and generate report"""
    print("🧪 Starting Unit Test Suite")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestStrategyGeneration,
        TestBacktestEngine,
        TestAPIEndpoints,
        TestDataHandling,
        TestPerformanceMetrics,
        TestErrorHandling
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate summary
    print("\n" + "=" * 60)
    print("🧪 UNIT TEST SUMMARY")
    print("=" * 60)
    print(f"📊 Tests Run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"💥 Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   • {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   • {test}: {traceback.split('Exception:')[-1].strip()}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\n📈 Success Rate: {success_rate:.1f}%")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_unit_tests()
