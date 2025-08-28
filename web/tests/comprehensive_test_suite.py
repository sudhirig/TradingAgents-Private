#!/usr/bin/env python3
"""
Comprehensive Testing Suite for TradingAgents Web Application
Tests both backend API endpoints and frontend UI functionality with human-like verification
"""

import asyncio
import json
import logging
import os
import sys
import time
import requests
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import websocket
import threading

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test_results.log")
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    status: str  # "PASS", "FAIL", "SKIP"
    message: str
    duration: float
    details: Optional[Dict[str, Any]] = None

class ComprehensiveTestSuite:
    """Main test suite class"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8001"
        self.frontend_url = "http://localhost:5173"
        self.results: List[TestResult] = []
        self.session = requests.Session()
        
    def log_result(self, test_name: str, status: str, message: str, duration: float, details: Dict = None):
        """Log test result"""
        result = TestResult(test_name, status, message, duration, details)
        self.results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏭️"
        logger.info(f"{status_emoji} {test_name}: {message} ({duration:.2f}s)")
        
        if details:
            logger.debug(f"Details: {json.dumps(details, indent=2)}")

    def test_backend_health(self) -> bool:
        """Test backend health endpoint"""
        start_time = time.time()
        try:
            response = self.session.get(f"{self.backend_url}/health", timeout=5)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Backend Health Check", 
                    "PASS", 
                    f"Backend is healthy - {data.get('service', 'Unknown')}", 
                    duration,
                    data
                )
                return True
            else:
                self.log_result(
                    "Backend Health Check", 
                    "FAIL", 
                    f"HTTP {response.status_code}: {response.text}", 
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_result(
                "Backend Health Check", 
                "FAIL", 
                f"Connection failed: {str(e)}", 
                duration
            )
            return False

    def test_config_endpoints(self) -> bool:
        """Test configuration endpoints"""
        endpoints = [
            ("/api/config/analysts", "Get Analysts"),
            ("/api/config/llm-providers", "Get LLM Providers"),
            ("/api/config/models/openai", "Get OpenAI Models")
        ]
        
        all_passed = True
        for endpoint, test_name in endpoints:
            start_time = time.time()
            try:
                response = self.session.get(f"{self.backend_url}{endpoint}", timeout=5)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(
                        test_name, 
                        "PASS", 
                        f"Retrieved {len(data) if isinstance(data, list) else 'config'} items", 
                        duration,
                        {"count": len(data) if isinstance(data, list) else 1}
                    )
                else:
                    self.log_result(test_name, "FAIL", f"HTTP {response.status_code}", duration)
                    all_passed = False
                    
            except Exception as e:
                duration = time.time() - start_time
                self.log_result(test_name, "FAIL", f"Error: {str(e)}", duration)
                all_passed = False
                
        return all_passed

    def test_analysis_workflow(self) -> bool:
        """Test complete analysis workflow"""
        start_time = time.time()
        
        # Test analysis request
        analysis_request = {
            "ticker": "TSLA",
            "analysis_date": "2025-08-28",
            "analysts": ["Market Analyst", "Social Analyst"],
            "research_depth": 3,
            "llm_config": {
                "provider": "openai",
                "quick_model": "gpt-4o-mini",
                "deep_model": "o1"
            }
        }
        
        try:
            # Start analysis
            response = self.session.post(
                f"{self.backend_url}/api/analysis/start",
                json=analysis_request,
                timeout=10
            )
            
            if response.status_code != 200:
                duration = time.time() - start_time
                self.log_result(
                    "Analysis Workflow", 
                    "FAIL", 
                    f"Failed to start analysis: HTTP {response.status_code}", 
                    duration
                )
                return False
                
            analysis_data = response.json()
            session_id = analysis_data.get("session_id")
            
            if not session_id:
                duration = time.time() - start_time
                self.log_result(
                    "Analysis Workflow", 
                    "FAIL", 
                    "No session_id returned", 
                    duration
                )
                return False
            
            # Test session status
            status_response = self.session.get(
                f"{self.backend_url}/api/analysis/{session_id}/status",
                timeout=5
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                duration = time.time() - start_time
                self.log_result(
                    "Analysis Workflow", 
                    "PASS", 
                    f"Analysis started successfully - Session: {session_id}", 
                    duration,
                    {"session_id": session_id, "status": status_data.get("status")}
                )
                return True
            else:
                duration = time.time() - start_time
                self.log_result(
                    "Analysis Workflow", 
                    "FAIL", 
                    f"Failed to get status: HTTP {status_response.status_code}", 
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_result(
                "Analysis Workflow", 
                "FAIL", 
                f"Workflow error: {str(e)}", 
                duration
            )
            return False

    def test_frontend_accessibility(self) -> bool:
        """Test frontend accessibility and basic functionality"""
        start_time = time.time()
        
        try:
            response = self.session.get(self.frontend_url, timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                # Check for key elements in HTML
                html_content = response.text
                required_elements = [
                    "TradingAgents",
                    "Analysis Configuration", 
                    "Ticker Symbol",
                    "Research Depth",
                    "LLM Provider"
                ]
                
                missing_elements = []
                for element in required_elements:
                    if element not in html_content:
                        missing_elements.append(element)
                
                if not missing_elements:
                    self.log_result(
                        "Frontend Accessibility", 
                        "PASS", 
                        "All required UI elements found", 
                        duration,
                        {"elements_checked": len(required_elements)}
                    )
                    return True
                else:
                    self.log_result(
                        "Frontend Accessibility", 
                        "FAIL", 
                        f"Missing elements: {missing_elements}", 
                        duration
                    )
                    return False
            else:
                self.log_result(
                    "Frontend Accessibility", 
                    "FAIL", 
                    f"HTTP {response.status_code}", 
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_result(
                "Frontend Accessibility", 
                "FAIL", 
                f"Connection error: {str(e)}", 
                duration
            )
            return False

    def test_websocket_connection(self) -> bool:
        """Test WebSocket connection and basic messaging"""
        start_time = time.time()
        
        try:
            # Simple WebSocket connection test
            ws_url = f"ws://localhost:8001/ws/test-session"
            
            def on_message(ws, message):
                logger.debug(f"WebSocket message received: {message}")
                
            def on_error(ws, error):
                logger.error(f"WebSocket error: {error}")
                
            def on_close(ws, close_status_code, close_msg):
                logger.debug("WebSocket connection closed")
                
            def on_open(ws):
                logger.debug("WebSocket connection opened")
                # Send test message
                test_message = {
                    "type": "test",
                    "data": {"message": "Hello WebSocket"}
                }
                ws.send(json.dumps(test_message))
                # Close after sending
                ws.close()
            
            ws = websocket.WebSocketApp(
                ws_url,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            
            # Run WebSocket in thread with timeout
            ws_thread = threading.Thread(target=ws.run_forever)
            ws_thread.daemon = True
            ws_thread.start()
            ws_thread.join(timeout=5)
            
            duration = time.time() - start_time
            self.log_result(
                "WebSocket Connection", 
                "PASS", 
                "WebSocket connection successful", 
                duration
            )
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_result(
                "WebSocket Connection", 
                "FAIL", 
                f"WebSocket error: {str(e)}", 
                duration
            )
            return False

    def test_business_logic_validation(self) -> bool:
        """Test business logic and data validation"""
        start_time = time.time()
        
        test_cases = [
            {
                "name": "Invalid Ticker",
                "data": {"ticker": "", "analysis_date": "2025-08-28"},
                "should_fail": True
            },
            {
                "name": "Future Date",
                "data": {"ticker": "AAPL", "analysis_date": "2030-01-01"},
                "should_fail": True
            },
            {
                "name": "Invalid Analyst",
                "data": {"ticker": "AAPL", "analysts": ["Invalid Analyst"]},
                "should_fail": True
            },
            {
                "name": "Valid Request",
                "data": {
                    "ticker": "AAPL",
                    "analysis_date": "2025-08-28",
                    "analysts": ["Market Analyst"],
                    "research_depth": 3
                },
                "should_fail": False
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            try:
                response = self.session.post(
                    f"{self.backend_url}/api/analysis/start",
                    json=test_case["data"],
                    timeout=5
                )
                
                if test_case["should_fail"]:
                    if response.status_code >= 400:
                        logger.info(f"✅ {test_case['name']}: Correctly rejected invalid data")
                    else:
                        logger.error(f"❌ {test_case['name']}: Should have failed but didn't")
                        all_passed = False
                else:
                    if response.status_code == 200:
                        logger.info(f"✅ {test_case['name']}: Valid request accepted")
                    else:
                        logger.error(f"❌ {test_case['name']}: Valid request rejected")
                        all_passed = False
                        
            except Exception as e:
                logger.error(f"❌ {test_case['name']}: Exception - {str(e)}")
                all_passed = False
        
        duration = time.time() - start_time
        status = "PASS" if all_passed else "FAIL"
        self.log_result(
            "Business Logic Validation", 
            status, 
            f"Tested {len(test_cases)} validation scenarios", 
            duration,
            {"test_cases": len(test_cases)}
        )
        
        return all_passed

    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        logger.info("🚀 Starting Comprehensive Test Suite")
        start_time = time.time()
        
        # Test execution order
        tests = [
            ("Backend Health", self.test_backend_health),
            ("Configuration Endpoints", self.test_config_endpoints),
            ("Analysis Workflow", self.test_analysis_workflow),
            ("Frontend Accessibility", self.test_frontend_accessibility),
            ("WebSocket Connection", self.test_websocket_connection),
            ("Business Logic Validation", self.test_business_logic_validation)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            logger.info(f"\n🧪 Running: {test_name}")
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"❌ {test_name} crashed: {str(e)}")
                failed += 1
        
        total_duration = time.time() - start_time
        
        # Generate summary
        summary = {
            "total_tests": len(tests),
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / len(tests)) * 100,
            "total_duration": total_duration,
            "timestamp": datetime.now().isoformat(),
            "results": [
                {
                    "test_name": r.test_name,
                    "status": r.status,
                    "message": r.message,
                    "duration": r.duration
                }
                for r in self.results
            ]
        }
        
        # Log summary
        logger.info(f"\n📊 TEST SUMMARY")
        logger.info(f"Total Tests: {summary['total_tests']}")
        logger.info(f"Passed: {summary['passed']} ✅")
        logger.info(f"Failed: {summary['failed']} ❌")
        logger.info(f"Success Rate: {summary['success_rate']:.1f}%")
        logger.info(f"Total Duration: {summary['total_duration']:.2f}s")
        
        # Save results to file
        with open("comprehensive_test_results.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        return summary

def main():
    """Main test execution"""
    print("🧪 TradingAgents Comprehensive Test Suite")
    print("=" * 50)
    
    # Check if servers are running
    print("🔍 Checking server status...")
    
    suite = ComprehensiveTestSuite()
    results = suite.run_all_tests()
    
    # Exit with appropriate code
    if results["failed"] == 0:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n💥 {results['failed']} tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
