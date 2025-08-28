"""
End-to-end testing for complete analysis flow
"""

import asyncio
import json
import time
import pytest
import websockets
from typing import Dict, Any, List
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class E2EAnalysisTest:
    """End-to-end analysis flow testing"""
    
    def __init__(self, backend_url: str = "http://localhost:8003", 
                 frontend_url: str = "http://localhost:5174"):
        self.backend_url = backend_url
        self.frontend_url = frontend_url
        self.session_id = None
        self.driver = None
        
    def setup_browser(self):
        """Setup Chrome browser for testing"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        
    def teardown_browser(self):
        """Clean up browser"""
        if self.driver:
            self.driver.quit()
            
    async def test_backend_health(self) -> bool:
        """Test backend health endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Backend health check failed: {e}")
            return False
            
    async def test_frontend_health(self) -> bool:
        """Test frontend accessibility"""
        try:
            response = requests.get(self.frontend_url, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Frontend health check failed: {e}")
            return False
            
    async def test_api_endpoints(self) -> Dict[str, bool]:
        """Test all API endpoints"""
        results = {}
        
        # Test config endpoints
        try:
            response = requests.get(f"{self.backend_url}/api/config/analysts")
            results['analysts_endpoint'] = response.status_code == 200
        except Exception:
            results['analysts_endpoint'] = False
            
        try:
            response = requests.get(f"{self.backend_url}/api/config/llm-providers")
            results['llm_providers_endpoint'] = response.status_code == 200
        except Exception:
            results['llm_providers_endpoint'] = False
            
        # Test metrics endpoint
        try:
            response = requests.get(f"{self.backend_url}/api/metrics/performance")
            results['metrics_endpoint'] = response.status_code == 200
        except Exception:
            results['metrics_endpoint'] = False
            
        return results
        
    async def test_websocket_connection(self) -> Dict[str, Any]:
        """Test WebSocket connection and messaging"""
        test_session_id = "test-session-123"
        ws_url = f"ws://localhost:8003/ws/{test_session_id}"
        
        results = {
            'connection_established': False,
            'messages_received': 0,
            'connection_ack': False,
            'heartbeat_received': False,
            'error': None
        }
        
        try:
            async with websockets.connect(ws_url) as websocket:
                results['connection_established'] = True
                
                # Wait for connection acknowledgment
                try:
                    ack_message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    ack_data = json.loads(ack_message)
                    if ack_data.get('type') == 'connection_ack':
                        results['connection_ack'] = True
                except asyncio.TimeoutError:
                    pass
                
                # Listen for messages for a short time
                start_time = time.time()
                while time.time() - start_time < 10:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        data = json.loads(message)
                        results['messages_received'] += 1
                        
                        if data.get('type') == 'heartbeat':
                            results['heartbeat_received'] = True
                            
                    except asyncio.TimeoutError:
                        break
                        
        except Exception as e:
            results['error'] = str(e)
            
        return results
        
    def test_frontend_ui_elements(self) -> Dict[str, bool]:
        """Test frontend UI elements are present"""
        results = {}
        
        try:
            self.driver.get(self.frontend_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check for key UI elements
            try:
                self.driver.find_element(By.CLASS_NAME, "websocket-test")
                results['websocket_test_component'] = True
            except:
                results['websocket_test_component'] = False
                
            # Check for connection status
            try:
                status_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Backend Server')]")
                results['backend_status_display'] = len(status_elements) > 0
            except:
                results['backend_status_display'] = False
                
            # Check for WebSocket connection button
            try:
                connect_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Connect')]")
                results['websocket_connect_button'] = len(connect_buttons) > 0
            except:
                results['websocket_connect_button'] = False
                
        except Exception as e:
            print(f"Frontend UI test error: {e}")
            results['error'] = str(e)
            
        return results
        
    def test_websocket_ui_interaction(self) -> Dict[str, bool]:
        """Test WebSocket UI interaction"""
        results = {}
        
        try:
            self.driver.get(self.frontend_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Find and click connect button
            try:
                connect_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Connect')]"))
                )
                connect_button.click()
                results['connect_button_clicked'] = True
                
                # Wait for connection status change
                time.sleep(2)
                
                # Check for connected status
                try:
                    connected_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Connected')]")
                    results['connection_status_updated'] = len(connected_elements) > 0
                except:
                    results['connection_status_updated'] = False
                    
            except Exception as e:
                results['connect_button_clicked'] = False
                results['error'] = str(e)
                
        except Exception as e:
            results['error'] = str(e)
            
        return results
        
    async def run_full_e2e_test(self) -> Dict[str, Any]:
        """Run complete end-to-end test suite"""
        print("🚀 Starting E2E Analysis Flow Test...")
        
        results = {
            'timestamp': time.time(),
            'backend_health': False,
            'frontend_health': False,
            'api_endpoints': {},
            'websocket_test': {},
            'frontend_ui': {},
            'websocket_ui': {},
            'overall_success': False
        }
        
        # Test backend health
        print("📡 Testing backend health...")
        results['backend_health'] = await self.test_backend_health()
        
        # Test frontend health
        print("🌐 Testing frontend health...")
        results['frontend_health'] = await self.test_frontend_health()
        
        # Test API endpoints
        print("🔌 Testing API endpoints...")
        results['api_endpoints'] = await self.test_api_endpoints()
        
        # Test WebSocket connection
        print("🔄 Testing WebSocket connection...")
        results['websocket_test'] = await self.test_websocket_connection()
        
        # Setup browser for UI tests
        print("🖥️  Setting up browser...")
        self.setup_browser()
        
        try:
            # Test frontend UI elements
            print("🎨 Testing frontend UI elements...")
            results['frontend_ui'] = self.test_frontend_ui_elements()
            
            # Test WebSocket UI interaction
            print("🔗 Testing WebSocket UI interaction...")
            results['websocket_ui'] = self.test_websocket_ui_interaction()
            
        finally:
            self.teardown_browser()
            
        # Determine overall success
        success_criteria = [
            results['backend_health'],
            results['frontend_health'],
            results['api_endpoints'].get('analysts_endpoint', False),
            results['websocket_test'].get('connection_established', False),
            results['frontend_ui'].get('websocket_test_component', False)
        ]
        
        results['overall_success'] = all(success_criteria)
        
        return results
        
    def print_results(self, results: Dict[str, Any]):
        """Print formatted test results"""
        print("\n" + "="*60)
        print("🧪 E2E ANALYSIS FLOW TEST RESULTS")
        print("="*60)
        
        # Backend tests
        print(f"📡 Backend Health: {'✅' if results['backend_health'] else '❌'}")
        print(f"🌐 Frontend Health: {'✅' if results['frontend_health'] else '❌'}")
        
        # API endpoints
        print("\n🔌 API Endpoints:")
        for endpoint, status in results['api_endpoints'].items():
            print(f"   {endpoint}: {'✅' if status else '❌'}")
            
        # WebSocket tests
        print(f"\n🔄 WebSocket Connection: {'✅' if results['websocket_test'].get('connection_established') else '❌'}")
        print(f"   Messages Received: {results['websocket_test'].get('messages_received', 0)}")
        print(f"   Connection Ack: {'✅' if results['websocket_test'].get('connection_ack') else '❌'}")
        
        # Frontend UI tests
        print(f"\n🎨 Frontend UI Elements: {'✅' if results['frontend_ui'].get('websocket_test_component') else '❌'}")
        print(f"   Backend Status Display: {'✅' if results['frontend_ui'].get('backend_status_display') else '❌'}")
        
        # Overall result
        print(f"\n🎯 Overall Success: {'✅ PASSED' if results['overall_success'] else '❌ FAILED'}")
        print("="*60)

async def main():
    """Main test execution"""
    tester = E2EAnalysisTest()
    results = await tester.run_full_e2e_test()
    tester.print_results(results)
    
    # Save results to file
    with open('e2e_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
        
    return results['overall_success']

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
