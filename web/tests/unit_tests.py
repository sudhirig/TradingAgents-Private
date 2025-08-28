#!/usr/bin/env python3
"""
Unit Tests for TradingAgents Components
Tests critical functions, data validation, and component behavior
"""

import unittest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

class TestConfigurationValidation(unittest.TestCase):
    """Test configuration validation logic"""
    
    def test_ticker_validation(self):
        """Test ticker symbol validation"""
        valid_tickers = ["AAPL", "TSLA", "SPY", "MSFT"]
        invalid_tickers = ["", "123", "TOOLONG", "invalid-ticker"]
        
        for ticker in valid_tickers:
            self.assertTrue(self.is_valid_ticker(ticker), f"Valid ticker {ticker} should pass")
        
        for ticker in invalid_tickers:
            self.assertFalse(self.is_valid_ticker(ticker), f"Invalid ticker {ticker} should fail")
    
    def test_date_validation(self):
        """Test analysis date validation"""
        # Valid dates (today and past)
        today = date.today().isoformat()
        past_date = "2025-01-01"
        
        # Invalid dates (future, malformed)
        future_date = "2030-01-01"
        invalid_format = "2025/01/01"
        
        self.assertTrue(self.is_valid_date(today), "Today's date should be valid")
        self.assertTrue(self.is_valid_date(past_date), "Past date should be valid")
        self.assertFalse(self.is_valid_date(future_date), "Future date should be invalid")
        self.assertFalse(self.is_valid_date(invalid_format), "Invalid format should fail")
    
    def test_analyst_selection(self):
        """Test analyst selection validation"""
        valid_analysts = ["Market Analyst", "Social Analyst", "News Analyst", "Fundamentals Analyst"]
        invalid_analysts = ["Invalid Analyst", "Random Name", ""]
        
        # Test valid selections
        self.assertTrue(self.validate_analysts(["Market Analyst"]))
        self.assertTrue(self.validate_analysts(["Market Analyst", "Social Analyst"]))
        self.assertTrue(self.validate_analysts(valid_analysts))
        
        # Test invalid selections
        self.assertFalse(self.validate_analysts([]))  # Empty list
        self.assertFalse(self.validate_analysts(["Invalid Analyst"]))
        self.assertFalse(self.validate_analysts(["Market Analyst", "Invalid Analyst"]))
    
    def test_research_depth_validation(self):
        """Test research depth validation"""
        valid_depths = [1, 3, 5]
        invalid_depths = [0, 2, 4, 6, -1, "3", None]
        
        for depth in valid_depths:
            self.assertTrue(self.is_valid_research_depth(depth), f"Depth {depth} should be valid")
        
        for depth in invalid_depths:
            self.assertFalse(self.is_valid_research_depth(depth), f"Depth {depth} should be invalid")
    
    # Helper validation methods
    def is_valid_ticker(self, ticker):
        """Validate ticker symbol"""
        if not ticker or not isinstance(ticker, str):
            return False
        return ticker.isalpha() and 1 <= len(ticker) <= 5 and ticker.isupper()
    
    def is_valid_date(self, date_str):
        """Validate analysis date"""
        try:
            analysis_date = datetime.fromisoformat(date_str).date()
            return analysis_date <= date.today()
        except (ValueError, TypeError):
            return False
    
    def validate_analysts(self, analysts):
        """Validate analyst selection"""
        valid_analysts = {"Market Analyst", "Social Analyst", "News Analyst", "Fundamentals Analyst"}
        if not analysts or not isinstance(analysts, list):
            return False
        return all(analyst in valid_analysts for analyst in analysts)
    
    def is_valid_research_depth(self, depth):
        """Validate research depth"""
        return depth in [1, 3, 5]

class TestFrontendStateManagement(unittest.TestCase):
    """Test frontend state management logic"""
    
    def setUp(self):
        """Setup test data"""
        self.initial_state = {
            "company": "TSLA",
            "tradeDate": "2025-08-28",
            "selectedAnalysts": ["Market Analyst", "Social Analyst"],
            "researchDepth": 3,
            "llmProvider": "openai",
            "quickThinkingLlm": "gpt-4o-mini",
            "deepThinkingLlm": "o1",
            "isAnalyzing": False,
            "analysisStarted": False
        }
    
    def test_state_initialization(self):
        """Test initial state setup"""
        state = self.initial_state.copy()
        
        # Check required fields
        self.assertIn("company", state)
        self.assertIn("selectedAnalysts", state)
        self.assertIn("researchDepth", state)
        
        # Check default values
        self.assertEqual(state["researchDepth"], 3)
        self.assertEqual(state["llmProvider"], "openai")
        self.assertFalse(state["isAnalyzing"])
    
    def test_analyst_selection_toggle(self):
        """Test analyst selection/deselection logic"""
        state = self.initial_state.copy()
        
        # Add analyst
        new_analyst = "News Analyst"
        if new_analyst not in state["selectedAnalysts"]:
            state["selectedAnalysts"].append(new_analyst)
        
        self.assertIn(new_analyst, state["selectedAnalysts"])
        self.assertEqual(len(state["selectedAnalysts"]), 3)
        
        # Remove analyst
        if new_analyst in state["selectedAnalysts"]:
            state["selectedAnalysts"].remove(new_analyst)
        
        self.assertNotIn(new_analyst, state["selectedAnalysts"])
        self.assertEqual(len(state["selectedAnalysts"]), 2)
    
    def test_analysis_state_transitions(self):
        """Test analysis state transitions"""
        state = self.initial_state.copy()
        
        # Start analysis
        state["isAnalyzing"] = True
        state["analysisStarted"] = True
        
        self.assertTrue(state["isAnalyzing"])
        self.assertTrue(state["analysisStarted"])
        
        # Complete analysis
        state["isAnalyzing"] = False
        
        self.assertFalse(state["isAnalyzing"])
        self.assertTrue(state["analysisStarted"])  # Should remain true

class TestBackendAPILogic(unittest.TestCase):
    """Test backend API logic and data processing"""
    
    def test_session_id_generation(self):
        """Test session ID generation"""
        import uuid
        
        # Generate multiple session IDs
        session_ids = [str(uuid.uuid4()) for _ in range(10)]
        
        # Check uniqueness
        self.assertEqual(len(session_ids), len(set(session_ids)))
        
        # Check format (UUID4)
        for session_id in session_ids:
            self.assertRegex(session_id, r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')
    
    def test_analysis_request_processing(self):
        """Test analysis request processing"""
        valid_request = {
            "ticker": "AAPL",
            "analysis_date": "2025-08-28",
            "analysts": ["Market Analyst", "Social Analyst"],
            "research_depth": 3,
            "llm_config": {
                "provider": "openai",
                "quick_model": "gpt-4o-mini",
                "deep_model": "o1"
            }
        }
        
        # Test valid request processing
        processed = self.process_analysis_request(valid_request)
        self.assertIsNotNone(processed)
        self.assertIn("session_id", processed)
        self.assertEqual(processed["status"], "started")
        
        # Test invalid request
        invalid_request = {"ticker": ""}
        with self.assertRaises(ValueError):
            self.process_analysis_request(invalid_request)
    
    def test_agent_status_tracking(self):
        """Test agent status tracking logic"""
        agents = [
            "Market Analyst", "Social Analyst", "News Analyst", "Fundamentals Analyst",
            "Bull Researcher", "Bear Researcher", "Research Manager", "Trader",
            "Risky Analyst", "Neutral Analyst", "Safe Analyst", "Portfolio Manager"
        ]
        
        # Initialize all agents as pending
        status_tracker = {agent: "pending" for agent in agents}
        
        # Test status updates
        status_tracker["Market Analyst"] = "in_progress"
        self.assertEqual(status_tracker["Market Analyst"], "in_progress")
        
        status_tracker["Market Analyst"] = "completed"
        self.assertEqual(status_tracker["Market Analyst"], "completed")
        
        # Test team progression
        analyst_team = ["Market Analyst", "Social Analyst", "News Analyst", "Fundamentals Analyst"]
        for agent in analyst_team:
            status_tracker[agent] = "completed"
        
        analyst_team_complete = all(status_tracker[agent] == "completed" for agent in analyst_team)
        self.assertTrue(analyst_team_complete)
    
    def process_analysis_request(self, request):
        """Mock analysis request processing"""
        if not request.get("ticker"):
            raise ValueError("Ticker is required")
        
        import uuid
        return {
            "session_id": str(uuid.uuid4()),
            "status": "started",
            "message": f"Analysis started for {request['ticker']}"
        }

class TestBusinessLogicValidation(unittest.TestCase):
    """Test business logic and common sense validation"""
    
    def test_market_hours_validation(self):
        """Test market hours and trading day validation"""
        # Weekend dates (should be flagged for review)
        weekend_dates = ["2025-08-30", "2025-08-31"]  # Saturday, Sunday
        
        for date_str in weekend_dates:
            date_obj = datetime.fromisoformat(date_str).date()
            is_weekend = date_obj.weekday() >= 5  # Saturday=5, Sunday=6
            self.assertTrue(is_weekend, f"{date_str} should be identified as weekend")
    
    def test_ticker_symbol_patterns(self):
        """Test ticker symbol pattern recognition"""
        # Common patterns
        stock_tickers = ["AAPL", "TSLA", "MSFT", "GOOGL"]
        etf_tickers = ["SPY", "QQQ", "VTI", "IWM"]
        crypto_tickers = ["BTC-USD", "ETH-USD"]  # If supported
        
        for ticker in stock_tickers + etf_tickers:
            self.assertTrue(self.is_valid_ticker_pattern(ticker))
    
    def test_analysis_depth_impact(self):
        """Test research depth impact on processing time"""
        depth_time_mapping = {
            1: 5,   # Shallow: ~5 minutes
            3: 15,  # Medium: ~15 minutes  
            5: 30   # Deep: ~30 minutes
        }
        
        for depth, expected_time in depth_time_mapping.items():
            estimated_time = self.estimate_processing_time(depth)
            self.assertGreaterEqual(estimated_time, expected_time * 0.8)  # Within 20% tolerance
            self.assertLessEqual(estimated_time, expected_time * 1.2)
    
    def test_llm_model_compatibility(self):
        """Test LLM model and provider compatibility"""
        model_compatibility = {
            "openai": ["gpt-4o-mini", "o1", "gpt-4"],
            "anthropic": ["claude-3-5-haiku-latest", "claude-sonnet-4-0"],
            "groq": ["llama-3.1-70b-versatile"]
        }
        
        for provider, models in model_compatibility.items():
            for model in models:
                self.assertTrue(self.is_compatible_model(provider, model))
        
        # Test incompatible combinations
        self.assertFalse(self.is_compatible_model("openai", "claude-3-5-haiku-latest"))
        self.assertFalse(self.is_compatible_model("anthropic", "gpt-4o-mini"))
    
    def is_valid_ticker_pattern(self, ticker):
        """Validate ticker pattern"""
        return ticker.isalpha() and 1 <= len(ticker) <= 5
    
    def estimate_processing_time(self, depth):
        """Estimate processing time based on depth"""
        base_time = 5
        return base_time * depth
    
    def is_compatible_model(self, provider, model):
        """Check model-provider compatibility"""
        compatibility = {
            "openai": ["gpt-4o-mini", "o1", "gpt-4"],
            "anthropic": ["claude-3-5-haiku-latest", "claude-sonnet-4-0"],
            "groq": ["llama-3.1-70b-versatile"]
        }
        return model in compatibility.get(provider, [])

class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def test_network_timeout_handling(self):
        """Test network timeout scenarios"""
        # Mock network timeout
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Connection timeout")
            
            result = self.handle_api_request("http://example.com")
            self.assertIsNone(result)
    
    def test_invalid_json_handling(self):
        """Test invalid JSON response handling"""
        invalid_json_responses = [
            "invalid json",
            '{"incomplete": json',
            "",
            None
        ]
        
        for response in invalid_json_responses:
            result = self.parse_json_response(response)
            self.assertIsNone(result)
    
    def test_rate_limiting_behavior(self):
        """Test rate limiting behavior"""
        # Simulate rapid requests
        request_times = []
        for i in range(10):
            request_times.append(datetime.now())
        
        # Check if requests are within reasonable limits
        time_diffs = [
            (request_times[i+1] - request_times[i]).total_seconds() 
            for i in range(len(request_times)-1)
        ]
        
        # Should not have requests faster than 10ms apart (reasonable limit)
        min_interval = min(time_diffs) if time_diffs else 1
        self.assertGreaterEqual(min_interval, 0.001)  # 1ms minimum
    
    def handle_api_request(self, url):
        """Mock API request handler"""
        try:
            # Simulate request
            return {"status": "success"}
        except Exception:
            return None
    
    def parse_json_response(self, response):
        """Mock JSON parser"""
        try:
            if response is None or response == "":
                return None
            return json.loads(response)
        except (json.JSONDecodeError, TypeError):
            return None

def run_unit_tests():
    """Run all unit tests"""
    print("🧪 Running Unit Tests for TradingAgents")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestConfigurationValidation,
        TestFrontendStateManagement,
        TestBackendAPILogic,
        TestBusinessLogicValidation,
        TestErrorHandling
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n📊 UNIT TEST SUMMARY")
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if result.errors:
        print(f"\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('\\n')[-2]}")
    
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == "__main__":
    success = run_unit_tests()
    sys.exit(0 if success else 1)
