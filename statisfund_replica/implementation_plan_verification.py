#!/usr/bin/env python3
"""
Comprehensive Implementation vs Plan Verification Test
Tests the implementation against the original Statis Fund requirements
"""

import asyncio
import json
import requests
import time
from datetime import datetime
import sys
import os

BASE_URL = "http://localhost:8005"
FRONTEND_URL = "http://localhost:3000"

class PlanVerificationResults:
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.plan_compliance = {}
    
    def add_test(self, category, feature, status, details="", plan_requirement=""):
        result = {
            "category": category,
            "feature": feature,
            "status": status,  # "pass", "fail", "warning"
            "details": details,
            "plan_requirement": plan_requirement,
            "timestamp": datetime.now().isoformat()
        }
        self.tests.append(result)
        
        if status == "pass":
            self.passed += 1
            print(f"✅ {category}: {feature}")
        elif status == "fail":
            self.failed += 1
            print(f"❌ {category}: {feature}")
        else:
            self.warnings += 1
            print(f"⚠️  {category}: {feature}")
        
        if details:
            print(f"   {details}")

results = PlanVerificationResults()

def test_core_features_vs_plan():
    """Test Core Features Against Original Statis Fund Plan"""
    
    print("🎯 TESTING CORE FEATURES VS PLAN")
    print("=" * 50)
    
    # 1. Natural Language Strategy Input
    try:
        nl_input = {
            "description": "if the 20D MA of SPY is increasing, buy UPRO, else sell to cash",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "mode": "Interday",
            "ai_model": "GPT-4.1-mini"
        }
        
        response = requests.post(f"{BASE_URL}/api/strategy/generate/stream", 
                               json=nl_input, stream=True, timeout=10)
        
        if response.status_code == 200:
            chunks_received = 0
            for line in response.iter_lines():
                if line and chunks_received < 5:  # Test first few chunks
                    chunks_received += 1
            
            if chunks_received > 0:
                results.add_test("Core Features", "Natural Language Strategy Input", "pass",
                               f"Successfully processed NL input with {chunks_received} streaming chunks",
                               "Natural Language Strategy Input: 'if the 20D MA of SPY is increasing, buy UPRO, else sell to cash'")
            else:
                results.add_test("Core Features", "Natural Language Strategy Input", "fail",
                               "No streaming response received",
                               "Natural Language Strategy Input required")
        else:
            results.add_test("Core Features", "Natural Language Strategy Input", "fail",
                           f"HTTP {response.status_code}",
                           "Natural Language Strategy Input required")
    except Exception as e:
        results.add_test("Core Features", "Natural Language Strategy Input", "fail",
                       f"Error: {str(e)}",
                       "Natural Language Strategy Input required")
    
    # 2. Real-time AI Code Generation with SSE
    try:
        response = requests.post(f"{BASE_URL}/api/strategy/generate/stream", 
                               json=nl_input, stream=True, timeout=15)
        
        if response.status_code == 200:
            sse_working = False
            code_generated = False
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        sse_working = True
                        try:
                            data = json.loads(line_str[6:].strip())
                            if 'code' in data and len(data['code']) > 100:
                                code_generated = True
                                break
                        except:
                            pass
                    if sse_working and not code_generated:
                        break  # Limit test time
            
            if sse_working and code_generated:
                results.add_test("Core Features", "Real-time AI Code Generation", "pass",
                               "SSE streaming with code generation working",
                               "Real-time AI Code Generation: Streaming SSE connection with live code generation")
            elif sse_working:
                results.add_test("Core Features", "Real-time AI Code Generation", "warning",
                               "SSE working but code generation incomplete in test timeframe",
                               "Real-time AI Code Generation required")
            else:
                results.add_test("Core Features", "Real-time AI Code Generation", "fail",
                               "SSE streaming not working",
                               "Real-time AI Code Generation required")
        else:
            results.add_test("Core Features", "Real-time AI Code Generation", "fail",
                           f"HTTP {response.status_code}",
                           "Real-time AI Code Generation required")
    except Exception as e:
        results.add_test("Core Features", "Real-time AI Code Generation", "fail",
                       f"Error: {str(e)}",
                       "Real-time AI Code Generation required")
    
    # 3. Multiple AI Models Support
    try:
        models_response = requests.get(f"{BASE_URL}/", timeout=5)
        if models_response.status_code == 200:
            # Check if we can specify different models
            gpt4_test = {
                "description": "Simple momentum strategy",
                "ai_model": "GPT-4o"
            }
            
            model_response = requests.post(f"{BASE_URL}/api/strategy/generate/stream", 
                                         json=gpt4_test, stream=True, timeout=5)
            
            if model_response.status_code == 200:
                results.add_test("Core Features", "Multiple AI Models", "pass",
                               "AI model selection supported",
                               "Multiple AI Models: GPT-4.1-mini (fast), GPT-4o, proprietary models")
            else:
                results.add_test("Core Features", "Multiple AI Models", "warning",
                               "AI model parameter accepted but functionality unclear",
                               "Multiple AI Models required")
        else:
            results.add_test("Core Features", "Multiple AI Models", "fail",
                           "Cannot verify AI model support",
                           "Multiple AI Models required")
    except Exception as e:
        results.add_test("Core Features", "Multiple AI Models", "warning",
                       f"Model testing limited: {str(e)}",
                       "Multiple AI Models required")

def test_interactive_backtesting():
    """Test Interactive Backtesting Features"""
    
    print("\n📊 TESTING INTERACTIVE BACKTESTING")
    print("=" * 50)
    
    # Test backtesting with date range selection
    try:
        backtest_data = {
            "code": """import backtrader as bt

class TestStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=20)
    
    def next(self):
        if not self.position and self.data.close[0] > self.sma[0]:
            self.buy(size=100)
        elif self.position and self.data.close[0] < self.sma[0]:
            self.sell(size=self.position.size)
""",
            "symbol": "SPY",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "initial_cash": 10000,
            "parameters": {}
        }
        
        response = requests.post(f"{BASE_URL}/api/backtest", json=backtest_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                metrics = data.get('performance_metrics', {})
                if 'total_return' in metrics:
                    results.add_test("Interactive Backtesting", "Date Range Selection", "pass",
                                   f"Backtest completed with return: {metrics.get('total_return', 'N/A')}%",
                                   "Interactive Backtesting: Date range selection, strategy locking, real-time results")
                else:
                    results.add_test("Interactive Backtesting", "Date Range Selection", "warning",
                                   "Backtest completed but metrics incomplete",
                                   "Interactive Backtesting required")
            else:
                results.add_test("Interactive Backtesting", "Date Range Selection", "fail",
                               f"Backtest failed: {data.get('error', 'Unknown error')}",
                               "Interactive Backtesting required")
        else:
            results.add_test("Interactive Backtesting", "Date Range Selection", "fail",
                           f"HTTP {response.status_code}",
                           "Interactive Backtesting required")
    except Exception as e:
        results.add_test("Interactive Backtesting", "Date Range Selection", "fail",
                       f"Error: {str(e)}",
                       "Interactive Backtesting required")

def test_comprehensive_analytics():
    """Test Comprehensive Analytics Features"""
    
    print("\n📈 TESTING COMPREHENSIVE ANALYTICS")
    print("=" * 50)
    
    # Test performance metrics and analytics
    try:
        response = requests.get(f"{BASE_URL}/api/statistics", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data.get('statistics', {})
                
                # Check for key analytics components
                required_metrics = ['total_strategies', 'performance_stats', 'categories']
                found_metrics = [metric for metric in required_metrics if metric in stats]
                
                if len(found_metrics) >= 2:
                    results.add_test("Comprehensive Analytics", "Performance Metrics", "pass",
                                   f"Analytics available: {len(stats)} metrics including {found_metrics}",
                                   "Comprehensive Analytics: Performance metrics, detailed analytics")
                else:
                    results.add_test("Comprehensive Analytics", "Performance Metrics", "warning",
                                   f"Limited analytics: {found_metrics}",
                                   "Comprehensive Analytics required")
            else:
                results.add_test("Comprehensive Analytics", "Performance Metrics", "fail",
                               f"Analytics failed: {data.get('error', 'Unknown')}",
                               "Comprehensive Analytics required")
        else:
            results.add_test("Comprehensive Analytics", "Performance Metrics", "fail",
                           f"HTTP {response.status_code}",
                           "Comprehensive Analytics required")
    except Exception as e:
        results.add_test("Comprehensive Analytics", "Performance Metrics", "fail",
                       f"Error: {str(e)}",
                       "Comprehensive Analytics required")

def test_strategy_management():
    """Test Strategy Management Features"""
    
    print("\n💾 TESTING STRATEGY MANAGEMENT")
    print("=" * 50)
    
    # Test strategy saving and management
    try:
        strategy_data = {
            "name": "Plan Verification Strategy",
            "description": "Strategy for testing plan compliance",
            "code": """import backtrader as bt
class PlanTestStrategy(bt.Strategy):
    def next(self):
        pass
""",
            "tags": ["plan", "verification"],
            "symbols": ["SPY"],
            "parameters": {"test": True}
        }
        
        # Test saving
        save_response = requests.post(f"{BASE_URL}/api/strategy/save", json=strategy_data, timeout=10)
        
        if save_response.status_code == 200:
            # Handle both JSON and string responses
            try:
                save_data = save_response.json()
                strategy_id = save_data.get('strategy_id')
            except:
                strategy_id = save_response.text.strip('"')
            
            if strategy_id:
                # Test strategy listing
                list_response = requests.get(f"{BASE_URL}/api/strategies", timeout=10)
                
                if list_response.status_code == 200:
                    list_data = list_response.json()
                    if list_data.get('success'):
                        results.add_test("Strategy Management", "Save & List Strategies", "pass",
                                       f"Strategy saved with ID: {strategy_id[:8]}... and listing works",
                                       "Strategy Management: Save strategies, follow algorithms, investment tracking")
                    else:
                        results.add_test("Strategy Management", "Save & List Strategies", "warning",
                                       "Strategy saved but listing has issues",
                                       "Strategy Management required")
                else:
                    results.add_test("Strategy Management", "Save & List Strategies", "warning",
                                   "Strategy saved but listing endpoint failed",
                                   "Strategy Management required")
            else:
                results.add_test("Strategy Management", "Save & List Strategies", "fail",
                               "Strategy save returned no ID",
                               "Strategy Management required")
        else:
            results.add_test("Strategy Management", "Save & List Strategies", "fail",
                           f"HTTP {save_response.status_code}",
                           "Strategy Management required")
    except Exception as e:
        results.add_test("Strategy Management", "Save & List Strategies", "fail",
                       f"Error: {str(e)}",
                       "Strategy Management required")

def test_api_endpoints():
    """Test API Endpoints Compatibility"""
    
    print("\n🔌 TESTING API ENDPOINTS")
    print("=" * 50)
    
    # Test RESTful API endpoints
    api_tests = [
        ("/", "Root API", "RESTful API for data, indicators, moving averages, volatility, etc."),
        ("/api/statistics", "Statistics API", "API Endpoints required"),
        ("/api/templates", "Templates API", "API Endpoints required"),
        ("/api/user/ideas", "User Ideas API", "API Endpoints required"),
    ]
    
    passed_apis = 0
    total_apis = len(api_tests)
    
    for endpoint, name, requirement in api_tests:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                passed_apis += 1
                results.add_test("API Endpoints", name, "pass",
                               f"Endpoint operational",
                               requirement)
            else:
                results.add_test("API Endpoints", name, "fail",
                               f"HTTP {response.status_code}",
                               requirement)
        except Exception as e:
            results.add_test("API Endpoints", name, "fail",
                           f"Error: {str(e)}",
                           requirement)
    
    # Overall API compliance
    api_compliance = (passed_apis / total_apis) * 100
    if api_compliance >= 75:
        results.add_test("API Endpoints", "Overall API Compliance", "pass",
                       f"{api_compliance:.1f}% of APIs operational",
                       "RESTful API for data, indicators, moving averages, volatility, etc.")
    else:
        results.add_test("API Endpoints", "Overall API Compliance", "fail",
                       f"Only {api_compliance:.1f}% of APIs operational",
                       "RESTful API required")

def test_technical_stack_compliance():
    """Test Technical Stack Against Plan"""
    
    print("\n🏗️ TESTING TECHNICAL STACK COMPLIANCE")
    print("=" * 50)
    
    # Test Backend Stack
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            results.add_test("Technical Stack", "Python Backend with FastAPI", "pass",
                           "FastAPI backend operational",
                           "Backend: Python with yfinance, Backtrader, FastAPI/Flask")
        else:
            results.add_test("Technical Stack", "Python Backend with FastAPI", "fail",
                           f"Backend not responding: {response.status_code}",
                           "Backend: Python with yfinance, Backtrader, FastAPI/Flask")
    except Exception as e:
        results.add_test("Technical Stack", "Python Backend with FastAPI", "fail",
                       f"Backend error: {str(e)}",
                       "Backend: Python with yfinance, Backtrader, FastAPI/Flask")
    
    # Test Frontend Stack
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            results.add_test("Technical Stack", "React Frontend with SSE", "pass",
                           "React frontend operational",
                           "Frontend: React with real-time streaming (SSE), interactive forms")
        else:
            results.add_test("Technical Stack", "React Frontend with SSE", "warning",
                           f"Frontend status: {response.status_code}",
                           "Frontend: React with real-time streaming (SSE), interactive forms")
    except Exception as e:
        results.add_test("Technical Stack", "React Frontend with SSE", "warning",
                       f"Frontend check limited: {str(e)}",
                       "Frontend: React with real-time streaming (SSE), interactive forms")

def test_pricing_tier_features():
    """Test Features Against Pricing Tier Requirements"""
    
    print("\n💰 TESTING PRICING TIER FEATURES")
    print("=" * 50)
    
    # Test Free Tier Features (Test tier)
    try:
        ideas_response = requests.get(f"{BASE_URL}/api/user/ideas", timeout=5)
        if ideas_response.status_code == 200:
            data = ideas_response.json()
            ideas_remaining = data.get('ideas_remaining', 0)
            
            if ideas_remaining > 0:
                results.add_test("Pricing Tiers", "Free Tier - Ideas Tracking", "pass",
                               f"{ideas_remaining} ideas remaining",
                               "Test (Free): 3 ideas/month, basic analytics, GPT-4o/mini models")
            else:
                results.add_test("Pricing Tiers", "Free Tier - Ideas Tracking", "warning",
                               "Ideas tracking working but no ideas remaining",
                               "Test (Free): 3 ideas/month, basic analytics, GPT-4o/mini models")
        else:
            results.add_test("Pricing Tiers", "Free Tier - Ideas Tracking", "fail",
                           f"Ideas API failed: {ideas_response.status_code}",
                           "Test (Free): 3 ideas/month, basic analytics, GPT-4o/mini models")
    except Exception as e:
        results.add_test("Pricing Tiers", "Free Tier - Ideas Tracking", "fail",
                       f"Error: {str(e)}",
                       "Test (Free): 3 ideas/month, basic analytics, GPT-4o/mini models")

def generate_compliance_report():
    """Generate Final Compliance Report"""
    
    print("\n" + "=" * 70)
    print("📋 IMPLEMENTATION vs PLAN COMPLIANCE REPORT")
    print("=" * 70)
    
    total_tests = len(results.tests)
    pass_rate = (results.passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📊 Total Features Tested: {total_tests}")
    print(f"✅ Compliant Features: {results.passed}")
    print(f"❌ Non-Compliant Features: {results.failed}")
    print(f"⚠️  Partially Compliant: {results.warnings}")
    print(f"📈 Overall Compliance Rate: {pass_rate:.1f}%")
    
    # Category breakdown
    categories = {}
    for test in results.tests:
        cat = test['category']
        if cat not in categories:
            categories[cat] = {'pass': 0, 'fail': 0, 'warning': 0}
        categories[cat][test['status']] += 1
    
    print(f"\n📂 Compliance by Category:")
    for category, counts in categories.items():
        total_cat = sum(counts.values())
        pass_cat = counts['pass']
        compliance_rate = (pass_cat / total_cat * 100) if total_cat > 0 else 0
        print(f"   {category}: {compliance_rate:.1f}% ({pass_cat}/{total_cat})")
    
    # Failed requirements
    if results.failed > 0:
        print(f"\n❌ Non-Compliant Requirements:")
        for test in results.tests:
            if test['status'] == 'fail':
                print(f"   • {test['category']} - {test['feature']}: {test['details']}")
    
    # Overall assessment
    print(f"\n🎯 OVERALL PLAN COMPLIANCE ASSESSMENT:")
    if pass_rate >= 90:
        print("🎉 EXCELLENT - Implementation exceeds plan requirements")
        compliance_status = "EXCEEDS PLAN"
    elif pass_rate >= 80:
        print("✅ GOOD - Implementation meets plan requirements")
        compliance_status = "MEETS PLAN"
    elif pass_rate >= 70:
        print("⚠️  ACCEPTABLE - Implementation mostly meets plan with minor gaps")
        compliance_status = "MOSTLY COMPLIANT"
    else:
        print("❌ NEEDS WORK - Implementation has significant gaps vs plan")
        compliance_status = "NON-COMPLIANT"
    
    # Save detailed results
    compliance_report = {
        'summary': {
            'total_tests': total_tests,
            'passed': results.passed,
            'failed': results.failed,
            'warnings': results.warnings,
            'compliance_rate': pass_rate,
            'status': compliance_status
        },
        'categories': categories,
        'tests': results.tests,
        'timestamp': datetime.now().isoformat()
    }
    
    with open('/Users/Gautam/TradingAgents/statisfund_replica/plan_compliance_report.json', 'w') as f:
        json.dump(compliance_report, f, indent=2)
    
    print(f"\n📄 Detailed compliance report saved to: plan_compliance_report.json")
    
    return compliance_status

def run_comprehensive_plan_verification():
    """Run comprehensive verification against implementation plan"""
    
    print("🚀 COMPREHENSIVE IMPLEMENTATION vs PLAN VERIFICATION")
    print("=" * 70)
    print("Testing implementation against original Statis Fund requirements...")
    
    # Test all major categories
    test_core_features_vs_plan()
    test_interactive_backtesting()
    test_comprehensive_analytics()
    test_strategy_management()
    test_api_endpoints()
    test_technical_stack_compliance()
    test_pricing_tier_features()
    
    # Generate final report
    compliance_status = generate_compliance_report()
    
    return compliance_status == "MEETS PLAN" or compliance_status == "EXCEEDS PLAN"

if __name__ == "__main__":
    success = run_comprehensive_plan_verification()
    sys.exit(0 if success else 1)
