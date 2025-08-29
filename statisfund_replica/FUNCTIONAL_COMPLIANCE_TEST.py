#!/usr/bin/env python3
"""
Statis Fund Functional Compliance Testing
Tests actual implementation against STATISFUND_BACKTRADER_INTEGRATION_GUIDE.md requirements
"""

import requests
import json
import asyncio
import time
import sys
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any

class StatisFundComplianceTest:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {},
            "compliance_score": 0
        }
        
        # Expected features from integration guide
        self.expected_features = {
            "strategy_generation": {
                "natural_language_input": True,
                "ai_code_generation": True,
                "backtrader_output": True,
                "streaming_support": True
            },
            "backtesting": {
                "historical_data": True,
                "performance_metrics": True,
                "risk_analytics": True,
                "multiple_symbols": True
            },
            "indicators": {
                "basic_indicators": ["SMA", "RSI", "MACD"],
                "advanced_indicators": ["BB", "ATR", "ADX"],
                "ta_lib_integration": False  # Not yet implemented
            },
            "order_management": {
                "basic_orders": ["Market", "Limit"],
                "advanced_orders": ["Stop", "StopLimit", "Trailing"],
                "risk_management": True
            },
            "performance_analytics": {
                "sharpe_ratio": True,
                "max_drawdown": True,
                "total_return": True,
                "advanced_metrics": ["Sortino", "Calmar", "VaR"]
            },
            "data_sources": {
                "yfinance": True,
                "alpha_vantage_fallback": True,
                "real_time_data": False,
                "multiple_assets": ["stocks", "crypto", "forex"]
            }
        }

    def log_test(self, test_name: str, status: str, details: Dict[str, Any]):
        """Log test result"""
        test_result = {
            "test_name": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.results["tests"].append(test_result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        
        if details.get("error"):
            print(f"   Error: {details['error']}")
        if details.get("expected"):
            print(f"   Expected: {details['expected']}")
        if details.get("actual"):
            print(f"   Actual: {details['actual']}")

    async def test_backend_health(self):
        """Test if backend is running and responsive"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                self.log_test("Backend Health Check", "PASS", {
                    "status_code": response.status_code,
                    "response": response.json()
                })
                return True
            else:
                self.log_test("Backend Health Check", "FAIL", {
                    "status_code": response.status_code,
                    "error": "Backend not healthy"
                })
                return False
        except Exception as e:
            self.log_test("Backend Health Check", "FAIL", {
                "error": str(e)
            })
            return False

    async def test_strategy_generation_basic(self):
        """Test basic natural language to code generation"""
        try:
            # Test natural language strategy input
            strategy_request = {
                "description": "Buy when RSI is below 30 and sell when RSI is above 70. Use stop loss of 5%.",
                "symbols": ["AAPL"],
                "timeframe": "1d",
                "start_date": "2023-01-01",
                "end_date": "2024-01-01"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/generate-strategy",
                json=strategy_request,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if strategy code is generated
                has_code = bool(result.get("strategy_code") or result.get("code"))
                has_backtrader_imports = False
                has_rsi_logic = False
                
                if has_code:
                    code = result.get("strategy_code") or result.get("code")
                    has_backtrader_imports = "backtrader" in code.lower() or "bt." in code
                    has_rsi_logic = "rsi" in code.lower()
                
                compliance_score = 0
                if has_code: compliance_score += 40
                if has_backtrader_imports: compliance_score += 30
                if has_rsi_logic: compliance_score += 30
                
                self.log_test("Strategy Generation - Basic", 
                    "PASS" if compliance_score >= 70 else "PARTIAL", {
                    "has_code": has_code,
                    "has_backtrader_imports": has_backtrader_imports,
                    "has_rsi_logic": has_rsi_logic,
                    "compliance_score": f"{compliance_score}/100",
                    "code_preview": (code[:200] + "...") if has_code and len(code) > 200 else code if has_code else None
                })
                
                return compliance_score >= 70, result
                
            else:
                self.log_test("Strategy Generation - Basic", "FAIL", {
                    "status_code": response.status_code,
                    "error": response.text
                })
                return False, None
                
        except Exception as e:
            self.log_test("Strategy Generation - Basic", "FAIL", {
                "error": str(e)
            })
            return False, None

    async def test_backtest_functionality(self, strategy_code=None):
        """Test backtesting engine functionality"""
        try:
            # Use provided strategy code or fallback
            if not strategy_code:
                strategy_code = """
import backtrader as bt
import pandas as pd

class RSIStrategy(bt.Strategy):
    params = (('rsi_period', 14), ('rsi_upper', 70), ('rsi_lower', 30),)
    
    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)
        
    def next(self):
        if not self.position and self.rsi[0] < self.params.rsi_lower:
            self.buy(size=100)
        elif self.position and self.rsi[0] > self.params.rsi_upper:
            self.sell(size=self.position.size)
"""
            
            backtest_request = {
                "strategy_code": strategy_code,
                "symbols": ["AAPL"],
                "start_date": "2023-01-01",
                "end_date": "2023-06-01",
                "initial_cash": 10000
            }
            
            response = requests.post(
                f"{self.backend_url}/api/backtest",
                json=backtest_request,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check for required backtest results
                has_results = bool(result.get("results") or result.get("backtest_results"))
                has_performance_metrics = False
                has_final_value = False
                has_returns = False
                
                if has_results:
                    results_data = result.get("results") or result.get("backtest_results")
                    has_final_value = "final_value" in str(results_data) or "ending_value" in str(results_data)
                    has_returns = "return" in str(results_data).lower() or "pnl" in str(results_data).lower()
                    has_performance_metrics = any(metric in str(results_data).lower() 
                                                for metric in ["sharpe", "drawdown", "volatility"])
                
                compliance_score = 0
                if has_results: compliance_score += 30
                if has_final_value: compliance_score += 25
                if has_returns: compliance_score += 25
                if has_performance_metrics: compliance_score += 20
                
                self.log_test("Backtest Functionality", 
                    "PASS" if compliance_score >= 70 else "PARTIAL", {
                    "has_results": has_results,
                    "has_final_value": has_final_value,
                    "has_returns": has_returns,
                    "has_performance_metrics": has_performance_metrics,
                    "compliance_score": f"{compliance_score}/100",
                    "result_preview": str(result)[:300] + "..." if len(str(result)) > 300 else str(result)
                })
                
                return compliance_score >= 70
                
            else:
                self.log_test("Backtest Functionality", "FAIL", {
                    "status_code": response.status_code,
                    "error": response.text[:500]
                })
                return False
                
        except Exception as e:
            self.log_test("Backtest Functionality", "FAIL", {
                "error": str(e)
            })
            return False

    async def test_indicators_support(self):
        """Test technical indicators support"""
        try:
            # Test indicators endpoint
            response = requests.get(f"{self.backend_url}/api/indicators", timeout=10)
            
            if response.status_code == 200:
                indicators = response.json()
                
                # Check for basic indicators from integration guide
                expected_basic = ["SMA", "RSI", "MACD", "EMA"]
                expected_advanced = ["BB", "ATR", "ADX", "Stochastic"]
                
                indicators_list = []
                if isinstance(indicators, dict) and "indicators" in indicators:
                    indicators_list = indicators["indicators"]
                elif isinstance(indicators, list):
                    indicators_list = indicators
                
                basic_coverage = sum(1 for ind in expected_basic 
                                   if any(ind.lower() in str(indicator).lower() 
                                         for indicator in indicators_list))
                
                advanced_coverage = sum(1 for ind in expected_advanced 
                                      if any(ind.lower() in str(indicator).lower() 
                                            for indicator in indicators_list))
                
                total_indicators = len(indicators_list) if indicators_list else 0
                
                compliance_score = (basic_coverage / len(expected_basic)) * 50 + \
                                 (advanced_coverage / len(expected_advanced)) * 30 + \
                                 min(total_indicators / 20, 1) * 20  # Bonus for having many indicators
                
                self.log_test("Indicators Support", 
                    "PASS" if compliance_score >= 60 else "PARTIAL", {
                    "total_indicators": total_indicators,
                    "basic_coverage": f"{basic_coverage}/{len(expected_basic)}",
                    "advanced_coverage": f"{advanced_coverage}/{len(expected_advanced)}",
                    "compliance_score": f"{compliance_score:.1f}/100",
                    "indicators_sample": indicators_list[:10] if indicators_list else []
                })
                
                return compliance_score >= 60
                
            else:
                self.log_test("Indicators Support", "FAIL", {
                    "status_code": response.status_code,
                    "error": "Indicators endpoint not accessible"
                })
                return False
                
        except Exception as e:
            self.log_test("Indicators Support", "FAIL", {
                "error": str(e)
            })
            return False

    async def test_market_data_integration(self):
        """Test market data connectivity and accuracy"""
        try:
            # Test market data endpoint
            response = requests.get(f"{self.backend_url}/api/market-data", timeout=15)
            
            if response.status_code == 200:
                market_data = response.json()
                
                # Check data quality and structure
                has_price_data = bool(market_data.get("data") or market_data.get("stocks"))
                has_real_prices = False
                has_multiple_stocks = False
                
                if has_price_data:
                    data = market_data.get("data") or market_data.get("stocks") or []
                    if isinstance(data, list) and len(data) > 0:
                        has_multiple_stocks = len(data) > 3
                        # Check if prices look realistic (not just mock 100.00 values)
                        prices = []
                        for item in data:
                            if isinstance(item, dict):
                                price = item.get("price") or item.get("current_price") or item.get("close")
                                if price and isinstance(price, (int, float)):
                                    prices.append(price)
                        
                        has_real_prices = len(set(prices)) > 1 and not all(p == 100.0 for p in prices)
                
                compliance_score = 0
                if has_price_data: compliance_score += 40
                if has_multiple_stocks: compliance_score += 30
                if has_real_prices: compliance_score += 30
                
                self.log_test("Market Data Integration", 
                    "PASS" if compliance_score >= 70 else "PARTIAL", {
                    "has_price_data": has_price_data,
                    "has_multiple_stocks": has_multiple_stocks,
                    "has_real_prices": has_real_prices,
                    "compliance_score": f"{compliance_score}/100",
                    "data_sample": str(market_data)[:200] + "..." if len(str(market_data)) > 200 else str(market_data)
                })
                
                return compliance_score >= 70
                
            else:
                self.log_test("Market Data Integration", "FAIL", {
                    "status_code": response.status_code,
                    "error": "Market data endpoint not accessible"
                })
                return False
                
        except Exception as e:
            self.log_test("Market Data Integration", "FAIL", {
                "error": str(e)
            })
            return False

    async def test_strategy_management(self):
        """Test strategy saving, loading, and management"""
        try:
            # Test saving a strategy
            save_request = {
                "name": "Test RSI Strategy",
                "description": "Simple RSI-based strategy for testing",
                "code": "class TestStrategy(bt.Strategy): pass",
                "parameters": {"rsi_period": 14}
            }
            
            response = requests.post(
                f"{self.backend_url}/api/strategies",
                json=save_request,
                timeout=10
            )
            
            save_success = response.status_code in [200, 201]
            
            # Test loading strategies
            response = requests.get(f"{self.backend_url}/api/strategies", timeout=10)
            load_success = response.status_code == 200
            
            strategies_list = []
            if load_success:
                strategies_data = response.json()
                if isinstance(strategies_data, list):
                    strategies_list = strategies_data
                elif isinstance(strategies_data, dict) and "strategies" in strategies_data:
                    strategies_list = strategies_data["strategies"]
            
            has_strategies = len(strategies_list) > 0
            
            compliance_score = 0
            if save_success: compliance_score += 50
            if load_success: compliance_score += 30
            if has_strategies: compliance_score += 20
            
            self.log_test("Strategy Management", 
                "PASS" if compliance_score >= 70 else "PARTIAL", {
                "save_success": save_success,
                "load_success": load_success,
                "has_strategies": has_strategies,
                "strategies_count": len(strategies_list),
                "compliance_score": f"{compliance_score}/100"
            })
            
            return compliance_score >= 70
            
        except Exception as e:
            self.log_test("Strategy Management", "FAIL", {
                "error": str(e)
            })
            return False

    async def test_phase2_features(self):
        """Test Phase 2 advanced features from integration guide"""
        phase2_results = {
            "advanced_indicators": False,
            "advanced_orders": False,
            "multi_asset": False,
            "live_trading": False,
            "performance_analytics": False
        }
        
        # Test advanced indicators (122+ indicators from Phase 2 plan)
        try:
            response = requests.get(f"{self.backend_url}/api/indicators/advanced", timeout=10)
            if response.status_code == 200:
                indicators = response.json()
                indicator_count = len(indicators.get("indicators", [])) if isinstance(indicators, dict) else len(indicators) if isinstance(indicators, list) else 0
                phase2_results["advanced_indicators"] = indicator_count >= 50  # At least 50 indicators
        except:
            pass
        
        # Test advanced order types
        try:
            response = requests.get(f"{self.backend_url}/api/orders/types", timeout=10)
            if response.status_code == 200:
                order_types = response.json()
                advanced_orders = ["stop", "limit", "trailing", "oco", "bracket"]
                supported_advanced = sum(1 for order in advanced_orders 
                                       if order in str(order_types).lower())
                phase2_results["advanced_orders"] = supported_advanced >= 3
        except:
            pass
        
        # Test multi-asset support
        try:
            response = requests.get(f"{self.backend_url}/api/assets/supported", timeout=10)
            if response.status_code == 200:
                assets = response.json()
                asset_types = ["stocks", "crypto", "forex", "futures"]
                supported_assets = sum(1 for asset in asset_types 
                                     if asset in str(assets).lower())
                phase2_results["multi_asset"] = supported_assets >= 2
        except:
            pass
        
        # Test live trading capabilities
        try:
            response = requests.get(f"{self.backend_url}/api/trading/brokers", timeout=10)
            if response.status_code == 200:
                brokers = response.json()
                expected_brokers = ["zerodha", "alpaca", "binance"]
                supported_brokers = sum(1 for broker in expected_brokers 
                                      if broker in str(brokers).lower())
                phase2_results["live_trading"] = supported_brokers >= 1
        except:
            pass
        
        # Test advanced performance analytics
        try:
            backtest_request = {
                "strategy_code": "class DummyStrategy(bt.Strategy): pass",
                "symbols": ["AAPL"],
                "start_date": "2023-01-01",
                "end_date": "2023-02-01",
                "advanced_analytics": True
            }
            response = requests.post(f"{self.backend_url}/api/advanced-backtest", 
                                   json=backtest_request, timeout=30)
            if response.status_code == 200:
                result = response.json()
                advanced_metrics = ["sortino", "calmar", "var", "sharpe", "alpha", "beta"]
                found_metrics = sum(1 for metric in advanced_metrics 
                                  if metric in str(result).lower())
                phase2_results["performance_analytics"] = found_metrics >= 4
        except:
            pass
        
        implemented_features = sum(phase2_results.values())
        total_features = len(phase2_results)
        compliance_score = (implemented_features / total_features) * 100
        
        self.log_test("Phase 2 Advanced Features", 
            "PASS" if compliance_score >= 60 else "PARTIAL", {
            "implemented_features": f"{implemented_features}/{total_features}",
            "advanced_indicators": phase2_results["advanced_indicators"],
            "advanced_orders": phase2_results["advanced_orders"],
            "multi_asset": phase2_results["multi_asset"],
            "live_trading": phase2_results["live_trading"],
            "performance_analytics": phase2_results["performance_analytics"],
            "compliance_score": f"{compliance_score:.1f}/100"
        })
        
        return compliance_score >= 60

    async def run_all_tests(self):
        """Run comprehensive functional compliance tests"""
        print("🧪 Starting Statis Fund Functional Compliance Testing...")
        print("=" * 60)
        
        # Test backend health first
        backend_healthy = await self.test_backend_health()
        if not backend_healthy:
            print("❌ Backend not available. Please ensure backend is running on http://localhost:8000")
            return
        
        # Core functionality tests
        test_results = []
        
        # Test 1: Strategy Generation
        strategy_success, generated_strategy = await self.test_strategy_generation_basic()
        test_results.append(strategy_success)
        
        # Test 2: Backtest Functionality
        backtest_success = await self.test_backtest_functionality(
            generated_strategy.get("code") if generated_strategy else None
        )
        test_results.append(backtest_success)
        
        # Test 3: Indicators Support
        indicators_success = await self.test_indicators_support()
        test_results.append(indicators_success)
        
        # Test 4: Market Data Integration
        market_data_success = await self.test_market_data_integration()
        test_results.append(market_data_success)
        
        # Test 5: Strategy Management
        strategy_mgmt_success = await self.test_strategy_management()
        test_results.append(strategy_mgmt_success)
        
        # Test 6: Phase 2 Advanced Features
        phase2_success = await self.test_phase2_features()
        test_results.append(phase2_success)
        
        # Calculate overall compliance
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        overall_compliance = (passed_tests / total_tests) * 100
        
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "overall_compliance": f"{overall_compliance:.1f}%",
            "status": "COMPLIANT" if overall_compliance >= 70 else "PARTIAL_COMPLIANCE" if overall_compliance >= 50 else "NON_COMPLIANT"
        }
        
        print("\n" + "=" * 60)
        print("📊 FUNCTIONAL COMPLIANCE SUMMARY")
        print("=" * 60)
        print(f"Overall Compliance: {overall_compliance:.1f}%")
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Status: {self.results['summary']['status']}")
        
        if overall_compliance >= 70:
            print("\n✅ COMPLIANT: Implementation meets integration guide requirements")
        elif overall_compliance >= 50:
            print("\n⚠️ PARTIAL COMPLIANCE: Some features missing or incomplete")
        else:
            print("\n❌ NON-COMPLIANT: Significant gaps from integration guide requirements")
        
        return self.results

async def main():
    """Run functional compliance testing"""
    tester = StatisFundComplianceTest()
    results = await tester.run_all_tests()
    
    # Save results to file
    with open("/Users/Gautam/TradingAgents/statisfund_replica/FUNCTIONAL_COMPLIANCE_RESULTS.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: FUNCTIONAL_COMPLIANCE_RESULTS.json")
    return results

if __name__ == "__main__":
    asyncio.run(main())
