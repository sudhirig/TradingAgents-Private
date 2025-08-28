#!/usr/bin/env python3
"""
Backend API Testing Suite
Comprehensive testing of all backend endpoints with curl commands and Python requests
"""

import requests
import json
import time
import subprocess
import logging
from typing import Dict, List, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackendAPITester:
    """Backend API testing class"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session_id = None
        
    def run_curl_command(self, curl_cmd: str) -> Dict[str, Any]:
        """Execute curl command and return result"""
        try:
            result = subprocess.run(
                curl_cmd.split(),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_health_endpoint(self):
        """Test health endpoint with both requests and curl"""
        logger.info("🏥 Testing Health Endpoint")
        
        # Python requests test
        try:
            response = self.session.get(f"{self.base_url}/health")
            logger.info(f"✅ Health check (requests): {response.status_code} - {response.json()}")
        except Exception as e:
            logger.error(f"❌ Health check (requests) failed: {e}")
        
        # Curl test
        curl_cmd = f"curl -X GET {self.base_url}/health -H 'Content-Type: application/json'"
        result = self.run_curl_command(curl_cmd)
        
        if result["success"]:
            logger.info(f"✅ Health check (curl): {result['stdout']}")
        else:
            logger.error(f"❌ Health check (curl) failed: {result.get('stderr', result.get('error'))}")
    
    def test_config_endpoints(self):
        """Test all configuration endpoints"""
        logger.info("⚙️ Testing Configuration Endpoints")
        
        endpoints = [
            "/api/config/analysts",
            "/api/config/llm-providers", 
            "/api/config/models/openai",
            "/api/config/models/anthropic"
        ]
        
        for endpoint in endpoints:
            # Python requests test
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ {endpoint} (requests): {len(data) if isinstance(data, list) else 'OK'}")
                else:
                    logger.error(f"❌ {endpoint} (requests): HTTP {response.status_code}")
            except Exception as e:
                logger.error(f"❌ {endpoint} (requests) failed: {e}")
            
            # Curl test
            curl_cmd = f"curl -X GET {self.base_url}{endpoint} -H 'Content-Type: application/json'"
            result = self.run_curl_command(curl_cmd)
            
            if result["success"]:
                try:
                    data = json.loads(result["stdout"])
                    logger.info(f"✅ {endpoint} (curl): {len(data) if isinstance(data, list) else 'OK'}")
                except:
                    logger.info(f"✅ {endpoint} (curl): Response received")
            else:
                logger.error(f"❌ {endpoint} (curl) failed")
    
    def test_analysis_endpoints(self):
        """Test analysis workflow endpoints"""
        logger.info("🔬 Testing Analysis Endpoints")
        
        # Test data
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
        
        # Start analysis with requests
        try:
            response = self.session.post(
                f"{self.base_url}/api/analysis/start",
                json=analysis_request
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get("session_id")
                logger.info(f"✅ Start analysis (requests): Session {self.session_id}")
            else:
                logger.error(f"❌ Start analysis (requests): HTTP {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Start analysis (requests) failed: {e}")
        
        # Start analysis with curl
        curl_data = json.dumps(analysis_request)
        curl_cmd = f"curl -X POST {self.base_url}/api/analysis/start -H 'Content-Type: application/json' -d '{curl_data}'"
        
        result = self.run_curl_command(curl_cmd)
        if result["success"]:
            try:
                data = json.loads(result["stdout"])
                curl_session_id = data.get("session_id")
                logger.info(f"✅ Start analysis (curl): Session {curl_session_id}")
            except:
                logger.info(f"✅ Start analysis (curl): Response received")
        else:
            logger.error(f"❌ Start analysis (curl) failed")
        
        # Test session status if we have a session ID
        if self.session_id:
            self.test_session_status()
    
    def test_session_status(self):
        """Test session status endpoints"""
        if not self.session_id:
            logger.warning("⚠️ No session ID available for status testing")
            return
            
        logger.info(f"📊 Testing Session Status for {self.session_id}")
        
        # Get status with requests
        try:
            response = self.session.get(f"{self.base_url}/api/analysis/{self.session_id}/status")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Session status (requests): {data.get('status', 'Unknown')}")
            else:
                logger.error(f"❌ Session status (requests): HTTP {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Session status (requests) failed: {e}")
        
        # Get status with curl
        curl_cmd = f"curl -X GET {self.base_url}/api/analysis/{self.session_id}/status -H 'Content-Type: application/json'"
        result = self.run_curl_command(curl_cmd)
        
        if result["success"]:
            try:
                data = json.loads(result["stdout"])
                logger.info(f"✅ Session status (curl): {data.get('status', 'Unknown')}")
            except:
                logger.info(f"✅ Session status (curl): Response received")
        else:
            logger.error(f"❌ Session status (curl) failed")
    
    def test_error_scenarios(self):
        """Test error handling and edge cases"""
        logger.info("🚨 Testing Error Scenarios")
        
        error_tests = [
            {
                "name": "Invalid JSON",
                "endpoint": "/api/analysis/start",
                "data": "invalid json",
                "expected_status": 422
            },
            {
                "name": "Missing Required Fields",
                "endpoint": "/api/analysis/start", 
                "data": {"ticker": "AAPL"},
                "expected_status": 422
            },
            {
                "name": "Invalid Session ID",
                "endpoint": "/api/analysis/invalid-session/status",
                "data": None,
                "expected_status": 404
            },
            {
                "name": "Non-existent Endpoint",
                "endpoint": "/api/nonexistent",
                "data": None,
                "expected_status": 404
            }
        ]
        
        for test in error_tests:
            try:
                if test["data"] is None:
                    response = self.session.get(f"{self.base_url}{test['endpoint']}")
                else:
                    if isinstance(test["data"], str):
                        # Test invalid JSON
                        response = self.session.post(
                            f"{self.base_url}{test['endpoint']}",
                            data=test["data"],
                            headers={"Content-Type": "application/json"}
                        )
                    else:
                        response = self.session.post(
                            f"{self.base_url}{test['endpoint']}",
                            json=test["data"]
                        )
                
                if response.status_code == test["expected_status"]:
                    logger.info(f"✅ {test['name']}: Correctly returned {response.status_code}")
                else:
                    logger.error(f"❌ {test['name']}: Expected {test['expected_status']}, got {response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ {test['name']} failed: {e}")
    
    def test_performance(self):
        """Test API performance and response times"""
        logger.info("⚡ Testing Performance")
        
        endpoints = [
            "/health",
            "/api/config/analysts",
            "/api/config/llm-providers"
        ]
        
        for endpoint in endpoints:
            times = []
            for i in range(5):  # Test 5 times
                start_time = time.time()
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}")
                    duration = time.time() - start_time
                    times.append(duration)
                except Exception as e:
                    logger.error(f"❌ Performance test {endpoint} failed: {e}")
                    continue
            
            if times:
                avg_time = sum(times) / len(times)
                max_time = max(times)
                min_time = min(times)
                
                logger.info(f"📈 {endpoint}: Avg={avg_time:.3f}s, Min={min_time:.3f}s, Max={max_time:.3f}s")
                
                if avg_time > 1.0:
                    logger.warning(f"⚠️ {endpoint}: Slow response time ({avg_time:.3f}s)")
    
    def run_all_tests(self):
        """Run complete backend API test suite"""
        logger.info("🚀 Starting Backend API Test Suite")
        logger.info("=" * 50)
        
        start_time = time.time()
        
        # Run all test categories
        self.test_health_endpoint()
        self.test_config_endpoints()
        self.test_analysis_endpoints()
        self.test_error_scenarios()
        self.test_performance()
        
        total_time = time.time() - start_time
        logger.info(f"\n✅ Backend API tests completed in {total_time:.2f}s")

def main():
    """Main execution"""
    print("🧪 Backend API Testing Suite")
    print("=" * 40)
    
    tester = BackendAPITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
