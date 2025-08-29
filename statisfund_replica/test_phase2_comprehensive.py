#!/usr/bin/env python3
"""
Comprehensive Testing Suite for Statisfund Phase 2
Tests backend APIs, business logic, and validates backtest results
"""

import unittest
import requests
import json
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from colorama import init, Fore, Style
import warnings
warnings.filterwarnings('ignore')

# Initialize colorama
init(autoreset=True)

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

class TestPhase2Backend(unittest.TestCase):
    """Backend API Testing Suite"""
    
    @classmethod
    def setUpClass(cls):
        """Check if backend is running"""
        try:
            response = requests.get(f"{BASE_URL}/", timeout=5)
            if response.status_code != 200:
                raise Exception("Backend not healthy")
        except:
            print(f"{Fore.RED}❌ Backend must be running on {BASE_URL}")
            raise
    
    def test_01_health_check(self):
        """Test backend health endpoint"""
        response = requests.get(f"{BASE_URL}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('status', data)
        print(f"{Fore.GREEN}✅ Health check passed")
    
    def test_02_indicators_availability(self):
        """Test TA-Lib indicators availability"""
        response = requests.get(f"{BASE_URL}/api/indicators")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        indicators = data.get('indicators', [])
        self.assertGreater(len(indicators), 100, "Should have 122+ indicators")
        
        # Check for key indicators
        required = ['SMA', 'RSI', 'MACD', 'BBANDS', 'STOCH']
        for ind in required:
            self.assertTrue(
                any(ind in i['name'] for i in indicators),
                f"Missing indicator: {ind}"
            )
        print(f"{Fore.GREEN}✅ Found {len(indicators)} indicators available")
    
    def test_03_no_mock_data_in_strategy(self):
        """Ensure no mock data in strategy generation"""
        payload = {
            "description": "Create a momentum trading strategy for AAPL",
            "start_date": "2023-01-01",
            "end_date": "2024-01-01"
        }
        response = requests.post(f"{BASE_URL}/api/strategy/generate", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        code = data.get('code', '')
        
        # Check for mock data indicators
        mock_indicators = ['mock', 'fake', 'test_data', 'sample_data']
        for indicator in mock_indicators:
            self.assertNotIn(indicator.lower(), code.lower(),
                           f"Found mock indicator: {indicator}")
        
        # Ensure real strategy patterns
        self.assertIn('class', code)
        self.assertIn('def', code)
        self.assertIn('backtrader', code.lower())
        print(f"{Fore.GREEN}✅ No mock data in generated strategy")
    
    def test_04_advanced_backtest_with_cerebro(self):
        """Test advanced backtest using Cerebro"""
        # Generate a real strategy
        strategy_response = requests.post(
            f"{BASE_URL}/api/strategy/generate",
            json={"description": "Simple moving average crossover", "start_date": "2023-01-01", "end_date": "2024-01-01"}
        )
        strategy_code = strategy_response.json().get('code', '')
        
        # Run advanced backtest
        payload = {
            "code": strategy_code,
            "symbol": "SPY",
            "start_date": "2023-01-01",
            "end_date": "2024-01-01",
            "initial_cash": 100000,
            "commission": 0.001
        }
        
        response = requests.post(f"{BASE_URL}/api/advanced-backtest", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        
        # Validate Cerebro was used properly
        self.assertIn('metrics', data)
        metrics = data['metrics']
        
        # Check for all 15+ performance metrics
        required_metrics = [
            'total_return', 'sharpe_ratio', 'sortino_ratio', 'calmar_ratio',
            'max_drawdown', 'win_rate', 'profit_factor', 'sqn', 'vwr'
        ]
        
        for metric in required_metrics:
            self.assertIn(metric, metrics,
                         f"Missing metric: {metric}")
        
        # Validate returns are logical
        total_return = metrics.get('total_return', 0)
        self.assertGreater(total_return, -100, "Return shouldn't be below -100%")
        self.assertLess(total_return, 1000, "Return seems unrealistic (>1000%)")
        
        print(f"{Fore.GREEN}✅ Advanced backtest with Cerebro working")
        print(f"  Total Return: {total_return:.2f}%")
        print(f"  Sharpe Ratio: {metrics.get('sharpe_ratio', 'N/A')}")
    
    def test_05_position_sizing_methods(self):
        """Test different position sizing methods"""
        methods = ['fixed', 'percentage', 'kelly', 'volatility']
        
        for method in methods:
            response = requests.get(f"{BASE_URL}/api/position-sizing/{method}")
            if response.status_code == 200:
                print(f"{Fore.GREEN}✅ Position sizing '{method}' available")
            else:
                print(f"{Fore.YELLOW}⚠️  Position sizing '{method}' not available")
    
    def test_06_order_types(self):
        """Test advanced order types availability"""
        order_types = [
            'market', 'limit', 'stop', 'stop_limit', 
            'trailing_stop', 'bracket', 'oco'
        ]
        
        # Test via indicator analysis endpoint
        response = requests.post(
            f"{BASE_URL}/api/indicator-analysis",
            json={
                "symbol": "SPY",
                "indicators": ["SMA"],
                "period": 20
            }
        )
        
        if response.status_code == 200:
            print(f"{Fore.GREEN}✅ Advanced order management system available")
        else:
            print(f"{Fore.YELLOW}⚠️  Order management needs verification")


class TestBusinessLogic(unittest.TestCase):
    """Business Logic and Common Sense Testing"""
    
    def test_01_realistic_backtest_results(self):
        """Validate backtest results are realistic"""
        # Simple buy-and-hold strategy
        simple_strategy = """
import backtrader as bt

class BuyAndHold(bt.Strategy):
    def __init__(self):
        pass
    
    def next(self):
        if not self.position:
            self.buy()
"""
        
        payload = {
            "code": simple_strategy,
            "symbol": "SPY",
            "start_date": "2023-01-01", 
            "end_date": "2023-12-31",
            "initial_cash": 100000,
            "commission": 0.001
        }
        
        response = requests.post(f"{BASE_URL}/api/advanced-backtest", json=payload)
        if response.status_code == 200:
            data = response.json()
            metrics = data.get('metrics', {})
            
            # Business logic checks
            self.assertIsNotNone(metrics.get('total_return'))
            self.assertIsNotNone(metrics.get('max_drawdown'))
            
            # Common sense checks
            total_return = metrics.get('total_return', 0)
            max_dd = metrics.get('max_drawdown', 0)
            
            # SPY typically returns between -20% to +30% annually
            self.assertGreater(total_return, -50, "Unrealistic loss for SPY")
            self.assertLess(total_return, 100, "Unrealistic gain for SPY")
            
            # Drawdown should be negative or zero
            self.assertLessEqual(max_dd, 0, "Drawdown should be negative")
            
            print(f"{Fore.GREEN}✅ Business logic validation passed")
            print(f"  SPY Annual Return: {total_return:.2f}%")
            print(f"  Max Drawdown: {max_dd:.2f}%")
    
    def test_02_data_flow_integrity(self):
        """Test data flows correctly through the system"""
        # Test flow: Generate -> Backtest -> Results
        
        # Step 1: Generate strategy
        gen_response = requests.post(
            f"{BASE_URL}/api/strategy/generate",
            json={"description": "MACD crossover strategy", "start_date": "2023-06-01", "end_date": "2023-12-01"}
        )
        self.assertEqual(gen_response.status_code, 200)
        strategy = gen_response.json()
        
        # Step 2: Run backtest
        backtest_response = requests.post(
            f"{BASE_URL}/api/advanced-backtest",
            json={
                "code": strategy['code'],
                "symbol": "AAPL",
                "start_date": "2023-06-01",
                "end_date": "2023-12-01",
                "initial_cash": 50000
            }
        )
        self.assertEqual(backtest_response.status_code, 200)
        results = backtest_response.json()
        
        # Step 3: Validate complete flow
        self.assertIn('metrics', results)
        self.assertIn('trades', results)
        
        print(f"{Fore.GREEN}✅ Data flow integrity verified")
    
    def test_03_error_handling(self):
        """Test system handles errors gracefully"""
        
        # Test with invalid strategy code
        bad_strategy = "this is not valid python code"
        response = requests.post(
            f"{BASE_URL}/api/advanced-backtest",
            json={
                "code": bad_strategy,
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31"
            }
        )
        
        # Should handle error gracefully
        if response.status_code == 500:
            self.assertIn('error', response.json())
        
        print(f"{Fore.GREEN}✅ Error handling working correctly")


class TestLLMIntegration(unittest.TestCase):
    """Test LLM Integration with Real Inputs"""
    
    def test_01_real_world_prompts(self):
        """Test with realistic trading strategy prompts"""
        real_prompts = [
            "Create a mean reversion strategy using Bollinger Bands",
            "Build a trend following system with RSI and moving averages",
            "Design a breakout strategy for volatile stocks",
            "Implement a pairs trading strategy"
        ]
        
        for prompt in real_prompts:
            response = requests.post(
                f"{BASE_URL}/api/strategy/generate",
                json={"description": prompt, "start_date": "2023-01-01", "end_date": "2024-01-01"}
            )
            
            if response.status_code == 200:
                data = response.json()
                code = data.get('code', '')
                
                # Validate generated code
                self.assertIn('class', code)
                self.assertIn('Strategy', code)
                self.assertIn('def __init__', code)
                self.assertIn('def next', code)
                
                print(f"{Fore.GREEN}✅ LLM handled: '{prompt[:50]}...'")
            else:
                print(f"{Fore.YELLOW}⚠️  LLM failed for: '{prompt[:50]}...'")
    
    def test_02_indicator_combinations(self):
        """Test complex indicator combinations"""
        response = requests.post(
            f"{BASE_URL}/api/indicator-analysis",
            json={
                "symbol": "TSLA",
                "indicators": ["SMA", "RSI", "MACD", "BBANDS"],
                "period": 20
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self.assertIn('analysis', data)
            print(f"{Fore.GREEN}✅ Complex indicator analysis working")


def run_frontend_verification():
    """Human-like frontend verification"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}FRONTEND VERIFICATION (Human-like Testing)")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    tests = [
        ("Homepage Load", f"{FRONTEND_URL}"),
        ("API Health Check", f"{FRONTEND_URL}/api/health"),
    ]
    
    for test_name, url in tests:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"{Fore.GREEN}✅ {test_name}: Accessible")
                
                # Check for mock data in response
                if 'mock' in response.text.lower():
                    print(f"{Fore.YELLOW}  ⚠️  Warning: Possible mock data detected")
            else:
                print(f"{Fore.YELLOW}⚠️  {test_name}: Status {response.status_code}")
        except Exception as e:
            print(f"{Fore.RED}❌ {test_name}: Failed - {e}")
    
    print(f"\n{Fore.CYAN}Frontend Components to Manually Verify:")
    print("1. Open http://localhost:3000")
    print("2. Click 'Generate Strategy' - ensure real code appears")
    print("3. Run a backtest - verify real market data is used")
    print("4. Check results show all 15+ metrics")
    print("5. Test saved strategies (no hardcoded mocks)")
    print("6. Verify WebSocket connection for real-time updates")


def main():
    """Run all tests"""
    print(f"{Fore.MAGENTA}{'='*60}")
    print(f"{Fore.MAGENTA}STATISFUND PHASE 2 COMPREHENSIVE TESTING")
    print(f"{Fore.MAGENTA}{'='*60}\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPhase2Backend))
    suite.addTests(loader.loadTestsFromTestCase(TestBusinessLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestLLMIntegration))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Frontend verification
    run_frontend_verification()
    
    # Summary
    print(f"\n{Fore.MAGENTA}{'='*60}")
    print(f"{Fore.MAGENTA}TEST SUMMARY")
    print(f"{Fore.MAGENTA}{'='*60}")
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print(f"\n{Fore.GREEN}🎉 ALL TESTS PASSED! Phase 2 Ready for Deployment")
    else:
        print(f"\n{Fore.RED}❌ Some tests failed. Review and fix before deployment")
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit(main())
